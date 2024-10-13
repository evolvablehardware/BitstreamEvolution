from pathlib import Path
from Circuit.FileBasedCircuit import FileBasedCircuit
import Config

class SimHardwareCircuit(FileBasedCircuit):
    """
    A concrete class, the simulated circuit that bases its fitness off of the hardware file
    """

    def __init__(self, index: int, filename: str, config: Config, template: Path, rand):
        FileBasedCircuit.__init__(self, index, filename, config, template, rand)

    def upload(self):
        # Need to compile, but not actually upload to the FPGA
        FileBasedCircuit._compile(self)

    def _get_measurement(self) -> list[float]:
        """
        Sum up all the bits in the compiled binary file
        Note: default configuration has 1728 modifiable bits

        Returns
        -------
        float
            The fitness of the sim hardware. (sum of all bytes in compiled binary file)
        """
        fitness = 0
        def evaluate_bit(bit, *rest):
            nonlocal fitness
            fitness = fitness + (bit - 48)

        self._run_at_each_modifiable(evaluate_bit)
        
        # self.__log_event(3, "Fitness: ", fitness)

        # self.__update_all_live_data()

        return [fitness]
    
    def calculate_fitness(self) -> float:
        # Calculate based on stored data
        # For sim mode, just take an average
        return sum(self._data) / len(self._data)
