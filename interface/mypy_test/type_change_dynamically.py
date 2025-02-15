from typing import Callable, TypeVar, Protocol
from types import ModuleType

class mini_cls(Protocol):
    def get_num(self)->int | float | str:
        ...

class mini_cls_int:
    def get_num(self)->int:
        return 5

class hold_func:
    def __init__(self, get_number:Callable[...,int | float | str], mini_c:mini_cls ):
        self.function = get_number
        self.get_number = get_number
        self.mc = mini_c
    
    def num(self) -> int | float | str:
        return self.function()
    
    #def get_number(self) -> int | float | str:
    #    raise NotImplementedError()

    def cls_num(self)-> int | float | str:
        return self.mc.get_num()
    
def get_int() -> int:
    return 6

def get_float() -> float:
    return 54.3

def get_str() -> str:
    return "str_thing"

# Test when passes in an int
int_func = hold_func(get_int, mini_cls_int())

# This Failed, needed to adopt the union types
#test1:int    = int_func.num() # Should pass
#test2:float  = int_func.num() # Should Fail
#test3:str    = int_func.num() # Should Fail

# This Failed because needed to adopt the union types
# test1:int    = int_func.get_number() # Should pass
# test2:float  = int_func.get_number() # Should Fail
# test3:str    = int_func.get_number() # Should Fail

# This Failed because needed to adopt the union types
# test1:int    = int_func.cls_num() # Should pass
# test2:float  = int_func.cls_num() # Should Fail
# test3:str    = int_func.cls_num() # Should Fail

# This Failed because needed to adopt the union types
# test1:int    = int_func.mc.get_num() # Should pass
# test2:float  = int_func.mc.get_num() # Should Fail
# test3:str    = int_func.mc.get_num() # Should Fail

# I don't think there is a way to properly type this where the internal
# Types could inform the external types in static analysis.
give_up:int = n if (good:=isinstance((n:=int_func.get_number()),int)) else 0

# I even have to add in a new line... :/   :(
if not good: raise ValueError()

