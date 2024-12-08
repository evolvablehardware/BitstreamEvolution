import os
from pathlib import Path
from unittest.mock import Mock
from Circuit.IntrinsicCircuit import IntrinsicCircuit

circuit = None
config = Mock()
rand = Mock()
logger = Mock()
microcontroller = Mock()

fitness_func = Mock()

# Set directories for workspace files in tests
config.get_data_directory.return_value = Path(os.path.join('test', 'out', 'data'))
config.get_asc_directory.return_value = Path(os.path.join('test', 'out', 'asc'))
config.get_bin_directory.return_value = Path(os.path.join('test', 'out', 'bin'))

# Set other relevant config values
config.get_accessed_columns.return_value = [14,15,24,25,40,41]
config.get_routing_type.return_value = 'MOORE'

template = Path(os.path.join('test', 'res', 'inputs', 'hardware_file.asc'))
circuit = IntrinsicCircuit(1, 'test', config, template, rand, logger, microcontroller, fitness_func)

# NOTE: Don't need to test mutation/crossover since those are already tested by sim hardware tests
# Just need to test fitness evaluation

def test_eval():
    fitness_func.get_measurements.return_value = [1, 2, 3]
    fitness_func.calculate_fitness.return_value = 6
    # Must check that get_measurements was called
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    assert fit == 6
    fitness_func.get_measurements.assert_called()
