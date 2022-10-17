from pathlib import Path

# TODO Add handling for missing values
# NOTE Fails ungracefully at missing values currently
class Config:
	def __init__(self, config_parser):
		self.__config_parser = config_parser

	# SECTION Generic getters for options in the various sections.
	def get_ga_parameters(self, param):
		return self.__config_parser.get("GA PARAMETERS", param)

	def get_logging_parameters(self, param):
		return self.__config_parser.get("LOGGING PARAMETERS", param)

	def get_system_parameters(self, param):
		return self.__config_parser.get("SYSTEM PARAMETERS", param)

	def get_hardware_parameters(self, param):
		return self.__config_parser.get("HARDWARE PARAMETERS", param)

	# SECTION Getters for GA Parameters.
	def get_population_size(self):
		return int(self.get_ga_parameters("POPULATION_SIZE"))

	def get_n_generations(self):
		return int(self.get_ga_parameters("GENERATIONS"))

	def get_genotypic_length(self):
		return int(self.get_ga_parameters("GENOTYPIC_LENGTH	"))

	def get_mutation_probability(self):
		return float(self.get_ga_parameters("MUTATION_PROBABILITY"))

	def get_crossover_probability(self):
		return float(self.get_ga_parameters("CROSSOVER_PROBABILITY"))

	def get_elitism_fraction(self):
		return float(self.get_ga_parameters("ELITISM_FRACTION"))

	def get_desired_frequency(self):
		return int(self.get_ga_parameters("DESIRED_FREQ"))

	def get_selection_type(self):
		return self.get_ga_parameters("SELECTION")

	def get_randomization_type(self):
		return self.get_ga_parameters("RANDOMIZE_UNTIL")

	def get_variance_threshold(self):
		return int(self.get_ga_parameters("VARIANCE_THRESHOLD"))

	def get_init_mode(self):
		return self.get_ga_parameters("INIT_MODE")

	def get_using_pulse_function(self):
		return self.get_ga_parameters("PULSE_FUNC") == "True"

	# We have 3 types of mode. There's FULLY_INTRINSIC, SIM_HARDWARE, and FULLY_SIM
	# FULLY_INTRINSIC: Runs the experiments on the actual hardware. Full normal experiment setup
	# SIM_HARDWARE: Simulation mode, but using an arbitrary function operating on compiled binary files
	# FULLY_SIM: Simulation mode, but operating on a small array of arbitrary bit values
	def get_simulation_mode(self):
		return self.get_ga_parameters("SIMULATION_MODE")

	# SECTION Getters for logging parameters.
	def get_asc_directory(self):
		return Path(self.get_logging_parameters("ASC_DIR"))

	def get_bin_directory(self):
		return Path(self.get_logging_parameters("BIN_DIR"))

	def get_data_directory(self):
		return Path(self.get_logging_parameters("DATA_DIR"))

	def get_analysis_directory(self):
		return Path(self.get_logging_parameters("ANALYSIS"))

	def get_monitor_file(self):
		return Path(self.get_logging_parameters("MONITOR_FILE"))

	def get_launch_monitor(self):
		return bool(self.get_logging_parameters("LAUNCH_MONITOR"))

	def get_datetime_format(self):
		return self.get_logging_parameters("DATETIME_FORMAT")

	# SECTION Getters for system parameters.
	def get_fpga(self):
		return self.get_system_parameters("FPGA")

	def get_usb_path(self):
		return self.get_system_parameters("USB_PATH")

	# SECTION Getters for hardware parameters
	def get_routing_type(self):
		return self.get_hardware_parameters("ROUTING")

	def get_serial_baud(self):
		return int(self.get_hardware_parameters("SERIAL_BAUD"))

	def get_accessed_columns(self):
		return self.get_hardware_parameters("ACCESSED_COLUMNS").split(",")

	def get_protected_columns(self):
		return self.get_hardware_parameters("PROTECTED_COLUMNS").split(",")

	def get_mcu_read_timeout(self):
		return float(self.get_hardware_parameters("MCU_READ_TIMEOUT"))
