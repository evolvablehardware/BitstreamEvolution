from pathlib import Path
from Circuit.FileBasedCircuit import FileBasedCircuit
from Circuit.FitnessFunction import FitnessFunction
from time import sleep
from subprocess import run
import Config
import Microcontroller

RUN_CMD = "iceprog"

class IntrinsicCircuit(FileBasedCircuit):
    """
    No longer an abstract class. Represents circuits that get uploaded to the physical FPGA
    The fitness strategy provided is used to evaluate the circuits
    """
    def __init__(self, index: int, filename: str, config: Config, template: Path, rand,  microcontroller: Microcontroller, fitness_func: FitnessFunction):
        FileBasedCircuit.__init__(index, filename, config, template, rand)
        self._fitness_func = fitness_func
        self._fitness_func.attach(self._data_filepath, microcontroller, self._config)

    def _get_measurement(self):
        return self._fitness_func.get_measurements()

    def calculate_fitness(self) -> float:
        return self._fitness_func.calculate_fitness(self._data)

    def upload(self):
        self.__run()

    def __run(self):
        """
        Compiles this Circuit, uploads it, and runs it on the FPGA
        """
        FileBasedCircuit._compile()
        
        cmd_str = [
            RUN_CMD,
            self._bitstream_filepath,
            "-d",
            self._microcontroller.get_fpga()
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