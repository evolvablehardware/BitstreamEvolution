import os
from pathlib import Path
from unittest.mock import Mock
from Circuit.SimHardwareCircuit import SimHardwareCircuit

circuit = None
config = Mock()
rand = Mock()
logger = Mock()

# Set directories for workspace files in tests
config.get_data_directory.return_value = Path(os.path.join('test', 'out', 'data'))
config.get_asc_directory.return_value = Path(os.path.join('test', 'out', 'asc'))
config.get_bin_directory.return_value = Path(os.path.join('test', 'out', 'bin'))

# Set other relevant config values
config.get_accessed_columns.return_value = [14,15,24,25,40,41]
config.get_routing_type.return_value = 'MOORE'

template = Path(os.path.join('test', 'res', 'inputs', 'hardware_file.asc'))
circuit = SimHardwareCircuit(1, 'test', config, template, logger, rand)

def test_zero_eval():
    # Mock randomize all to set every bit to 0
    rand.integers.return_value = 48
    circuit.randomize_bitstream()

    circuit.clear_data()
    circuit.upload()
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    # Sums up all the bits
    assert fit == 0

def test_simple_eval():
    # Mock randomize all to set every bit to 1
    rand.integers.return_value = 49
    circuit.randomize_bitstream()
    
    circuit.clear_data()
    circuit.upload()
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    assert fit == 1728

def test_mutate():
    # Mock randomize all to set every bit to 0
    rand.integers.return_value = 48
    circuit.randomize_bitstream()

    # Should mutate every value (since all start at 0)
    config.get_mutation_probability.return_value = 1
    rand.uniform.return_value = 0
    circuit.mutate()

    circuit.clear_data()
    circuit.upload()
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    assert fit == 1728
    
def test_crossover():
    parent = SimHardwareCircuit(2, 'test2', config, template, logger, rand)
    
    rand.integers.return_value = 48
    circuit.randomize_bitstream()

    rand.integers.return_value = 49
    parent.randomize_bitstream()

    circuit.crossover(parent, 3)
    
    circuit.clear_data()
    circuit.upload()
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    # 96 tiles, and we are allowing 2 bits in each of them to be crossed over & set to 1
    assert fit == 96 * 2
