# Genetic Algorithm for Intrinsic Analog Hardware Evolution
# FOR USE WITH LATTICE iCE40 FPGAs ONLY
#
# This code can be used to evolve an analog oscillator
#
# Author: Derek Whitley


from Microcontroller import Microcontroller
from CircuitPopulation import CircuitPopulation
from ConfigBuilder import ConfigBuilder
from Circuit import Circuit
from Config import Config
from Logger import Logger
from subprocess import run
import argparse
import os

#This argument configuration could be moved to a separate module, like config, if desired.

#Program info for --help output
program_name="evolve"
program_description="""This program evolves a population of FPGA layouts (or simulations of them) acording to a predefined fitness function. 
All files will presume the main directory of BitStreamEvolution unless absolute path given."""
program_epilog="""For non-simulations, and Arduino and the Lattice iCE40 FPGA are also needed.
Exit Status:
0 - No issues
1 - Issue while running"""

# Exit codes
# 0 - Default for no issues
# 1 - Default for errors
# 130 - KeyboardInterrupt default (i.e. ctrl+c in therminal)
#Check exit codes by running `echo $?` after running the command.


default_config = "data/config.ini" #Use none if want specified
default_base_config = "data/default_config.ini"
default_output_directory = None #If not changed, information only saved internally.
default_experiment_description = None #If not changed, requires user to enter.

parser = argparse.ArgumentParser(prog=program_name,
                                 description=program_description,
                                 epilog=program_epilog)
parser.add_argument('-c','--config',type=str,default=default_config,
                   help=f"The file this simulation is generated from. Default: {default_config}")
parser.add_argument('-bc','--base-config',typt=str,default=default_base_config,
                    help= f"The config any unspecified values in the main config is pulled from. " +\
                        f"This overpowers the main config specified in the file if provided. Default: {default_base_config}")
parser.add_argument('-o','--output-directory', type=str,default=default_output_directory,
                    help=f"The directory output from the simulation is copied to after a successful simulation. Default: {default_output_directory}")
parser.add_argument('-d','--description', type=str,default=default_experiment_description,
                    help="The description of this simulation. Requires manual entry if not an argument.")
# --help is added by default

args=parser.parse_args()
config = args.config
base_config = args.base_config
output_directory = args.output_directory

## DELETE ME WHEN args are Logged
print(args) # probably should log this instead. not sure if with logger directly or through config.

def validate_arguments():
    if (args.output_directory is not None) and (not os.path.isdir(args.output_directory)):
        raise ValueError(f"Output directory not recognized: {args.output_directory}")

        #alternate solution if wanted to do more with exit statuses for bash scripting
        #parser.exit(status=1, message=f"Output directory not recognized: {args.output_directory}")

#create desired config
config_builder = ConfigBuilder(config,override_base_config=base_config)
final_config_path = "./workspace/builtconfig.ini"
config_builder.build_config(final_config_path)

config = Config(final_config_path)

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

# make sure config file specified above ends up in output.
if output_directory is not None:
    #copy simulation information to this output directory
    logger.save_workspace(output_directory)
elif config.get_backup_workspace():
    logger.save_workspace(config.get_output_directory())