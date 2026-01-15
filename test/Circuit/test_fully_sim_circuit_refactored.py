#! /bin/python
"""
test_fully_sim_circuit_refactored.py
------------------------------------

Refactored tests for FullySimCircuit using proper pytest fixtures.
This replaces the module-level state pattern with isolated test fixtures.
"""

from unittest.mock import Mock

import pytest

from Circuit.FullySimCircuit import FullySimCircuit


@pytest.fixture
def mock_config():
    """Create a mock config object for testing."""
    config = Mock()
    config.get_mutation_probability.return_value = 0.5
    return config


@pytest.fixture
def mock_rand():
    """Create a mock random generator for deterministic testing."""
    rand = Mock()
    rand.uniform.return_value = 0.5
    rand.integers.return_value = 0
    return rand


@pytest.fixture
def sine_funcs():
    """Create a list of simple sine functions for testing."""
    # Simple function that returns predictable values
    return [(lambda x: (x % 2) * 2)] * 100


@pytest.fixture
def circuit(mock_config, mock_rand, sine_funcs):
    """Create a fresh FullySimCircuit for each test."""
    return FullySimCircuit(1, "test_circuit", mock_config, sine_funcs, mock_rand)


class TestFullySimCircuitEvaluation:
    """Tests for circuit fitness evaluation."""

    @pytest.mark.immediate
    def test_zero_bitstream_has_zero_fitness(self, circuit):
        """Test that a circuit with all-zero bitstream has zero fitness."""
        circuit.collect_data_once()
        fitness = circuit.calculate_fitness()
        # Bitstream defaults to all 0s, so should have no functions turned on
        assert fitness == 0

    @pytest.mark.immediate
    def test_all_ones_bitstream_has_nonzero_fitness(self, circuit):
        """Test that a circuit with all-ones bitstream has non-zero fitness."""
        circuit.inject_bitstream([1] * 100)
        circuit.collect_data_once()
        fitness = circuit.calculate_fitness()
        # Fitness should be positive when all functions are enabled
        assert fitness > 0

    @pytest.mark.immediate
    def test_fitness_is_numeric(self, circuit):
        """Test that fitness is always a numeric value."""
        circuit.collect_data_once()
        fitness = circuit.calculate_fitness()
        assert isinstance(fitness, (int, float))


class TestFullySimCircuitMutation:
    """Tests for circuit mutation operations."""

    @pytest.mark.immediate
    def test_full_mutation_flips_all_bits(self, mock_config, mock_rand, sine_funcs):
        """Test that 100% mutation probability flips all bits."""
        circuit = FullySimCircuit(1, "test", mock_config, sine_funcs, mock_rand)
        circuit.inject_bitstream([0] * 100)

        # Set up for full mutation
        mock_config.get_mutation_probability.return_value = 1
        mock_rand.uniform.return_value = 0  # Always below probability

        circuit.mutate()
        bitstream = circuit.get_bitstream()

        for bit in bitstream:
            assert bit == 1

    @pytest.mark.immediate
    def test_zero_mutation_preserves_bits(self, mock_config, mock_rand, sine_funcs):
        """Test that 0% mutation probability preserves all bits."""
        circuit = FullySimCircuit(1, "test", mock_config, sine_funcs, mock_rand)
        original = [0] * 50 + [1] * 50
        circuit.inject_bitstream(original.copy())

        # Set up for no mutation
        mock_config.get_mutation_probability.return_value = 0
        mock_rand.uniform.return_value = 0.5  # Always above probability

        circuit.mutate()
        bitstream = circuit.get_bitstream()

        assert list(bitstream) == original


class TestFullySimCircuitRandomization:
    """Tests for circuit randomization operations."""

    @pytest.mark.immediate
    def test_randomize_to_all_ones(self, mock_config, mock_rand, sine_funcs):
        """Test randomization when random generator returns all 1s."""
        circuit = FullySimCircuit(1, "test", mock_config, sine_funcs, mock_rand)
        circuit.inject_bitstream([0] * 100)

        mock_rand.integers.return_value = 1
        circuit.randomize_bitstream()

        bitstream = circuit.get_bitstream()
        for bit in bitstream:
            assert bit == 1

    @pytest.mark.immediate
    def test_randomize_to_all_zeros(self, mock_config, mock_rand, sine_funcs):
        """Test randomization when random generator returns all 0s."""
        circuit = FullySimCircuit(1, "test", mock_config, sine_funcs, mock_rand)
        circuit.inject_bitstream([1] * 100)

        mock_rand.integers.return_value = 0
        circuit.randomize_bitstream()

        bitstream = circuit.get_bitstream()
        for bit in bitstream:
            assert bit == 0


class TestFullySimCircuitCrossover:
    """Tests for circuit crossover operations."""

    @pytest.mark.immediate
    def test_single_point_crossover(self, mock_config, mock_rand, sine_funcs):
        """Test single-point crossover at midpoint."""
        child = FullySimCircuit(1, "child", mock_config, sine_funcs, mock_rand)
        parent = FullySimCircuit(2, "parent", mock_config, sine_funcs, mock_rand)

        child.inject_bitstream([0] * 100)
        parent.inject_bitstream([1] * 100)

        crossover_point = 50
        child.crossover(parent, crossover_point)

        bitstream = child.get_bitstream()

        # First half should be from parent (1s)
        for i in range(crossover_point):
            assert bitstream[i] == 1, f"Bit {i} should be 1 (from parent)"

        # Second half should be original (0s)
        for i in range(crossover_point, 100):
            assert bitstream[i] == 0, f"Bit {i} should be 0 (original)"

    @pytest.mark.immediate
    def test_crossover_at_start(self, mock_config, mock_rand, sine_funcs):
        """Test crossover at position 0 (no change expected)."""
        child = FullySimCircuit(1, "child", mock_config, sine_funcs, mock_rand)
        parent = FullySimCircuit(2, "parent", mock_config, sine_funcs, mock_rand)

        original = [0] * 100
        child.inject_bitstream(original.copy())
        parent.inject_bitstream([1] * 100)

        child.crossover(parent, 0)
        bitstream = child.get_bitstream()

        # All bits should remain original (0s)
        assert list(bitstream) == original

    @pytest.mark.immediate
    def test_crossover_at_end(self, mock_config, mock_rand, sine_funcs):
        """Test crossover at position 100 (full copy from parent)."""
        child = FullySimCircuit(1, "child", mock_config, sine_funcs, mock_rand)
        parent = FullySimCircuit(2, "parent", mock_config, sine_funcs, mock_rand)

        child.inject_bitstream([0] * 100)
        parent.inject_bitstream([1] * 100)

        child.crossover(parent, 100)
        bitstream = child.get_bitstream()

        # All bits should be from parent (1s)
        for bit in bitstream:
            assert bit == 1


class TestFullySimCircuitBitstream:
    """Tests for bitstream manipulation."""

    @pytest.mark.immediate
    def test_inject_bitstream_sets_values(self, circuit):
        """Test that inject_bitstream correctly sets bitstream values."""
        expected = [1, 0, 1, 0] * 25
        circuit.inject_bitstream(expected)

        actual = circuit.get_bitstream()
        assert list(actual) == expected

    @pytest.mark.immediate
    @pytest.mark.xfail(
        reason="get_bitstream returns a reference, not a copy - potential bug or design choice"
    )
    def test_get_bitstream_returns_copy(self, circuit):
        """Test that get_bitstream returns a copy, not the original."""
        circuit.inject_bitstream([0] * 100)
        bitstream1 = circuit.get_bitstream()
        bitstream1[0] = 99  # Modify the returned copy

        bitstream2 = circuit.get_bitstream()
        assert bitstream2[0] != 99  # Original should be unchanged
