import random
from BitstreamEvolutionProtocols import Circuit, Individual,FPGA_Compilation_Data, Population, CircuitFactory, Measurement, EvaluatePopulationFitness, GenData, GenDataFactory, GenerateInitialPopulation, GenerateMeasurements, Hardware, Reproducer
from pathlib import Path
from result import Result, Ok, Err # type: ignore

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


def TrivialCircuitFactory(individuals: list[Individual]) -> list[Circuit]:
    # they are the same thing for this implementation
    return individuals # type: ignore


## --------------------------------------------- Other People's Code --------------------------------------------------
class TrivialReproduce:
    def __init__(self, random: random.Random):
        self.random = random

    def __call__(self, population: Population[TrivialCircuit]) -> Population[TrivialCircuit]:
        population.sort(lambda x: x, True)
        individuals = list(iter(population))
        kept_individuals = individuals[0:(len(individuals) // 2)]
        new_pop = []
        new_fits = []
        for (p, f) in kept_individuals:
            # keep one
            new_pop.append(TrivialCircuit(f)) # type: ignore
            new_fits.append(f)
            # mutate
            if self.random.random() < 0.5:
                new_pop.append(TrivialCircuit(f + 1)) # type: ignore
                new_fits.append(f + 1) # type: ignore
            else:
                new_pop.append(TrivialCircuit(f - 1)) # type: ignore
                new_fits.append(f - 1) # type: ignore
        return Population(new_pop, new_fits)



class TrivialGenerateInitialPopulation:
    "Generates a a list of two populations which have fitnesses numbered from"
    "zero and population_size sorted in descending order"
    def __init__(self, random: random.Random):
        self.random = random

    def __call__(self, population_size:int) -> list [Population[TrivialCircuit]]:
        num_populations = 2;

        population_list = []
        for(i) in range(num_populations):
            new_pop = []
            new_fitnesses = []
            for (j) in range(population_size):
                new_pop.append(TrivialCircuit(j))
                new_fitnesses.append(j)
            new_pop.sort(reverse=True);
            population_list.append(Population(new_pop, new_fitnesses))
        return population_list


## ------------------------------------ Trivial Evolution Object -----------------------------------------

def fake_evaluate_measurements_trivialimplemention(measurements: list[Measurement])->list[Measurement]:
    "This is a function that prevents me from having to use async & hardware while testing out TrivialEvolution."
    return measurements


class TrivialEvolution:
    """
    This class utilizes the protocols defined to run experiments
    This is an example that should be generalized for a more general solution.
    There should be different versions of Evolution for structurally different experiments.
        (e.x. Multiple populations of individuals evolved simultaniously, bacterial populations where only some individuals are evaluated and reproduce each loop)
    Any other evolution implementations should try to maintain as similar of function signatures as possible, 
        with arguments communicated with protocols that are as general as possible. 
    This implementations generates, evaluates, and reproduces entire populations at once,
        and does so in discrete timesteps.
    """

    def __init__(self, 
                 generation_data_factory:GenDataFactory,
                 circuit_factory:CircuitFactory,
                 reproducer:Reproducer,
                 generate_intial_population: GenerateInitialPopulation,
                 evaluate_population_fitness: EvaluatePopulationFitness,
                 generate_measurements: GenerateMeasurements,
                 hardware:Hardware):
        """
        Initializes the Evolution with all of the objects and functions needed for it
        to carry out it the evolution.
        This does not execute any functions passed in.
        """
        self._generation_data_factory:GenDataFactory                 = generation_data_factory
        self._circuit_factory:CircuitFactory                         = circuit_factory
        self._reproduce:Reproducer                                   = reproducer
        self._generate_intial_population:GenerateInitialPopulation   = generate_intial_population
        self._evaluate_population_fitness:EvaluatePopulationFitness  = evaluate_population_fitness
        self._generate_measurements:GenerateMeasurements             = generate_measurements
        self._hardware:Hardware                                      = hardware

    def run(self):
        """
        This Function Runs the evolution run specified by the protocols provided, using them
        according to how the architecture of this evolution object is configured.

        This implementations generates, evaluates, and reproduces entire populations at once,
            and does so in discrete timesteps.
        """
        prev_population:Population|None = None
        current_population:Population = self._generate_intial_population()
        current_gendata:GenData|None = None

        while (current_gendata:=
               self._generation_data_factory(gen_data=current_gendata)
               ) is not None:
            
            measurements:list[Measurement] = self._generate_measurements(self._circuit_factory,[current_population])
            #NOTE: If we want to add multiple populations, create different evolution object, 
            #       and specify how you create initial populations for each set of individuals, 
            #       then specify in circuit_factory how to turn one individual from each population into a circuit,
            #       then, generate measurements decides which circuits it wants to make from those individuals 
            #       and it should be provided with a list that is the same number of populations as the number of arguments in circuit_factory.

            measurements = fake_evaluate_measurements_trivialimplemention(measurements)

            #move current_population to prev. & reproduce to current_pop
            prev_population = self._evaluate_population_fitness(current_population,measurements)
            current_population = self._reproduce(prev_population)
        
        print("Trivial Evolution Complete!")



