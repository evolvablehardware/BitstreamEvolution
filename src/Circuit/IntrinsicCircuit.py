from pathlib import Path
from Circuit.FileBasedCircuit import FileBasedCircuit
from Circuit.FitnessFunction import FitnessFunction
from time import sleep
from subprocess import run
import Config
import Microcontroller
import Logger

RUN_CMD = "iceprog"
COMPILE_CMD = "icepack"

class IntrinsicCircuit(FileBasedCircuit):
    """
    No longer an abstract class. Represents circuits that get uploaded to the physical FPGA
    The fitness strategy provided is used to evaluate the circuits
    """
    def __init__(self, index: int, filename: str, config: Config, template: Path, rand, logger: Logger, microcontroller: Microcontroller, fitness_func: FitnessFunction):
        FileBasedCircuit.__init__(self, index, filename, config, template, rand, logger)
        self._fitness_func = fitness_func
        self._extra_data = dict()
        self._fitness_func.attach(self._data_filepath, microcontroller, self._config, self._extra_data)

    def evaluate_once(self):
        self.clear_data()
        self.collect_data_once()
        self.calculate_fitness()

    def _get_measurement(self):
        return self._fitness_func.get_measurements()

    def _calculate_fitness(self) -> float:
        fitness_sum = 0
        for data in self._fpga_datas:
            fitness_sum = fitness_sum + self._fitness_func.calculate_fitness(data)
        mean = fitness_sum / len(self._fpga_datas)
        return mean

    def upload(self):
        self.__run()

    def get_waveform(self):
        return self._fitness_func.get_waveform()

    def get_extra_data(self, key):
        return self._extra_data[key]

    def __run(self):
        """
        Compiles and uploads the compiled circuit and runs it on the FPGA
        """
        self._compile()
        
        cmd_str = [
            RUN_CMD,
            self._bitstream_filepath,
            "-d",
            self._config.get_fpgas()[self._fpga_index]
        ]
        print(cmd_str)
        run(cmd_str)
        sleep(1)

        # if switching fpgas every sample, need to upload to the second fpga also
        if self._config.get_transfer_sample():
            cmd_str = [
                RUN_CMD,
                self._bitstream_filepath,
                "-d",
                self._config.get_fpga2()
            ]
            print(cmd_str)
            run(cmd_str)
            sleep(1)
