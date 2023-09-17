import argparse
from ConfigBuilder import ConfigBuilder

# This runs as a separate program, taking in the input config path and the output path for the final config
# It will follow the linked list of config files (with the base_config param)
# and output the final config at the specified location

program_name="config_builder"
program_description="""This program combines config files together and outputs a single, final config."""
program_epilog=""
parser = argparse.ArgumentParser(prog=program_name,
                                 description=program_description,
                                 epilog=program_epilog)
parser.add_argument('-i', '--input', type=str, help="The input config file to use")
parser.add_argument('-o', '--output', type=str, help="The path to output the result to")
# NOTE: Could add arg to override the default config

args = parser.parse_args()

input = args.input
output = args.output

configBuilder = ConfigBuilder(input)
configBuilder.build_config(output)