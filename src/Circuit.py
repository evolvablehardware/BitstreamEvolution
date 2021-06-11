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

        # REVIEW Consider using data buffer instead of file.
        self.__data_filepath = data_dir.joinpath(filename + ".log")

        # SECTION Intialize the hardware file
        copyfile(template, self.__hardware_filepath)

        # Since the hardware file is written to and read from a lot, we
        # mmap it to improve preformance.
        hardware_file = open(self.__hardware_filepath, "r+")
        self.__hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()

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

    # FIXME Rename this to account for multiple fitness functions.
    # TODO Rename to some like evaluate_variance
    def evaluate(self):
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

    # FIXME This should also be "evaluating"
    def get_pulse_count(self):
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

    # REVIEW We could probably improve this by using a buffer instead of a file.
    def __measure_variance_fitness(self):
        """
        Measure the fitness of this circuit using the ??? fitness
        function
        """
        data_file = open(self.__data_filepath, "rb")
        data = data_file.readlines()

        wave = 0
        waveform = []
        for i in range(499):
            # REVIEW Really need to review what this section does.
            try:
                initial1 = int(data[i].strip().split(b": ", 1)[1])
                initial2 = int(data[i + 1].strip().split(b": ", 1)[1])
                variance = abs(initial2 - initial1)
                waveform.append(initial1)

                if initial1 != None and initial1 < 1000:
                    wave += variance
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

        self.__fitness = wave / 500
        # return self.__fitness

        # TODO Make sure alllivedata.log is cleared before run
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

    # REVIEW We could probably improve this by using a buffer instead of a file.
    def __measure_pulse_fitness(self):
        """
        Measures the fitness of this circuit using the pulse-count
        fitness function
        """
        data_file = open(self.__data_filepath, "r")
        data = data_file.readlines()

        # REVIEW Look more into what exactly this code is doing.
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
    # TODO Initialize function to avoid conditional checks?
    def mutate(self):
        """
        Mutate the configuration of this circuit.
        """
        tile = self.__hardware_file.find(b".logic_tile")
        while tile > 0:
            pos = tile + len(".logic_tile")
            if self.__tile_is_included(pos):
                line_start = self.__hardware_file.find(b"\n", tile) + 1
                line_end = self.__hardware_file.find(b"\n", line_start + 1)
                line_size = line_end - line_start + 1

                # TODO Should line 14 be included in MOORE routing?
                if self.__config.get_routing == "MOORE":
                    rows = [1, 2, 13]
                elif self.__config.get_routing == "NEWSE":
                    rows = [1, 2]
                for row in rows:
                    for col in self.__config.get_acccessed_columns:
                        if self.__config.mutation_probability >= self.__rand.uniform(0,1):
                            pos = tile + line_size * (row - 1) + col
                            self.__hardware_filefile[pos] = str(self.__rand.integers(0,2))

            tile = self.__hardware_file.find(b".logic_tile", tile + 1)

    def copy_genes_from(self, parent, crossover_point):
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

    # TODO Do we need to add the extension here?
    def get_hardware_filepath(self):
        """
        Returns the path to the hardware file associated with this
        Circuit.
        """
        return self.__hardware_filepath

    # TODO Do we need to add the extension here?
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
        VALID_TILE_X = range(4, 10)
        VALID_TILE_Y = range(1, 17)

        # REVIEW Should we store the x and y as strings?
        is_x_valid = int(self.__hardware_file[pos + 1]) in VALID_TILE_X
        is_y_valid = int(self.__hardware_file[pos + 3]) in VALID_TILE_Y

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