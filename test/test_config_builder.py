from ConfigBuilder import ConfigBuilder
import os
import re
from test_utils import compare_files

# Build paths OS-agnostically so we can test on Windows and Linux

def test_baseless():
    '''
    This tests the baseless config file
    It has no base file, so it should have similar output to the input, but we expect certain comments to be removed
    '''
    input = os.path.join('test', 'res', 'inputs', 'baseless_config.ini')
    output = os.path.join('test', 'out', 'baseless_output.ini')
    expected = os.path.join('test', 'res', 'expected_out', 'baseless_expected.ini')
    configBuilder = ConfigBuilder(input)
    configBuilder.build_config(output)
    compare_files(expected, output)

def test_single_base():
    '''
    This tests a single config file with one base file
    '''
    input = os.path.join('test', 'res', 'inputs', 'tree_config1.ini')
    output = os.path.join('test', 'out', 'tree1_output.ini')
    expected = os.path.join('test', 'res', 'expected_out', 'tree1_expected.ini')
    configBuilder = ConfigBuilder(input)
    configBuilder.build_config(output)
    compare_files(expected, output)

def test_double_base():
    '''
    This tests a config file with 2 base files (layered)
    '''
    input = os.path.join('test', 'res', 'inputs', 'tree_config2.ini')
    output = os.path.join('test', 'out', 'tree2_output.ini')
    expected = os.path.join('test', 'res', 'expected_out', 'tree2_expected.ini')
    configBuilder = ConfigBuilder(input)
    configBuilder.build_config(output)
    compare_files(expected, output)

def test_override_base():
    '''
    This tests a config file, but with the base config overridden
    '''
    input = os.path.join('test', 'res', 'inputs', 'tree_config2.ini')
    output = os.path.join('test', 'out', 'override_output.ini')
    expected = os.path.join('test', 'res', 'expected_out', 'override_expected.ini')
    configBuilder = ConfigBuilder(input, override_base_config=os.path.join('test', 'res', 'inputs', 'baseless_config.ini'))
    configBuilder.build_config(output)
    compare_files(expected, output)