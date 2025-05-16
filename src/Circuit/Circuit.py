from abc import ABC, abstractmethod
from pathlib import Path

from BitstreamEvolutionProtocols import FPGA_Compilation_Data
from Logger import Logger
from result import Result # type: ignore

class Circuit(ABC):
    def __repr__(self):
        """
        Returns the string representation of this Circuit, used in
        functions such as 'print'.

        Returns
        -------
        str
            A string representation of the Circuit. (the file name)
        """
        return self._filename

    def __init__(self, index: int, filename: str, logger: Logger):
        self._filename = filename
        self._index = index
        self._logger = logger

    @abstractmethod
    def compile(self, fpga: FPGA_Compilation_Data) -> Result[None,Exception]:
        """
        Performs the upload function of this Circuit. Prerequisite to collecting data
        """
        pass

    @abstractmethod
    def get_bitstream(self) -> list[bool]:
        """
        Returns the full bitstream of the circuit
        """
        pass

    @abstractmethod
    def set_bitstream(self, bitstream: list[bool]):
        """
        Sets the bitstream of the circuit
        """
        pass
    
    def set_file_attribute(self, attribute, value):
        pass # No default behavior

    def get_file_attribute(self, attribute) -> str | None:
        return '0' # No default behavior

    @abstractmethod
    def copy_from(self, other):
        """
        Fully copy the bitstream from the other circuit

        Parameters
        ----------
        other : Circuit
            The other circuit to copy the bitstream from
        """
        pass
