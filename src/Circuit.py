from subprocess import run
from time import time, sleep
from shutil import copyfile
from mmap import mmap
from io import SEEK_CUR

# TODO Integrate globals in a more elegant manner.
RUN_CMD = "iceprog"
COMPILE_CMD = "icepack"

class Circuit:
    """
    Represents a manifestation of a particular configuration
    on an FPGA and all its associated information. It tracks the
    location of the various files associated with the FPGA
    configurations as well as GA information associated with the
    configuration. This class also defines methods to run, modify,
    and analyze FPGA configurations.
    """

    def __repr__(self):
        """
        Returns the string representation of this Circuit, used in
        functions such as 'print'.
        """
        return self.__filename

    def __init__(self, index, filename, template, mcu, logger, config, rand):
        self.__index = index
        self.__filename = filename
        self.__microcontroller = mcu
        self.__config = config
        self.__logger = logger
        self.__rand = rand
        self.__fitness = 0

        # SECTION Build the relevant paths
        asc_dir = config.get_asc_directory()
        bin_dir = config.get_bin_directory()
        data_dir = config.get_data_directory()
        self.__hardware_filepath = asc_dir.joinpath(filename + ".asc")
        self.__bitstream_filepath = bin_dir.joinpath(filename + ".bin")

        # NOTE Using log files instead of a data buffer in the event of premature termination
        self.__data_filepath = data_dir.joinpath(filename + ".log")

        # SECTION Intialize the hardware file
        copyfile(template, self.__hardware_filepath)

        # Since the hardware file is written to and read from a lot, we
        # mmap it to improve preformance.
        hardware_file = open(self.__hardware_filepath, "r+")
        self.__hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()
        
        # If simulation mode, then we don't compile or read the binary or anything, just simply keep a bitstream of 100 bits we modify in here
        self.__simulation_bitstream = [0] * 100;

    def __compile(self):
        """
        Compile circuit ASC file to a BIN file for hardware upload.
        """
        self.__log_event("Compiling", self, "with icepack...")

        # Ensure the file backing the mmap is up to date with the latest
        # changes to the mmap.
        self.write_hardware_changes()

        compile_command = [
            COMPILE_CMD,
            self.__hardware_filepath,
            self.__bitstream_filepath
        ]
        run(compile_command);

        self.__log_event("Finished compiling", self)

    # TODO Evaluate based on a fitness function defined in the config file
    # while still utilizing the existing or newly added evaluate functions in this class
    # def evaluate(self):
    #     return 
    
    def evaluate_sim(self):
        """
        Just evaluate the simulation bitstream (count # of 1s)
        """
        
        self.__fitness = self.__simulation_bitstream.count(1)
	
        return self.__fitness

    def evaluate_sim_hardware(self):
        """
        Sum up all the bytes in the compiled binary file
        """
        
        self.__compile()
        
        self.__fitness = 0
        with open(self.__bitstream_filepath, "rb") as f:
            byte = f.read(1)
            while byte != b"":
                self.__fitness = self.__fitness + int.from_bytes(byte, "big")
                byte = f.read(1)
        
        return self.__fitness

    def evaluate_variance(self):
        """
        Upload and run this Circuit on the FPGA and analyze its
        performance.
        """
        start = time()

        self.__run()
        self.__microcontroller.measure_signal(self)

        elapsed = time() - start
        self.__log_event(
            "TIME TAKEN RUNNING AND LOGGING ---------------------- ",
            elapsed
        )

        return self.__measure_variance_fitness()

    def evaluate_pulse_count(self):
        """
        Upload and run this circuit and count the number of pulses it
        generates.
        """
        start = time()
        self.__run()
        self.__microcontroller.measure_pulses(self)

        elapsed = time() - start
        self.__log_event(
            "TIME TAKEN RUNNING AND LOGGING ---------------------- ",
            elapsed
        )

        self.__measure_pulse_fitness()

    def __run(self):
        """
        Compiles this Circuit, uploads it, and runs it on the FPGA
        """
        self.__compile()
        
        cmd_str = [
            RUN_CMD,
            self.__bitstream_filepath,
            "-d",
            self.__config.get_fpga()
        ]
        print(cmd_str)
        run(cmd_str)
        sleep(1)

    # NOTE Using log files instead of a data buffer in the event of premature termination
    def __measure_variance_fitness(self):
        """
        Measure the fitness of this circuit using the ??? fitness
        function
        """
        data_file = open(self.__data_filepath, "rb")
        data = data_file.readlines()

        variance_sum = 0
        total_samples = 500
        waveform = []
        for i in range(total_samples-1):
            # NOTE Signal Variance is calculated by summing the absolute difference of
            # sequential voltage samples from the microcontroller.
            try:
                # Capture the next point in the data file to a variable
                initial1 = int(data[i].strip().split(b": ", 1)[1])
                # Capture the next point + 1 in the data file to a variable
                initial2 = int(data[i + 1].strip().split(b": ", 1)[1])
                # Take the absolute difference of the two points and store to a variable
                variance = abs(initial2 - initial1)
                # Append the variance to the waveform list
                waveform.append(initial1)


                if initial1 != None and initial1 < 1000:
                    variance_sum += variance
            except:
                self.__log_error("FAILED TO READ {} AT LINE {} -> ZEROIZING LINE".format(
                    self,
                    i
                ))

        with open("workspace/waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i += 1

        self.__fitness = variance_sum / total_samples
        # return self.__fitness

        # TODO ALIFE2021 Make sure alllivedata.log is cleared before run
        with open("workspace/alllivedata.log", "br+") as allLive:
            line = allLive.readline()
            while line != b'':
                if line.find(str(self).encode()) >= 0:
                    allLive.seek(-1 * len(line), SEEK_CUR)
                    allLive.write(
                        "{}, {}\n".format(
                            self,
                            str(self.__fitness).rjust(8))
                        .encode()
                    )
                    allLive.flush()
                    return self.__fitness
                line = allLive.readline()

            allLive.write("{}, {}\n".format(
                    self,
                    str(self.__fitness).rjust(8)
                )
                .encode()
            )
            allLive.flush()
        return self.__fitness

    # NOTE Using log files instead of a data buffer in the event of premature termination
    def __measure_pulse_fitness(self):
        """
        Measures the fitness of this circuit using the pulse-count
        fitness function
        """
        data_file = open(self.__data_filepath, "r")
        data = data_file.readlines()

        # Extract the integer value from the log file indicating the pulses counted from
        # the microcontroller. Pulses are currently measured by Rising or Falling edges
        # that cross the microcontrollers reference voltage (currently ~2.25 Volts)
        pulse_count = 0
        for i in range(len(data)):
            pulse_count += int(data[i])
        self.__log_event("Pulses counted: {}".format(pulse_count))

        if pulse_count == 0:
            self.__log_event("NULL DATA FILE. ZEROIZING")

        desired_freq = self.__config.get_desired_frequency()
        var = self.__config.get_variance_threshold()
        if pulse_count == desired_freq:
            self.__log_event("Unity achieved: {}".format(self))
            self.__fitness = 1
        elif pulse_count == 0:
            self.__fitness = var
        else:
            self.__fitness = var + (1.0 / desired_freq - pulse_count)

    # SECTION Genetic Algorithm related functions
    
    def mutate(self):
        """
        Decide which mutation function to used based on configuration
        Only the full simulation mode uses a special function, otherwise we use the default to operate on the hardware files
        """
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            self.__mutate_simulation()
        else:
            self.__mutate_actual()
    
    def __mutate_simulation(self):
        """
        Mutate the simulation mode circuit
        """
        # Pick a random position and flip it
        pos = self.__rand.integers(0, len(self.__simulation_bitstream))
        value = self.__simulation_bitstream[pos]
        if value == 0:
            self.__simulation_bitstream[pos] = 1
        else:
            self.__simulation_bitstream[pos] = 0
    
    # TODO Initialize function to avoid conditional checks?
    def __mutate_actual(self):
        """
        Mutate the configuration of this circuit.
        """
        
        # Set tile to the first location of the substring ".logic_tile"
        # The b prefix makes the string an instance of the "bytes" type
        # The .logic_tile header indicates that there is a tile, so the "tile" variable stores the starting point of the current tile
        tile = self.__hardware_file.find(b".logic_tile")
        
        
        while tile > 0:
            # Set pos to the position of this tile, but with the length of ".logic_tile" added so it is the position of the first 0 or 1
            pos = tile + len(".logic_tile")
            
            self.__log_event("=============++++++++++++++++++++++++++++++++++++++++++++++++++++ INSIDE MUTATE!!", pos)
            
            # Check if the position is legal to modify
            if self.__tile_is_included(pos):
                # Find the start and end of the line; the positions of the \n newline just before and at the end of this line
                # The start is the newline position + 1, so the first valid bit character
                # line_size is self-explanatory
                # The line in question seems to be the .logic_tile line, so this should theoretically find where that line starts and ends, and find the size of the line
                # that we should ignore (the header of the tile)
                line_start = self.__hardware_file.find(b"\n", tile) + 1
                line_end = self.__hardware_file.find(b"\n", line_start + 1)
                line_size = line_end - line_start + 1

                # Determine which rows we can modify
                # TODO ALIFE2021 The routing protocol here is dated and needs to mimic that of the Tone Discriminator
                if self.__config.get_routing_type() == "MOORE":
                    rows = [1, 2, 13]
                elif self.__config.get_routing_type() == "NEWSE":
                    rows = [1, 2]
                # Iterate over each row and the columns that we can access within each row
                for row in rows:
                    for col in self.__config.get_accessed_columns():
                        # This will get us to individual bits. If the mutation probability passes, then...
                        if self.__config.get_mutation_probability() >= self.__rand.uniform(0,1):
                            # ... our position is now going to be the tile location, plus the line size multiplied to get to our desired row,
                            # and finally added to the column (with the int cast to sanitize user input)
                            pos = tile + line_size * (row - 1) + int(col)
                            # Set this bit to either a 0 or 1 randomly
                            self.__hardware_file[pos] = self.__rand.integers(0,2)

            # Find the next logic tile, and start again
            # Will return -1 if .logic_tile isn't found, and the while loop will exit
            tile = self.__hardware_file.find(b".logic_tile", tile + 1)

    # TODO Incorporate crossover into simulation mode; right now it won't do any crossover
    def copy_genes_from(self, parent, crossover_point):
        """
        Decide which crossover function to used based on configuration
        Only the full simulation mode uses a special crossover function, otherwise we use the default to operate on the hardware files
        """
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            self.__crossover_sim(parent, crossover_point)
        else:
            self.__crossover_actual(parent, crossover_point)
        
    def __crossover_sim(self, parent, crossover_point):
        """
        Simulated crossover, pulls first n bits from parent and remaining from self
        """
        for i in range(0, crossover_point):
            self.__simulation_bitstream[i] = parent.__simulation_bitstream[i]
        # Remaining bits left unchanged
        
    def __crossover_actual(self, parent, crossover_point):
        """
        Copy part of the configuration from parent into this circuit.
        """
        parent_hw_file = parent.get_hardware_file()
        tile = parent_hw_file.find(b".logic_tile")
        while tile > 0:
            pos = tile + len(".logic_tile")
            if self.__tile_is_included(pos):
                line_start = parent_hw_file.find(b"\n", tile) + 1
                line_end = parent_hw_file.find(b"\n", line_start + 1)
                line_size = line_end - line_start + 1

                pos = tile + line_size * (crossover_point - 1)
                data = parent_hw_file[pos:pos + line_size]
                self.update_hardware_file(pos, line_size, data)

            tile = parent.get_hardware_file().find(b".logic_tile", tile + 1)

    # SECTION Functions involving the underlying hardware

    # TODO Add error checking here
    def update_hardware_file(self, pos, length, data):
        """
        Make changes to the hardware file associated with this circuit.
        """
        self.__hardware_file[pos:pos + length] = data

    def write_hardware_changes(self):
        """
        Write the changes that were made to the mmap instance back to
        its underlying file.
        """
        self.__hardware_file.flush()

    def replace_hardware_file(self, new_file_path):
        """
        Replaces the hardware file associated with this Circuit with
        the given file.
        """
        self.__hardware_file.close()
        hardware_filepath = self.get_hardware_filepath()
        copyfile(new_file_path, hardware_filepath)
        hardware_file = open(hardware_filepath, "r+")
        self.__hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()

    def copy_hardware_from(self, source):
        """Copy the hardware from a source circuit to this circuit."""
        source.write_hardware_change()
        self.replace_hardware_file(source.get_hardware_file)

    # SECTION Getters.
    def get_fitness(self):
        """Returns the fitness of this circuit."""
        return self.__fitness

    # TODO Add docstring.
    def get_hardware_file(self):
        return self.__hardware_file

    # NOTE may need to add the file extension here (.asc)
    def get_hardware_filepath(self):
        """
        Returns the path to the hardware file associated with this
        Circuit.
        """
        return self.__hardware_filepath

    # NOTE may need to add the file extension here (.bin)
    def get_bitstream_filepath(self):
        """
        Returns the path to the bitstream file associated with this
        Circuit.
        """
        return self.__bitstream_filepath

    def get_data_filepath(self):
        """
        Returns the path to the data log file associated with this
        Circuit.
        """
        return self.__data_filepath

    def get_index(self):
        """Returns the index of this Circuit."""
        return self.__index

    # SECTION Miscellanious helper functions.
    def __tile_is_included(self, pos):
    
        """
        Determines whether a given tile is available for modificiation.
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
        space_pos = self.__hardware_file.find(b" ", pos + 1)
        eol_pos = self.__hardware_file.find(b"\n", pos)
        x_bytes = self.__hardware_file[pos:space_pos]
        y_bytes = self.__hardware_file[space_pos:eol_pos]
        x_str = x_bytes.decode("utf-8").strip()
        y_str = y_bytes.decode("utf-8").strip()
        self.__log_event("Attempting", x_str, ",", y_str, pos, self.__hardware_file[pos:pos + 100].decode("utf-8"), self)
        x = int(x_str)
        y = int(y_str)
        is_x_valid = x in VALID_TILE_X
        is_y_valid = y in VALID_TILE_Y

        return is_x_valid and is_y_valid

    def __log_event(self, *event):
        """
        Emit an event-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_event(*event)

    def __log_info(self, *info):
        """
        Emit an info-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_info(*info)

    def __log_error(self, *error):
        """
        Emit an error-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_error(*error)

    def __log_warning(self, *warning):
        """
        Emit a warning-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_warning(*warning)
