# Genetic Algorithm for Intrinsic Analog Hardware Evolution
# FOR USE WITH LATTICE iCE40 FPGAs ONLY
#
# This code can be used to evolve an analog oscillator
#
# Author: Derek Whitley


from Microcontroller import Microcontroller
from CircuitPopulation import CircuitPopulation
from Circuit import Circuit
from Config import Config
from Logger import Logger
from subprocess import run

config = Config("data/config.ini")

explanation = input("Explain this experiment: ")

logger = Logger(config, explanation)
config.add_logger(logger)
config.validate_all()
mcu = Microcontroller(config, logger)
population = CircuitPopulation(mcu, config, logger)

population.populate()
population.evolve()

logger.log_event(0, "Evolution has completed successfully")

# SECTION Clean up resources


if config.get_simulation_mode() == "FULLY_INTRINSIC":
    # Upload a sample bitstream to the FPGA.
    run([
        "iceprog",
        "-d",
        "i:0x0403:0x6010:0",
        "data/hardware_blink.bin"
    ])

