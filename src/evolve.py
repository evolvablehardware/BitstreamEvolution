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
from configparser import ConfigParser
from subprocess import run

config_parser = ConfigParser()
config_parser.read("data/config.ini")
config = Config(config_parser)

explanation = input("Explain this experiment: ")

logger = Logger(config, explanation)
mcu = Microcontroller(config, logger)
population = CircuitPopulation(mcu, config, logger)


population.populate()
population.evolve()

# SECTION Clean up resources


if config.get_simulation_mode() == "FULLY_INTRINSIC":
    # Upload a sample bitstream to the FPGA.
    run([
        "iceprog",
        "-d",
        "i:0x0403:0x6010:0",
        "data/hardware_blink.bin"
    ])

