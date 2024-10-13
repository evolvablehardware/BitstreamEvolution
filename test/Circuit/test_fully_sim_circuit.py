from unittest.mock import Mock
from Circuit.FullySimCircuit import FullySimCircuit

circuit = None
config = Mock()
rand = Mock()

sine_funcs = [(lambda x: (x % 2) * 2)] * 100
circuit = FullySimCircuit(1, 'n/a', config, sine_funcs, rand)

def test_zero_eval():
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    # Bitstream defaults to all 0s, so should have no functions turned on
    assert fit == 0

def test_simple_eval():
    circuit.inject_bitstream([1] * 100)
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    assert fit == 0.998

def test_mutate():
    circuit.inject_bitstream([0] * 100)
    # Should mutate every value (since all start at 0)
    config.get_mutation_probability.return_value = 1
    rand.uniform.return_value = 0
    circuit.mutate()
    bitstream = circuit.get_bitstream()
    for bit in bitstream:
        assert bit == 1

def test_randomize_all():
    # Bitstream starts as all 0s, so mock to change it to all 1s
    circuit.inject_bitstream([0] * 100)
    rand.integers.return_value = 1
    circuit.randomize_bitstream()
    bitstream = circuit.get_bitstream()
    for bit in bitstream:
        assert bit == 1

def test_crossover():
    parent = FullySimCircuit(1, 'n/a', config, sine_funcs, rand)
    circuit.inject_bitstream([0] * 100)
    parent.inject_bitstream([1] * 100)
    circuit.crossover(parent, 50)
    bitstream = circuit.get_bitstream()
    for i in range(50):
        assert bitstream[i] == 1
        assert bitstream[i + 50] == 0
