from sys import stdout
from datetime import datetime
from subprocess import CalledProcessError, run
from os.path import exists
from os import mkdir
from pathlib import Path

# The window dimensions
LINE_WIDTH = 112
WIN_DIM="105x29"
DOUBLE_HLINE = "=" * LINE_WIDTH

MONITOR_FILE = None

TERM_CMD=["gnome-terminal", "--geometry={}".format(WIN_DIM), "--"]

# The time between animation frames in milliseconds
FRAME_DELAY = 200

# The spacing between matplotlib subplots as a percentage of the average
# axis height
SUBPLOT_SPACING = 0.5

# Formatting constants
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

README_FILE_HEADER = "FPGA/MCU [1] \n"

# TODO Utilize Python logging library
class Logger:
    def __init_analysis(self):
        # Make a directory to store data
        analysis = self.__config.get_analysis_directory()
        datetime_format = self.__config.get_datetime_format()
        current_time = str(datetime.now().strftime(datetime_format))
        current_time = current_time.replace('/', '-')
        self.__analysis_dir = analysis.joinpath(current_time)

        self.__analysis_a_dir = self.__analysis_dir.joinpath("asc/")
        self.__analysis_l_dir = self.__analysis_dir.joinpath("log/")
        self.__analysis_b_dir = self.__analysis_dir.joinpath("best/")
        self.__analysis_bh_dir = self.__analysis_dir.joinpath("best/html/")
        self.__analysis_ba_dir = self.__analysis_dir.joinpath("best/asc/")
        self.__analysis_bl_dir = self.__analysis_dir.joinpath("best/log/")

        if not self.__analysis_dir.exists():
            self.__analysis_dir.mkdir()
            self.__analysis_a_dir.mkdir()
            self.__analysis_l_dir.mkdir()
            self.__analysis_b_dir.mkdir()
            self.__analysis_bh_dir.mkdir()
            self.__analysis_ba_dir.mkdir()
            self.__analysis_bl_dir.mkdir()

        # Put the readme in the Analysis folder
        readme_file = open(self.__analysis_dir.joinpath("README.txt"), "w")
        readme_file.write(README_FILE_HEADER)
        readme_file.write(str(self.__experiment_explanation))
        readme_file.close()

    def __init_monitor(self):
        # Start the monitor
        self.log_event("Creating the monitor file...")

        self.log_monitor("{}{}".format(
            "Evolutionary Experiment Monitor".center(LINE_WIDTH),
            "\n"
        ))
        self.log_monitor("{}\n".format(DOUBLE_HLINE))
        self.log_monitor("Parameters and updates load during circuit evaluation")
        self.log_monitor(".\n" * 23)
        self.__monitor_file.flush()

        args = TERM_CMD + ["python3", "src/Monitor.py"]
        try:
            run(args, check=True, capture_output=True)
        except OSError as e:
            self.log_error("An error occured while launching the process")
        except CalledProcessError as e:
            self.log_error("An error occured in the launched process")

        self.log_event("Launching the Live Plot window...")
        args = TERM_CMD + ["python3", "src/PlotEvolutionLive.py"]
        try:
            run(args, check=True, capture_output=True)
        except OSError as e:
            self.log_error("An error occured while launching the process")
        except CalledProcessError as e:
            self.log_error("An error occured in the launched process")
            self.log_error(e)

    def __init__(self, config, explanation):
        self.__config = config
        self.__monitor_file = open(config.get_monitor_file(), "w")
        self.__log_file = stdout
        self.__experiment_explanation = explanation

        # Ensure the logs exists and have been cleared. Not happy with
        # this method, but couldn't find a better way to do it.
        open("workspace/alllivedata.log", "w").close()
        open("workspace/bestlivedata.log", "w").close()
        open("workspace/waveformlivedata.log", "w").close()

        # Determine if we need to the to initialize the analysis and
        # if so, do so.
        if explanation != "test":
            self.__init_analysis()

        # Determine whether we need to launch the monitor and launch it
        # if so.
        if config.get_launch_monitor():
            self.__init_monitor()

    def log_generation(self, population, epoch_time):
        self.log_event(DOUBLE_HLINE)
        self.log_event(DOUBLE_HLINE)
        self.log_event(DOUBLE_HLINE)

        current_best_circuit = population.get_current_best_circuit()
        overall_best_circuit = population.get_overall_best_circuit_info()

        self.log_event("CURRENT BEST: {} : EPOCH {} : FITNESS {}".format(
            str(overall_best_circuit.name),
            str(population.get_best_epoch()),
            str(overall_best_circuit.fitness)
        ))

        print("HIGHEST FITNESS OF EPOCH {} IS: {} = {} over {} seconds".format(
            str(population.get_current_epoch()),
            str(current_best_circuit),
            str(current_best_circuit.get_fitness()),
            str(epoch_time)
        ))

        self.log_event(DOUBLE_HLINE)
        self.log_event(DOUBLE_HLINE)
        self.log_event(DOUBLE_HLINE)

    def log_monitor(self, *msg):
        print(*msg, file=self.__monitor_file)

    def log_event(self, *msg):
        print(*msg, file=self.__log_file)

    def log_info(self, *msg):
        print("INFO: ", OKBLUE, *msg, ENDC, file=self.__log_file)

    def log_warning(self, *msg):
        print("WARNING: ", WARNING, *msg, ENDC, file=self.__log_file)

    def log_error(self, *msg):
        print("ERROR: ", FAIL, *msg, ENDC, file=self.__log_file)

    def log_critical(self, *msg):
        print("CRITICAL: ", FAIL, *msg, ENDC, file=self.__log_file)
