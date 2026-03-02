"""Main evolution loop orchestrator.

Wires together the protocol implementations (population generation,
circuit factory, fitness evaluation, reproduction) and runs the
generational evolution loop with async hardware measurements.

.. warning::
    This module is marked as NOT CURRENT VERSION. See
    :class:`~TrivialImplementation.TrivialEvolution` for the reference
    implementation currently used for testing.
"""

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
            # asyncio.gather dispatches all measurement requests concurrently. In the intended
            # server-client model, each await genuinely suspends while waiting for a network
            # response, so multiple FPGAs are measured in parallel here.
            # NOTE: asyncio.run() creates a new event loop each generation and destroys it
            # after. A cleaner approach is to make run() itself async (i.e. `async def run`)
            # and use `await asyncio.gather(*tasks)` directly, keeping one event loop for the
            # whole experiment. See .claude/docs/hardware_concurrency.md for discussion.
            results = asyncio.run( asyncio.gather(*tasks) )

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
