'''
reconstruct.py - current state
==============================
This is a test piece of code that is currently not used, and was an exploratory plan that was put to the side due to storage space conserns.

program goal
============
This program is for reconstructing a generation, from another file
This will build all of the circuit files from a generation file, and put them in 
the ASC directory

Args: generation number to reconstruct
The code will use the config file for the paths to the ASC directory and generations directory
But, it will use the config values provided in the generation files for the routing and accessible columns
'''

from argparse import ArgumentParser
import os
from Circuit.CircuitLegacy import CircuitLegacy
from utilities import wipe_folder
from Config import Config
from CircuitPopulation import SEED_HARDWARE_FILEPATH

program_name = "reconstruct"
program_description = "This program reconstructs a generation using the config's ASC directory and generations directory"
program_epilog = None

def run():
    #Argument Parser is in the run file because it scared sphinx into thinking sys.exit() might be called
    parser = ArgumentParser(prog=program_name,
                            description=program_description,
                            epilog=program_epilog)
    parser.add_argument('-g','--generation',type=int,default=None,
                    help=f"The generation to reconstruct. Default: last generation")
    args = parser.parse_args()

    config = Config('./workspace/builtconfig.ini')

    gen_path = config.get_generations_directory().joinpath('gen' + str(args.generation) + '.log')

    # Separate this out so Sphinx can scan this file without causing side effects or hitting "exit(1)"


    if not os.path.isfile(gen_path):
        print(f'Generation {args.generation} does not exist.')
        exit(1)

    wipe_folder(config.get_asc_directory())

    # Read the generation file
    with open(gen_path, 'r') as f:
        gen_lines = f.readlines()

    # Check the first two lines, to get our necessary config values
    routing = gen_lines[0]
    accessed_columns = gen_lines[1].split(',')
    for i in range(len(accessed_columns)):
        accessed_columns[i] = int(accessed_columns[i])

    # Now get all of the bitstreams
    bitstreams = []
    for i in range(2, len(gen_lines)):
        bitstream = gen_lines[i].split('')
        for j in range(len(bitstream)):
            bitstream[j] = int(bitstream[j])
        bitstreams.append(bitstream)

    # Now, we can reconstruct each circuit
    for i in range(len(bitstreams)):
        # Some of these can be None since we aren't doing actual evolution with this circuit
        circuit = CircuitLegacy(i + 1, 
            "hardware" + str(i), 
            SEED_HARDWARE_FILEPATH,
            None,
            None,
            config,
            None,
            []
        )
        circuit.reconstruct_from_bistream(bitstreams[i], accessed_columns, routing)

    # Now tell user that we're done
    print("Generation has been reconstructed")

    
#only runs if it is imported directly
if (__name__ == "__main__"):
    run()
