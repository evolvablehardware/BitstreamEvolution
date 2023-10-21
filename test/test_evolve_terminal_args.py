import argparse
from subprocess import run
import os
import pytest
from typing import Callable
import evolve 

#NOTE: This runs expecting to start in the BitstreamEvolution parent directory

@pytest.fixture
def evolve_arg_parse_function() -> Callable[[str],evolve.EvolveArgs]:
    return evolve.get_evolve_args_from_argument_string
    

def test_terminal_connects():
    """Verify that any failures are with the command running rather than our setup to run the command."""

    program = run("ls".split(" "),capture_output=True)
    assert program.returncode == 0
    assert program.stdout is not None

def test_evolve_runs_without_error():
    """Verify that evolve, running in --test mode does not error out, and writes to stdout"""

    program = run("python3 src/evolve.py --test".split(" "),capture_output=True)
    empty = [None,'',b'']
    # assert no errors, standard printout
    assert program.returncode == 0
    assert program.stderr in empty
    assert program.stdout not in empty

@pytest.mark.parametrize("flag",["-c","--config"])
@pytest.mark.parametrize("configName",["config.ini","config1.ini","thisIsAVeryLongConfigNameThatShouldWorkWellConfig.ini","conf_01.ini","conf.file.ini"])
def test_config_only_is_interpreted(flag:str,configName:str,evolve_arg_parse_function:Callable):
    "Tests the config is interpreted correctly"

    terminal_arguments = flag+" "+configName
    args:evolve.EvolveArgs = evolve_arg_parse_function(terminal_arguments)
    assert args.config == configName, "'"+terminal_arguments + "' was not valid"

@pytest.mark.parametrize("flag",['-bc','--base-config'])
@pytest.mark.parametrize("configName",["config.ini","config1.ini","thisIsAVeryLongConfigNameThatShouldWorkWellConfig.ini","conf_01.ini"])
def test_base_config_only_is_interpreted(flag:str,configName:str,evolve_arg_parse_function:Callable):
    "Tests the base config is interpreted correctly"

    terminal_arguments = flag+" "+configName
    args:evolve.EvolveArgs = evolve_arg_parse_function(terminal_arguments)
    assert args.base_config == configName, "'"+terminal_arguments + "' was not valid"

@pytest.mark.parametrize("flag",['-o','--output-directory'])
@pytest.mark.parametrize("outputName",["output/","out","out-put_directory/"])
def test_output_directory_only_is_interpreted(flag:str,outputName:str,evolve_arg_parse_function:Callable):
    "Tests the output directory is interpreted correctly"

    terminal_arguments = flag+" "+outputName
    args:evolve.EvolveArgs = evolve_arg_parse_function(terminal_arguments)
    assert args.output_directory == outputName, "'"+terminal_arguments + "' was not valid"

@pytest.mark.parametrize("flag",['-d','--description'])
@pytest.mark.parametrize("descriptionText",["''",'"sdsafasdfasdf"',"'This is a great description.'",
                                            '"This is a great description that keeps going for quite a while and will take a while."'])
def test_description_only_is_interpreted(flag:str,descriptionText:str,evolve_arg_parse_function:Callable):
    "Tests the description is interpreted correctly."

    terminal_arguments = flag+" "+descriptionText
    args:evolve.EvolveArgs = evolve_arg_parse_function(terminal_arguments)
    assert args.description == descriptionText, "'"+terminal_arguments + "' was not valid"

@pytest.mark.parametrize("flag",['-p','--print-only','--test','--no-action'])
def test_print_only_alone_is_interpreted(flag:str,evolve_arg_parse_function:Callable):
    "Tests the print only flag is interpreted correctly."

    terminal_arguments = flag
    args:evolve.EvolveArgs = evolve_arg_parse_function(terminal_arguments)
    assert args.print_only == True, "'"+terminal_arguments + "' was not valid"

@pytest.mark.parametrize("flag",["",'-np', '--no-print-only','--normal','--act'])
def test_specify_default_action_alone_is_interpreted(flag:str,evolve_arg_parse_function:Callable):
    "Tests the standard action flag is interpreted correctly and is default."

    terminal_arguments = flag
    args:evolve.EvolveArgs = evolve_arg_parse_function(terminal_arguments)
    assert args.print_only == False, "'"+terminal_arguments + "' was not valid"


def test_normal_queries(evolve_arg_parse_function:Callable[[str],evolve.EvolveArgs]):
    "Tests queries that specify a config and a description simultaniously."

    configName,description = "configName.ini","'this is the description that I am writing.'"
    args = evolve_arg_parse_function(f"-c {configName} -d {description}")
    assert args.config == configName
    assert args.description == description

    configName,description = "configName.ini","'this is the description that I am writing.'"
    args = evolve_arg_parse_function(f"--config {configName} --description {description}")
    assert args.config == configName
    assert args.description == description

def test_complex_queries(evolve_arg_parse_function:Callable[[str],evolve.EvolveArgs]):
    "This test runs some arguments with variations that specify all values."

    configName = "thisStrangeConfig_File.thing.ini"
    baseConfigName = "baseConfig.ini"
    outputDirName = "output/directory/"
    description = '''"Isn\'t this just a wonderful description. I think it is."'''
    printOnly = True

    def assert_args_set_correctly():
        assert args.config == configName
        assert args.base_config == baseConfigName
        assert args.output_directory == outputDirName
        assert args.description == description
        assert args.print_only == printOnly

    argument = f"""-c {configName} -bc {baseConfigName} -o {outputDirName} -d {description} -p"""
    args = evolve_arg_parse_function(argument)
    assert_args_set_correctly()

    argument = f"""-c {configName} --print-only --description {description} -o {outputDirName} -bc {baseConfigName}"""
    args = evolve_arg_parse_function(argument)
    assert_args_set_correctly()

    printOnly = False

    argument = f"""--config {configName} -d {description} -o {outputDirName} -bc {baseConfigName}"""
    args = evolve_arg_parse_function(argument)
    assert_args_set_correctly()

    argument = f"""--act -o {outputDirName} -c {configName} -d {description} -bc {baseConfigName}"""
    args = evolve_arg_parse_function(argument)
    assert_args_set_correctly()

    argument = f"""-d {description} --no-print-only --output-directory {outputDirName} -c {configName} -bc {baseConfigName}"""
    args = evolve_arg_parse_function(argument)
    assert_args_set_correctly()