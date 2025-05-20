from abc import ABC
from typing import Any, Protocol
from BitstreamEvolutionProtocols import Fitness, Measurement, Population
from result import is_ok # type: ignore

class FitnessEvaluator(Protocol):
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
            if is_ok(m.result):
                data = m.result.ok_value # type: ignore
                fit = self.__evaluator.calculate_success(data, i, '')
                population.set_fitness_by_index(i, fit)
            else:
                err = m.result.err_value # type: ignore
                fit = self.__evaluator.calculate_error(err, i, '')
                population.set_fitness_by_index(i, fit)
        self.__evaluator.end_eval()
