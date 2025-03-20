import argparse

"""This file is where we can keep scripts to interpret arguments that are going to be used in multiple command-line scripts.
This is intended to keep imports clear and allow easy reuse of this code."""

def add_bool_argument(arg_parser:argparse.ArgumentParser,
                 feature_name:str,
                 flag_names:{'enable':[str],'disable':[str]} = {'enable':[],'disable':[]}, #pyright: ignore
                 default:bool=False,
                 is_required:bool=False):
    "This allows you to create mutually exclusive boolean flags for the feature, and even specify the names of the flags you desire to switch it with, but you don't need to."
    
    group = arg_parser.add_mutually_exclusive_group(required=is_required)

    ## create all flags enabling it
    if len(flag_names['enable']) == 0:
        group.add_argument('--'+feature_name,dest=feature_name,action="store_true")
    else:
        for flag in flag_names['enable']:
            group.add_argument(flag,dest=feature_name,action="store_true")

    ## create all flags disabling it
    if len(flag_names['disable']) == 0:
        group.add_argument('--no-'+feature_name,dest=feature_name, action="store_false")
    else:
        for flag in flag_names['disable']:
            group.add_argument(flag,dest=feature_name, action='store_false')

    arg_parser.set_defaults(**{feature_name:default})