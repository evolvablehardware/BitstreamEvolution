from unittest.mock import Mock
import pytest
from returns.result import Failure, Success

from BitstreamEvolutionProtocols import (
    Circuit, DataRequest, Measurement, MeasurementNotTaken,
)


# --- Tests for Measurement initial state ---

def test_Measurement_initial_result_is_failure():  # Written by AI
    """A new Measurement should start with result = Failure(MeasurementNotTaken)."""
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    assert isinstance(m.result, Failure)
    inner = m.result.failure()
    assert isinstance(inner, MeasurementNotTaken)


# --- Tests for recording success ---

def test_Measurement_record_success():  # Written by AI
    """record_measurement_result with valid data should set result to Success."""
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    m.record_measurement_result([1, 2, 3])

    assert isinstance(m.result, Success)
    assert m.result.unwrap() == [1, 2, 3]


# --- Tests for recording error ---

def test_Measurement_record_error():  # Written by AI
    """record_measurement_result with an Exception should set result to Failure."""
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    err = Exception("test error")
    m.record_measurement_result(err)

    assert isinstance(m.result, Failure)
    assert m.result.failure() is err


# --- Tests for record_FPGA_used ---

def test_Measurement_record_FPGA_used():  # Written by AI
    """record_FPGA_used should update the FPGA_used field."""
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    assert m.FPGA_used is None
    m.record_FPGA_used("FPGA_42")
    assert m.FPGA_used == "FPGA_42"


# --- Tests for generic types ---

def test_Measurement_generic_types():  # Written by AI
    """Measurement should work with different Circuit and measurement data types."""
    ckt = Mock(spec=Circuit)

    # int measurement data
    m_int = Measurement("fpga", DataRequest.OSCILLATIONS, ckt, 3)
    m_int.record_measurement_result(42)
    assert m_int.result.unwrap() == 42

    # list measurement data
    m_list = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)
    m_list.record_measurement_result([10, 20, 30])
    assert m_list.result.unwrap() == [10, 20, 30]


# --- Tests for initial attributes ---

def test_Measurement_stores_constructor_args():  # Written by AI
    """Measurement should store all constructor arguments as attributes."""
    ckt = Mock(spec=Circuit)
    m = Measurement("my_fpga", DataRequest.OSCILLATIONS, ckt, 5)

    assert m.FPGA_request == "my_fpga"
    assert m.data_request == DataRequest.OSCILLATIONS
    assert m.circuit is ckt
    assert m.num_samples == 5
