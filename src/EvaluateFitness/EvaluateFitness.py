"""Generic fitness evaluation wrapper.

Delegates to a :class:`FitnessEvaluator` strategy for computing fitness
from measurement results. Connects the measurement pipeline to the
population's fitness slots.
"""

from abc import ABC
from typing import Any, Protocol
from BitstreamEvolutionProtocols import Fitness, Measurement, Population
from returns.result import Success # type: ignore

class FitnessEvaluator(Protocol):
    """Strategy protocol for computing fitness from measurement data."""
    def start_eval(self) -> None: ...

    def end_eval(self) -> None: ...

    def calculate_success(self, data: Any, index: int, src_pop: str) -> Fitness: ...

    def calculate_error(self, err: Exception, index: int, src_pop: str) -> Fitness: ...

class EvaluateFitness:
    '''
    A generic evaluate fitness class that has protocols for defining behavior more simply
    '''
    def __init__(self, evaluator: FitnessEvaluator):
        self.__evaluator = evaluator

    def evaluate(self, population: Population, measurements: list[Measurement]) -> None:
        self.__evaluator.start_eval()
        for i in range(len(measurements)):
            m = measurements[i]
            if isinstance(m.result, Success):
                data = m.result.unwrap()
                fit = self.__evaluator.calculate_success(data, i, '')
                population.set_fitness_by_index(i, fit)
            else:
                err = m.result.failure()
                fit = self.__evaluator.calculate_error(err, i, '')
                population.set_fitness_by_index(i, fit)
        self.__evaluator.end_eval()
