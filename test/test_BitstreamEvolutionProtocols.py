from src.BitstreamEvolutionProtocols import Population, Individual, Fitness, GenData, GenDataFactory, GenDataIncrementer
from dataclasses import dataclass
from typing import Optional
from unittest.mock import Mock
import pytest # type: ignore


def test_GenDataIncrementer_InstantiatesInput():
    inc = GenDataIncrementer(200)
    result = inc(None)
    assert result is not None
    assert result.generation_number == 0

@pytest.mark.parametrize(
        "pre_increment,post_increment",
        [(  0,   1),
         (  1,   2),
         (  2,   3),
         (  3,   4),
         ( 10,  11), 
         ( 47,  48),
         ( 75,  76), 
         ( 99, 100), 
         (300, 301), 
         (498, 499),
         ( -1,   0), #Specify how it should handle edge case
         (-30, -29)
        ]
)
def test_GenDataIncrementer_Increments(pre_increment, post_increment):
    input = GenData(54)
    inc = GenDataIncrementer(500)
    result = inc(input)
    assert result is not None
    assert result.generation_number == 55
    result = inc(result)
    assert result is not None
    assert result.generation_number == 56

def test_GenDataIncrementer_EndsLoopCorrectly():
    input = GenData(499)
    inc = GenDataIncrementer(500)
    result = inc(input)
    assert result is None

def test_GenDataIncrementer_EndsLoop_IfExceedsMaxGenNumber():
    assert GenDataIncrementer(500)(GenData(500)) is None, "Failed to end loop when Gen Data (500) exceeded max_gen_num (500)"
    assert GenDataIncrementer(500)(GenData(501)) is None, "Failed to end loop when Gen Data (501) exceeded max_gen_num (500)"
    assert GenDataIncrementer(500)(GenData(600)) is None, "Failed to end loop when Gen Data (600) exceeded max_gen_num (500)"
    assert GenDataIncrementer(500)(GenData(999)) is None, "Failed to end loop when Gen Data (999) exceeded max_gen_num (500)"

    assert GenDataIncrementer(30)(GenData(30)) is None,   "Failed to end loop when Gen Data  (30) exceeded max_gen_num  (30)"
    assert GenDataIncrementer(30)(GenData(490)) is None,  "Failed to end loop when Gen Data (490) exceeded max_gen_num  (30)"

    assert GenDataIncrementer(709)(GenData(709)) is None, "Failed to end loop when Gen Data (709) exceeded max_gen_num (709)"
    assert GenDataIncrementer(709)(GenData(999)) is None, "Failed to end loop when Gen Data (999) exceeded max_gen_num (709)"


@pytest.mark.parametrize(
        "max_gen_num",
        [(50),(500),(609),(920)]
)
def test_GenDataIncrementer_PerformsEntireLoopCorrectly(max_gen_num):
    input = None
    inc = GenDataIncrementer(max_gen_num)
    for i in range(max_gen_num):
        input = inc(input)
        assert input is not None, f"Error, failed to increment to {i}, instead was None"
        assert input.generation_number == i, f"Error, failed to increment to {i}, instead was {input.generation_number}"
    input = inc(input)
    assert input is None, f"Failed to correctly end the loop. Returned: {input}"
    

"""
Markers for Pytest:

Markers can be applied to tests so only particular tests are run when you run pytest. 
We have a custom addon that adds "long, short, and immediate" markers as specified in `pyproject.toml`.
All tests automatically have one of these markers applied if they have none, in this case 'immediate'.
This is also configured in `pyproject.toml` and more groups can be added.

You can see what each marker means with the command line by writing the command:
    `pytest --markers`
You can run only tests with particular markers (in this case 'long') by running:
    `pytest -m "long"`
You can run tests with both markers applied: 
    `pytest -m "long and short"`
You can run tests with either marker applied:
    `pytest -m "long or short"`

You can apply a marker to a test (in this case 'long') by typing : `@pytest.mark.long` above the test function you want to mark.
"""

@pytest.mark.long
def test_LongTest():
    "In the testing pipeline we need at least one 'long' test or the code running tests on github will break. This ensures we have that long test."
    pass


# --- GenDataIncrementer edge cases ---

def test_GenDataIncrementer_ZeroGenerations():
    """max_gen_num=0 should return gen 0 on first call, then None."""
    inc = GenDataIncrementer(0)
    result = inc(None)
    assert result is not None
    assert result.generation_number == 0
    result = inc(result)
    assert result is None


def test_GenDataIncrementer_SingleGeneration():
    """max_gen_num=1 should return gen 0, then gen 1 is not reached (returns None after gen 0)."""
    inc = GenDataIncrementer(1)
    result = inc(None)
    assert result is not None
    assert result.generation_number == 0
    result = inc(result)
    assert result is None


def test_GenDataIncrementer_return_type_validation():
    """GenDataIncrementer should return GenData or None."""
    inc = GenDataIncrementer(5)
    result = inc(None)
    assert isinstance(result, GenData)
    # Run to completion
    for _ in range(4):
        result = inc(result)
    assert result is not None
    result = inc(result)
    assert result is None


# --- Fitness protocol tests ---

def test_float_satisfies_Fitness_protocol():
    """float should work as Fitness type in Population sort."""
    pop = Population([Mock(), Mock()], [1.5, 2.5])
    pop.sort(lambda x: x, reverse=True)
    fitnesses = [f for _, f in pop]
    assert fitnesses[0] == 2.5
    assert fitnesses[1] == 1.5


def test_int_satisfies_Fitness_protocol():
    """int should work as Fitness type in Population sort."""
    pop = Population([Mock(), Mock()], [1, 2])
    pop.sort(lambda x: x, reverse=True)
    fitnesses = [f for _, f in pop]
    assert fitnesses[0] == 2
    assert fitnesses[1] == 1


def test_custom_Fitness_class():
    """A custom class with comparison operators should work as Fitness."""

    class CustomFitness:
        def __init__(self, val):
            self.val = val

        def __lt__(self, other):
            return self.val < other.val

        def __gt__(self, other):
            return self.val > other.val

        def __eq__(self, other):
            return self.val == other.val

        def __le__(self, other):
            return self.val <= other.val

        def __ge__(self, other):
            return self.val >= other.val

    f1 = CustomFitness(10)
    f2 = CustomFitness(20)
    pop = Population([Mock(), Mock()], [f1, f2])
    pop.sort(lambda x: x, reverse=True)
    fitnesses = [f for _, f in pop]
    assert fitnesses[0].val == 20
    assert fitnesses[1].val == 10