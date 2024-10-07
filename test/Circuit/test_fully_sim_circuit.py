from unittest.mock import Mock
from Circuit.FullySimCircuit import FullySimCircuit

circuit = None
config = Mock() #patch('Config.Config')
rand = Mock() #patch('numpy.Generator')

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


