from Circuit.FitnessFunction import FitnessFunction
import math

class ToneDiscriminatorFitnessFunction(FitnessFunction):
    def __init__(self):
        FitnessFunction.__init__(self)

    def get_measurements(self) -> list[float]:
        self._microcontroller.measure_signal_td(self._data_filepath)
        (waveform, state) = self.__read_variance_data_td()
        fitness = self.__measure_tonedisc_fitness(waveform, state)
        return fitness

    def calculate_fitness(self, measurements: list[float]) -> float:
        # Just take an average
        return sum(data) / len(data)

    def __read_variance_data_td(self):
        """
        Reads tone discriminator data from the Circuit data file, 
        which contains readings from the Microcontroller. Data includes waveform (ADC) AND 
        state (input frequency) information.

        .. todo::
            Check the condition of the for loop. Why the -1? 

        Returns
        -------
        (list[int], list[int])
            waveform
            state
        """
        data_file = open(self._data_filepath, "rb")
        data = data_file.readlines()

        # We take 1000 samples during each circuit's evaluation period
        total_samples = 1000

        # Create 2 empty arrays which will contain the waveform and state information.
        waveform = []
        state = []

        # Append each data point to the appropriate array
        for i in range(total_samples-1):
            try:
                # If the reading of the data suceeds, split into the waveform and state readings
                dataPoint = data[i].decode("utf-8")
                
                x = int(re.split(" ", dataPoint)[1])
                y = int(re.split(" ", dataPoint)[2])

                # Add readings to arrays
                waveform.append(x)
                state.append(y)
            except:
                # If the reading of the data fails, just record the data as 0s
                # self.__log_error(1, "TONE_DISC FAILED TO READ {} AT LINE {} -> ZEROIZING LINE".format(
                #     self,
                #     i
                # ))
                waveform.append(0)
                state.append(0)

        # self.__log_event(5, "Waveform: ", waveform)
        # self.__log_event(5, "State: ", state) 

        # Return the populated arrays
        return (waveform, state)

    def get_waveform(self):
        wf = []
        # Since __read_variance_data_td() returns 2 arrays (waveform & state), we want the first array (waveform)
        for pt in self.__read_variance_data_td()[0]:
            wf.append(str(pt))
        return wf

    def __measure_tonedisc_fitness(self, waveform, state):
        """
        Measure the fitness of this circuit using the tone discriminator fitness
        function. 
        
        Parameters
        ----------
        waveform : list[int]
            Waveform of the run
        state : list[int]
            State of the run

        Returns
        -------
        float
            The fitness. (Tone Discriminator Fitness)
        """

        # Note: operating voltage of the Arduino Nano is 5 V, while that of the FPGA is 3.3 V
        # According to the ice40 datasheet, 3.6 V is the absolute maximum output voltage of FPGA
        # Thus, each ADC reading can range from 0 (0 V) to 737 (3.6 V = 5 V * (737 / 1024))
        
        # There are 2 acceptable cases to produce a perfect fitness of 1:
            # (1): The circuit outputs 0 V for low frequencies (State = 0) and 3.6 V for high frequencies (State = 1)
            # (2): The circuit outputs 0 V for high frequencies (State = 1) and 3.6 V for low frequencies (State = 0)

        # waveform_diffs holds two values that correspond to the 2 cases outlined above
            # (1): The first value holds the sum of absolute differences between the FPGA's waveform samples and an ideal, fitness = 1 waveform satisfying (1) above
            # (2): The second value holds the sum of absolute differences between the FPGA's waveform samples and an ideal, fitness = 1 waveform satisfying (2) above
        # waveform_diffs is ONLY used to check if the circuit is a perfect one, so this function can be rewritten to exclude it

        # waveform_sums holds two values that correspond to:
            # (1): The sum of the ADC waveform readings for when State = 0
            # (2): The sum of the ADC waveform readings for when State = 1
        # These sums are crucial to compute the fitness
        # The sums are used to compute the AVERAGE FPGA voltage for when State = 0 and the AVERAGE FPGA voltage for when State = 1
        # The higher the absolute difference between these averages, the better the circuit has done to "discriminate" the frequencies

        waveform_diffs = [0, 0]
        waveform_sums = [0, 0]

        # 1000 samples are taken per circuit
        total_samples = 1000

        # Counter variables track how many samples were captured when State = 0 and State = 1
        # Ideally, these should be 500 and 500, but the Nano is not perfect.
        # They should always add up to 1000 and should be very close to 500.
        stateZeroCount = 0
        stateOneCount = 0

        # Reset high/low vals to min/max respectively
        low_val = 1024
        high_val = 0
        for i in range(len(waveform)):
            waveformPoint = waveform[i]

            # Perform bounds checking for valid ADC readings
            if waveformPoint < low_val:
                low_val = waveformPoint
            if waveformPoint > high_val:
                high_val = waveformPoint

            # If we have a valid reading, check if the State was 0 (low frequency) or 1 (high frequency)
            if waveformPoint != None and waveformPoint < 1000:
                # Update the correct arrays based on the state
                if state[i] == 0:
                    stateZeroCount += 1
                    waveform_diffs[0] += waveformPoint
                    waveform_diffs[1] += (737 - waveformPoint)
                    waveform_sums[0] += waveformPoint
                else:
                    stateOneCount += 1
                    waveform_diffs[0] += (737 - waveformPoint)
                    waveform_diffs[1] += waveformPoint
                    waveform_sums[1] += waveformPoint
        
        # Write waveform data to file
        with open("workspace/waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i += 1

        # Write state data to file
        with open("workspace/statelivedata.log", "w+") as stateLive:
            i = 1
            for points in state:
                stateLive.write(str(i) + ", " + str(points) + "\n")
                i += 1

        # Edge case checks for fitness
        if sum(waveform) == 0:
            fitness = 0
        elif waveform_diffs[0] == 0 or waveform_diffs[1] == 0:
            fitness = 1

        # Most common case below: fitness is proportional to the absolute different in mean voltage between States 0 and 1
        # A perfect fitness of 1 means the difference was a perfect 3.6 V, meaning perfect discrimination.
        else:
            stateZeroAve = (waveform_sums[0] / stateZeroCount)
            stateOneAve = (waveform_sums[1] / stateOneCount)
            fitness = (abs(stateZeroAve - stateOneAve) / 737.0)
            # self.__log_event(1,
            # "State 0 Average = ",
            # stateZeroAve, " --- State 0 Count = ", stateZeroCount,
            #   " ----- State 1 Average = ", stateOneAve,
            #   " State 1 Count = ", stateOneCount)
        
        # Compute mean voltage
        mean_voltage = sum(waveform) / len(waveform) #used by combined fitness func

        return fitness
