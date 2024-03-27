#! /bin/python
import pytest

from collections.abc import Iterator  
from functools import partial

from typing import Callable
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
        self.evolve_call_count += 1
        self.previous_evolve_argument_list.append(argument_dict)

    def evolve_was_called(self)->bool:
        return self.evolve_call_count > 0
    
    def get_evolve_call_count(self)->int:
        return self.evolve_call_count
    
    def assert_evolve_call_contains(self,callIndex,args:list[(str,any)]):
        """Loops through every arg name and checks if it matches the value passed in with it in the tupple."""
        call_argument_dict:dict = self.previous_evolve_argument_list[callIndex]

        for argument in args:
            if not argument[0] in call_argument_dict:
                raise IndexError(f"Argument '{argument[0]}' not found in evolve call. Available arguments are: '{call_argument_dict.keys()}'")

            assert argument[1] == call_argument_dict[argument[0]], f"Argument '{argument[0]}' did not match on evolve call index {callIndex}. {args[argument]} != {call_argument_dict[argument]}."

    def assert_last_evolve_call_contains(self,args:list[(str,any)]):
        self.assert_evolve_call_contains(len(self.previous_evolve_argument_list)-1,args)

    def assert_all_calls_contain(self,args:list[(str,any)]):
        for call_dict_index in range(len(self.previous_evolve_argument_list)):
            self.assert_evolve_call_contains(call_dict_index,args)

    def all_evolve_call_arguments(self)->list[dict]:
        return self.previous_evolve_argument_list

TestEvolution.__test__ = False


@pytest.fixture
def test_evolution_object() -> Iterator[TestEvolution]:
    test_evolution_object = TestEvolution()
    yield test_evolution_object
    #any teardown code here


@pytest.fixture
def test_evolve_list_of_configs(test_evolution_object) -> Iterator[Callable]:
    test_evolve_list_of_configs = partial(multi_evolve.evolve_list_of_configs_selecting_evolution,evolution_object=test_evolution_object)
    yield test_evolve_list_of_configs


def test_check_call_count_on_mock(test_evolution_object:TestEvolution,test_evolve_list_of_configs:Callable):
    test_evolution_object.evolve_call_count

## Test Values passed to EvolutionObject Correctly.

@pytest.mark.parametrize("configName",["config1",
                                       "config2",
                                       "config3",
                                       "config4"])
def test_single_config_recieved(configName:str,test_evolution_object:TestEvolution,test_evolve_list_of_configs:Callable):
    """Verify that when a single config is passed in multiEvolve works properly."""
    assert not test_evolution_object.evolve_was_called() 
    #call evolve list of configs on test_evolution_object
    print(type(configName))
    test_evolve_list_of_configs(
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


@pytest.mark.parametrize("configs_name",[("configs1","configs2","configs3"),
                                        ("configA.txt","configB.txt"),
                                        ("configThing.ini","configActivity.ini","anotherName.ini","things.ini","lastLittleThing.ini")])
def test_multiple_config_recieved(configs_name:[str],test_evolution_object:TestEvolution,test_evolve_list_of_configs:Callable):
    """Verify that when multiple configs are passed in multiEvolve calls evolve properly."""
    assert not test_evolution_object.evolve_was_called()

    #call evolve on test object
    test_evolve_list_of_configs(
        *configs_name, # unpack tupple of config names
        base_config="base-config",
        output_directory="output-directory",
        experiment_description="experiment-description",
        print_action_only=False
    )

    test_evolution_object.assert_all_calls_contain([(TestEvolution.BASE_CONFIG_PATH,"base-config"),
                                                    (TestEvolution.OUTPUT_DIRECTORY,"output-directory"),
                                                    (TestEvolution.EXPERIMENT_DESCRIPTION,"experiment-description"),
                                                    (TestEvolution.PRINT_ACTION_ONLY,False)])
    
    # verify the configs are in the same order and are the same values
    configs_evolved:list[str] = list(map(lambda call: call[TestEvolution.PRIMARY_CONFIG_PATH], test_evolution_object.all_evolve_call_arguments()))

    assert test_evolution_object.get_evolve_call_count() == len(configs_name), "Incorrect number of calls ("+str(test_evolution_object.get_evolve_call_count())+")"
    for i in range(len(configs_name)):
        assert configs_name[i] == configs_evolved[i], "Error: "+str(configs_name)+"!="+str(configs_evolved)


