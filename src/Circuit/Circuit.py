from abc import ABC, abstractmethod
import Config

'''
TODO: Remove this comment; this is just used as a scratchpad

What is the core API we want from the Circuit?
* Upload to FPGA
* Perform one run of collecting data
* Calculate fitness based on the already-collected data
* Clearing the collected data
* Mutating itself
* Crossover
'''

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
        return self.__filename

    def __init__(self, index: int, filename: str, config: Config):
        self.__filename = filename
        self.__config = config
        self.__index = index
        
        self.__data = []

    @abstractmethod
    def upload(self):
        """
        Performs the upload function of this Circuit. Prerequisite to collecting data
        """
        pass

    @abstractmethod
    def collect_data_once(self):
        """
        Collects one round of measurement data. Can be performed multiple times before each calculate_fitness call
        """
        self.__data.append(self.__get_measurement())

    @abstractmethod
    def __get_measurement(self) -> float:
        """
        This is for child classes to override
        Collects and returns the value of one round of data
        """
        pass

    @abstractmethod
    def calculate_fitness(self) -> float:
        """
        Calculates and returns the fitness indicated by the Circuit's currently-collected data
        """
        pass

    def clear_data(self):
        """
        Clears the stored measurement data
        """
        self.__data.clear()

    @abstractmethod
    def mutate(self):
        """
        Mutates the Circuit's bitstream. Mutation is performed on a per-bit basis
        """
        pass

    @abstractmethod
    def randomize_bitstream(self):
        """
        Randomizes every modifiable bit in this Circuit's bitstream
        """
        pass

    @abstractmethod
    def crossover(self, parent, crossover_point: int):
        """
        Decide which crossover function to used based on configuration

        Parameters
        ----------
        parent : Circuit
            The other circuit the crossover is being performed with
        corssover_point : int
            The point in the modifiable bitstream to perform the point crossover.
        """
        pass
