from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from datetime import datetime
from subprocess import CalledProcessError, run
from os.path import exists
from os.path import join
from os import mkdir
from shutil import copytree
from shutil import rmtree
from datetime import datetime

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

@dataclass
class LoggerConfig:
    plots_dir: Path
    launch_plots: bool
    is_sensitivity: bool
    frame_interval: int
    log_file: Path
    log_level: int
    save_log: bool
    datetime_format: str

# TODO Utilize Python logging library
class Logger:
    def __init_monitor(self):
        # Start the monitor
        # self.log_event(1, "Creating the monitor file...")

        self.log_monitor(1, "{}{}".format(
            "Evolutionary Experiment Monitor".center(LINE_WIDTH),
            "\n"
        ))
        self.log_monitor("", "{}".format(DOUBLE_HLINE))
        # self.log_monitor(1, "Parameters and updates load during circuit evaluation")
        # self.log_monitor(1, ".\n" * 23)
        self.log_monitor("", str(self.__experiment_explanation))
        self.log_monitor("", "{}".format(DOUBLE_HLINE))
        # self.log_monitor("", self.__config.get_raw_data())
        self.log_monitor("", "{}".format(DOUBLE_HLINE))
        self.__monitor_file.flush()

        # args = TERM_CMD + ["python3", "src/Monitor.py"]
        # try:
        #     run(args, check=True, capture_output=True)
        # except OSError as e:
        #     self.log_error(1, "An error occured while launching Monitor.py")
        # except CalledProcessError as e:
        #     self.log_error(1, "An error occured in Monitor.py")

        #set up directory for saving files
        plots_dir = self.__config.plots_dir
        try:
            rmtree(plots_dir)
        except OSError as error:
            print(error)

        if not plots_dir.exists():
            plots_dir.mkdir()

        if self.__config.launch_plots:
            if self.__config.is_sensitivity:
                args = TERM_CMD + ["python3", "src/PlotSensitivityLive.py"]
            else: 
                args = TERM_CMD + ["python3", "src/PlotEvolutionLive.py", "--frame-interval", str(self.__config.frame_interval)]
            
            try:
                run(args, check=True, capture_output=True)
            except OSError as e:
                self.log_error(1, "An error occured while launching PlotEvolutionLive.py")
            except CalledProcessError as e:
                self.log_error(1, "An error occured in PlotEvolutionLive.py")
                self.log_error(1, e)

    def __init__(self, explanation: str, logger_config: LoggerConfig):
        self.__monitor_file = open(logger_config.log_file, "w")
        self.__log_file = stdout
        self.__config = logger_config
        self.__experiment_explanation = explanation

        # Ensure the logs exists and have been cleared. Not happy with
        # this method, but couldn't find a better way to do it.
        open("workspace/alllivedata.log", "w").close()
        open("workspace/bestlivedata.log", "w").close()
        open("workspace/waveformlivedata.log", "w").close()
        open("workspace/maplivedata.log", "w").close()
        open("workspace/heatmaplivedata.log", "w").close()
        open("workspace/pulselivedata.log", "w").close()
        open("workspace/violinlivedata.log", "w").close()
        open("workspace/poplivedata.log", "w").close()
        open("workspace/randomizationdata.log", "w").close()
        open("workspace/fitnesssensitivity.log", "w").close()
        open("workspace/bitstream_avg.log", "w").close()
        if not exists("workspace/template"):
            mkdir("workspace/template")

        if exists("workspace/plots"):
            rmtree("workspace/plots")
        if not exists("workspace/plots"):
            mkdir("workspace/plots")
        # Determine if we need to the to initialize the analysis and
        # if so, do so.
        # currently removed since we're not currently storing any data, so there's a bunch of empty files and directories
        # if explanation != "test":
        #     self.__init_analysis()

        # Determine whether we need to launch the monitor and launch it
        # if so.
        # if config.get_launch_monitor():
        #     self.__init_monitor()
        self.__init_monitor()

    def log_generation(self, population, epoch_time):
        self.log_event(2, DOUBLE_HLINE)
        self.log_event(2, DOUBLE_HLINE)
        self.log_event(2, DOUBLE_HLINE)

        current_best_circuit = population.get_current_best_circuit()
        overall_best_circuit = population.get_overall_best_circuit_info()

        self.log_event(2, "CURRENT BEST: {} : EPOCH {} : FITNESS {}".format(
            str(overall_best_circuit.name),
            str(population.get_best_epoch()),
            str(overall_best_circuit.fitness)
        ))

        self.log_event(2, "HIGHEST FITNESS OF EPOCH {} IS: {} = {} over {} seconds".format(
            str(population.get_current_epoch()),
            str(current_best_circuit),
            str(current_best_circuit.get_fitness()),
            str(epoch_time)
        ))

        self.log_event(2, DOUBLE_HLINE)
        self.log_event(2, DOUBLE_HLINE)
        self.log_event(2, DOUBLE_HLINE)

    def log_monitor(self, prefix,  *msg):
        if self.__config.save_log:
            now = datetime.now()
            print(now, prefix, *msg, file=self.__monitor_file)

    def log_event(self, level, *msg):
        if self.__config.log_level >= level:
            print(*msg, file=self.__log_file)
            self.log_monitor("", *msg)

    def log_info(self, level, *msg):
        if self.__config.log_level >= level:
            print("INFO: ", OKBLUE, *msg, ENDC, file=self.__log_file)
            self.log_monitor("INFO: ", *msg)

    def log_warning(self, level, *msg):
        if self.__config.log_level >= level:
            print("WARNING: ", WARNING, *msg, ENDC, file=self.__log_file)
            self.log_monitor("WARNING: ", *msg)

    def log_error(self, level, *msg):
        if self.__config.log_level >= level:
            print("ERROR: ", FAIL, *msg, ENDC, file=self.__log_file)
            self.log_monitor("ERROR: ", *msg)

    def log_critical(self, level, *msg):
        if self.__config.log_level >= level:
            print("CRITICAL: ", FAIL, *msg, ENDC, file=self.__log_file)
            self.log_monitor("CRITICAL: ", *msg)

    def save_workspace(self, directory):
        self.__monitor_file.close()
        current_time = str(datetime.now().strftime(self.__config.datetime_format))
        current_time = current_time.replace('/', '-')
        copytree("./workspace", join(directory, current_time))
