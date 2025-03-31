from BitstreamEvolutionProtocols import Circuit, Individual, CircuitFactory, FPGA_Compilation_Data
from pathlib import Path
from result import Result, Ok, Err

"""
As discussed in the main meeting (3/28/2025), we are first putting together a trivial implementation of all of the components.

In this implementation:
    - Fitness is an integer
    - Individuals & Circuits only hold an integer
    - Circuits are also Individuals, but we still use the correct type hints as if they may not be
    - The circuit's fitness equals the integer it holds
    - The simulation is run for 500 generations.
    - The larger the circuit's integer fitness, the more fit
    - Selection is performed as desired (Just top half, somewhat random, etc.)
    - Mutations, occouring in reproduction, simply increment or decrement the Individual's Integer for their child.

This should be fairly simple.
While writing this code, please write tests in the test_TrivialImplementation.py file as you are writing your code.
Make sure all functions that are tests begin with "test_" to make sure pytest can find them.
Run tests with "pytest" on the command line.
See "test_BitstreamEvolutionProtocols.py" for examples with writing tests.
"""

## ---------------------------- Circuit & Individual & CircuitFactory Code (Isaac) ---------------------------------

class TrivialCircuit:
    "This is a very simple circuit that is also the Individual evolution is performed on"
    def __init__(self,inherent_fitness:int):
        self.inherent_fitness = inherent_fitness

    def compile(self, fpga: FPGA_Compilation_Data, working_dir:Path) -> Result[Path,Exception]:
        return Ok("no/compilation/used/../../..")


def TrivialCircuitFactory(individual:Individual)->Circuit:
    return individual #they are the same thing for this implementation


## --------------------------------------------- Other People's Code --------------------------------------------------