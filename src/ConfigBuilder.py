from configparser import ConfigParser
import re

from ConfigValue import ConfigValue

BASE_CONFIG_PARAM_SECTION = 'TOP-LEVEL PARAMETERS'
BASE_CONFIG_PARAM_NAME = 'base_config'

'''
Takes in an input config to use, and will output the fully-built config file to the specified path
when build_config is called
'''
class ConfigBuilder:
    def __init__(self, input, override_base_config = None):
        self.__input = input
        self.__override_base_config = override_base_config

    def build_config(self, output):
        '''
        Uses the base configs of the input to build an internal representation of the final config file,
        then output it to the specified output file
        '''
        config_values = self.__get_config_values_from_file(self.__input, self.__override_base_config)
        # TODO: Save config_values to a file

    def __get_config_values_from_file(self, input, override_base_config = None):
        '''
        Returns the config values by reading in the file
        This will include all config values, recursing into base configs if needed
        '''
        config_parser = ConfigParser()
        config_parser.read(input)
        file = open(input, mode='r')
        config_lines = file.readlines()
        file.close()
        base_config_path = None
        if override_base_config != None:
            base_config_path = override_base_config
        elif config_parser.has_option(BASE_CONFIG_PARAM_SECTION, BASE_CONFIG_PARAM_NAME):
            base_config_path = config_parser.get(BASE_CONFIG_PARAM_SECTION, BASE_CONFIG_PARAM_NAME)
        # Get the values from the base config & current config
        config_values = self.__get_config_values(config_parser, config_lines)
        base_values = []
        if base_config_path != None:
            base_values = self.__get_config_values_from_file(base_config_path)
        # Okay, now we need to merge with the values we find in our own file
        # To do this, we will add from base_values only if we don't currently have the specified value 
        # in our config_values list
        for val in base_values:
            if not self.__config_values_contains(config_values, val):
                config_values.append(val)
        return config_values

    def __get_config_values(self, config_parser, config_lines):
        '''
        This will return a list of ConfigValue
        This function reads the input file, gathering every config value
        It will basically just convert everything from config parser into our ConfigValue class
        '''
        sections = config_parser.sections()
        result_list = []
        for section in sections:
            for (key, val) in config_parser.items(section):
                comment = self.__get_comment_for_param(section, key, config_lines)
                result_list.add(ConfigValue(section, key, val, comment))

    def __get_comment_for_param(self, section, param, config_lines):
        '''
        This will find the specified section and return a list of comment lines (without the comment signifier)
        that appear above this config parameter
        '''
        # Need to find the line with this section
        section_line_index = -1
        for i in range(len(config_lines)):
            line = config_lines[i]
            if line.startswith('[' + section + ']'):
                section_line_index = i
                break
        # If section doesn't exist, need to throw error
        if section_line_index < 0:
            raise Exception('The section ' + section + ' could not be found')
        # Next we need the line of this parameter, starting at the section line until we find a line that
        # has brackets (i.e. another section)
        param_line_index = -1
        for i in range(section_line_index + 1, len(config_lines)):
            line = config_lines[i]
            if re.search(r"^" + re.escape(param) + r"\s*\=.*$", line) != None:
                # We've found the param line, so just break out since our index is properly set now
                param_line_index = i
                break
            if line.startswith('['):
                break

        if param_line_index < 0:
            raise Exception('The parameter ' + param + ' could not be found in section ' + section + '\n' + str(config_lines[section_line_index:]))

        # At this point we have our parameter line, just need to iterate backwards until
        # we hit a non-comment line
        i = param_line_index
        comments = []
        while i >= 0:
            line = config_lines[i]
            if line.startswith(';'):
                # Take out the first character, which is the ';'
                comments.append(line[1:])
            else:
                # Non-comment line, so we should stop adding comments
                break
            i = i - 1

        return comments

    def __config_values_contains(self, config_values, config_value):
        for val in config_values:
            if val.section == config_value.section and val.param == config_value.param:
                return True
        return False