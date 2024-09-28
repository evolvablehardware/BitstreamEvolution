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

    def mutate(self):
        """
        Mutate the simulation mode circuit
        """
        for i in range(0, len(self.__simulation_bitstream)):
            if self._config.get_mutation_probability() >= self._rand.uniform(0,1):
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

    def upload(self):
        # Doesn't need to do anything, runs locally
        pass

    def _get_measurement(self) -> float:
        """
        Evaluate the simulation bitstream (use sine function combinations, with variance formula)
        """
        
        # Need to sum up the waveforms of every 1 that appears in our bitstream
        sine_funcs = []
        for pos in range(len(self.__simulation_bitstream)):
            if self.__simulation_bitstream[pos] == 1:
                # Need to calculate sine function for this position
                sine_funcs.append(self.__src_sine_funcs[pos])

        # Force them to have at least 10 sine functions turned on
        if len(sine_funcs) <= 10:
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
        
        fitness = Circuit._calculate_variance_fitness(waveform)
        return fitness
    
    def calculate_fitness(self) -> float:
        # Calculate based on stored data
        # For sim mode, just take an average
        return sum(self._data) / len(self._data)
