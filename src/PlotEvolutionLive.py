"""
Plot Evolution Live
===================

This program is spawned by a bash script to run parallel to our main program when performing an evolution.
Plots of the active evolution are created and updated in this script using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib import colormaps # type: ignore
import configparser
import re
import math 
import numpy as np
import sys
from PlotConfig import PlotConfig
from utilities import determine_color
from os.path import exists
from os import mkdir
import argparse

"""
Static parameters can be found and changed in the config.ini file in the root project folder
DO NOT CHANGE THEM HERE
"""

MAX_VIOLIN_PLOTS = 11
HEATMAP_BINS = 40

config = PlotConfig('./workspace/plot_config.ini')

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-f", "--frame-interval", required=False, default=10000)
args = arg_parser.parse_args()
FRAME_INTERVAL = int(args.frame_interval)

def run():
    """Temporary function to run all of Plot Evolution Live."""
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
        ax1.set_xlim([0, config.get_population_size()+1]) # type: ignore
        # ax1.set_xticks(range(1, config.get_population_size(), 1))
        ax1.hlines(y=avg, xmin=0, xmax=config.get_population_size()+1, color="violet", linestyles="dotted")
        ax1.scatter(xs, ys, color=((accent_color2 + "dd") if is_transparent else (accent_color2 + "ff") ))
        if config.is_pulse_count():
            title = 'Circuit Pulses this Generation'
            ylabel = 'Pulses'
            # Add a line for desired frequency
            if config.is_pulse_count():
                ax1.hlines(y=config.get_desired_frequency(), xmin=1, xmax=config.get_population_size(), color="red", linestyles="dotted")
            ax1.set_ylim([0, None]) # type: ignore
        else:
            title = 'Circuit Fitness this Generation'
            ylabel = 'Fitness'
        ax1.set(xlabel='Circuit Number', ylabel=ylabel, title=title)

        if formal:
            ax1.legend(['Average Fitness', 'Individual Fitness', 'Target Fitness'],\
                    bbox_to_anchor=(1.05, 0.5), loc="center left", borderaxespad=0)

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
                ax2.axvline(x=i, color=accent_color, linestyle="dashed")

        plots = []
        labels = []
        # Plot the overall best before the gen best so the gen best line appears on top
        plots += ax2.plot(xs, ts, color="#00b87d") # Ovr best Fitness
        labels.append("Overall Best")
        plots += ax2.plot(xs, ys, color="green") # Generation/Epoch Best Fitness
        plots += ax2.plot(xs, zs, color="red") # Generation Worst Fitness
        plots += ax2.plot(xs, ws, color=yellow) # Generation Average Fitness
        labels.append("Best")
        labels.append("Worst")
        labels.append("Average")
        ax2.tick_params(axis='y', labelcolor=accent_color)

        if config.get_diversity_measure() != "NONE":
            ax3.clear()
            plots += ax3.plot(xs, ds, color="#5a70ed") # Generation diversity measure
            ax3.tick_params(axis='y', labelcolor='#5a70ed')
            ax3.set_ylabel('Diversity', color='#5a70ed')
            ax3.set_ylim(bottom=0)
            ax3.yaxis.set_label_position("right")
        
        ax2.set(xlabel='Generation', ylabel='Fitness', title='Circuit Fitness per Generation')

        if formal:
            ax2.legend(plots, labels, bbox_to_anchor=(1.15, 0.5), loc="center left", borderaxespad=0)

        if(config.get_save_plots()):
            fig.savefig(str(plots_dir.joinpath("1_main.png")), bbox_inches="tight")

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

        plots = []
        labels = ['Minimum', 'Maximum', 'Average', 'Best', 'Desired Frequency']
        plots += ax9.plot(ts, zs, color="cornflowerblue", linewidth=0.75)
        plots += ax9.plot(ts, ws, color="coral", linewidth=0.75)
        plots += ax9.plot(ts, ys, color=yellow, linewidth=0.75)
        plots += ax9.plot(ts, xs, color="lime")
        ax9.tick_params(axis='y', labelcolor=accent_color)

        if config.is_pulse_count():
            ax9.hlines(y=config.get_desired_frequency(), xmin=1, xmax=len(lines), color="violet", linestyles="dotted")
            # labels.append("Desired Frequency")
        ax9.set(xlabel='Generation', ylabel='Pulses', title='Circuit Pulse Count per Generation')

        if config.using_transfer_interval():
            for i in range(0,len(lines),config.get_transfer_interval()):
                ax9.axvline(x=i, color=accent_color, linestyle="dashed")

        if formal:
            ax9.legend(plots, labels, bbox_to_anchor=(1.15, 0.5), loc="center left", borderaxespad=0)

        if(config.get_save_plots()):
            fig4.savefig(str(plots_dir.joinpath("2_pulses.png")), bbox_inches="tight")


    def animate_waveform(i):    
        graph_data = open('workspace/waveformlivedata.log','r').read()
        lines = graph_data.split('\n')
        pulse_trigger = [341*3.3/715]*500
        xs = []
        ys = []
        for line in lines:
            if len(line) > 1:
                x, y = line.split(',')
                xs.append(int(x))
                ys.append(float(y) * 3.3/715)
        ax4.clear()
        if config.is_tone_discriminator():
            ax4.set_xlim([0, 1000]) # type: ignore
        else:
            ax4.set_xlim([0, 500]) # type: ignore
        #ax4.set_ylim([0, 750])
        ax4.set_ylim([-0.2, 3.5]) # type: ignore
        ax4.plot(pulse_trigger, "r--")
        ax4.plot(xs, ys, color="blue")

        if formal:
            ax4.legend(['Trigger Voltage', 'Circuit Voltage'], bbox_to_anchor=(1.15, 0.5), loc="lower center", borderaxespad=0)

        ax4.set(xlabel='Time (μs)', ylabel='Voltage (V)', title='Current Hardware Waveform')

    def animate_state(i):    
        graph_data = open('workspace/statelivedata.log','r').read()
        lines = graph_data.split('\n')
        pulse_trigger = [341*3.3/715]*500
        xs = []
        ys = []
        for line in lines:
            if len(line) > 1:
                x, y = line.split(',')
                xs.append(int(x))
                ys.append(float(y))
        ax5.clear()
        ax5.set_xlim([0, 1000]) # type: ignore
        #ax4.set_ylim([0, 750])
        ax5.set_ylim([-0.1, 1.1]) # type: ignore
        ax5.plot(pulse_trigger, "r--")
        ax5.plot(xs, ys, color="blue")

        if formal:
            ax5.legend(['Trigger Voltage', 'Circuit Voltage'], bbox_to_anchor=(1.15, 0.5), loc="lower center", borderaxespad=0)

        ax5.set(xlabel='Time (μs)', ylabel='Voltage (V)', title='Current State')

    # def animate_map(i):
    #     graph_data = open('workspace/maplivedata.log','r').read()
    #     lines = graph_data.split('\n')
    #     xs = []
    #     ys = []
    #     fits = []
    #     if len(lines) > 0 and len(lines[0]) > 0:
    #         scale_factor = int(lines[0])
    #         lines.pop(0) # Remove scale factor from the lines set

    #         for line in lines:
    #             vals = line.split(' ')
    #             if (len(vals) > 2 and len(vals[2]) > 0):
    #                 row = int(vals[0])
    #                 col = int(vals[1])
    #                 fit = float(vals[2])
    #                 fits.append(fit)
    #                 xs.append((col + 0.5) * scale_factor)
    #                 ys.append((row + 0.5) * scale_factor)

    #     ax5.clear()

    #     # Add a line to the middle that separates possible from impossible cells
    #     ax5.plot([0, 750], [0, 750], color='#444444', linewidth=0.5)

    #     scatterplot = ax5.scatter(xs, ys, c=fits, s=50, cmap='winter')
    #     plt.colorbar(scatterplot)

    #     ax5.set_xlim(0, 750)
    #     ax5.set_ylim(0, 750)
    #     ax5.set_aspect('equal')
    #     #ax5.set_xticks(np.arange(0, 1024, 50), minor=True)
    #     #ax5.set_yticks(np.arange(0, 1024, 50), minor=True)
    #     #ax5.grid(color = '#363636', which = 'minor')
    #     ax5.set(xlabel='Max Voltage (norm)', ylabel='Min Voltage (norm)', title='Elite Map')

    #     if(config.get_save_plots()):
    #         fig_map.savefig(str(plots_dir.joinpath("5_map.png")), bbox_inches="tight")

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
            ax6.legend( bbox_to_anchor=(1.15, 0.5), loc="center left", borderaxespad=0)
            ax6.set(xlabel='Generation', ylabel='Number from Population', title='Circuits from Each Source Population')

    def anim_violin_plots(i):
        data = open('workspace/violinlivedata.log','r').read()
        collections = []
        gens = []
        widths = []
        lines = data.split('\n')
        # Decide which generations to include based on the number to have and the number available
        interval = len(lines) / (MAX_VIOLIN_PLOTS - 1)
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

        # Make sure that we always include the final generation
        # File always ends with a blank line, so go 2 lines back
        line = lines[len(lines)-2]
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
                    ax7.axvline(x=i, color=accent_color, linestyle="dashed")
            ax7.violinplot(collections, positions=gens, widths=widths)
            ax7.set(xlabel='Generation', ylabel='Fitness', title='Fitness Violin Plots')

        if(config.get_save_plots()):
            fig2.savefig(str(plots_dir.joinpath("3_violin_plots.png")))

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
                    ax10.axvline(x=i, color=accent_color, linestyle="dashed")
            if config.is_pulse_count():
                ax10.hlines(y=config.get_desired_frequency(), xmin=1, xmax=len(lines), color="violet", linestyles="dotted")  
            ax10.set(xlabel='Generation', ylabel='Pulses', title='Pulse Violin Plots')
            ax10.set(xlabel='Generation', ylabel='Pulses')

    def anim_heatmap(i):
        global max_pulses
        if config.is_pulse_count():
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
                    if config.is_pulse_count():
                        collections.append(float(pt))
                    else:
                        collections.append(float(pt)*3.3/715)
                
        ax8.clear()                         
        ax8.hist2d(gens,collections,bins=HEATMAP_BINS)

        if config.is_pulse_count():
            ax8.set(xlabel='Generation', ylabel='Pulses', title='Pulse Count Histogram')
        else:
            ax8.set(xlabel='Generation', ylabel='Voltage (V)', title='Voltage Heatmap')

        if config.using_transfer_interval():
                for i in range(0,len(lines),config.get_transfer_interval()):
                    ax8.axvline(x=i, color=accent_color, linestyle="dashed")

        if(config.get_save_plots()):
            fig3.savefig(str(plots_dir.joinpath("4_heatmap.png")))

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

    # def plot(fig, function):
    #     if formal:
    #         return function(0)
    #     else:
    #         return animation.FuncAnimation(fig, function, interval=FRAME_INTERVAL, cache_frame_data=False)


    plots_dir = config.get_plots_directory()

    formal = False
    if len(sys.argv) > 1 and sys.argv[1] == 'formal':
        formal = True 
        plots_dir = plots_dir.joinpath("Formal")
        accent_color = "black"
        accent_color2 = "#65187A"
        heatmap_color = 'Blues'
        yellow = "goldenrod"
        plot = lambda fig, function : function(0)
    else:
        style.use('dark_background')
        accent_color = "white"
        accent_color2 = "#f0f8ff"
        heatmap_color = 'viridis'
        yellow = "yellow"
        plot = lambda fig, function : animation.FuncAnimation(fig, function, interval=FRAME_INTERVAL, cache_frame_data=False)

    
    if not exists(plots_dir):
        mkdir(plots_dir)

    fig = plt.figure(figsize=(9,7))
    rows = 2
    cols = 1
    has_wf_plot = False
    has_st_plot = False
    if not config.is_pulse_count():
        rows = rows + 1
        has_wf_plot = True

    if config.is_tone_discriminator():
        rows = rows + 1
        has_st_plot = True

    has_pop_plot = False
    if config.uses_init_existing_population():
        rows = rows + 1
        has_pop_plot = True

    ax1 = fig.add_subplot(rows, cols, 2)
    ani = plot(fig, animate_generation)
    ax2 = fig.add_subplot(rows, cols, 1)
    ax3 = ax2.twinx()
    ani2 = plot(fig, animate_epoch)

    if has_wf_plot:
        ax4 = fig.add_subplot(rows, cols, 3)
        ani3 = plot(fig, animate_waveform)
    
    if has_st_plot:
        ax5 = fig.add_subplot(rows, cols, 4)
        ani4 = plot(fig, animate_state)

    if has_pop_plot:
        ax6 = fig.add_subplot(rows, cols, rows * cols)
        ani6 = plot(fig, animate_pops)

    fig2 = plt.figure()
    ax7 = fig2.add_subplot(1, 1, 1)
    ani7 = plot(fig2, anim_violin_plots)

    fig3 = plt.figure()
    ax8 = fig3.add_subplot(1,1,1)
    ani8 = plot(fig3, anim_heatmap)

    if config.is_pulse_count():
        fig4 = plt.figure()
        ax9 = fig4.add_subplot(2,1,1)
        ani9 = plot(fig4, animate_epoch_pulses)
        ax10 = fig4.add_subplot(2,1,2)
        ani10 = plot(fig4, anim_violin_plots_pulse)

    # if config.get_selection_type() == 'MAP_ELITES':
    #     fig_map = plt.figure()
    #     ax5 = fig_map.add_subplot(1, 1, 1)
    #     if config.get_fitness_func() == "PULSE_CONSISTENCY":
    #         ani4 = plot(fig_map, animate_pulse_map)
    #     else:
    #         ani4 = plot(fig_map, animate_map)

    plt.subplots_adjust(hspace=0.50)
    fig.tight_layout(pad=5.0)
    plt.show(block=(not formal))
    #plt.show(block=True)

# only run if this is the main method.
if (__name__ == "__main__"):
    run()