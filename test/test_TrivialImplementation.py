from pathlib import Path
from random import Random
from BitstreamEvolutionProtocols import FPGA_Compilation_Data, FPGA_Model, Population
from TrivialImplementation import TrivialCircuit, TrivialCircuitFactory, TrivialReproduce, TrivialGenerateInitialPopulation
from result import Result, Ok, Err # type: ignore
import pytest # type: ignore
from collections.abc import Generator
import functools as ft


## ------------------------------------------------- Mocks & Fixtures -------------------------------------------------

@pytest.fixture
def FPGA_compilation_data()->Generator[FPGA_Compilation_Data,None,None]:
    #Do setup
    yield FPGA_Compilation_Data(FPGA_Model.ICE40,"randomID") #get object
    #Do Cleanup

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

## ----------------------------------------- Other People's Tests ----------------------------------------------------
@pytest.mark.skip
def test_TrivialReproduce_KeepsTopHalf():
    pop = []
    fits = []
    for f in range(100):
        pop.append(TrivialCircuit(f + 1))
        fits.append(f + 1)
    population = Population(pop, fits)
    r = TrivialReproduce(Random())
    result = r(population)
    print(result)
    fit_list = list(map(lambda x: x[1], iter(result)))
    for f in range(50):
        fit = f + 50
        assert fit in fit_list
    # also, we know all individuals should have >= 49 fitness, and <= 101
    assert all(map(lambda x: x is not None and x <= 101 and x >= 49, fit_list))

@pytest.mark.parametrize("size", [1,2,3,6,10,100,1000])
def test_TrivialGenerateInitialPopulation_ReturnsCorrectlySizedPopulation(size):
    population:Population[TrivialCircuit] = TrivialGenerateInitialPopulation(
        population_size= size,
        random= Random(),
        min_fitness= 0,
        max_fitness= 100
    )
    assert len(list(population)) == size, f"Generated population with {len(list(population))} not {size} individuals."