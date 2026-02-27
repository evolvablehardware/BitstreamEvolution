from unittest.mock import Mock
import pytest

from BitstreamEvolutionProtocols import Population


# --- Fixtures ---

@pytest.fixture
def mock_individuals():
    """Create a list of 10 unique mock individuals."""
    return [Mock() for _ in range(10)]


# --- Tests for set_fitness ---

def test_set_fitness_updates_only_specified_individual(mock_individuals):
    """Setting fitness on one individual should not affect others.

    Validates Population.set_fitness() from BitstreamEvolutionProtocols.py:145-150.
    """
    target_individual = mock_individuals[5]
    population = Population(mock_individuals)

    population.set_fitness(target_individual, 100)

    for individual, fitness in population:
        if individual == target_individual:
            assert fitness == 100, "Target individual should have fitness 100"
        else:
            assert fitness is None, "Other individuals should remain unevaluated"


# --- Tests for sort ---

def test_sort_orders_by_fitness_ascending(mock_individuals):
    """Population.sort() should order individuals by fitness.

    Validates Population.sort() from BitstreamEvolutionProtocols.py:158-166.
    """
    fitnesses = [2, 3, 8, 1, 5, 0, 6, 7, 4, 9]
    population = Population(mock_individuals, fitnesses.copy())

    population.sort(key=lambda x: x, reverse=False)

    expected_order = sorted(fitnesses)
    actual_fitnesses = [fitness for _, fitness in population]
    assert actual_fitnesses == expected_order


# --- Tests for set_fitness_of_unevaluated_individuals ---

def test_set_fitness_of_unevaluated_individuals_fills_none_values():
    """Unevaluated individuals (fitness=None) should receive the default fitness.

    Validates Population.set_fitness_of_unevaluated_individuals()
    from BitstreamEvolutionProtocols.py:153-156.
    """
    individuals = [Mock() for _ in range(9)]
    fitnesses = [1, 2, 3, 4, 5, None, 6, 7, 8]
    population = Population(individuals, fitnesses.copy())

    population.set_fitness_of_unevaluated_individuals(default_fitness=100)

    expected_fitnesses = [1, 2, 3, 4, 5, 100, 6, 7, 8]
    actual_fitnesses = [fitness for _, fitness in population]
    assert actual_fitnesses == expected_fitnesses


# --- Tests for uniqueness constraint ---

def test_Population_rejects_duplicate_individuals():
    """Population should raise ValueError when given duplicate individuals.

    Validates the uniqueness constraint from BitstreamEvolutionProtocols.py:122-126.
    Each Individual in a population must be a unique object (determined using ==).
    """
    individual = Mock()

    with pytest.raises(ValueError, match="duplicate"):
        Population([individual, individual], None)


# --- Tests for set_fitness ValueError ---

def test_Population_set_fitness_raises_on_missing_individual():
    """set_fitness should raise ValueError when individual is not in the population."""
    pop = Population([Mock()], None)
    missing = Mock()
    with pytest.raises(ValueError):
        pop.set_fitness(missing, 1.0)


# --- Tests for sort with unevaluated fitness ---

def test_Population_sort_raises_on_unevaluated():
    """sort() should raise TypeError when any fitness is None."""
    pop = Population([Mock(), Mock()], [1.0, None])
    with pytest.raises(TypeError):
        pop.sort(lambda x: x, False)


# --- Tests for iteration ---

def test_Population_iteration_yields_tuples():
    """__iter__ should yield (Individual, Fitness|None) tuples."""
    ind = Mock()
    pop = Population([ind], [1.0])
    for item in pop:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert item[0] is ind
        assert item[1] == 1.0


# --- Tests for __len__ ---

def test_Population_length():
    """__len__ should return the correct count of individuals."""
    individuals = [Mock() for _ in range(5)]
    pop = Population(individuals, None)
    assert len(pop) == 5


# --- Tests for fitness length mismatch ---

def test_Population_fitness_length_mismatch():
    """When fitness list length doesn't match individuals, all default to None."""
    individuals = [Mock() for _ in range(3)]
    pop = Population(individuals, [1.0, 2.0])  # length mismatch
    actual_fitnesses = [f for _, f in pop]
    assert actual_fitnesses == [None, None, None]
