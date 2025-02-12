"""
Initial Design Ideas
--------------------

Looking at this example code, it seems ideal to only have Hardware, Individual, and Evolution (Maybe) actually be classes, have a couple of dataclasses, and the rest just be functions.

.. important::
    It seems like adopting a more functional-programming based architecture might be ideal as most of the classes just had one function of any significance.
    Maybe we could use __call__ or something to make classes functions if that is nicer syntax.

    Also, functools.partial() would be convenient for a fair number of these situations.

    You can also assign .verify() methods to functions. 

"""

from result import Ok, Err, Result, is_ok, is_err
from dataclasses import dataclass

class Individual:
    """
    This class holds all relevant for a particular individual.

    This is basically "Circuit" but I wanted to make the name more abstract.
    """


class HardwareData:
    """
    This class stores the data resulting from a test performed, and is specified and acted upon by the EvaluateFitness function used.

    This is likely specified by what the hardware is capable of doing and matches protocols specified EvaluateFitness.
    """



class Hardware:
    """
    This class stores all the necessary information to initialize hardware, read from it, and write to it. 
    
    It may be a good idea to pass this to the fitness evaluation function or something similar. 
    This must also have a function that is called when starting evolution to connect to the hardware, make sure it is all accessible, and even upload scripts to the hardware.
    """
    def run_fitness_test(self,individual:Individual)-> tuple[Individual,Result[HardwareData,Exception]]:
        "This runs the fitness test on the hardware and return a result either with the relevant data if successful or the exception thrown if failed."
        return (Individual(),Ok(HardwareData()))



class Fitness:
    """
    This class contains all information about the evaluated fitness of an individual. 

    This class should also implement >, <, >=, <=, == dunder methods.
    """





class FitnessEvaluator:
    """
    This class specifies how you will evaluate fitness. It will be handed a population and then perform a fitness evaluation on all members of the population.

    This will need to have some connection to the hardware of some nature to enable it to evaluate fitness on hardware with a considerable deal of abstraction.

    .. attention::
        This could also poetntially be a function that is partially configured functools.partial() on initialization and called whenever, poetentially with the hardware unspecified so it can be provided in the evolution class with functools.partial as well.
    """
    def __init__(self, hardware:Hardware)->None:
        "This sets up the hardware and allows any parameters of fitness to be changed."
        pass

    def evaluate_fitness(self,population:tuple[Individual]) -> tuple[ tuple[Individual, Result[Fitness,Exception] ] ]:
        "This gets a population and outputs the fitness evaluation it performed using the hardware."
        return ((Individual(),Ok(Fitness())),)

class Mutator:
    """
    This takes in a population and mutates it.
    """

class Selector:
    """
    This class takes an evaluated population as input and outputs a new unevaluated population.

    This, like the Evaluated Fitness, also has an opportunity to implemented as a function.
    """
    def select(self,evaluated_population:tuple[ tuple[Individual, Result[Fitness,Exception] ] ])->dict[str,tuple[ tuple[Individual, Result[Fitness,Exception] ] ]]:
        "Splits a single populations into smaller populations that can be acted on."
        return {"":((Individual(),Ok(Fitness())),)}

class Reproducer:
    """
    This gets an evaluated population from the selector and it creates a new population from the population provided.

    This may be implenented to maintain the same population size or change it and configured for whatever is desired.
    """

class ReproducePopulation:
    """
    This class gets an evaluated populatoin and outputs a new unevaluated population, after both selection and mutation.
    """
    def reproduce(self,select:Selector,final_muatator:Mutator,
                  selected_mutator:dict[str,Mutator],selected_reproducer:dict[str,Reproducer],
                  evaluated_population: tuple[ tuple[Individual, Result[Fitness,Exception] ] ]
                  ) ->tuple[Individual]:
        return (Individual(),)

class EvolutionRunner:
    """
    Runs the Evolution

    The initialization of the evolution runner specifies exactly what should be done in the process of evolution.
    Then, this object can be manipulated to perform high-level control of the evolution process, basically orchestrating the entire flowchart
    for the initial implementation.

    All logging should be performed by the Logger class and done individually, as the python Logger class can easily handle the difficulty of combining these logs.
    
    """
    def __init__(self,hardware:Hardware,fitness_evaluator:FitnessEvaluator,reproducer:ReproducePopulation)->None:
        """
        Stores the configuration and general process of evolution, then performs it when requested.

        Parameters
        ----------
        hardware: Hardware
            name thing
        """
        pass

    def verify(self)->bool:
        "Verify all parts of the evolution object are designed to work together"
        return True

    def evolve(self):
        "Performs evolution when called"
        pass