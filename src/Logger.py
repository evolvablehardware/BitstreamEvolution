from datetime import datetime
from os import mkdir
from os.path import exists, join
from pathlib import Path
from shutil import copytree, rmtree
from subprocess import CalledProcessError, run
from sys import stdout

# The window dimensions
LINE_WIDTH = 112
WIN_DIM = "105x29"
DOUBLE_HLINE = "=" * LINE_WIDTH

MONITOR_FILE = None

TERM_CMD = ["gnome-terminal", f"--geometry={WIN_DIM}", "--"]

# The time between animation frames in milliseconds
FRAME_DELAY = 200

# The spacing between matplotlib subplots as a percentage of the average
# axis height
SUBPLOT_SPACING = 0.5

# Formatting constants
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

README_FILE_HEADER = "FPGA/MCU [1] \n"


# TODO Utilize Python logging library
class Logger:
    def __init_analysis(self):
        # Make a directory to store data
        analysis = self.__config.get_analysis_directory()
        datetime_format = self.__config.get_datetime_format()
        current_time = str(datetime.now().strftime(datetime_format))
        current_time = current_time.replace("/", "-")
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
        with open(self.__analysis_dir.joinpath("README.txt"), "w") as readme_file:
            readme_file.write(README_FILE_HEADER)
            readme_file.write(str(self.__experiment_explanation))

    def __init_monitor(self):
        # Start the monitor
        # self.log_event(1, "Creating the monitor file...")

        self.log_monitor(
            1, "{}{}".format("Evolutionary Experiment Monitor".center(LINE_WIDTH), "\n")
        )
        self.log_monitor("", f"{DOUBLE_HLINE}")
        # self.log_monitor(1, "Parameters and updates load during circuit evaluation")
        # self.log_monitor(1, ".\n" * 23)
        self.log_monitor("", str(self.__experiment_explanation))
        self.log_monitor("", f"{DOUBLE_HLINE}")
        self.log_monitor("", self.__config.get_raw_data())
        self.log_monitor("", f"{DOUBLE_HLINE}")
        self.__monitor_file.flush()

        # args = TERM_CMD + ["python3", "src/Monitor.py"]
        # try:
        #     run(args, check=True, capture_output=True)
        # except OSError as e:
        #     self.log_error(1, "An error occured while launching Monitor.py")
        # except CalledProcessError as e:
        #     self.log_error(1, "An error occured in Monitor.py")

        # set up directory for saving files
        plots_dir = self.__config.get_plots_directory()
        try:
            rmtree(plots_dir)
        except OSError as error:
            print(error)

        if not plots_dir.exists():
            plots_dir.mkdir()

        if self.__config.get_launch_plots():
            if self.__config.get_simulation_mode() == "INTRINSIC_SENSITIVITY":
                args = [*TERM_CMD, "python3", "src/PlotSensitivityLive.py"]
            else:
                args = [
                    *TERM_CMD,
                    "python3",
                    "src/PlotEvolutionLive.py",
                    "--frame-interval",
                    str(self.__config.get_frame_interval()),
                ]

            try:
                run(args, check=True, capture_output=True)
            except OSError:
                self.log_error(1, "An error occured while launching PlotEvolutionLive.py")
            except CalledProcessError as e:
                self.log_error(1, "An error occured in PlotEvolutionLive.py")
                self.log_error(1, e)

    def __init__(self, config, explanation):
        self.__config = config
        self.__config.add_logger(self)
        self.__monitor_file = open(config.get_log_file(), "w")  # noqa: SIM115 - managed by close()
        self.__log_file = stdout
        self.__experiment_explanation = explanation

        # Ensure the logs exist and have been cleared
        log_files = [
            "workspace/alllivedata.log",
            "workspace/bestlivedata.log",
            "workspace/waveformlivedata.log",
            "workspace/maplivedata.log",
            "workspace/heatmaplivedata.log",
            "workspace/pulselivedata.log",
            "workspace/violinlivedata.log",
            "workspace/poplivedata.log",
            "workspace/randomizationdata.log",
            "workspace/fitnesssensitivity.log",
            "workspace/bitstream_avg.log",
        ]
        for log_file in log_files:
            Path(log_file).write_text("")
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

        self.log_event(
            2,
            f"CURRENT BEST: {overall_best_circuit.name!s} : EPOCH {population.get_best_epoch()!s} : FITNESS {overall_best_circuit.fitness!s}",
        )

        self.log_event(
            2,
            f"HIGHEST FITNESS OF EPOCH {population.get_current_epoch()!s} IS: {current_best_circuit!s} = {current_best_circuit.get_fitness()!s} over {epoch_time!s} seconds",
        )

        self.log_event(2, DOUBLE_HLINE)
        self.log_event(2, DOUBLE_HLINE)
        self.log_event(2, DOUBLE_HLINE)

    def log_monitor(self, prefix, *msg):
        if self.__config.get_save_log():
            now = datetime.now()
            print(now, prefix, *msg, file=self.__monitor_file)

    def log_event(self, level, *msg):
        if self.__config.get_log_level() >= level:
            print(*msg, file=self.__log_file)
            self.log_monitor("", *msg)

    def log_info(self, level, *msg):
        if self.__config.get_log_level() >= level:
            print("INFO: ", OKBLUE, *msg, ENDC, file=self.__log_file)
            self.log_monitor("INFO: ", *msg)

    def log_warning(self, level, *msg):
        if self.__config.get_log_level() >= level:
            print("WARNING: ", WARNING, *msg, ENDC, file=self.__log_file)
            self.log_monitor("WARNING: ", *msg)

    def log_error(self, level, *msg):
        if self.__config.get_log_level() >= level:
            print("ERROR: ", FAIL, *msg, ENDC, file=self.__log_file)
            self.log_monitor("ERROR: ", *msg)

    def log_critical(self, level, *msg):
        if self.__config.get_log_level() >= level:
            print("CRITICAL: ", FAIL, *msg, ENDC, file=self.__log_file)
            self.log_monitor("CRITICAL: ", *msg)

    def save_workspace(self, directory):
        self.__monitor_file.close()
        datetime_format = self.__config.get_datetime_format()
        current_time = str(datetime.now().strftime(datetime_format))
        current_time = current_time.replace("/", "-")
        copytree("./workspace", join(directory, current_time))
