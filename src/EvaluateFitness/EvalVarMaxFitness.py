# For use with EvaluateFitness: 
# eval_var_max = EvalVarMaxFitness()
# EvaluateFitness(eval_var_max.calculate_success, eval_var_max.calculate_err)
from PlotDataRecorder import PlotDataRecorder


class EvalVarMaxFitness:
    def __init__(self, plot_data_recorder: PlotDataRecorder):
        self.__plot_data_recorder = plot_data_recorder
        self.__best_waveform = []
        self.__best_waveform_fit = 0
        self.__epoch = 0

    def start_eval(self):
        self.__best_waveform = []
        self.__best_waveform_fit = 0

    def end_eval(self):
        self.__plot_data_recorder.record_waveform_heatmap(self.__epoch, self.__best_waveform)
        self.__epoch += 1

    def calculate_success(self, data: list[int], index: int, src_pop: str) -> float:
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
        self.__plot_data_recorder.record_all_live_data(index, 0, src_pop)
        return 0
