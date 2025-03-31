from BitstreamEvolutionProtocols import FPGA_Compilation_Data, FPGA_Model
from TrivialImplementation import TrivialCircuit, TrivialCircuitFactory
from result import Result, Ok, Err
import pytest
from collections.abc import Generator

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
    output = TrivialCircuit(23).compile(FPGA_compilation_data,"random/dir")
    match output:
        case Ok(filepath):
            pass #don't care what this is
        case Err(error):
            assert False, f"This should not return an Exception, but returned {error}"
        case _:
            assert False, f"This should return a Result, instead was {output}"

def test_TrivialCircuitFatory_ReturnsTheIndividualAsACircuit():
    individual = TrivialCircuit(34)
    circuit = TrivialCircuitFactory(individual)
    assert individual is circuit, "Should return the exact same object"






## ----------------------------------------- Other People's Tests ----------------------------------------------------