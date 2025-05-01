from abc import ABC, abstractmethod
import Microcontroller
import Config

class FitnessFunction(ABC):
    """
    Represents a method of evaluating fitness intrinsically (strategy pattern)
    For example, we can create pulse count and variance maximization strategies
    For combined fitness, we could create a concrete implementation that 
    combines two fitness strategies together
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_waveform(self) -> list[float]:
        pass

    @abstractmethod
    def get_measurements(self) -> list[float]:
        pass

    @abstractmethod
    def calculate_fitness(self, measurements: list[float]) -> float:
        pass
