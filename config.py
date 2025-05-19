# Bitstream Evolution Config File
# This is where you setup an experiment to run.

# Set BitstreamEvolution (a.k.a. The folder this config is in) as the current working directory
import os
from pathlib import Path
from random import Random

from Directories import Directories
from EvaluateFitness.EvaluateFitness import EvaluateFitness
from Evolution import Evolution
from GenerateMeasurements.GenerateMeasurements import SimpleGenerateMeasurements
from Hardware.Microcontroller import Microcontroller, MicrocontrollerConfig
from Logger import Logger, LoggerConfig
from Population.PopulationInitialization import FileBasedCircuitFactory, GenerateBitstreamPopulation, GenerateSinglePopulationWrapper, NoPostConstructionStrategy, NoRandomizationStrategy
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from BitstreamEvolutionProtocols import DataRequest, GenDataIncrementer
from EvaluateFitness.EvalVarMaxFitness import EvalVarMaxFitness

logger_config = LoggerConfig(
    plots_dir=Path('workspace', 'plots'),
    launch_plots=True,
    is_sensitivity=False,
    frame_interval=100,
    log_file=Path('workspace', 'log'),
    log_level=0,
    save_log=False,
    datetime_format='%%m/%%d/%%Y - %%H:%%M:%%S'
)

mcu_config = MicrocontrollerConfig(
    usb_path='/dev/ttyUSB0',
    serial_baud=115200,
    read_timeout=1.1
)

directories = Directories(
    asc_dir=Path('workspace', 'experiment_asc'), 
    bin_dir=Path('workspace', 'experiment_bin'), 
    data_dir=Path('workspace', 'experiment_data')
)

sz = 50
fpga = 'i:0x0403:0x6010:0'

rand = Random()

logger = Logger("<empty explanation>", logger_config)
evaluation = EvalVarMaxFitness()
evolution = Evolution(
    gen_data_factory=GenDataIncrementer(200),
    circuit_factory=FileBasedCircuitFactory(
        sz=sz,
        logger=logger,
        directories=directories,
        routing_type='MOORE',
        accessed_columns=[14, 15, 24, 25, 40, 41]
    ).create,
    reproduce=None,
    gen_init_populations=GenerateSinglePopulationWrapper(GenerateBitstreamPopulation(
        sz=sz,
        bitstream_sz=1728,
        post_construction_strategy=NoPostConstructionStrategy(),
        randomization_strategy=NoRandomizationStrategy(),
        mutation_prob=0.0021,
        rand=rand
    ).generate
    ).generate,
    eval_population_fitness=EvaluateFitness(evaluation.calculate_success, evaluation.calculate_err).evaluate,
    generate_measurements=SimpleGenerateMeasurements(fpga, DataRequest.WAVEFORM).generate,
    hardware=Microcontroller(
        fpga=fpga,
        logger=logger,
        config=mcu_config
    )
)

