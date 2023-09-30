from Microcontroller import Microcontroller
from CircuitPopulation import CircuitPopulation
from ConfigBuilder import ConfigBuilder
from Config import Config
from Logger import Logger
from subprocess import run
import os

class Evolution:

    def __init__(self):
        #set to dict of arguments once used, primarily for tests
        self.evolve_has_run = False
        self.last_evolution_arguments_dict = None 
        '''Do nothing'''

    def evolve(self,
            primary_config_path:str,
            experiment_description:str,
            base_config_path:str,
            built_config_path:str,
            output_directory:str=None,
            print_action_only:bool=False) -> None:
        
        self.evolve_has_run = True
        self.last_evolution_arguments_dict = {
            "primary_config_path":      primary_config_path,
            "experiment_description":   experiment_description,
            "base_config_path":         base_config_path,
            "built_config_path":        built_config_path,
            "output_directory":         output_directory,
            "print_action_only":        print_action_only
        }

        if (print_action_only):
            print('Running evolve.py in print only mode:')
            print(f"Config: {primary_config_path}, Base Config: {base_config_path}, Output Directory: {output_directory}, Experiment Description: {experiment_description}.")
            # TODO: If wish to validate operations would work properly, we should implement some validation of inputs
            # This would quickly add confidence that the arguments would work properly, perhaps like this.
            invalid_notifications = self.validate_arguments(output_directory)
            print(invalid_notifications)

            print('Execution of evolve.py Finished.')
            return

        ## Creating the config that will be used.
        config_builder = ConfigBuilder(primary_config_path, override_base_config=base_config_path)
        config_builder.build_config(built_config_path)
        
        ## Use config generated to run experiment
        config = Config(built_config_path)

        ## get the experiment description if not previously given
        if experiment_description is None:
            experiment_description = input("Explain this experiment: ")

        ## Run Evolution
        logger = Logger(config, experiment_description)
        # logger.log_info(1, args) - Not sure how to log arguments. This was my attempt to do so.
        config.add_logger(logger)
        config.validate_all()
        self.validate_arguments(output_directory)
        mcu = Microcontroller(config, logger)
        population = CircuitPopulation(mcu, config, logger)

        population.populate()
        population.evolve()

        logger.log_event(0, "Evolution has completed successfully")

        # SECTION Clean up resources

        if config.get_simulation_mode() == "FULLY_INTRINSIC":
            # Upload a sample bitstream to the FPGA.
            run([
                "iceprog",
                "-d",
                "i:0x0403:0x6010:0",
                "data/hardware_blink.bin"
            ])

        # TODO: make sure config file specified above ends up in output.
        if output_directory is not None:
            #copy simulation information to this output directory
            logger.save_workspace(output_directory)
        elif config.get_backup_workspace():
            logger.save_workspace(config.get_output_directory())

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