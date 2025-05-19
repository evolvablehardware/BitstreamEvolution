class PlotDataRecorder:
    def __init__(self):
        self.__ovr_best_fit = 0

    def reset(self):
        self.__ovr_best_fit = 0

    def record_waveform(self, waveform: list[int]):
        with open("workspace/waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i += 1
    
    def record_generation(self, fits: list[float], current_epoch: int, diversity: float):
        fits.sort(reverse=True)
        fitness_sum = 0
        for f in fits:
            fitness_sum += f
            if f > self.__ovr_best_fit:
                self.__ovr_best_fit = f
        
        with open("workspace/bestlivedata.log", "a") as liveFile:
            avg = fitness_sum / len(fits)
            # Format: Epoch, Best Fitness, Worst Fitness, Average Fitness, Ovr Best Fitness, Diversity Measure
            liveFile.write("{}, {}, {}, {}, {}, {}\n".format(
                str(current_epoch),
                str(fits[0]),
                str(fits[-1]),
                str(avg),
                str(self.__ovr_best_fit),
                str(diversity)
            ))

        fit_strs = list(map(lambda x: str(x), fits))
        with open("workspace/violinlivedata.log", "a") as live_file:
            live_file.write(("{}:{}\n").format(current_epoch, ",".join(fit_strs)))
