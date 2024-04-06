"""
Generate a bash script to run multiple experiments.

Origionally written by Allyn, improved and extended by Isaac.

"""

import os 
from typing import Generator, Any
from functools import partial

# mkdir("data/SensitivityConfigs")

# Set some defaults
base_config_path =              "data/sensitivity.ini"
generated_configs_dir =         "data/GeneratedConfigs"
generated_bash_script_path =    "data/runGeneratedConfigs.sh"
results_output_directory =      "data/GeneratedConfigsResults"


# This will create the directory to put the generated configs in if it doesn't exist
if not os.path.isdir(generated_configs_dir):
    os.makedirs(generated_configs_dir)

#Make the directory for the final results
if not os.path.isdir(results_output_directory):
    os.makedirs(results_output_directory)



# All {variables_in_brackets} need to be specified and formatted later as .format(variables_in_brackets="value")
# It is fine to specify unused variables in .format(), but will error out if a value isn't included
# You only need to include the values here that you don't want to inherit from your base config.

######################### USEFUL CONFIG BASES ############################
sensitivity_config_base = \
"""[TOP-LEVEL PARAMETERS]
base_config = {base_config_path}

[FITNESS SENSITIVITY PARAMETERS]
test_circuit = data/saved_bests/{circuit_id}.asc
"""

# return the path to the new config
def sensitivity_config_generator()->Generator[str,None,None]:

    for circuit_id in range(10,510,10):

        config_path = os.path.join(generated_configs_dir, f"{circuit_id}.ini")
        # Create the config file using the config_base file
        with open(config_path, "w") as config_file:
            config_file.write(sensitivity_config_base.format(
                base_config_path = base_config_path,
                circuit_id = circuit_id
            ))

        yield config_path


pulse_count_config_base = \
"""[TOP-LEVEL PARAMETERS]
base_config = {base_config_path}

[FITNESS PARAMETERS]
fitness_func = {fitness_function}
desired_freq = {desired_frequency}

"""

def pulse_count_config_generator(target_pulses:list[int],
                use_tolerant_ff:bool=True,
                use_sensitive_ff:bool=True)->Generator[str,None,None]:
    """
    Generates configs for pulse_count experiments

    The order experiments will run if all fitness functions are selected is:
    tolerant -> sensitive

    Parameters
    ----------
    target_pulses : list[int]
        A list of all of the target pulse counts you want to train for
    use_tolerant_ff : bool, optional
        If each pulse get a run using the tolerant fitness function, by default True
    use_sensitive_ff: bool, optional
        If each pulse get a run using the sinsitive fitness function, by default True

    Yields
    ------
    Generator[str,None,None]
        The path to the output file generated.
    """
    def create_config(target_pulse_count:int,fitness_funciton:str)->str:
        # Generate the path for each pulse count
        config_path=os.path.join(generated_configs_dir,f"{target_pulse_count}_with__{fitness_funciton}.ini")

        with open(config_path, "w") as config_file:
            config_file.write(pulse_count_config_base.format(
                base_config_path = base_config_path,
                fitness_function = fitness_funciton,
                desired_frequency = target_pulse_count
            ))
        return config_path

    for target_pulse in target_pulses:
        if use_sensitive_ff:
            yield create_config(target_pulse,"SENSITIVE_PULSE_COUNT")
        if use_tolerant_ff:
            yield create_config(target_pulse,"TOLERANT_PULSE_COUNT")


def repeat(repeat_count:int, generator:Generator[Any,None,None])->Generator[Any,None,None]:
    """
    Repeats the outputs of the instantiated generator it is passed.

    Parameters
    ----------
    repeat_count : int
        number of times to duplicate the sequence
    generator : Generator[Any,None,None]
        Instantiated generator it duplicates

    Yields
    ------
    Generator[Any,None,None]
        The repeated output of the input generator
    """
    generator_results = list(generator)
    for i in range(repeat_count):
        for result in generator_results:
            yield result
        

## Select the config_generator you want to use and pass arguments
## OPTIONS:
# sensitivity_config_generator()
# pulse_count_config_generator(target_pulses = [1000,10000], use_tolerant_ff = True, use_sensitive_ff = True)
config_generator = repeat(2,pulse_count_config_generator(target_pulses = [1000, 10000], use_tolerant_ff = True, use_sensitive_ff = True))

evolve_command_base = "python3 src/evolve.py -c {config_path} -d {description} -o {output_directory}\n"

with open(generated_bash_script_path, 'w') as bash_file:
    # Invoke the bash shell for bash script
    bash_file.write("#!/bin/bash\n")

    for config_path in config_generator:

        # Add a call to this 
        bash_file.write(evolve_command_base.format(
            config_path = config_path,
            description = f"'running config at: {config_path}'",
            output_directory = results_output_directory
        ))

#ensure bash script is executable.
os.chmod(generated_bash_script_path,"+x")
