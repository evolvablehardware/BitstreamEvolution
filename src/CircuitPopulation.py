from os import name
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
            self.__log_error("Invalid Selection method in config.ini. Exiting...")
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
            self.__log_event("Created circuit: {0}".format(ckt))

        # Randomize initial circuits until waveform variance or
        # pulses are found
        if not self.__config.get_simulation_mode() == "FULLY_INTRINSIC":
            pass # No randomization implemented for simulation mode
        elif self.__config.get_randomization_type() == "PULSE":
            self.__log_info("PULSE randomization mode selected.")
            self.__randomize_until_pulses()
        elif self.__config.get_randomization_type() == "VARIANCE":
            self.__log_info("VARIANCE randomization mode selected.")
            if self.config.variance_threshold() <= 0:
                self.log_error(INVALID_VARIANCE_ERR_MSG)
            else:
                self.__randomize_until_variance()
        elif self.__config.get_randomization_type() == "NO":
            self.__log_info("NO randomization mode selected.")
        else:
            self.__log_error(RANDOMIZE_UNTIL_NOT_SET_ERR_MSG)

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
            self.__log_error("Attempting to evolve with empty population. Exiting...")
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
                    fitness = circuit.evaluate_variance()
                if fitness > self.__config.get_variance_threshold():
                    self.__log_event("{} fitness: {}".format(circuit, fitness))
                    return
                fitness_sum += fitness
                reevaulated_circuits.add(circuit)
            epoch_time = time() - start
            self.__circuits = reevaulated_circuits

            # If one of the new Circuits has a higher fitness than our
            # recorded best, make it the recorded best.
            best_circuit_info = self.get_overall_best_circuit_info()
            self.__log_event("Best circuit info", best_circuit_info.fitness)
            self.__log_event("Circuit 0 info", self.__circuits[0].get_fitness())
            if self.__circuits[0].get_fitness() > best_circuit_info.fitness:
                self.__overall_best_circuit_info = CircuitInfo(
                    str(self.__circuits[0]),
                    self.__circuits[0].get_fitness()
                )
                self.__best_epoch = self.get_current_epoch()
                self.__log_event("New best found")

            self.__logger.log_generation(self, epoch_time)
            self.__run_selection()
            self.__next_epoch()

            with open("workspace/bestlivedata.log", "a") as liveFile:
                avg = fitness_sum / self.__config.get_population_size()
                # Format: Epoch, Best Fitness, Worst Fitness, Average Fitness
                liveFile.write("{}, {}, {}, {}\n".format(
                    str(self.get_current_epoch()),
                    str(self.__circuits[0].get_fitness()),
                    str(self.__circuits[-1].get_fitness()),
                    str(avg)
                ))

    # SECTION Selection algorithms.
    # TODO Add docstring.
    def __run_classic_tournament(self):
        population = self.__rand.permuation(
            self.__circuits,
            k=len(self.__circuits)
        )[0]

        self.__log_event("Tournament Number:", self.get_current_epoch())

        # For all Circuits in the CircuitPopulation, take two random
        # circuits at a time from the population and compare them. Copy
        # some genes from the fittest of the two to the least fittest of
        # the two and mutate the latter.
        for ckt1, ckt2 in CircuitPopulation.__group(population, 2):
            ckt1_fitness = ckt1.get_fitness()
            ckt2_fitness = ckt2.get_fitness()
            if ckt1_fitness > ckt2_fitness:
                self.__log_event(
                    "Fitness {}: {} > Fitness {}: {}".format(
                        ckt1,
                        ckt1.get_fitness(),
                        ckt2,
                        ckt2.get_fitness()
                ))

                self.__single_point_crossover(ckt1, ckt2)
                ckt2.mutate()
            else:
                self.__log_event(
                    "Fitness {}: {} < Fitness {}: {}".format(
                        ckt1,
                        ckt1.get_fitness(),
                        ckt2,
                        ckt2.get_fitness*()
                ))

                self.__single_point_crossover(ckt2, ckt1)
                ckt1.mutate()

    # TODO Add docstring.
    def __run_single_elite_tournament(self):
        self.__log_event("Tournament Number: {}".format(str(self.get_current_epoch())))

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
                self.__log_info(ckt, "is current BEST")

    # TODO Add docstring.
    def __run_fractional_elite_tournament(self):
        self.__log_info("Number of Elites: ", str(self.__n_elites))
        self.__log_info("Ranked Fitness: ", self.__circuits)

        # Generate a group of elite Circuits from the
        # n = <self.__n_elites> best performing Circuits.
        elite_group = []
        for i in range(0, self.__n_elites):
            elite_group.append(self.__circuits[i])
        self.__log_info("Elite Group:", elite_group)

        # For all the Circuits in the CircuitPopulation compare the
        # Circuit against a random elite Circuit from the group
        # generated above. If the Circuit's fitness is less than than
        # the elite's perform crossover (or clone if crossover is
        # disabled) and then mutate the Circuit.
        for ckt in self.__circuits:
            rand_elite = self.__rand.choice(elite_group)[0]
            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite:
                if self.__config.crossover_probability  == 0:
                    self.__log_event("Cloning:", rand_elite, " ---> ", ckt)
                    ckt.replace_hardware_file(rand_elite.get_hardware_filepath)
                else:
                    self.__single_point_crossover(rand_elite, ckt)
                ckt.mutate()

    # TODO Add docstring.
    def __run_fitness_proportional_selection(self):
        self.__log_event("Number of Elites:", self.__n_elites)
        self.__log_event("Ranked Fitness:", self.__circuits)

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
            self.__log_error("Elite_sum is negative. Exiting...")
            exit()

        self.__log_event("Elite Group:", elites.keys())
        self.__log_event("Elite Probabilites:", elites.values())

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

            #self.__log_event("Elite", rand_elite)

            if ckt.get_fitness() <= rand_elite.get_fitness() and ckt != rand_elite:
                if self.__config.get_crossover_probability() == 0:
                    self.__log_event("Cloning:", rand_elite, " ---> ", ckt)
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
            crossover_point = self.__rand.integers(1, 99)
        elif self.__config.get_routing_type() == "MOORE":
            crossover_point = self.__rand.integers(1,3)
        elif self.__config.get_routing_type() == "NWSE":
            crossover_point = self.__rand.integers(13,15)
        else:
            self.__log_error("Invalid routing type specified in config.ini. Exiting...")
            exit()
        dest.copy_genes_from(source, crossover_point)

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
