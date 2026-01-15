#! /bin/python
"""
test_evolve.py
--------------

End-to-end tests for the evolution system using FULLY_SIM mode.
These tests verify that the evolution pipeline runs correctly without hardware.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from Config import Config
from ConfigBuilder import ConfigBuilder
from Evolution import Evolution


# Path to test resources
TEST_RES_DIR = Path("test/res/inputs")
TEST_OUT_DIR = Path("test/out")


@pytest.fixture
def temp_workspace():
    """
    Create a temporary workspace directory for test isolation.
    Cleans up after the test completes.
    """
    temp_dir = tempfile.mkdtemp(prefix="bitstreamevo_test_")
    workspace_dir = Path(temp_dir) / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def fully_sim_config_content():
    """
    Returns config content for a minimal FULLY_SIM evolution run.
    Uses small population and few generations for fast tests.

    Note: This config is self-contained (no base_config) to allow tests
    to run from any directory without path issues.
    """
    return """[TOP-LEVEL PARAMETERS]
simulation_mode = FULLY_SIM
; No base_config - this config is self-contained for testing

[FITNESS PARAMETERS]
fitness_func = VARIANCE
desired_freq = 50000
combined_mode = MULT
pulse_weight = 2
var_weight = 0
num_samples = 1
num_passes = 1

[GA PARAMETERS]
population_size = 5
mutation_probability = 0.05
crossover_probability = 0.7
elitism_fraction = 0.2
selection = FIT_PROP_SEL
diversity_measure = HAMMING_DIST
random_injection = 0.0

[INITIALIZATION PARAMETERS]
init_mode = RANDOM
randomize_until = NO
randomize_threshold = 0
randomize_mode = RANDOM

[STOPPING CONDITION PARAMETERS]
generations = 3
target_fitness = IGNORE

[PLOTTING PARAMETERS]
launch_plots = false
frame_interval = 10000

[LOGGING PARAMETERS]
log_level = 1
save_log = true
save_plots = false
backup_workspace = false
log_file = ./workspace/log
plots_dir = ./workspace/plots
output_dir = ./prev_workspaces
asc_dir = ./workspace/experiment_asc
bin_dir = ./workspace/experiment_bin
data_dir = ./workspace/experiment_data
analysis = ./workspace/analysis
best_file = ./workspace/best.asc
generations_dir = ./workspace/generations
src_populations_dir = ./workspace/source_populations
final_experiment_dir = ./experiments
show_ovr_best = false
datetime_format = %%m/%%d/%%Y - %%H:%%M:%%S
population_bitstream_save_interval = 10

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
"""


@pytest.fixture
def create_test_config(temp_workspace, fully_sim_config_content):
    """
    Factory fixture to create test config files in the temp workspace.

    :returns: Function that creates a config file and returns its path
    """
    def _create_config(config_content=None, filename="test_config.ini"):
        if config_content is None:
            config_content = fully_sim_config_content
        config_path = Path(temp_workspace) / filename
        with open(config_path, "w") as f:
            f.write(config_content)
        return str(config_path)
    return _create_config


class TestEvolutionFullySim:
    """Tests for evolution in FULLY_SIM mode."""

    @pytest.mark.short
    def test_evolution_completes_without_error(self, temp_workspace, create_test_config):
        """
        Test that evolution completes the specified number of generations
        without raising exceptions in FULLY_SIM mode.
        """
        config_path = create_test_config()
        built_config_path = str(Path(temp_workspace) / "workspace" / "builtconfig.ini")

        evolution = Evolution()

        # Mock the plot subprocess call since we don't need visualization in tests
        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Should complete without raising
            evolution.evolve(
                primary_config_path=config_path,
                experiment_description="Test evolution run",
                base_config_path=None,
                built_config_path=built_config_path,
                output_directory=None,
                print_action_only=False,
            )

        # Verify evolution object has expected attributes after completion
        assert hasattr(evolution, "population")
        assert hasattr(evolution, "config")
        assert hasattr(evolution, "logger")

    @pytest.mark.short
    def test_evolution_creates_workspace_files(self, temp_workspace, create_test_config):
        """
        Test that evolution creates expected files in the workspace.
        """
        config_path = create_test_config()
        workspace_path = Path(temp_workspace) / "workspace"
        built_config_path = str(workspace_path / "builtconfig.ini")

        evolution = Evolution()

        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Change to temp directory so workspace is created there
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_workspace)
                evolution.evolve(
                    primary_config_path=config_path,
                    experiment_description="Test workspace files",
                    base_config_path=None,
                    built_config_path=built_config_path,
                    output_directory=None,
                    print_action_only=False,
                )
            finally:
                os.chdir(original_cwd)

        # Verify built config was created
        assert Path(built_config_path).exists(), "Built config file should be created"

    @pytest.mark.immediate
    def test_evolution_print_only_mode(self, temp_workspace, create_test_config):
        """
        Test that print_only mode does not execute evolution.
        """
        config_path = create_test_config()
        built_config_path = str(Path(temp_workspace) / "workspace" / "builtconfig.ini")

        evolution = Evolution()

        # print_action_only should return early without creating population
        evolution.evolve(
            primary_config_path=config_path,
            experiment_description="Test print only",
            base_config_path=None,
            built_config_path=built_config_path,
            output_directory=None,
            print_action_only=True,
        )

        # In print_only mode, population should NOT be created
        assert not hasattr(evolution, "population")


class TestConfigLoading:
    """Tests for configuration loading and validation."""

    @pytest.mark.immediate
    def test_config_loads_simulation_mode(self, temp_workspace, create_test_config):
        """Test that Config correctly loads simulation_mode."""
        config_path = create_test_config()
        built_config_path = str(Path(temp_workspace) / "builtconfig.ini")

        # Build the config first
        config_builder = ConfigBuilder(config_path)
        config_builder.build_config(built_config_path)

        # Load and verify
        config = Config(built_config_path)
        assert config.get_simulation_mode() == "FULLY_SIM"

    @pytest.mark.immediate
    def test_config_loads_population_size(self, temp_workspace, create_test_config):
        """Test that Config correctly loads population_size as int."""
        config_path = create_test_config()
        built_config_path = str(Path(temp_workspace) / "builtconfig.ini")

        config_builder = ConfigBuilder(config_path)
        config_builder.build_config(built_config_path)

        config = Config(built_config_path)
        pop_size = config.get_population_size()

        assert isinstance(pop_size, int)
        assert pop_size == 5

    @pytest.mark.immediate
    def test_config_loads_generations(self, temp_workspace, create_test_config):
        """Test that Config correctly loads number of generations."""
        config_path = create_test_config()
        built_config_path = str(Path(temp_workspace) / "builtconfig.ini")

        config_builder = ConfigBuilder(config_path)
        config_builder.build_config(built_config_path)

        config = Config(built_config_path)
        generations = config.get_n_generations()

        assert generations == 3


class TestEvolutionWithDifferentSelections:
    """Tests for different selection algorithms."""

    @pytest.fixture
    def config_with_selection(self, temp_workspace, fully_sim_config_content):
        """
        Factory fixture to create config with a specific selection method.
        """
        def _create_config(selection_method):
            content = fully_sim_config_content.replace(
                "selection = FIT_PROP_SEL",
                f"selection = {selection_method}"
            )
            config_path = Path(temp_workspace) / f"config_{selection_method}.ini"
            with open(config_path, "w") as f:
                f.write(content)
            return str(config_path)
        return _create_config

    @pytest.mark.short
    @pytest.mark.parametrize("selection_method", [
        "FIT_PROP_SEL",
        "RANK_PROP_SEL",
        pytest.param(
            "CLASSIC_TOURN",
            marks=pytest.mark.xfail(
                reason="Bug: CLASSIC_TOURN accesses .get_fitness() on None with small populations"
            )
        ),
        "SINGLE_ELITE",
        "FRAC_ELITE",
    ])
    def test_selection_methods_complete(
        self, temp_workspace, config_with_selection, selection_method
    ):
        """
        Test that evolution completes with different selection methods.

        :param selection_method: The selection algorithm to test
        """
        config_path = config_with_selection(selection_method)
        built_config_path = str(Path(temp_workspace) / "workspace" / "builtconfig.ini")

        evolution = Evolution()

        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_workspace)
                evolution.evolve(
                    primary_config_path=config_path,
                    experiment_description=f"Test {selection_method}",
                    base_config_path=None,
                    built_config_path=built_config_path,
                    output_directory=None,
                    print_action_only=False,
                )
            finally:
                os.chdir(original_cwd)

        assert hasattr(evolution, "population")


class TestEvolutionWithDifferentFitnessFunctions:
    """Tests for different fitness functions in FULLY_SIM mode."""

    @pytest.fixture
    def config_with_fitness(self, temp_workspace, fully_sim_config_content):
        """
        Factory fixture to create config with a specific fitness function.
        """
        def _create_config(fitness_func):
            content = fully_sim_config_content.replace(
                "fitness_func = VARIANCE",
                f"fitness_func = {fitness_func}"
            )
            config_path = Path(temp_workspace) / f"config_{fitness_func}.ini"
            with open(config_path, "w") as f:
                f.write(content)
            return str(config_path)
        return _create_config

    @pytest.mark.short
    @pytest.mark.parametrize("fitness_func", [
        "VARIANCE",
        # Note: Pulse-based functions may not work in FULLY_SIM mode
        # Add more as appropriate for simulation
    ])
    def test_fitness_functions_complete(
        self, temp_workspace, config_with_fitness, fitness_func
    ):
        """
        Test that evolution completes with different fitness functions.

        :param fitness_func: The fitness function to test
        """
        config_path = config_with_fitness(fitness_func)
        built_config_path = str(Path(temp_workspace) / "workspace" / "builtconfig.ini")

        evolution = Evolution()

        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_workspace)
                evolution.evolve(
                    primary_config_path=config_path,
                    experiment_description=f"Test {fitness_func}",
                    base_config_path=None,
                    built_config_path=built_config_path,
                    output_directory=None,
                    print_action_only=False,
                )
            finally:
                os.chdir(original_cwd)

        assert hasattr(evolution, "population")
