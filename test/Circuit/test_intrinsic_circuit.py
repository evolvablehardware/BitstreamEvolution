"""
test_intrinsic_circuit.py
-------------------------

Tests for IntrinsicCircuit using proper pytest fixtures.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from Circuit.IntrinsicCircuit import IntrinsicCircuit


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace with required directories."""
    temp_dir = tempfile.mkdtemp(prefix="intrinsic_test_")

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
    return config


@pytest.fixture
def mock_fitness_func():
    """Create a mock fitness function."""
    return Mock()


@pytest.fixture
def intrinsic_circuit(mock_config, mock_fitness_func):
    """Create an IntrinsicCircuit for testing."""
    rand = Mock()
    logger = Mock()
    microcontroller = Mock()

    template = Path(os.path.join("test", "res", "inputs", "hardware_file.asc"))

    return IntrinsicCircuit(
        1, "test", mock_config, template, rand, logger,
        microcontroller, mock_fitness_func
    )


# NOTE: Don't need to test mutation/crossover since those are already tested by sim hardware tests
# Just need to test fitness evaluation


class TestIntrinsicCircuitEvaluation:
    """Tests for IntrinsicCircuit fitness evaluation."""

    @pytest.mark.immediate
    def test_eval(self, intrinsic_circuit, mock_fitness_func):
        """Test that fitness evaluation uses the fitness function correctly."""
        mock_fitness_func.get_measurements.return_value = [1, 2, 3]
        mock_fitness_func.calculate_fitness.return_value = 6

        # Must check that get_measurements was called
        intrinsic_circuit.collect_data_once()
        fit = intrinsic_circuit.calculate_fitness()

        assert fit == 6
        mock_fitness_func.get_measurements.assert_called()
