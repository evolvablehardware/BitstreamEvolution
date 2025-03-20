from dataclasses import dataclass, field
from typing import Protocol, TypeVar, Union, Final, Optional, overload, Any
from abc import ABC, abstractmethod
from pathlib import Path
from enum import Enum, Flag, IntEnum, IntFlag, auto
from result import Ok, Err, Result, as_result           # https://pypi.org/project/result/ #https://result.readthedocs.io/en/latest/result.html

from functools import partial as part



@dataclass
class PulseCountData:
    """Holds Data for hardware outputs"""
    pulse_count:int

@dataclass
class VariabilityData:
    """Holds Data for hardware outputs when returning configurability data"""
    voltages:tuple[float, ... ]
    # Due to post_init the following are generated automatically on creation
    max_voltage:float = field(init=False)
    min_voltage:float = field(init=False)

    def __post_init__(self):
        self.max_voltage = max(self.voltages)
        self.min_voltage = min(self.min_voltage)

HardwareData = Union[PulseCountData,VariabilityData]

class DataConfiguration(Enum):
    """
    This configures the state of the software so that it 
    can be changed when different tests require different 
    software to be running on the hardware.
    """
    VARIABILITY = auto()
    PULSE_COUNT = auto()
    

class Hardware(ABC):
    """
    Hardware is an abstract class for a particular 
    hardware piece of hardware, where all subclasses are possible configurations of it.
    I am not sure if this is good because it allows for good type-checking in python for the different data configs result in,
    but it does not have any way to switch between these hardware modes or ensure that
    only one mode is active at any one point.
    """

    @abstractmethod
    def get_config(self) -> Path:
        "Gets Path of the code to be programmed on hardware."
        ...
    
    @abstractmethod
    def initialize_hardware(self) -> None:
        "any specific initialization code"
        ...
    
    @abstractmethod
    def get_data(self) -> HardwareData:
        "pulls the data from the hardware."
        ...



def getHardware(type:DataConfiguration)->HardwareData:
    match type:
        case DataConfiguration.VARIABILITY:
            return VariabilityData((2,2.3,3.33,2323))
        case DataConfiguration.PULSE_COUNT:
            return PulseCountData(5)
    

