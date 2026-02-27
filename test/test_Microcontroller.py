"""Tests for Microcontroller with mocked serial communication."""
import asyncio
from unittest.mock import Mock, patch, MagicMock

import pytest

from BitstreamEvolutionProtocols import (
    Circuit, DataRequest, FPGA_Compilation_Data, FPGA_Model, Measurement,
)
from Hardware.Microcontroller import Microcontroller, MicrocontrollerConfig
from Logger import Logger


@pytest.fixture
def mock_serial():
    """Create a mock Serial object."""
    with patch("Hardware.Microcontroller.Serial") as MockSerial:
        mock_ser = MagicMock()
        MockSerial.return_value = mock_ser
        yield mock_ser


@pytest.fixture
def make_mcu(mock_serial):
    """Create a Microcontroller with mocked serial."""
    logger = Mock(spec=Logger)
    config = MicrocontrollerConfig(
        usb_path="/dev/ttyUSB0",
        serial_baud=115200,
        read_timeout=5.0,
    )

    def _make(fpga="FPGA_TEST"):
        return Microcontroller(fpga, logger, config)

    return _make


def test_Microcontroller_init(make_mcu, mock_serial):
    """Microcontroller should initialize and configure serial connection."""
    mcu = make_mcu()
    assert mcu is not None
    assert mock_serial.dtr is False


def test_Microcontroller_get_available_FPGAs(make_mcu):
    """get_available_FPGAs should return a list with the configured FPGA."""
    mcu = make_mcu("MY_FPGA")
    fpgas = mcu.get_available_FPGAs()
    assert fpgas == ["MY_FPGA"]


def test_Microcontroller_measure_signal(make_mcu, mock_serial):
    """measure_signal should parse waveform data from serial."""
    mcu = make_mcu()

    # Simulate serial responses: first read returns something, then START, then data, then FINISHED
    mock_serial.read.return_value = b'x'
    mock_serial.read_until.side_effect = [
        b"START\n",       # START signal
        b"100\n",         # data point 1
        b"200\n",         # data point 2
        b"300\n",         # data point 3
        b"FINISHED\n",   # end signal
    ]

    result = asyncio.run(mcu.measure_signal())

    assert isinstance(result, list)
    assert result == [100, 200, 300]


def test_Microcontroller_measure_pulses(make_mcu, mock_serial):
    """measure_pulses should collect data from multiple samples."""
    mcu = make_mcu()

    # For 2 samples, measure_pulses_once is called twice
    # Each call: write b'1', then read_until returns data
    mock_serial.read_until.side_effect = [
        b"42\n",   # first pulse measurement
        b"43\n",   # second pulse measurement
    ]

    result = asyncio.run(mcu.measure_pulses(2))

    assert isinstance(result, list)
    assert len(result) == 2


def test_Microcontroller_request_measurement_waveform(make_mcu, mock_serial):
    """request_measurement with WAVEFORM should compile circuit and measure signal."""
    mcu = make_mcu()

    ckt = Mock(spec=Circuit)
    ckt.compile.return_value = Mock()  # Ok(None)

    measure = Measurement("FPGA_TEST", DataRequest.WAVEFORM, ckt, 1)

    mock_serial.read.return_value = b'x'
    mock_serial.read_until.side_effect = [
        b"START\n",
        b"500\n",
        b"FINISHED\n",
    ]

    result = asyncio.run(mcu.request_measurement(measure))

    assert result is measure
    ckt.compile.assert_called_once()


def test_Microcontroller_request_measurement_oscillations(make_mcu, mock_serial):
    """request_measurement with OSCILLATIONS should compile circuit and measure pulses."""
    mcu = make_mcu()

    ckt = Mock(spec=Circuit)
    ckt.compile.return_value = Mock()

    measure = Measurement("FPGA_TEST", DataRequest.OSCILLATIONS, ckt, 1)

    mock_serial.read_until.side_effect = [
        b"55\n",  # one pulse measurement
    ]

    result = asyncio.run(mcu.request_measurement(measure))

    assert result is measure
    ckt.compile.assert_called_once()


def test_Microcontroller_timeout_recovery(make_mcu, mock_serial):
    """Microcontroller should handle serial timeouts gracefully."""
    mcu = make_mcu()

    # Simulate timeout by making read_until return empty bytes repeatedly
    # and having time exceed the timeout
    mock_serial.read_until.return_value = b""

    # Use a very short timeout config to trigger timeout behavior
    with patch("Hardware.Microcontroller.time") as mock_time:
        # First call returns 0, subsequent calls return values beyond timeout
        mock_time.side_effect = [0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

        result = asyncio.run(mcu.measure_pulses_once())

        # Should return -1 on timeout
        assert -1 in result
