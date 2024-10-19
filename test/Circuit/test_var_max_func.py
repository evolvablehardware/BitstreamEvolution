import os
from unittest.mock import Mock
from pathlib import Path
from Circuit.VarMaxFitnessFunction import VarMaxFitnessFunction

# Takes in total samples
ff = VarMaxFitnessFunction(6)

data_filepath = Path(os.path.join('test', 'res', 'inputs', 'test_varmax_data.txt'))
mcu = Mock()
config = Mock()

ff.attach(data_filepath, mcu, config)

def test_get_measurement():
    # Fake data file should produce 400/5 = 80 for fitness
    fit = ff.get_measurements()
    assert fit[0] == 80

def test_calculate_fitness():
    # Takes the average of the data
    fit = ff.calculate_fitness([1, 2, 3])
    assert fit == 2
