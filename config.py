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
from PlotConfig import save_plot_config
from PlotDataRecorder import PlotDataRecorder
from Population.PopulationInitialization import FileBasedCircuitFactory, GenerateBitstreamPopulation, GenerateSinglePopulationWrapper, NoPostConstructionStrategy, NoRandomizationStrategy
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from BitstreamEvolutionProtocols import DataRequest, GenDataIncrementer
from EvaluateFitness.EvalVarMaxFitness import EvalVarMaxFitness

explanation = '<empty explanation>'

run_fitness_sensitivity_exp = False
population_size = 50
num_generations = 200
bitstream_length = 1728
fpga = 'i:0x0403:0x6010:0'
post_construction_strategy = NoPostConstructionStrategy()
randomization_strategy = NoRandomizationStrategy()
mutation_prob = 0.0021
crossover_prob = 0.7
uses_init_existing_population = False
num_samples = 1

plot_data_recorder = PlotDataRecorder()

desired_frequency = 0
data_request = DataRequest.WAVEFORM
evaluation = EvalVarMaxFitness(plot_data_recorder)

log_file = Path('workspace', 'log')
log_level = 0
save_log = False

plots_dir = Path('workspace', 'plots')
launch_plots = True
save_plots = True
frame_interval = 100

usb_path = '/dev/ttyUSB0'
serial_baud = 115200
read_timeout = 1.1
routing_type = 'MOORE'
accessed_columns = [14, 15, 24, 25, 40, 41]

asc_dir=Path('workspace', 'experiment_asc')
bin_dir=Path('workspace', 'experiment_bin')
data_dir=Path('workspace', 'experiment_data')

is_pulse_count = False
is_tone_discriminator = False

transfer_interval = 0
diversity_measure = 'HAMMING_DIST'

########################################################

save_plot_config(Path('workspace', 'plot_config.ini'), 
                 pop_sz=population_size,
                 is_pulse_count=is_pulse_count,
                 is_td=is_tone_discriminator,
                 desired_freq=desired_frequency,
                 transfer_interval=transfer_interval,
                 diversity_measure=diversity_measure,
                 save_plots=save_plots,
                 plots_dir=str(plots_dir),
                 uses_init_existing_population=uses_init_existing_population)

logger_config = LoggerConfig(
    plots_dir=plots_dir,
    launch_plots=launch_plots,
    is_sensitivity=run_fitness_sensitivity_exp,
    frame_interval=frame_interval,
    log_file=log_file,
    log_level=log_level,
    save_log=save_log,
    datetime_format='%%m/%%d/%%Y - %%H:%%M:%%S'
)

mcu_config = MicrocontrollerConfig(
    usb_path=usb_path,
    serial_baud=serial_baud,
    read_timeout=read_timeout
)

directories = Directories(
    asc_dir,
    bin_dir,
    data_dir
)

rand = Random()

logger = Logger(explanation, logger_config)
evolution = Evolution(
    gen_data_factory=GenDataIncrementer(num_generations),
    circuit_factory=FileBasedCircuitFactory(
        sz=population_size,
        logger=logger,
        directories=directories,
        routing_type=routing_type,
        accessed_columns=accessed_columns
    ).create,
    reproduce=None,
    gen_init_populations=GenerateSinglePopulationWrapper(GenerateBitstreamPopulation(
        sz=population_size,
        bitstream_sz=bitstream_length,
        post_construction_strategy=post_construction_strategy,
        randomization_strategy=randomization_strategy,
        mutation_prob=mutation_prob,
        rand=rand
    ).generate
    ).generate,
    eval_population_fitness=EvaluateFitness(evaluation).evaluate,
    generate_measurements=SimpleGenerateMeasurements(fpga, data_request, num_samples).generate,
    hardware=Microcontroller(
        fpga=fpga,
        logger=logger,
        config=mcu_config
    ),
    plot_data_recorder=plot_data_recorder
)

