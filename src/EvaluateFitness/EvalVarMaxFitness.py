"""Variance-based (signal activity) fitness evaluator.

Fitness equals the mean absolute difference between consecutive waveform
samples, rewarding circuits that produce high-activity signals. Used with
:class:`~EvaluateFitness.EvaluateFitness.EvaluateFitness` via the
:class:`~EvaluateFitness.EvaluateFitness.FitnessEvaluator` protocol::

    evaluator = EvalVarMaxFitness(plot_data_recorder=recorder)
    EvaluateFitness(evaluator)
"""

from PlotDataRecorder import PlotDataRecorder


class EvalVarMaxFitness:
    """Evaluate fitness by measuring sequential voltage variance in a waveform.

    Tracks the best waveform per generation for heatmap recording.
    """

    def __init__(self, plot_data_recorder: PlotDataRecorder):
        """Create an evaluator that records live data to *plot_data_recorder*."""
        self.__plot_data_recorder = plot_data_recorder
        self.__best_waveform = []
        self.__best_waveform_fit = 0
        self.__epoch = 0

    def start_eval(self):
        """Reset per-generation best waveform tracking."""
        self.__best_waveform = []
        self.__best_waveform_fit = 0

    def end_eval(self):
        """Record the best waveform of this generation and advance the epoch counter."""
        self.__plot_data_recorder.record_waveform_heatmap(self.__epoch, self.__best_waveform)
        self.__epoch += 1

    def calculate_success(self, data: list[int], index: int, src_pop: str) -> float:
        """Compute variance-based fitness from a waveform in *data*."""
        waveform = data
        variance_sum = 0
        total_samples = len(waveform)
        for i in range(len(waveform)-1):
            # NOTE Signal Variance is calculated by summing the absolute difference of
            # sequential voltage samples from the microcontroller.
            # Capture the next point in the data file to a variable
            initial1 = waveform[i]
            # Capture the next point + 1 in the data file to a variable
            initial2 = waveform[i+1]
            # Take the absolute difference of the two points and store to a variable
            variance = abs(initial2 - initial1)

            if initial1 != None and initial1 < 1000:
                variance_sum += variance

        fitness = variance_sum / total_samples

        if fitness > self.__best_waveform_fit:
            self.__best_waveform_fit = fitness
            self.__best_waveform = waveform

        self.__plot_data_recorder.record_waveform(waveform)
        self.__plot_data_recorder.record_all_live_data(index, fitness, src_pop)

        return fitness

    def calculate_error(self, err: Exception, index: int, src_pop: str) -> float:
        """Return zero fitness when measurement fails."""
        self.__plot_data_recorder.record_all_live_data(index, 0, src_pop)
        return 0
