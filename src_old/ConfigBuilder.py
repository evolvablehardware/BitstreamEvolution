from configparser import ConfigParser
import re
from ConfigValue import ConfigValue

BASE_CONFIG_PARAM_SECTION = 'TOP-LEVEL PARAMETERS'
BASE_CONFIG_PARAM_NAME = 'base_config'

# TODO: Add comment w/ list of config files used in the final config output

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
        config_values, files_list = self.__get_config_values_from_file(self.__input, self.__override_base_config)
        self.__output_config_to_file(config_values, files_list, output)

    def __get_config_values_from_file(self, input, override_base_config = None):
        '''
        Multi-value return
        Returns the config values by reading in the file, and the list of config files used to build those values
        This will include all config values, recursing into base configs if needed
        '''
        config_files_list = [ input ]
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
        base_config_files_list = []
        if base_config_path != None:
            base_values, base_config_files_list = self.__get_config_values_from_file(base_config_path)

        config_files_list = config_files_list + base_config_files_list
        # Okay, now we need to merge with the values we find in our own file
        # To do this, we will add from base_values only if we don't currently have the specified value 
        # in our config_values list
        for val in base_values:
            if not self.__config_values_contains(config_values, val):
                config_values.append(val)
        return config_values, config_files_list

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
                if section == BASE_CONFIG_PARAM_SECTION and key == BASE_CONFIG_PARAM_NAME:
                    # Always skip the base config parameter, it is considered not a true parameter and is
                    # never in the result config
                    continue
                comment = self.__get_comment_for_param(section, key, config_lines)
                result_list.append(ConfigValue(section, key, val, comment))
        
        return result_list

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
        i = param_line_index - 1
        comments = []
        while i >= 0:
            line = config_lines[i]
            if line.startswith(';'):
                # Take out the first character, which is the ';', and the whitespace at the end
                # Since we're iterating backwards, need to append to the beginning of the list every time
                comments.insert(0, line[1:].rstrip())
            else:
                # Non-comment line, so we should stop adding comments
                break
            i = i - 1

        return comments

    def __output_config_to_file(self, config_values, files_list, output_path):
        '''
        Outputs the specified config values to an output file
        '''
        sections = self.__consolidate_configvalues_by_section(config_values)
        file = open(output_path, 'w')
        # Write info comment at top, add list of config files used to build
        file.write('; This configuration file was generated through combining the following files:\n')
        for f in files_list:
            # Convert Windows paths to Unix if necessary
            file.write('; ' + f.replace('\\', '/') + '\n')
        # Add a newline before the actual config stuff
        file.write('\n')

        is_first_section = True
        for name, config_values in sections.items():
            # Add the section header to the file first
            # If we are past the first section, add a newline in front of it
            if not is_first_section:
                file.write('\n')
            is_first_section = False
            file.write('[' + name + ']\n')
            for config_value in config_values:
                # Write the comments first, then the actual config value
                for comment in config_value.comment:
                    file.write(';' + comment + '\n')
                # Now write the actual parameter itself
                file.write(config_value.param + ' = ' + self.__escape_config_value(config_value.value) + '\n')
            
        file.close()

    def __config_values_contains(self, config_values, config_value):
        for val in config_values:
            if val.section == config_value.section and val.param == config_value.param:
                return True
        return False

    def __consolidate_configvalues_by_section(self, config_values):
        sections = dict()
        for value in config_values:
            if value.section in sections:
                sections[value.section].append(value)
            else:
                sections[value.section] = [ value ]
        return sections
    
    def __escape_config_value(self, value: str) -> str:
        return value.replace('%', '%%')