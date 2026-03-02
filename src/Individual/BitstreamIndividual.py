"""Individual representation for evolutionary bitstream experiments.

Each individual wraps a boolean bitstream that maps to an FPGA circuit
configuration. Provides mutation, crossover, and randomization operators
used by the population initialization and reproduction strategies.
"""

from random import Random


class BitstreamIndividual:
    """A genetic individual whose genome is a list of boolean bits.

    Used by :class:`~Population.PopulationInitialization.GenerateBitstreamPopulation`
    to create populations, and by reproducers to generate offspring.
    """
    def __init__(self, bitstream_sz: int, rand: Random, mutation_probability: float):
        """Create an individual with a zeroed bitstream of the given size."""
        self.__bitstream: list[bool] = [False] * bitstream_sz
        self.__rand = rand
        self.__mutation_probability = mutation_probability

    def set_bitstream(self, bitstream: list[bool]):
        """Replace the entire bitstream with the provided list."""
        self.__bitstream = bitstream

    def get_bitstream(self) -> list[bool]:
        """Return the current bitstream."""
        return self.__bitstream

    def mutate(self):
        """Flip each bit independently with the configured mutation probability."""
        for i in range(len(self.__bitstream)):
            if self.__mutation_probability >= self.__rand.uniform(0,1):
                self.__bitstream[i] = not self.__bitstream[i]

    def crossover(self, parent: 'BitstreamIndividual', crossover_point: int):
        """Single-point crossover: take bits before *crossover_point* from self and the rest from *parent*."""
        first = self.__bitstream[0:crossover_point]
        second = parent.__bitstream[crossover_point:]
        new_bitstream = first + second
        self.set_bitstream(new_bitstream)

    def randomize(self):
        """Set every bit to a uniformly random value."""
        for i in range(len(self.__bitstream)):
            if self.__rand.randint(0, 1) == 0:
                self.__bitstream[i] = False
            else:
                self.__bitstream[i] = True

    def copy_from(self, other: 'BitstreamIndividual'):
        """Deep-copy the bitstream from *other* into this individual."""
        self.__bitstream = other.__bitstream.copy()
    