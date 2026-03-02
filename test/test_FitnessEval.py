from unittest.mock import Mock
import pytest
from BitstreamEvolutionProtocols import DataRequest, Measurement, Population
from Circuit.FileBasedCircuit import FileBasedCircuit
from EvaluateFitness.EvalPulseCountFitness import EvalPulseCountFitness
from EvaluateFitness.EvalVarMaxFitness import EvalVarMaxFitness
from EvaluateFitness.EvaluateFitness import EvaluateFitness
from PlotDataRecorder import PlotDataRecorder
from returns.result import Success, Failure # type: ignore

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


# --- EvalPulseCountFitness additional tests ---

def test_EvalPulseCountFitness_perfect_match():
    """When pulses == target, fitness should be 1.0."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    pulse = EvalPulseCountFitness(500, plot_data_recorder)
    fit = pulse.calculate_success([500], 0, '')
    assert fit == 1.0


def test_EvalPulseCountFitness_zero_pulses():
    """When pulses == 0, fitness should be 0.0."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    pulse = EvalPulseCountFitness(500, plot_data_recorder)
    fit = pulse.calculate_success([0], 0, '')
    assert fit == 0.0


def test_EvalPulseCountFitness_multiple_samples():
    """With multiple samples, fitness should be the minimum across all."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    pulse = EvalPulseCountFitness(100, plot_data_recorder)
    # 100 -> 1.0, 90 -> 1/10 = 0.1, 50 -> 1/50 = 0.02
    fit = pulse.calculate_success([100, 90, 50], 0, '')
    assert fit == pytest.approx(1.0 / 50)


def test_EvalPulseCountFitness_negative_difference():
    """Pulses below target should still produce valid fitness."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    pulse = EvalPulseCountFitness(100, plot_data_recorder)
    # 95: 1/abs(100-95) = 1/5 = 0.2
    fit = pulse.calculate_success([95], 0, '')
    assert fit == pytest.approx(0.2)


def test_EvalPulseCountFitness_error_returns_zero():
    """calculate_error should return 0."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    pulse = EvalPulseCountFitness(100, plot_data_recorder)
    fit = pulse.calculate_error(Exception("err"), 0, '')
    assert fit == 0


# --- EvalVarMaxFitness additional tests ---

def test_EvalVarMaxFitness_constant_data():
    """Constant data (no variance) should give fitness = 0."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    varmax.start_eval()
    fit = varmax.calculate_success([5, 5, 5, 5], 0, '')
    assert fit == 0.0


def test_EvalVarMaxFitness_high_variance():
    """High variance data should give high fitness."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    varmax.start_eval()
    # [0, 100, 0, 100] -> variance_sum = 100+100+100 = 300, total_samples = 4
    fit = varmax.calculate_success([0, 100, 0, 100], 0, '')
    assert fit == pytest.approx(300.0 / 4)


def test_EvalVarMaxFitness_single_element():
    """Single element data: no pairs to compare, variance_sum=0, fitness=0/1=0."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    varmax.start_eval()
    fit = varmax.calculate_success([42], 0, '')
    assert fit == 0.0


def test_EvalVarMaxFitness_error_returns_zero():
    """calculate_error should return 0."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    fit = varmax.calculate_error(Exception("err"), 0, '')
    assert fit == 0


def test_EvalVarMaxFitness_start_end_eval_lifecycle():
    """start_eval resets state, end_eval records heatmap and increments epoch."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    varmax = EvalVarMaxFitness(plot_data_recorder)

    varmax.start_eval()
    varmax.calculate_success([0, 10], 0, '')
    varmax.end_eval()

    plot_data_recorder.record_waveform_heatmap.assert_called_once()
    args = plot_data_recorder.record_waveform_heatmap.call_args
    assert args[0][0] == 0  # epoch 0

    # Second eval cycle
    varmax.start_eval()
    varmax.calculate_success([0, 20], 0, '')
    varmax.end_eval()

    assert plot_data_recorder.record_waveform_heatmap.call_count == 2
    args2 = plot_data_recorder.record_waveform_heatmap.call_args
    assert args2[0][0] == 1  # epoch 1
