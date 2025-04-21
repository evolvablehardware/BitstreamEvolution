import random
from BitstreamEvolutionProtocols import Circuit, Individual,FPGA_Compilation_Data, Population, CircuitFactory, Measurement, EvaluatePopulationFitness, GenData, GenDataFactory, GenerateInitialPopulation, GenerateMeasurements, Hardware, Reproducer
from pathlib import Path
from result import Result, Ok, Err # type: ignore
import functools as ft

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


## --------------------------------------------- Generate & Reproduce Populations --------------------------------------------------
def TrivialReproduceWithMutation (population: Population[TrivialCircuit],random: random.Random) -> Population[TrivialCircuit]:
    """
    Returns a population where all of the top half of the circuits are included, unchanged, 
        and each will get a child that is mutated randomly, being incremented or decremented.
    This primarily ensures the population remains the same size.
    If an odd length population is passed on, the next individual is kept, but does not reproduce or mutate.
    The outputed population has all of its fitnesses unevaluated (None).
    """
    population.sort(lambda x: x, True)
    individuals = list(iter(population))

    population_size = len(individuals)
    #keep_extra = population_size % 2 != 0

    kept_individuals = individuals[0:((population_size+1) // 2)]
    new_pop = [i[0] for i in kept_individuals] #get only the trivial circuits
    for (individual, fitness) in kept_individuals[0:(population_size//2)]: 
        # mutate & add child
        if random.random() < 0.5:
            new_pop.append(TrivialCircuit(fitness + 1))
        else:
            new_pop.append(TrivialCircuit(fitness - 1)) 
    return Population(new_pop, None)


def TrivialGenerateInitialPopulation(population_size:int, 
                                     random: random.Random, min_fitness:int, max_fitness:int) -> Population[TrivialCircuit]:
    """
    Generates a a list of two populations which have fitnesses numbered from
    zero and population_size sorted in descending order

    Here min & max fitness refers to the minimum and maximum inherent fitnesses that can be generated for an individual. 
    """

    new_pop = []
    for _ in range(population_size):
        new_pop.append(TrivialCircuit(random.randint(min_fitness,max_fitness)))

    #create new population with fitnesses unspecified b/c "unknown"
    return Population(new_pop, None)


## ------------------------------------ Generate Measurements --------------------------------------------



## ------------------------------------ Trivial Evolution Object -----------------------------------------

def FakeMeasuringFitnessTrivialImplemention(unevaluated_population: Population[TrivialCircuit])->Population[TrivialCircuit]:
    """This is a function that prevents me from having to use async & hardware while testing out TrivialEvolution. 
    This returns the same population, it just evaluates it."""
    
    for individual, fitness in unevaluated_population:
        unevaluated_population.set_fitness(individual,individual.inherent_fitness)

    return unevaluated_population


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
                 #circuit_factory:CircuitFactory,
                 reproducer:Reproducer,
                 generate_intial_population: GenerateInitialPopulation,
                 #evaluate_population_fitness: EvaluatePopulationFitness,
                 #generate_measurements: GenerateMeasurements,
                 #hardware:Hardware
                 ):
        """
        Initializes the Evolution with all of the objects and functions needed for it
        to carry out it the evolution.
        This does not execute any functions passed in.
        """
        self._generation_data_factory:GenDataFactory                 = generation_data_factory
        #self._circuit_factory:CircuitFactory                         = circuit_factory
        self._reproduce:Reproducer                                   = reproducer
        self._generate_intial_population:GenerateInitialPopulation   = generate_intial_population
        #self._evaluate_population_fitness:EvaluatePopulationFitness  = evaluate_population_fitness
        #self._generate_measurements:GenerateMeasurements             = generate_measurements
        #self._hardware:Hardware                                      = hardware

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
            
            # measurements:list[Measurement] = self._generate_measurements(self._circuit_factory,[current_population])
            # tasks = [self.__hardware.request_measurement(m) for m in measurements]
            # self._hardware.request_measurement(measurement for measurement in measurements)
            # results = asyncio.run( asyncio.gather(*tasks) ) # I added asyncio.run to make sure that the async experiements were run at this point
            #     # Maybe figure out task groups. See https://docs.python.org/3/library/asyncio-task.html#coroutines-and-tasks
            #
            # prev_population = self._evaluate_population_fitness(current_population,measurements)

            #NOTE: If we want to add multiple populations, create different evolution object, 
            #       and specify how you create initial populations for each set of individuals, 
            #       then specify in circuit_factory how to turn one individual from each population into a circuit,
            #       then, generate measurements decides which circuits it wants to make from those individuals 
            #       and it should be provided with a list that is the same number of populations as the number of arguments in circuit_factory.

            

            #move current_population to prev. & reproduce to current_pop
            prev_population = FakeMeasuringFitnessTrivialImplemention(current_population)
            current_population = self._reproduce(prev_population)
        
        print("Trivial Evolution Complete!")



