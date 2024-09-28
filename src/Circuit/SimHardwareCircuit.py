from Circuit import FileBasedCircuit
import Config

class SimHardwareCircuit(FileBasedCircuit):
    """
    A concrete class, the simulated circuit that bases its fitness off of the hardware file
    """

    def __init__(self, index: int, filename: str, config: Config, sine_funcs):
        FileBasedCircuit.__init__(index, filename, config)

    def upload(self):
        # Need to compile, but not actually upload to the FPGA
        FileBasedCircuit._compile(self)

    def _get_measurement(self) -> float:
        """
        Sum up all the bytes in the compiled binary file

        Returns
        -------
        float
            The fitness of the sim hardware. (sum of all bytes in compiled binary file)
        """
        fitness = 0
        with open(self._bitstream_filepath, "rb") as f:
            byte = f.read(1)
            while byte != b"":
                fitness = fitness + int.from_bytes(byte, "big")
                byte = f.read(1)
        
        # self.__log_event(3, "Fitness: ", fitness)

        # self.__update_all_live_data()

        return fitness
    
    def calculate_fitness(self) -> float:
        # Calculate based on stored data
        # For sim mode, just take an average
        return sum(self._data) / len(self._data)
