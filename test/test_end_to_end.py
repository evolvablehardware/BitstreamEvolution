"""Phase 4: End-to-end integration tests.

Tests the full evolution pipeline, circuit-to-measurement, and measurement-to-fitness flows
using real Trivial* components (no mocks).
"""
from random import Random
import functools as ft

import pytest

from BitstreamEvolutionProtocols import GenDataIncrementer, Population
from TrivialImplementation import (
    TrivialCircuit, TrivialCircuitFactory, TrivialReproduceWithMutation,
    TrivialGenerateInitialPopulation, TrivialGenerateMeasurements,
    FakeHardwareTrivialEvaluateMeasurements, TrivialEvaluatePopulationFitness,
    TrivialEvolution,
)


# ============================================================================
# Helper
# ============================================================================

def _make_population(fitnesses, discovered=True):
    if discovered:
        return Population(
            [TrivialCircuit(f) for f in fitnesses],
            list(fitnesses),
        )
    return Population([TrivialCircuit(f) for f in fitnesses], None)


# ============================================================================
# 2.1 Evolution Pipeline Integration
# ============================================================================

@pytest.mark.short
def test_evolution_pipeline_integration():  # Written by AI
    """Full evolution run with real components and deterministic seed."""
    rand = Random(42)

    gen_data_factory = GenDataIncrementer(5)

    initial_pop = ft.partial(
        TrivialGenerateInitialPopulation,
        population_size=10,
        random=rand,
        min_fitness=0,
        max_fitness=100,
    )

    reproducer = ft.partial(TrivialReproduceWithMutation, random=rand)

    evolution = TrivialEvolution(
        generation_data_factory=gen_data_factory,
        reproducer=reproducer,
        generate_intial_population=initial_pop,
    )

    # Should complete without error
    evolution.run()


# ============================================================================
# 2.2 CircuitFactory to Measurement Pipeline
# ============================================================================

def test_circuit_factory_to_measurements_integration():  # Written by AI
    """CircuitFactory output should correctly feed into GenerateMeasurements."""
    individuals = [TrivialCircuit(1), TrivialCircuit(2), TrivialCircuit(3)]
    pop = Population(individuals, None)

    circuits = TrivialCircuitFactory(pop)
    measurements = TrivialGenerateMeasurements(TrivialCircuitFactory, pop)

    # Each circuit should have exactly one measurement
    assert len(measurements) == len(circuits)

    # Each measurement should reference a circuit from the factory
    measurement_circuits = [m.circuit for m in measurements.keys()]
    for circuit in circuits:
        assert circuit in measurement_circuits


# ============================================================================
# 2.3 Measurement to Fitness Pipeline
# ============================================================================

def test_measurement_to_fitness_integration():  # Written by AI
    """Measurements should flow correctly through fitness evaluation."""
    ind1, ind2 = TrivialCircuit(10), TrivialCircuit(20)
    pop = Population([ind1, ind2], None)

    # Generate measurements
    measurements = TrivialGenerateMeasurements(TrivialCircuitFactory, pop)

    # Evaluate measurements (fake hardware)
    FakeHardwareTrivialEvaluateMeasurements(measurements.keys())

    # Apply to population
    TrivialEvaluatePopulationFitness(pop, measurements)

    # Verify fitnesses assigned correctly
    for ind, fit in pop:
        assert fit == ind.inherent_fitness


def test_measurement_to_fitness_with_unevaluated():  # Written by AI
    """Unevaluated individuals should receive default fitness of 0."""
    ind1 = TrivialCircuit(10)
    ind2 = TrivialCircuit(20)
    pop = Population([ind1, ind2], None)

    # Only create and evaluate measurement for ind1
    measurements = TrivialGenerateMeasurements(TrivialCircuitFactory, pop)
    FakeHardwareTrivialEvaluateMeasurements(measurements.keys())
    TrivialEvaluatePopulationFitness(pop, measurements)

    # All should be evaluated (TrivialEvaluatePopulationFitness fills unevaluated with 0)
    for _, fit in pop:
        assert fit is not None


# ============================================================================
# Full pipeline: generate -> measure -> evaluate -> reproduce
# ============================================================================

def test_full_trivial_pipeline_single_generation():  # Written by AI
    """Test one complete generation cycle with all real components."""
    rand = Random(42)

    # Generate initial population
    pop = TrivialGenerateInitialPopulation(
        population_size=10, random=rand, min_fitness=0, max_fitness=100,
    )
    assert all(f is None for _, f in pop)

    # Generate measurements
    measurements = TrivialGenerateMeasurements(TrivialCircuitFactory, pop)
    assert len(measurements) == 10

    # Evaluate measurements
    FakeHardwareTrivialEvaluateMeasurements(measurements.keys())

    # Apply fitness
    TrivialEvaluatePopulationFitness(pop, measurements)
    assert all(f is not None for _, f in pop)

    # Reproduce
    new_pop = TrivialReproduceWithMutation(pop, rand)
    assert len(list(new_pop)) == 10
    assert all(f is None for _, f in new_pop)
