from pathlib import Path
from random import Random
from typing import Protocol
from BitstreamEvolutionProtocols import Circuit, Individual, Population
from Circuit.FileBasedCircuit import FileBasedCircuit
from Directories import Directories
from Individual.BitstreamIndividual import BitstreamIndividual
from Logger import Logger
from utilities import wipe_folder
import os

SEED_HARDWARE_FILEPATH = Path("data/seed-hardware.asc")

# File for implementations of GenerateInitialPopulations

class GenerateInitialPopulations(Protocol):
    "Somehow gets you an initial implementation."
    def generate(self) -> list[Population]: ...

class GenerateInitialPopulation(Protocol):
    "The special case of GenerateInitialPopulations that constructs only a single population"
    def generate(self) -> Population: ...

class GenerateSinglePopulationWrapper:
    """
    A wrapper around GenerateInitialPopulation (singular) that follows
    GenerateInitialPopulations (plural) which is the protocol used in Evolution
    Returns a one-element list of the population created
    Example Usage: Evolution(..., GenerateSinglePopulationWrapper(GenerateRandomPopulation(...)), ...)
    """
    def __init__(self, gen_func: GenerateInitialPopulation):
        self.__gen_func = gen_func
    def generate(self) -> list[Population]:
        return [self.__gen_func.generate()]

class PostConstructionStrategy(Protocol):
    '''Consumes the incoming parameter'''
    def run(self, individual: BitstreamIndividual) -> BitstreamIndividual: ...

class RandomizationStrategy(Protocol):
    '''Consumes the incoming parameter'''
    def randomize(self, individuals: list[BitstreamIndividual]) -> list[BitstreamIndividual]: ...

class GenerateBitstreamPopulation:
    # force everything to be passed by keyword
    def __init__(self, *, sz: int, bitstream_sz: int,
                 post_construction_strategy: PostConstructionStrategy,
                 randomization_strategy: RandomizationStrategy,
                 mutation_prob: float, rand: Random):
        self.__sz = sz
        self.__bitstream_sz = bitstream_sz
        self.__post_construction_strategy = post_construction_strategy
        self.__randomization_strategy = randomization_strategy
        self.__rand = rand

        self.__mutation_prob = mutation_prob
        
    def generate(self) -> Population:
        """
        Creates initial population based on the config.
        1. Clears the files used to keep track of circuit
        2. Uses appropriate initialization method specified by config.
        3. Handles randomization until condition in config is met.
        """

        individuals = []

        for index in range(1, self.__sz + 1):
            individual = BitstreamIndividual(self.__bitstream_sz, self.__rand, self.__mutation_prob)
            individual = self.__post_construction_strategy.run(individual)

            individuals.append(individual)

        circuits = self.__randomization_strategy.randomize(individuals)

        return Population(circuits, None)

# used for CLONE_SEED
class NoPostConstructionStrategy:
    def run(self, individual: BitstreamIndividual) -> BitstreamIndividual:
        return individual

# used for CLONE_SEED_MUTATE
class MutateOncePostConstructionStrategy:
    def run(self, individual: BitstreamIndividual) -> BitstreamIndividual:
        individual.mutate()
        return individual
    
# used for RANDOM
class RandomizeBitstreamPostConstructionStrategy:
    def run(self, individual: BitstreamIndividual) -> BitstreamIndividual:
        individual.randomize()
        return individual

class NoRandomizationStrategy:
    def randomize(self, individuals: list[BitstreamIndividual]) -> list[BitstreamIndividual]:
        return individuals

class FileBasedCircuitFactory:
    def __init__(self, *, sz: int, logger: Logger, directories: Directories, routing_type: str, accessed_columns: list[int]):
        self.__logger = logger
        self.__directories = directories
        self.__routing_type = routing_type
        self.__accessed_columns = accessed_columns

        wipe_folder(self.__directories.asc_dir)
        wipe_folder(self.__directories.bin_dir)
        wipe_folder(self.__directories.data_dir)

        self.__circuits = []
        for i in range(sz):
            circuit = FileBasedCircuit(
                index=i,
                filename="hardware" + str(i),
                template=SEED_HARDWARE_FILEPATH,
                logger=self.__logger,
                directories=self.__directories,
                routing_type=self.__routing_type,
                accessed_columns=self.__accessed_columns
            )
            self.__circuits.append(circuit)

    def create(self, populations: list[Population]) -> dict[Circuit, list[tuple[Population, Individual]]]:
        res: dict[Circuit, list[tuple[Population, Individual]]] = {}
        index = 0
        for p in populations:
            pop = p.population_list
            for (individual, _) in pop:
                circuit = self.__circuits[index]
                bitstream: list[bool] = individual.get_bitstream() # type: ignore
                circuit.set_bitstream(bitstream)
                res[circuit] = [(p, individual)]
                index += 1

        return res

# TODO: to add in randomize_until modes, we need a way to get circuit fitness/measurements AT initialization time
