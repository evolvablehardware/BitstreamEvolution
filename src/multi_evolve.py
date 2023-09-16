import argparse
from evolve import program_description as evolve_description

program_name="multi_evolve"
program_description=f"""This function runs multiple evolution simulations specified by multiple config files.
All files will presume the main directory of BitStreamEvolution unless absolute path given.

The Evolution Simulator works as follows: 
---
{evolve_description}
---
"""
program_epilog="""
Exit Status:
0 - No issues
1 - Issue while running
130 - Keyboard Interrupt"""

default_config = None #Use none if want specified
default_base_config = None
default_output_directory = None #If not changed, information only saved internally.
default_experiment_description = None #If not changed, requires user to enter.

parser = argparse.ArgumentParser(prog=program_name,
                                 description=program_description,
                                 epilog=program_epilog)
parser.add_argument('-c','--config',type=[str],default=default_config,
                   help=f"")
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




def evolve_list_of_configs(base_config,*configs):
    for config in configs:
        


