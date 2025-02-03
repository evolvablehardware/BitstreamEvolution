"""
This file is intended to help brainstorm a way to cleanly allow you to run a check to verify.

Below are examples of the code needed to write verifyable code, and how to verify it.

"""
from typing import Protocol, runtime_checkable, Callable
import functools as ft   #ft.wraps(), ft.partial()


# ----------------------------------------------- Version 1: Verification with Inheritence -----------------------------------------------
@runtime_checkable
class V1Thing(Protocol):
    """
    This is an Protocol (Abstract Class with fancy syntax) for defining a verifiable thing with .verify()
    """
    def verify(self)->bool:
        ...
    def evaluate(self,*args,**kwargs)-> any:
        ...

@runtime_checkable
class V1ThingInherited(V1Thing,Protocol): # The protocol is also required to note that this is abstract and can't be implemented
    """
    This is a Protocol subtype of verifiable thing with .verify().
    """
    def evaluate(self,int_list:list[int]) -> float:
        ...

# ------------------------------------------------ Version 2: Verification with Decorator ------------------------------------------------

# The decorator instantiated
def v2verify_with(verify_function:Callable):
    "This is a decorator to attatch a verified function to it."

    @ft.wraps(verify_function) # Maintain name information
    def verifier(func:Callable):
        verified = func
        verified.verify = verify_function
        # We could also potentially put this funtion into a list for testing.
        return verified
    
    return verifier

# ------------------------------------------- Version 3: Verification of Funciton With Argument -------------------------------------------

class V3Verifior:
    "When this class is passed to a function, it is requesting the function quickly verify it's arguments and functions it calls."
    def __init__(self):
        self.errors = []

    def was_valid(self)->bool:
        return len(self.errors)
    
    def mark_invalid(self,message:str,function:Callable): #This could be an exception, too
        self.errors.append((message,function))
    
    def issues(self):
        if len(self.errors) == 0:
            print("Operations are Valid.")

        for e in self.errors:
            print(f"Validation Error: '{e[0]}' in '{e[1].__name__}'")



########################################################## COMPARING RESULTING SYNTAX ##########################################################

class V1ThingObj(V1ThingInherited):
    """
    This implements a Protocol and verify.
    """
    def evaluate(self,Integer_List: list[int]) -> float:
        return sum(Integer_List)/len(Integer_List)
    
    def verify(self) -> bool:
        # This can only verify VThingObj class -> isinstance(Integer_List,list)
        return isinstance(self,V1Thing) # This isn't useful, but emulates the types of checks you may want to make 

v1t = V1ThingObj()
print("1) Using Inheritence and classes to verify"
        +"\n\t" + f"VThing Obj Verified <{v1t.verify()}>  and evaluated <{v1t.evaluate([1,2,3,4])}>"
        +"\n\t" + "NOTE that this cannot validate the input to the evaluate function."
        +"\n\t" + "This was demonstrated with Protocols, but may be best implemented with ABC's Abstract classes to avoid duck_typing" )

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Common verify functions could be imported and used easily, removing need for this define
def v2verify(higher_num:int, lower_num:int, mod_denom:int)->bool:
    return isinstance(higher_num,int) and \
            isinstance(lower_num,int) and \
            isinstance(mod_denom,int)
    # Note that this function does not have access to actual inputs to v2func

@v2verify_with(v2verify)
def v2func(higher_num:int, lower_num:int, mod_denom:int)->int:
    return (higher_num-lower_num) % mod_denom

v2func_part         = ft.partial(v2func,mod_denom=5)
v2func_verify_part  = ft.partial(v2func.verify,mod_denom=5)

print("2) Using Decorators and Functions to verify"
        +"\n\t" + f"Function verified '{v2func.verify(25,3,5)}'  and evaluated '{v2func(25,3,5)}'"
        +"\n\t" + f"Functool Partial Function Verified: '{v2func_verify_part(25,3)}' and evaluated '{v2func_part(25,3)}'"
        +"\n\t" + "NOTE that this cannot validate the input to the evaluate function, requiring validation be passed separately, as the .verify() is removed when using functools."
        +"\n\t" + "NOTE that verify function is not syntactically highlighted" )

# ------------------------------------------------------------------------------------------------------------------------------------------------

def v3func(higher_num:int, lower_num:int, mod_denom:int,verify:None|V3Verifior=None)-> int:
    if verify is not None:
        if not isinstance(higher_num,int):
            verify.mark_invalid("Higher num is not an int",v3func)

        if not isinstance(lower_num,int):
            verify.mark_invalid("Lower num is not an int",v3func)

        if not isinstance(mod_denom,int):
            verify.mark_invalid("Modulo Denominator is not an int",v3func)

        # Can easily call all classes used or functions used with the verifior

        return 0 # Return some valid output
    
    return (higher_num-lower_num) % mod_denom

v3_1 = V3Verifior()
v3_2 = V3Verifior()
v3_partial = ft.partial(v3func,lower_num=3,mod_denom=5)

print("3) Using Validator object and Functions to verify"
        +"\n\t" + f"Function verified '{v3func(25,3,5,verify=v3_1)}, valid={v3_1.was_valid()}'  and evaluated '{v3func(25,3,5)}'"
        +"\n\t" + f"Functool Partial Function Verified: '{v3_partial(25,verify=v3_2)}, valid={v3_2.was_valid()}' and evaluated '{v3_partial(25)}' (much nicer)"
        +"\n\t" + "NOTE this is nice because you can easily verify in partial, and you can check all errors simultaniously and recursively and with .verify()." 
        +"\n\t" + "NOTE Below is an example of what happens when verification fails: (verifior.was_valid()->False) v3func(4.3, 9.2 ,8)->" 
        +"\n\t" + "NOTE that the verify if statement takes up a lot of space, which can be annoying, and may require rasing an error for each issue, and may break the program if someone accidentially fills that field of a function with ft.partial.")
v3func(4.3,9.2,8,verify=v3_2)
v3_2.issues()

# ------------------------------------------------------------------------------------------------------------------------------------------------

def v4func(higher_num:int, lower_num:int, mod_denom:int,verify:bool=False)-> int:
    if verify: #This could also potentially involve calling pre-made verification things
        if not isinstance(higher_num,int):
            raise TypeError("Higher Number was not an int")
        if not isinstance(lower_num,int):
            raise TypeError("Lower Number was not an int")
        if not isinstance(mod_denom,int):
            raise TypeError("Modulo Denominator was not an int")
        # Also put any calls here so they can be verified quickly
        return 0 #Something arbitrary to stop execution

    return (higher_num-lower_num) % mod_denom

v4_partial = ft.partial(v4func,lower_num=3,mod_denom=5)

print("4) Using argument and Functions to verify"
        +"\n\t" + f"Function verified '{v4func(25,3,5,verify=True)}'  and evaluated '{v4func(25,3,5)}'"
        +"\n\t" + f"Functool Partial Function Verified: '{v4_partial(25,verify=True)}' and evaluated '{v4_partial(25)}' (much nicer)"
        +"\n\t" + "NOTE this is nice because you can easily verify in partial, and you can check all errors simultaniously and recursively and with .verify()." 
        +"\n\t" + "NOTE that the verify if statement takes up a lot of space in the function (could be moved to another function), which can be annoying, and may require rasing an error for each issue, and may break the program if someone accidentially fills that field of a function with ft.partial."
        +"\n\t" + "NOTE Errors can arise if forget to put all functions used in verify statement")

# ------------------------------------------------------------------------------------------------------------------------------------------------
print("5) Use a Linter and type annotations to verify."
      +"\n\t" + "If we simply ran a linter before we run the code, it should be able to catch type errors as long as we enforce typehints"
      +"\n\t" + "We may also invoke it when we start the program to enforce this check occouring.")
print("Can enforce on individual functions with typeguard: https://typeguard.readthedocs.io/en/latest/userguide.html\n or the whole program with beartype: https://beartype.readthedocs.io/en/latest/")