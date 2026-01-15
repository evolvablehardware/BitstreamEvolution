#! /bin/python
"""
test_evolution.py
-----------------

Tests for the Evolution class which orchestrates the evolutionary process.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    temp_dir = tempfile.mkdtemp(prefix="evolution_test_")
    workspace = Path(temp_dir) / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    # Cleanup handled by OS


@pytest.fixture
def valid_config_content():
    """Returns a valid, self-contained configuration for testing."""
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
randomize_threshold = 4
randomize_mode = RANDOM

[STOPPING CONDITION PARAMETERS]
generations = 2
target_fitness = IGNORE

[PLOTTING PARAMETERS]
launch_plots = false
frame_interval = 10000

[LOGGING PARAMETERS]
log_level = 1
save_log = true
save_plots = false
backup_workspace = false
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
show_ovr_best = false

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
def create_config_file(temp_workspace, valid_config_content):
    """Factory to create config files."""
    def _create(content=None, filename="config.ini"):
        if content is None:
            content = valid_config_content
        path = Path(temp_workspace) / filename
        with open(path, "w") as f:
            f.write(content)
        return str(path)
    return _create


class TestEvolutionInitialization:
    """Tests for Evolution class initialization."""

    @pytest.mark.immediate
    def test_evolution_can_be_instantiated(self):
        """Test that Evolution class can be instantiated."""
        from Evolution import Evolution

        evolution = Evolution()
        assert evolution is not None

    @pytest.mark.immediate
    def test_evolution_has_evolve_method(self):
        """Test that Evolution has an evolve method."""
        from Evolution import Evolution

        evolution = Evolution()
        assert hasattr(evolution, "evolve")
        assert callable(evolution.evolve)

    @pytest.mark.immediate
    def test_evolution_has_validate_arguments_method(self):
        """Test that Evolution has a validate_arguments method."""
        from Evolution import Evolution

        evolution = Evolution()
        assert hasattr(evolution, "validate_arguments")


class TestEvolutionValidation:
    """Tests for Evolution argument validation."""

    @pytest.mark.immediate
    def test_validate_arguments_accepts_none_directory(self):
        """Test that validate_arguments accepts None as output directory."""
        from Evolution import Evolution

        evolution = Evolution()
        result = evolution.validate_arguments(None)
        assert result == ""

    @pytest.mark.immediate
    def test_validate_arguments_accepts_valid_directory(self, temp_workspace):
        """Test that validate_arguments accepts a valid directory."""
        from Evolution import Evolution

        evolution = Evolution()
        result = evolution.validate_arguments(temp_workspace)
        assert result == ""

    @pytest.mark.immediate
    def test_validate_arguments_rejects_invalid_directory(self):
        """Test that validate_arguments reports invalid directories."""
        from Evolution import Evolution

        evolution = Evolution()
        result = evolution.validate_arguments("/nonexistent/path/12345")
        assert "PATH_NOT_RECOGNIZED" in result


class TestEvolutionPrintOnly:
    """Tests for Evolution print-only mode."""

    @pytest.mark.immediate
    def test_print_only_does_not_create_population(self, temp_workspace, create_config_file):
        """Test that print_only mode doesn't create a population."""
        from Evolution import Evolution

        config_path = create_config_file()
        built_config_path = str(Path(temp_workspace) / "built.ini")

        evolution = Evolution()
        evolution.evolve(
            primary_config_path=config_path,
            experiment_description="test",
            base_config_path=None,
            built_config_path=built_config_path,
            output_directory=None,
            print_action_only=True,
        )

        assert not hasattr(evolution, "population")

    @pytest.mark.immediate
    def test_print_only_does_not_create_logger(self, temp_workspace, create_config_file):
        """Test that print_only mode doesn't create a logger."""
        from Evolution import Evolution

        config_path = create_config_file()
        built_config_path = str(Path(temp_workspace) / "built.ini")

        evolution = Evolution()
        evolution.evolve(
            primary_config_path=config_path,
            experiment_description="test",
            base_config_path=None,
            built_config_path=built_config_path,
            output_directory=None,
            print_action_only=True,
        )

        assert not hasattr(evolution, "logger")


class TestEvolutionExecution:
    """Tests for Evolution execution."""

    @pytest.mark.short
    @pytest.mark.xfail(
        reason="WorkspaceFormatter.format_workspace expects files that don't exist in test environment"
    )
    def test_evolution_creates_config(self, temp_workspace, create_config_file):
        """Test that evolution creates the built config file."""
        from Evolution import Evolution

        config_path = create_config_file()
        built_config_path = str(Path(temp_workspace) / "workspace" / "built.ini")

        evolution = Evolution()

        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_workspace)
                evolution.evolve(
                    primary_config_path=config_path,
                    experiment_description="test",
                    base_config_path=None,
                    built_config_path=built_config_path,
                    output_directory=None,
                    print_action_only=False,
                )
            finally:
                os.chdir(original_cwd)

        assert Path(built_config_path).exists()

    @pytest.mark.short
    @pytest.mark.xfail(
        reason="WorkspaceFormatter.format_workspace expects files that don't exist in test environment"
    )
    def test_evolution_sets_experiment_description(self, temp_workspace, create_config_file):
        """Test that evolution stores the experiment description."""
        from Evolution import Evolution

        config_path = create_config_file()
        built_config_path = str(Path(temp_workspace) / "workspace" / "built.ini")
        description = "Test experiment description"

        evolution = Evolution()

        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_workspace)
                evolution.evolve(
                    primary_config_path=config_path,
                    experiment_description=description,
                    base_config_path=None,
                    built_config_path=built_config_path,
                    output_directory=None,
                    print_action_only=False,
                )
            finally:
                os.chdir(original_cwd)

        assert evolution.experiment_description == description

    @pytest.mark.short
    @pytest.mark.xfail(
        reason="WorkspaceFormatter.format_workspace expects files that don't exist in test environment"
    )
    def test_evolution_creates_population(self, temp_workspace, create_config_file):
        """Test that evolution creates a CircuitPopulation."""
        from Evolution import Evolution

        config_path = create_config_file()
        built_config_path = str(Path(temp_workspace) / "workspace" / "built.ini")

        evolution = Evolution()

        with patch("Evolution.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_workspace)
                evolution.evolve(
                    primary_config_path=config_path,
                    experiment_description="test",
                    base_config_path=None,
                    built_config_path=built_config_path,
                    output_directory=None,
                    print_action_only=False,
                )
            finally:
                os.chdir(original_cwd)

        assert hasattr(evolution, "population")
        assert evolution.population is not None


class TestEvolutionCleanup:
    """Tests for Evolution cleanup operations."""

    @pytest.mark.immediate
    def test_clean_up_method_exists(self):
        """Test that Evolution has a clean_up method."""
        from Evolution import Evolution

        evolution = Evolution()
        assert hasattr(evolution, "clean_up")
