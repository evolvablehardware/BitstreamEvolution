from random import Random
from unittest.mock import Mock

from Population.PopulationInitialization import GenerateBitstreamPopulation, MutateOncePostConstructionStrategy, NoPostConstructionStrategy, NoRandomizationStrategy, RandomizeBitstreamPostConstructionStrategy

def test_generate_no_strategies():
    rand = Mock(spec=Random)
    gen_bitstream_population = GenerateBitstreamPopulation(
        sz=10, 
        bitstream_sz=100,
        post_construction_strategy=NoPostConstructionStrategy(),
        randomization_strategy=NoRandomizationStrategy(),
        mutation_prob=0.5,
        rand=rand)
    pop = gen_bitstream_population.generate()
    assert len(pop) == 10
    for (i, f) in pop:
        bs = i.get_bitstream() # type: ignore
        for bit in bs:
            assert not bit

def test_generate_randomize_strategy():
    rand = Mock(spec=Random)
    rand.randint.return_value = 1
    gen_bitstream_population = GenerateBitstreamPopulation(
        sz=10, 
        bitstream_sz=100,
        post_construction_strategy=RandomizeBitstreamPostConstructionStrategy(),
        randomization_strategy=NoRandomizationStrategy(),
        mutation_prob=0.5,
        rand=rand)
    pop = gen_bitstream_population.generate()
    assert len(pop) == 10
    for (i, f) in pop:
        bs = i.get_bitstream() # type: ignore
        for bit in bs:
            assert bit

def test_generate_mutate_once_strategy():
    rand = Mock(spec=Random)
    rand.uniform.return_value = 0
    gen_bitstream_population = GenerateBitstreamPopulation(
        sz=10, 
        bitstream_sz=100,
        post_construction_strategy=MutateOncePostConstructionStrategy(),
        randomization_strategy=NoRandomizationStrategy(),
        mutation_prob=0.5,
        rand=rand)
    pop = gen_bitstream_population.generate()
    assert len(pop) == 10
    for (i, f) in pop:
        bs = i.get_bitstream() # type: ignore
        for bit in bs:
            assert bit
