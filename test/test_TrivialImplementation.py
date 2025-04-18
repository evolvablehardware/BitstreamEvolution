from pathlib import Path
from random import Random
from BitstreamEvolutionProtocols import FPGA_Compilation_Data, FPGA_Model, Population, GenerateInitialPopulation
from TrivialImplementation import TrivialCircuit, TrivialCircuitFactory, TrivialReproduce, TrivialGenerateInitialPopulation
from result import Result, Ok, Err # type: ignore
import pytest # type: ignore
from pytest_mock import MockerFixture
from collections.abc import Generator,Iterable
import functools as ft

## ------------------------------------------------- Mocks & Fixtures -------------------------------------------------

@pytest.fixture
def FPGA_compilation_data()->Generator[FPGA_Compilation_Data,None,None]:
    #Do setup
    yield FPGA_Compilation_Data(FPGA_Model.ICE40,"randomID") #get object
    #Do Cleanup

def Generate_Population_From_Iterable(inherent_fitnesses:Iterable[int],
                                      fitnesses_discovered:bool)->Population[TrivialCircuit]:
    """
    Returns a population of circuits with the inherent_fitnesses specified, 
    which is also stored in the population if fitness_discovered==true."
    """
    if fitnesses_discovered:
        return Population([TrivialCircuit(f) for f in inherent_fitnesses],[f for f in inherent_fitnesses])
    else:
        return Population([TrivialCircuit(f) for f in inherent_fitnesses],None)
    

## ----------------------- Circuit & Individual & CircuitFactory Tests (Isaac) ---------------------------------------

def test_TrivialCircuit_SetsInherentFitness():
    assert TrivialCircuit( 34).inherent_fitness ==  34
    assert TrivialCircuit(-23).inherent_fitness == -23

#This test uses the fixture seen above
def test_TrivialCircuit_ImplementsCompile(FPGA_compilation_data:FPGA_Compilation_Data):
    output = TrivialCircuit(23).compile(FPGA_compilation_data, Path("random", "dir"))
    match output:
        case Ok(filepath):
            pass #don't care what this is
        case Err(error):
            assert False, f"This should not return an Exception, but returned {error}"
        case _:
            assert False, f"This should return a Result, instead was {output}"

def test_TrivialCircuitFatory_ReturnsTheIndividualAsACircuit():
    individual = TrivialCircuit(34)
    circuit = TrivialCircuitFactory([individual])[0]
    assert individual is circuit, "Should return the exact same object"

## ----------------------------------------- Generate Initial Population ----------------------------------------------------

@pytest.mark.parametrize("size", [1,2,3,6,10,100,1000])
def test_TrivialGenerateInitialPopulation_ReturnsCorrectlySizedPopulation(size):
    population:Population[TrivialCircuit] = TrivialGenerateInitialPopulation(
        population_size= size,
        random= Random(),
        min_fitness= 0,
        max_fitness= 100
    )
    assert len(list(population)) == size, f"Generated population with {len(list(population))} not {size} individuals."

def test_TrivialGenerateInitialPopulation_GeneratesIndividualsWithRandomInt(monkeypatch,mocker:MockerFixture):
    rand = Random()
    min_fit = 34
    max_fit = 69
    population_size = 200
    rand_returns = []   + [34]*50 \
                        + [45]*50 \
                        + [52]*50 \
                        + [69]*50
    
    mock_randint = mocker.patch.object(rand,"randint",side_effect = rand_returns)

    pop = TrivialGenerateInitialPopulation(
        population_size = population_size,
        random          = rand,
        min_fitness     = min_fit,
        max_fitness     = max_fit
    )

    assert len(list(pop)) == population_size
    assert mock_randint.call_count == population_size, "randint() should be called once for each individual"
    assert all((i.args[0] == min_fit for i in mock_randint.call_args_list)), "Should always pass the minimum fitness as first argument"
    assert all((i.args[1] == max_fit for i in mock_randint.call_args_list)), "Should always pass the max fitness as second argument"

    assert all([i[1] is None for i in pop]), "All fitnesses should be set to None"
    inherent_fitnesses = [i[0].inherent_fitness for i in pop]
    assert sorted(inherent_fitnesses) == sorted(rand_returns), "all fitnesses should be assigned based on rand return value"


def test_TrivialGenerateInitialPopulation_ReturnsEmptyPopulationIfZeroOrNegativePopulationSize():
    
    result = TrivialGenerateInitialPopulation(0,Random(),0,100)
    assert len(list(result)) == 0, "Population_size=0 should Be an Empty Population"
    
    result = TrivialGenerateInitialPopulation(-1,Random(),0,100)
    assert len(list(result)) == 0, "Population_size=-1 should Be an Empty Population"
    
    result = TrivialGenerateInitialPopulation(-43,Random(),0,100)
    assert len(list(result)) == 0, "Population_size=-43 should Be an Empty Population"

def test_TrivialGenerateInitialPopulation_WorksWithPartial(mocker:MockerFixture):
    
    rand = Random()

    partial_func:GenerateInitialPopulation = \
            ft.partial(TrivialGenerateInitialPopulation,
                        random = rand,
                        min_fitness = 34,
                        max_fitness = 100)
    
    mocker.patch.mock_module

    spy_rand = mocker.spy(rand,"randint")

    result = partial_func(10)

    assert len(list(result)) == 10
    assert spy_rand.call_count == 10
    assert all(map(lambda call: call.args[0] == 34 and call.args[1] == 100, spy_rand.call_args_list)),\
          "Fitness limits should be passed by functools.partial() and used in function."

    spy_rand.reset_mock()

    result = partial_func(100)

    assert len(list(result)) == 100
    assert spy_rand.call_count == 100
    assert all(map(lambda call: call.args[0] == 34 and call.args[1] == 100, spy_rand.call_args_list)),\
          "Fitness limits should be passed by functools.partial() and used in function."

## -------------------------------------- Reproduce ---------------------------------------------

def test_TrivialReproduce_KeepsTopHalf():
    
    population = Generate_Population_From_Iterable(range(1,100+1),fitnesses_discovered=True)

    r = TrivialReproduce(Random())
    result = r(population)
    print(result)
    fit_list = list(map(lambda x: x[1], iter(result)))
    for f in range(50):
        fit = f + 50
        assert fit in fit_list
    # also, we know all individuals should have >= 49 fitness, and <= 101
    assert all(map(lambda x: x is not None and x <= 101 and x >= 49, fit_list))
