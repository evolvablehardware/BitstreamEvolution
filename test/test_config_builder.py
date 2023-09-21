from ConfigBuilder import ConfigBuilder
import os
import re

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
    __compare_files(expected, output)

def test_single_base():
    '''
    This tests a single config file with one base file
    '''
    input = os.path.join('test', 'res', 'inputs', 'tree_config1.ini')
    output = os.path.join('test', 'out', 'tree1_output.ini')
    expected = os.path.join('test', 'res', 'expected_out', 'tree1_expected.ini')
    configBuilder = ConfigBuilder(input)
    configBuilder.build_config(output)
    __compare_files(expected, output)

def test_double_base():
    '''
    This tests a config file with 2 base files (layered)
    '''
    input = os.path.join('test', 'res', 'inputs', 'tree_config2.ini')
    output = os.path.join('test', 'out', 'tree2_output.ini')
    expected = os.path.join('test', 'res', 'expected_out', 'tree2_expected.ini')
    configBuilder = ConfigBuilder(input)
    configBuilder.build_config(output)
    __compare_files(expected, output)

def __compare_files(path1, path2):
    '''
    Reads in the contents of two files as a string list of lines, and returns on the equality of each line
    '''
    f1 = open(path1, 'r')
    f2 = open(path2, 'r')
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    f1.close()
    f2.close()
    assert len(lines1) == len(lines2)
    for i in range(len(lines1)):
        l1 = lines1[i].rstrip()
        l2 = lines2[i].rstrip()
        assert l1 == l2

# Prevent this function from being run as a test
__compare_files.__test__ = False