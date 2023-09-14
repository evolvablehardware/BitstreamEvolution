from configparser import ConfigParser
from configparser import NoOptionError
from pathlib import Path

'''
Takes in an input config to use, and will output the fully-built config file to the specified path
when build_config is called
'''
class ConfigBuilder:
    def __init__(self, input, override_base_config):
        self.__config_parser = ConfigParser()
        self.__config_parser.read(input)

    def build_config(self, output):

        print('hi')

    def __get_config_values(self):
        '''
        This will return a list of ConfigValue
        This function reads the input file, gathering every config value
        It will basically just convert everything from config parser into our ConfigValue class
        '''
        top_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        fitness_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        ga_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        init_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        stop_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        logging_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        system_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))
        hw_params = dict(self.__config_parser.items("TOP-LEVEL PARAMETERS"))