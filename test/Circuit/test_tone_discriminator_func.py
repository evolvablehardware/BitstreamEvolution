#! /bin/python
"""
test_tone_discriminator_func.py
-------------------------------

Tests for the ToneDiscriminatorFitnessFunction class.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from Circuit.ToneDiscriminatorFitnessFunction import ToneDiscriminatorFitnessFunction


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    config = Mock()
    return config


@pytest.fixture
def mock_mcu():
    """Create a mock microcontroller for testing."""
    mcu = Mock()
    mcu.measure_signal_td = Mock()
    return mcu


@pytest.fixture
def fitness_func():
    """Create a ToneDiscriminatorFitnessFunction instance."""
    return ToneDiscriminatorFitnessFunction()


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for test output files."""
    temp_dir = tempfile.mkdtemp(prefix="tone_disc_test_")
    workspace = Path(temp_dir) / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    yield temp_dir

    os.chdir(original_cwd)


class TestToneDiscriminatorFitnessFunctionInit:
    """Tests for ToneDiscriminatorFitnessFunction initialization."""

    @pytest.mark.immediate
    def test_can_instantiate(self, fitness_func):
        """Test that ToneDiscriminatorFitnessFunction can be instantiated."""
        assert fitness_func is not None

    @pytest.mark.immediate
    def test_inherits_from_fitness_function(self, fitness_func):
        """Test that ToneDiscriminatorFitnessFunction inherits from FitnessFunction."""
        from Circuit.FitnessFunction import FitnessFunction
        assert isinstance(fitness_func, FitnessFunction)


class TestToneDiscriminatorCalculateFitness:
    """Tests for the calculate_fitness method."""

    @pytest.mark.immediate
    def test_calculate_fitness_returns_average(self, fitness_func):
        """Test that calculate_fitness returns the average of measurements."""
        measurements = [0.5, 0.6, 0.7]
        result = fitness_func.calculate_fitness(measurements)
        expected = sum(measurements) / len(measurements)
        assert abs(result - expected) < 0.001

    @pytest.mark.immediate
    def test_calculate_fitness_single_value(self, fitness_func):
        """Test calculate_fitness with a single measurement."""
        measurements = [0.8]
        result = fitness_func.calculate_fitness(measurements)
        assert result == 0.8

    @pytest.mark.immediate
    def test_calculate_fitness_zero_measurements(self, fitness_func):
        """Test calculate_fitness with zero values."""
        measurements = [0.0, 0.0, 0.0]
        result = fitness_func.calculate_fitness(measurements)
        assert result == 0.0

    @pytest.mark.immediate
    def test_calculate_fitness_perfect_score(self, fitness_func):
        """Test calculate_fitness with perfect measurements."""
        measurements = [1.0, 1.0, 1.0]
        result = fitness_func.calculate_fitness(measurements)
        assert result == 1.0

    @pytest.mark.immediate
    @pytest.mark.parametrize("measurements,expected", [
        ([0.2, 0.4, 0.6], 0.4),
        ([0.1, 0.9], 0.5),
        ([0.0, 1.0], 0.5),
        ([0.25, 0.25, 0.5], 1.0/3.0),
    ])
    def test_calculate_fitness_various_inputs(self, fitness_func, measurements, expected):
        """Test calculate_fitness with various input combinations."""
        result = fitness_func.calculate_fitness(measurements)
        assert abs(result - expected) < 0.001


class TestToneDiscriminatorDataReading:
    """Tests for data reading functionality."""

    @pytest.mark.immediate
    def test_attach_sets_data_filepath(self, fitness_func, mock_mcu, mock_config):
        """Test that attach correctly sets the data filepath."""
        test_path = Path("test/data/file.txt")
        extra_data = {}
        fitness_func.attach(test_path, mock_mcu, mock_config, extra_data)

        assert fitness_func._data_filepath == test_path

    @pytest.mark.immediate
    def test_attach_sets_microcontroller(self, fitness_func, mock_mcu, mock_config):
        """Test that attach correctly sets the microcontroller."""
        test_path = Path("test/data/file.txt")
        extra_data = {}
        fitness_func.attach(test_path, mock_mcu, mock_config, extra_data)

        assert fitness_func._microcontroller == mock_mcu


class TestToneDiscriminatorFitnessCalculation:
    """Tests for the internal fitness calculation logic."""

    @pytest.mark.immediate
    def test_fitness_range_zero_to_one(self, fitness_func):
        """Test that fitness values are in the range [0, 1]."""
        # Test various measurement sets that should produce valid fitness values
        test_cases = [
            [0.0],
            [1.0],
            [0.5],
            [0.0, 1.0],
            [0.25, 0.75],
        ]

        for measurements in test_cases:
            fitness = fitness_func.calculate_fitness(measurements)
            assert 0.0 <= fitness <= 1.0, f"Fitness {fitness} out of range for {measurements}"
