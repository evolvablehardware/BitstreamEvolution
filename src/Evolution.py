
from BitstreamEvolutionProtocols import CircuitFactory, EvaluatePopulationFitness, GenDataFactory, GenerateInitialPopulation, GenerateMeasurements, Hardware, Reproduce
import asyncio

class Evolution:
    """
    This class utilizes the protocols defined to run experiments
    There is only one implementation of Evolution needed
    If there are any desired features that are not supported in this version of the class
    then this class should be modified to support them *and* preserve existing behavior
    """

    def __init__(self, gen_data_factory: GenDataFactory, circuit_factory: CircuitFactory, reproduce: Reproduce, 
                 gen_init_population: GenerateInitialPopulation, eval_population_fitness: EvaluatePopulationFitness,
                 generate_measurements: GenerateMeasurements, hardware: Hardware):
        '''
        Initializes the Evolution object with all of the protocols.
        Does not execute any protocols
        '''
        self.__gen_data_factory = gen_data_factory
        self.__circuit_factory = circuit_factory
        self.__reproduce = reproduce
        self.__gen_init_population = gen_init_population
        self.__eval_population_fitness = eval_population_fitness
        self.__generate_measurements = generate_measurements
        self.__hardware = hardware

    async def run(self):
        '''
        Runs the desired experiment, based on the protocols provided
        '''
        population = self.__gen_init_population()
        gen_data = self.__gen_data_factory(None)
        while gen_data is not None:
            individuals = list(map(lambda x: x[0], iter(population)))
            circuits = self.__circuit_factory(individuals)
            measurements = self.__generate_measurements(circuits)
            tasks = [self.__hardware.request_measurement(m) for m in measurements]
            results = await asyncio.gather(*tasks)
            population = self.__eval_population_fitness(population, results)
            population = self.__reproduce(population)
            gen_data = self.__gen_data_factory(gen_data)
