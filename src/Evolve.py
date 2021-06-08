"""
Genetic Algorithm for Intrinsic Analog Hardware Evolution
FOR USE WITH LATTICE iCE40 FPGAs ONLY

This code can be used to evolve an analog oscillator

Author: Derek Whitley
"""

import os
import sys
import random
import operator
import time
import datetime
import tailer
import configparser
import numpy as np
import math
import matplotlib.pyplot as plt
from itertools import izip_longest, chain
from shutil import copyfile, move
from numpy.random import choice
from numpy.polynomial.polynomial import polyfit

#internal libraries
import SerialMonitor

"""
Static parameters can be found and changed in the config.ini file in the root project folder
DO NOT CHANGE THEM HERE
"""
config = configparser.ConfigParser()
config.read("../config.ini")

POPULATION_SIZE         =       int(config['DEFAULT']['POPULATION_SIZE'])
GENOTYPIC_LENGTH        =       int(config['DEFAULT']['GENOTYPIC_LENGTH'])
GENERATIONS             =       int(config['DEFAULT']['GENERATIONS'])
MUTATION_PROBABILITY    =       float(config['DEFAULT']['MUTATION_PROBABILITY'])
CROSSOVER_PROBABILITY   =       float(config['DEFAULT']['CROSSOVER_PROBABILITY'])
ELITISM_FRACTION        =       float(config['DEFAULT']['ELITISM_FRACTION'])
DESIRED_FREQ            =       int(config['DEFAULT']['DESIRED_FREQ'])
PROTECTED_COLUMNS       =       map(int, str(config['DEFAULT']['PROTECTED_COLUMNS']).split(','))
FPGA                    =       str(config['DEFAULT']['FPGA'])

#https://docs.python.org/3/library/configparser.html#supported-datatypes
PULSE_FUNC              =       config['DEFAULT'].getboolean('PULSE_FUNC') 

ASC_DIR                 =       str(config['DEFAULT']['ASC_DIR'])
BIN_DIR                 =       str(config['DEFAULT']['BIN_DIR'])
DATA_DIR                =       str(config['DEFAULT']['DATA_DIR'])
ANALYSIS                =       str(config['DEFAULT']['ANALYSIS'])
ROUTING                 =       str(config['DEFAULT']['ROUTING'])
MONITOR                 =       str(config['DEFAULT']['MONITOR_FILE'])
SELECTION               =       str(config['DEFAULT']['SELECTION'])

#Recently Added Params
RANDOMIZE_UNTIL         =       str(config['DEFAULT']['RANDOMIZE_UNTIL'])
VARIANCE_THRESHOLD      =       float(config['DEFAULT']['VARIANCE_THRESHOLD'])
INIT_MODE               =       str(config['DEFAULT']['INIT_MODE'])
LAUNCH_MONITOR          =       config['DEFAULT'].getboolean('LAUNCH_MONITOR')
USB_PATH                =       str(config['DEFAULT']['USB_PATH'])


# Colors for console
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

"""
Global Trackers
"""
FITNESS = {} #dictionary of fitness scores
MUTATION_LIST = [] #list of circuits mutated this cycle
BEST = "Evaluating..." #current best performing circuit name
BEST_FITNESS = 0.0
BEST_EPOCH = 0
START_DATETIME = 0.0
START_TIME = 0.0
EXPLANATION = ""
CURRENT_GEN = 0
EPOCH_TIME = {} #list of times taken per generation
EPOCH_BEST_FITNESS =  [] #list of best fitnesses
VARIANCE = 0
PULSES = {}

FAIL = '\033[91m' 
ENDC = '\033[0m'



def reset_globals():
    global FITNESS, MUTATION_LIST, BEST, BEST_FITNESS, BEST_EPOCH, CURRENT_GEN, EPOCH_BEST_FITNESS, VARIANCE, PULSE_FUNC
    FITNESS = {} #dictionary of fitness scores
    MUTATION_LIST = [] #list of circuits mutated this cycle
    BEST = "Evaluating..." #current best performing circuit name
    BEST_FITNESS = 0.0
    BEST_EPOCH = 0
    START_DATETIME = 0.0
    START_TIME = 0.0
    EXPLANATION = ""
    CURRENT_GEN = 0
    EPOCH_TIME = {} #list of times taken per generation
    EPOCH_BEST_FITNESS =  [] #list of best fitnesses
    VARIANCE = 0
    PULSES = {}

def clear_temp_dirs():
    for temps in os.listdir(ASC_DIR): os.remove(ASC_DIR+temps)
    for temps in os.listdir(BIN_DIR): os.remove(BIN_DIR+temps)
    for temps in os.listdir(DATA_DIR): os.remove(DATA_DIR+temps)

"""
Terminal Color Codes
"""
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

"""
Plot experiment variables
"""
def plot_fitness():
    pulse_count = 0.0
    wave = 0.0
    fitness_score = 0.0
    fitness_list = []
    generations = []
    generation = 0

    #Read the data file associated with this individual
    for files in os.listdir("./"):
        generation += 1
        generations.append(generation)
        pulse_count = 0.0
        wave = 0.0
        fitness_score = 0.0
        with open(files, "r+") as file:
            data = file.readlines()
            for i in range(0, 499):
                try:
                    initial1 = int(data[i].strip().split(": ", 1)[1])
                    if int(data[i].strip().split(": ", 1)[1] == None): wave += 0;
                    else:
                        if int(data[i+1].strip().split(": ", 1)[1] == None): pulse_count += 0;
                        else: wave += abs(int(data[i+1].strip().split(": ", 1)[1]) - initial1)

                except:
                    wave += 0

            fitness_score = wave/500 #500 samples at 10 uS = 5 mS
            fitness_list.append(fitness_score)

    fig, ax = plt.subplots()
    ax.plot(fitness_list)

    plt.plot(fitness_list, 'rx')
    print(fitness_list)

    ax.set(xlabel='generation', ylabel='fitness', title='Best fitness per generation')
    ax.grid()

    # fig.savefig(plot_filepath)

    plt.show()

"""
Writes to the monitor file
"""
def write_to_monitor():
    updates = [
        "Population Size: " + str(POPULATION_SIZE) + '\n',
        "Genotypic Length: " + str(GENOTYPIC_LENGTH) + '\n',
        "Total Generations: " + str(GENERATIONS) + '\n',
        "Mutation Probability: " + str(MUTATION_PROBABILITY) + '\n',
        "Crossover Probability:  " + str(CROSSOVER_PROBABILITY) + '\n',
        "Selection Method: " + str(SELECTION) + '\n',
        "Routing Method: " + str(ROUTING) + '\n',
        "Desired Pulse Frequency: " + str(DESIRED_FREQ) + '\n',
        "FPGA Address: " + str(FPGA) + '\n',
        "Using Pulse Fitness Function: " + str(PULSE_FUNC) + '\n',
        "========================================" + '\n',
        "Explanation: " + str(EXPLANATION) + '\n',
        "Overall Best Circuit: " + bcolors.OKGREEN + str(BEST) + bcolors.ENDC + '\n',
        "Overall Best Fitness: " + bcolors.OKGREEN + str(BEST_FITNESS) + bcolors.ENDC + '\n',
        "Overall Best Epoch: " + str(BEST_EPOCH) + '\n',
        "Experiment Started at: " + str(START_DATETIME) + '\n',
        "Current Generation: " + str(CURRENT_GEN) + '\n',
        "Total Runtime: " + str(round((time.time()-START_TIME)/60, 2)) + " minutes" + '\n'
    ]

    with open(MONITOR, 'r+') as fn:
        data = fn.readlines()
        for ind, lines in enumerate(data):
            for row in range (3, 23): #(20,56)
                if row < len(updates):
                    data[row] = updates[row-2]
        fn.close()
        with open(MONITOR, 'r+') as fn:
            fn.writelines(data)

"""
Compile circuit ASC file to a BIN file for hardware upload
"""
def compile_circuit(circuit):
    print("Compiling "+circuit+" with icepack...")
    bin_name = os.path.splitext(circuit)[0]+'.bin'
    cmd = "icepack {0}{1} {2}{3}".format(ASC_DIR, circuit, BIN_DIR, bin_name)
    os.system(cmd)
    print("Finished.")
    return bin_name


"""
Compile all circuit ASC files to BIN files 
"""
def compile_all_circuits():
    for files in os.listdir(ASC_DIR):
        name = os.path.splitext(files)[0]+'.bin'
        cmd = "icepack {0}{1} {2}{3}".format(ASC_DIR, files, BIN_DIR, name)
        print("Compiling "+files+" with icepack...")
        os.system(cmd)
        print("Finished.")


"""
Collect data into fixed-length chunks or blocks
 #grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
Taken from python recipes
"""
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


"""
Make a copy of the hardware template for each member of the population
"""
def copy_hardware_template():
    for i in range(1, POPULATION_SIZE+1):
        copyfile("../hardware.asc", "../asc/hardware"+str(i)+".asc")
        print("Copied template: hardware"+str(i)+".asc")


"""
Programs and runs the circuit on hardware
"""
def run_circuit(circuit):
    global PULSE_FUNC;

    #Program the hardware
    cmd = "iceprog {0}{1} -d {2}".format(BIN_DIR,circuit,FPGA)
    start = time.time()
    os.system(cmd)
    circuit = os.path.splitext(circuit)[0]
    time.sleep(.1) # delay 1 ms
    data = SerialMonitor.Begin(circuit, PULSE_FUNC)
    elapsed = time.time() - start
    print("TIME TAKEN RUNNING AND LOGGING ---------------------- : " + str(elapsed))
    return evaluate(circuit)


"""
Create a population of random tile configurations
"""
def populate(size):
    global MUTATION_LIST;

    #First, create bitstream files (.asc)
    index = 1
    while index < size+1:
        with open("../asc/hardware"+str(index)+".asc", "r+") as file:
            # search the hardware file for the appropriate logic tiles
            # [4 1]->[8 5]
            data = file.readlines()
            print("Randomizing hardware"+str(index)+"")
            for i in range(4, 10):
                for j in range(1, 17):
                    # print("hardware"+str(index)+".logic_tile "+str(i)+" "+str(j)+"")
                    for ind, lines in enumerate(data):
                        if ".logic_tile "+str(i)+" "+str(j)+"\n" in lines:
                            if (ROUTING == 'MOORE'):
                                for row in chain(range(1, 3), range(13,14)):
                                    configuration_codon = ""
                                    # the number of bits programming each logic element
                                    for column in range(0, 54):
                                        if column in PROTECTED_COLUMNS:
                                            configuration_codon += str(data[ind+row][column])
                                        else:# column >= 36 and column <= 45:
                                        
                                            # RANDOM FROM SEED POPULATION
                                            if INIT_MODE == "RAND_FROM_SEED":
                                                if random.uniform(0,1) <= MUTATION_PROBABILITY: configuration_codon += str(random.randint(0,1))
                                                else: configuration_codon += data[ind+row][column]
                                            # COMPLETE RANDOM POPULATION
                                            elif INIT_MODE == "COMPLETE_RAND":                                    
                                                configuration_codon += str(random.randint(0,1))
                                            # NON RANDOM POPULATION ( CLONING SEED )
                                            elif INIT_MODE == "CLONE_FROM_SEED":
                                                configuration_codon += data[ind+row][column]
                                            elif INIT_MODE == "CONTINUE":
                                                #KEEP AS IS
                                                configuration_codon += data[ind+row][column]
                                            else:
                                                print(bcolors.FAIL + "ERROR: INIT_MODE not set in config.ini" + bcolors.ENDC)
                                                exit()
                                        
                                        # else:
                                        #     configuration_codon += str(0)
                                    # write the codon to this line of the logic tile (data[ind+row])
                                    data[ind+row] = configuration_codon+"\n"
                            elif (ROUTING == 'NEWSE'):
                                for row in range(1, 3):
                                    configuration_codon = ""
                                    # the number of bits programming each logic element
                                    for column in range(0, 54):
                                        if column in PROTECTED_COLUMNS:
                                            configuration_codon += str(data[ind+row][column])
                                        else:# column >= 36 and column <= 45:

                                            # RANDOM FROM SEED POPULATION
                                            if INIT_MODE == "RAND_FROM_SEED":
                                                if random.uniform(0,1) <= MUTATION_PROBABILITY: configuration_codon += str(random.randint(0,1))
                                                else: configuration_codon += data[ind+row][column]
                                            # COMPLETE RANDOM POPULATION
                                            elif INIT_MODE == "COMPLETE_RAND":                                    
                                                configuration_codon += str(random.randint(0,1))
                                            # NON RANDOM POPULATION ( CLONING SEED )
                                            elif INIT_MODE == "CLONE_FROM_SEED":
                                                configuration_codon += data[ind+row][column]
                                            elif INIT_MODE == "CONTINUE":
                                                #KEEP AS IS
                                                configuration_codon += data[ind+row][column]
                                            else:
                                                print(bcolors.FAIL + "ERROR: INIT_MODE not set in config.ini" + bcolors.ENDC)
                                                exit()

                                        # else:
                                        #     configuration_codon += str(0)
                                    # write the codon to this line of the logic tile (data[ind+row])
                                    data[ind+row] = configuration_codon+"\n"
                            
            file.close()
            with open("../asc/hardware"+str(index)+".asc", "r+") as file:
                file.writelines(data)
        index += 1

    for circuits in os.listdir(ASC_DIR):
        MUTATION_LIST.append(os.path.splitext(circuits)[0])

"""
Randomizes population until minimum variance is found
"""
def randomize_until_variance():
    att = 0
    while True:
        att+=1
        print("attempt " + str(att) + " at reaching variance fitness of " + str(VARIANCE_THRESHOLD) )
        PULSE_FUNC = False
        randomize_initial_circuit()
        cmd = "icepack {0} {1}".format("../hardware.asc", "../hardware.bin")
        os.system(cmd)
        data = run_circuit('../hardware.bin')
        if data < 4:
            print("Fitness of randomization: " + str(data))
            print("-------------------Repopulating due to low variance: "+str(data)+"-------------------\n")
        else:
            PULSE_FUNC = True
            data = run_circuit('hardware.bin')
            if data > 0.0:
                reset_globals()
                with open("bestlivedata.log", "w+") as liveFile:
                    liveFile.write("0, 0.0, 0.0\n")
                    liveFile.close()
                with open("alllivedata.log", "w+") as liveFile:
                    # liveFile.write("hardware1, 0.0")
                    liveFile.close()
                PULSE_FUNC = False
                break; break; break;

"""
Randomizes population until minimum variance is found
"""
def randomize_until_pulses():
    global PULSES
    while PULSE_FUNC:
        clear_temp_dirs()
        reset_globals()
        copy_hardware_template()
        populate(POPULATION_SIZE)
        current_generation = 0
        gather_data(current_gen=0)
        if max(PULSES.items(), key=operator.itemgetter(1))[1] == 0 and current_generation == 0:
            print(PULSES)
            PULSES = {}
        else:
            break;

"""
Randomizes an incoming circuit
"""
def randomize_initial_circuit():
    with open("../hardware.asc", "r+") as file:
        # search the hardware file for the appropriate logic tiles
        # [4 1]->[8 5]
        data = file.readlines()
        print("Randomizing initial circuit...")
        for i in range(4, 10):
            for j in range(1, 17):
                for ind, lines in enumerate(data):
                    if ".logic_tile "+str(i)+" "+str(j)+"\n" in lines:
                        if (ROUTING == 'MOORE'):
                            for row in chain(range(1, 3), range(13,14)):
                                configuration_codon = ""
                                # the number of bits programming each logic element
                                for column in range(0, 54):
                                    if column in PROTECTED_COLUMNS:
                                        configuration_codon += str(data[ind+row][column])
                                    else:# column >= 36 and column <= 45:

                                        # RANDOM FROM SEED POPULATION
                                        if INIT_MODE == "RAND_FROM_SEED":
                                            if random.uniform(0,1) <= MUTATION_PROBABILITY: configuration_codon += str(random.randint(0,1))
                                            else: configuration_codon += data[ind+row][column]
                                        # COMPLETE RANDOM POPULATION
                                        elif INIT_MODE == "COMPLETE_RAND":                                    
                                            configuration_codon += str(random.randint(0,1))
                                        # NON RANDOM POPULATION ( CLONING SEED )
                                        elif INIT_MODE == "CLONE_FROM_SEED":
                                            configuration_codon += data[ind+row][column]
                                        elif INIT_MODE == "CONTINUE":
                                            #DO NOTHING THIS SHOULDN"T HAPPEN
                                            print(bcolors.FAIL + "ERROR: CONTINUE==INIT_MODE should not run randomize!" + bcolors.ENDC)
                                            exit()
                                        else:
                                            print(bcolors.FAIL + "ERROR: INIT_MODE not set in config.ini" + bcolors.ENDC)
                                            exit()
                                        
                                    #ALWAYS leave commented unless SPECIFICALLY trying to zeroize a template (Dangerous!)
                                    # else:
                                    #     configuration_codon += str(0)
                                # write the codon to this line of the logic tile (data[ind+row])
                                data[ind+row] = configuration_codon+"\n"
                        elif (ROUTING == 'NEWSE'):
                            for row in range(1, 3):
                                configuration_codon = ""
                                # the number of bits programming each logic element
                                for column in range(0, 54):
                                    if column in PROTECTED_COLUMNS:
                                        configuration_codon += str(data[ind+row][column])
                                    else:# column >= 36 and column <= 45:

                                        # if random.uniform(0,1) <= MUTATION_PROBABILITY: configuration_codon += str(random.randint(0,1))
                                        # else: configuration_codon += data[ind+row][column]
                                        
                                        configuration_codon += str(random.randint(0,1))

                                        # configuration_codon += data[ind+row][column]
                                    # else:
                                    #     configuration_codon += str(0)
                                # write the codon to this line of the logic tile (data[ind+row])
                                data[ind+row] = configuration_codon+"\n"
                        
        file.close()
        with open("../hardware.asc", "r+") as file:
            file.writelines(data)

"""
Evaluate an individual's fitness
"""
def evaluate(individual):
    global FITNESS, PULSE_FUNC, VARIANCE, PULSES;
    
    ind = os.path.splitext(individual)[0]

    pulse_count = 0
    wave = 0.0
    fitness_score = 0.0
    waveform = []

    #Read the data file associated with this individual
    with open("../data/"+ind+".log", "r+") as file:
        data = file.readlines()
        if PULSE_FUNC:
            sumdata = sum([int(i) for i in data])
            print(bcolors.WARNING + "Pulses counted: " + str(sumdata) + bcolors.ENDC)
            # if any data set is empty, zeroize values
            if (sumdata == None):
                print("NULL DATA FILE. ZEROIZING.")
                pulse_count = 0;
            else:
                pulse_count = int(sumdata) # 
        else:
            for i in range(0, 499):
                try:
                    initial1 = int(data[i].strip().split(": ", 1)[1])
                    waveform.append(int(data[i].strip().split(": ", 1)[1]))
                    if int(data[i].strip().split(": ", 1)[1]) == None or int(data[i].strip().split(": ", 1)[1]) > 1000.0: 
                        wave += 0;
                    else:
                        if int(data[i+1].strip().split(": ", 1)[1] == None): pulse_count += 0;
                        else: wave += abs(int(data[i+1].strip().split(": ", 1)[1]) - initial1)

                except:
                    print(bcolors.FAIL + "FAILED TO READ "+ind+" AT LINE ["+str(i)+"] -> ZEROIZING LINE." + bcolors.ENDC)
                    wave += 0

        if not PULSE_FUNC:
            fitness_score = wave/500 #500 samples at 10 uS = 5 mS
            if fitness_score > VARIANCE_THRESHOLD:
                print(individual + " " + str(fitness_score))
                VARIANCE = fitness_score
                exit()

        elif PULSE_FUNC:
            if DESIRED_FREQ == pulse_count:
                print("Unity Achieved: " + ind)
                fitness_score = 1
            elif pulse_count == 0:
                fitness_score = VARIANCE + 0.0
            else:
                fitness_score = VARIANCE + (1.0/abs(DESIRED_FREQ - pulse_count))
        

        print(bcolors.OKGREEN + individual+" fitness score: "+str(fitness_score) + bcolors.ENDC + "\n")
        FITNESS.update({ind : fitness_score})
        PULSES.update({ind : pulse_count})

        #Update the monitor
        write_to_monitor()

        #Update live plot
        with open("alllivedata.log", "w+") as allLive:
            for fits in sorted(PULSES.items()):
                if fits[0] == "../hardware" or fits[0] == "hardware":
                    print("Skip writing hardware0 to file.")
                    # allLive.write("hardware0, " + str(fits[1]) + "\n")
                else:
                    allLive.write(str(fits[0]) + ", " + str(fits[1]) + "\n")
            allLive.close()
        with open("waveformlivedata.log", "w+") as waveLive:
            i = 1
            for points in waveform:
                waveLive.write(str(i) + ", " + str(points) + "\n")
                i+=1
            waveLive.close()

        return fitness_score 



"""
Systematically convert and upload the bitstream files to gather fitness data for the epoch
"""
def gather_data(individual="", current_gen=None):
    global BEST, MUTATION_LIST;
    # print("MUTATION LIST: " + str(MUTATION_LIST))

    if not MUTATION_LIST:   
        # for name in os.listdir(BIN_DIR):
        #     os.remove(BIN_DIR+name)
        #     compile_circuit((os.path.splitext(name)[0])+'.asc')
        print("Mutation List is Blank")
    else:
        for circuit in MUTATION_LIST:
            compile_circuit(circuit+'.asc')

    count = 1
    total = len(os.listdir(BIN_DIR))
    orderedDirectory = sorted(os.listdir(BIN_DIR), key = lambda l: int(l.split('hardware')[1].split('.bin')[0]))
    for compiled_circuit in orderedDirectory:
        cc = os.path.splitext(compiled_circuit)[0] 
        if (cc in MUTATION_LIST or cc == BEST):# or not MUTATION_LIST):
            print(bcolors.OKBLUE + "Running Circuit " + compiled_circuit + bcolors.ENDC + ": " + str(count) + " of " + str(total))
            count += 1
            data = run_circuit(compiled_circuit)


"""
Mutate a gene of individuals that don't perform well
"""
def mutate(individual):
    global MUTATION_LIST;
    ind = os.path.splitext(individual)[0]
    if ind not in MUTATION_LIST: MUTATION_LIST.append(ind)

    print("MUTATING "+individual)

    with open(ASC_DIR+individual, "r+") as file:
        # search the hardware file for the appropriate logic tiles
        data = file.readlines()
        for i in range(4, 10):
            for j in range(1, 17):
                for ind, lines in enumerate(data):
                    if ".logic_tile "+str(i)+" "+str(j)+"\n" in lines:
                        if (ROUTING == 'MOORE'):
                            for row in chain(range(1, 3), range(13,14)):
                                configuration_codon = ""
                                # the number of bits programming each logic element
                                for column in range(0, 54):
                                    if column in PROTECTED_COLUMNS:
                                        configuration_codon += str(data[ind+row][column])
                                    else:
                                        if (random.uniform(0,1) <= MUTATION_PROBABILITY):
                                            m = random.randint(0,1)
                                            configuration_codon += str(m)
                                        else:
                                            configuration_codon += str(data[ind+row][column])

                                # write the codon to this line of the logic tile (data[ind+row])
                                data[ind+row] = configuration_codon+"\n"
                        elif (ROUTING == 'NEWSE'):
                            for row in range(1,3):
                                configuration_codon = ""
                                # the number of bits programming each logic element
                                for column in range(0, 54):
                                    if column in PROTECTED_COLUMNS:
                                        configuration_codon += str(data[ind+row][column])
                                    else:
                                        if (random.uniform(0,1)() <= MUTATION_PROBABILITY):
                                            m = random.randint(0,1)
                                            configuration_codon += str(m)
                                        else:
                                            configuration_codon += str(data[ind+row][column])

                                # write the codon to this line of the logic tile (data[ind+row])
                                data[ind+row] = configuration_codon+"\n"

        file.close()
        
        # file.close()
        with open(ASC_DIR+individual, "r+") as file:
            file.writelines(data)

"""
Single Point Crossover - copy some series of chiasmas from fitter circuit into children
"""
def crossover(parent1, parent2):
    configuration_codon1 = ""
    configuration_codon2 = ""
    crossover_point1 = random.randint(1,2)
    crossover_point2 = random.randint(13,14)
    if (random.uniform(0, 1) <= CROSSOVER_PROBABILITY):
        print("Breeding: ", parent1, parent2)
        with open(ASC_DIR+parent1, "r") as file:
            # search the hardware file for the appropriate logic tiles
            data = file.readlines()
            for i in range(4, 10):
                for j in range(1, 17):
                    for ind, lines in enumerate(data):
                        if ".logic_tile "+str(i)+" "+str(j)+"\n" in lines:
                            for row in range(1, 3):
                                if row == crossover_point1:
                                    for column in range(0,54):
                                        configuration_codon1 += str(data[ind+row][column])
                            for row in range(13, 15):
                                if row == crossover_point2:
                                    for column in range(0,54):
                                        configuration_codon2 += str(data[ind+row][column])
                            with open(ASC_DIR+parent2, "r+") as file2:
                                # search the hardware file for the appropriate logic tiles
                                data2 = file2.readlines()
                                if ".logic_tile "+str(i)+" "+str(j)+"\n" in lines:
                                    for row in range(1, 3):
                                        if row == crossover_point1:
                                            data2[ind+row] = configuration_codon1+"\n"
                                            configuration_codon1=""
                                    for row in range(13, 15):
                                        if row == crossover_point2:
                                            data2[ind+row] = configuration_codon2+"\n"
                                            configuration_codon2=""
                            with open(ASC_DIR+parent2, "r+") as file2:
                                file2.writelines(data2)
                            file2.close()


"""
Single Elite Tournament style fitness test
"""
def single_elite_tournament(current_gen):
    global BEST, BEST_FITNESS, FITNESS;

    population = os.listdir(DATA_DIR)
    # BEST = max(FITNESS.items(), key=operator.itemgetter(1))[0]
    best_fitness = BEST_FITNESS#max(FITNESS.items(), key=operator.itemgetter(1))[1]

    print("Tournament Number: " + str(current_gen))
    for ind in population:
        ind = os.path.splitext(ind)[0]
        if ind != BEST: # don't overwrite the best
            if best_fitness >= FITNESS.get(ind):
                copyfile(ASC_DIR+str(BEST)+".asc", ASC_DIR+str(ind)+".asc") #cloning
                # crossover(BEST+'.asc',ind+'.asc')
                mutate(ind+'.asc')
        else:
            print(ind + " is current BEST")


"""
Fractional Elite Tournament style fitness test
"""
def fractional_elite_tournament(current_gen):
    global FITNESS;

    population = os.listdir(DATA_DIR)
    elite_group = []
    num_of_elites = int(math.ceil(ELITISM_FRACTION * POPULATION_SIZE)) # ceil rounds up
    print("Number of Elites: " + str(num_of_elites))
    ranked_fitness = sorted(FITNESS.items(), key=operator.itemgetter(1), reverse=True)
    print("Ranked Fitness: " + str(ranked_fitness))
    if num_of_elites == 1: 
        elite_group.append(ranked_fitness[0])
    else:
        for i in range(0, num_of_elites):
            elite_group.append(ranked_fitness[i])
    print("Elite Group: " + str(elite_group))
    for ind in population:
        ind = os.path.splitext(ind)[0]
        rand_elite = random.choice(elite_group)
        # print("Rand Elite: " + str(rand_elite)) # show elites and scores
        if FITNESS.get(rand_elite[0]) >= FITNESS.get(ind) and rand_elite[0] != ind:
            if CROSSOVER_PROBABILITY == 0.0:
                print("Cloning: "+str(rand_elite[0])+".asc ---> "+str(ind)+".asc")
                copyfile(ASC_DIR+str(rand_elite[0])+".asc", ASC_DIR+str(ind)+".asc") #clone the elite
            else:
                crossover(rand_elite[0]+'.asc',ind+'.asc')
            mutate(ind+'.asc')


"""
Classical Tournament Style fitness selection
"""
def classic_tournament(current_gen):
    global BEST, BEST_FITNESS, FITNESS;

    population = os.listdir(DATA_DIR)
    #BEST = max(FITNESS.items(), key=operator.itemgetter(1))[0]

    print("Tournament Number: " + str(current_gen))
    random.shuffle(population)
    for A, B in grouper(population, 2):
        A = os.path.splitext(A)[0]
        B = os.path.splitext(B)[0]

        #Evaluate the data files
        if FITNESS.get(A) > FITNESS.get(B):
            print("Fitness "+str(A)+": "+str(FITNESS.get(A))+ " > " +"Fitness "+str(B)+": "+str(FITNESS.get(B)))
            crossover(A +'.asc', B +'.asc')
            mutate(B +'.asc') 
        else:
            print("Fitness "+str(A)+": "+str(FITNESS.get(A))+ " < " +"Fitness "+str(B)+": "+str(FITNESS.get(B)))
            crossover(B +'.asc', A +'.asc')
            mutate(A +'.asc')



"""
Fitness Proportionate Selection
"""
def fit_prop_sel():
    global FITNESS;

    population = os.listdir(DATA_DIR)
    elite_group = []
    elite_names = []
    elite_fitnesses = []
    elite_prob = []

    num_of_elites = int(math.ceil(ELITISM_FRACTION * POPULATION_SIZE)) # ceil rounds up
    print("Number of Elites: " + str(num_of_elites))
    ranked_fitness = sorted(FITNESS.items(), key=operator.itemgetter(1), reverse=True)
    print("Ranked Fitness: " + str(ranked_fitness))
    if num_of_elites == 1: 
        elite_group.append(ranked_fitness[0])
        elite_names.append(ranked_fitness[0][0])
        elite_fitnesses.append(ranked_fitness[0][1])
        elite_prob.append(1.0)
    else:
        for i in range(0, num_of_elites):
            elite_group.append(ranked_fitness[i])
            elite_names.append(ranked_fitness[i][0])
            elite_fitnesses.append(ranked_fitness[i][1])
    
    elite_sum = sum(elite_fitnesses)
    if elite_sum > 0:
        for i in range(0, num_of_elites): 
            sel_prob = elite_fitnesses[i]/elite_sum
            elite_prob.append(sel_prob)
    elif elite_sum == 0:
        for i in range(0, num_of_elites): 
            sel_prob = 1/num_of_elites
            elite_prob.append(sel_prob)
    else:
        for i in range(0, num_of_elites): 
            sel_prob = 1/num_of_elites
            elite_prob.append(sel_prob)
    print("Elite Group: " + str(elite_group))
    print("Elite Probs: " + str(elite_prob))
    for ind in population:
        ind = os.path.splitext(ind)[0]
        if sum(elite_prob) > 0.0:
            rand_elite = choice(elite_names, num_of_elites, p=elite_prob)
        else:
            rand_elite = choice(elite_names)
        # print("Rand Elite: " + str(rand_elite)) # show elites and scores
        if FITNESS.get(rand_elite[0]) >= FITNESS.get(ind) and rand_elite[0] != ind:
            if CROSSOVER_PROBABILITY == 0.0:
                print("Cloning: "+str(rand_elite[0])+".asc ---> "+str(ind)+".asc")
                copyfile(ASC_DIR+str(rand_elite[0])+".asc", ASC_DIR+str(ind)+".asc") #clone the elite
            else:
                crossover(rand_elite[0]+'.asc',ind+'.asc')
            mutate(ind+'.asc')


"""
Initialize the GA
"""
def main():
    global BEST, BEST_EPOCH, BEST_FITNESS, CURRENT_GEN, FITNESS, MUTATION_LIST, PULSE_FUNC, START_TIME, START_DATETIME, EXPLANATION, PULSES;

    explanation = raw_input("Explain this experiment: ")
    EXPLANATION = explanation
    header = "FPGA/MCU [1] \n"


    if INIT_MODE != "CONTINUE":
        # Clear temporary folders
        for temps in os.listdir(ASC_DIR): os.remove(ASC_DIR+temps)
        for temps in os.listdir(BIN_DIR): os.remove(BIN_DIR+temps)
        for temps in os.listdir(DATA_DIR): os.remove(DATA_DIR+temps)


    if explanation != "test":
        #Make a directory to store data
        analysis_dir = ANALYSIS + str(datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S"))
        analysis_l_dir = analysis_dir+"/log/"
        analysis_a_dir = analysis_dir+"/asc/"
        analysis_b_dir = analysis_dir+"/best/"
        analysis_bh_dir = analysis_dir+"/best/html/"
        analysis_ba_dir = analysis_dir+"/best/asc/"
        analysis_bl_dir = analysis_dir+"/best/log/"
        
        if not os.path.exists(analysis_dir):
            os.mkdir(analysis_dir)
            os.mkdir(analysis_l_dir)
            os.mkdir(analysis_a_dir)
            os.mkdir(analysis_b_dir)
            os.mkdir(analysis_bh_dir)
            os.mkdir(analysis_ba_dir)
            os.mkdir(analysis_bl_dir)

        #Put the readme in the Analysis folder
        readme_file = open(analysis_dir+"/README.txt", "w")
        readme_file.write(header)
        readme_file.write(str(explanation))
        readme_file.close()


    # Start the monitor
    START_DATETIME = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
    START_TIME = time.time()
    print("Creating the monitor file...")
    with open(MONITOR, "w+") as openFile:
        openFile.write("                                    Evolutionary Experiment Monitor\n")
        openFile.write("========================================================================================================\n")
        openFile.write("Parameters and updates load during circuit evaluation")
        for i in range(0,23):
            openFile.write('.\n')
    if LAUNCH_MONITOR:
        os.system("gnome-terminal -e 'python Monitor.py' --geometry=105x29")
        print("Launching the Live Plot window...")
        os.system("gnome-terminal -e 'python PlotEvolutionLive.py' --geometry=105x29")

    # Randomize initial circuits until waveform variance or pulses are found
    if RANDOMIZE_UNTIL == "PULSE":
        print("PULSE randomization mode selected.")
        randomize_until_pulses() 
    elif RANDOMIZE_UNTIL == "VARIANCE":    
        print("VARIANCE randomization mode selected.")
        if VARIANCE_THRESHOLD <= 0:
            print(bcolors.FAIL + "ERROR: VARIANCE_THRESHOLD <= 0 as set in config.ini" + bcolors.ENDC)
            exit()
        randomize_until_variance()
    elif RANDOMIZE_UNTIL == "NO":
        print("NO randomization mode selected.")
    else:
        print(bcolors.FAIL + "ERROR: RANDOMIZE_UNTIL not set in config.ini" + bcolors.ENDC)
        exit()
    
    
    if INIT_MODE != "CONTINUE":
        # Clear temporary folders
        clear_temp_dirs()
        # Prepare copies of the hardware.asc template
        copy_hardware_template()
    
    # generate random population
    populate(POPULATION_SIZE)  # currently copying without randomization

    current_generation = 1
    while current_generation != GENERATIONS+1:
        CURRENT_GEN = current_generation
        epoch_time = time.time()
        gather_data(current_gen=current_generation)

        # Update console with generational fitness information
        print("================================================================================================================")
        print("================================================================================================================")
        print("================================================================================================================")
        if current_generation == 1:
            BEST = max(FITNESS.items(), key=operator.itemgetter(1))[0]
            BEST_FITNESS =  max(FITNESS.items(), key=operator.itemgetter(1))[1]
            BEST_EPOCH = current_generation
        best = max(FITNESS.items(), key=operator.itemgetter(1))[0]
        best_val = max(FITNESS.items(), key=operator.itemgetter(1))[1]
        if best_val > BEST_FITNESS:
            print("New Best Found!")
            BEST = best
            BEST_FITNESS = best_val
            BEST_EPOCH = current_generation
        epoch_time = time.time() - epoch_time
        print("CURRENT BEST: " + str(BEST) + " : EPOCH " + str(BEST_EPOCH) + " : FITNESS " + str(BEST_FITNESS))
        print("HIGHEST FITNESS OF EPOCH " + str(current_generation) + " IS: " + str(best) + " = " + str(best_val)
        + ", over " +str(epoch_time)+" seconds")
        print("================================================================================================================")
        print("================================================================================================================")
        print("================================================================================================================")

        # Write to live data plot file
        with open("bestlivedata.log", "a") as liveFile:
            avg = sum(FITNESS.values()) / POPULATION_SIZE
            liveFile.write(str(current_generation) + ", " + str(best_val) + ", " + str(avg) + "\n") #str(BEST_FITNESS)+"\n")
            liveFile.close()
        
        # Save all circuits and logs this generation
        if explanation != "test":
            # Update directory name with new generation number
            a_dir = analysis_a_dir+"GENERATION-" + str(current_generation)+'/'
            l_dir = analysis_l_dir+"GENERATION-" + str(current_generation)+'/'
            # Make the new directory
            os.mkdir(a_dir)
            os.mkdir(l_dir)
            # Copy circuits and logs into new directory
            for files in os.listdir(DATA_DIR): copyfile(DATA_DIR+str(files), l_dir+str(files))
            for files in os.listdir(ASC_DIR): copyfile(ASC_DIR+str(files), a_dir+str(files))
            # Copy BEST circuit and log
            copyfile(ASC_DIR+str(BEST)+".asc", analysis_ba_dir+"BEST_CIRCUIT_GENERATION-"+str(current_generation)+".asc")
            copyfile(DATA_DIR+str(BEST)+".log", analysis_bl_dir+"BEST_CIRCUIT_GENERATION-"+str(current_generation)+".log")
            # Generate HTML view of BEST
            cmd = "python {0} {1}{2}{3} {4}{5}".format("../../ice40_viewer-master/iceview_html.py", "../asc/", str(BEST), ".asc", 
                                                        analysis_bh_dir, "BEST_CIRCUIT_GENERATION-"+str(current_generation)+".html")
            os.system(cmd)

        if  SELECTION == 'CLASSIC_TOURN':
            classic_tournament(current_generation)
        elif SELECTION == 'SINGLE_ELITE':
            single_elite_tournament(current_generation)
        elif SELECTION == 'FRAC_ELITE':
            fractional_elite_tournament(current_generation)
        elif SELECTION == 'FIT_PROP_SEL':
            fit_prop_sel()
        else:
            print("NO SELECTION METHOD USED IN config.ini")
            exit()
        # if BEST_FITNESS > 100.0:
        #     PULSE_FUNC = True
        
        current_generation += 1
        PULSES = {}
       

    print("Best Bitstream: " + str(BEST) + " (fitness: " + str(BEST_FITNESS) + ")")

main()
os.system("gnome-terminal -e 'iceprog -d i:0x0403:0x6010:0 ../example_hardware_files/hardware_blink.bin'")

# Evolve a 1khz oscillator from total random initial population of 96 blocks.