from dataclasses import dataclass
from time import time
from serial import Serial
from BitstreamEvolutionProtocols import Circuit, DataRequest, FPGA_Compilation_Data, FPGA_Model, Measurement
from Logger import Logger
from result import Ok, Err # type: ignore

@dataclass
class MicrocontrollerConfig:
    usb_path: str
    serial_baud: int
    read_timeout: float

class Microcontroller:
    def __init__(self, fpga: str, logger: Logger, config: MicrocontrollerConfig):
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
        ckt: Circuit = measurement.circuit
        fpga_data = FPGA_Compilation_Data(FPGA_Model.ICE40, self.__fpga)
        if measurement.data_request == DataRequest.WAVEFORM:
            ckt.compile(fpga_data)
            try:
                waveform = await self.measure_signal()
                measurement.result = Ok(waveform)
            except Exception as e:
                measurement.result = Err(e)
        # TODO: elif cases for other measurement types...
        return measurement

    def get_available_FPGAs(self) -> list[str]:
        return [self.__fpga]
    
    async def measure_signal(self) -> list[int]:
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

