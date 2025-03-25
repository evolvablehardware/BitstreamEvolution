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


