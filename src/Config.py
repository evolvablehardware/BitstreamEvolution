from pathlib import Path
from configparser import ConfigParser
from configparser import NoOptionError

# TODO Add handling for missing values
# NOTE Fails ungracefully at missing values currently

FAIL = '\033[91m'
ENDC = '\033[0m'
class Config:
	def __init__(self, filename):
		self.__config_parser = ConfigParser()
		self.__config_parser.read(filename)
		self.__filename = filename

	def add_logger(self, logger):
		self.__logger = logger

	# SECTION Generic getters for options in the various sections.
	def get_top_parameters(self, param):
		return self.__config_parser.get("TOP-LEVEL PARAMETERS", param)
	
	def get_fitness_parameters(self, param):
		return self.__config_parser.get("FITNESS PARAMETERS", param)
	
	def get_ga_parameters(self, param):
		return self.__config_parser.get("GA PARAMETERS", param)
	
	def get_init_parameters(self, param):
		return self.__config_parser.get("INITIALIZATION PARAMETERS", param)
	
	def get_stop_parameters(self, param):
		return self.__config_parser.get("STOPPING CONDITION PARAMETERS", param)

	def get_logging_parameters(self, param):
		return self.__config_parser.get("LOGGING PARAMETERS", param)

	def get_system_parameters(self, param):
		return self.__config_parser.get("SYSTEM PARAMETERS", param)

	def get_hardware_parameters(self, param):
		return self.__config_parser.get("HARDWARE PARAMETERS", param)
	
	# SECTION Getters for Top-Level Parameters.
	# We have 3 types of mode. There's FULLY_INTRINSIC, SIM_HARDWARE, and FULLY_SIM
	# FULLY_INTRINSIC: Runs the experiments on the actual hardware. Full normal experiment setup
	# SIM_HARDWARE: Simulation mode, but using an arbitrary function operating on compiled binary files
	# FULLY_SIM: Simulation mode, but operating on a small array of arbitrary bit values
	def get_simulation_mode(self):
		input = self.get_top_parameters("SIMULATION_MODE")
		valid_vals = ["FULLY_INTRINSIC", "FULLY_SIM", "SIM_HARDWARE"]
		self.check_valid_value("simulation mode", input, valid_vals)
		return input
	
	# SECTION Getters for Fitness Parameters.
	def get_fitness_func(self):
		input = self.get_fitness_parameters("FITNESS_FUNC")
		valid_vals = ["VARIANCE", "PULSE_COUNT", "COMBINED"]
		self.check_valid_value("fitness function", input, valid_vals)
		return input
	
	def get_desired_frequency(self):
		desiredFreq = int(self.get_fitness_parameters("DESIRED_FREQ"))
		if desiredFreq < 0:
			self.__log_error(1, "Invalid desired frequency " + str(desiredFreq) + "'. Must be greater than zero.")
			exit()
		return desiredFreq
	
	def get_combined_mode(self):
		input = self.get_fitness_parameters("COMBINED_MODE")
		valid_vals = ["ADD", "MULT"]
		self.check_valid_value("combined mode", input, valid_vals)
		return input
	
	def get_pulse_weight(self):
		return float(self.get_fitness_parameters("PULSE_WEIGHT"))

	def get_var_weight(self):
		return float(self.get_fitness_parameters("VAR_WEIGHT"))


	# SECTION Getters for GA Parameters.
	def get_population_size(self):
		popSize = int(self.get_ga_parameters("POPULATION_SIZE"))
		if popSize < 1:
			self.__log_error(1, "Invalid population size " + str(popSize) + "'. Must be greater than zero.")
			exit()
		return popSize

	def get_mutation_probability(self):
		prob = float(self.get_ga_parameters("MUTATION_PROBABILITY"))
		if prob < 0.0:
			self.__log_error(1, "Invalid mutation probability " + str(prob) + "'. Must be greater than zero.")
			exit()
		if prob > 1.0:
			self.__log_error(1, "Invalid mutation probability " + str(prob) + "'. Must be less than one.")
			exit()
		return prob

	def get_crossover_probability(self):
		prob = float(self.get_ga_parameters("CROSSOVER_PROBABILITY"))
		if prob < 0.0:
			self.__log_error(1, "Invalid crossover probability " + str(prob) + "'. Must be greater than zero.")
			exit()
		if prob > 1.0:
			self.__log_error(1, "Invalid crossover probability " + str(prob) + "'. Must be less than one.")
			exit()
		return prob

	def get_elitism_fraction(self):
		frac = float(self.get_ga_parameters("ELITISM_FRACTION"))
		if frac < 0.0:
			self.__log_error(1, "Invalid elitism fraction " + str(frac) + "'. Must be greater than zero.")
			exit()
		if frac > 1.0:
			self.__log_error(1, "Invalid elistism probability " + str(frac) + "'. Must be less than one.")
			exit()
		return frac

	def get_selection_type(self):
		input = self.get_ga_parameters("SELECTION")
		valid_vals = ["SINGLE_ELITE", "FRAC_ELITE", "CLASSIC_TOURN", "FIT_PROP_SEL", "RANK_PROP_SEL", "MAP_ELITES"]
		self.check_valid_value("selection type", input, valid_vals)
		return input

	def get_random_injection(self):
		frac = float(self.get_ga_parameters("RANDOM_INJECTION"))
		if frac < 0.0:
			self.__log_error(1, "Invalid random injection rate " + str(frac) + "'. Must be greater than zero.")
			exit()
		if frac > 1.0:
			self.__log_error(1, "Invalid random injection rate " + str(frac) + "'. Must be less than one.")
			exit()
		return frac
	
	def get_diversity_measure(self):
		input = self.get_ga_parameters("DIVERSITY_MEASURE")
		valid_vals = ["HAMMING_DIST", "UNIQUE"]
		self.check_valid_value("diversity measure", input, valid_vals)
		return input
	
	# SECTION Getters for Initialization Parameters.
	# RANDOM (randomizes all available bits), CLONE_SEED (copies one seed individual to every circuit), 
	# CLONE_SEED_MUTATE (clones the seed but also mutates each individual), EXISTING_POPULATION (uses the existing population files)
	def get_init_mode(self):
		input = self.get_init_parameters("INIT_MODE")
		valid_vals = ["RANDOM", "CLONE_SEED", "CLONE_SEED_MUTATE", "EXISTING_POPULATION"]
		self.check_valid_value("init mode", input, valid_vals)
		return input
	
	def get_randomization_type(self):
		input = self.get_init_parameters("RANDOMIZE_UNTIL")
		valid_vals = ["PULSE", "VARIANCE", "VOLTAGE", "NO"]
		self.check_valid_value("randomization type", input, valid_vals)
		return input
	
	def get_randomize_threshold(self):
		threshold = float(self.get_init_parameters("RANDOMIZE_THRESHOLD"))
		if threshold < 0:
			self.__log_error(1, "Invalid random threshold " + str(threshold) + "'. Must be greater than zero.")
			exit()
		return threshold

	def get_randomize_mode(self):
		input = self.get_init_parameters("RANDOMIZE_MODE")
		valid_vals = ["RANDOM", "MUTATE"]
		self.check_valid_value("randomization mode", input, valid_vals)
		return input
	
	# SECTION Getters for stopping conditions parameters.
	# Since you can use target fitness instead of gens, we'll need options to see which is turned on
	# Using both will 
	def using_n_generations(self):
		return self.get_stop_parameters("GENERATIONS") != "IGNORE"

	def get_n_generations(self):
		try:
			nGenerations = int(self.get_stop_parameters("GENERATIONS"))
		except:
			self.__log_warning(2, "Non-int user input for number of generations. Program will not terminate based on the number of generations",)
			return "IGNORE"
		if nGenerations < 1:
			self.__log_error(1, "Invalid number of generations " + str(nGenerations) + "'. Must be greater than zero.")
			exit()
		return nGenerations

	def using_target_fitness(self):
		return self.get_stop_parameters("TARGET_FITNESS") != "IGNORE"

	def get_target_fitness(self):
		try:
			targetFitness = float(self.get_stop_parameters("TARGET_FITNESS"))
		except:
			self.__log_warning(2, "Non-int user input for target fitness. Program will not terminate based on fitness")
			return "IGNORE"
		if targetFitness < 0.0:
			self.__log_error(1, "Invalid target fitness " + str(targetFitness) + "'. Must be greater than zero.")
			exit()
		return targetFitness

	# SECTION Getters for logging parameters.
	def get_plots_directory(self):
		try:
			return Path(self.get_logging_parameters("PLOTS_DIR"))
		except NoOptionError:
			return Path("./workspace/plots")
	
	def get_save_plots(self):
		try:
			input = self.get_logging_parameters("save_plots")
			return input == "true" or input == "True"
		except NoOptionError:
			return True	
	
	def get_output_directory(self):
		try:
			return Path(self.get_logging_parameters("OUTPUT_DIR"))
		except NoOptionError:
			return Path("./prev_workspaces")
	
	def get_backup_workspace(self):
		try:
			input = self.get_logging_parameters("backup_workspace")
			return input == "true" or input == "True"
		except NoOptionError:
				return True	
	
	def get_asc_directory(self):
		try:
			return Path(self.get_logging_parameters("ASC_DIR"))
		except NoOptionError:
			return Path("./workspace/experiment_asc")

	def get_bin_directory(self):
		try:
			return Path(self.get_logging_parameters("BIN_DIR"))
		except NoOptionError:
			return Path("./workspace/experiment_bin")

	def get_data_directory(self):
		try:
			return Path(self.get_logging_parameters("DATA_DIR"))
		except NoOptionError:
			return Path("./workspace/experiment_data")

	def get_analysis_directory(self):
		try:
			return Path(self.get_logging_parameters("ANALYSIS"))
		except NoOptionError:
			return Path("./workspace/analysis")

	def get_log_file(self):
		try:
			return Path(self.get_logging_parameters("LOG_FILE"))
		except NoOptionError:
			return Path("./workspace/log")

	def get_save_log(self):
		try:
			input = self.get_logging_parameters("save_log")
			return input == "true" or input == "True"
		except NoOptionError:
			return True	

	def get_datetime_format(self):
		try:
			return self.get_logging_parameters("DATETIME_FORMAT")
		except NoOptionError:
			return Path("%%m/%%d/%%Y - %%H:%%M:%%S")

	def get_best_file(self):
		try:
			return self.get_logging_parameters("BEST_FILE")
		except NoOptionError:
			return Path("./workspace/best.asc")

	def get_src_pops_dir(self):
		try:
			return Path(self.get_logging_parameters("SRC_POPULATIONS_DIR"))
		except NoOptionError:
			return Path("./workspace/source_population")
		
	# There are 5 log levels (0-4)
	# 4 will log the most information, 1 will log the least
	# 0 will log nothing
	# So when putting a log level as an arg to a log event, higher numbers = seen less often
	def get_log_level(self):
		input = int(self.get_logging_parameters("LOG_LEVEL"))
		valid_vals = [0, 1, 2, 3, 4, 5]
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
			self.__log_error(1, "Invalid " + param_name + " '" + str(user_input) + "'. Valid selection types are: " + 
			", ".join(list(map(lambda x: str(x), allowed_values))))
			exit()
	
	def validate_all(self):
		self.get_simulation_mode()

		self.get_fitness_func()
		self.get_desired_frequency()
		self.get_combined_mode()
		self.get_pulse_weight()
		self.get_var_weight()

		self.get_population_size()
		self.get_mutation_probability()
		self.get_crossover_probability()
		self.get_elitism_fraction()
		self.get_selection_type()
		self.get_diversity_measure()
		self.get_random_injection()

		self.get_init_mode()
		self.get_randomization_type()
		self.get_randomize_threshold()
		self.get_randomize_mode()

		self.using_n_generations()
		self.get_n_generations()
		self.using_target_fitness()
		self.get_target_fitness()
	
		self.get_log_level()
		self.get_save_log()
		self.get_save_plots()
		self.get_log_file()
		self.get_plots_directory()
		self.get_asc_directory()
		self.get_bin_directory()
		self.get_data_directory()
		self.get_analysis_directory()
		self.get_best_file()
		self.get_src_pops_dir()
		self.get_datetime_format()

		self.get_fpga()
		self.get_usb_path()
		
		self.get_routing_type()
		self.get_serial_baud()
		self.get_accessed_columns()
		self.get_mcu_read_timeout()
		
	def __log_event(self, level, *event):
		"""
		Emit an event-level log. This function is fulfilled through
		the logger.
		"""
		self.__logger.log_event(level, *event)

	def __log_info(self, level, *info):
		"""
		Emit an info-level log. This function is fulfilled through
		the logger.
		"""
		self.__logger.log_info(level, *info)

	def __log_error(self, level, *error):
		"""
		Emit an error-level log. This function is fulfilled through
		the logger.
		"""
		self.__logger.log_error(level, *error)

	def __log_warning(self, level, *warning):
		"""
		Emit a warning-level log. This function is fulfilled through
		the logger.
		"""
		self.__logger.log_warning(level, *warning)

	# used by the logger to store a back-up of the config
	# probably not the cleanest way to do this
	def get_raw_data(self):
		f = open(self.__filename, "r")
		return f.read()
