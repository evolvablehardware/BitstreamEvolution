from configparser import ConfigParser
from configparser import NoOptionError
from pathlib import Path

from ConfigValue import ConfigValue

BASE_CONFIG_PARAM_SECTION = 'TOP-LEVEL PARAMETERS'
BASE_CONFIG_PARAM_NAME = 'base_config'

'''
Takes in an input config to use, and will output the fully-built config file to the specified path
when build_config is called
'''
class ConfigBuilder:
    def __init__(self, input, override_base_config = None):
        self.__config_parser = ConfigParser()
        self.__config_parser.read(input)
        self.__override_base_config = override_base_config

        # Also read all the text so we can get the comments as well
        file = open(input, mode='r')
        self.__config_lines = file.readlines()
        file.close()

    def build_config(self, output):
        configvals = self.__get_config_values()
        base_config_path = self.__override_base_config if self.__override_base_config != None else self.__config_parser.get(BASE_CONFIG_PARAM_SECTION, BASE_CONFIG_PARAM_NAME)

    def __get_config_values(self):
        '''
        This will return a list of ConfigValue
        This function reads the input file, gathering every config value
        It will basically just convert everything from config parser into our ConfigValue class
        '''
        sections = self.__config_parser.sections()
        result_list = []
        for section in sections:
            for (key, val) in self.__config_parser.items(section):
                comment = self.__get_comment_for_param(section, key)
                result_list.add(ConfigValue(section, key, val, comment))

    def __get_comment_for_param(self, section, param):
        '''
        This will find the specified section and return a list of comment lines (without the comment signifier)
        that appear above this config parameter
        '''
        # Need to find the line with this section
        section_line_index = -1
        for i in range(len(self.__config_lines)):
            line = self.__config_lines[i]
            if line == '[' + section + ']':
                section_line_index = i
                break
        # If section doesn't exist, need to throw error
        if section_line_index < 0:
            raise Exception('The section ' + section + ' could not be found')
        # Next we need the line of this parameter, starting at the section line until we find a line that
        # has brackets (i.e. another section)
        param_line_index = section_line_index
        while True:
            line = self.__config_lines[param_line_index]
            if line.startswith(param + '='):
                # We've found the param line, so just break out since our index is properly set now
                break
            if line.startswith('['):
                # We've found a new section without ever hitting our desired parameter,
                # so throw an exception
                raise Exception('The parameter ' + param + ' could not be found in section ' + section)
            param_line_index = param_line_index + 1

        # At this point we have our parameter line, just need to iterate backwards until
        # we hit a non-comment line
        i = param_line_index
        comments = []
        while i >= 0:
            line = self.__config_lines[i]
            if line.startswith(';'):
                # Take out the first character, which is the ';'
                comments.append(line[1:])
            else:
                # Non-comment line, so we should stop adding comments
                break
            i = i - 1

        return comments