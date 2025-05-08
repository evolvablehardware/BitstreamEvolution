from unittest.mock import Mock
from Individual.BitstreamIndividual import BitstreamIndividual
from random import Random

def test_randomize():
    rand = Mock(spec=Random)
    rand.randint.return_value = 0
    individual = BitstreamIndividual(rand, 0.5)
    individual.set_bitstream([True] * 100)
    individual.randomize()
    bitstream = individual.get_bitstream()
    for bit in bitstream:
        assert not bit

def test_mutate():
    rand = Mock(spec=Random)
    individual = BitstreamIndividual(rand, 0.5)
    individual.set_bitstream([True] * 100)
    
    rand.uniform.return_value = 0
    individual.mutate()
    bitstream = individual.get_bitstream()
    for bit in bitstream:
        assert not bit # all mutated

    rand.uniform.return_value = 1
    individual.mutate()
    bitstream = individual.get_bitstream()
    for bit in bitstream:
        assert not bit # all not mutated; same as before

def test_crossover():
    rand = Mock(spec=Random)
    individual1 = BitstreamIndividual(rand, 0.5)
    individual1.set_bitstream([True] * 100)

    individual2 = BitstreamIndividual(rand, 0.5)
    individual2.set_bitstream([False] * 100)

    individual1.crossover(individual2, 50)

    bitstream = individual1.get_bitstream()

    assert len(bitstream) == 100
    for i in range(50):
        assert bitstream[i]
    for i in range(50):
        assert not bitstream[i + 50]
