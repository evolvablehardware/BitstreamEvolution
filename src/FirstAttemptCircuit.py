from mmap import mmap
from pathlib import Path
from shutil import copyfile
from time import sleep
from BitstreamEvolutionProtocols import Circuit, CircuitFactory, FPGA_Compilation_Data
from result import Result, Ok # type: ignore
import os
from subprocess import run

RUN_CMD = "iceprog"
COMPILE_CMD = "icepack"

class IntrinsicCircuit(Circuit):
    def __init__(self, filename: str, template: Path, asc_dir: Path, bin_dir: Path, data_dir: Path):
        self.__filename = filename

        self.__hardware_filepath = asc_dir.joinpath(filename + ".asc")

        # Create directories if they don't exist
        os.makedirs(asc_dir, exist_ok=True)
        os.makedirs(bin_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # NOTE Using log files instead of a data buffer in the event of premature termination
        self.__data_filepath = data_dir.joinpath(filename + ".log")
        # Create the data file if it doesn't exist
        open(self.__data_filepath, "w+").close()

        if template:
            copyfile(template, self.__hardware_filepath)

        # Since the hardware file is written to and read from a lot, we
        # mmap it to improve preformance.
        hardware_file = open(self.__hardware_filepath, "r+")
        self.__hardware_file = mmap(hardware_file.fileno(), 0)
        hardware_file.close()

    # TODO: I'm not 100% sure why we want the path returned here, but maybe I'm misunderstanding what the path should be for
    # To clarify, we currently have 2 steps we do with circuits: Compiling (into a binary file) and running (uploading to the physical FPGA)
    # The current implementation of this function performs both operations (although we currently have separate terminology, we dont really ever compile
    # a circuit that we aren't going to upload)
    # However, in that case I don't see why any caller would need a filepath to anything this function produces
    # Also, my understanding is that the Hardware implementations will handle recording diff. fitness functions, instead of delegating that logic
    # to the Circuits as we have done in the past
    def compile(self, fpga: FPGA_Compilation_Data, working_dir: Path) -> Result[Path, Exception]:
        # Ensure the file backing the mmap is up to date with the latest
        # changes to the mmap.
        self.__hardware_file.flush()

        bitstream_filepath = working_dir.joinpath(self.__filename + ".bin")
        compile_command = [
            COMPILE_CMD,
            self.__hardware_filepath,
            bitstream_filepath
        ]
        run(compile_command)

        cmd_str = [
            RUN_CMD,
            bitstream_filepath,
            "-d",
            fpga.id
        ]
        print(cmd_str)
        run(cmd_str)
        sleep(1)

        Ok(bitstream_filepath)
