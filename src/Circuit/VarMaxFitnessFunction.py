from Circuit.FitnessFunction import FitnessFunction

class VarMaxFitnessFunction(FitnessFunction):
    def __init__(self, total_samples: int):
        FitnessFunction.__init__(self)
        self.__total_samples = total_samples

    def get_measurements(self) -> list[float]:
        self._microcontroller.measure_signal()
        waveform = self.__read_waveform()
        fitness = self.__measure_variance_fitness(waveform)
        return [fitness]

    def calculate_fitness(self, data: list[float]) -> float:
        # Just take an average
        return sum(data) / len(data)

    def __read_waveform(self):
        """
        Reads variance data from the Circuit data file, which contains readings from the Microcontroller

        Returns
        -------
        list[int]
            waveform
        """
        data_file = open(self._data_filepath, "rb")
        data = data_file.readlines()
        waveform = []
        for i in range(self.__total_samples-1):
            try:
                x = int(data[i].strip().split(b": ", 1)[1])
                waveform.append(x)
            except:
                # self.__log_error(1, "FAILED TO READ {} AT LINE {} -> ZEROIZING LINE".format(
                #     self,
                #     i
                # ))
                waveform.append(0)

        # self.__log_event(5, "Waveform: ", waveform) 
        return waveform

    def __measure_variance_fitness(self, waveform):
        """
        Measure the fitness of this circuit using the variance-maximization fitness
        function
        
        Parameters
        ----------
        waveform : list[int]
            Waveform of the run

        Returns
        -------
        float
            The fitness. (Variance Maximization Fitness)
        """

        variance_sum = 0
        variances = []
        # Reset high/low vals to min/max respectively
        low_val = 1024
        high_val = 0
        for i in range(len(waveform)-1):
            # NOTE Signal Variance is calculated by summing the absolute difference of
            # sequential voltage samples from the microcontroller.
            # Capture the next point in the data file to a variable
            initial1 = waveform[i] #int(data[i].strip().split(b": ", 1)[1])
            # Capture the next point + 1 in the data file to a variable
            initial2 = waveform[i+1] #int(data[i + 1].strip().split(b": ", 1)[1])
            # Take the absolute difference of the two points and store to a variable
            variance = abs(initial2 - initial1)
            # Append the variance to the waveform list
            # Removed since we do this already
            #waveform.append(initial1)

            if initial1 < self.__low_val:
                low_val = initial1
            if initial1 > self.__high_val:
                high_val = initial1

            # Stability: if we want stable waves, we should want to differences between points to be
            # similar. i.e. we want to minimize the differences between these differences
            # Can do 1/[(std. deviation)+0.01] to find a fitness value for the stability
            # To do that we'll start by storing the variances to its own collection
            # NOTE: This encourages frequencies that match the sampling rate
            variances.append(variance)

            if initial1 != None and initial1 < 1000:
                variance_sum += variance

        with open("workspace/waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i += 1

        var_max_fitness = variance_sum / len(waveform)
        mean_voltage = sum(waveform) / len(waveform) #used by combined fitness func

        self._extra_data['mean_voltage'] = mean_voltage
        self._extra_data['low_voltage'] = low_val
        self._extra_data['high_voltage'] = high_val

        return var_max_fitness
