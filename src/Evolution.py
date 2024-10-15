from Microcontroller import Microcontroller
from CircuitPopulation import CircuitPopulation
from ConfigBuilder import ConfigBuilder
from Config import Config
from Logger import Logger
from subprocess import CalledProcessError, run
import os

from WorkspaceFormatter import WorkspaceFormatter

class Evolution:

    def __init__(self):
        '''Do nothing'''

    def evolve(self,
            primary_config_path:str,
            experiment_description:str,
            base_config_path:str,
            built_config_path:str,
            output_directory:str=None,
            print_action_only:bool=False) -> None:

        if (print_action_only):
            print('Running evolve.py in print only mode:')
            print(f"Config: {primary_config_path}, Base Config: {base_config_path}, Output Directory: {output_directory}, Experiment Description: {experiment_description}.")
            # TODO: If wish to validate operations would work properly, we should implement some validation of inputs
            # This would quickly add confidence that the arguments would work properly, perhaps like this.
            invalid_notifications = self.validate_arguments(output_directory)
            print(invalid_notifications)

            print('Execution of evolve.py Finished.')
            return
    
        if not os.path.exists("./workspace"):
            os.mkdir("./workspace")

        ## Creating the config that will be used.
        config_builder = ConfigBuilder(primary_config_path, override_base_config=base_config_path)
        config_builder.build_config(built_config_path)
        
        ## Use config generated to run experiment
        config = Config(built_config_path)

        ## get the experiment description if not previously given
        if experiment_description is None:
            experiment_description = input("Explain this experiment: ")
        self.experiment_description = experiment_description

        # compiling and uploading to the Arduino
        if config.get_upload_to_arduino():
            c = run(["./arduino-cli", "compile", "-b", "arduino:avr:nano", "data/ReadSignal/ReadSignal.ino"])
            usb_port = config.get_usb_path()
            u = run(["./arduino-cli", "upload", "-b", "arduino:avr:nano", "-p", usb_port, "data/ReadSignal/ReadSignal.ino"])

        ## Run Evolution
        logger = Logger(config, experiment_description)
        # logger.log_info(1, args) - Not sure how to log arguments. This was my attempt to do so.
        config.add_logger(logger)
        config.validate_all()
        self.validate_arguments(output_directory)
        mcu = Microcontroller(config, logger)
        population = CircuitPopulation(mcu, config, logger)

        self.output_directory = output_directory
        self.config = config
        self.logger = logger
        self.population = population

        if config.get_simulation_mode() != "INTRINSIC_SENSITIVITY":
            population.populate()
            population.evolve()
        else:
            population.run_fitness_sensitity()


        logger.log_event(0, "Evolution has completed successfully")

        logger.log_event(1, "Launching the Live Plot window...")
        args = ["python3", "src/PlotEvolutionLive.py", "formal"]
        try:
            run(args, check=True, capture_output=True)
        except OSError as e:
            self.log_error(1, "An error occured while launching PlotEvolutionLive.py")
        except CalledProcessError as e:
            self.log_error(1, "An error occured in PlotEvolutionLive.py")
            self.log_error(1, e)

        # SECTION Clean up resources

        if config.get_simulation_mode() == "FULLY_INTRINSIC":
            # Upload a sample bitstream to the FPGA.
            run([
                "iceprog",
                "-d",
                "i:0x0403:0x6010:0",
                "data/hardware_blink.bin"
            ])
        
        self.clean_up()

    def clean_up(self):
        # TODO: make sure config file specified above ends up in output.
        if self.output_directory is not None:
            #copy simulation information to this output directory
            self.logger.save_workspace(self.output_directory)
        elif self.config.get_backup_workspace():
            self.logger.save_workspace(self.config.get_output_directory())

        self.__WorkspaceFormatter = WorkspaceFormatter(self.config, self.experiment_description)
        self.__WorkspaceFormatter.format_workspace()

    ## Don't know if this is needed, but it might be useful to validate all inputs 
    ## especially if this is going to take a while to run.
    ## It would also be nice if we could have script that could look over a bunch of configs and validate
    ## that they have all necessary parameters
    def validate_arguments(self, output_directory):
        invalid_info = ""
        if (output_directory is not None) and (not os.path.isdir(output_directory)):
            invalid_info += (f"PATH_NOT_RECOGNIZED: Output directory not recognized: {output_directory}\n")

            #alternate solution if wanted to do more with exit statuses for bash scripting
            #parser.exit(status=1, message=f"Output directory not recognized: {args.output_directory}")
        return invalid_info