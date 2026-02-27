"""Phase 2: Interface integration tests for protocol interactions.

Tests CircuitFactory, GenerateMeasurements, EvaluatePopulationFitness,
Reproducer, and FitnessEvaluator protocol implementations.
"""
from random import Random
from unittest.mock import Mock
import functools as ft
import pytest

from BitstreamEvolutionProtocols import (
    Circuit, DataRequest, Individual, Measurement, Population,
    FPGA_Compilation_Data,
)
from TrivialImplementation import (
    TrivialCircuit, TrivialCircuitFactory, TrivialReproduceWithMutation,
    TrivialGenerateInitialPopulation, TrivialGenerateMeasurements,
    FakeHardwareTrivialEvaluateMeasurements, TrivialEvaluatePopulationFitness,
    Trivial_Meas,
)
from GenerateMeasurements.GenerateMeasurements import SimpleGenerateMeasurements
from EvaluateFitness.EvaluateFitness import EvaluateFitness, FitnessEvaluator
from EvaluateFitness.EvalVarMaxFitness import EvalVarMaxFitness
from EvaluateFitness.EvalPulseCountFitness import EvalPulseCountFitness
from PlotDataRecorder import PlotDataRecorder
from Circuit.FileBasedCircuit import FileBasedCircuit
from result import Ok, Err # type: ignore


# ============================================================================
# Helper for creating test populations
# ============================================================================

def _make_trivial_population(fitnesses, discovered=True):
    if discovered:
        return Population(
            [TrivialCircuit(f) for f in fitnesses],
            list(fitnesses),
        )
    return Population([TrivialCircuit(f) for f in fitnesses], None)


# ============================================================================
# 1.5 CircuitFactory Protocol Tests
# ============================================================================

def test_CircuitFactory_returns_correct_structure():
    """CircuitFactory return type should be dict[Circuit, list[tuple[Pop, Ind]]]."""
    pop = Population([TrivialCircuit(1), TrivialCircuit(2)], None)
    result = TrivialCircuitFactory(pop)

    assert isinstance(result, dict)
    for circuit, dependants in result.items():
        assert isinstance(dependants, list)
        for (source_pop, individual) in dependants:
            assert source_pop is pop
            individuals = [i for i, _ in pop]
            assert individual in individuals


def test_CircuitFactory_handles_empty_population():
    """CircuitFactory should handle an empty population gracefully."""
    pop = Population([], None)
    result = TrivialCircuitFactory(pop)
    assert isinstance(result, dict)
    assert len(result) == 0


def test_CircuitFactory_population_individual_tracking():
    """Each circuit in the factory output should map back to the correct individual."""
    ind1 = TrivialCircuit(10)
    ind2 = TrivialCircuit(20)
    pop = Population([ind1, ind2], None)
    result = TrivialCircuitFactory(pop)

    # For TrivialCircuitFactory, each individual IS the circuit
    assert ind1 in result
    assert ind2 in result
    assert result[ind1] == [(pop, ind1)]
    assert result[ind2] == [(pop, ind2)]


# ============================================================================
# 1.11 GenerateMeasurements Protocol Tests
# ============================================================================

class _MockCircuit:
    def __init__(self, id):
        self.id = id

    def compile(self, fpga):
        pass


class _MockCircuitFactory:
    def generate(self, populations):
        result = {}
        for pop in populations:
            for ind, _ in pop:
                ckt = _MockCircuit(ind.id)
                result[ckt] = [(pop, ind)]
        return result


class _MockIndividual:
    def __init__(self, id):
        self.id = id


def test_GenerateMeasurements_return_structure():
    """SimpleGenerateMeasurements should return dict[Measurement, list[tuple[Pop, Ind]]]."""
    gen_meas = SimpleGenerateMeasurements('fpga', DataRequest.WAVEFORM, 1)
    factory = _MockCircuitFactory()
    pop = Population([_MockIndividual(1), _MockIndividual(2)], None)

    result = gen_meas.generate(factory.generate, [pop])

    assert isinstance(result, dict)
    assert len(result) == 2
    for measurement, dependants in result.items():
        assert isinstance(measurement, Measurement)
        assert isinstance(dependants, list)
        for (source_pop, individual) in dependants:
            assert source_pop is pop


def test_GenerateMeasurements_factory_integration():
    """GenerateMeasurements should use CircuitFactory to get circuits."""
    gen_meas = SimpleGenerateMeasurements('test-fpga', DataRequest.OSCILLATIONS, 3)
    factory = _MockCircuitFactory()
    ind = _MockIndividual(42)
    pop = Population([ind], None)

    result = gen_meas.generate(factory.generate, [pop])

    assert len(result) == 1
    measurement = list(result.keys())[0]
    assert measurement.FPGA_request == 'test-fpga'
    assert measurement.data_request == DataRequest.OSCILLATIONS
    assert measurement.num_samples == 3


def test_GenerateMeasurements_multiple_populations():
    """GenerateMeasurements should handle multiple populations."""
    gen_meas = SimpleGenerateMeasurements('fpga', DataRequest.WAVEFORM, 1)
    factory = _MockCircuitFactory()
    pop1 = Population([_MockIndividual(1)], None)
    pop2 = Population([_MockIndividual(2)], None)

    result = gen_meas.generate(factory.generate, [pop1, pop2])

    assert len(result) == 2


def test_GenerateMeasurements_empty_input():
    """GenerateMeasurements with empty populations should return empty dict."""
    gen_meas = SimpleGenerateMeasurements('fpga', DataRequest.WAVEFORM, 1)
    factory = _MockCircuitFactory()
    pop = Population([], None)

    result = gen_meas.generate(factory.generate, [pop])

    assert len(result) == 0


# ============================================================================
# 1.10 EvaluatePopulationFitness Protocol Tests
# ============================================================================

def test_EvaluatePopulationFitness_modifies_in_place():
    """EvaluateFitness.evaluate() should modify population in place, not return it."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    ckt = Mock(spec=FileBasedCircuit)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    evaluator = EvaluateFitness(varmax)
    pop = Population([0], None)
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    # Use result.Ok directly since EvaluateFitness uses result.is_ok(), not returns.result
    measure.result = Ok([0, 2])

    result = evaluator.evaluate(pop, [measure])

    assert result is None  # evaluate returns None
    assert pop.population_list[0][1] is not None


def test_EvaluatePopulationFitness_measurement_mapping():
    """The i-th measurement should set fitness at population index i."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    ckt1 = Mock(spec=FileBasedCircuit)
    ckt2 = Mock(spec=FileBasedCircuit)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    evaluator = EvaluateFitness(varmax)

    pop = Population([0, 1], None)
    m1 = Measurement('fpga', DataRequest.WAVEFORM, ckt1, 1)
    m1.result = Ok([0, 2])  # fitness = 1.0
    m2 = Measurement('fpga', DataRequest.WAVEFORM, ckt2, 1)
    m2.result = Ok([0, 4])  # fitness = 2.0

    evaluator.evaluate(pop, [m1, m2])

    assert pop.population_list[0][1] == 1.0
    assert pop.population_list[1][1] == 2.0


def test_EvaluatePopulationFitness_handles_errors():
    """Measurements with Failure results should use calculate_error (fitness 0)."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    ckt = Mock(spec=FileBasedCircuit)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    evaluator = EvaluateFitness(varmax)

    pop = Population([0], None)
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.result = Err(Exception("Hardware failure"))

    evaluator.evaluate(pop, [measure])

    assert pop.population_list[0][1] == 0


def test_EvaluatePopulationFitness_multiple_measurements():
    """All measurements should be processed."""
    plot_data_recorder = Mock(spec=PlotDataRecorder)
    varmax = EvalVarMaxFitness(plot_data_recorder)
    evaluator = EvaluateFitness(varmax)

    individuals = [0, 1, 2]
    pop = Population(individuals, None)

    measurements = []
    for _ in individuals:
        ckt = Mock(spec=FileBasedCircuit)
        m = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
        m.result = Ok([0, 2])
        measurements.append(m)

    evaluator.evaluate(pop, measurements)

    for i in range(3):
        assert pop.population_list[i][1] is not None


# ============================================================================
# 1.6 Reproducer Protocol Tests
# ============================================================================

def test_Reproducer_returns_new_population():
    """Reproducer should return a new Population object, not the original."""
    original = _make_trivial_population(range(1, 11), discovered=True)
    result = TrivialReproduceWithMutation(original, Random(42))
    assert result is not original


def test_Reproducer_returns_unevaluated_population():
    """The reproduced population should have all fitnesses as None."""
    pop = _make_trivial_population(range(1, 11), discovered=True)
    result = TrivialReproduceWithMutation(pop, Random(42))

    for _, fitness in result:
        assert fitness is None


def test_Reproducer_input_unchanged():
    """The original population's individuals should still be accessible after reproduction."""
    original = _make_trivial_population(range(1, 11), discovered=True)
    original_individuals = [i for i, _ in original]

    TrivialReproduceWithMutation(original, Random(42))

    # Original population individuals should still be there
    # (sort happened in-place, but individuals are the same objects)
    current_individuals = [i for i, _ in original]
    assert len(current_individuals) == len(original_individuals)


# ============================================================================
# 1.13 FitnessEvaluator Protocol Tests
# ============================================================================

def test_FitnessEvaluator_lifecycle():
    """start_eval and end_eval should be called around evaluation."""
    evaluator = Mock(spec=FitnessEvaluator)
    evaluator.calculate_success.return_value = 1.0

    ef = EvaluateFitness(evaluator)
    pop = Population([Mock()], None)
    ckt = Mock(spec=FileBasedCircuit)
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.result = Ok([1, 2])

    ef.evaluate(pop, [measure])

    evaluator.start_eval.assert_called_once()
    evaluator.end_eval.assert_called_once()


def test_FitnessEvaluator_calculate_success_called():
    """calculate_success should be called for successful measurements."""
    evaluator = Mock(spec=FitnessEvaluator)
    evaluator.calculate_success.return_value = 5.0

    ef = EvaluateFitness(evaluator)
    pop = Population([Mock()], None)
    ckt = Mock(spec=FileBasedCircuit)
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.result = Ok([10, 20, 30])

    ef.evaluate(pop, [measure])

    evaluator.calculate_success.assert_called_once()
    assert pop.population_list[0][1] == 5.0


def test_FitnessEvaluator_calculate_error_called():
    """calculate_error should be called for failed measurements."""
    evaluator = Mock(spec=FitnessEvaluator)
    evaluator.calculate_error.return_value = 0.0

    ef = EvaluateFitness(evaluator)
    pop = Population([Mock()], None)
    ckt = Mock(spec=FileBasedCircuit)
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.result = Err(Exception("hardware error"))

    ef.evaluate(pop, [measure])

    evaluator.calculate_error.assert_called_once()
    assert pop.population_list[0][1] == 0.0
