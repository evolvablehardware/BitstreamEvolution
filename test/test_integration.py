#! /bin/python
"""
test_integration.py
-------------------

Integration tests that verify multiple components work together correctly.
These tests use FULLY_SIM mode to avoid hardware dependencies.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from Config import Config
from ConfigBuilder import ConfigBuilder
from CircuitPopulation import CircuitPopulation


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    temp_dir = tempfile.mkdtemp(prefix="integration_test_")
    workspace = Path(temp_dir) / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    yield temp_dir


@pytest.fixture
def integration_config_content():
    """
    Returns a complete config for integration testing.
    Uses FULLY_SIM mode with small parameters for fast testing.
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
generations = 3
target_fitness = IGNORE

[PLOTTING PARAMETERS]
launch_plots = false
frame_interval = 10000

[LOGGING PARAMETERS]
log_level = 1
save_log = false
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
def create_integration_config(temp_workspace, integration_config_content):
    """Factory to create built config for integration tests."""
    def _create(modifications=None):
        content = integration_config_content
        if modifications:
            for old, new in modifications.items():
                content = content.replace(old, new)

        input_path = Path(temp_workspace) / "config.ini"
        output_path = Path(temp_workspace) / "built_config.ini"

        with open(input_path, "w") as f:
            f.write(content)

        builder = ConfigBuilder(str(input_path))
        builder.build_config(str(output_path))

        config = Config(str(output_path))

        # Add a mock logger
        mock_logger = Mock()
        mock_logger.log_event = Mock()
        mock_logger.log_info = Mock()
        mock_logger.log_error = Mock()
        mock_logger.log_warning = Mock()
        mock_logger.get_best_file = Mock(return_value=Path("./workspace/best.asc"))
        config.add_logger(mock_logger)

        return config, mock_logger

    return _create


class TestConfigToPopulationIntegration:
    """Tests for Config -> CircuitPopulation integration."""

    @pytest.mark.short
    def test_config_creates_correct_population_size(self, create_integration_config):
        """Test that CircuitPopulation uses population_size from Config."""
        config, logger = create_integration_config()
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()

        circuits = pop._CircuitPopulation__circuits
        assert len(circuits) == config.get_population_size()

    @pytest.mark.short
    def test_config_elitism_affects_population(self, create_integration_config):
        """Test that elitism_fraction from Config affects population behavior."""
        config, logger = create_integration_config({
            "elitism_fraction = 0.2": "elitism_fraction = 0.4"
        })
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)

        # With 0.4 elitism and 5 population, we should have 2 elites (ceil(0.4 * 5))
        expected_elites = 2
        assert pop._CircuitPopulation__n_elites == expected_elites

    @pytest.mark.short
    def test_config_generations_controls_evolution(self, create_integration_config):
        """Test that generations from Config controls evolution length."""
        n_generations = 2
        config, logger = create_integration_config({
            "generations = 3": f"generations = {n_generations}"
        })
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()
        pop.evolve()

        assert pop.get_current_epoch() == n_generations


class TestPopulationEvolutionIntegration:
    """Tests for population evolution with multiple components."""

    @pytest.mark.short
    def test_evolution_preserves_population_integrity(self, create_integration_config):
        """Test that population maintains integrity through evolution."""
        config, logger = create_integration_config()
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()

        initial_size = len(pop._CircuitPopulation__circuits)
        pop.evolve()
        final_size = len(pop._CircuitPopulation__circuits)

        assert initial_size == final_size

    @pytest.mark.short
    def test_evolution_circuits_have_valid_fitness(self, create_integration_config):
        """Test that all circuits have valid fitness after evolution."""
        config, logger = create_integration_config()
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()
        pop.evolve()

        circuits = pop._CircuitPopulation__circuits
        for circuit in circuits:
            fitness = circuit.get_fitness()
            assert isinstance(fitness, (int, float))
            assert fitness >= 0  # Fitness should be non-negative

    @pytest.mark.short
    def test_evolution_maintains_sorted_order(self, create_integration_config):
        """Test that circuits remain sorted by fitness after evolution."""
        config, logger = create_integration_config()
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()
        pop.evolve()

        circuits = pop._CircuitPopulation__circuits
        fitnesses = [c.get_fitness() for c in circuits]

        # Circuits should be sorted in descending order
        for i in range(len(fitnesses) - 1):
            assert fitnesses[i] >= fitnesses[i + 1]


class TestSelectionMethodIntegration:
    """Tests for different selection methods in integration context."""

    @pytest.mark.short
    @pytest.mark.parametrize("selection_method", [
        "FIT_PROP_SEL",
        "RANK_PROP_SEL",
        "SINGLE_ELITE",
        "FRAC_ELITE",
    ])
    def test_selection_methods_complete_evolution(
        self, create_integration_config, selection_method
    ):
        """Test that evolution completes with different selection methods."""
        config, logger = create_integration_config({
            "selection = FIT_PROP_SEL": f"selection = {selection_method}"
        })
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()

        # Should complete without exception
        pop.evolve()

        assert pop.get_current_epoch() == 3


class TestConfigBuilderIntegration:
    """Tests for ConfigBuilder integration."""

    @pytest.mark.immediate
    def test_config_builder_creates_valid_config(self, temp_workspace, integration_config_content):
        """Test that ConfigBuilder creates a valid, usable config."""
        input_path = Path(temp_workspace) / "input.ini"
        output_path = Path(temp_workspace) / "output.ini"

        with open(input_path, "w") as f:
            f.write(integration_config_content)

        builder = ConfigBuilder(str(input_path))
        builder.build_config(str(output_path))

        # Should be able to load and use the config
        config = Config(str(output_path))
        assert config.get_simulation_mode() == "FULLY_SIM"
        assert config.get_population_size() == 5
        assert config.get_fitness_func() == "VARIANCE"


class TestFullPipelineIntegration:
    """Tests for the full evolution pipeline."""

    @pytest.mark.short
    def test_full_pipeline_runs_to_completion(self, create_integration_config):
        """Test that the full pipeline runs without errors."""
        config, logger = create_integration_config({
            "population_size = 5": "population_size = 4",
            "generations = 3": "generations = 2"
        })
        mock_mcu = Mock()

        # Create and run evolution
        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()
        pop.evolve()

        # Verify completion
        assert pop.get_current_epoch() == 2
        assert len(pop._CircuitPopulation__circuits) == 4

    @pytest.mark.short
    def test_pipeline_best_circuit_tracking(self, create_integration_config):
        """Test that best circuit is tracked throughout evolution."""
        config, logger = create_integration_config()
        mock_mcu = Mock()

        pop = CircuitPopulation(mock_mcu, config, logger)
        pop.populate()
        pop.evolve()

        # Best circuit info should be available
        best_info = pop.get_overall_best_circuit_info()
        assert best_info is not None
        assert hasattr(best_info, "fitness")
        assert hasattr(best_info, "name")
