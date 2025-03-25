from dataclasses import dataclass
from typing import Protocol, Callable, Iterable, Optional, Any, TypeVar
from abc import ABC
from pathlib import Path
from result import Result,Ok
from enum import Enum, auto
import asyncio

class GenData(Protocol):
    """
    The most basic Class Protocol for Generation Data Objects. This simply requires a generation_number.
    """
    generation_number: int

# This is the "Evolution Generation Info Incrementer" in the diagram. It is a function.
class GenDataFactory(Protocol):
    """
    The most basic Function Protocol that converts the Generation Data 
    from the previous iteration to the one for the next generation. 
    It also constructs the initial GenData object (gen_data is None) 
    and determines when the final generation occours (returns None).
    """
    def __call__(self,gen_data:GenData|None,*args:Any, **kwds:Any) -> GenData|None: ...
    # If want to say it can't have any other positional only arguments, use:
    #def __call__(self,gen_data:GenData|None,/, **kwds:Any) -> GenData|None: ...


# TODO: Replace this with Self if update to python 3.12
F = TypeVar('F',bound='Fitness')
# Want this to match the specific instance of the thing implementing Fitness it was matched with,
#   not anything that matches the protocol, so this may not be exactly correct.

class Fitness(Protocol):
    """
    The most basic Class Protocol that contains the result of an evaluation, allowing you to
    compare the resulting fitness. This should match most numeric types (i.e. int, float) 
    but allows you to do something more complex as desired.
    """
    def __lt__(self: F, o: F)->bool: ...
    def __gt__(self: F, o: F)->bool: ...
    def __eq__(self: F, o: F)->bool: ...
    def __le__(self: F, o: F)->bool: ...
    def __ge__(self: F, o: F)->bool: ...

class Individual(Protocol):
    """
    The most basic Class Protocol for creating the Individuals that evolution will act upon.
    This specifies basically nothing.
    """
    ...

class FPGA_Model(Enum):
    "All of the FPGA models that any part of our code supports"
    ICE40 = auto()          # Check

# This class may even be able to have somewhat of a universal application for for particular FPGA models.
class FPGA_Compilation_Data(Protocol):
    "This contains all data needed to compile data for a particular FPGA."
    model:FPGA_Model
    "The id for the particular FPGA (Maybe?)"

class Circuit(Protocol):
    """
    The most basic Class Protocol for creating the Circuits that are evaluated on physical FPGAs.
    This may or may not be an Individual based on what the Individual represents.
    It will if the Individual represents a circuit in its entirety.
    It will not if you are simultaniously evolving multiple sub-sections that need to be combined to make the circuit to be evaluated.
    """
    def compile(self, fpga: FPGA_Compilation_Data, working_dir:Path) -> Result[Path,Exception]:
        """
        This looks at the fpga and compiles the circuit for it if it can. 
        If it can it does all of its work in the working_dir and returns with Ok(Path) for the path to the file/directory containing this data.
        If it cannot, it should return an exception Err(Exception) explaining why it failed.
        This should never raise an Exception, only return one as described.
        """
        ...

class CircuitFactory(Protocol):
    """
    The most basic Function Protocol for Turning Individuals into Circuits in whatever way best fits your application.
    How the circuit is built should be fully specified here, and any unique roles the individuals have should be specified here;
    however, how these individuals are selected and matched to roles is not.
    """
    def __call__(self, *args:Individual, **kwds:Any)->Circuit:
        "This takes one or many Individuals and constructs a Circuit from it as requested."
        ...

class Population:
    """
    This is the Population object used to hold individuals and their fitnesses durring evolution. 
    It starts out with its full list of individuals, and optionally fitnesses.
    No individuals in the list may be duplicates. (determined using == )
    If there is no fitness it is None. 
    Fitnesses can be added to individuals in the population as desired, and once all individuals are added, the population can be sorted. 
    The Population can also be itterated through. (iter() -then-> next())
    """
    # May want specific type variables.
    def __init__(self,individuals: Iterable[Individual], fitnesses:Optional[Iterable[Fitness|None]]=None):
        "Can raise ValueError if Individuals are not unique."
        ind = list(individuals)

        if len(set(ind)) != len(ind):
            raise ValueError("There are duplicate individuals in this population. Each Individual in a population must be a unique object.")

        fit = list(fitnesses) if (fitnesses is not None) and (len(fitnesses) == len(ind)) else [None]*len(ind)

        self.population_list:list[tuple[Individual,Optional[Fitness]]] = list(zip(ind,fit))
        # = [(Individual, Fitness), (Individual2, Fitness2), ...]

    def __iter__(self)->list[tuple[Individual,Optional[Fitness]]]:
        # call iter() to get iterator, then next()
        # If wanted to be safe, return a copy that can't change
        return self.population_list
    
    def set_fitness_by_index(self,index:int,fitness:Fitness)->None:
        self.population_list[index] = (self.population_list[index][0],fitness)

    def set_fitness(self, individual:Individual, fitness:Fitness)->None:
        "This can return value error if provided individual is not in the population."
        for i,if_tup in self.population_list:
            if if_tup[0] == individual:
                self.set_fitness_by_index(index=i,fitness=fitness)
                return
        raise ValueError(f"Cound not find provided Individual in the population. Individual: {individual}")
    
    def set_fitness_of_unevaluated_individuals(self,default_fitness:Fitness)->None:
        for i,if_tup in self.population_list:
            if if_tup[1] is None:
                self.set_fitness_by_index(index=i,fitness=default_fitness)
                
    def sort(self,key:Callable[[Fitness],Fitness],reverse:bool)->None:
        "Operates on the Population fitness function like the standard sort for a list. May Raise TypeError if population not fully evaluated."
        try:
            self.population_list.sort(
                key=lambda if_tup: key(if_tup[1]),
                reverse= reverse
            )
        except TypeError:
            raise TypeError(f"Population does not have all individual's fitnesses fully specified. {sum([t[1] is None for t in self.population_list])} individuals did not have a fitness assigned.")

def Reproduce(Protocol):
    def __call__(self,population:Population)->Population: ...

def Generate_Initial_Population(Protocol):
    def __call__(self)->Population: ...

def Measurement(Protocol):
    "All measurement data, this could even be a class potentially"
    FPGA_request:str
    data_request:Enum
    circuit:Circuit
    FPGA_used:Optional[str]
    result = Result[Any,Exception] # The Any should be the measurement data, which we may want to standardize at some point

def EvaluateFitness(Protocol):
    "Fully Evaluates a Population"
    def __call__(self,population:Population,measurements:list[Measurement])->Population: ...

def GenerateMeasurements(Protocol):
    "Generate the measurements to take for the given population"
    def __call__(self,population:Population)->list[Measurement]: ...

def Hardware(Protocol):
    "Used to Evaluate Measurements. Compile hardware would be responsible for compiling the Circuit in the Measurement object passed to it in request_measurement()."
    #Has FPGAs
    #Has Active Measurements being evaluated
    #Has Pending MEasurements to be evaluated
    async def request_measurement(measurement:Measurement)->Measurement: ... #make this an async function
    def get_available_FPGAs()->list[str]: ... # This could be a list of ids, or some sort of FPGA object with the UUID included and other relevant data.

# Example usage
if False:
    #https://www.pythontutorial.net/python-concurrency/python-async-await/
    async def evalMeas(Measurements:list[Measurement]):
        hw = Hardware(...)
        for m in Measurements:
            await Hardware.request_measurement(m)
    
    asyncio.run(evalMeas(...))
    
    


## Interesting Experiment to consider if update python version;


#from mypy_extensions import Arg,VarArg,KwArg

# "type" requires python 3.12+
#type GenDataFactory = Callable[[Arg(GenData|None),VarArg(Any),KwArg(Any)],GenData|None]
