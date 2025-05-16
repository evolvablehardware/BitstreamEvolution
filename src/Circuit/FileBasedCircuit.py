from mmap import mmap
from pathlib import Path
from shutil import copyfile
from subprocess import run
import os
from time import sleep
from BitstreamEvolutionProtocols import FPGA_Compilation_Data
from Circuit.Circuit import Circuit
from Directories import Directories
from Logger import Logger
from result import Result, Ok, Err # type: ignore

COMPILE_CMD = "icepack"
RUN_CMD = "iceprog"

class FileBasedCircuit(Circuit):
    """
    Represents a Circuit that is based on an ASC file, in a format
    ready to be compiled by IceStorm tools.
    Provides useful methods for working with hardware files
    """

    def __init__(self, *, index: int, filename: str, template: Path, logger: Logger, directories: Directories,
                 routing_type: str, accessed_columns: list[int]):
        Circuit.__init__(self, index, filename, logger)
        self.__routing_type = routing_type
        self.__accessed_columns = accessed_columns

        asc_dir = directories.asc_dir
        bin_dir = directories.bin_dir
        data_dir = directories.data_dir
        self.__hardware_filepath = asc_dir.joinpath(filename + ".asc")
        self.__bitstream_filepath = bin_dir.joinpath(filename + ".bin")

        # Create directories if they don't exist
        os.makedirs(asc_dir, exist_ok=True)
        os.makedirs(bin_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # NOTE Using log files instead of a data buffer in the event of premature termination
        self._data_filepath = data_dir.joinpath(filename + ".log")
        # Create the data file if it doesn't exist
        open(self._data_filepath, "w+").close()

        if template:
            copyfile(template, self.__hardware_filepath)

        # Since the hardware file is written to and read from a lot, we
        # mmap it to improve preformance.
        hardware_file = open(self.__hardware_filepath, "r+")
        self._hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()

    def copy_from(self, other):
        copyfile(other._hardware_filepath, self.__hardware_filepath)

    def compile(self, fpga: FPGA_Compilation_Data) -> Result[None,Exception]:
        """
        Compiles and uploads the compiled circuit and runs it on the FPGA
        """

        self.__compile()
        
        cmd_str = [
            RUN_CMD,
            self.__bitstream_filepath,
            "-d",
            fpga.id
        ]
        print(cmd_str)
        run(cmd_str)
        sleep(1)

        return Ok(None)

        # if switching fpgas every sample, need to upload to the second fpga also
        # if self._config.get_transfer_sample():
        #     cmd_str = [
        #         RUN_CMD,
        #         self._bitstream_filepath,
        #         "-d",
        #         self._config.get_fpga2()
        #     ]
        #     print(cmd_str)
        #     run(cmd_str)
        #     sleep(1)

    def __run_at_each_modifiable(self, lambda_func, hardware_file = None, accessible_columns = None,
        routing_type=None):
        """
        Runs the lambda_func at every modifiable position
        Args passed to lambda_func: value of bit (as a byte), row, col
        If lambda_func returns a value (byte), then the bit is set to that number
        If lambda_func returns None, then the bit is left unmodified
        Keep in mind the bytes are the ASCII codes, so for example 49 = 1

        .. warning::
            Go over this with someone who can clarify what all of the data types are. 

        Parameters
        ----------
        lambda_func : Callable
            This function is called for each modifiable bit. The bit value is passed into lambda_func.
            If lambda_func returns None, the bit is left unmodified. If lambda_func returns another value,
            then the bit at that position is replaced with the return value of lambda_func.
        hardware_file : str | None
            The path to the hardware file to read from/write to. If no value provided, uses this Circuit's hardware file.
        accessible_columns : list[str] | None
            The accessible columns. If no value provided, uses the current configuration value.
        routing_type: str | None
            The routing type (MOORE or NEWSE). If no value provided, uses the current configuration value.
        """

        if hardware_file is None:
            hardware_file = self._hardware_file

        if accessible_columns is None:
            accessible_columns = self.__accessed_columns

        if routing_type is None:
            routing_type = self.__routing_type

        # Set tile to the first location of the substring ".logic_tile"
        # The b prefix makes the string an instance of the "bytes" type
        # The .logic_tile header indicates that there is a tile, so the "tile" variable stores the starting point of the current tile
        tile = hardware_file.find(b".logic_tile")
        
        while tile > 0:
            # Set pos to the position of this tile, but with the length of ".logic_tile" added so it is in front of where we have the x/y coords
            pos = tile + len(".logic_tile")
            
            # Check if the position is legal to modify
            if self.__tile_is_included(hardware_file, pos):
                # Find the start and end of the line; the positions of the \n newline just before and at the end of this line
                # The start is the newline position + 1, so the first valid bit character
                # line_size is self-explanatory
                # This finds the length of a standard line of bits (so the width of each data-containing line in this tile)
                line_start = hardware_file.find(b"\n", tile) + 1
                line_end = hardware_file.find(b"\n", line_start + 1)
                line_size = line_end - line_start + 1

                # Determine which rows we can modify
                # TODO ALIFE2021 The routing protocol here is dated and needs to mimic that of the Tone Discriminator
                rows = []
                if routing_type == "MOORE":
                    rows = [1, 2, 13]
                elif routing_type == "NEWSE":
                    rows = [1, 2]
                # Iterate over each row and the columns that we can access within each row
                for row in rows:
                    for col in accessible_columns:
                        # This will get us to individual bits. If the mutation probability passes
                        # Our position is now going to be the start of the first line, plus the line size multiplied to get to our desired row,
                        # and finally added to the column (with the int cast to sanitize user input)
                        pos = line_start + line_size * (row - 1) + int(col)
                        bit_value = hardware_file[pos]
                        lambda_return = lambda_func(bit_value, row, col)
                        if lambda_return is not None:
                            # need to re-assign the bit
                            hardware_file[pos] = lambda_return

            # Find the next logic tile, and start again
            # Will return -1 if .logic_tile isn't found, and the while loop will exit
            tile = hardware_file.find(b".logic_tile", tile + 1)

    def __compile(self):
        """
        Compile circuit ASC file to a BIN file for hardware upload.
        """
        self.__log_event(2, "Compiling", self, "with icepack...")

        # Ensure the file backing the mmap is up to date with the latest
        # changes to the mmap.
        self._hardware_file.flush()

        compile_command = [
            COMPILE_CMD,
            self.__hardware_filepath,
            self.__bitstream_filepath
        ]
        run(compile_command)

        self.__log_event(2, "Finished compiling", self)

    def __tile_is_included(self, hardware_file, pos):
        """
        Determines whether a given tile is available for modificiation.
        NOTE: Tile = the .logic_tile in the asc file.

        .. warning::
            Preexisting todo: Replace magic values with a more generalized solution. 
            These magic values are indicative of the underlying hardware (ice40kh1k)

        Parameters
        ----------
        hardware_file : mmap
            Memory Mapped hardware file
        pos : int
            Index of the first byte in the .asc file for the hardware

        Returns
        -------
        bool
            True if the tile at that position is valid (The Tiles we can modigy)
        """
        # Replace these magic values with a more generalized solution
        # Magic values are indicative of the underlying hardware (ice40hx1k)
        # A different model will require different magic values (i.e. ice40hx8k)
        VALID_TILE_X = range(4, 10)
        VALID_TILE_Y = range(1, 17)

        # NOTE x and y are stored as ints to aid the loops that search and identify
        # tiles while scraping the asc files
        # This is in the actual asc file; this is why we can simply pull from "pos"
        # i.e. you'll see the header ".logic_file 1 1" - x=1, y=1
        
        # This is where we had a fundamental issue before: The value in the hardware at this position is going to be an ASCII char value, not the actual
        # number. Here, we parse the byte as an integer, then to a char, then back to an integer
        
        # However, we have a great problem now: what about multi-digit numbers?
        # Find the space that separates the x and y, and find the end of the line
        # Then, grab the bytes for x, grab the bytes for y, convert to strings, and parse those strings
        space_pos = hardware_file.find(b" ", pos + 1)
        eol_pos = hardware_file.find(b"\n", pos)
        x_bytes = hardware_file[pos:space_pos]
        y_bytes = hardware_file[space_pos:eol_pos]
        x_str = x_bytes.decode("utf-8").strip()
        y_str = y_bytes.decode("utf-8").strip()
        x = int(x_str)
        y = int(y_str)
        is_x_valid = x in VALID_TILE_X
        is_y_valid = y in VALID_TILE_Y

        return is_x_valid and is_y_valid

    def get_bitstream(self) -> list[bool]:
        bitstream: list[bool] = []
        def add_bit(bit: int, *rest):
            if bit == 48:
                bitstream.append(False)
            elif bit == 49:
                bitstream.append(True)
        self.__run_at_each_modifiable(add_bit)
        return bitstream
    
    def set_bitstream(self, bitstream: list[bool]):
        index = 0
        def get_bit(*rest):
            nonlocal index
            bit = bitstream[index]
            index = index + 1
            if bit:
                return 49
            else:
                return 48
        self.__run_at_each_modifiable(get_bit)

    @staticmethod
    def get_file_attribute_st(mmapped_file, attribute):
        '''
        Returns the value of the stored attribute from the hardware file.
        Circuits are capable of storing string name-value pairs in their hardware file, for purposes such as
        tracking most recently-evaluated fitness of a Circuit
        Static version of get_file_attribute that requires the memory-mapped file to be provided

        Parameters
        ----------
        mmapped_file : mmap
            The memory-mapped hardware file of the circuit
        attribute : str
            Attribute name to lookup

        Returns
        -------
        str
            File attribute value
        '''
        index = mmapped_file.find(b".comment FILE_ATTRIBUTES")
        if index < 0:
            return '0'
        else:
            newline_index = mmapped_file.find(b'\n', index)
            searchable_area = mmapped_file[index:newline_index]
            attr_index = searchable_area.find(bytes(attribute + '={', 'utf-8'))
            if attr_index < 0: # Value doesn't exist yet
                return '0'
            attr_index = attr_index + len(attribute + "={")
            end_index = searchable_area.find(b'}', attr_index)
            value_bytes = searchable_area[attr_index:end_index]
            return str(value_bytes, 'utf-8')

    @staticmethod
    def set_file_attribute_st(hardware_file, attribute, value):
        '''
        Sets a Circuit's file attribute to the specified value
        Circuits are capable of storing string name-value pairs in their hardware file, for purposes such as
        tracking most recently-evaluated fitness of a Circuit
        Static version of set_file_attribute that requires the memory-mapped file to be provided

        Parameters
        ----------
        hardware_file : mmap
            The memory-mapped hardware file of the Circuit
        attribute : str
            The name of the attribute to modify
        value : str
            The value to assign to the attribute
        '''
        # Check if the comment exists
        #hardware_file = open(file_path, "r+")
        mmapped_file = mmap(hardware_file.fileno(), 0)
        index = mmapped_file.find(b".comment FILE_ATTRIBUTES")
        if index < 0:
            # Create the comment
            comment_line = ".comment FILE_ATTRIBUTES " + attribute + "={" + value + "}\n"
            # This requires re-mapping the self._hardware_file
            #hardware_file = open(file_path, "r+")
            content = hardware_file.read()
            hardware_file.seek(0, 0)
            hardware_file.write(comment_line + content)
        else:
            # Check if the attribute exists
            end_index = mmapped_file.find(b'\n', index)
            line = str(mmapped_file[index:end_index], 'utf-8')
            attr_index = line.find(attribute + "={")
            lines = hardware_file.readlines()
            line_index = 0 # Index of the line that contains the attribute comment
            for l in lines:
                if l.find(".comment FILE_ATTRIBUTES") >= 0:
                    break
                line_index = line_index + 1

            if attr_index < 0:
                # Attribute doesn't exist yet
                line = line + " " + attribute + "={" + value + "}\n"
            else:
                attr_end_index = line.find('}', attr_index) + 2
                before_attr = line[:attr_index]
                after_attr = line[attr_end_index:]
                line = before_attr + attribute + "={" + value + "} " + after_attr + '\n'
            lines[line_index] = line
            hardware_file.truncate(0)
            hardware_file.seek(0)
            hardware_file.writelines(lines)

    def get_file_attribute(self, attribute) -> str | None:
        '''
        Returns the value of the stored attribute for this Circuit
        Circuits are capable of storing string name-value pairs in their hardware file, for purposes such as
        tracking most recently-evaluated fitness of a Circuit

        Parameters
        ----------
        attrbute : str
            The name of the attribute of this circuit you want

        Returns
        -------
        str
            The value of the attribute
        '''
        return FileBasedCircuit.get_file_attribute_st(self._hardware_file, attribute)
    
    def set_file_attribute(self, attribute, value):
        '''
        Sets this Circuit's file attribute to the specified value
        Circuits are capable of storing string name-value pairs in their hardware file, for purposes such as
        tracking most recently-evaluated fitness of a Circuit

        Parameters
        ----------
        attribute : str
            The name of the attribute to modify
        value : str
            The value to assign to the attribute
        '''
        hardware_file = open(self.__hardware_filepath, "r+")
        FileBasedCircuit.set_file_attribute_st(hardware_file, attribute, value)
        # Re-map our hardware file
        self._hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()

    def __log_event(self, level, *event):
        """
        Emit an event-level log. This function is fulfilled through
        the logger.
        """
        self._logger.log_event(level, *event)
