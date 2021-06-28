from serial import Serial
from time import time

class Microcontroller:
    def __log_event(self, *event):
        self.__logger.log_event(*event)

    def __log_info(self, *info):
        self.__logger.log_info(*info)

    def __log_error(self, *error):
        self.__logger.log_error(*error)

    def __log_warning(self, *warning):
        self.__logger.log_warning(*warning)

    def __init__(self, config, logger):
        self.__logger = logger
        self.__config = config
        self.__serial =  Serial(
            config.get_usb_path(),
            config.get_serial_baud(),
        )

    def measure_pulses(self, circuit):
        samples = 2

        # TODO Use pathlib here
        # Begin monitoring on load
        data_file = open(circuit.get_data_filepath(), "wb")

        buf = []

        for i in range(0,samples):
            # Poll serial line until START signal
            self.__serial.reset_input_buffer()
            self.__serial.write(bytes(1))
            start = time()

            while True:
                p = self.__serial.read()
                if (time() - start) >= self.__config.get_mcu_read_timeout():
                    self.__log_warning("Time Exceeded. Halting MCU Reading")
                    break
                # TODO We should be able to do whatever this line does better
                if (p != b"" and b":" not in p and b"START" not in p and b"FINISH" not in p and b" " not in p):
                    p = p.translate(None, b"\r\n")
                    buf.append(p)
                    break

            end = time() - start

        buf_dif = 0
        weighted_count = 0

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
            data_file.write(bytes(weighted_count) + "\n")

        if len(buf) > 0:
            freq = sum(buf)/len(buf)
        else:
            freq = 0.0

        self.__log_event("Length of Buffer:", len(buf))
        self.__log_event("Number Pulses:", sum(buf))
        self.__log_event("Average Frequency: ~", freq, "Hz")
        self.__log_event("Sampling Duration:", end)
        self.__log_event("Completed writing to data file")

        data_file.close()

    def measure_signal(self, circuit):
        buf = []

        # Begin monitoring on load
        data_file = open(circuit.get_data_filepath(), "wb")

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer();
        self.__log_event("Reading microcontroller.")
        self.__serial.write(b'2')
        line = self.__serial.read()

        start = time()

        # TODO REVIEW This whole section can probably be optimized
        while b"START\n" not in line:
            self.__serial.write(b'2')
            line = self.__serial.read_until()

            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning("Did not read START from MCU")
                self.__log_warning("Time Exceeded. Halting MCU Reading.")
                break

        # TODO REVIEW This whole section can probably be optimized
        while (b"FINISHED\n" not in line):
            line = self.__serial.read_until()
            if line != b"\n" and line != b"START\n" and line != b"FINISHED\n" and line != b"FINISHED\n":
                buf.append(line)
            if (time() - start) >= self.__config.get_mcu_read_timeout():
                self.__log_warning("Time Exceeded. Halting MCU Reading.")
                break

        self.__log_event("Finished reading microcontroller. Logging data to file.")

        for i in buf:
            if b"FINISHED" not in i:
                data_file.write(bytes(i))

        data_file.close()
        self.__log_event("Completed writing to data file")