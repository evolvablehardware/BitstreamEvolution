from pathlib import Path

# TODO Add handling for missing values
# NOTE Fails ungracefully at missing values currently

FAIL = '\033[91m'
ENDC = '\033[0m'
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

	def get_fitness_parameters(self, param):
		return self.__config_parser.get("FITNESS FUNC PARAMETERS", param)

	# SECTION Getters for GA Parameters.
	def get_population_size(self):
		return int(self.get_ga_parameters("POPULATION_SIZE"))

	# Since you can use target fitness instead of gens, we'll need options to see which is turned on
	# Using both will 
	def using_n_generations(self):
		return self.get_ga_parameters("GENERATIONS") != "IGNORE"

	def get_n_generations(self):
		return int(self.get_ga_parameters("GENERATIONS"))

	def using_target_fitness(self):
		return self.get_ga_parameters("TARGET_FITNESS") != "IGNORE"

	def get_target_fitness(self):
		return float(self.get_ga_parameters("TARGET_FITNESS"))

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
		input = self.get_ga_parameters("SELECTION")
		valid_vals = ["SINGLE_ELITE", "FRAC_ELITE", "CLASSIC_TOURN", "FIT_PROP_SEL", "RANK_PROP_SEL", "MAP_ELITES"]
		self.check_valid_value("selection type", input, valid_vals)
		return input

	def get_randomization_type(self):
		input = self.get_ga_parameters("RANDOMIZE_UNTIL")
		valid_vals = ["PULSE", "VARIANCE", "VOLTAGE", "NO"]
		self.check_valid_value("randomization type", input, valid_vals)
		return input

	def get_variance_threshold(self):
		return int(self.get_ga_parameters("VARIANCE_THRESHOLD"))

	def get_random_injection(self):
		return float(self.get_ga_parameters("RANDOM_INJECTION"))

	# RANDOM (randomizes all available bits), CLONE_SEED (copies one seed individual to every circuit), 
	# CLONE_SEED_MUTATE (clones the seed but also mutates each individual), EXISTING_POPULATION (uses the existing population files)
	def get_init_mode(self):
		input = self.get_ga_parameters("INIT_MODE")
		valid_vals = ["RANDOM", "CLONE_SEED", "CLONE_SEED_MUTATE", "EXISTING_POPULATION"]
		self.check_valid_value("init mode", input, valid_vals)
		return input

	def get_num_samples(self):
		return self.get_ga_parameters("NUM_SAMPLES")

	def get_sampling_method(self):
		input = self.get_ga_parameters("SAMPLING_METHOD")
		valid_vals = ["AVG", "MEDIAN", "PERCENTAGE", "OUTLIERS"]
		self.check_valid_value("sampling method", input, valid_vals)
		return input

	# We have 3 types of mode. There's FULLY_INTRINSIC, SIM_HARDWARE, and FULLY_SIM
	# FULLY_INTRINSIC: Runs the experiments on the actual hardware. Full normal experiment setup
	# SIM_HARDWARE: Simulation mode, but using an arbitrary function operating on compiled binary files
	# FULLY_SIM: Simulation mode, but operating on a small array of arbitrary bit values
	def get_simulation_mode(self):
		input = self.get_ga_parameters("SIMULATION_MODE")
		valid_vals = ["FULLY_INTRINSIC", "FULLY_SIM", "SIM_HARDWARE"]
		self.check_valid_value("simulation mode", input, valid_vals)
		return input
	
	def get_diversity_measure(self):
		input = self.get_ga_parameters("DIVERSITY_MEASURE")
		valid_vals = ["HAMMING_DIST", "UNIQUE"]
		self.check_valid_value("diversity measure", input, valid_vals)
		return input

	# Pulse Count, Variance
	def get_fitness_func(self):
		input = self.get_ga_parameters("FITNESS_FUNC")
		valid_vals = ["VARIANCE", "PULSE_COUNT", "COMBINED"]
		self.check_valid_value("fitness function", input, valid_vals)
		return input

	def get_fitness_mode(self):
		input = self.get_fitness_parameters("FITNESS_MODE")
		valid_vals = ["ADD", "MULT"]
		self.check_valid_value("fitness mode", input, valid_vals)
		return input
	
	def get_pulse_weight(self):
		return float(self.get_fitness_parameters("PULSE_WEIGHT"))

	def get_var_weight(self):
		return float(self.get_fitness_parameters("VAR_WEIGHT"))

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

	def get_best_file(self):
		return self.get_logging_parameters("BEST_FILE")

	def get_src_pops_dir(self):
		return Path(self.get_logging_parameters("SRC_POPULATIONS_DIR"))
		
	# There are 5 log levels (0-4)
	# 4 will log the most information, 1 will log the least
	# 0 will log nothing
	# So when putting a log level as an arg to a log event, higher numbers = seen less often
	def get_log_level(self):
		input = int(self.get_logging_parameters("LOG_LEVEL"))
		valid_vals = [0, 1, 2, 3, 4]
		self.check_valid_value("logging level", input, valid_vals)
		return input

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

	def get_mcu_read_timeout(self):
		return float(self.get_hardware_parameters("MCU_READ_TIMEOUT"))

	def check_valid_value(self, param_name, user_input, allowed_values):
		if not user_input in allowed_values:
			self.log_error("Invalid " + param_name + " '" + str(user_input) + "'. Valid selection types are: " + 
			", ".join(list(map(lambda x: str(x), allowed_values))))
			exit()
		
	def log_error(self, *msg):
		print("ERROR: ", FAIL, *msg, ENDC)
