from src.BitstreamEvolutionProtocols import Population, Individual, Fitness, GenData,GenDataFactory
from dataclasses import dataclass
from typing import Optional
import pytest

class SimpleIndividual:
    def __init__(self):
        pass


def GenDataIncrementer(initialGenData:Optional[GenData], max_gen_num:int)->Optional[GenData]:
    if initialGenData is None:
        return GenData(generation_number=0)
    if initialGenData.generation_number < max_gen_num-1:
        return GenData(initialGenData.generation_number + 1)
    else:
        return None


def test_InstantiatesInitialInput():
    result = GenDataIncrementer(None,500)
    assert result is not None
    assert result.generation_number == 0

def test_AssertIncrements():
    input = GenData(54)
    result = GenDataIncrementer(input,500)
    assert result is not None
    assert result.generation_number == 55
    result = GenDataIncrementer(result,500)
    assert result is not None
    assert result.generation_number == 56

def test_EndsLoopCorrectly():
    input = GenData(499)
    result = GenDataIncrementer(input,500)
    assert result is None

