from typing import Any, Protocol
from BitstreamEvolutionProtocols import Fitness, Measurement, Population
from result import is_ok # type: ignore

class CalculateSingleFitness(Protocol):
    def __call__(self, data: Any) -> Fitness: ...

class CalculateErrorFitness(Protocol):
    def __call__(self, err: Exception) -> Fitness: ...

class EvaluateFitness:
    '''
    A generic evaluate fitness class that has protocols for defining behavior more simply
    '''
    def __init__(self, calc: CalculateSingleFitness, calc_err: CalculateErrorFitness):
        self.__calc = calc
        self.__calc_err = calc_err

    def evaluate(self, population: Population, measurements: list[Measurement]) -> None:
        for i in range(len(measurements)):
            m = measurements[i]
            if is_ok(m.result):
                data = m.ok_value # type: ignore
                fit = self.__calc(data)
                population.set_fitness_by_index(i, fit)
            else:
                err = m.err_value # type: ignore
                fit = self.__calc_err(err)
                population.set_fitness_by_index(i, fit)
