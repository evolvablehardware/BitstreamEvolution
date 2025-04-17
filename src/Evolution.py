
from BitstreamEvolutionProtocols import CircuitFactory, EvaluatePopulationFitness, GenDataFactory, GenerateInitialPopulations, GenerateMeasurements, Hardware, Reproduce
import asyncio

class Evolution:
    """
    This class utilizes the protocols defined to run experiments
    There is only one implementation of Evolution needed
    If there are any desired features that are not supported in this version of the class
    then this class should be modified to support them *and* preserve existing behavior
    """

    def __init__(self, gen_data_factory: GenDataFactory, circuit_factory: CircuitFactory, reproduce: Reproduce, 
                 gen_init_populations: GenerateInitialPopulations, eval_population_fitness: EvaluatePopulationFitness,
                 generate_measurements: GenerateMeasurements, hardware: Hardware):
        '''
        Initializes the Evolution object with all of the protocols.
        Does not execute any protocols
        '''
        self.__gen_data_factory = gen_data_factory
        self.__circuit_factory = circuit_factory
        self.__reproduce = reproduce
        self.__gen_init_populations = gen_init_populations
        self.__eval_population_fitness = eval_population_fitness
        self.__generate_measurements = generate_measurements
        self.__hardware = hardware

    async def run(self):
        '''
        Runs the desired experiment, based on the protocols provided
        '''
        populations = self.__gen_init_populations()
        gen_data = self.__gen_data_factory(None)
        while gen_data is not None:
            measurements = self.__generate_measurements(self.__circuit_factory, populations)
            tasks = [self.__hardware.request_measurement(m) for m in measurements]
            results = await asyncio.gather(*tasks)
            populations = list(map(lambda p: self.__eval_population_fitness(p, results), populations))
            populations = list(map(lambda p: self.__reproduce(p), populations))                         # 
            # population = self.__eval_population_fitness(population, results)
            # population = self.__reproduce(population)                                                 # Create next population
            gen_data = self.__gen_data_factory(gen_data)                                                # Decide what to do for next Iteration  
