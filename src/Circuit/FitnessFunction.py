from abc import ABC, abstractmethod
import Microcontroller

class FitnessFunction(ABC):
    """
    Represents a method of evaluating fitness intrinsically (strategy pattern)
    For example, we can create pulse count and variance maximization strategies
    For combined fitness, we could create a concrete implementation that 
    combines two fitness strategies together
    """

    def __init__(self):
        pass

    def attach(self, data_filepath, microcontroller: Microcontroller):
        self._data_filepath = data_filepath
        self._microcontroller = microcontroller

    @abstractmethod
    def measure_fitness(self) -> float:
        pass
