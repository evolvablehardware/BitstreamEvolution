"""Oscillation pulse-count fitness evaluator.

Fitness is computed as the inverse distance from a target pulse count.
Used with :class:`~EvaluateFitness.EvaluateFitness.EvaluateFitness` via
the :class:`~EvaluateFitness.EvaluateFitness.FitnessEvaluator` protocol::

    evaluator = EvalPulseCountFitness(target=1000, plot_data_recorder=recorder)
    EvaluateFitness(evaluator)
"""

from PlotDataRecorder import PlotDataRecorder


class EvalPulseCountFitness:
    """Evaluate fitness based on how close measured pulse counts are to a target.

    For each individual the minimum fitness across all samples is used,
    where fitness = 1 when pulses == target, 0 when pulses == 0, and
    ``1 / abs(target - pulses)`` otherwise.
    """
    def __init__(self, target: int, plot_data_recorder: PlotDataRecorder):
        """Create an evaluator targeting *target* pulses."""
        self.__target = target
        self.__plot_data_recorder = plot_data_recorder

    def start_eval(self):
        """Called before evaluating a generation (no-op for pulse count)."""
        pass

    def end_eval(self):
        """Called after evaluating a generation (no-op for pulse count)."""
        pass

    def calculate_success(self, data: list[int], index: int, src_pop: str) -> float:
        """Return the minimum fitness across all pulse-count samples in *data*."""
        acc: list[float] = []
        for p in data:
            acc.append(self.__calculate_individual(p))
        fit = min(acc)

        min_idx = acc.index(fit)
        pulses_at_min = data[min_idx]

        self.__plot_data_recorder.record_all_live_data(index, pulses_at_min, src_pop)

        return fit
    
    def calculate_error(self, err: Exception, index: int, src_pop: str) -> float:
        """Return zero fitness when measurement fails."""
        self.__plot_data_recorder.record_all_live_data(index, -1, src_pop)
        return 0
    
    def __calculate_individual(self, pulses: int) -> float:
        if pulses == self.__target:
            return 1
        elif pulses == 0:
            return 0
        else:
            return 1.0 / abs(self.__target - pulses)
