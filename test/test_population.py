from unittest.mock import Mock

from BitstreamEvolutionProtocols import Population


def test_set_fitness():
    group = []
    designated_individual = None
    designated_idx = 5
    for i in range(10):
        individual = Mock()
        if i == designated_idx:
            designated_individual = individual
        group.append(individual)
    
    population = Population(group)
    population.set_fitness(designated_individual, 100)
    it = iter(population)
    for (individual, fitness) in it:
        if individual == designated_individual:
            assert fitness == 100
        else:
            assert fitness is None

def test_sort():
    group = []
    fits = [2, 3, 8, 1, 5, 0, 6, 7, 4, 9]
    for _ in range(10):
        individual = Mock()
        group.append(individual)
    population = Population(group.copy(), fits.copy())
    population.sort(lambda x: x, False)
    it = iter(population)
    fits.sort()
    for (i, (_, fitness)) in enumerate(it):
        assert fits[i] == fitness

def test_set_fitness_of_unevaluated_individuals():
    group = []
    designated_idx = 5
    fits = [1, 2, 3, 4, 5, None, 6, 7, 8]
    for i in range(len(fits)):
        individual = Mock()
        group.append(individual)
    
    population = Population(group, fits.copy())

    population.set_fitness_of_unevaluated_individuals(100)
    fits[designated_idx] = 100
    it = iter(population)
    for (i, (_, fitness)) in enumerate(it):
        assert fits[i] == fitness
