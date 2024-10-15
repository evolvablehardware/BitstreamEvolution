"""
Generate a bash script to run multiple experiments.
Make sure you generate configs from base BitstreamEvolution Directory.

Origionally written by Allyn, improved and extended by Isaac.

"""

import os, stat
from typing import Generator, Any, Protocol
from dataclasses import dataclass

# mkdir("data/SensitivityConfigs")

# Set some defaults
base_config_path =              "data/config.ini"
generated_configs_dir =         "data/GeneratedConfigs"
generated_bash_script_path =    "data/runGeneratedConfigs.sh"
results_output_directory =      "data/GeneratedConfigsResults"
path_best_asc_in_workspace =    "./workspace/best.asc"
path_store_best_asc =           "data/previous_best.asc"
"""This variable is where the best.asc is copied to is set command to copy_best_target_path by default"""


# This will create the directory to put the generated configs in if it doesn't exist
if not os.path.isdir(generated_configs_dir):
    os.makedirs(generated_configs_dir)

#Make the directory for the final results
if not os.path.isdir(results_output_directory):
    os.makedirs(results_output_directory)

## Some Protocalls and Dataclasses to streamline operation & Provide good defaults

class CommandInfo(Protocol):
    """A protocol specifying all data needed to invoke and run evolve on the command line."""
    config_path:str
    description:str
    copy_best_asc_target_path:str|None
    """This is the path we want to copy best.asc to once it has run successfully, None if don't want to copy it to a different location."""
    best_asc_workspace_path:str
    skip_next_command_if_success:bool
    skip_next_command_if_error:bool
    skip_next_command_if_skipped:bool

@dataclass
class CommandData:
    """A class that stores all data needed to invoke and run  evolve on the command line."""
    config_path:str
    description:str
    copy_best_asc_target_path:str|None = None
    best_asc_workspace_path:str = path_best_asc_in_workspace
    skip_next_command_if_success:bool = False
    skip_next_command_if_error:bool = False
    skip_next_command_if_skipped:bool = False


# All {variables_in_brackets} need to be specified and formatted later as .format(variables_in_brackets="value")
# It is fine to specify unused variables in .format(), but will error out if a value isn't included
# You only need to include the values here that you don't want to inherit from your base config.

######################### OLD SENSITIVITY SCRIPT ############################
old_sensitivity_config_base = \
"""[TOP-LEVEL PARAMETERS]
base_config = {base_config_path}

[FITNESS SENSITIVITY PARAMETERS]
test_circuit = data/saved_bests/{circuit_id}.asc
"""

# return the path to the new config
def old_sensitivity_config_generator()->Generator[CommandInfo,None,None]:

    for circuit_id in range(10,510,10):
        config_path = os.path.join(generated_configs_dir, f"{circuit_id}.ini")
        # Create the config file using the config_base file
        with open(config_path, "w") as config_file:
            config_file.write(old_sensitivity_config_base.format(
                base_config_path = base_config_path,
                circuit_id = circuit_id
            ))

        yield CommandData(config_path=config_path,description=f"Runing sensitivity experiment on {circuit_id}.ini")


################################## PULSE COUNT SCRIPTS ################################

pulse_count_config_base = \
"""[TOP-LEVEL PARAMETERS]
base_config = {base_config_path}
simulation_mode = FULLY_INTRINSIC

[FITNESS PARAMETERS]
fitness_func = {fitness_function}
desired_freq = {desired_frequency}

[GA PARAMETERS]
population_size = {population_size}

[STOPPING CONDITION PARAMETERS]
generations = {generations}

[LOGGING PARAMETERS]
best_file = {best_asc_path}
"""

def pulse_count_config_generator(target_pulses:list[int],
                use_tolerant_ff:bool=True,
                use_sensitive_ff:bool=True,
                population_size:int=50,
                max_generations:int=500,
                store_best_circuit:bool=False,
                skip_next_if_fail:bool=False,
                skip_next_if_skipped:bool=False)->Generator[CommandInfo,None,None]:
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
    population_size: int, optional
        This sets how many circuits are in each population, by default 50
    max_generations: int, optional
        Sets how many generations are allowed to run before the experiment ends, by default 500
    store_best_circuit: bool, optional
        If this is set the best.asc file will be copied to the data directory specified in path_store_best_asc, by default False
    skip_next_if_fail: bool, optional
        This will set the bash script to skip the next command it would run if this script fails, by default False
    skip_next_if_skipped: bool, optional
        Sets the bash script to skip the next command if this command is skipped, by default False

    Yields
    ------
    Generator[CommandInfo,None,None]
        The path to the output file generated.
    """
    def create_config(target_pulse_count:int,fitness_funciton:str,population_size:int,max_generations:int)->str:
        # Generate the path for each pulse count
        config_path=os.path.join(generated_configs_dir,f"{target_pulse_count}_with__{fitness_funciton}.ini")

        with open(config_path, "w") as config_file:
            config_file.write(pulse_count_config_base.format(
                base_config_path = base_config_path,
                fitness_function = fitness_funciton,
                desired_frequency = target_pulse_count,
                best_asc_path = path_best_asc_in_workspace,
                population_size = population_size,
                generations = max_generations
            ))
        return CommandData(config_path=config_path, 
                           description=f"Pulse Count experiment targeting {target_pulse_count}Hz using fitness function {fitness_funciton}.",
                           copy_best_asc_target_path= path_store_best_asc if store_best_circuit else None,
                           skip_next_command_if_error=skip_next_if_fail,
                           skip_next_command_if_skipped=skip_next_if_skipped,
                           skip_next_command_if_success=False)

    for target_pulse in target_pulses:
        if use_sensitive_ff:
            yield create_config(target_pulse,"SENSITIVE_PULSE_COUNT",population_size=population_size,max_generations=max_generations)
        if use_tolerant_ff:
            yield create_config(target_pulse,"TOLERANT_PULSE_COUNT",population_size=population_size,max_generations=max_generations)

pulse_count_sensitivity_config_base = \
"""[TOP-LEVEL PARAMETERS]
base_config = {base_config_path}
simulation_mode = INTRINSIC_SENSITIVITY

[FITNESS PARAMETERS]
fitness_func = {fitness_function}
desired_freq = {desired_frequency}

[FITNESS SENSITIVITY PARAMETERS]
test_circuit = {test_circuit_path}
sensitivity_trials = IGNORE
sensitivity_time = 001:00:00:00
reading_temp_humidity = false
"""

def pulse_count_then_sensitivity_config_generator(target_pulses:list[int],
                use_tolerant_ff:bool=True,
                use_sensitive_ff:bool=True,
                population_size:int=50,
                max_generations:int=500)->Generator[CommandInfo,None,None]:
    """
    Generates configs for pulse_count experiments,
    then follows them with the config for a sensitivity config.

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
    population_size: int, optional
        The number of circuits in each generation for pulse count, by default 50
    max_generations: int, optional
        The number of generations run before ending the simulation for pulse count, by default 500
    """
    def create_config_pair(target_pulse_count:int,fitness_funciton:str,pop_size:int,max_gens:int)->Generator[CommandInfo,None,None]:
        # Generate a pulse_count_config_generator to get first config
        use_sensitive = False
        use_tolerant = False
        match fitness_funciton:
            case "SENSITIVE_PULSE_COUNT":
                use_sensitive = True
            case "TOLERANT_PULSE_COUNT":
                use_tolerant = True
            case bad_name:
                raise ValueError(f"Fitness funciton name '{bad_name}' not recognised")

        # This would be easier if we just pulled out the function the generator used, but I couldn't be bothered.
        pc_gen = pulse_count_config_generator(target_pulses=[target_pulse_count],
                                              use_sensitive_ff=use_sensitive,
                                              use_tolerant_ff=use_tolerant,
                                              population_size=pop_size,
                                              max_generations=max_gens,
                                              store_best_circuit=True,
                                              skip_next_if_fail=True,
                                              skip_next_if_skipped=True)
        pulse_count_experiment = list(pc_gen)[0] # yield the first element only (there should only be 1)
        yield pulse_count_experiment

        # make sure we have a best.asc to act on.
        if pulse_count_experiment.copy_best_asc_target_path is None:
            raise ValueError("The pulse count must output to a target path for Sensitivity to test it.")

        ## Generate the config for the Sensitivity run.
        config_path=os.path.join(generated_configs_dir,f"Sensitivity_For_Pulse_Count_of_{target_pulse_count}_with_{fitness_funciton}.ini")

        ## UPDATE SO TO GENERATE SENSITIVITY CONFIG 120 mins
        with open(config_path, "w") as config_file:
            config_file.write(pulse_count_sensitivity_config_base.format(
                base_config_path = base_config_path,
                fitness_function = fitness_funciton,
                desired_frequency = target_pulse_count,
                test_circuit_path = pulse_count_experiment.copy_best_asc_target_path # get the asc file stored by p_c_experiment
            ))
        yield CommandData(config_path=config_path, 
                           description=f"Sensitivity Evaluation for Pulse Count experiment targeting {target_pulse_count}Hz with {fitness_funciton}.",
                           copy_best_asc_target_path= None, # No best_asc to copy out
                           skip_next_command_if_error=False,
                           skip_next_command_if_skipped=False,
                           skip_next_command_if_success=False)
    
    for target_pulse in target_pulses:
        if use_sensitive_ff:
            configs = create_config_pair(target_pulse,"SENSITIVE_PULSE_COUNT",pop_size=population_size,max_gens=max_generations)
            for config in configs:
                yield config
        if use_tolerant_ff:
            configs = create_config_pair(target_pulse,"TOLERANT_PULSE_COUNT",pop_size=population_size,max_gens=max_generations)
            for config in configs:
                yield config
    

############################ USEFUL UTILITIES ##############################################
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
# repeat(2,pulse_count_config_generator(target_pulses = [1000, 10000], use_tolerant_ff = True, use_sensitive_ff = True))
# pulse_count_config_generator(target_pulses = [40000,20000,20000],use_tolerant_ff=False,use_sensitive_ff=True)
config_generator: Generator[CommandInfo,None,None] = \
    pulse_count_then_sensitivity_config_generator(target_pulses= [1000,2000,4000],use_tolerant_ff=True, use_sensitive_ff=True,max_generations=12,population_size=53)
## Bash File Configuration

# Note that there are no spaces between variables, =, and value assigned. This is needed. 
#Bash will not recognize them as variables if there is a space in them.
bash_head = \
"""#!/bin/bash
# make sure this was generated from the BitstreamEvolution folder at the base of this directory.

# This variables stores the number or errors that occour
ErrorCounter=0
SuccessCounter=0
SkippedCounter=0
UserInterruptTriggered=0
SkipNextCommand=0
FailedCommands=''
SkippedCommands=''



#Run Commands, log if they fail.
"""

evolve_command_base = "python3 src/evolve.py -c {config_path} -d {description} -o {output_directory}"

# The || only runs 2nd if left fails, && only if left succeeds
# parenthesis is to extend command over multiple lines
# The not means it enters the then statement if there is an error
# the UserInterruptTriggered=$((exitCode==130)) allows us to stop other code if user interrupt occoured (set to 1 if called)
bash_command_wrapper_logic = \
"""
Current_Command=$'{command}'
if [ $UserInterruptTriggered -eq 0 ]; then
if [ $SkipNextCommand -eq 0 ]; then
{command}
exitCode=$?
if [ $exitCode -ne 0 ]; then  #Error
    UserInterruptTriggered=$((exitCode == 130))
    ((ErrorCounter=ErrorCounter+1)) && FailedCommands+="$Current_Command"+$'\\n' 
    {action_if_failure}
else # Success
    ((SuccessCounter=SuccessCounter+1))
    {action_if_success}
fi 
else # Skipped
    ((SkippedCounter=SkippedCounter+1)) && SkippedCommands+="$Current_Command"+$'\\n'
    {action_if_skipped}
fi #ctrl+c
fi
"""

bash_tail = \
"""
if [ $UserInterruptTriggered -ne 0 ]; then
#print these results if the script had a user interrupt
echo "=================================== USER INTERRUPT RESULTS ===================================="
echo "Canceled Commands Due to Keyboard Interrupt while running:"
echo $"$Current_Command"
echo ""
echo "Commands That Failed:"
echo "$FailedCommands"
echo ""
echo "Commands Skipped:"
echo "$SkippedCommands"

echo "==============================================================================================="
echo "$ErrorCounter of $((ErrorCounter+SuccessCounter+SkippedCounter)) commands Failed, including the one not completed."
echo "$SkippedCounter of $((ErrorCounter+SuccessCounter+SkippedCounter)) commands were Skipped"
echo "$(({num_commands}-(ErrorCounter+SuccessCounter+SkippedCounter))) of {num_commands} were not run at all."


exit 1
fi

# Print out the results of the Tests
echo ""
echo "=================================== RESULTS ===================================="
echo ""
echo "Commands That Failed:"
echo "$FailedCommands"
echo ""
echo "Commands Skipped:"
echo "$SkippedCommands"

echo "================================================================================"
echo "$ErrorCounter of {num_commands} commands Failed"
echo "$SkippedCounter of {num_commands} commands were Skipped"

exit 0

"""

with open(generated_bash_script_path, 'w') as bash_file:
    # Invoke the bash shell for bash script
    bash_file.write(bash_head)

    command_count = 0
    for command_data in config_generator:

        # Add a call to this 
        bash_file.write(
            bash_command_wrapper_logic.format(
                command = evolve_command_base.format(
                    config_path = command_data.config_path,
                    description = f'"{command_data.description}"', 
                    # Note that it is important that outer string uses double quotes or this messes up wrapper logic
                    output_directory = results_output_directory
                ),
                action_if_failure = "SkipNextCommand=1" if command_data.skip_next_command_if_error else "SkipNextCommand=0",
                action_if_success = ("SkipNextCommand=1" if command_data.skip_next_command_if_success else "SkipNextCommand=0")  +\
                                    (f"\n\tcp {path_best_asc_in_workspace} {command_data.copy_best_asc_target_path}" if command_data.copy_best_asc_target_path is not None else ""),
                action_if_skipped = "SkipNextCommand=1" if command_data.skip_next_command_if_skipped else "SkipNextCommand=0"
            )
        )

        #count the number of commands we add
        command_count += 1
    
    bash_file.write(bash_tail.format(num_commands = command_count))

#ensure bash script is executable if possible, but don't require permisions to do so.
try:
    os.chmod(generated_bash_script_path,stat.S_IREAD
            |stat.S_IWRITE
            |stat.S_IRWXU
            |stat.S_IRWXG
            |stat.S_IRWXO)
except PermissionError:
    print(
    f"""
You may need to make the bash file executable.
Alternatively, you could run this command with sudo privilages. (sudo python3 ...)
To do so run the following command:
    
chmod +x {bash_file.name}

"""
    )

completion_message=\
f"""
--------------------------------------------------------------------------
Finished completing the bash file, and related folders.

Folder containing generated partial configs: {generated_configs_dir}
Reference base config: {base_config_path}
Results are output to the following directory: {results_output_directory}

Created the bash file at: {bash_file.name}
---------------------------------------------------------------------------

Begin the experiment by running ./{bash_file.name}

---------------------------------------------------------------------------
If you didn't run this script from the base of the BitstreamEvolution project,
it is best you regenerate the file after you cd there and run the file from that folder, too.

i.e.   .../BitstreamEvolution$ python3 src/tools/generate_configs.py
       .../BitstreamEvolution$ ./{bash_file.name}
"""

print(completion_message)