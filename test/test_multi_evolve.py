#! /bin/python

import pytest
#from typing import override
def override(func):
    """Temporary structure before implement override in python 3.12 released Today... (10/2/2023) apearently."""
    return func
from Evolution import Evolution
import multi_evolve

class TestEvolution(Evolution):
    """This class is a utility that allows us to easily test evolution by giving us access to all function calls."""

    PRIMARY_CONFIG_PATH = "primary_config_path"
    EXPERIMENT_DESCRIPTION = "experiment_description"
    BASE_CONFIG_PATH = "base_config_path"
    BUILT_CONFIG_PATH = "built_config_path"
    OUTPUT_DIRECTORY = "output_directory"
    PRINT_ACTION_ONLY = "print_action_only"


    def __init__(self):
        super().__init__()
        self.previous_evolve_argument_list = []
        self.evolve_call_count = 0

    @override
    def evolve(self, 
               primary_config_path: str, 
               experiment_description: str, 
               base_config_path: str, 
               built_config_path: str, 
               output_directory: str = None, 
               print_action_only: bool = False) -> None:
        
        argument_dict =  {
            "primary_config_path":      primary_config_path,
            "experiment_description":   experiment_description,
            "base_config_path":         base_config_path,
            "built_config_path":        built_config_path,
            "output_directory":         output_directory,
            "print_action_only":        print_action_only
        }

        self.previous_evolve_argument_list.append(argument_dict)
        self.evolve_call_count+=1

    def evolve_was_called(self)->bool:
        return self.evolve_call_count > 0
    
    def evolve_call_count(self)->int:
        return self.evolve_call_count
    
    def assert_evolve_call_contains(self,callIndex,**args):
        call_argument_dict:dict = self.all_evolve_call_arguments[callIndex]
        for argument in args:
            if not argument in call_argument_dict:
                raise IndexError(f"Argument '{argument}' not found in evolve call. Available arguments are: '{call_argument_dict.keys()}'")

            assert args[argument] == call_argument_dict[argument], f"Argument '{argument}' did not match on evolve call index {callIndex}. {args[argument]} != {call_argument_dict[argument]}."

    def assert_last_evolve_call_contains(self,**args):
        self.assert_evolve_call_contains(len(self.all_evolve_call_arguments)-1,args)

    def assert_all_calls_contain(self,**args):
        for call_dict_index in range(len(self.all_evolve_call_arguments)):
            self.assert_evolve_call_contains(call_dict_index,args)

    def all_evolve_call_arguments(self)->[dict]:
        return self.all_evolve_call_arguments

TestEvolution.__test__ = False

def test_monkeypatch_stuff(monkeypatch):
    testEvolution = TestEvolution()
    #multi_evolve.evolution=testEvolution
    monkeypatch.setattr(multi_evolve,"evolution",testEvolution)
    multi_evolve.evolve_list_of_configs(("nonsenseConfig1","nonsenseConfig2","nonsenseConfig3"),
                           base_config="nonsense",
                           output_directory="nonsense directory",
                           experiment_description="nonsense description",
                           print_action_only=True)
    
    assert testEvolution.evolve_was_called() == True
