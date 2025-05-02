from abc import ABC, abstractmethod
from pathlib import Path

from BitstreamEvolutionProtocols import FPGA_Compilation_Data
from Logger import Logger
from result import Result # type: ignore

class Circuit(ABC):
    def __repr__(self):
        """
        Returns the string representation of this Circuit, used in
        functions such as 'print'.

        Returns
        -------
        str
            A string representation of the Circuit. (the file name)
        """
        return self._filename

    def __init__(self, index: int, filename: str, logger: Logger):
        self._filename = filename
        self._index = index
        self._logger = logger

    @abstractmethod
    def compile(self, fpga: FPGA_Compilation_Data, working_dir:Path) -> Result[Path,Exception]:
        """
        Performs the upload function of this Circuit. Prerequisite to collecting data
        """
        pass

    @abstractmethod
    def get_bitstream(self) -> list[bool]:
        """
        Returns the full bitstream of the circuit
        """
        pass

    @abstractmethod
    def set_bitstream(self, bitstream: list[bool]):
        """
        Sets the bitstream of the circuit
        """
        pass
    
    def set_file_attribute(self, attribute, value):
        pass # No default behavior

    def get_file_attribute(self, attribute) -> str | None:
        return '0' # No default behavior

    # @abstractmethod
    # def mutate(self):
    #     """
    #     Mutates the Circuit's bitstream. Mutation is performed on a per-bit basis
    #     """
    #     pass

    # @abstractmethod
    # def randomize_bitstream(self):
    #     """
    #     Randomizes every modifiable bit in this Circuit's bitstream
    #     """
    #     pass

    # @abstractmethod
    # def crossover(self, parent, crossover_point: int):
    #     """
    #     Decide which crossover function to used based on configuration

    #     Parameters
    #     ----------
    #     parent : Circuit
    #         The other circuit the crossover is being performed with
    #     corssover_point : int
    #         The point in the modifiable bitstream to perform the point crossover.
    #     """
    #     pass

    @abstractmethod
    def copy_from(self, other):
        """
        Fully copy the bitstream from the other circuit

        Parameters
        ----------
        other : Circuit
            The other circuit to copy the bitstream from
        """
        pass

    # def _update_all_live_data(self):
    #     '''
    #     Updates this circuit's entry in alllivedata.log (the circuit's fitness and source population)
    #     '''
    #     # Read in the file contents first
    #     lines = []
    #     with open("workspace/alllivedata.log", "r") as allLive:
    #         lines = allLive.readlines()

    #     # Modify the content internally
    #     index = self._index - 1
    #     if len(lines) <= index:
    #         for i in range(index - len(lines) + 1):
    #             lines.append("\n")

    #     # Shows pulse count in this chart if in PULSE_COUNT fitness func, and fitness otherwise
    #     # Value is always an array separated by semicolons. If values in __data, then use those. Otherwise, use scalar pulses or fitness
    #     value = [str(x) for x in self._get_all_live_reported_value()] 
    #     # if len(self._data) > 0:
    #     #     # Flatten data
    #     #     value = [str(item) for sublist in self._data for item in sublist]
    #     # else:
    #     #     if is_pulse_func(self._config):
    #     #         value = [str(self._pulses)]
    #     #     else:
    #     #         value = [str(self._fitness)]

    #     lines[index] = "{},{},{}\n".format(
    #         self._index, 
    #         ';'.join(value),
    #         self.get_file_attribute('src_population')
    #     )

    #     # Write these new lines to the file
    #     with open("workspace/alllivedata.log", "w+") as allLive:
    #         allLive.writelines(lines)

    # @staticmethod
    # def _calculate_variance_fitness(waveform):
    #     """
    #     Measure the fitness of this circuit using the variance-maximization fitness
    #     function
        
    #     Parameters
    #     ----------
    #     waveform : list[int]
    #         Waveform of the run

    #     Returns
    #     -------
    #     float
    #         The fitness. (Variance Maximization Fitness)
    #     """

    #     variance_sum = 0
    #     total_samples = 500
    #     # Reset high/low vals to min/max respectively
    #     # self.__low_val = 1024
    #     # self.__high_val = 0
    #     for i in range(len(waveform)-1):
    #         # NOTE Signal Variance is calculated by summing the absolute difference of
    #         # sequential voltage samples from the microcontroller.
    #         # Capture the next point in the data file to a variable
    #         initial1 = waveform[i]
    #         # Capture the next point + 1 in the data file to a variable
    #         initial2 = waveform[i+1]
    #         # Take the absolute difference of the two points and store to a variable
    #         variance = abs(initial2 - initial1)

    #         # if initial1 < self.__low_val:
    #         #     self.__low_val = initial1
    #         # if initial1 > self.__high_val:
    #             # self.__high_val = initial1

    #         if initial1 != None and initial1 < 1000:
    #             variance_sum += variance

    #     fitness = variance_sum / total_samples
    #     #self.__mean_voltage = sum(waveform) / len(waveform) #used by combined fitness func

    #     return fitness
