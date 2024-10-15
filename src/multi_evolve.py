#! /bin/python3
# This program calls evolve.py multiple times in order to run multiple evolutionary experiments.


import argparse
from Evolution import Evolution
from evolve import BUILT_CONFIG_PATH, program_description as evolve_program_description
from arg_parse_utils import add_bool_argument
from functools import partial

program_name="multi_evolve"
program_description=f"""This function runs multiple evolution simulations specified by multiple config files.
All files will presume the main directory of BitStreamEvolution unless absolute path given.

The Evolution Simulator works as follows: 
---
{evolve_program_description}
---
"""
program_epilog="""
Exit Status:
0 - No issues
1 - Issue while running
130 - Keyboard Interrupt"""

default_config_array = None #Use none if want specified
default_base_config = None
default_output_directory = None #If not changed, information only saved internally.
default_experiment_description = "multi_evolve.py for config file: '{config}' itteration number: {config_num}" #If not changed, requires user to enter.

parser = argparse.ArgumentParser(prog=program_name,
                                 description=program_description,
                                 epilog=program_epilog)
parser.add_argument('-c','--configs',type=str,nargs='*',default=default_config_array,
                   help=f"")
parser.add_argument('-bc','--base-config',type=str,default=default_base_config,
                    help= f"The config any unspecified values in the main config is pulled from. " +\
                        f"This overpowers the main config specified in the file if provided. Default: {default_base_config}")
parser.add_argument('-o','--output-directory', type=str,default=default_output_directory,
                    help=f"The directory output from the simulation is copied to after a successful simulation. Default: {default_output_directory}")
parser.add_argument('-d','--description', type=str,default=default_experiment_description,
                    help="The description of this simulation. Requires manual entry if not an argument.")
flags = {'enable':["-p","--print_only", "--no-action","--test"],
         'disable':['-np',"--no-print-only",'--act']}
add_bool_argument(parser,"print_only",flag_names=flags,default=False)
# --help is added by default

## need to add a way to create custom experiment descriptions.
## This allows us to pass in an evolution object to test functionality.
def evolve_list_of_configs_selecting_evolution(*configs:str,
                           base_config:str,
                           output_directory:str,
                           experiment_description:str,
                           print_action_only:bool=False,
                           evolution_object:Evolution = Evolution()
                           ):
    """This functin evolves a list of configs. 
    In experiment desctiption, the strings '{config}' for the current config's file path and 
    '{config_num}' for the itterastion number of the experiment."""
     #"multi_evolve.py for config file: '{config}' itteration number: {config_num}"

    if (evolution_object == None):
        evolution_object = Evolution()

    config_num = 1
    for config in configs:

        formatted_name = experiment_description.format(config=config,config_num=config_num)
        
        if (print_action_only):
            print(f"multi-evolve:{{config:{config},output:{output_directory},base_config:{base_config},description:{experiment_description}}}")

        evolution_object.evolve(
            primary_config_path=    config,
            output_directory=       output_directory,
            base_config_path=       base_config,
            built_config_path=      BUILT_CONFIG_PATH,
            experiment_description= formatted_name,
            print_action_only=      print_action_only
        )
        
        config_num += 1

# create origional function by partially completing the function, relying on None to make the function create it's own evolution_object
evolve_list_of_configs = partial(evolve_list_of_configs_selecting_evolution,evolution_object=None)

def run():
    args=parser.parse_args()

    evolve_list_of_configs(
        configs=args.configs,
        base_config=args.base_config,
        output_directory=args.output_directory,
        experiment_description=args.description,
        print_action_only=args.print_only
    )

if __name__ == "__main__":
    run()