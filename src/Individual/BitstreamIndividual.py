from random import Random

class BitstreamIndividual:
    def __init__(self, bitstream_sz: int, rand: Random, mutation_probability: float):
        self.__bitstream: list[bool] = [False] * bitstream_sz
        self.__rand = rand
        self.__mutation_probability = mutation_probability

    def set_bitstream(self, bitstream: list[bool]):
        self.__bitstream = bitstream
    
    def get_bitstream(self) -> list[bool]:
        return self.__bitstream
    
    def mutate(self):
        for i in range(len(self.__bitstream)):
            if self.__mutation_probability >= self.__rand.uniform(0,1):
                self.__bitstream[i] = not self.__bitstream[i]

    def crossover(self, parent: 'BitstreamIndividual', crossover_point: int):
        first = self.__bitstream[0:crossover_point]
        second = parent.__bitstream[crossover_point:]
        new_bitstream = first + second
        self.set_bitstream(new_bitstream)

    def randomize(self):
        for i in range(len(self.__bitstream)):
            if self.__rand.randint(0, 1) == 0:
                self.__bitstream[i] = False
            else:
                self.__bitstream[i] = True

    def copy_from(self, other: 'BitstreamIndividual'):
        self.__bitstream = other.__bitstream.copy()
    