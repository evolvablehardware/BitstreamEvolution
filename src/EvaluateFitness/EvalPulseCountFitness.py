# For use with EvaluateFitness: 
# eval_oscillator = EvalPulseCountFitness()
# EvaluateFitness(eval_oscillator.calculate_success, eval_oscillator.calculate_err)
from PlotDataRecorder import PlotDataRecorder


class EvalPulseCountFitness:
    def __init__(self, target: int, plot_data_recorder: PlotDataRecorder):
        self.__target = target
        self.__plot_data_recorder = plot_data_recorder

    def start_eval(self):
        pass

    def end_eval(self):
        pass

    def calculate_success(self, data: list[int], index: int, src_pop: str) -> float:
        # List is of pulse count measurements
        # Currently, return the min fitness
        acc: list[float] = []
        for p in data:
            acc.append(self.__calculate_individual(p))
        fit = min(acc)

        min_idx = acc.index(fit)
        pulses_at_min = data[min_idx]

        self.__plot_data_recorder.record_all_live_data(index, pulses_at_min, src_pop)

        return fit
    
    def calculate_error(self, err: Exception, index: int, src_pop: str) -> float:
        self.__plot_data_recorder.record_all_live_data(index, -1, src_pop)
        return 0
    
    def __calculate_individual(self, pulses: int) -> float:
        if pulses == self.__target:
            return 1
        elif pulses == 0:
            return 0
        else:
            return 1.0 / abs(self.__target - pulses)
