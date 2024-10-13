import os
from pathlib import Path
from unittest.mock import Mock
from Circuit.SimHardwareCircuit import SimHardwareCircuit

circuit = None
config = Mock()
rand = Mock()

# Set directories for workspace files in tests
config.get_data_directory.return_value = Path(os.path.join('test', 'out', 'data'))
config.get_asc_directory.return_value = Path(os.path.join('test', 'out', 'asc'))
config.get_bin_directory.return_value = Path(os.path.join('test', 'out', 'bin'))

template = Path(os.path.join('test', 'res', 'inputs', 'hardware_file.asc'))
circuit = SimHardwareCircuit(1, 'test', config, template, rand)

def test_zero_eval():
    circuit.upload()
    circuit.collect_data_once()
    fit = circuit.calculate_fitness()
    # Bitstream defaults to all 0s, so should have no functions turned on
    assert fit == 0
