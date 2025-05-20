from unittest.mock import Mock
from BitstreamEvolutionProtocols import DataRequest, Measurement, Population
from Circuit.FileBasedCircuit import FileBasedCircuit
from EvaluateFitness.EvalPulseCountFitness import EvalPulseCountFitness
from EvaluateFitness.EvalVarMaxFitness import EvalVarMaxFitness
from EvaluateFitness.EvaluateFitness import EvaluateFitness
from PlotDataRecorder import PlotDataRecorder

def test_varmax_fitness():
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    ckt = Mock(spec=FileBasedCircuit)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    eval = EvaluateFitness(varmax)
    pop = Population([0], None) # using the number '0' as an individual works fine
    measure = Measurement('fake-fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.record_measurement_result([0, 2]) # expect fitness = 1
    eval.evaluate(pop, [measure])
    fit = pop.population_list[0][1]
    assert fit == 1

def test_pulse_fitness():
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    ckt = Mock(spec=FileBasedCircuit)
    pulse = EvalPulseCountFitness(1000, plot_data_recorder)
    eval = EvaluateFitness(pulse)
    pop = Population([0], None) # using the number '0' as an individual works fine
    measure = Measurement('fake-fpga', DataRequest.OSCILLATIONS, ckt, 2)
    measure.record_measurement_result([1001, 1002]) # expect using 1002, so 1/(1002-1000) = 1/2 = 0.5
    eval.evaluate(pop, [measure])
    fit = pop.population_list[0][1]
    assert fit == 0.5
