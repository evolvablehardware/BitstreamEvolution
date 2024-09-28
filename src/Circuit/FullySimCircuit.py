from Circuit import Circuit
import Config

class FullySimCircuit(Circuit):
    """
    A concrete class, the fully simulated circuit that stores its own bitstream in memory
    """

    def __init__(self, index: int, filename: str, config: Config, sine_funcs):
        Circuit.__init__(index, filename, config)

        self.__src_sine_funcs = sine_funcs
        self.__simulation_bitstream = [0] * 100
        pass

    def mutate(self):
        """
        Mutate the simulation mode circuit
        """
        for i in range(0, len(self.__simulation_bitstream)):
            if self.__config.get_mutation_probability() >= self.__rand.uniform(0,1):
                # Mutate this bit
                self.__simulation_bitstream[i] = 1 - self.__simulation_bitstream[i]

    def randomize_bitstream(self):
        """
        Fully randomize the simulation mode circuit
        """
        for i in range(0, len(self.__simulation_bitstream)):
            self.__simulation_bitstream[i] = self.__rand.integers(0, 2)

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

    def upload(self):
        # Doesn't need to do anything, runs locally
        pass
