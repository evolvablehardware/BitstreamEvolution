from abc import ABC, abstractmethod
import Config

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

    def __init__(self, index: int, filename: str, config: Config):
        self._filename = filename
        self._config = config
        self._index = index
        self._fitness = 0
        
        self._data = []

    @abstractmethod
    def upload(self):
        """
        Performs the upload function of this Circuit. Prerequisite to collecting data
        """
        pass

    @abstractmethod
    def get_bitstream(self) -> list[int]:
        """
        Returns the full bitstream of the circuit
        """
        pass

    def collect_data_once(self):
        """
        Collects one round of measurement data. Can be performed multiple times before each calculate_fitness call
        """
        self._data.extend(self._get_measurement())

    @abstractmethod
    def _get_measurement(self) -> list[float]:
        """
        This is for child classes to override
        Collects and returns the value of one round of data
        """
        pass

    def calculate_fitness(self) -> float:
        """
        Calculates and returns the fitness indicated by the Circuit's currently-collected data
        """
        self._fitness = self._calculate_fitness()
        return self._fitness

    @abstractmethod
    def _calculate_fitness(self) -> float:
        pass

    def clear_data(self):
        """
        Clears the stored measurement data
        """
        self._data.clear()

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

    def get_fitness(self):
        return self._fitness

    @staticmethod
    def _calculate_variance_fitness(waveform):
        """
        Measure the fitness of this circuit using the variance-maximization fitness
        function
        
        Parameters
        ----------
        waveform : list[int]
            Waveform of the run

        Returns
        -------
        float
            The fitness. (Variance Maximization Fitness)
        """

        variance_sum = 0
        total_samples = 500
        # Reset high/low vals to min/max respectively
        # self.__low_val = 1024
        # self.__high_val = 0
        for i in range(len(waveform)-1):
            # NOTE Signal Variance is calculated by summing the absolute difference of
            # sequential voltage samples from the microcontroller.
            # Capture the next point in the data file to a variable
            initial1 = waveform[i] #int(data[i].strip().split(b": ", 1)[1])
            # Capture the next point + 1 in the data file to a variable
            initial2 = waveform[i+1] #int(data[i + 1].strip().split(b": ", 1)[1])
            # Take the absolute difference of the two points and store to a variable
            variance = abs(initial2 - initial1)
            # Append the variance to the waveform list
            # Removed since we do this already
            #waveform.append(initial1)

            # if initial1 < self.__low_val:
            #     self.__low_val = initial1
            # if initial1 > self.__high_val:
                # self.__high_val = initial1

            if initial1 != None and initial1 < 1000:
                variance_sum += variance

        # with open("workspace/waveformlivedata.log", "w+") as waveLive:
        #     i = 1
        #     for points in waveform:
        #         waveLive.write(str(i) + ", " + str(points) + "\n")
        #         i += 1

        fitness = variance_sum / total_samples
        #self.__mean_voltage = sum(waveform) / len(waveform) #used by combined fitness func

        return fitness
