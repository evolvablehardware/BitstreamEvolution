from Circuit.Circuit import Circuit
from Logger import Logger

class FullySimCircuit(Circuit):
    """
    A concrete class, the fully simulated circuit that stores its own bitstream in memory
    """

    def __init__(self, index: int, filename: str, sine_funcs, rand, logger: Logger, 
                 mutation_prob: float):
        Circuit.__init__(self, index, filename, logger)

        self.__src_sine_funcs = sine_funcs
        self.__simulation_bitstream = [0] * 100
        self._rand = rand
        self.__mutation_prob = mutation_prob
        self.randomize_bitstream()

    def mutate(self):
        """
        Mutate the simulation mode circuit
        """
        for i in range(0, len(self.__simulation_bitstream)):
            if self.__mutation_prob >= self._rand.uniform(0,1):
                # Mutate this bit
                self.__simulation_bitstream[i] = 1 - self.__simulation_bitstream[i]

    def randomize_bitstream(self):
        """
        Fully randomize the simulation mode circuit
        """
        for i in range(0, len(self.__simulation_bitstream)):
            self.__simulation_bitstream[i] = self._rand.integers(0, 2)

    def crossover(self, parent, crossover_point: int):
        """
        Simulated crossover, pulls first n bits from parent and remaining from self
        
        Parameters
        ----------
        parent : Circuit
            The other circuit the crossover is performed with
        crossover_point : int
            The index in the editable bitstream the crossover occours at
        """
        for i in range(0, crossover_point):
            self.__simulation_bitstream[i] = parent.__simulation_bitstream[i]
        # Remaining bits left unchanged

    def copy_from(self, other):
        for i in range(0, len(other.__simulation_bitstream)):
            self.__simulation_bitstream[i] = other.__simulation_bitstream[i]

    def upload(self):
        # Doesn't need to do anything, runs locally
        pass

    def get_bitstream(self) -> list[int]:
        return self.__simulation_bitstream
    
    def inject_bitstream(self, bitstream: list[int]):
        self.__simulation_bitstream = bitstream

    def get_file_attribute(self, attribute: str) -> str | None:
        return None
