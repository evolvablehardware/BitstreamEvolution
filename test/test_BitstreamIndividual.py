from unittest.mock import Mock
from Individual.BitstreamIndividual import BitstreamIndividual
from random import Random

def test_randomize():
    rand = Mock(spec=Random)
    rand.randint.return_value = 0
    individual = BitstreamIndividual(100, rand, 0.5)
    individual.set_bitstream([True] * 100)
    individual.randomize()
    bitstream = individual.get_bitstream()
    for bit in bitstream:
        assert not bit

def test_mutate():
    rand = Mock(spec=Random)
    individual = BitstreamIndividual(100, rand, 0.5)
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
    individual1 = BitstreamIndividual(100, rand, 0.5)
    individual1.set_bitstream([True] * 100)

    individual2 = BitstreamIndividual(100, rand, 0.5)
    individual2.set_bitstream([False] * 100)

    individual1.crossover(individual2, 50)

    bitstream = individual1.get_bitstream()

    assert len(bitstream) == 100
    for i in range(50):
        assert bitstream[i]
    for i in range(50):
        assert not bitstream[i + 50]


# --- Additional BitstreamIndividual tests ---

def test_BitstreamIndividual_init_bitstream_size():
    """New individual should have bitstream of correct size, all False."""
    rand = Mock(spec=Random)
    ind = BitstreamIndividual(50, rand, 0.5)
    bitstream = ind.get_bitstream()
    assert len(bitstream) == 50
    assert all(b is False for b in bitstream)


def test_BitstreamIndividual_copy_from():
    """copy_from should deep copy the bitstream from another individual."""
    rand = Mock(spec=Random)
    ind1 = BitstreamIndividual(10, rand, 0.5)
    ind1.set_bitstream([True, False, True, False, True, False, True, False, True, False])

    ind2 = BitstreamIndividual(10, rand, 0.5)
    ind2.copy_from(ind1)

    assert ind2.get_bitstream() == [True, False, True, False, True, False, True, False, True, False]

    # Verify it's a deep copy - modifying one shouldn't affect the other
    ind1.set_bitstream([False] * 10)
    assert ind2.get_bitstream() == [True, False, True, False, True, False, True, False, True, False]


def test_BitstreamIndividual_crossover_at_zero():
    """Crossover at point 0 should take all bits from parent."""
    rand = Mock(spec=Random)
    ind1 = BitstreamIndividual(10, rand, 0.5)
    ind1.set_bitstream([True] * 10)

    ind2 = BitstreamIndividual(10, rand, 0.5)
    ind2.set_bitstream([False] * 10)

    ind1.crossover(ind2, 0)

    bitstream = ind1.get_bitstream()
    assert all(b is False for b in bitstream)


def test_BitstreamIndividual_crossover_at_end():
    """Crossover at the end should keep all of self's bits."""
    rand = Mock(spec=Random)
    ind1 = BitstreamIndividual(10, rand, 0.5)
    ind1.set_bitstream([True] * 10)

    ind2 = BitstreamIndividual(10, rand, 0.5)
    ind2.set_bitstream([False] * 10)

    ind1.crossover(ind2, 10)

    bitstream = ind1.get_bitstream()
    assert all(b is True for b in bitstream)
