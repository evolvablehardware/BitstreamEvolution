
from BitstreamEvolutionProtocols import CircuitFactory, EvaluatePopulationFitness, GenDataFactory, GenerateMeasurements, Hardware, Population, Reproducer
from PlotDataRecorder import PlotDataRecorder
from Population.PopulationInitialization import GenerateInitialPopulations

import asyncio

class Evolution:
    """
    NOT CURRENT VERSION, SHOULD BE REVISED USING TRIVIAL_EVOLUTION
    This class utilizes the protocols defined to run experiments
    There is only one implementation of Evolution needed
    If there are any desired features that are not supported in this version of the class
    then this class should be modified to support them *and* preserve existing behavior
    """

    def __init__(self, gen_data_factory: GenDataFactory, circuit_factory: CircuitFactory, reproduce: Reproducer, 
                 gen_init_populations: GenerateInitialPopulations, eval_population_fitness: EvaluatePopulationFitness,
                 generate_measurements: GenerateMeasurements, hardware: Hardware, plot_data_recorder: PlotDataRecorder):
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
        self.__plot_data_recorder = plot_data_recorder

    def run(self):
        '''
        Runs the desired experiment, based on the protocols provided
        '''
        populations: list[Population] = self.__gen_init_populations()
        gen_data = self.__gen_data_factory(None)
        while gen_data is not None:
            measurements = self.__generate_measurements(self.__circuit_factory, populations)
            tasks = [self.__hardware.request_measurement(m) for m in measurements]
            results = asyncio.run( asyncio.gather(*tasks) ) # I added asyncio.run to make sure that the async experiements were run at this point
            # Maybe figure out task groups. See https://docs.python.org/3/library/asyncio-task.html#coroutines-and-tasks

            for p in populations:
                self.__eval_population_fitness(p, results)
            populations = list(map(lambda p: self.__reproduce(p), populations))

            fits: list[float] = []
            for p in populations:
                for (i, f) in p:
                    fits.append(f) # type: ignore
            # TODO: calculate diversity
            self.__plot_data_recorder.record_generation(fits, gen_data.generation_number, 0)

            gen_data = self.__gen_data_factory(gen_data)
