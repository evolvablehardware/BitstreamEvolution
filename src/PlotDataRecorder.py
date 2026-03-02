"""Records live experiment data to workspace log files for real-time plotting."""


class PlotDataRecorder:
    """Tracks overall best fitness and writes data to log files consumed by PlotEvolutionLive."""
    def __init__(self):
        """Initialize the recorder with zero overall best fitness."""
        self.__ovr_best_fit = 0

    def reset(self):
        """Reset overall best fitness to zero."""
        self.__ovr_best_fit = 0

    def record_waveform(self, waveform: list[int]):
        """Write waveform sample points to the waveform live-data log.

        Parameters
        ----------
        waveform : list[int]
            Sampled waveform data points.
        """
        with open("workspace/waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i += 1
    
    def record_generation(self, fits: list[float], current_epoch: int, diversity: float):
        """Append generation summary (best, worst, avg, diversity) to log files.

        Parameters
        ----------
        fits : list[float]
            Fitness values for the current generation.
        current_epoch : int
            Current generation number.
        diversity : float
            Population diversity measure.
        """
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

    def record_waveform_heatmap(self, current_epoch: int, best_waveform: list[int]):
        """Append the best waveform of this epoch to the heatmap log.

        Parameters
        ----------
        current_epoch : int
            Current generation number.
        best_waveform : list[int]
            Waveform data of the best individual.
        """
        best_waveform_str = list(map(lambda x: str(x), best_waveform))
        with open("workspace/heatmaplivedata.log", "a") as live_file2:
            live_file2.write(("{}:{}\n").format(current_epoch, ",".join(best_waveform_str)))

    def record_all_live_data(self, index: int, reported_value: float, src_population: str):
        """Update a specific line in the all-live-data log with a new value.

        Parameters
        ----------
        index : int
            Line index to update.
        reported_value : float
            Fitness or metric value to record.
        src_population : str
            Name of the source population.
        """
        # Read in the file contents first
        lines = []
        with open("workspace/alllivedata.log", "r") as allLive:
            lines = allLive.readlines()

        # Modify the content internally
        if len(lines) <= index:
            for i in range(index - len(lines) + 1):
                lines.append("\n")

        lines[index] = "{},{},{}\n".format(
            str(index),
            str(reported_value),
            src_population
        )

        # Write these new lines to the file
        with open("workspace/alllivedata.log", "w+") as allLive:
            allLive.writelines(lines)
