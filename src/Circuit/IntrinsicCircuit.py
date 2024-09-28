from pathlib import Path
from Circuit import FileBasedCircuit
from time import sleep
from subprocess import run

import Config

RUN_CMD = "iceprog"

class IntrinsicCircuit(FileBasedCircuit):
    """
    Still an abstract class. Represents circuits that get uploaded to the physical FPGA
    """
    def __init__(self, index: int, filename: str, config: Config, template: Path):
        FileBasedCircuit.__init__(index, filename, config, template)

    def upload(self):
        FileBasedCircuit.__compile()
        self.__run()

    def __run(self):
        """
        Compiles this Circuit, uploads it, and runs it on the FPGA
        """
        self.__compile()
        
        cmd_str = [
            RUN_CMD,
            self.__bitstream_filepath,
            "-d",
            self.__microcontroller.get_fpga()
        ]
        print(cmd_str)
        run(cmd_str)
        sleep(1)

        # if switching fpgas every sample, need to upload to the second fpga also
        if self.__config.get_transfer_sample():
            cmd_str = [
                RUN_CMD,
                self.__bitstream_filepath,
                "-d",
                self.__config.get_fpga2()
            ]
            print(cmd_str)
            run(cmd_str)
            sleep(1)