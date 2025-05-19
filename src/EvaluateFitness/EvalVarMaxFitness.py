# For use with EvaluateFitness: 
# eval_var_max = EvalVarMaxFitness()
# EvaluateFitness(eval_var_max.calculate_success, eval_var_max.calculate_err)
from PlotDataRecorder import PlotDataRecorder


class EvalVarMaxFitness:
    def __init__(self, plot_data_recorder: PlotDataRecorder):
        self.__plot_data_recorder = plot_data_recorder

    def calculate_success(self, data: list[int], index: int, src_pop: str) -> float:
        waveform = data
        variance_sum = 0
        total_samples = 500
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

        self.__plot_data_recorder.record_waveform(waveform)
        self.__plot_data_recorder.record_all_live_data(index, fitness, src_pop)

        return fitness
    
    def calculate_err(self, err: Exception, index: int, src_pop: str) -> float:
        self.__plot_data_recorder.record_all_live_data(index, 0, src_pop)
        return 0
