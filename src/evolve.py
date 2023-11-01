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
import argparse
import os

#This argument configuration could be moved to a separate module, like config, if desired.

#Program info for --help output
program_name="evolve"
program_description="""This program evolves a population of FPGA layouts (or simulations of them) acording to a predefined fitness function."""
program_epilog="""The Config overrides seemed like they could be useful for specific parts of the config, such as the logging level or the simulation mode, but is unimplemented.
For non-simulations, and Arduino and the Lattice iCE40 FPGA are also needed.
Exit Status:
0 - No issues
1 - Issue while running"""

# Exit codes
# 0 - Default for no issues
# 1 - Default for errors
# 130 - KeyboardInterrupt default (i.e. ctrl+c in therminal)
#Check exit codes by running `echo $?` after running the command.


default_config = "data/config.ini"
default_output_directory = None #If not changed, information only saved internally.
default_experiment_description = None #If not changed, requires user to enter.

parser = argparse.ArgumentParser(prog=program_name,
                                 description=program_description,
                                 epilog=program_epilog)
parser.add_argument('-c','--config',type=str,default=default_config,
                   help=f"The file this simulation is generated from. Default: {default_config}")
parser.add_argument('-o','--output-directory', type=str,default=default_output_directory,
                    help=f"The directory output from the simulation is copied to after a successful simulation. Default: {default_output_directory}")
parser.add_argument('-d','--description', type=str,default=default_experiment_description,
                    help="The description of this simulation. Requires manual entry if not an argument.")
# --help is added by default

#Section of arguments that overwrite what config says for
#config_overrides=parser.add_argument_group("Config Overrides","Arguments that override contents of config file. NOT IMPLEMENTED")
#config_overrides.add_argument('--override-population-size', type=int,default=None)
#config_overrides.add_argument('--override-generation-size', type=int,default=None)
#config_overrides.add_argument('-l','--log-level', type=int,default=None,help="Most intense logging at 4, least intense at 0")
#mayby impliment simulation mode using mutual exclusion group for keywords  https://docs.python.org/3/library/argparse.html#mutual-exclusion

args=parser.parse_args()
print(args) # probably should log this instead. not sure if with logger directly or through config.

def validate_arguments():
    if (args.output_directory is not None) and (not os.path.isdir(args.output_directory)):
        raise ValueError(f"Output directory not recognized: {args.output_directory}")

        #alternate solution if wanted to do more with exit statuses for bash scripting
        #parser.exit(status=1, message=f"Output directory not recognized: {args.output_directory}")

#create desired config
#if we want to override config in args for easier bash scripting, we would want to change config variable
config = Config(args.config)

# get the explaination if not previously given
if args.description is None:
    args.description = input("Explain this experiment: ")

logger = Logger(config, args.description)
logger.log_info(1, args)
config.add_logger(logger)
config.validate_all()
validate_arguments()
mcu = Microcontroller(config, logger)
population = CircuitPopulation(mcu, config, logger)

if config.get_simulation_mode() != "INTRINSIC_SENSITIVITY":
    population.populate()
    population.evolve()
else:
    population.run_fitness_sensitity()


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

if args.output_directory is not None:
    #copy simulation information to this output directory
    logger.save_workspace(args.output_directory)
elif config.get_backup_workspace():
    logger.save_workspace(config.get_output_directory())