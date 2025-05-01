from pathlib import Path

class Directories:
    def __init__(self, asc_dir: Path, bin_dir: Path, data_dir: Path):
        self.asc_dir = asc_dir
        self.bin_dir = bin_dir
        self.data_dir = data_dir
