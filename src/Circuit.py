from subprocess import run
from time import time, sleep
from shutil import copyfile
from mmap import mmap
from io import SEEK_CUR
from statistics import stdev
import math

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

    def __init__(self, index, filename, template, mcu, logger, config, rand, sine_funcs):
        self.__index = index
        self.__filename = filename
        self.__microcontroller = mcu
        self.__config = config
        self.__logger = logger
        self.__rand = rand
        self.__fitness = 0
        self.__mean_voltage = 0 #needed for combined fitness func

        # SECTION Build the relevant paths
        asc_dir = config.get_asc_directory()
        bin_dir = config.get_bin_directory()
        data_dir = config.get_data_directory()
        self.__hardware_filepath = asc_dir.joinpath(filename + ".asc")
        self.__bitstream_filepath = bin_dir.joinpath(filename + ".bin")

        # NOTE Using log files instead of a data buffer in the event of premature termination
        self.__data_filepath = data_dir.joinpath(filename + ".log")

        # SECTION Intialize the hardware file
        # If template is falsy, won't copy the file
        if template:
            copyfile(template, self.__hardware_filepath)

        # Since the hardware file is written to and read from a lot, we
        # mmap it to improve preformance.
        hardware_file = open(self.__hardware_filepath, "r+")
        self.__hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()
        
        # Used for the sine simulation mode; up to 100 sine waves
        self.__src_sine_funcs = sine_funcs
        self.__simulation_bitstream = [0] * 100

        # Values for MAP elites
        self.__low_val = 0
        self.__high_val = 0

    @staticmethod
    def get_file_attribute_st(mmapped_file, attribute):
        '''
        Static get file attribute method; allows using without creating a full circuit object
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
        Static version of set file attribute; allows using without creating a full circuit object
        '''
        # Check if the comment exists
        #hardware_file = open(file_path, "r+")
        mmapped_file = mmap(hardware_file.fileno(), 0)
        index = mmapped_file.find(b".comment FILE_ATTRIBUTES")
        if index < 0:
            # Create the comment
            comment_line = ".comment FILE_ATTRIBUTES " + attribute + "={" + value + "}\n"
            # This requires re-mapping the self.__hardware_file
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

        #self.__hardware_file = mmap(hardware_file.fileno(), 0)
        #hardware_file.close()

    def get_file_attribute(self, attribute):
        '''
        Gets the value of attribute stored in a comment in the circuit's .asc file
        '''
        return Circuit.get_file_attribute_st(self.__hardware_file, attribute)
    
    def set_file_attribute(self, attribute, value):
        '''
        Sets the value of the attribute stored in a comment in the circuit's .asc file
        '''
        hardware_file = open(self.__hardware_filepath, "r+")
        Circuit.set_file_attribute_st(hardware_file, attribute, value)
        # Re-map our hardware file
        self.__hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()


    def randomize_bits(self):
        # Simply set mutation chance to 100%
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            self.__mutate_simulation(True)
        else:
            self.__mutate_actual(True)

    def __compile(self):
        """
        Compile circuit ASC file to a BIN file for hardware upload.
        """
        self.__log_event(2, "Compiling", self, "with icepack...")

        # Ensure the file backing the mmap is up to date with the latest
        # changes to the mmap.
        self.write_hardware_changes()

        compile_command = [
            COMPILE_CMD,
            self.__hardware_filepath,
            self.__bitstream_filepath
        ]
        run(compile_command);

        self.__log_event(2, "Finished compiling", self)

    def get_sim_bitstream(self):
        """
        Returns the simulation bitstream array
        """
        return self.__simulation_bitstream

    def get_hardware_file_path(self):
        """
        Returns the hardware file path
        """
        return self.__hardware_filepath

    # TODO Evaluate based on a fitness function defined in the config file
    # while still utilizing the existing or newly added evaluate functions in this class
    # def evaluate(self):
    #     return 
    
    def evaluate_sim(self, is_combined):
        """
        Just evaluate the simulation bitstream (use sine function combinations, with variance formula)
        """
        
        # Need to sum up the waveforms of every 1 that appears in our bitstream
        sine_funcs = []
        for pos in range(len(self.__simulation_bitstream)):
            if self.__simulation_bitstream[pos] == 1:
                # Need to calculate sine function for this position
                sine_funcs.append(self.__src_sine_funcs[pos])

        # Force them to have at least 10 sine functions turned on
        if len(sine_funcs) <= 10:
            self.__fitness = 0
            return 0

        # Ok now we need to generate our waveform
        num_samples = 500
        waveform = []
        for i in range(num_samples):
            sum = 0
            for func in sine_funcs:
                sum = sum + func(i)
            # Taking the average keeps it within the drawable range
            waveform.append(sum / len(sine_funcs))
        
        if is_combined:
            fitness = self.__measure_combined_fitness(waveform)
        else:
            fitness = self.__measure_variance_fitness(waveform)

        self.__update_all_live_data()
        return fitness

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
        
        self.__log_event(3, "Fitness: ", self.__fitness)

        self.__update_all_live_data()

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
        self.__log_event(1,
            "TIME TAKEN RUNNING AND LOGGING ---------------------- ",
            elapsed
        )

        waveform = self.__read_variance_data()
        fitness = self.__measure_variance_fitness(waveform)
        self.__update_all_live_data()
        return fitness

    def evaluate_pulse_count(self):
        """
        Upload and run this circuit and count the number of pulses it
        generates.
        """
        start = time()
        self.__run()
        self.__microcontroller.measure_pulses(self)

        elapsed = time() - start
        self.__log_event(1,
            "TIME TAKEN RUNNING AND LOGGING ---------------------- ",
            elapsed
        )

        fitness = self.__measure_pulse_fitness()
        self.__update_all_live_data()
        return fitness

    def evaluate_combined(self):
        """
        Upload and run this circuit and take a combined measure of fitness
        """
        start = time()
        self.__run()
        self.__microcontroller.measure_signal(self)

        elapsed = time() - start
        self.__log_event(1,
            "TIME TAKEN RUNNING AND LOGGING ---------------------- ",
            elapsed
        )

        waveform = self.__read_variance_data()
        fitness = self.__measure_combined_fitness(waveform)
        self.__update_all_live_data()
        return fitness

    def measure_mean_voltage(self):
        """
        Upload and run this circuit and take a mean voltage measure

        """
        start = time()
        self.__run()
        self.__microcontroller.measure_signal(self)

        elapsed = time() - start
        self.__log_event(1,
            "TIME TAKEN RUNNING AND LOGGING ---------------------- ",
            elapsed
        )

        waveform = self.__read_variance_data()
        return self.__measure_mean_voltage(waveform)

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

    def __read_variance_data(self):
        data_file = open(self.__data_filepath, "rb")
        data = data_file.readlines()
        total_samples = 500
        waveform = []
        for i in range(total_samples-1):
            try:
                x = int(data[i].strip().split(b": ", 1)[1])
                waveform.append(x)
            except:
                self.__log_error(1, "FAILED TO READ {} AT LINE {} -> ZEROIZING LINE".format(
                    self,
                    i
                ))
                waveform.append(0)
        return waveform

    # NOTE Using log files instead of a data buffer in the event of premature termination
    def __measure_variance_fitness(self, waveform):
        """
        Measure the fitness of this circuit using the ??? fitness
        function
        TODO: Clarify
        """

        variance_sum = 0
        total_samples = 500
        variances = []
        # Reset high/low vals to min/max respectively
        self.__low_val = 1024
        self.__high_val = 0
        for i in range(len(waveform)-1):
            # NOTE Signal Variance is calculated by summing the absolute difference of
            # sequential voltage samples from the microcontroller.
            # Capture the next point in the data file to a variable
            initial1 = waveform[i] #int(data[i].strip().split(b": ", 1)[1])
            # Capture the next point + 1 in the data file to a variable
            initial2 = waveform[i+1] #int(data[i + 1].strip().split(b": ", 1)[1])
            # Take the absolute difference of the two points and store to a variable
            variance = abs(initial2 - initial1)
            # Append the variance to the waveform list
            # Removed since we do this already
            #waveform.append(initial1)

            if initial1 < self.__low_val:
                self.__low_val = initial1
            if initial1 > self.__high_val:
                self.__high_val = initial1

            # Stability: if we want stable waves, we should want to differences between points to be
            # similar. i.e. we want to minimize the differences between these differences
            # Can do 1/[(std. deviation)+0.01] to find a fitness value for the stability
            # To do that we'll start by storing the variances to its own collection
            # NOTE: This encourages frequencies that match the sampling rate
            variances.append(variance)

            if initial1 != None and initial1 < 1000:
                variance_sum += variance

        with open("workspace/waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i += 1

        var_max_fitness = variance_sum / total_samples
        self.__fitness = var_max_fitness
        self.__mean_voltage = sum(waveform) / len(waveform) #used by combined fitness func

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
        self.__log_event(3, "Pulses counted: {}".format(pulse_count))

        if pulse_count == 0:
            self.__log_event(2, "NULL DATA FILE. ZEROIZING")

        desired_freq = self.__config.get_desired_frequency()
        var = self.__config.get_variance_threshold()
        if pulse_count == desired_freq:
            self.__log_event(1, "Unity achieved: {}".format(self))
            self.__fitness = 1
        elif pulse_count == 0:
            self.__fitness = var
        else:
            self.__fitness = var + (1.0 / desired_freq - pulse_count)
        
        return self.__fitness

    def __measure_combined_fitness(self, waveform):
        """
        Calculates the circuit's fitness based on a combination of it's pulse count and variance
        """

        # need to evaluate var fitness first since it calculates the mean voltage
        varFitness = self.__measure_variance_fitness(waveform)
        varWeight = self.__config.get_var_weight()

        # Using the different between average and threshhold voltage since pulse count is normally 0
        # pulseFitness = self.__measure_pulse_fitness()
        # Add 1 to it so that it is a whole number, and raising to a power will increase the value
        #pulseFitness = 1 / (abs(self.__mean_voltage - 341) + 1) + 1
        # Issue with old approach is graph was mostly a straight line with a spike at the target voltage
        # We've changed to a somewhat normal distribution-like function to provide better encouragement
        # Constants:
        # The 341 is the target threshold voltage
        # The 200 is used as a sort of "standard deviation"-esque variable. Raising it widens the graph
        pulseFitness = 10 * math.exp(-0.5 * math.pow((self.__mean_voltage - 341) / 200, 2))
        pulseWeight = self.__config.get_pulse_weight()

        self.__log_event(4, "Pulse Fitness: ", pulseFitness)
        self.__log_event(4, "Variance Fitness: ", varFitness)

        if self.__config.get_fitness_mode() == "ADD":
            self.__fitness = (pulseWeight * pulseFitness) + (varWeight * varFitness)
        else: #MULT
            self.__fitness = pow(pulseFitness, pulseWeight) * pow(varFitness, varWeight)

        self.__log_event(3, "Combined Fitness: ", self.__fitness)
        
        return self.__fitness
 
    def __measure_mean_voltage(self, waveform):
        self.__measure_variance_fitness(waveform)
        return self.__mean_voltage

    def __update_all_live_data(self):
        # TODO ALIFE2021 Make sure alllivedata.log is cleared before run
        with open("workspace/alllivedata.log", "br+") as allLive:
            line = allLive.readline()
            while line != b'':
                if line.find(str(self).encode()) >= 0:
                    allLive.seek(-1 * len(line), SEEK_CUR)
                    allLive.write(
                        "{}, {}, {}\n".format(
                            self,
                            str(self.__fitness).rjust(8),
                            self.get_file_attribute('src_population').rjust(8))
                        .encode()
                    )
                    allLive.flush()
                    return
                line = allLive.readline()

            allLive.write("{}, {}, {}\n".format(
                    self,
                    str(self.__fitness).rjust(8),
                    self.get_file_attribute('src_population').rjust(8))
                .encode()
            )
            allLive.flush()

    # SECTION Genetic Algorithm related functions
    
    def mutate(self):
        """
        Decide which mutation function to used based on configuration
        Only the full simulation mode uses a special function, otherwise we use the default to operate on the hardware files
        """
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            self.__mutate_simulation(False)
        else:
            self.__mutate_actual(False)
    
    def __mutate_simulation(self, all_random):
        """
        Mutate the simulation mode circuit
        self.__config.get_mutation_probability()
        """
        # Try to mutate each bit, flip if possible
        for i in range(0, len(self.__simulation_bitstream)):
            if all_random:
                self.__simulation_bitstream[i] = self.__rand.integers(0, 2)
            else:
                if self.__config.get_mutation_probability() >= self.__rand.uniform(0,1):
                    # Mutate this bit
                    self.__simulation_bitstream[i] = 1 - self.__simulation_bitstream[i]

    def __mutate_actual(self, all_random):
        """
        Mutate the configuration of this circuit.
        This involves checking the mutation chance per-bit and, if it passes, flipping that bit
        """
        
        # Set tile to the first location of the substring ".logic_tile"
        # The b prefix makes the string an instance of the "bytes" type
        # The .logic_tile header indicates that there is a tile, so the "tile" variable stores the starting point of the current tile
        tile = self.__hardware_file.find(b".logic_tile")
        
        while tile > 0:
            # Set pos to the position of this tile, but with the length of ".logic_tile" added so it is in front of where we have the x/y coords
            pos = tile + len(".logic_tile")
            
            
            # Check if the position is legal to modify
            if self.__tile_is_included(self.__hardware_file, pos):
                # Find the start and end of the line; the positions of the \n newline just before and at the end of this line
                # The start is the newline position + 1, so the first valid bit character
                # line_size is self-explanatory
                # This finds the length of a standard line of bits (so the width of each data-containing line in this tile)
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
                        # This will get us to individual bits. If the mutation probability passes
                        # Our position is now going to be the start of the first line, plus the line size multiplied to get to our desired row,
                        # and finally added to the column (with the int cast to sanitize user input)
                        pos = line_start + line_size * (row - 1) + int(col)
                        if all_random:
                            self.__hardware_file[pos] = self.__rand.integers(48, 50)
                        else:
                            if self.__config.get_mutation_probability() >= self.__rand.uniform(0,1):
                                # Set this bit to either a 0 or 1 randomly
                                # Keep in mind that these are BYTES that we are modifying, not characters
                                # Therefore, we have to set it to either ASCII 0 (48) or ASCII 1 (49), not actual 0 or 1, which represent different characters
                                # and will corrupt the file if we mutate in this way
                                prev = self.__hardware_file[pos]
                                # 48 = 0, 49 = 1. To flip, just need to do (48+49) - the current value (48+49=97)
                                # This now always flips the bit instead of randomly assigning it every time
                                self.__hardware_file[pos] = 97 - prev
                                # Note: If prev != 48 or 49, then we changed the wrong value because it was not a 0 or 1 previously
                                self.__log_event(4, "Mutating:", self, "@(", row, ",", col, ") previous was", prev)

            # Find the next logic tile, and start again
            # Will return -1 if .logic_tile isn't found, and the while loop will exit
            tile = self.__hardware_file.find(b".logic_tile", tile + 1)

    def get_file_intrinsic_modifiable_bitstream(self, hardware_file):
        """
        Returns an array of bytes (that correspond to characters, so they will either be 48 or 49)
        These bytes represent the bits of the circuit's bitstream that can be modified. All other bits are left out
        """

        # TODO: Convert this to be a single function that takes this functionality and the mutate_actual one. Function takes in a callback to call on each modifiable position
        # Set tile to the first location of the substring ".logic_tile"
        # The b prefix makes the string an instance of the "bytes" type
        # The .logic_tile header indicates that there is a tile, so the "tile" variable stores the starting point of the current tile
        tile = hardware_file.find(b".logic_tile")
        
        bitstream = []
        
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
                if self.__config.get_routing_type() == "MOORE":
                    rows = [1, 2, 13]
                elif self.__config.get_routing_type() == "NEWSE":
                    rows = [1, 2]
                # Iterate over each row and the columns that we can access within each row
                for row in rows:
                    for col in self.__config.get_accessed_columns():
                        # This will get us to individual bits. Our position is now going to be the start of the first line, plus the line size multiplied to get to our desired row,
                        # and finally added to the column (with the int cast to sanitize user input)
                        pos = line_start + line_size * (row - 1) + int(col)
                        byte = hardware_file[pos]
                        bitstream.append(byte)

            # Find the next logic tile, and start again
            # Will return -1 if .logic_tile isn't found, and the while loop will exit
            tile = hardware_file.find(b".logic_tile", tile + 1)
            
        return bitstream

    def get_intrinsic_modifiable_bitstream(self):
        """
        Returns an array of bytes (that correspond to characters, so they will either be 48 or 49)
        These bytes represent the bits of the circuit's bitstream that can be modified. All other bits are left out
        """
        return self.get_file_intrinsic_modifiable_bitstream(self.__hardware_file)
    
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
        Copy part of the hardware file from parent into this circuit's hardware file.
        Additionally, need to copy the parent's info line
        """
        parent_hw_file = parent.get_hardware_file()
        # Need to keep track separately since we can have different-length comments
        parent_tile = parent_hw_file.find(b".logic_tile")
        my_tile = self.__hardware_file.find(b".logic_tile")
        while my_tile > 0:
            my_pos = my_tile + len(".logic_tile")
            parent_pos = parent_tile + len(".logic_tile")
            if self.__tile_is_included(self.__hardware_file, my_pos):
                line_start = parent_hw_file.find(b"\n", parent_tile) + 1
                line_end = parent_hw_file.find(b"\n", line_start + 1)
                line_size = line_end - line_start + 1

                my_pos = my_tile + line_size * (crossover_point - 1)
                parent_pos = parent_tile + line_size * (crossover_point - 1)

                data = parent_hw_file[parent_pos:parent_pos + line_size]
                self.update_hardware_file(my_pos, line_size, data)

            parent_tile = parent_hw_file.find(b".logic_tile", parent_tile + 1)
            my_tile = self.__hardware_file.find(b".logic_tile", my_tile + 1)
        
        # Need to set our source population to our parent's
        src_pop = parent.get_file_attribute("src_population")
        if src_pop != None:
            self.set_file_attribute("src_population", src_pop)

    def copy_sim(self, src):
        self.__simulation_bitstream = []
        for val in src.get_sim_bitstream():
            self.__simulation_bitstream.append(val)

    # SECTION Functions involving the underlying hardware

    # TODO Add error checking here
    def update_hardware_file(self, pos, length, data):
        """
        Make changes to the hardware file associated with this circuit, updating it
        with the value in "data"
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
        """
        Copy the hardware from a source circuit to this circuit.
        """
        source.write_hardware_changes()
        self.replace_hardware_file(source.get_hardware_filepath())

    # SECTION Getters.
    def get_fitness(self):
        """
        Returns the fitness of this circuit.
        """
        return self.__fitness

    def get_hardware_file(self):
        """
        Returns the hardware file of this circuit
        """
        return self.__hardware_file

    # NOTE may need to add the file extension here (.asc)
    def get_hardware_filepath(self):
        """
        Returns the path to the hardware file associated with this
        Circuit (the raw .asc)
        """
        return self.__hardware_filepath

    # NOTE may need to add the file extension here (.bin)
    def get_bitstream_filepath(self):
        """
        Returns the path to the bitstream file associated with this
        Circuit (the compiled .bin)
        """
        return self.__bitstream_filepath

    def get_data_filepath(self):
        """
        Returns the path to the data log file associated with this
        Circuit.
        """
        return self.__data_filepath

    def get_index(self):
        """
        Returns the index of this Circuit, as provided upon initialization.
        """
        return self.__index

    # SECTION Miscellanious helper functions.
    def __tile_is_included(self, hardware_file, pos):
        """
        Determines whether a given tile is available for modificiation.
        NOTE: Tile = the .logic_tile in the asc file.
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
        #print("Trying", self, "'" + x_str + "'", "'" + y_str + "'", "Pos was:", pos, "First bit is: ", "'" + str(hardware_file[pos:(pos+20)], 'utf-8') + "'",
        #    "prev bit is: " + "'" + str(hardware_file[(pos-20):pos], 'utf-8') + "'")
        x = int(x_str)
        y = int(y_str)
        is_x_valid = x in VALID_TILE_X
        is_y_valid = y in VALID_TILE_Y

        return is_x_valid and is_y_valid

    # Values for MAP elites
    def get_low_value(self):
        return self.__low_val
    def get_high_value(self):
        return self.__high_val

    def __log_event(self, level, *event):
        """
        Emit an event-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_event(level, *event)

    def __log_info(self, level, *info):
        """
        Emit an info-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_info(level, *info)

    def __log_error(self, level, *error):
        """
        Emit an error-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_error(level, *error)

    def __log_warning(self, level, *warning):
        """
        Emit a warning-level log. This function is fulfilled through
        the logger.
        """
        self.__logger.log_warning(level, *warning)
