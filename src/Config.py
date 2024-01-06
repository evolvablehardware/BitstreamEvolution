from pathlib import Path
from configparser import ConfigParser
from configparser import NoOptionError
from xml.dom import NotFoundErr
from datetime import datetime

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

	def get_sensitivity_parameters(self, param):
		return self.__config_parser.get("FITNESS SENSITIVITY PARAMETERS", param)
	
	def get_transfer_parameters(self, param):
		return self.__config_parser.get("TRANSFERABILITY PARAMETERS", param)
	
	# SECTION Getters for Top-Level Parameters.
	# We have 3 types of mode. There's FULLY_INTRINSIC, SIM_HARDWARE, and FULLY_SIM
	# FULLY_INTRINSIC: Runs the experiments on the actual hardware. Full normal experiment setup
	# SIM_HARDWARE: Simulation mode, but using an arbitrary function operating on compiled binary files
	# FULLY_SIM: Simulation mode, but operating on a small array of arbitrary bit values
	def get_simulation_mode(self):
		input = self.get_top_parameters("SIMULATION_MODE")
		valid_vals = ["FULLY_INTRINSIC", "FULLY_SIM", "SIM_HARDWARE", "INTRINSIC_SENSITIVITY"]
		self.check_valid_value("simulation mode", input, valid_vals)
		return input
	
	# SECTION Getters for Fitness Parameters.
	def get_fitness_func(self):
		input = self.get_fitness_parameters("FITNESS_FUNC")
		# We're leaving "PULSE_COUNT" for backwards-compatibility
		# It will use the sensitive function
		valid_vals = ["VARIANCE", "PULSE_COUNT", "TOLERANT_PULSE_COUNT", "SENSITIVE_PULSE_COUNT", "COMBINED", "PULSE_CONSISTENCY"]
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
	
	def get_num_samples(self):
		value = int(self.get_fitness_parameters("NUM_SAMPLES"))
		if value < 1:
			self.__log_error(1, "Invalid number of samples " + str(value) + "'. Must be greater than zero.")
			exit()
		return value

	def get_num_passes(self):
		value = int(self.get_fitness_parameters("NUM_PASSES"))
		if value < 1:
			self.__log_error(1, "Invalid number of passes " + str(value) + "'. Must be greater than zero.")
			exit()
		return value

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
		valid_vals = ["HAMMING_DIST", "UNIQUE", "NONE"]
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

	# SECTION Getters for fitness sensitivity parameters.
	def get_test_circuit(self):
		try:
			return Path(self.get_sensitivity_parameters("TEST_CIRCUIT"))
		except NoOptionError:
			self.__log_error(1, "Invalid file path " + self.get_sensitivity_parameters("TEST_CIRCUIT") + " for test circuit.")

	def using_sensitivity_trials(self):
		return self.get_sensitivity_parameters("SENSITIVITY_TRIALS") != "IGNORE"

	def get_sensitivity_trials(self):
		try:
			trials = int(self.get_sensitivity_parameters("SENSITIVITY_TRIALS"))
		except:
			self.__log_warning(1, "Non-int user input for the number of sensitivity trials. Program will not terminate based on the number of generations")
			return "IGNORE"
		if trials < 1:
			self.__log_error(1, "Invalid number of sensitivity trials" + str(trials) + "'. Must be greater than zero.")
			exit()
		return trials
	
	def using_sensitivity_time(self):
		return self.get_sensitivity_parameters("SENSITIVITY_TIME") != "IGNORE"

	def get_sensitivity_time(self):
		try:
			date_time = datetime.strptime(self.get_sensitivity_parameters("SENSITIVITY_TIME"), '%H:%M:%S')
			seconds = 3600*date_time.hour + 60*date_time.minute + date_time.second
			print(seconds)
		except ValueError:
			self.__log_warning(1, "Non-int user input for the amount of time to sensitivity trials. Program will not terminate based on the number of generations")
			return "IGNORE"
		if seconds < 0:
			self.__log_error(1, "Invalid amount of time to do sensitivity trials: " + str(seconds) + "'. Must be greater than zero.")
			exit()
		return seconds
	
	#SECTION getts for transferability experiment parameters
	def using_transfer_interval(self):
		return isinstance(self.get_transfer_interval(), int)
	
	def get_transfer_sample(self):
		return self.get_transfer_parameters("TRANSFER_INTERVAl") == "SAMPLE"

	def get_transfer_interval(self):
		try:
			interval = int(self.get_transfer_parameters("TRANSFER_INTERVAl"))
		except:
			# self.__log_info(2, "Non-int user input for transfer interval. Evolution will occur on only one FPGA")
			return "IGNORE"
		if interval < 1:
			self.__log_error(1, "Invalid transfer interval size " + str(interval) + "'. Must be greater than zero.")
			exit()
		return interval
	
	def get_fpga2(self):
		return self.get_transfer_parameters("FPGA2")

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

	def get_generations_directory(self):
		try:
			return Path(self.get_logging_parameters("GENERATIONS_DIR"))
		except NoOptionError:
			return Path("./workspace/generations")

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

	def get_use_ovr_best(self):
		try:
			input = self.get_logging_parameters("show_ovr_best")
			return input == "true" or input == "True"
		except NoOptionError:
			return True	

	# SECTION Getters for system parameters.
	def get_fpga(self):
		return self.get_system_parameters("FPGA")

	def get_usb_path(self):
		return self.get_system_parameters("USB_PATH")
	
	def get_upload_to_arduino(self):
		input = self.get_system_parameters("auto_upload_to_arduino")
		return input == "true" or input == "True"
		
	# SECTION Getters for hardware parameters
	def get_routing_type(self):
		input = self.get_hardware_parameters("ROUTING")
		valid_vals = ["MOORE", "NEWSE"]
		self.check_valid_value("routing type", input, valid_vals)
		return input

	def get_serial_baud(self):
		return int(self.get_hardware_parameters("SERIAL_BAUD"))

	def get_accessed_columns(self):
		return self.get_hardware_parameters("ACCESSED_COLUMNS").split(",")
	
	def get_using_configurable_io(self):
		input = self.get_hardware_parameters("configurable_io")
		return input == "true" or input == "True"
	
	def get_input_pins(self):
		valid_vals = [112, 113, 114, 115, 116, 117, 118, 119, 44, 45, 47, 48, 56, 60, 61, 62]
		pins = self.get_hardware_parameters("INPUT_PINS").split(",")
		for pin in pins:
			self.check_valid_value("input pin", int(pin), valid_vals)
		return pins
	
	def get_output_pins(self):
		valid_vals = [112, 113, 114, 115, 116, 117, 118, 119, 44, 45, 47, 48, 56, 60, 61, 62]
		pins = self.get_hardware_parameters("OUTPUT_PINS").split(",")
		for pin in pins:
			self.check_valid_value("output pin", int(pin), valid_vals)
		return pins

	def get_mcu_read_timeout(self):
		return float(self.get_hardware_parameters("MCU_READ_TIMEOUT"))

	def check_valid_value(self, param_name, user_input, allowed_values):
		if not user_input in allowed_values:
			self.__log_error(1, "Invalid " + param_name + " '" + str(user_input) + "'. Valid parameters are: " + 
			", ".join(list(map(lambda x: str(x), allowed_values))))
			exit()
	
	def validate_all(self):
		self.get_simulation_mode()
		self.validate_fitness_params()

		if self.get_simulation_mode == 'INTRINSIC_SENSITIVITY':
			self.validate_sensitivity_params()
		else:
			self.validate_ga_params()
			self.validate_init_params()
			self.validate_stopping_params()

		self.validate_logging_params()
		
		if self.get_simulation_mode != 'FULLY_SIM' and self.get_simulation_mode != 'SIM_HARDWARE':
			self.validate_system_params()
			self.validate_hardware_params()

		# Make sure user follows our requirements
		# Pulse consistency must have >=1 passes and >=1 samples
		if self.get_fitness_func() == "PULSE_CONSISTENCY" and (self.get_num_passes() * self.get_num_samples()) <= 1:
			self.__log_error(1, "PULSE_CONSISTENCY function can only be used with multiple samples/passes")
			exit()
		# MAP elites can only be used with VARIANCE, COMBINED, and PULSE CONSISTENCY
		if self.get_selection_type() == "MAP_ELITES":
			if self.get_fitness_func() not in ["VARIANCE", "COMBINED", "PULSE_CONSISTENCY"]:
				self.__log_error(1, "MAP_ELITES selection can only be used with the following fitness functions: " +
				"VARIANCE, COMBINED, PULSE_CONSISTENCY")
				exit()

	# True if the fitness function counts pulses
	def is_pulse_func(self):
		return (self.get_fitness_func() == 'PULSE_COUNT' or self.get_fitness_func() == 'TOLERANT_PULSE_COUNT' 
            	or self.get_fitness_func() == 'SENSITIVE_PULSE_COUNT' or self.get_fitness_func() == 'PULSE_CONSISTENCY')
	
	# Contrary to the above, this only returns true if the target is to count pulses for a target frequency
	def is_pulse_count(self):
		return (self.get_fitness_func() == 'PULSE_COUNT' or self.get_fitness_func() == 'TOLERANT_PULSE_COUNT' 
				or self.get_fitness_func() == 'SENSITIVE_PULSE_COUNT')
	
	def get_map_elites_dimension(self):
		if self.get_fitness_func() in ['PULSE_CONSISTENCY']:
			return 1
		elif self.get_fitness_func() in ['VARIANCE', 'COMBINED']:
			return 2

	def validate_fitness_params(self):
		self.get_fitness_func()

		if self.get_fitness_func() == "COMBINED":
			self.get_combined_mode()
			self.get_pulse_weight()
			self.get_var_weight()

		if self.is_pulse_func():
			self.get_desired_frequency()
			self.get_num_samples()
			self.get_num_passes()

	def validate_ga_params(self):
		self.get_population_size()
		self.get_mutation_probability()
		self.get_crossover_probability()
		self.get_elitism_fraction()
		self.get_selection_type()
		self.get_diversity_measure()
		self.get_random_injection()

	def validate_init_params(self):
		self.get_init_mode()
		self.get_randomization_type()
		self.get_randomize_threshold()
		self.get_randomize_mode()

	def validate_stopping_params(self):
		self.using_n_generations()
		self.get_n_generations()
		self.using_target_fitness()
		self.get_target_fitness()

	def validate_logging_params(self):
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
		self.get_generations_directory()
		self.get_use_ovr_best()

	def validate_system_params(self):
		self.get_fpga()
		self.get_usb_path()

	def validate_hardware_params(self):
		self.get_routing_type()
		self.get_serial_baud()
		self.get_accessed_columns()
		self.get_mcu_read_timeout()
		if self.get_using_configurable_io():
			self.get_input_pins()
			self.get_output_pins()

	def validate_sensitivity_params(self):
		self.get_test_circuit()
		self.get_sensitivity_trials()
		
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
