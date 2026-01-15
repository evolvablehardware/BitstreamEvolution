#! /bin/python
"""
test_config.py
--------------

Tests for the Config class which handles configuration file parsing and validation.
"""

import os
import tempfile
from pathlib import Path

import pytest

from Config import Config
from ConfigBuilder import ConfigBuilder


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for test config files."""
    temp_dir = tempfile.mkdtemp(prefix="config_test_")
    yield temp_dir
    # Cleanup handled by OS or manual if needed


@pytest.fixture
def valid_config_content():
    """
    Returns a valid, self-contained configuration for testing.
    All required parameters are included with valid values.
    """
    return """[TOP-LEVEL PARAMETERS]
simulation_mode = FULLY_SIM

[FITNESS PARAMETERS]
fitness_func = VARIANCE
desired_freq = 10000
combined_mode = MULT
pulse_weight = 2.0
var_weight = 1.0
num_samples = 1
num_passes = 1

[GA PARAMETERS]
population_size = 50
mutation_probability = 0.0021
crossover_probability = 0.7
elitism_fraction = 0.1
selection = FIT_PROP_SEL
diversity_measure = HAMMING_DIST
random_injection = 0.0

[INITIALIZATION PARAMETERS]
init_mode = RANDOM
randomize_until = NO
randomize_threshold = 4
randomize_mode = RANDOM

[STOPPING CONDITION PARAMETERS]
generations = 100
target_fitness = IGNORE

[PLOTTING PARAMETERS]
launch_plots = false
frame_interval = 10000

[LOGGING PARAMETERS]
log_level = 4
save_log = true
save_plots = true
backup_workspace = true
population_bitstream_save_interval = 10
log_file = ./workspace/log
plots_dir = ./workspace/plots
output_dir = ./prev_workspaces
final_experiment_dir = ./experiments
asc_dir = ./workspace/experiment_asc
bin_dir = ./workspace/experiment_bin
data_dir = ./workspace/experiment_data
analysis = ./workspace/analysis
best_file = ./workspace/best.asc
generations_dir = ./workspace/generations
src_populations_dir = ./workspace/source_populations
datetime_format = %%m/%%d/%%Y - %%H:%%M:%%S
show_ovr_best = true

[SYSTEM PARAMETERS]
fpga = i:0x0403:0x6010:0
usb_path = /dev/ttyUSB0
auto_upload_to_arduino = false

[HARDWARE PARAMETERS]
routing = MOORE
mcu_read_timeout = 1.1
serial_baud = 115200
accessed_columns = 14,15,24,25,40,41
configurable_io = false
input_pins = 45,47,48
output_pins = 44

[FITNESS SENSITIVITY PARAMETERS]
test_circuit = data/test.asc
sensitivity_trials = IGNORE
sensitivity_time = 24:00:00

[TRANSFERABILITY PARAMETERS]
transfer_interval = IGNORE
fpga2 = i:0x0403:0x6010:0
"""


@pytest.fixture
def create_config(temp_config_dir, valid_config_content):
    """
    Factory fixture to create a Config object from content.

    :returns: Function that creates a built config and returns Config object
    """
    def _create_config(content=None):
        if content is None:
            content = valid_config_content

        input_path = Path(temp_config_dir) / "input_config.ini"
        output_path = Path(temp_config_dir) / "built_config.ini"

        with open(input_path, "w") as f:
            f.write(content)

        # Build the config (resolves inheritance)
        builder = ConfigBuilder(str(input_path))
        builder.build_config(str(output_path))

        return Config(str(output_path))

    return _create_config


class TestSimulationModeConfig:
    """Tests for simulation mode configuration."""

    @pytest.mark.immediate
    @pytest.mark.parametrize("mode", [
        "FULLY_SIM",
        "SIM_HARDWARE",
        "FULLY_INTRINSIC",
        "INTRINSIC_SENSITIVITY",
    ])
    def test_valid_simulation_modes(self, create_config, valid_config_content, mode):
        """Test that all valid simulation modes are accepted."""
        content = valid_config_content.replace(
            "simulation_mode = FULLY_SIM",
            f"simulation_mode = {mode}"
        )
        config = create_config(content)
        assert config.get_simulation_mode() == mode


class TestFitnessParameterConfig:
    """Tests for fitness parameter configuration."""

    @pytest.mark.immediate
    @pytest.mark.parametrize("func", [
        "VARIANCE",
        "PULSE_COUNT",
        "TOLERANT_PULSE_COUNT",
        "SENSITIVE_PULSE_COUNT",
        "COMBINED",
        "TONE_DISCRIMINATOR",
    ])
    def test_valid_fitness_functions(self, create_config, valid_config_content, func):
        """Test that all valid fitness functions are accepted."""
        content = valid_config_content.replace(
            "fitness_func = VARIANCE",
            f"fitness_func = {func}"
        )
        config = create_config(content)
        assert config.get_fitness_func() == func

    @pytest.mark.immediate
    def test_desired_frequency_returns_int(self, create_config):
        """Test that desired frequency is returned as an integer."""
        config = create_config()
        freq = config.get_desired_frequency()
        assert isinstance(freq, int)
        assert freq == 10000

    @pytest.mark.immediate
    @pytest.mark.parametrize("mode", ["ADD", "MULT"])
    def test_valid_combined_modes(self, create_config, valid_config_content, mode):
        """Test that valid combined modes are accepted."""
        content = valid_config_content.replace(
            "combined_mode = MULT",
            f"combined_mode = {mode}"
        )
        config = create_config(content)
        assert config.get_combined_mode() == mode

    @pytest.mark.immediate
    def test_pulse_weight_returns_float(self, create_config):
        """Test that pulse weight is returned as a float."""
        config = create_config()
        weight = config.get_pulse_weight()
        assert isinstance(weight, float)
        assert weight == 2.0

    @pytest.mark.immediate
    def test_var_weight_returns_float(self, create_config):
        """Test that var weight is returned as a float."""
        config = create_config()
        weight = config.get_var_weight()
        assert isinstance(weight, float)
        assert weight == 1.0

    @pytest.mark.immediate
    def test_num_samples_returns_int(self, create_config):
        """Test that num_samples is returned as an integer."""
        config = create_config()
        samples = config.get_num_samples()
        assert isinstance(samples, int)
        assert samples == 1

    @pytest.mark.immediate
    def test_num_passes_returns_int(self, create_config):
        """Test that num_passes is returned as an integer."""
        config = create_config()
        passes = config.get_num_passes()
        assert isinstance(passes, int)
        assert passes == 1


class TestGAParameterConfig:
    """Tests for genetic algorithm parameter configuration."""

    @pytest.mark.immediate
    def test_population_size_returns_int(self, create_config):
        """Test that population size is returned as an integer."""
        config = create_config()
        pop_size = config.get_population_size()
        assert isinstance(pop_size, int)
        assert pop_size == 50

    @pytest.mark.immediate
    def test_mutation_probability_returns_float(self, create_config):
        """Test that mutation probability is returned as a float."""
        config = create_config()
        mut_prob = config.get_mutation_probability()
        assert isinstance(mut_prob, float)
        assert mut_prob == 0.0021

    @pytest.mark.immediate
    def test_crossover_probability_returns_float(self, create_config):
        """Test that crossover probability is returned as a float."""
        config = create_config()
        cross_prob = config.get_crossover_probability()
        assert isinstance(cross_prob, float)
        assert cross_prob == 0.7

    @pytest.mark.immediate
    def test_elitism_fraction_returns_float(self, create_config):
        """Test that elitism fraction is returned as a float."""
        config = create_config()
        elitism = config.get_elitism_fraction()
        assert isinstance(elitism, float)
        assert elitism == 0.1

    @pytest.mark.immediate
    @pytest.mark.parametrize("selection", [
        "SINGLE_ELITE",
        "FRAC_ELITE",
        "CLASSIC_TOURN",
        "FIT_PROP_SEL",
        "RANK_PROP_SEL",
        "MAP_ELITES",
    ])
    def test_valid_selection_types(self, create_config, valid_config_content, selection):
        """Test that all valid selection types are accepted."""
        content = valid_config_content.replace(
            "selection = FIT_PROP_SEL",
            f"selection = {selection}"
        )
        config = create_config(content)
        assert config.get_selection_type() == selection

    @pytest.mark.immediate
    def test_random_injection_returns_float(self, create_config):
        """Test that random injection is returned as a float."""
        config = create_config()
        injection = config.get_random_injection()
        assert isinstance(injection, float)
        assert injection == 0.0

    @pytest.mark.immediate
    @pytest.mark.parametrize("measure", ["HAMMING_DIST", "UNIQUE"])
    def test_valid_diversity_measures(self, create_config, valid_config_content, measure):
        """Test that valid diversity measures are accepted."""
        content = valid_config_content.replace(
            "diversity_measure = HAMMING_DIST",
            f"diversity_measure = {measure}"
        )
        config = create_config(content)
        assert config.get_diversity_measure() == measure


class TestInitializationConfig:
    """Tests for initialization parameter configuration."""

    @pytest.mark.immediate
    @pytest.mark.parametrize("init_mode", [
        "CLONE_SEED",
        "CLONE_SEED_MUTATE",
        "RANDOM",
        "EXISTING_POPULATION",
    ])
    def test_valid_init_modes(self, create_config, valid_config_content, init_mode):
        """Test that all valid initialization modes are accepted."""
        content = valid_config_content.replace(
            "init_mode = RANDOM",
            f"init_mode = {init_mode}"
        )
        config = create_config(content)
        assert config.get_init_mode() == init_mode

    @pytest.mark.immediate
    @pytest.mark.parametrize("rand_until", ["PULSE", "VARIANCE", "NO"])
    def test_valid_randomize_until(self, create_config, valid_config_content, rand_until):
        """Test that valid randomize_until values are accepted."""
        content = valid_config_content.replace(
            "randomize_until = NO",
            f"randomize_until = {rand_until}"
        )
        config = create_config(content)
        assert config.get_randomization_type() == rand_until


class TestStoppingConditionConfig:
    """Tests for stopping condition configuration."""

    @pytest.mark.immediate
    def test_generations_returns_int(self, create_config):
        """Test that generations returns an integer."""
        config = create_config()
        gens = config.get_n_generations()
        assert isinstance(gens, int)
        assert gens == 100

    @pytest.mark.immediate
    @pytest.mark.xfail(
        reason="Bug: Config.__log_warning fails when logger not added via add_logger()"
    )
    def test_generations_ignore_returns_none(self, create_config, valid_config_content):
        """Test that IGNORE for generations returns None."""
        content = valid_config_content.replace(
            "generations = 100",
            "generations = IGNORE"
        )
        config = create_config(content)
        assert config.get_n_generations() is None

    @pytest.mark.immediate
    @pytest.mark.xfail(
        reason="Bug: Config.__log_warning fails when logger not added via add_logger()"
    )
    def test_target_fitness_ignore_returns_none(self, create_config):
        """Test that IGNORE for target_fitness returns None."""
        config = create_config()
        assert config.get_target_fitness() is None

    @pytest.mark.immediate
    def test_target_fitness_returns_float(self, create_config, valid_config_content):
        """Test that target_fitness returns a float when set."""
        content = valid_config_content.replace(
            "target_fitness = IGNORE",
            "target_fitness = 0.95"
        )
        config = create_config(content)
        target = config.get_target_fitness()
        assert isinstance(target, float)
        assert target == 0.95


class TestLoggingConfig:
    """Tests for logging configuration."""

    @pytest.mark.immediate
    def test_log_level_returns_int(self, create_config):
        """Test that log level returns an integer."""
        config = create_config()
        level = config.get_log_level()
        assert isinstance(level, int)
        assert level == 4

    @pytest.mark.immediate
    def test_save_log_returns_bool(self, create_config):
        """Test that save_log returns a boolean."""
        config = create_config()
        save = config.get_save_log()
        assert isinstance(save, bool)
        assert save is True

    @pytest.mark.immediate
    def test_save_plots_returns_bool(self, create_config):
        """Test that save_plots returns a boolean."""
        config = create_config()
        save = config.get_save_plots()
        assert isinstance(save, bool)
        assert save is True

    @pytest.mark.immediate
    def test_backup_workspace_returns_bool(self, create_config):
        """Test that backup_workspace returns a boolean."""
        config = create_config()
        backup = config.get_backup_workspace()
        assert isinstance(backup, bool)
        assert backup is True

    @pytest.mark.immediate
    def test_directory_paths_return_path(self, create_config):
        """Test that directory getters return Path objects."""
        config = create_config()

        # Test various directory getters
        assert config.get_plots_directory() == Path("./workspace/plots")
        assert config.get_output_directory() == Path("./prev_workspaces")
        assert config.get_asc_directory() == Path("./workspace/experiment_asc")
        assert config.get_bin_directory() == Path("./workspace/experiment_bin")
        assert config.get_data_directory() == Path("./workspace/experiment_data")


class TestHardwareConfig:
    """Tests for hardware configuration."""

    @pytest.mark.immediate
    @pytest.mark.parametrize("routing", ["MOORE", "NEWSE"])
    def test_valid_routing_types(self, create_config, valid_config_content, routing):
        """Test that valid routing types are accepted."""
        content = valid_config_content.replace(
            "routing = MOORE",
            f"routing = {routing}"
        )
        config = create_config(content)
        assert config.get_routing_type() == routing

    @pytest.mark.immediate
    def test_serial_baud_returns_int(self, create_config):
        """Test that serial baud rate returns an integer."""
        config = create_config()
        baud = config.get_serial_baud()
        assert isinstance(baud, int)
        assert baud == 115200

    @pytest.mark.immediate
    def test_fpga_returns_string(self, create_config):
        """Test that FPGA identifier returns a string."""
        config = create_config()
        fpga = config.get_fpga()
        assert isinstance(fpga, str)
        assert fpga == "i:0x0403:0x6010:0"

    @pytest.mark.immediate
    def test_usb_path_returns_string(self, create_config):
        """Test that USB path returns a string."""
        config = create_config()
        usb = config.get_usb_path()
        assert isinstance(usb, str)
        assert usb == "/dev/ttyUSB0"

    @pytest.mark.immediate
    def test_upload_to_arduino_returns_bool(self, create_config):
        """Test that upload_to_arduino returns a boolean."""
        config = create_config()
        upload = config.get_upload_to_arduino()
        assert isinstance(upload, bool)
        assert upload is False

    @pytest.mark.immediate
    def test_mcu_read_timeout_returns_float(self, create_config):
        """Test that MCU read timeout returns a float."""
        config = create_config()
        timeout = config.get_mcu_read_timeout()
        assert isinstance(timeout, float)
        assert timeout == 1.1


class TestPlottingConfig:
    """Tests for plotting configuration."""

    @pytest.mark.immediate
    def test_launch_plots_returns_bool(self, create_config):
        """Test that launch_plots returns a boolean."""
        config = create_config()
        launch = config.get_launch_plots()
        assert isinstance(launch, bool)
        assert launch is False

    @pytest.mark.immediate
    def test_frame_interval_returns_int(self, create_config):
        """Test that frame_interval returns an integer."""
        config = create_config()
        interval = config.get_frame_interval()
        assert isinstance(interval, int)
        assert interval == 10000
