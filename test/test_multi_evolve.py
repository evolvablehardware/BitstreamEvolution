#! /bin/python
import pytest

from collections.abc import Iterator  

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
    
    def assert_evolve_call_contains(self,callIndex,args:[(str,any)]):
        call_argument_dict:dict = self.previous_evolve_argument_list[callIndex]
        for argument in args:
            if not argument[0] in call_argument_dict:
                raise IndexError(f"Argument '{argument[0]}' not found in evolve call. Available arguments are: '{call_argument_dict.keys()}'")

            assert argument[1] == call_argument_dict[argument[0]], f"Argument '{argument[0]}' did not match on evolve call index {callIndex}. {args[argument]} != {call_argument_dict[argument]}."

    def assert_last_evolve_call_contains(self,args:[(str,any)]):
        self.assert_evolve_call_contains(len(self.previous_evolve_argument_list)-1,args)

    def assert_all_calls_contain(self,args:[(str,any)]):
        for call_dict_index in range(len(self.previous_evolve_argument_list)):
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

@pytest.fixture
def test_evolution_object(monkeypatch) -> Iterator[TestEvolution]:
    test_evolution = TestEvolution()
    monkeypatch.setattr(multi_evolve,"evolution",test_evolution)
    yield test_evolution
    #any taredown code goes here



@pytest.mark.parametrize("configName",[("config1"),
                                       ("config2"),
                                       ("config3")])
def test_single_configRecieved(configName:str,test_evolution_object:TestEvolution):
    """Verify that when a single config is passed in multiEvolve works properly."""
    assert not test_evolution_object.evolve_was_called() 
    multi_evolve.evolve_list_of_configs(
        configName,
        base_config="base-config",
        output_directory="output-directory",
        experiment_description="experiment-description",
        print_action_only=False
        )
    
    test_evolution_object.assert_last_evolve_call_contains([(TestEvolution.PRIMARY_CONFIG_PATH,configName),
                                                            (TestEvolution.BASE_CONFIG_PATH,"base-config"),
                                                            (TestEvolution.OUTPUT_DIRECTORY,"output-directory"),
                                                            (TestEvolution.EXPERIMENT_DESCRIPTION,"experiment-description"),
                                                            (TestEvolution.PRINT_ACTION_ONLY,False)])



