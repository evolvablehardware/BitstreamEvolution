"""Serial interface for MCU-mediated FPGA measurement.

Provides the ``Microcontroller`` class that communicates with a
microcontroller over a serial link to program an ICE40 FPGA and
retrieve fitness-evaluation data (pulse counts or ADC waveforms).

.. note:: Serial protocol details were inferred from code and may need
   verification against MCU firmware.
"""

from dataclasses import dataclass
from time import time
from serial import Serial
from BitstreamEvolutionProtocols import Circuit, DataRequest, FPGA_Compilation_Data, FPGA_Model, Measurement
from Logger import Logger
from returns.result import Success, Failure # type: ignore

@dataclass
class MicrocontrollerConfig:
    """Serial connection parameters for the MCU.

    Attributes
    ----------
    usb_path : str
        Device path to the serial port (e.g. ``/dev/ttyUSB0``).
    serial_baud : int
        Baud rate for the serial connection.
    read_timeout : float
        Timeout in seconds for serial read operations.
    """

    usb_path: str
    serial_baud: int
    read_timeout: float

class Microcontroller:
    """Driver for a serial-connected MCU that programs and reads from an FPGA.

    Opens a persistent serial connection on construction and provides
    async methods to request waveform or pulse-count measurements.

    Concurrency note:
    =================
    The async methods in this class use blocking pyserial calls and do NOT yield
    to the event loop. As a result, asyncio.gather() over multiple Microcontroller
    instances currently runs them sequentially, not in parallel.

    TODO: Migrate serial I/O to serial_asyncio (https://pypi.org/project/serial-asyncio/)
    so that serial reads genuinely suspend and allow other coroutines to run. This is
    the server-side component — when the architecture moves to a server-client model,
    this class (or its replacement) will run on the server and use serial_asyncio.

    Per-Icestick exclusivity:
    =========================
    Each Microcontroller instance manages exactly one Icestick via one serial port.
    iceprog holds exclusive USB access to the device during compile(). Concurrent
    calls to request_measurement() on the SAME Microcontroller instance will corrupt
    each other. The server must serialize calls per-instance (e.g. one
    asyncio.Semaphore(1) per Microcontroller, or a dedicated worker coroutine per
    device). Calls on DIFFERENT Microcontroller instances (different Icesticks) can
    run concurrently. See .claude/docs/hardware_concurrency.md.
    """

    def __init__(self, fpga: str, logger: Logger, config: MicrocontrollerConfig):
        """Initialize the serial connection to the MCU.

        Parameters
        ----------
        fpga : str
            FPGA device identifier passed to ``icepack``/``iceprog``.
        logger : Logger
            Logger instance for event and warning messages.
        config : MicrocontrollerConfig
            Serial port settings.
        """
        self.__fpga = fpga
        self.__logger = logger
        self.__config = config
        self.__logger.log_event(1, "MCU SETTINGS ================================", config.usb_path, config.serial_baud)
        self.__serial =  Serial(
            config.usb_path,
            config.serial_baud,
            timeout=config.read_timeout
        )
        self.__serial.dtr = False

    async def request_measurement(self, measurement: Measurement) -> Measurement:
        """Compile the circuit and perform the requested measurement.

        Dispatches to ``measure_signal`` or ``measure_pulses`` based on
        ``measurement.data_request``.  The result (or error) is stored in
        ``measurement.result`` as a ``Success`` or ``Failure``.

        Parameters
        ----------
        measurement : Measurement
            Measurement descriptor specifying circuit and data type.

        Returns
        -------
        Measurement
            The same object with ``result`` populated.
        """
        ckt: Circuit = measurement.circuit
        fpga_data = FPGA_Compilation_Data(FPGA_Model.ICE40, self.__fpga)
        if measurement.data_request == DataRequest.WAVEFORM:
            ckt.compile(fpga_data)
            try:
                waveform = await self.measure_signal()
                measurement.result = Success(waveform)
            except Exception as e:
                measurement.result = Failure(e)
        elif measurement.data_request == DataRequest.OSCILLATIONS:
            ckt.compile(fpga_data)
            try:
                data = await self.measure_pulses(measurement.num_samples)
                measurement.result = Success(data)
            except Exception as e:
                measurement.result = Failure(e)
        # TODO: elif cases for other measurement types...
        return measurement

    def get_available_FPGAs(self) -> list[str]:
        """Return the list of FPGA device identifiers managed by this MCU."""
        return [self.__fpga]
    
    async def measure_signal(self) -> list[int]:
        """Capture an ADC waveform from the FPGA via the MCU.

        Sends command ``'2'`` to initiate ADC capture, then reads
        lines between ``START`` and ``FINISHED`` delimiters.

        Returns
        -------
        list[int]
            Integer ADC samples (~10 us apart).
        """
        buf = []

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__logger.log_event(1, "Reading microcontroller.")
        # The MCU is expecting a string '2' to initiate the ADC capture from the FPGA (waveform as opposed to pulses)
        self.__serial.write(b'2')
        line = self.__serial.read()

        start = time()

        # The MCU returns a START line followed by many lines of data (500 currently) followed by a FINISHED line
        while b"START\n" not in line:
            self.__serial.write(b'2')
            line = self.__serial.read_until()

            if (time() - start) >= self.__config.read_timeout:
                self.__logger.log_warning(1, "Did not read START from MCU")
                self.__logger.log_warning(1, "Time Exceeded. Halting MCU Reading.")
                break

        # TODO  This whole section can probably be optimized
        # Reads in samples from MCU, with each being 10microseconds apart
        while (b"FINISHED\n" not in line):
            line = self.__serial.read_until()
            if line != b"\n" and line != b"START\n" and line != b"FINISHED\n" and line != b"FINISHED\n":
                buf.append(line)
            if (time() - start) >= self.__config.read_timeout:
                self.__logger.log_warning(1, "Time Exceeded. Halting MCU Reading.")
                break

        self.__logger.log_event(2, "Finished reading microcontroller. Logging data to file.")

        waveform: list[int] = []
        for i in buf:
            if b"FINISHED" not in i:
                waveform.append(int(i))

        self.__logger.log_event(2, "Completed reading waveform")
        return waveform

    async def measure_pulses(self, samples: int) -> list[int]:
        """Collect multiple pulse-count samples from the FPGA.

        Parameters
        ----------
        samples : int
            Number of times to call ``measure_pulses_once``.

        Returns
        -------
        list[int]
            Concatenated pulse counts from all sample rounds.
        """
        result = []
        for i in range(samples):
            result.extend(await self.measure_pulses_once())
        return result

    async def measure_pulses_once(self) -> list[int]:
        """Perform a single pulse-count read from the MCU.

        Sends command ``'1'`` and polls the serial line for a numeric
        response, retrying up to 5 times on timeout.  Returns ``-1``
        on timeout and ``-2`` on parse failure.

        Returns
        -------
        list[int]
            Parsed pulse count(s) from a single read cycle.
        """
        buf = []
        # Poll serial line until START signal
        self.__logger.log_event(3, f"Starting loop for reading")
        
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        # NOTE The MCU is expecting a string '1' if fitness isn't measured this may be why
        self.__serial.write(b'1') 
        start = time()
        self.__logger.log_event(3, f"Starting MCU loop...")

        max_attempts = 5
        attempts = 0
        while True:
            attempts = attempts + 1
            self.__logger.log_event(3, f"Serial reading...")
            p = self.__serial.read_until()
            self.__logger.log_event(3, f"Serial read done")
            if (time() - start) >= self.__config.read_timeout:
                self.__logger.log_warning(1, f"Time Exceeded")
                if attempts >= max_attempts:
                    self.__logger.log_warning(3, f"Exceeded max attempts ({max_attempts}). Halting MCU reading")
                    buf.append(-1)
                    break
            # TODO We should be able to do whatever this line does better
            # This is currently doing a poor job at REGEXing the MCU serial return - can be done better
            # It's supposed to handle exceptions from transmission loss (i.e. dropped or additional spaces, shifted colons, etc)
            self.__logger.log_event(3, "Pulled", p, f"from MCU")
            if (p != b"" and b":" not in p and b"START" not in p and b"FINISH" not in p and b" " not in p):
                p = p.translate(None, b"\r\n")
                buf.append(p)
                break

        end = time() - start

        self.__logger.log_event(2, 'Length of buffer:', len(buf))
        if len(buf) == 0:
            buf.append(-1000) # This should never happen

        result = []
        for i in range(len(buf)):
            self.__logger.log_event(2, f'Buffer entry {i}:', buf[i])
            try:
                result.append(int(buf[i]))
            except ValueError:
                result.append(-2)
        
        return result

