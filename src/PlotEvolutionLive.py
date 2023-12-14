import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib import colormaps
import configparser
import re
from Config import Config
import math 
import numpy as np
from utilities import determine_color

"""
Static parameters can be found and changed in the config.ini file in the root project folder
DO NOT CHANGE THEM HERE
"""

MAX_VIOLIN_PLOTS = 10
HEATMAP_BINS = 40 
FRAME_INTERVAL = 10000

config = Config("workspace/builtconfig.ini")

#the below were moved to the config class, since they were useful in some other classes
# # True if the fitness function counts pulses
# def is_pulse_func():
#     return (config.get_fitness_func() == 'PULSE_COUNT' or config.get_fitness_func() == 'TOLERANT_PULSE_COUNT' 
#             or config.get_fitness_func() == 'SENSITIVE_PULSE_COUNT' or config.get_fitness_func() == 'PULSE_CONSISTENCY')
# # Contrary to the above, this only returns true if the target is to count pulses for a target frequency
# def is_pulse_count():
#     return (config.get_fitness_func() == 'PULSE_COUNT' or config.get_fitness_func() == 'TOLERANT_PULSE_COUNT' 
#             or config.get_fitness_func() == 'SENSITIVE_PULSE_COUNT')

def animate_generation(i):
    graph_data = open('workspace/alllivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    
    is_transparent = False
    for line in lines:
        if len(line) > 1:
            x, y, z = line.split(',')
            all_ys = y.split(';')
            if len(all_ys) > 1:
                is_transparent = True
            for y in all_ys:
                xs.append(int(x))
                ys.append(float(y))
    avg = 0.0
    if len(ys) > 0:
        avg = sum(ys)/len(ys)

    ax1.clear()
    ax1.set_xlim([0, config.get_population_size()+1])
    ax1.hlines(y=avg, xmin=1, xmax=config.get_population_size(), color="violet", linestyles="dotted")
    ax1.scatter(xs, ys, color=('#f0f8ffdd' if is_transparent else '#f0f8ffff'))
    if config.is_pulse_func():
        title = 'Circuit Pulses this Generation'
        ylabel = 'Pulses'
        # Add a line for desired frequency
        if config.is_pulse_count():
            ax1.hlines(y=config.get_desired_frequency(), xmin=1, xmax=config.get_population_size(), color="red", linestyles="dotted")
        ax1.set_ylim([0, None])
    else:
        title = 'Circuit Fitness this Generation'
        ylabel = 'Fitness'
    ax1.set(xlabel='Circuit Number', ylabel=ylabel, title=title)

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
    if config.using_transfer_interval():
        for i in range(0,len(lines),config.get_transfer_interval()):
            ax2.axvline(x=i, color="white", linestyle="dashed")

    if config.get_use_ovr_best():
        # Plot the overall best before the gen best so the gen best line appears on top
        ax2.plot(xs, ts, color="#00b87d") # Ovr best Fitness
    ax2.plot(xs, ys, color="green") # Generation/Epoch Best Fitness
    ax2.plot(xs, zs, color="red") # Generation Worst Fitness
    ax2.plot(xs, ws, color="yellow") # Generation Average Fitness
    ax2.tick_params(axis='y', labelcolor='white')

    if config.get_diversity_measure() != "NONE":
        ax3.clear()
        ax3.plot(xs, ds, color="#5a70ed") # Generation diversity measure
        ax3.tick_params(axis='y', labelcolor='#5a70ed')
        ax3.set_ylabel('Diversity', color='#5a70ed')
        ax3.set_ylim(bottom=0)
        ax3.yaxis.set_label_position("right")
    
    ax2.set(xlabel='Generation', ylabel='Fitness', title='Best Circuit Fitness per Generation')

    if(config.get_save_plots()):
        fig.savefig(plots_dir.joinpath("main.png"))

def animate_epoch_pulses(i):
    graph_data = open('workspace/pulselivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = [] # closest to desired frequency
    ys = [] # avg # of pulses
    zs = [] # min # of pulses
    ws = [] # max # of pulses
    ts = []
    for line in lines:
        if len(line) > 1:
            t, d = line.split(':')
            d = list(map(lambda x: int(x), d.split(',')))
            xs.append(d[0])
            ys.append(np.average(d))
            zs.append(min(d))
            ws.append(max(d))
            ts.append(int(t))
    ax9.clear()

    ax9.plot(ts, zs, color="cornflowerblue", linewidth=0.75)
    ax9.plot(ts, ws, color="coral", linewidth=0.75)
    ax9.plot(ts, ys, color="yellow", linewidth=0.75)
    ax9.plot(ts, xs, color="lime")
    ax9.tick_params(axis='y', labelcolor='white')

    if config.is_pulse_count():
        ax9.hlines(y=config.get_desired_frequency(), xmin=1, xmax=len(lines), color="violet", linestyles="dotted")  
    ax9.set(xlabel='Generation', ylabel='Pulses', title='Best Circuit Pulse Count per Generation')

    if config.using_transfer_interval():
        for i in range(0,len(lines),config.get_transfer_interval()):
            ax9.axvline(x=i, color="white", linestyle="dashed")

    if(config.get_save_plots()):
        fig4.savefig(plots_dir.joinpath("pulses.png"))


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
    fits = []
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

    heatmap_colors = [[.83, .06, 0], [.83, .4, 0], [.8, .8, .63], [.27, .59, .8], [.31, .31, .8]]
    colors = []
    max_fit = max(fits)
    min_fit = min(fits)
    for f in fits:
        ratio = (f-min_fit) / (max_fit-min_fit)
        color = determine_color(ratio, heatmap_colors)
        colors.append(color)
    
    ax5.clear()

    # Add a line to the middle that separates possible from impossible cells
    ax5.plot([0, 1024], [0, 1024], color='#444444', linewidth=0.5)

    ax5.scatter(xs, ys, c=colors, s=50)

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
    lines = data.split('\n')
    # Decide which generations to include based on the number to have and the number available
    interval = len(lines) / MAX_VIOLIN_PLOTS
    if len(lines) < MAX_VIOLIN_PLOTS:
        interval = 1
    # Makes sure the first generation displayed will always be generation 2 (the first where we have interesting data)
    index = 1 - interval
    while int(index + interval) < len(lines):
        index = index + interval
        int_index = int(index)
        line = lines[int_index]
        if len(line) > 1:
            vals = line.split(':')
            gen = int(vals[0])
            gens.append(gen)
            pts = vals[1].split(',')
            collections.append(list(map(lambda x: float(x), pts)))

    for i in range(0, len(collections)):
        widths.append(interval * 0.5)

    if len(collections) > 0:
        ax7.clear()
        if config.using_transfer_interval():
            for i in range(0,len(lines),config.get_transfer_interval()):
                ax7.axvline(x=i, color="white", linestyle="dashed")
        ax7.violinplot(collections, positions=gens, widths=widths)

    if(config.get_save_plots()):
        fig2.savefig(plots_dir.joinpath("violin_plots.png"))

def anim_violin_plots_pulse(i):
    data = open('workspace/pulselivedata.log','r').read()
    collections = []
    gens = []
    widths = []
    lines = data.split('\n')
    # Decide which generations to include based on the number to have and the number available
    interval = len(lines) / MAX_VIOLIN_PLOTS
    if len(lines) < MAX_VIOLIN_PLOTS:
        interval = 1
    # Makes sure the first generation displayed will always be generation 2 (the first where we have interesting data)
    index = 1 - interval
    while int(index + interval) < len(lines):
        index = index + interval
        int_index = int(index)
        line = lines[int_index]
        if len(line) > 1:
            vals = line.split(':')
            gen = int(vals[0])
            gens.append(gen)
            pts = vals[1].split(',')
            collections.append(list(map(lambda x: float(x), pts)))

    for i in range(0, len(collections)):
        widths.append(interval * 0.5)

    if len(collections) > 0:
        ax10.clear()
        ax10.violinplot(collections, positions=gens, widths=widths)
        if config.using_transfer_interval():
            for i in range(0,len(lines),config.get_transfer_interval()):
                ax10.axvline(x=i, color="white", linestyle="dashed")
        if config.is_pulse_count():
            ax10.hlines(y=config.get_desired_frequency(), xmin=1, xmax=len(lines), color="violet", linestyles="dotted")  
        ax10.set(xlabel='Generation', ylabel='Pulses')

def anim_heatmap(i):
    global max_pulses
    if config.is_pulse_func():
        data = open('workspace/pulselivedata.log','r').read()
    else:
        data = open('workspace/heatmaplivedata.log','r').read()

    
    lines = data.split('\n')
    collections = []
    gens = []

    for line in lines:
        if len(line) > 1:
            vals = line.split(':')
            pts = vals[1].split(',')
            for pt in pts:
                gens.append(int(vals[0]))
                collections.append(float(pt))
            
    ax8.clear()                         
    ax8.hist2d(gens,collections,bins=HEATMAP_BINS)

    if config.is_pulse_func():
        ax8.set(xlabel='Generation', ylabel='Pulses')
    else:
        ax8.set(xlabel='Generation', ylabel='Voltage (Normalized)')

    if config.using_transfer_interval():
            for i in range(0,len(lines),config.get_transfer_interval()):
                ax8.axvline(x=i, color="white", linestyle="dashed")

    if(config.get_save_plots()):
        fig3.savefig(plots_dir.joinpath("heatmap.png"))
        

def animate_sensitivity(i):
    graph_data = open('workspace/fitnesssensitivity.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    ts = []
    for line in lines:
        if len(line) > 1:
            t,d = line.split(':')
            d = d.split(",")
            xs.append(float(d[0]))
            ys.append(float(d[1]))
            ts.append(float(t))

    #fitness
    ax2.clear()
    ax2.hist(xs, bins=HEATMAP_BINS)
    ax2.tick_params(axis='y', labelcolor='white')
    ax2.set_ylim(bottom=0)

    ax3.clear()
    ax3.hist2d(ts,xs,bins=HEATMAP_BINS)
    ax3.tick_params(axis='y', labelcolor='white')
    ax3.set_ylim(bottom=0)
    
    #pulses/mean voltage
    ax4.clear()
    ax4.hist(ys, bins=HEATMAP_BINS)
    ax4.tick_params(axis='y', labelcolor='white') 
    ax4.set_ylim(bottom=0)

    ax5.clear()
    ax5.hist2d(ts, ys, bins=HEATMAP_BINS)
    ax5.tick_params(axis='y', labelcolor='white') 
    ax5.set_ylim(bottom=0)
    
    ax2.set(xlabel='Fitness', ylabel='Count', title='Circuit Fitness per Trial')
    ax3.set(xlabel='Trial', ylabel='Fitness', title='Circuit Fitness per Trial')
    if config.get_fitness_func() != "PULSE_COUNT":
        ax4.set(xlabel='Mean Voltage (Normalized)', ylabel='Count', title='Circuit Voltage per Trial')
        ax5.set(xlabel='Trial', ylabel='Mean Voltage (Normalized)', title='Circuit Voltage per Trial')
    else:
        ax4.set(xlabel='Pulses', ylabel='Count', title='Pulses')
        ax5.set(xlabel='Trial', ylabel='Pulses', title='Pulses')


    if(config.get_save_plots()):
        fig.savefig(plots_dir.joinpath("sensitivity.png"))

def animate_pulse_map(i):
    graph_data = open('workspace/maplivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    fits = []
    if len(lines) > 0 and len(lines[0]) > 0:
        scale_factor = int(lines[0])
        lines.pop(0) # Remove scale factor from the lines set

        for line in lines:
            # Two values; the pulse count (frequency) and the fitness
            for line in lines:
                vals = line.split(' ')

                col = int(vals[0])
                fit = float(vals[1])
                fits.append(fit)
                xs.append((col-0.5) * scale_factor)

        ax5.clear()

        ax5.bar(xs, fits, width=scale_factor)

        ax5.set_xlim(1000, 150_000)
        ax5.set_ylim(0, 1000)
        ax5.set(xlabel='Frequency (Hz)', ylabel='Fitness', title='Elite Map')


plots_dir = config.get_plots_directory()

style.use('dark_background')

if (config.get_simulation_mode() == 'INTRINSIC_SENSITIVITY'):
    fig = plt.figure(figsize=(9,7))
    ax2 = fig.add_subplot(2, 2, 1)
    ax3 = fig.add_subplot(2, 2, 2)
    ax4 = fig.add_subplot(2, 2, 3)
    ax5 = fig.add_subplot(2, 2, 4)
    ani = animation.FuncAnimation(fig, animate_sensitivity, interval=FRAME_INTERVAL)
    plt.show()
    while True:
        pass

rows = 2
cols = 1
has_wf_plot = False
if (config.get_simulation_mode() == 'FULLY_INTRINSIC' and not config.is_pulse_func()) or config.get_simulation_mode() == 'FULLY_SIM':
    rows = rows + 1
    has_wf_plot = True

has_var_map_plot = False
has_pulse_map_plot = False
if config.get_selection_type() == 'MAP_ELITES':
    if config.get_fitness_func() == "PULSE_CONSISTENCY":
        has_pulse_map_plot = True
    else:
        has_var_map_plot = True

has_pop_plot = False
if config.get_init_mode() == 'EXISTING_POPULATION':
    rows = rows + 1
    has_pop_plot = True

fig = plt.figure(figsize=(9,7))
fig2 = plt.figure()

ax2 = fig.add_subplot(rows, cols, 1)
ax3 = ax2.twinx()
if has_wf_plot:
    ax4 = fig.add_subplot(rows, cols, 3)

if has_var_map_plot:
    fig_map = plt.figure()
    ax5 = fig_map.add_subplot(1, 1, 1)

if has_pulse_map_plot:
    fig_map = plt.figure()
    ax5 = fig_map.add_subplot(1, 1, 1)

ax1 = fig.add_subplot(rows, cols, 2)
ax1.set_xticks(range(1, config.get_population_size(), 1))

if has_pop_plot:
    # Put this plot in the last slot
    ax6 = fig.add_subplot(rows, cols, rows * cols)

ax7 = fig2.add_subplot(1, 1, 1)

if has_wf_plot:
    ani3 = animation.FuncAnimation(fig, animate_waveform, cache_frame_data=False)#, interval=200)

if has_var_map_plot:
    ani4 = animation.FuncAnimation(fig_map, animate_map, cache_frame_data=False)
elif has_pulse_map_plot:
    ani4 = animation.FuncAnimation(fig_map, animate_pulse_map, cache_frame_data=False)

ani = animation.FuncAnimation(fig, animate_generation, cache_frame_data=False)

if has_pop_plot:
    ani6 = animation.FuncAnimation(fig, animate_pops, interval=FRAME_INTERVAL, cache_frame_data=False)

ani7 = animation.FuncAnimation(fig2, anim_violin_plots, interval=FRAME_INTERVAL, cache_frame_data=False)

if config.get_simulation_mode() == 'FULLY_INTRINSIC':
    fig3 = plt.figure()
    ax8 = fig3.add_subplot(1,1,1)
    ani8 = animation.FuncAnimation(fig3, anim_heatmap, interval=FRAME_INTERVAL, cache_frame_data=False)

ani2 = animation.FuncAnimation(fig, animate_epoch, interval=FRAME_INTERVAL, cache_frame_data=False)

if config.is_pulse_count():
    fig4 = plt.figure()
    ax9 = fig4.add_subplot(2,1,1)
    anim9 = animation.FuncAnimation(fig4, animate_epoch_pulses, interval=FRAME_INTERVAL, cache_frame_data=False)

    ax10 = fig4.add_subplot(2,1,2)
    anim10 = animation.FuncAnimation(fig4, anim_violin_plots_pulse, interval=FRAME_INTERVAL, cache_frame_data=False)

plt.subplots_adjust(hspace=0.50)
fig.tight_layout(pad=5.0)
plt.show()