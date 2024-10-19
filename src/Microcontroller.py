"""
Microcontroller.py
------------------

This file has a class that is used to interact with a microcontroller to extract information about the running circuit.
This interacts with serial. 

.. todo::
    Make a Mock of the Microcontroller to test standard operation without connection to the microcontroller.

.. todo::
    Make a Testing program that would allow you to directly get values from the micrcocontroller class. Maybe a terminal input or something would be good.

.. todo::
    Figure out how to mock Serial connection to allow this class to be tested.

"""
from serial import Serial
from time import time
import numpy as np

from Circuit.CircuitLegacy import CircuitLegacy
import typing

from Config import Config
from Logger import Logger

class Microcontroller:
    """
    This is a class that represents the microcontroller connected to the FPGA. 
    It is primarily used to interpret the serial output into values that are useful for the rest of the program. 
    It mostly deals with  values for fitness functions.
    """
    def __log_event(self, level, *event):
        self.__logger.log_event(level, *event)

    def __log_info(self, level, *info):
        self.__logger.log_info(level, *info)

    def __log_error(self, level, *error):
        self.__logger.log_error(level, *error)

    def __log_warning(self, level, *warning):
        self.__logger.log_warning(level, *warning)

    def __init__(self, config: Config, logger: Logger):
        """
        Initializes Microcontroller Object

        Parameters
        ----------
        config : Config
            Configuration object that determines what Microcontroller does.
        logger : Logger
            Logger object where this object stores its logging information.
        """
        self.__logger = logger
        self.__config = config
        if config.get_simulation_mode() == "FULLY_INTRINSIC" or config.get_simulation_mode() == "INTRINSIC_SENSITIVITY":
            self.__log_event(1, "MCU SETTINGS ================================", config.get_usb_path(), config.get_serial_baud())
            self.__serial =  Serial(
                config.get_usb_path(),
                config.get_serial_baud(),
                timeout=config.get_mcu_read_timeout()
            )
            self.__serial.dtr = False
            if(config.reading_temp_humidity()):
                self.__env_serial =  Serial(
                    config.get_env_usb_path(),
                    config.get_serial_baud(),
                    timeout=config.get_mcu_read_timeout()
                )
                self.__env_serial.dtr = False
            self.__fpga = config.get_fpga()

    def switch_fpga(self):
        """
        If there are multiple FPGAs, switch which FPGA the microcontroller is acting on and reading from.

        .. todo::
            Allyn, Is this the correct interpretation of what this does? Do you want to add additional detail?
            Please also check that the other multi-fpga logic is properly represented as well.
        """
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(b'4') 
        if self.__fpga == self.__config.get_fpga():
            self.__log_event(2, "Switching to FPGA 2")
            self.__fpga = self.__config.get_fpga2()
        else :
            self.__log_event(2, "Switching to FPGA 1")
            self.__fpga = self.__config.get_fpga()
        self.__log_event(2, "Done switching FPGAs")
    
    def get_fpga(self):
        """
        Get __fpga string

        .. todo::
            Allyn, another one for you. What is this?

        Returns
        -------
        str
           FPGA Identifier
        """
        return self.__fpga

    def simple_measure_pulses(self, data_filepath):
        """
        This measure pulses function will poll the MCU,
        and just put the raw pulse count recorded into the circuit's data file

        Parameters
        ----------
        circuit : Circuit
            The circuit we will measure pulses of.
        """
        data_file = open(data_filepath, "w")
        lines = []
        buf = []
        # Poll serial line until START signal
        self.__log_event(3, f"Starting loop for reading (sample {i+1}/{samples})")
        
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        # NOTE The MCU is expecting a string '1' if fitness isn't measured this may be why
        self.__serial.write(b'1') 
        start = time()
        self.__log_event(3, f"Starting MCU loop... (sample {i+1}/{samples})")

        max_attempts = 5
        attempts = 0
        while True:
            attempts = attempts + 1
            self.__log_event(3, f"Serial reading... (sample {i+1}/{samples})")
            p = self.__serial.read_until()
            self.__log_event(3, f"Serial read done (sample {i+1}/{samples})")
            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning(1, f"Time Exceeded (sample {i+1}/{samples})")
                if attempts >= max_attempts:
                    self.__log_warning(3, f"Exceeded max attempts ({max_attempts}). Halting MCU reading")
                    buf.append(-1)
                    break
            # TODO We should be able to do whatever this line does better
            # This is currently doing a poor job at REGEXing the MCU serial return - can be done better
            # It's supposed to handle exceptions from transmission loss (i.e. dropped or additional spaces, shifted colons, etc)
            self.__log_event(3, "Pulled", p, f"from MCU (sample {i+1}/{samples})")
            if (p != b"" and b":" not in p and b"START" not in p and b"FINISH" not in p and b" " not in p):
                p = p.translate(None, b"\r\n")
                buf.append(p)
                break

        end = time() - start

        # if the transfer interval is "SAMPLE", switch to the other fpga between samples
        # if self.__config.get_transfer_sample():
        #     self.switch_fpga()

        # buf now has `samples` entries
        self.__log_event(2, 'Length of buffer:', len(buf))
        if len(buf) == 0:
            buf.append(-1000) # This should never happen
        for i in range(len(buf)):
            self.__log_event(2, f'Buffer entry {i}:', buf[i])
            try:
                buf[i] = int(buf[i])
            except ValueError:
                buf[i] = -1
            lines.append(str(buf[i]) + "\n")

        data_file.writelines(lines)
        data_file.close()

    def measure_pulses(self, circuit: CircuitLegacy):
        """
        Measures the number of pulses generated by the circuit provided.
        
        Parameters
        ----------
        circuit : Circuit
            The circuit we are measuring pulses of
        """
        samples = 2
        if self.__config.get_simulation_mode() == "INTRINSIC_SENSITIVITY":
            samples = 1

        # TODO Use pathlib here
        # Begin monitoring on load
        data_file = open(circuit.get_data_filepath(), "wb")

        buf = []
        for i in range(0,samples):
            # Poll serial line until START signal
            self.__log_event(3, "Starting loop for reading")
            
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            # NOTE The MCU is expecting a string '1' if fitness isn't measured this may be why
            self.__serial.write(b'1') 
            start = time()
            self.__log_event(3, "Starting MCU loop...")

            while True:
                self.__log_event(3, "Serial reading...")
                p = self.__serial.read_until()
                self.__log_event(3, "Serial read done")
                if (time() - start) >= self.__config.get_mcu_read_timeout():
                    self.__log_warning(1, "Time Exceeded. Halting MCU Reading")
                    buf.append(0)
                    break
                # TODO We should be able to do whatever this line does better
                # This is currently doing a poor job at REGEXing the MCU serial return - can be done better
                # It's supposed to handle exceptions from transmission loss (i.e. dropped or additional spaces, shifted colons, etc)
                self.__log_event(3, "Pulled", p, "from MCU")
                if (p != b"" and b":" not in p and b"START" not in p and b"FINISH" not in p and b" " not in p):
                    p = p.translate(None, b"\r\n")
                    buf.append(p)
                    break

            end = time() - start

        buf_dif = 0
        weighted_count = int(buf[0])

        for i in range(0, len(buf)):
            if buf[i] == b'':
                buf[i] = 0
            else:
                buf[i] = int(buf[i])
                if i + 1 < len(buf):
                    buf_dif = abs(int(buf[i]) - int(buf[i+1]))

        if len(buf) > 0:
            if samples > 1:
                weighted_count = abs(buf[0] - buf_dif)
            data_file.write(bytes(str(weighted_count) + "\n", "utf-8"))

        if len(buf) > 0:
            freq = sum(buf)/len(buf)
        else:
            freq = 0.0

        self.__log_event(2, "Length of Buffer:", len(buf))
        self.__log_event(2, "Number Pulses:", sum(buf))
        self.__log_event(2, "Average Frequency: ~", freq, "Hz")
        self.__log_event(2, "Sampling Duration:", end)
        self.__log_event(2, "Completed writing to data file")

        data_file.close()

    def measure_signal(self, data_filepath):
        """
        Measures the signal, writing the waveform data to the provided data file
        
        .. todo::
            Preexisting todo: This whole section can probably be optimized.

        Parameters
        ----------
        circuit : Circuit
            The circuit we are measuring the signal of
        """
        buf = []

        # Begin monitoring on load
        data_file = open(data_filepath, "wb")

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__log_event(1, "Reading microcontroller.")
        # The MCU is expecting a string '2' to initiate the ADC capture from the FPGA (waveform as opposed to pulses)
        self.__serial.write(b'2')
        line = self.__serial.read()

        start = time()

        # The MCU returns a START line followed by many lines of data (500 currently) followed by a FINISHED line
        while b"START\n" not in line:
            self.__serial.write(b'2')
            line = self.__serial.read_until()

            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning(1, "Did not read START from MCU")
                self.__log_warning(1, "Time Exceeded. Halting MCU Reading.")
                break

        # TODO  This whole section can probably be optimized
        # Reads in 500 samples from MCU, with each being 10microseconds apart
        # Then, dumps into a file
        while (b"FINISHED\n" not in line):
            line = self.__serial.read_until()
            if line != b"\n" and line != b"START\n" and line != b"FINISHED\n" and line != b"FINISHED\n":
                buf.append(line)
            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning(1, "Time Exceeded. Halting MCU Reading.")
                break

        self.__log_event(2, "Finished reading microcontroller. Logging data to file.")

        for i in buf:
            if b"FINISHED" not in i:
                data_file.write(bytes(i))

        data_file.close()
        self.__log_event(2, "Completed writing to data file")

    def measure_signal_td(self, circuit):
        """
        Measures (1) the FPGA waveform directly from FPGA output pin and (2) the "state"/frequency waveform
        directly from the signal-generating Nano. Writes 1000 sample points' data to a file.
        
        .. todo::
            Preexisting todo: This whole section can probably be optimized.

        Parameters
        ----------
        circuit : Circuit
            The circuit we are measuring the signal of
        """
        # TODO This whole section can probably be optimized
        
        buf = []

        # Begin monitoring on load
        data_file = open(circuit.get_data_filepath(), "wb")

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__log_event(1, "Reading microcontroller.")
        # The MCU is expecting a string '5' to initiate the ADC capture from the FPGA (waveform & state as opposed to pulses)
        self.__serial.write(b'5')
        line = self.__serial.read()

        start = time()

        # The MCU returns a START line followed by many lines of data (1000 currently) followed by a FINISHED line
        while b"START\n" not in line:
            # Avoid spamming serial link. Experiment works without this.
            # self.__serial.write(b'5')
            line = self.__serial.read_until()
            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning(1, "Did not read START from MCU")
                self.__log_warning(1, "Time Exceeded. Halting MCU Reading.")
                break

        # TODO  This whole section can probably be optimized
        # Reads in 1000 samples from MCU, with each being 2.5 ms apart
        # Then, dumps into a file
        while (b"FINISHED\n" not in line):
            line = self.__serial.read_until()
            if line != b"\n" and line != b"START\n" and line != b"FINISHED\n" and line != b"FINISHED\n":
                buf.append(line)
            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning(1, "Time Exceeded. Halting MCU Reading.")
                break

        self.__log_event(2, "Finished reading microcontroller. Logging data to file.")

        for i in buf:
            if b"FINISHED" not in i:
                data_file.write(bytes(i))

        data_file.close()
        self.__log_event(2, "Completed writing to data file")

        
    def measure_temp(self):
        """
        Measures the temperature using a DHT22 sensor conected to the Arduino.
        """
        self.__log_event(3, "Measuring temperature")
            
        self.__env_serial.reset_input_buffer()
        self.__env_serial.reset_output_buffer()
        self.__env_serial.write(b'5') 
        start = time()

        self.__log_event(3, "Serial reading...")
        p = self.__env_serial.read_until()
        self.__log_event(3, "Serial read done")
        if (time() - start) >= self.__config.get_mcu_read_timeout():
            self.__log_warning(1, "Time Exceeded. Halting MCU Reading of temperature")
            return -1;
        # TODO We should be able to do whatever this line does better
        # This is currently doing a poor job at REGEXing the MCU serial return - can be done better
        # It's supposed to handle exceptions from transmission loss (i.e. dropped or additional spaces, shifted colons, etc)
        self.__log_event(3, "Pulled", p, "from MCU")
        if (p != b"" and b":" not in p and b"START" not in p and b"FINISH" not in p and b" " not in p):
            p = p.translate(None, b"\r\n")
            return(float(p))
        
    def measure_humidity(self):
        """
        Measures the humidity using a DHT22 sensor conected to the Arduino.
        """
        self.__log_event(3, "Measuring humidity")
            
        self.__env_serial.reset_input_buffer()
        self.__env_serial.reset_output_buffer()
        self.__env_serial.write(b'6') 
        start = time()

        self.__log_event(3, "Serial reading...")
        p = self.__env_serial.read_until()
        self.__log_event(3, "Serial read done")
        if (time() - start) >= self.__config.get_mcu_read_timeout():
            self.__log_warning(1, "Time Exceeded. Halting MCU Reading of humidity")
            return -1;
        # TODO We should be able to do whatever this line does better
        # This is currently doing a poor job at REGEXing the MCU serial return - can be done better
        # It's supposed to handle exceptions from transmission loss (i.e. dropped or additional spaces, shifted colons, etc)
        self.__log_event(3, "Pulled", p, "from MCU")
        if (p != b"" and b":" not in p and b"START" not in p and b"FINISH" not in p and b" " not in p):
            p = p.translate(None, b"\r\n")
            return(float(p))





