"""
test_hardware_sim_circuit.py
----------------------------

Tests for SimHardwareCircuit using proper pytest fixtures.
NOTE: These tests require the IceStorm toolchain (icepack) to be installed.
They will be skipped if the toolchain is not available.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from Circuit.SimHardwareCircuit import SimHardwareCircuit

# Check if icepack is available - if not, skip these tests
ICEPACK_AVAILABLE = shutil.which("icepack") is not None

pytestmark = pytest.mark.skipif(
    not ICEPACK_AVAILABLE,
    reason="IceStorm toolchain (icepack) not installed - required for SimHardwareCircuit tests"
)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace with required directories."""
    temp_dir = tempfile.mkdtemp(prefix="sim_hw_test_")

    # Create required directories
    data_dir = Path(temp_dir) / "data"
    asc_dir = Path(temp_dir) / "asc"
    bin_dir = Path(temp_dir) / "bin"

    data_dir.mkdir(parents=True, exist_ok=True)
    asc_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)

    yield {
        "temp_dir": temp_dir,
        "data_dir": data_dir,
        "asc_dir": asc_dir,
        "bin_dir": bin_dir,
    }


@pytest.fixture
def mock_config(temp_workspace):
    """Create a mock config with workspace directories."""
    config = Mock()
    config.get_data_directory.return_value = temp_workspace["data_dir"]
    config.get_asc_directory.return_value = temp_workspace["asc_dir"]
    config.get_bin_directory.return_value = temp_workspace["bin_dir"]
    config.get_accessed_columns.return_value = [14, 15, 24, 25, 40, 41]
    config.get_routing_type.return_value = "MOORE"
    config.get_mutation_probability.return_value = 1
    return config


@pytest.fixture
def mock_rand():
    """Create a mock random generator."""
    return Mock()


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock()


@pytest.fixture
def template_path():
    """Return the path to the hardware template file."""
    return Path(os.path.join("test", "res", "inputs", "hardware_file.asc"))


@pytest.fixture
def circuit(mock_config, template_path, mock_logger, mock_rand):
    """Create a SimHardwareCircuit for testing."""
    return SimHardwareCircuit(1, "test", mock_config, template_path, mock_logger, mock_rand)


class TestSimHardwareCircuitEvaluation:
    """Tests for SimHardwareCircuit fitness evaluation."""

    @pytest.mark.immediate
    def test_zero_eval(self, circuit, mock_rand):
        """Test fitness evaluation with all-zero bitstream."""
        # Mock randomize all to set every bit to 0
        mock_rand.integers.return_value = 48
        circuit.randomize_bitstream()

        circuit.clear_data()
        circuit.upload()
        circuit.collect_data_once()
        fit = circuit.calculate_fitness()
        # Sums up all the bits
        assert fit == 0

    @pytest.mark.immediate
    def test_simple_eval(self, circuit, mock_rand):
        """Test fitness evaluation with all-ones bitstream."""
        # Mock randomize all to set every bit to 1
        mock_rand.integers.return_value = 49
        circuit.randomize_bitstream()

        circuit.clear_data()
        circuit.upload()
        circuit.collect_data_once()
        fit = circuit.calculate_fitness()
        assert fit == 1728


class TestSimHardwareCircuitMutation:
    """Tests for SimHardwareCircuit mutation."""

    @pytest.mark.immediate
    def test_mutate(self, circuit, mock_config, mock_rand):
        """Test mutation flips all bits when probability is 1."""
        # Mock randomize all to set every bit to 0
        mock_rand.integers.return_value = 48
        circuit.randomize_bitstream()

        # Should mutate every value (since all start at 0)
        mock_config.get_mutation_probability.return_value = 1
        mock_rand.uniform.return_value = 0
        circuit.mutate()

        circuit.clear_data()
        circuit.upload()
        circuit.collect_data_once()
        fit = circuit.calculate_fitness()
        assert fit == 1728


class TestSimHardwareCircuitCrossover:
    """Tests for SimHardwareCircuit crossover."""

    @pytest.mark.immediate
    def test_crossover(self, circuit, mock_config, template_path, mock_logger, mock_rand):
        """Test crossover transfers bits from parent."""
        parent = SimHardwareCircuit(2, "test2", mock_config, template_path, mock_logger, mock_rand)

        mock_rand.integers.return_value = 48
        circuit.randomize_bitstream()

        mock_rand.integers.return_value = 49
        parent.randomize_bitstream()

        circuit.crossover(parent, 3)

        circuit.clear_data()
        circuit.upload()
        circuit.collect_data_once()
        fit = circuit.calculate_fitness()
        # 96 tiles, and we are allowing 2 bits in each of them to be crossed over & set to 1
        assert fit == 96 * 2
