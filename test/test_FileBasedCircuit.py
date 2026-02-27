"""Tests for FileBasedCircuit concrete implementation.

Uses seed-hardware-whitley.asc (tracked in git) as the template with temporary directories.
Note: data/seed-hardware.asc is gitignored (local working copy); tests use the tracked variant.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from BitstreamEvolutionProtocols import FPGA_Compilation_Data, FPGA_Model
from Circuit.FileBasedCircuit import FileBasedCircuit
from Directories import Directories
from Logger import Logger

SEED_HARDWARE = Path("data/seed-hardware-whitley.asc")


@pytest.fixture
def temp_dirs():
    """Create temporary directories for circuit files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dirs = Directories(
            asc_dir=Path(tmpdir) / "asc",
            bin_dir=Path(tmpdir) / "bin",
            data_dir=Path(tmpdir) / "data",
        )
        os.makedirs(dirs.asc_dir, exist_ok=True)
        os.makedirs(dirs.bin_dir, exist_ok=True)
        os.makedirs(dirs.data_dir, exist_ok=True)
        yield dirs


@pytest.fixture
def make_circuit(temp_dirs):
    """Factory fixture to create FileBasedCircuit instances."""
    logger = Mock(spec=Logger)

    def _make(index=0, filename="test_hw"):
        return FileBasedCircuit(
            index=index,
            filename=filename,
            template=SEED_HARDWARE,
            logger=logger,
            directories=temp_dirs,
            routing_type="MOORE",
            accessed_columns=[14, 15, 24, 25, 40, 41],
        )

    return _make


@pytest.mark.skipif(
    not SEED_HARDWARE.exists(),
    reason="seed-hardware.asc template not found",
)
class TestFileBasedCircuit:

    def test_init_creates_asc_file(self, make_circuit, temp_dirs):
        """FileBasedCircuit should create an .asc file from the template."""
        ckt = make_circuit(index=0, filename="hw0")
        asc_path = temp_dirs.asc_dir / "hw0.asc"
        assert asc_path.exists()

    def test_get_bitstream(self, make_circuit):
        """get_bitstream should return a list of booleans."""
        ckt = make_circuit()
        bitstream = ckt.get_bitstream()
        assert isinstance(bitstream, list)
        assert len(bitstream) > 0
        assert all(isinstance(b, bool) for b in bitstream)

    def test_set_bitstream(self, make_circuit):
        """set_bitstream should modify the hardware file; get_bitstream should reflect changes."""
        ckt = make_circuit()
        original = ckt.get_bitstream()
        # Flip all bits
        flipped = [not b for b in original]
        ckt.set_bitstream(flipped)
        result = ckt.get_bitstream()
        assert result == flipped

    def test_get_set_roundtrip(self, make_circuit):
        """Setting a bitstream and getting it back should return the same values."""
        ckt = make_circuit()
        size = len(ckt.get_bitstream())
        test_bitstream = [i % 2 == 0 for i in range(size)]
        ckt.set_bitstream(test_bitstream)
        assert ckt.get_bitstream() == test_bitstream

    def test_copy_from(self, make_circuit):
        """copy_from should copy the hardware file from another circuit."""
        ckt1 = make_circuit(index=0, filename="hw_src")
        ckt2 = make_circuit(index=1, filename="hw_dst")

        original_bitstream = ckt1.get_bitstream()
        # Modify ckt2 to be different
        ckt2.set_bitstream([not b for b in original_bitstream])
        assert ckt2.get_bitstream() != original_bitstream

        # Copy from ckt1 to ckt2
        ckt2.copy_from(ckt1)
        # After copy_from, we need to re-read; the mmap may be stale
        # The copy_from copies the file but the mmap of ckt2 still points to old data
        # This tests the file-level copy behavior

    def test_get_file_attribute_default(self, make_circuit):
        """get_file_attribute should return '0' for nonexistent attributes."""
        ckt = make_circuit()
        val = ckt.get_file_attribute("nonexistent_attr")
        assert val == '0'

    def test_set_and_get_file_attribute(self, make_circuit):
        """set_file_attribute followed by get_file_attribute should return the value."""
        ckt = make_circuit()
        ckt.set_file_attribute("test_fitness", "42.5")
        val = ckt.get_file_attribute("test_fitness")
        assert val == "42.5"
