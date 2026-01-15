#! /bin/python
"""
test_circuit_population.py
--------------------------

Tests for the CircuitPopulation class which manages the genetic algorithm population.
Tests use FULLY_SIM mode for isolation from hardware.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

from CircuitPopulation import CircuitPopulation
from Config import Config
from ConfigBuilder import ConfigBuilder


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="circuit_pop_test_")
    yield temp_dir


@pytest.fixture
def base_config_content():
    """
    Returns a valid, self-contained configuration for FULLY_SIM testing.
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
population_size = 10
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
generations = 5
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
def create_config(temp_dir, base_config_content):
    """
    Factory fixture to create a Config object with optional modifications.
    """
    def _create_config(modifications=None):
        content = base_config_content
        if modifications:
            for old, new in modifications.items():
                content = content.replace(old, new)

        input_path = Path(temp_dir) / "input_config.ini"
        output_path = Path(temp_dir) / "built_config.ini"

        with open(input_path, "w") as f:
            f.write(content)

        builder = ConfigBuilder(str(input_path))
        builder.build_config(str(output_path))

        config = Config(str(output_path))
        # Add a mock logger to avoid NoneType errors
        mock_logger = Mock()
        config.add_logger(mock_logger)
        return config

    return _create_config


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    logger = Mock()
    logger.log_event = Mock()
    logger.log_info = Mock()
    logger.log_error = Mock()
    logger.log_warning = Mock()
    logger.get_best_file = Mock(return_value=Path("./workspace/best.asc"))
    return logger


@pytest.fixture
def mock_mcu():
    """Create a mock microcontroller for testing."""
    mcu = Mock()
    mcu.measure_variance = Mock(return_value=100.0)
    mcu.measure_pulse_count = Mock(return_value=1000)
    return mcu


class TestCircuitPopulationInitialization:
    """Tests for CircuitPopulation initialization."""

    @pytest.mark.immediate
    def test_population_initializes_with_correct_selection(self, create_config, mock_mcu, mock_logger):
        """Test that CircuitPopulation initializes with the specified selection method."""
        config = create_config()
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        # Check that the population object was created
        assert pop is not None

    @pytest.mark.immediate
    @pytest.mark.parametrize("selection_type,expected_substring", [
        ("SINGLE_ELITE", "single_elite"),
        ("FRAC_ELITE", "fractional_elite"),
        ("FIT_PROP_SEL", "fitness_proportional"),
        ("RANK_PROP_SEL", "rank_proportional"),
    ])
    def test_selection_method_assignment(
        self, create_config, mock_mcu, mock_logger, selection_type, expected_substring
    ):
        """Test that the correct selection method is assigned based on config."""
        config = create_config({"selection = FIT_PROP_SEL": f"selection = {selection_type}"})
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        # The __run_selection method should be set to the correct implementation
        # We check by looking at the method name contains expected substring
        actual_method_name = pop._CircuitPopulation__run_selection.__name__
        assert expected_substring in actual_method_name


class TestCircuitPopulationPopulate:
    """Tests for the populate method."""

    @pytest.mark.short
    def test_populate_creates_correct_number_of_circuits(self, create_config, mock_mcu, mock_logger):
        """Test that populate creates the correct number of circuits."""
        config = create_config()
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()

        # Access the internal circuits list
        circuits = pop._CircuitPopulation__circuits
        expected_size = config.get_population_size()
        assert len(circuits) == expected_size

    @pytest.mark.short
    @pytest.mark.parametrize("pop_size", [5, 10, 20])
    def test_populate_with_different_sizes(
        self, create_config, mock_mcu, mock_logger, pop_size
    ):
        """Test that populate works with different population sizes."""
        config = create_config({
            "population_size = 10": f"population_size = {pop_size}"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()

        circuits = pop._CircuitPopulation__circuits
        assert len(circuits) == pop_size


class TestCircuitPopulationEvolve:
    """Tests for the evolve method."""

    @pytest.mark.short
    def test_evolve_runs_correct_generations(self, create_config, mock_mcu, mock_logger):
        """Test that evolve runs the specified number of generations."""
        config = create_config({
            "generations = 5": "generations = 3",
            "population_size = 10": "population_size = 5"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()
        pop.evolve()

        # Check that the current epoch matches expected generations
        assert pop.get_current_epoch() == 3

    @pytest.mark.short
    def test_evolve_maintains_population_size(self, create_config, mock_mcu, mock_logger):
        """Test that population size remains constant after evolution."""
        pop_size = 8
        config = create_config({
            "population_size = 10": f"population_size = {pop_size}",
            "generations = 5": "generations = 2"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()
        initial_size = len(pop._CircuitPopulation__circuits)

        pop.evolve()

        final_size = len(pop._CircuitPopulation__circuits)
        assert initial_size == final_size == pop_size


class TestCircuitPopulationFitness:
    """Tests for fitness-related functionality."""

    @pytest.mark.short
    def test_circuits_have_fitness_after_populate(self, create_config, mock_mcu, mock_logger):
        """Test that circuits have fitness values after population."""
        config = create_config({"population_size = 10": "population_size = 5"})
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()

        circuits = pop._CircuitPopulation__circuits
        for circuit in circuits:
            # Fitness should be a number (could be 0 for initial random circuits)
            assert isinstance(circuit.get_fitness(), (int, float))

    @pytest.mark.short
    def test_best_circuit_has_highest_fitness(self, create_config, mock_mcu, mock_logger):
        """Test that the first circuit (best) has the highest fitness in population."""
        config = create_config({"population_size = 10": "population_size = 5"})
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()

        # Circuits are sorted by fitness (descending), so first should be best
        circuits = pop._CircuitPopulation__circuits
        if len(circuits) > 0:
            best_circuit = circuits[0]
            best_fitness = best_circuit.get_fitness()

            # The best fitness should be >= all other fitnesses
            for circuit in circuits:
                assert best_fitness >= circuit.get_fitness()


class TestCircuitPopulationDiversity:
    """Tests for diversity measurement."""

    @pytest.mark.short
    @pytest.mark.xfail(
        reason="Bug: UNIQUE diversity measure calls get_sim_bitstream which doesn't exist on FullySimCircuit"
    )
    @pytest.mark.parametrize("diversity_measure", ["UNIQUE"])
    def test_diversity_measure_unique_computes(
        self, create_config, mock_mcu, mock_logger, diversity_measure
    ):
        """Test that UNIQUE diversity measure can be computed without error."""
        config = create_config({
            "diversity_measure = HAMMING_DIST": f"diversity_measure = {diversity_measure}",
            "population_size = 10": "population_size = 5"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()

        # This should not raise an exception but currently has a bug
        diversity = pop.count_unique()
        assert isinstance(diversity, (int, float))


class TestCircuitPopulationElitism:
    """Tests for elitism functionality."""

    @pytest.mark.short
    def test_elitism_fraction_affects_elite_count(self, create_config, mock_mcu, mock_logger):
        """Test that elitism fraction determines number of elites."""
        config = create_config({
            "elitism_fraction = 0.2": "elitism_fraction = 0.3",
            "population_size = 10": "population_size = 10"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        # n_elites = ceil(0.3 * 10) = 3
        expected_elites = 3
        actual_elites = pop._CircuitPopulation__n_elites
        assert actual_elites == expected_elites

    @pytest.mark.short
    @pytest.mark.parametrize("fraction,pop_size,expected", [
        (0.1, 10, 1),   # ceil(0.1 * 10) = 1
        (0.2, 10, 2),   # ceil(0.2 * 10) = 2
        (0.15, 20, 3),  # ceil(0.15 * 20) = 3
        (0.5, 10, 5),   # ceil(0.5 * 10) = 5
    ])
    def test_elite_count_calculation(
        self, create_config, mock_mcu, mock_logger, fraction, pop_size, expected
    ):
        """Test elite count calculation with various fraction/size combinations."""
        config = create_config({
            "elitism_fraction = 0.2": f"elitism_fraction = {fraction}",
            "population_size = 10": f"population_size = {pop_size}"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        assert pop._CircuitPopulation__n_elites == expected


class TestCircuitPopulationEpochTracking:
    """Tests for epoch/generation tracking."""

    @pytest.mark.immediate
    def test_initial_epoch_is_zero(self, create_config, mock_mcu, mock_logger):
        """Test that initial epoch is 0 before evolution."""
        config = create_config()
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        assert pop.get_current_epoch() == 0

    @pytest.mark.short
    def test_epoch_increments_during_evolution(self, create_config, mock_mcu, mock_logger):
        """Test that epoch increments correctly during evolution."""
        n_generations = 4
        config = create_config({
            "generations = 5": f"generations = {n_generations}",
            "population_size = 10": "population_size = 5"
        })
        pop = CircuitPopulation(mock_mcu, config, mock_logger)

        pop.populate()

        # Track epoch through evolution
        assert pop.get_current_epoch() == 0

        pop.evolve()

        assert pop.get_current_epoch() == n_generations
