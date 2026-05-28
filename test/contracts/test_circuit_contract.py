"""Contract tests for the Circuit protocol.

These tests define the behavioral contract that ALL Circuit implementations must satisfy.
Adding a new implementation is straightforward:

  1. Subclass ``CircuitContractTests`` (note: no ``Test`` prefix on the base class,
     so pytest ignores it and only collects the concrete subclasses)
  2. Implement the ``circuit`` fixture to return an instance of your implementation
  3. pytest will automatically run all contract tests against it
"""

import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from returns.result import Failure, Success

from BitstreamEvolutionProtocols import FPGA_Compilation_Data, FPGA_Model
from TrivialImplementation import TrivialCircuit


# ---------------------------------------------------------------------------
# Base contract — NOT collected by pytest (no ``Test`` prefix)
# ---------------------------------------------------------------------------

class CircuitContractTests:
    """Defines the behavioral contract for any class satisfying the Circuit protocol.

    Every method here is a test that every implementation must pass.
    """

    @pytest.fixture
    def circuit(self):
        raise NotImplementedError("Subclasses must override the 'circuit' fixture")

    @pytest.fixture
    def fpga_data(self):
        return FPGA_Compilation_Data(FPGA_Model.ICE40, "test-id")

    def test_compile_returns_result_type(self, circuit, fpga_data):  # Written by AI
        """compile() must return a Result — either Success(None) or Failure(Exception)."""
        result = circuit.compile(fpga_data)
        assert isinstance(result, (Success, Failure))

    def test_compile_never_raises(self, circuit, fpga_data):  # Written by AI
        """compile() must never raise; errors must be returned as Failure, not raised."""
        try:
            circuit.compile(fpga_data)
        except Exception as exc:
            pytest.fail(
                f"compile() raised {type(exc).__name__} instead of returning Failure: {exc}"
            )


# ---------------------------------------------------------------------------
# TrivialCircuit
# ---------------------------------------------------------------------------

class TestTrivialCircuit_Circuit(CircuitContractTests):  # Written by AI
    """Runs all CircuitContractTests against TrivialCircuit."""

    @pytest.fixture
    def circuit(self):
        return TrivialCircuit(10)

    def test_compile_always_succeeds(self, circuit, fpga_data):  # Written by AI
        """TrivialCircuit.compile() is a no-op that always returns Success(None)."""
        result = circuit.compile(fpga_data)
        assert isinstance(result, Success)
        assert result.unwrap() is None


# ---------------------------------------------------------------------------
# FileBasedCircuit
# ---------------------------------------------------------------------------

SEED_HARDWARE = Path("data/seed-hardware-whitley.asc")


@pytest.mark.skipif(
    not SEED_HARDWARE.exists(),
    reason="seed-hardware-whitley.asc template not found",
)
class TestFileBasedCircuit_Circuit(CircuitContractTests):  # Written by AI
    """Runs all CircuitContractTests against FileBasedCircuit.

    ``subprocess.run`` and ``time.sleep`` are patched so the tests do not
    require ``icepack`` or ``iceprog`` to be installed.
    """

    @pytest.fixture(autouse=True)
    def _patch_subprocess(self, monkeypatch):
        """Patch out the hardware tools so compile() can run without them."""
        monkeypatch.setattr("Circuit.FileBasedCircuit.run", Mock())
        monkeypatch.setattr("Circuit.FileBasedCircuit.sleep", Mock())

    @pytest.fixture
    def circuit(self, tmp_path):
        from Circuit.FileBasedCircuit import FileBasedCircuit
        from Directories import Directories
        from Logger import Logger

        dirs = Directories(
            asc_dir=tmp_path / "asc",
            bin_dir=tmp_path / "bin",
            data_dir=tmp_path / "data",
        )
        os.makedirs(dirs.asc_dir, exist_ok=True)
        os.makedirs(dirs.bin_dir, exist_ok=True)
        os.makedirs(dirs.data_dir, exist_ok=True)

        return FileBasedCircuit(
            index=0,
            filename="contract_hw",
            template=SEED_HARDWARE,
            logger=Mock(spec=Logger),
            directories=dirs,
            routing_type="MOORE",
            accessed_columns=[14, 15, 24, 25, 40, 41],
        )
