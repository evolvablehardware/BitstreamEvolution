#! /bin/python3
#Genetic Algorithm for Intrinsic Analog Hardware Evolution
# FOR USE WITH LATTICE iCE40 FPGAs ONLY
#
# This code can be used to evolve an analog oscillator
#
# Author: Derek Whitley

from Evolution import Evolution
from arg_parse_utils import add_bool_argument
from dataclasses import dataclass
import argparse
from shlex import split as terminal_input_split


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
# By default, we don't want to use a base config.
# We also don't want to override by default, as that would defeat the purpose of the parameter
# in config files to specify the base config to use
# 'default_config' is provided as a sample file, not totally meant to be used - but, might need a rename
default_base_config = None #"data/default_config.ini"
default_output_directory = None #If not changed, information only saved internally.
default_experiment_description = None #If not changed, requires user to enter.

# This is where the completed config from Config Builder is stored while evolution is active for easy access.
BUILT_CONFIG_PATH = "./workspace/builtconfig.ini"

## Creating an Argument Parser to Parse Arguments
parser = argparse.ArgumentParser(prog=program_name,
                                 description=program_description,
                                 epilog=program_epilog)
parser.add_argument('-c','--config',type=str,default=default_config,
                   help=f"The file this simulation is generated from. Default: {default_config}")
parser.add_argument('-bc','--base-config',type=str,default=default_base_config,
                    help= f"The config any unspecified values in the main config is pulled from. " +\
                        f"This overpowers the main config specified in the file if provided. Default: {default_base_config}")
parser.add_argument('-o','--output-directory', type=str,default=default_output_directory,
                    help=f"The directory output from the simulation is copied to after a successful simulation. Default: {default_output_directory}")
parser.add_argument('-d','--description', type=str,default=default_experiment_description,
                    help="The description of this simulation. Requires manual entry if not an argument.")
print_flags = {'enable':['-p','--print-only','--test','--no-action'],
            'disable':['-np', '--no-print-only','--normal','--act']}
add_bool_argument(parser,"print_only",flag_names=print_flags,default=False)
# --help is added by default

@dataclass
class EvolveArgs():
    "These are the arguments used to perform evolutions and generally compiled from arguments passed in."
    config: str
    base_config: str
    output_directory: str
    description: str 
    built_config_path: str
    print_only: bool

    def __init__(self,argument_string:str=None):
        "This function initializes EvolveArgs by parsing from terminal arguments, if argument_string passed, it parses arguments using that"
        if argument_string is None:
            __args=parser.parse_args()
        else:
            __args = parser.parse_args(args=terminal_input_split(argument_string,posix=False))

        self.config = __args.config
        self.base_config = __args.base_config
        self.output_directory = __args.output_directory
        self.description = __args.description
        self.built_config_path = BUILT_CONFIG_PATH
        self.print_only = __args.print_only
        

def get_evolve_args_from_terminal() -> EvolveArgs:
    "Generates EvolveArgs from terminal values"
    return EvolveArgs()

def get_evolve_args_from_argument_string(arguments:str) -> EvolveArgs:
    "Generates EvolveArgs from string"
    return EvolveArgs(arguments)
    
def run():
    ## Parsing Args and configuring Variables
    args:EvolveArgs = get_evolve_args_from_terminal()

    ## TODO: DELETE ME WHEN args are Logged
    if (args.print_only):
        print(f"Arguments Detected:  {args}") # probably should log this instead. not sure if with logger directly or through config.

    # Run Evolution class, which actually executes an experiment
    evolution = Evolution()
    evolution.evolve(
        primary_config_path =       args.config,
        base_config_path =          args.base_config,
        output_directory =          args.output_directory,
        experiment_description =    args.description,
        built_config_path=          args.built_config_path,
        print_action_only=          args.print_only
    )

if __name__ == "__main__":
    run()
