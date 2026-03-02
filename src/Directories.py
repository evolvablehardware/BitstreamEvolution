"""Directory path container for circuit file storage."""

from pathlib import Path

class Directories:
    """Holds paths for ASC, BIN, and data directories used by FileBasedCircuit."""

    def __init__(self, asc_dir: Path, bin_dir: Path, data_dir: Path):
        """Store the three directory paths.

        Parameters
        ----------
        asc_dir : Path
            Directory for ASC bitstream text files.
        bin_dir : Path
            Directory for compiled binary bitstream files.
        data_dir : Path
            Directory for experiment output data.
        """
        self.asc_dir = asc_dir
        self.bin_dir = bin_dir
        self.data_dir = data_dir
