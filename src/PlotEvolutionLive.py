import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import configparser
import re
from Config import Config
import math
import numpy as np

"""
Static parameters can be found and changed in the config.ini file in the root project folder
DO NOT CHANGE THEM HERE
"""

MAX_VIOLIN_PLOTS = 10

def animate_generation(i):
    avg_fitness = []
    graph_data = open('workspace/alllivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    
    # There used to be a bug where the program always believed it was in sim mode, but once that was fixed, the code below
    # broke the chart on non-simulation mode. As such, the target frequency is just always set to 1728, which worked fine before
    #if not config.get_simulation_mode() == "FULLY_INTRINSIC":
        #target_freq = 1728
        # Based on my calculations for the maximum number of bits we can 
        # modify with our given search space constraints
    #else:
        #target_freq = [config.get_desired_frequency()]*(config.get_population_size+2)
    target_freq = 1728
    
    base = [config.get_desired_frequency()]*0
    for line in lines:
        if len(line) > 1:
            x, y, z = line.split(',')
            if x == "../hardware": x = "hardware0";
            match = re.match(r"([a-z]+)([0-9]+)", x, re.I)
            if match:
                items = match.groups()
                xs.append(int(items[1]))
            ys.append(float(y))
    avg = 0.0
    if sum(ys) > 0:
        avg = sum(ys)/len(ys)
    else:
        avg_fitness.append(avg)
    ax1.clear()
    # ax1.plot(xs, ys)
    ax1.set_xlim([0, config.get_population_size()+1])
    ax1.plot(target_freq, "r--")
    ax1.plot(base, "w-")
    ax1.plot(avg_fitness, color="violet")
    '''if not config.get_simulation_mode() == "FULLY_INTRINSIC":
        ax1.set_yscale('symlog')
        ax1.set_ylim([0, 1000000])'''
    # ax1.plot.stem(xs,ys,  color="green", use_line_collection=True)
    ax1.scatter(xs, ys)
    # plt.stem(xs, ys, markerfmt="bo", linefmt="b-", use_line_collection=True)
    # plt.plot(xs, ys, color="blue")
    ax1.set(xlabel='Circuit Number', ylabel='Fitness', title='Circuit Fitness this Generation')

# fig2 = plt.figure()
def animate_epoch(i):
    graph_data = open('workspace/bestlivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    zs = []
    ws = []
    ts = []
    ds = []
    for line in lines:
        if len(line) > 1:
            x, y, z, w, t, d = line.split(',')
            xs.append(int(x))
            ys.append(float(y))
            zs.append(float(z))
            ws.append(float(w))
            ts.append(float(t))
            ds.append(float(d))
    ax2.clear()
    # ax2.set_yscale('symlog')
    # Plot the overall best before the gen best so the gen best line appears on top
    ax2.plot(xs, ts, color="#00b87d") # Ovr best Fitness
    ax2.plot(xs, ys, color="green") # Generation/Epoch Best Fitness
    ax2.plot(xs, zs, color="red") # Generation Worst Fitness
    ax2.plot(xs, ws, color="yellow") # Generation Average Fitness
    ax2.tick_params(axis='y', labelcolor='white')
    
    ax3.clear()
    ax3.plot(xs, ds, color="#5a70ed") # Generation diversity measure
    ax3.tick_params(axis='y', labelcolor='#5a70ed')
    ax3.set_ylabel('Diversity', color='#5a70ed')
    ax3.set_ylim(bottom=0)
    
    ax2.set(xlabel='Generation', ylabel='Fitness', title='Best Circuit Fitness per Generation')


def animate_waveform(i):    
    graph_data = open('workspace/waveformlivedata.log','r').read()
    lines = graph_data.split('\n')
    pulse_trigger = [341]*500
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(',')
            xs.append(int(x))
            ys.append(float(y))
    ax4.clear()
    ax4.set_ylim([0, 1000])
    ax4.plot(pulse_trigger, "r--")
    ax4.plot(xs, ys, color="blue")
    ax4.set(xlabel='Time (50 mS Total)', ylabel='Voltage (normalized)', title='Current Hardware Waveform')

def animate_map(i):
    graph_data = open('workspace/maplivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    sizes = []
    fits = []
    colors = []
    if len(lines) > 0 and len(lines[0]) > 0:
        scale_factor = int(lines[0])
        lines.pop(0) # Remove scale factor from the lines set

        for line in lines:
            vals = line.split(' ')
            if (len(vals) > 2 and len(vals[2]) > 0):
                row = int(vals[0])
                col = int(vals[1])
                fit = float(vals[2])
                fits.append(fit)
                xs.append((col + 0.5) * scale_factor)
                ys.append((row + 0.5) * scale_factor)

        # We'll make 25 the size of the largest individual, and 1 the size of the smallest
        min_fit = min(fits)
        max_fit = max(fits)
        max_size = 25
        min_size = 5
        old_range = max_fit - min_fit
        new_range = max_size - min_size
        
        all_colors = [ 'red', '#ff8000', 'yellow', 'green', 'blue', '#4400ff', 'magenta' ]
        color_i = 0
        for f in fits:
            size = (f - min_fit) * new_range / old_range + min_size
            sizes.append(size)
            colors.append(all_colors[color_i])
            color_i = (color_i + 1) % len(all_colors)
    
    ax5.clear()

    # Add a line to the middle that separates possible from impossible cells
    ax5.plot([0, 1024], [0, 1024], color='#444444', linewidth=0.5)

    ax5.scatter(xs, ys, s=sizes, c=colors)

    ax5.set_xlim(0, 1024)
    ax5.set_ylim(0, 1024)
    ax5.set_aspect('equal')
    #ax5.set_xticks(np.arange(0, 1024, 50), minor=True)
    #ax5.set_yticks(np.arange(0, 1024, 50), minor=True)
    #ax5.grid(color = '#363636', which = 'minor')
    ax5.set(xlabel='Max Voltage (norm)', ylabel='Min Voltage (norm)', title='Elite Map')

def animate_pops(i):
    graph_data = open('workspace/poplivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    ylabels = []
    ylabel_i = 1
    
    x = 1
    for line in lines:
        if len(line) > 1:
            xs.append(x)
            x = x + 1

            args = line.split(' ')
            parsed = []
            for i in range(len(args)):
                if len(args[i]) > 0:
                    parsed.append(int(args[i]))
            if len(ys) <= 0:
                # Haven't initialized the y's list yet, lets throw in an empty list for each out our source populations
                for i in range(len(parsed)):
                    ys.append([])

            # Now we need to add to ys based on the index in parsed
            ylabels.append("Population " + str(ylabel_i))
            ylabel_i = ylabel_i + 1
            for i in range(len(parsed)):
                ys[i].append(parsed[i])
    
    if len(ys) > 0:
        ax6.clear()
        ax6.stackplot(xs, ys, labels=ylabels)
        ax6.legend(loc='upper right')
        ax6.set(xlabel='Generation', ylabel='Number from Population', title='Circuits from Each Source Population')

def anim_violin_plots(i):
    data = open('workspace/violinlivedata.log','r').read()
    collections = []
    gens = []
    widths = []
    last = 0
    lines = data.split('\n')
    # Decide which generations to include based on the number to have and the number available
    interval = len(lines) / MAX_VIOLIN_PLOTS
    if len(lines) < MAX_VIOLIN_PLOTS:
        interval = 1
    index = 0
    while int(index + interval) < len(lines):
        index = index + interval
        int_index = int(index)
        line = lines[int_index]
        if len(line) > 1:
            vals = line.split(':')
            gen = int(vals[0])
            widths.append((gen - last) * 0.8)
            last = gen
            gens.append(gen)
            pts = vals[1].split(',')
            collections.append(list(map(lambda x: float(x), pts)))

    if len(collections) > 0:
        ax7.clear()
        ax7.violinplot(collections, positions=gens, widths=widths)

config_parser = configparser.ConfigParser()
config_parser.read("data/config.ini")
config = Config(config_parser)

style.use('dark_background')

rows = 2
cols = 1
has_wf_plot = False
if (config.get_simulation_mode() == 'FULLY_INTRINSIC' and config.get_fitness_func() != "PULSE_COUNT") or config.get_simulation_mode() == 'FULLY_SIM':
    rows = rows + 1
    has_wf_plot = True

has_map_plot = False
if config.get_selection_type() == 'MAP_ELITES':
    # Replace the fitness plot with the map plot
    has_map_plot = True

has_pop_plot = False
if config.get_init_mode() == 'EXISTING_POPULATION':
    rows = rows + 1
    has_pop_plot = True

fig = plt.figure()
fig2 = plt.figure()

ax2 = fig.add_subplot(rows, cols, 1)
ax3 = ax2.twinx()
if has_wf_plot:
    ax4 = fig.add_subplot(rows, cols, 3)

if has_map_plot:
    ax5 = fig.add_subplot(rows, cols, 2)
else:
    ax1 = fig.add_subplot(rows, cols, 2)
    ax1.set_xticks(range(1, config.get_population_size(), 1))

if has_pop_plot:
    # Put this plot in the last slot
    ax6 = fig.add_subplot(rows, cols, rows * cols)

ax7 = fig2.add_subplot(1, 1, 1)

if has_wf_plot:
    ani3 = animation.FuncAnimation(fig, animate_waveform)#, interval=200)

if has_map_plot:
    ani4 = animation.FuncAnimation(fig, animate_map)
else:
    ani = animation.FuncAnimation(fig, animate_generation)

if has_pop_plot:
    ani6 = animation.FuncAnimation(fig, animate_pops, interval=500)

ani7 = animation.FuncAnimation(fig2, anim_violin_plots)

ani2 = animation.FuncAnimation(fig, animate_epoch)

plt.subplots_adjust(hspace=0.50)
plt.show()