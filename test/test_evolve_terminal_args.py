import argparse
from subprocess import run
import os
import pytest

#NOTE: This runs expecting to start in the BitstreamEvolution parent directory

def test_terminal_connects():
    program = run("ls".split(" "),capture_output=True)
    assert program.returncode == 0
    assert program.stdout is not None

def test_evolve_runs_as_test_without_error():
    program = run("python3 src/evolve.py --test".split(" "),capture_output=True)
    empty = [None,'',b'']
    assert program.returncode == 0
    assert program.stderr in empty
    assert program.stdout not in empty
    