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

## Command Line Argument And Help information for this file.

#Program info for --help output
program_name="evolve"
program_description="""This program evolves a population of FPGA layouts (or simulations of them) acording to a predefined fitness function. 
All files will presume the main directory of BitStreamEvolution unless absolute path given."""
program_epilog="""For non-simulations, and Arduino and the Lattice iCE40 FPGA are also needed.
Exit Status:
0 - No issues
1 - Issue while running
130 - KeyboardInterrupt (ctrl+c)"""
#Check exit codes by running `echo $?` after running the command.

## Setting Default Values for Function Call
default_config = "data/config.ini" #Use none if want specified
default_base_config = "data/default_config.ini"
default_output_directory = None #If not changed, information only saved internally.
default_experiment_description = None #If not changed, requires user to enter.

## Global Variables Used in this Function (not changed by user input)
compiled_config_path = "./workspace/builtconfig.ini" # This is where the completed config from Config Builder is stored while evolution is active for easy access.



## Creating an Argument Parser to Parse Arguments
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

## Don't know if this is needed, but it might be useful to validate all inputs especially if this is going to take a while to run.
## It would also be nice if we could have script that could look over a bunch of configs
def validate_arguments():
    if (args.output_directory is not None) and (not os.path.isdir(args.output_directory)):
        raise ValueError(f"Output directory not recognized: {args.output_directory}")

        #alternate solution if wanted to do more with exit statuses for bash scripting
        #parser.exit(status=1, message=f"Output directory not recognized: {args.output_directory}")

## This function performs evolution.
def evolve(primary_config_path:str=default_config,
           output_directory:str=default_output_directory,/,
           experiment_description:str=default_experiment_description,
           base_config_path:str=default_base_config)-> None:

    ## Creating the config that will be used.
    config_builder = ConfigBuilder(primary_config_path, override_base_config=base_config_path)
    config_builder.build_config(compiled_config_path)

    ## Use config generated to run experiment
    config = Config(compiled_config_path)

    ## get the explaination if not previously given
    if experiment_description is None:
        experiment_description = input("Explain this experiment: ")

    ## Run the Simulation
    logger = Logger(config, experiment_description)
    # logger.log_info(1, args) - Not sure how to log arguments. This was my attempt to do so.
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

    # TODO: make sure config file specified above ends up in output.
    if output_directory is not None:
        #copy simulation information to this output directory
        logger.save_workspace(output_directory)
    elif config.get_backup_workspace():
        logger.save_workspace(config.get_output_directory())

## If called directly, use argparse to run, otherwise, just wait for function call to occour with needed information.
if (__name__ == "__main__"):

    ## Parsing Args and configuring Variables
    args=parser.parse_args()

    ## DELETE ME WHEN args are Logged
    print(args) # probably should log this instead. not sure if with logger directly or through config.

    ## Perform Evolution
    evolve(
        primary_config_path =       args.config,
        base_config_path =          args.base_config,
        output_directory =          args.output_directory,
        experiment_description =    args.description
    )

