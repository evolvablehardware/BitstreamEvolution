# For use with EvaluateFitness: 
# eval_oscillator = EvalPulseCountFitness()
# EvaluateFitness(eval_oscillator.calculate_success, eval_oscillator.calculate_err)
class EvalPulseCountFitness:
    def __init__(self, target: int):
        self.__target = target

    def calculate_success(self, data: list[int]) -> float:
        # List is of pulse count measurements
        # Currently, return the average fitness
        acc = 0
        for p in data:
            acc += self.__calculate_individual(p)
        fit = acc / len(data)
        return fit
    
    def calculate_err(self, err: Exception) -> float:
        return 0
    
    def __calculate_individual(self, pulses: int) -> float:
        if pulses == self.__target:
            return 1
        elif pulses == 0:
            return 0
        else:
            return 1.0 - abs(self.__target - pulses)
