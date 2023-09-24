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
import random
import math
from mmap import mmap

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
CIRCUIT_FILE_BASENAME = "hardware"

ELITE_MAP_SCALE_FACTOR = 50

# Create a named tuple for easy and clear storage of information about
# a Circuit (currently its name and fitness)
CircuitInfo = namedtuple("CircuitInfo", ["name", "fitness"])

# Named tuple for circuit's path and fitness; currently only used for combining populations
CircuitPathInfo = namedtuple("CircuitPathInfo", ["path", "fitness"])

ELITE_MAP_SCALE_FACTOR = 50

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
        elif config.get_selection_type() == "RANK_PROP_SEL":
            self.__run_selection = self.__run_rank_proportional_selection
        elif config.get_selection_type() == "MAP_ELITES":
            self.__run_selection = self.__run_map_elites_selection
        else:
            self.__log_error(
                1, "Invalid Selection method in config.ini. Exiting...")
            exit()

        elitism_fraction = config.get_elitism_fraction()
        population_size = config.get_population_size()
        self.__n_elites = int(ceil(elitism_fraction * population_size))

    @staticmethod
    def __wipe_folder(dir):
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

    def populate(self):
        """
        Creates initial population.
        """
        # Always creates a circuit with the seed file, but if we have certain randomization
        # modes then perform necessary operations

        sine_funcs = []
        self.__sine_strs = []
        for i in range(100):
            # Don't let amplitude and y-offset get too out of hand
            a = random.uniform(0, 100)
            b = random.uniform(0.02, 2)
            c = (random.randint(0, 7) / 8) * (2 * math.pi / b)
            d = random.uniform(100, 900)
            # We provide many parameters with default values here, because Python closures
            # work like JS using the "var" keyword, and do not "properly" create environments the way we'd expect
            # For this reason, we add default parameters, providing our current var values to them
            # This works because the variable values are then *evaluated* as the lambda (closure) is constructed
            # Before this fix, we had a bug where every single sine function would be exactly the same;
            # all holding a/b/c/d values from the very last function to be generated
            sine_funcs.append((lambda x,a=a,b=b,c=c,d=d: a * math.sin(b * (x + c)) + d))
            sine_str = "Sine function: " + str(i) + " | y = " + str(a) + " * sin(" + str(b) + " * (x + " + str(c) + ")) + " + str(d)
            self.__sine_strs.append(sine_str)

        # Wipe the current folder, so if we go from 100 circuits in one experiment to 50 in the next,
        # we don't still have 100 (with 50 that we use and 50 residual ones)
        CircuitPopulation.__wipe_folder(self.__config.get_asc_directory())
        CircuitPopulation.__wipe_folder(self.__config.get_bin_directory())
        CircuitPopulation.__wipe_folder(self.__config.get_data_directory())

        self.__multiple_populations = False
        if self.__config.get_init_mode() == "EXISTING_POPULATION":
            # Need to assign where each circuit gets its source from
            # Get number of subpopulations, then grab random circuits from each
            subdirectories = next(os.walk(self.__config.get_src_pops_dir()))[1]
            subdirectory_files = list(map(lambda dir: next(os.walk(self.__config.get_src_pops_dir().joinpath(dir)))[2], subdirectories))
            self.__num_subpops = len(subdirectories)
            self.__multiple_populations = True
            # Existing population setting, load in all circuits from each population and get the ones with the highest fitness
            # If any are missing the fitness measure, then we will randomly select them.
            # We could manually measure their fitnesses, but as of now we've decided that is too slow
            all_subdir_circuits = []
            for i in range(len(subdirectories)):
                # Load every circuit
                subdir_circuits = SortedKeyList(
                    key=lambda ckt: -ckt.fitness
                )
                for file in subdirectory_files[i]:
                    path = self.__config.get_src_pops_dir().joinpath(subdirectories[i]).joinpath(file)
                    hw_file = open(path, "r+")
                    mmapped_file = mmap(hw_file.fileno(), 0)
                    hw_file.close()
                    fitness = float(Circuit.get_file_attribute_st(mmapped_file, "fitness"))
                    if fitness == None:
                        fitness = 0
                    subdir_circuits.add(CircuitPathInfo(path, fitness))

                all_subdir_circuits.append(subdir_circuits)
            subdirectory_index = 0

        for index in range(1, self.__config.get_population_size() + 1):
            file_name = "hardware" + str(index)
            if self.__config.get_init_mode() == "EXISTING_POPULATION":
                # Grab the top circuit from the current population, unless it is empty, then we'll jump to the next one
                while len(all_subdir_circuits[subdirectory_index]) <= 0:
                    subdirectory_index = (subdirectory_index + 1) % len(all_subdir_circuits)
                seedArg = all_subdir_circuits[subdirectory_index].pop(0).path
                subdirectory_index = (subdirectory_index + 1) % len(all_subdir_circuits)
            else:
                seedArg = SEED_HARDWARE_FILEPATH
            ckt = Circuit(
                index,
                file_name,
                seedArg,
                self.__microcontroller,
                self.__logger,
                self.__config,
                self.__rand,
                sine_funcs
            )
            if self.__config.get_init_mode() == "RANDOM":
                ckt.randomize_bits()
            elif self.__config.get_init_mode() == "CLONE_SEED_MUTATE":
                # Call mutate once on this circuit
                ckt.mutate()
            elif self.__config.get_init_mode() == "EXISTING_POPULATION":
                # Make sure the circuit puts a line at the top of its .asc file denoting the source population
                ckt.set_file_attribute('src_population', str(subdirectory_index))

            self.__circuits.add(ckt)
            self.__log_event(3, "Created circuit: {0}".format(ckt))

        # If map-elites selection method selected, then randomly generate until we fill up 25% of the map
        '''if self.__config.get_selection_type() == 'MAP_ELITES':
            self.__log_event(1, 'Randomizing until map is 25% full...')
            elites = list(filter(lambda x: x != 0, [j for sub in self.__generate_map() for j in sub]))
            elite_count = len(elites)
            while elite_count < 0.1 * (21 * 21 / 2):
                self.__log_event(3, "Got %s%% (%s)" % (elite_count / (21*21/2) * 100, elite_count))
                # Need to mutate non-elites
                for ckt in self.__circuits:
                    if not ckt in elites:
                        ckt.copy_sim(random.choice(elites))
                        ckt.mutate()
                        #ckt.randomize_bits()
                        ckt.evaluate_sim(False)

                elite_map = self.__generate_map()
                elites = list(filter(lambda x: x != 0, [j for sub in elite_map for j in sub]))
                elite_count = len(elites)
                self.__output_map_file(elite_map)'''

        # Randomize initial circuits until waveform variance or
        # pulses are found
        if self.__config.get_simulation_mode() != "FULLY_INTRINSIC":
            pass # No randomization implemented for simulation mode
        elif self.__config.get_randomization_type() == "PULSE":
            self.__log_info(1, "PULSE randomization mode selected.")
            self.__randomize_until_pulses()
        elif self.__config.get_randomization_type() == "VARIANCE":
            self.__log_info(1, "VARIANCE randomization mode selected.")
            if self.__config.get_randomize_threshold() <= 0:
                self.log_error(INVALID_VARIANCE_ERR_MSG)
            else:
                self.__randomize_until_variance()
        elif self.__config.get_randomization_type() == "VOLTAGE":
            self.__randomize_until_voltage()
        elif self.__config.get_randomization_type() == "NO":
            self.__log_info(1, "NO randomization mode selected.")
        else:
            self.__log_error(1, RANDOMIZE_UNTIL_NOT_SET_ERR_MSG)

        # Output the first data point to live data files
        self.__write_to_livedata()

    def __randomize_until_pulses(self):
        """
        Randomizes population until minimum variance is found
        """
        no_pulses_generated = True
        while no_pulses_generated:
            # NOTE Randomize until pulses will continue mutating and
            # not revert to the original seed-hardware until restarting
            self.__log_event(3, "Randomizing to generate pulses")
            for circuit in self.__circuits:
                circuit.randomize_bits()
                fitness = circuit.evaluate_pulse_count()
                var_th = self.__config.get_randomize_threshold()
                if (fitness > var_th):
                    no_pulses_generated = False
                    self.__log_info(1, "Pulse generated! Exiting randomization. Fitness:", fitness)
                    break
    
    def __randomize_until_voltage(self):
        """
        Randomizes population until a mean voltage is found near the desired value
        """
        while True:
            self.__log_event(3, "Randomizing to get voltage")
            for circuit in self.__circuits:
                circuit.randomize_bits()
                mean_voltage = circuit.measure_mean_voltage()
                if (abs(mean_voltage - 341) < 10):
                    self.__log_info(1, "Voltage Achieved! Exiting randomization. Voltage:", mean_voltage)
                    break

    # NOTE This is whole function going to be upgraded to handle a from-scratch circuit seeding process.
    # https://github.com/evolvablehardware/BitstreamEvolution/issues/3
    def __randomize_until_variance(self):
        """
        Randomizes population until minimum variance is found
        """
        # Variance threshold is the desired variance
        bestVariance = 0
        variance = 0
        while bestVariance < self.__config.get_randomize_threshold():
            self.__log_event(3, "Randomizing to generate variance")
            for circuit in self.__circuits:
                circuit.randomize_bits()
                variance = circuit.evaluate_variance()
                self.__log_info(3, "Variance generated:", variance)

                with open("workspace/randomizationdata.log", "a") as liveFile:
                    liveFile.write(str(variance) + "\n")

                if variance > bestVariance:
                    self.__log_info(3, "New best variance: ", variance)
                    bestVariance = variance
                    self.__overall_best_circuit_info = CircuitInfo(str(circuit), variance)
                    copyfile(circuit.get_hardware_file_path(), self.__config.get_best_file())
                    break

        self.__log_info(3, "Variance generated! Exiting randomization. Fitness:", variance)

    def __next_epoch(self):
        """
        Moves to the next generation/epoch
        Currently, only needs to increase the generation by 1
        All other generation-specific behavior will be derived from this value
        """
        self.__current_epoch += 1

    def __should_continue_evo(self):
        should_continue = True
        if self.__config.using_n_generations():
            if self.get_current_epoch() >= self.__config.get_n_generations():
                should_continue = False
        if self.__config.using_target_fitness():
            if self.__overall_best_circuit_info.fitness >= self.__config.get_target_fitness():
                should_continue = False
        return should_continue

    def __eval_ckt(self, circuit):
        # Biggest difference between Fully Instrinsic and Hardware Sim: The fitness evaluation
        fitness = 0
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            func = self.__config.get_fitness_func()
            fitness = circuit.evaluate_sim(func == "COMBINED")
        elif self.__config.get_simulation_mode() == "SIM_HARDWARE":
            fitness = circuit.evaluate_sim_hardware()
        else:
            func = self.__config.get_fitness_func()
            if func == "PULSE_COUNT":
                fitness = circuit.evaluate_pulse_count()
            elif func == "VARIANCE":
                fitness = circuit.evaluate_variance()
            elif func == "COMBINED":
                fitness = circuit.evaluate_combined()
            #fitness = circuit.evaluate_variance()
        return fitness

    def evolve(self):
        """
        Runs an evolutionary loop and records the circuit with the highest fitness throughout the loop,
        while also storing statistics in a file for the plot to access
        """
        if len(self.__circuits) == 0:
            self.__log_error(
                1, "Attempting to evolve with empty population. Exiting...")
            exit()

        # Set initial values for 'best' data
        self.__overall_best_circuit_info = CircuitInfo(
            str(self.__circuits[0]),
            self.__circuits[0].get_fitness()
        )
        self.__best_epoch = 0
        self.__next_epoch()

        while(self.__should_continue_evo()): #self.get_current_epoch() < self.__config.get_n_generations()):

            #self.__log_event(3, "Starting evo cycle", self.get_current_epoch(
            #), "<", self.__config.get_n_generations(), "?")

            # Since sortedcontainers don't update when the value by
            # which an item is sorted gets updated, we have to add the
            # Circuits to a new list after we evaluate them and then
            # make the new list the working Circuit list.
            reevaulated_circuits = SortedKeyList(
                key=lambda ckt: -ckt.get_fitness()
            )

            # Evaluate all the Circuits in this CircuitPopulation.
            start = time()
            for circuit in self.__circuits:
                # If evaluate returns true, then a circuit has surpassed
                # the threshold and we are done.

                fitness = self.__eval_ckt(circuit)

                # We've got the fitness we're evaluating the circuit off of, so make sure it gets
                # added to the circuit's file attributes
                # Only if we are in a sim mode with circuit files
                if self.__config.get_simulation_mode() != 'FULLY_SIM':
                    circuit.set_file_attribute("fitness", str(fitness))

                # Commented out for now while we test
                # Pretty sure this was originally for pulse count only, leaving it commented out since things are working right now
                '''if fitness > self.__config.get_randomize_threshold():
                    self.__log_event(1, "{} fitness: {}".format(circuit, fitness))
                    return'''
                reevaulated_circuits.add(circuit)
            epoch_time = time() - start
            self.__circuits = reevaulated_circuits

            # If one of the new Circuits has a higher fitness than our
            # recorded best, make it the recorded best.
            best_circuit_info = self.get_overall_best_circuit_info()
            self.__log_event(2, "Best circuit info", best_circuit_info.fitness)
            self.__log_event(2, "Circuit 0 info",
                             self.__circuits[0].get_fitness())
            if self.__circuits[0].get_fitness() > best_circuit_info.fitness:
                self.__overall_best_circuit_info = CircuitInfo(
                    str(self.__circuits[0]),
                    self.__circuits[0].get_fitness()
                )
                self.__best_epoch = self.get_current_epoch()
                # Copy this circuit to the best file
                copyfile(self.__circuits[0].get_hardware_file_path(), self.__config.get_best_file())
                self.__log_event(2, "New best found")

            self.__logger.log_generation(self, epoch_time)
            # The circuits that are protected from randomization
            self.__protected_elites = []
            self.__run_selection()

            # Remove bottom X% of population to replace with random circuits
            # (just randomize bitstream of the bottom X%)
            if self.__config.get_random_injection() > 0:
                amt = int(self.__config.get_random_injection() * self.__config.get_population_size())
                circuits_to_randomize = self.__circuits[-amt:]
                for ckt in circuits_to_randomize:
                    if ckt not in self.__protected_elites:
                        ckt.randomize_bits()

            self.__write_to_livedata()
            self.__next_epoch()

        # We have finished evolution! Lets quickly re-evaluate the top circuit, since it
        # will then output its waveform
        self.__eval_ckt(self.__circuits[0])


    def __write_to_livedata(self):
        '''
        Runs each generation to write data to live data files
        '''
        fitness_sum = 0
        for c in self.__circuits:
            fitness_sum = fitness_sum + c.get_fitness()
        # Calculate the diversity measure
        diversity = 0
        if self.__config.get_diversity_measure() == "HAMMING_DIST":
            diversity = self.avg_hamming_dist()
        elif self.__config.get_diversity_measure() == "UNIQUE":
            diversity = self.count_unique()
        # Providing any invalid measure of diversity will make it constantly 0
        # Write the generation data (avg/best/worst fitness, etc) to file
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
        
        if self.__multiple_populations:
            # Write the population counts to file (i.e. count of circuits from each source population)
            with open("workspace/poplivedata.log", "a") as live_file:
                counts = [0] * self.__num_subpops
                for ckt in self.__circuits:
                    population = int(ckt.get_file_attribute('src_population'))
                    counts[population] = counts[population] + 1
                live_file.write(("{} " * self.__num_subpops + "\n").format(*counts))

        if (self.__current_epoch > 0):
            with open("workspace/violinlivedata.log", "a") as live_file:
                fits = []
                for ckt in self.__circuits:
                    fits.append(str(ckt.get_fitness()))
                live_file.write(("{}:{}\n").format(self.__current_epoch, ",".join(fits)))
            
            if self.__config.get_simulation_mode() == "FULLY_INTRINSIC":
                with open("workspace/heatmaplivedata.log", "a") as live_file2:
                    best = self.__circuits[0]
                    live_file2.write(("{}:{}\n").format(self.__current_epoch, ",".join(best.get_waveform())))


    # SECTION Selection algorithms.
    def __run_classic_tournament(self):
        """
        Randomly pairs together circuits, compares their fitness, and preforms crossover on and mutates the "loser"
        """
        population = self.__rand.permutation(self.__circuits)

        self.__log_event(3, "Tournament Number:", self.get_current_epoch())

        # For all Circuits in the CircuitPopulation, take two random
        # circuits at a time from the population and compare them. Copy
        # some genes from the fittest of the two to the least fittest of
        # the two and mutate the latter.
        for ckt1, ckt2 in CircuitPopulation.__group(population, 2):
            winner = ckt1
            loser = ckt2
            if ckt2.get_fitness() > ckt1.get_fitness():
                winner = ckt2
                loser = ckt1

            self.__log_event(3,
                            "Fitness {}: {} < Fitness {}: {}".format(
                                loser,
                                loser.get_fitness(),
                                winner,
                                winner.get_fitness()
                            ))

            if self.__rand.uniform(0, 1) <= self.__config.get_crossover_probability():
                self.__single_point_crossover(winner, loser)
            else:
                self.__log_event(3, "Cloning:", winner, " ---> ", loser)
                loser.copy_hardware_from(winner)

            loser.mutate()


    def __run_single_elite_tournament(self):
        """
        Mutates the hardware of every circuit that is not the current best circuit
        """
        self.__log_event(3, "Tournament Number: {}".format(
            str(self.get_current_epoch())))

        best = self.__circuits[0]
        self.__protected_elites.append(best)
        for ckt in self.__circuits:
            # Mutate the hardware of every circuit that is not the best
            if ckt != best:
                if ckt.get_fitness() <= best.get_fitness():
                    #ckt.copy_hardware_from(best)
                    ckt.mutate()
            else:
                self.__log_info(2, ckt, "is current BEST")

    def __run_fitness_proportional_selection(self):
        """
        Compares every circuit in the population to a random elite (chosen proportionally based on each elite's fitness).
        If circuit has a lower fitness, crossover or mutate the circuit
        """
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

        self.__log_event(2, "Elite Group:", elites.keys())
        self.__log_event(2, "Elite Probabilites:", elites.values())
        self.__protected_elites = elites.keys()

        # For all Circuits in this CircuitPopulation, choose a random
        # elite (based on the associated probabilities calculated above)
        # and compare it to the Circuit. If the Circuit has lower
        # fitness than the elite, perform crossover (with the elite) and
        # mutation on it (or copy the elite's hardware if crossover is
        # disabled).
        elite_prob_sum = sum(elites.values())
        for ckt in self.__circuits:
            if self.__n_elites != 0:
                if elite_prob_sum > 0:
                    rand_elite = self.__rand.choice(
                        list(elites.keys()),
                        self.__n_elites,
                        p=list(elites.values())
                    )[0]
                else:  # If fitness isn't negative, this should never happen
                    rand_elite = self.__rand.choice(list(elites.keys()))[0]
            else:
                rand_elite = self.__rand.choice(self.__circuits)

            self.__log_event(4, "Elite", rand_elite)

            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite and ckt not in elites:
                # if self.__config.get_crossover_probability() == 0:
                # 	self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                # 	ckt.copy_hardware_from(rand_elite)
                # else:
                # 	self.__single_point_crossover(rand_elite, ckt)
                if self.__rand.uniform(0, 1) <= self.__config.get_crossover_probability():
                    self.__single_point_crossover(rand_elite, ckt)
                else:
                    self.__log_event(4, "Cloning:", rand_elite, " ---> ", ckt)
                    ckt.copy_hardware_from(rand_elite)
                ckt.mutate()

    def __run_rank_proportional_selection(self):
        '''
        Compares every circuit in the population to a random elite (chosen proportionally based on each elite's rank).
        If circuit has a lower fitness, crossover or mutate the circuit
        '''
        self.__log_event(2, "Number of Elites:", self.__n_elites)
        self.__log_event(2, "Ranked Fitness:", self.__circuits)

        # Generate a group of elites from the best n = <self.__n_elites>
        # Circuits. Based on their fitness values, map each Circuit with
        # a probabilty value (used later for crossover/copying/mutation).
        elites = {}
        # can use summation formula since sum of ranks is the sum of natural numbers
        elite_sum = (self.__n_elites) * (self.__n_elites + 1) / 2
        if (elite_sum > 0):
            for i in range(self.__n_elites):
                # Using (self.__n_elites - i) since highest ranked indiviual is at self.__circuits[0]
                elites[self.__circuits[i]] = (self.__n_elites - i) / elite_sum
        else:
            # elite_sum is negative. This should not be possible.
            self.__log_error(1, "Elite_sum is zero or negative. Exiting...")
            exit()

        self.__log_event(3, "Elite Group:", elites.keys())
        self.__log_event(3, "Elite Probabilites:", elites.values())
        self.__protected_elites = elites.keys()
        #self.__log_event(3, "Elite", rand_elite)

        # For all Circuits in this CircuitPopulation, choose a random
        # elite (based on the associated probabilities calculated above)
        # and compare it to the Circuit. If the Circuit has lower
        # fitness than the elite, perform crossover (with the elite) and
        # mutation on it (or copy the elite's hardware if crossover is
        # disabled).
        elite_prob_sum = sum(elites.values())
        for ckt in self.__circuits:
            if self.__n_elites != 0:
                if elite_prob_sum > 0:
                    rand_elite = self.__rand.choice(
                        list(elites.keys()),
                        self.__n_elites,
                        p=list(elites.values())
                    )[0]
                else:  # If fitness isn't negative, this should never happen
                    rand_elite = self.__rand.choice(list(elites.keys()))[0]
            else:
                rand_elite = self.__rand.choice(self.__circuits)

            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite and ckt not in elites:
                # if self.__config.get_crossover_probability() == 0:
                #     self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                #     ckt.copy_hardware_from(rand_elite)
                # else:
                #     self.__single_point_crossover(rand_elite, ckt)

                if self.__rand.uniform(0, 1) <= self.__config.get_crossover_probability():
                    self.__single_point_crossover(rand_elite, ckt)
                else:
                    self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                    ckt.copy_hardware_from(rand_elite)
                ckt.mutate()

    def __run_fractional_elite_tournament(self):
        """
        Compares every circuit in the population to a random elite. If circuit has a lower fitness, crossover or mutate the circuit
        """
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
        self.__protected_elites = elite_group
        for ckt in self.__circuits:
            rand_elite = self.__rand.choice(elite_group)
            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite and ckt not in elite_group:
                # if self.__config.crossover_probability  == 0:
                #     self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                #     ckt.replace_hardware_file(rand_elite.get_hardware_filepath)
                # else:
                #     self.__single_point_crossover(rand_elite, ckt)

                if self.__rand.uniform(0, 1) <= self.__config.get_crossover_probability():
                    self.__single_point_crossover(rand_elite, ckt)
                else:
                    self.__log_event(3, "Cloning:", rand_elite, " ---> ", ckt)
                    ckt.copy_hardware_from(rand_elite)
                ckt.mutate()

    def __run_map_elites_selection(self):
        """
        This version of map elites will protect the highest-fitness individual in each "square"
        We're going to have slightly granular squares to make sure that circuits have room to spread out early
        to hopefully promote diversity
        Group size length of 50 means we'll have 21x21 groups
        """

        elite_map = self.__generate_map()
        # Clone to all non-elites and mutate
        elites = list(filter(lambda x: x != 0, [j for sub in elite_map for j in sub]))

        self.__protected_elites = elites

        for ckt in self.__circuits:
            # If not an elite, then we will clone and mutate
            if ckt not in elites:
                rand_elite = self.__rand.choice(elites)
                ckt.copy_hardware_from(rand_elite)
                ckt.mutate()
        
        self.__output_map_file(elite_map)

    def __output_map_file(self, elite_map):
        with open("workspace/maplivedata.log", "w+") as liveFile:
            # First line describes granularity/scale factor
            liveFile.write("{}\n".format(str(ELITE_MAP_SCALE_FACTOR)))
            # If square is empty, write a "blank" to that line
            for r in range(len(elite_map)):
                sl = elite_map[r]
                for c in range(len(sl)):
                    ckt = sl[c]
                    to_write = ""
                    if ckt != 0:
                        to_write = str(ckt.get_fitness())
                    liveFile.write("{} {} {}\n".format(r, c, to_write))

    def __generate_map(self):
        """
        Generates the elite map for this generation
        """
        # If the value is not a circuit (i.e. it is 0) then we know the spot is open to be filled in
        # Go up to 21 since upper bound is 1024
        # Can't do [[0]*21]*21 because this will make all the sub-arrays point to same memory location
        elite_map = []
        for i in range(22):
            elite_map.append([0]*21)
        # Evaluate each circuit's fitness and where it falls on the elite map
        # Populate elite map first
        for ckt in self.__circuits:
            row = math.floor(ckt.get_low_value() / ELITE_MAP_SCALE_FACTOR)
            col = math.floor(ckt.get_high_value() / ELITE_MAP_SCALE_FACTOR)
            if elite_map[row][col] == 0 or ckt.get_fitness() > elite_map[row][col].get_fitness():
                elite_map[row][col] = ckt
        return elite_map

    # SECTION Getters.
    def get_current_best_circuit(self):
        """
        Returns the circuit in the current generation with the highest fitness
        """
        return self.__circuits[0]

    def get_overall_best_circuit_info(self):
        """
        Returns the information of the circuit with the highest fitness throughout the run 
        """
        return self.__overall_best_circuit_info

    def get_current_epoch(self):
        """
        Returns the generation number
        """
        return self.__current_epoch

    def get_best_epoch(self):
        """
        Returns the generation number that contained the circuit with the highest fitness
        """
        return self.__best_epoch

    # SECTION Miscellaneous helper functions.
    def __single_point_crossover(self, source, dest):
        """
        Copy some series of chiasmas (points of genetic exchange) from fitter circuit into children
        """
        crossover_point = 0

        # Replace magic values with more generalized solutions
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            crossover_point = self.__rand.integers(
                1, len(self.__circuits[0].get_sim_bitstream()) - 1)
        elif self.__config.get_routing_type() == "MOORE":
            crossover_point = self.__rand.integers(1, 3)
        elif self.__config.get_routing_type() == "NWSE":
            crossover_point = self.__rand.integers(13, 15)
        else:
            self.__log_error(
                1, "Invalid routing type specified in config.ini. Exiting...")
            exit()
        dest.copy_genes_from(source, crossover_point)

    def avg_hamming_dist(self):
        """
        Calculates and returns the average Hamming distance for the population
        """
        running_total = 0
        n = len(self.__circuits)
        num_pairs = n * (n-1) / 2

        self.__log_event(4, "Starting Hamming Distance Calculation")

        bitstreams = []
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            bitstreams = map(lambda c: c.get_sim_bitstream(), self.__circuits)
        else:
            # Need to convert the char byte values to 0s and 1s along the way
            bitstreams = map(lambda c: list(map(
                lambda char: char-48, c.get_intrinsic_modifiable_bitstream())), self.__circuits)
        bitstreams = list(bitstreams)

        # We now have all the bitstreams, we can do the faster hamming calculation by comparing each bit of them
        # Then we multiply the count of 1s for that bit by the count of 0s for that bit and add it to the running_total
        # Divide that by # of pairs at the end (calculation shown below)
        running_total = 0
        n = len(self.__circuits)
        num_pairs = n * (n-1) / 2
        self.__log_event(4, "HDIST - Entering loop")
        for i in range(len(bitstreams[0])):
            ones_count = 0
            zero_count = 0
            for j in range(n):
                if bitstreams[j][i] == 0:
                    zero_count = zero_count + 1
                else:
                    ones_count = ones_count + 1
            running_total = running_total + ones_count * zero_count

        running_total = running_total / num_pairs
        self.__log_event(4, "HDIST - Final value", running_total)
        return running_total

    def count_unique(self):
        """
        Returns the number of unique files in the population
        """
        if self.__config.get_simulation_mode() == "FULLY_SIM":
            bitstreams = []
            for ckt in self.__circuits:
                bitstreams.append(ckt.get_sim_bitstream())
            bitstreams = self.__unique(bitstreams)
            self.__log_event(
                2, "Number of Unique Individuals:", len(bitstreams))
            return len(bitstreams)

        # If not FULLY_SIM, then run this
        # TODO: Optimize
        bin_dir = self.__config.get_bin_directory()
        dir_list = os.listdir(bin_dir)
        files = [f for f in dir_list if os.path.isfile(
            str(bin_dir)+'/'+f)]  # Filter out non-files
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
        self.__log_event(2, "Number of Unique Individuals:",
                         len(unique_file_paths))
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
        Returns true if the files are equal (have the same content)
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
