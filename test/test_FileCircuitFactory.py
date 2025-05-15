from pathlib import Path
from random import Random
from unittest.mock import Mock
from Directories import Directories
from Logger import Logger
from Population.PopulationInitialization import FileBasedCircuitFactory, GenerateBitstreamPopulation, NoRandomizationStrategy, RandomizeBitstreamPostConstructionStrategy
import os

def test_file_based_circuit_factory():
    rand=Mock(spec=Random)
    logger = Mock(spec=Logger)
    directories = Directories(Path('test', 'out', 'asc'), Path('test', 'out', 'bin'), Path('test', 'out', 'data'))
    factory = FileBasedCircuitFactory(
        sz=10,
        logger=logger,
        directories=directories,
        routing_type='MOORE',
        accessed_columns=[14, 15, 24, 25, 40, 41])
    gen_bitstream_population = GenerateBitstreamPopulation(
        sz=10, 
        bitstream_sz=1728,
        post_construction_strategy=RandomizeBitstreamPostConstructionStrategy(),
        randomization_strategy=NoRandomizationStrategy(),
        mutation_prob=0.5,
        rand=rand)
    pop = gen_bitstream_population.generate()
    circuits = factory.create([pop])
    asc_count = count_files_in_directory(Path('test', 'out', 'asc'))
    assert asc_count == 10
    assert len(circuits) == 10
    for c in circuits:
        makeup = circuits[c]
        assert len(makeup) == 1
        tup = makeup[0]
        assert tup[0] == pop

def count_files_in_directory(directory_path):
    if not os.path.isdir(directory_path):
        return -1
    return len([name for name in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, name))])
count_files_in_directory.__test__ = False # type: ignore
