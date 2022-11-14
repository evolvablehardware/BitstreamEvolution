from os import name
import os
import numpy as np
from typing import NamedTuple
from Circuit import Circuit
from shutil import copyfile
from sortedcontainers import SortedKeyList
from math import ceil
from numpy.random import default_rng
from pathlib import Path
from itertools import zip_longest
from collections import namedtuple
from time import time
from subprocess import run

RANDOMIZE_UNTIL_NOT_SET_ERR_MSG = '''\
RANDOMIZE_UNTIL not set in config.ini, continuing without randomization'''

INVALID_VARIANCE_ERR_MSG = '''\
VARIANCE_THRESHOLD <= 0 as set in config.ini, continuing without randomization'''

# SEED_HARDWARE is the hardware file used as an initial template for the Circuits
# NOTE The Seed file is provided as a way to kickstart the evolutionary process
# without having to perform a time-consuming random search for a seedable circuit.
# Contact repository authors if you're interested in a new seed file.
SEED_HARDWARE_FILEPATH = Path("data/seed-hardware.asc")

# The basename (filename without path or extensions) of the Circuit
# hardware, bitstream, and data files.
CIRCUIT_FILE_BASENAME="hardware"

# Create a named tuple for easy and clear storage of information about
# a Circuit (currently its name and fitness)
CircuitInfo = namedtuple("CircuitInfo", ["name", "fitness"])

class CircuitPopulation:
    # SECTION Initialization functions
    def __init__(self, mcu, config, logger):
        """ Generates the initial population of circuits with the following arguments

                Args:
                    mcu::[Class Object] containing an instance of Microcontroller class

                    config::[Class Object] containing an instance of Config class

                    logger::[Class Object] containing an instance of Logger class

        """
        self.__config = config
        self.__microcontroller = mcu

        # A list of Circuits that's sorted by fitness decreasing order
        # (to get it to sort in decreasing order I had to multiply the
        # sort key by negative one to reverse the natural sorting order
        # since sortedcontainers don't have a way to be in reverse order).
        self.__circuits = SortedKeyList(key=lambda ckt: -1 * ckt.get_fitness())
        self.__logger = logger
        self.__overall_best_circuit_info = CircuitInfo("", 0)
        self.__rand = default_rng()
        self.__current_epoch = 0
        self.__best_epoch = 0

        # Set the selection type here since the selection type should
        # not change during a run. This way we don't have to branch each
        # time we run selection.
        if config.get_selection_type() == "SINGLE_ELITE":
            self.__run_selection = self.__run_single_elite_tournament
        elif config.get_selection_type() == "FRAC_ELITE":
            self.__run_selection = self.__run_fractional_elite_tournament
        elif config.get_selection_type() == "CLASSIC_TOURN":
            self.__run_selection = self.__run_classic_tournament
        elif config.get_selection_type() == "FIT_PROP_SEL":
            self.__run_selection = self.__run_fitness_proportional_selection
        else:
            self.__log_error(1, "Invalid Selection method in config.ini. Exiting...")
            exit()

        elitism_fraction = config.get_elitism_fraction()
        population_size = config.get_population_size()
        self.__n_elites = int(ceil(elitism_fraction * population_size))

    # TODO Add docstring.
    def populate(self):
        for index in range(1, self.__config.get_population_size() + 1):
            ckt = Circuit(
                index,
                "hardware" + str(index),
                SEED_HARDWARE_FILEPATH,
                self.__microcontroller,
                self.__logger,
                self.__config,
                self.__rand
            )
            self.__circuits.add(ckt)
            self.__log_event(3, "Created circuit: {0}".format(ckt))

        # Randomize initial circuits until waveform variance or
        # pulses are found
        if not self.__config.get_simulation_mode() == "FULLY_INTRINSIC":
            pass # No randomization implemented for simulation mode
        elif self.__config.get_randomization_type() == "PULSE":
            self.__log_info(2, "PULSE randomization mode selected.")
            self.__randomize_until_pulses()
        elif self.__config.get_randomization_type() == "VARIANCE":
            self.__log_info(2, "VARIANCE randomization mode selected.")
            if self.config.variance_threshold() <= 0:
                self.log_error(INVALID_VARIANCE_ERR_MSG)
            else:
                self.__randomize_until_variance()
        elif self.__config.get_randomization_type() == "NO":
            self.__log_info(2, "NO randomization mode selected.")
        else:
            self.__log_error(1, RANDOMIZE_UNTIL_NOT_SET_ERR_MSG)

    def __randomize_until_pulses(self):
        """
        Randomizes population until minimum variance is found
        """
        no_pulses_generated = True
        while no_pulses_generated:
            # NOTE Randomize until pulses will continue mutating and
            # not revert to the original seed-hardware until restarting 
            for circuit in self.__circuits:
                circuit.mutate()
                pulses = circuit.evaluate_pulse_count()
                if (pulses > 0):
                    no_pulses_generated = False

    # NOTE This is whole function going to be upgraded to handle a from-scratch circuit seeding process.
    # https://github.com/evolvablehardware/BitstreamEvolution/issues/3 
    def __randomize_until_variance(self):
        """
        Randomizes population until minimum variance is found
        """
        pass

    # TODO Add docstring.
    def __next_epoch(self):
        self.__current_epoch += 1

    # TODO Add docstring.
    def evolve(self):
        if len(self.__circuits) == 0:
            self.__log_error(1, "Attempting to evolve with empty population. Exiting...")
            exit()

        # Set initial values for 'best' data
        self.__overall_best_circuit_info = CircuitInfo(
            str(self.__circuits[0]),
            self.__circuits[0].get_fitness()
        )
        self.__best_epoch = 0
        self.__next_epoch()
        
        while(self.get_current_epoch() < self.__config.get_n_generations()):
            # Since sortedcontainers don't update when the value by
            # which an item is sorted gets updated, we have to add the
            # Circuits to a new list after we evaluate them and then
            # make the new list the working Circuit list.
            reevaulated_circuits = SortedKeyList(
                key=lambda ckt: -ckt.get_fitness()
            )

            # Evaluate all the Circuits in this CircuitPopulation.
            start = time()
            fitness_sum = 0
            for circuit in self.__circuits:
                # If evaluate returns true, then a circuit has surpassed
                # the threshold and we are done.
                
                # Biggest difference between Fully Instrinsic and Hardware Sim: The fitness evaluation
                if self.__config.get_simulation_mode() == "FULLY_SIM":
                    fitness = circuit.evaluate_sim()
                elif self.__config.get_simulation_mode() == "SIM_HARDWARE":
                    fitness = circuit.evaluate_sim_hardware()
                else:
                    fitness = circuit.evaluate_pulse_count()
                if fitness > self.__config.get_variance_threshold():
                    self.__log_event(1, "{} fitness: {}".format(circuit, fitness))
                    return
                fitness_sum += fitness
                reevaulated_circuits.add(circuit)
            epoch_time = time() - start
            self.__circuits = reevaulated_circuits

            # If one of the new Circuits has a higher fitness than our
            # recorded best, make it the recorded best.
            best_circuit_info = self.get_overall_best_circuit_info()
            self.__log_event(2, "Best circuit info", best_circuit_info.fitness)
            self.__log_event(2, "Circuit 0 info", self.__circuits[0].get_fitness())
            if self.__circuits[0].get_fitness() > best_circuit_info.fitness:
                self.__overall_best_circuit_info = CircuitInfo(
                    str(self.__circuits[0]),
                    self.__circuits[0].get_fitness()
                )
                self.__best_epoch = self.get_current_epoch()
                self.__log_event(2, "New best found")

            self.__logger.log_generation(self, epoch_time)
            self.__run_selection()
            self.__next_epoch()
            
            # Calculate the diversity measure
            diversity = 0
            if self.__config.get_diversity_measure() == "HAMMING_DIST":
                diversity = self.avg_hamming_dist()
            elif self.__config.get_diversity_measure() == "UNIQUE":
                diversity = self.count_unique()
            # Providing any invalid measure of diversity will make it constantly 0

            with open("workspace/bestlivedata.log", "a") as liveFile:
                avg = fitness_sum / self.__config.get_population_size()
                # Format: Epoch, Best Fitness, Worst Fitness, Average Fitness, Ovr Best Fitness, Diversity Measure
                liveFile.write("{}, {}, {}, {}, {}, {}\n".format(
                    str(self.get_current_epoch()),
                    str(self.__circuits[0].get_fitness()),
                    str(self.__circuits[-1].get_fitness()),
                    str(avg),
                    str(self.get_overall_best_circuit_info().fitness),
                    diversity
                ))

    # SECTION Selection algorithms.
    # TODO Add docstring.
    def __run_classic_tournament(self):
        population = self.__rand.permutation(self.__circuits)

        self.__log_event(3, "Tournament Number:", self.get_current_epoch())

        # For all Circuits in the CircuitPopulation, take two random
        # circuits at a time from the population and compare them. Copy
        # some genes from the fittest of the two to the least fittest of
        # the two and mutate the latter.
        for ckt1, ckt2 in CircuitPopulation.__group(population, 2):
            ckt1_fitness = ckt1.get_fitness()
            ckt2_fitness = ckt2.get_fitness()
            if ckt1_fitness > ckt2_fitness:
                self.__log_event(3,
                    "Fitness {}: {} > Fitness {}: {}".format(
                        ckt1,
                        ckt1.get_fitness(),
                        ckt2,
                        ckt2.get_fitness()
                ))

                self.__single_point_crossover(ckt1, ckt2)
                ckt2.mutate()
            else:
                self.__log_event(3,
                    "Fitness {}: {} < Fitness {}: {}".format(
                        ckt1,
                        ckt1.get_fitness(),
                        ckt2,
                        ckt2.get_fitness()
                ))

                self.__single_point_crossover(ckt2, ckt1)
                ckt1.mutate()

    # TODO Add docstring.
    def __run_single_elite_tournament(self):
        self.__log_event(3, "Tournament Number: {}".format(str(self.get_current_epoch())))

        best = self.get_best_circuit()
        for ckt in self.__circuits:
            # Replace the hardware of all the Circuits (except for the
            # best) with the current best Circuit's hardware and then
            # mutate them.
            if ckt != best:
                if  ckt.get_fitness() <= best.fitness():
                    ckt.copy_hardware_from()
                    ckt.mutate()
            else:
                self.__log_info(2, ckt, "is current BEST")

    # TODO Add docstring.
    def __run_fractional_elite_tournament(self):
        self.__log_info(2, "Number of Elites: ", str(self.__n_elites))
        self.__log_info(2, "Ranked Fitness: ", self.__circuits)

        # Generate a group of elite Circuits from the
        # n = <self.__n_elites> best performing Circuits.
        elite_group = []
        for i in range(0, self.__n_elites):
            elite_group.append(self.__circuits[i])
        self.__log_info(3, "Elite Group:", elite_group)

        # For all the Circuits in the CircuitPopulation compare the
        # Circuit against a random elite Circuit from the group
        # generated above. If the Circuit's fitness is less than than
        # the elite's perform crossover (or clone if crossover is
        # disabled) and then mutate the Circuit.
        for ckt in self.__circuits:
            rand_elite = self.__rand.choice(elite_group)[0]
            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite:
                if self.__config.crossover_probability  == 0:
                    self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                    ckt.replace_hardware_file(rand_elite.get_hardware_filepath)
                else:
                    self.__single_point_crossover(rand_elite, ckt)
                ckt.mutate()

    # TODO Add docstring.
    def __run_fitness_proportional_selection(self):
        self.__log_event(2, "Number of Elites:", self.__n_elites)
        self.__log_event(2, "Ranked Fitness:", self.__circuits)

        # Generate a group of elites from the best n = <self.__n_elites>
        # Circuits. Based on their fitness values, map each Circuit with
        # a probabilty value (used later for crossover/copying/mutation).
        elites = {}
        elite_sum = 0
        
        for i in range(self.__n_elites):
            elites[self.__circuits[i]] = 0
            elite_sum += self.__circuits[i].get_fitness()
        if elite_sum > 0:
            for elite in elites.keys():
                elites[elite] = elite.get_fitness() / elite_sum
        elif elite_sum == 0:
            for elite in elites.keys():
                elites[elite] = 1 / self.__n_elites
        else:
            # elite_sum is negative. This should not be possible.
            self.__log_error(1, "Elite_sum is negative. Exiting...")
            exit()

        self.__log_event(3, "Elite Group:", elites.keys())
        self.__log_event(3, "Elite Probabilites:", elites.values())

        # For all Circuits in this CircuitPopulation, choose a random
        # elite (based on the associated probabilities calculated above)
        # and compare it to the Circuit. If the Circuit has lower
        # fitness than the elite, perform crossover (with the elite) and
        # mutation on it (or copy the elite's hardware if crossover is
        # disabled).
        elite_prob_sum = sum(elites.values())
        for ckt in self.__circuits:
            if elite_prob_sum > 0:
                rand_elite = self.__rand.choice(
                    list(elites.keys()),
                    self.__n_elites,
                    p=list(elites.values())
                )[0]
            else:
                rand_elite = self.__rand.choice(list(elite.keys()))[0]

            #self.__log_event(3, "Elite", rand_elite)

            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite:
                if self.__config.get_crossover_probability() == 0:
                    self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                    ckt.copy_hardware_from(rand_elite)
                else:
                    self.__single_point_crossover(rand_elite, ckt)
                    
                ckt.mutate()

    # SECTION Getters.
    # TODO Add docstring.
    def get_current_best_circuit(self):
        return self.__circuits[0]

    # TODO Add docstring.
    def get_overall_best_circuit_info(self):
        return self.__overall_best_circuit_info

    # TODO Add docstring.
    def get_current_epoch(self):
        return self.__current_epoch

    # TODO Add docstring.
    def get_best_epoch(self):
        return self.__best_epoch

    # SECTION Miscellaneous helper functions.
    def __single_point_crossover(self, source, dest):
        """
        Copy some series of chiasmas (points of genetic exchange) from fitter circuit into children
        """
        crossover_point = 0

        # Replace magic values with more generalized solutions
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            crossover_point = self.__rand.integers(1, len(self.__circuits[0].get_sim_bitstream()) - 1)
        elif self.__config.get_routing_type() == "MOORE":
            crossover_point = self.__rand.integers(1,3)
        elif self.__config.get_routing_type() == "NWSE":
            crossover_point = self.__rand.integers(13,15)
        else:
            self.__log_error(1, "Invalid routing type specified in config.ini. Exiting...")
            exit()
        dest.copy_genes_from(source, crossover_point)

    def avg_hamming_dist(self):
        """
        Calculates and returns the average Hamming distance for the population
        Currently runs in O(N^2) time
        """
        running_total = 0
        n = len(self.__circuits)
        num_pairs = n * (n-1) / 2
        for i in range(n):
            for j in range(i+1, n, 1):
                running_total = running_total + self.__single_hamming_dist(self.__circuits[i], self.__circuits[j])
        return running_total / num_pairs
    def __single_hamming_dist(self, ckt1, ckt2):
        """
        Calculates and returns the Hamming distance between two circuits
        """
        # If we are doing full simulation, need to compare array bitstreams
        # Otherwise, look at the hardware files
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            bs1 = ckt1.get_sim_bitstream()
            bs2 = ckt2.get_sim_bitstream()
        else:
            # TODO: Modify to search only for the modifiable bits: this will make the function run much faster (currently, it is very slow)
            bs1 = ckt1.get_intrinsic_modifiable_bitstream()
            bs2 = ckt2.get_intrinsic_modifiable_bitstream()
        count = 0
        for i in range(len(bs1)):
            if bs1[i] != bs2[i]:
                count = count + 1
        return count

    def count_unique(self):
        """
        Returns the number of unique files in the population
        """
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            bitstreams = []
            for ckt in self.__circuits:
                bitstreams.append(ckt.get_sim_bitstream())
            bitstreams = self.__unique(bitstreams)
            self.__log_event(2, "Number of Unique Individuals:", len(bitstreams)) 
            return len(bitstreams)
            
        # If not FULLY_SIM, then run this
        # TODO: Optimize
        bin_dir = self.__config.get_bin_directory()
        dir_list = os.listdir(bin_dir)
        files = [f for f in dir_list if os.path.isfile(str(bin_dir)+'/'+f)] # Filter out non-files
        unique_file_paths = []
        for file in files:
            full_path = str(bin_dir) + '/' + file
            not_unique = False
            for u in unique_file_paths:
                if self.__files_eq(full_path, u):
                    not_unique = True
                    break
            if not not_unique:
                unique_file_paths.append(full_path)
        self.__log_event(2, "Number of Unique Individuals:", len(unique_file_paths))
        return len(unique_file_paths)
    
    def __unique(self, arrays):
        """
        Returns an array of unique arrays from the input
        """
        soln = []
        for a in arrays:
            # Check if its in soln; if not, then add it
            shouldAdd = True
            for b in soln:
                if self.__arr_eq(a, b):
                    shouldAdd = False
                    break
            if shouldAdd:
                soln.append(a)
        return soln
        
    def __arr_eq(self, ar1, ar2):
        """
        Returns True if the arrays or equal or False otherwise
        """
        if len(ar1) != len(ar2):
            return False
        for i in range(0, len(ar1)):
            if ar1[i] != ar2[i]:
                return False
        return True
    
    def __files_eq(self, fp1, fp2):
        """
        Returns true if the files are equal (have the same content), otherwise not
        """
        content1 = []
        content2 = []
        with open(fp1, 'rb') as content:
            content1 = content.read()
        with open(fp2, 'rb') as content:
            content2 = content.read()
        return list(content1) == list(content2)

    # TODO Take a closer look at this function
    @staticmethod
    def __group(iterable, n, fillvalue=None):
        """
        Collect data into fixed-length chunks or blocks
        #grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        Taken from python recipes.
        """

        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fillvalue, *args)

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
