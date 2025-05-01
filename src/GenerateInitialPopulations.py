# Refactoring code in Circuit Population line 244
from pathlib import Path
from random import Random

class GenerateInitialPopulation:
    def __init__(self, circuit_directory:Path, random:Random):
        self.circuit_directory:Path = circuit_directory
        self.random:Random          = random

    def FromExistingPopulation():
        pass
        #see line 302 in Circuit Population
        #also see line 317

    def Randomly():

        pass
        #see line 312 in Circuit Population
    
    def CloneSeedMutate():

        pass
        #see line 314 in Circuit Population

GenerateInitialPopulation(
    ...
    ).Randomly()
GenerateInitialPopulation(   ...    ).Randomly

gen_init_pop = GenerateInitialPopulation(...)
gen_init_pop.Randomly

gen_init_func = GenerateInitialPopulation(...).Randomly



class GenerateInitialPopulationFromExistingPopulation:
    def __init__(self, circuit_directory:Path, random:Random):
        self.circuit_directory:Path = circuit_directory
        self.random:Random          = random

    def generate():
        pass
        #see line 302 in Circuit Population
        #also see line 317

class GenerateInitialPopulationRandomly:
    def __init__(self, circuit_directory:Path, random:Random):
        self.circuit_directory:Path = circuit_directory
        self.random:Random          = random

    def generate():

        pass
        #see line 312 in Circuit Population

class GenerateInitialPopulationCloneSeedMutate: 
    def __init__(self, circuit_directory:Path, random:Random):
        self.circuit_directory:Path = circuit_directory
        self.random:Random          = random
    def generate():

        pass
        #see line 314 in Circuit Population