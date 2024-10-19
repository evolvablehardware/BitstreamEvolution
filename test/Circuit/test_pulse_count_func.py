import os
from unittest.mock import Mock
from pathlib import Path
from Circuit.PulseCountFitnessFunction import PulseCountFitnessFunction

ff = PulseCountFitnessFunction()

data_filepath = Path(os.path.join('test', 'res', 'inputs', 'test_pulse_count_data.txt'))
mcu = Mock()
config = Mock()

ff.attach(data_filepath, mcu, config)

config.get_desired_frequency.return_value = 1000

def test_get_measurement():
    fit = ff.get_measurements()
    assert fit[0] == 5

def test_calculate_tolerant_fitness():
    config.get_fitness_func.return_value = 'TOLERANT_PULSE_COUNT'
    # Takes the average of the data
    fit = ff.calculate_fitness([980])
    assert abs(fit - 0.726) < 0.001
