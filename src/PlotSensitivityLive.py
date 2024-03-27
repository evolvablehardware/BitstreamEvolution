"""
Plot Sensivity Live
===================

This program is spawned by a bash script to run parallel to our main program when performing a sensitvity experiment.
Plots of the active experiment are created and updated in this script using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from Config import Config
import numpy as np
import sys
from os.path import exists
from os import mkdir

"""
Static parameters can be found and changed in the config.ini file in the root project folder
DO NOT CHANGE THEM HERE
"""

HEATMAP_BINS = 40 
FRAME_INTERVAL = 10000

config = Config("workspace/builtconfig.ini")

def run():
    def get_data():
        graph_data = open('workspace/fitnesssensitivity.log','r').read()
        lines = graph_data.split('\n')
        xs = []
        ys = []
        ts = []
        cs = []
        hs = []
        for line in lines:
            if len(line) > 1:
                x,d = line.split(':')
                d = d.split(",")
                ts.append(float(x))
                xs.append(float(d[0]))
                ys.append(float(d[1]))
                cs.append(float(d[2]))
                hs.append(float(d[3]))
        return ts, xs, ys, cs, hs

    def animate_sensitivity(i):
        xs = []
        ys = []
        ts = []
        cs = []
        hs = []
        ts, xs, ys, cs, hs = get_data()

        #fitness
        ax2.clear()
        ax2.hist(xs, bins=HEATMAP_BINS)
        ax2.tick_params(axis='y', labelcolor=accent_color)
        ax2.set_ylim(bottom=0)

        ax3.clear()
        ax3.hist2d(ts,xs,bins=HEATMAP_BINS, cmap=heatmap_color)
        ax3.tick_params(axis='y', labelcolor=accent_color)
        ax3.set_ylim(bottom=0)
        
        #pulses/mean voltage
        ax4.clear()
        ax4.hist(ys, bins=HEATMAP_BINS)
        ax4.tick_params(axis='y', labelcolor=accent_color) 

        ax5.clear()
        ax5.hist2d(ts, ys, bins=HEATMAP_BINS, cmap=heatmap_color)
        ax5.tick_params(axis='y', labelcolor=accent_color) 
        
        ax2.set(xlabel='Fitness', ylabel='Count', title='Circuit Fitness per Trial')
        ax3.set(xlabel='Trial', ylabel='Fitness', title='Circuit Fitness per Trial')
        if not config.is_pulse_func():
            ax4.set(xlabel='Mean Voltage (Normalized)', ylabel='Count', title='Circuit Voltage per Trial')
            ax5.set(xlabel='Trial', ylabel='Mean Voltage (Normalized)', title='Circuit Voltage per Trial')
        else:
            ax4.set(xlabel='Pulses', ylabel='Count', title='Pulses')
            ax5.set(xlabel='Trial', ylabel='Pulses', title='Pulses')

        if(config.get_save_plots()):
            fig.savefig(plots_dir.joinpath("1_sensitivity.png"))

    def animate_temp_humidity(i):
        xs = []
        ys = []
        ts = []
        cs = []
        hs = []
        ts, xs, ys, cs, hs = get_data()


        if len(ts) == 0:
            return

        temp_bins = max(1, min(int(HEATMAP_BINS/2), int(10*(max(cs)-min(cs)))))
        humidity_bins = max(1, min(int(HEATMAP_BINS/2), int(10*(max(hs)-min(hs)))))

        #fitness
        ax6.clear()
        ax6.hist2d(cs,xs, bins=temp_bins, cmap=heatmap_color)
        ax6.tick_params(axis='y', labelcolor=accent_color)
        ax6.set(xlabel='Temperature', ylabel='Fitness', title='Temperature vs Circuit Fitness')

        ax7.clear()
        ax7.hist2d(hs,xs,bins=humidity_bins,cmap=heatmap_color)
        ax7.tick_params(axis='y', labelcolor=accent_color)
        ax7.set(xlabel='Humidity', ylabel='Fitness', title='Humidity vs Circuit Fitness')
        
        #pulses/mean voltage
        ax8.clear()
        ax8.hist2d(cs, ys, bins=temp_bins,cmap=heatmap_color)
        ax8.tick_params(axis='y', labelcolor=accent_color) 

        ax9.clear()
        ax9.hist2d(hs, ys, bins=humidity_bins, cmap=heatmap_color)
        ax9.tick_params(axis='y', labelcolor=accent_color) 
        
        if config.is_pulse_func():
            ax8.set(xlabel='Temperature', ylabel='Pulses', title='Temperature vs Pulses')
            ax9.set(xlabel='Humidity', ylabel='Pulses', title='Humidity vs Pulses')
        else:
            ax8.set(xlabel='Temperature', ylabel='Mean Voltage (Normalized)', title='Temperature vs Circuit Voltage per Trial')
            ax9.set(xlabel='Humidity', ylabel='Mean Voltage (Normalized)', title='Humidity vs Circuit Voltage per Trial')

        if(config.get_save_plots()):
            fig2.savefig(plots_dir.joinpath("2_sensitivity_temp_humidity.png"))

    def animate_avg_temp_humidity(i):
        xs = []
        ys = []
        ts = []
        cs = []
        hs = []
        ts, xs, ys, cs, hs = get_data()
        
        if len(ts) == 0:
            return

        min_t = min(cs)
        max_t = max(cs)
        temp_fitness = []
        temp_data2= []
        temp_xs = []
        # set up bins
        for i in range(int(10*(max_t-min_t)) + 1):
            temp_fitness.append([])
            temp_data2.append([])
            temp_xs.append(i/10 + min_t)
        #sort temp data into bins
        for i in range(len(cs)):
           index = int(10*(cs[i] - min_t))
           temp_fitness[index].append(xs[i])
           temp_data2[index].append(ys[i])
        #find empty slices
        i = 0
        while i < len(temp_xs):
            if(len(temp_fitness[i]) == 0):
                temp_xs.pop(i)
                temp_fitness.pop(i)
                temp_data2.pop(i)
                i -= 1
            i += 1
        #calc averages and variance
        avg_temp_fitness = []
        avg_temp_data2 = []
        std_temp_fitness = []
        std_temp_data2 = []
        for i in range(len(temp_xs)):
            avg_temp_fitness.append(np.average(temp_fitness[i]))
            avg_temp_data2.append(np.average(temp_data2[i]))
            std_temp_fitness.append(np.std(temp_fitness[i]))
            std_temp_data2.append(np.std(temp_data2[i]))

        ax10.clear() 
        ax10.plot(temp_xs, avg_temp_fitness, color=accent_color)
        ax10.set(xlabel='Temperature', ylabel='Average Fitness', title='Temperature vs Average Circuit Fitness')
        ax12.clear() 
        ax12.plot(temp_xs, avg_temp_data2, color=accent_color)

        ax14.clear() 
        ax14.plot(temp_xs, std_temp_fitness, color=accent_color)
        ax14.set(xlabel='Temperature', ylabel='Standard Deviation of Fitness', title='Temperature vs Standard Deviation of Circuit Fitness')
        ax16.clear() 
        ax16.plot(temp_xs, std_temp_data2, color=accent_color)

        min_h = min(hs)
        max_h = max(hs)
        humidity_fitness = []
        humidity_data2= []
        humidity_xs = []
        #set up bins
        for i in range(int(10*(max_h-min_h)) + 1):
            humidity_fitness.append([])
            humidity_data2.append([])
            humidity_xs.append(i/10 + min_h)
        #sort humidity data into bins
        for i in range(len(hs)):
           index = int(10*(hs[i] - min_h))
           humidity_fitness[index].append(xs[i])
           humidity_data2[index].append(ys[i])
        #find empty slices
        i = 0
        while i < len(humidity_xs):
            if(len(humidity_fitness[i]) == 0):
                humidity_xs.pop(i)
                humidity_fitness.pop(i)
                humidity_data2.pop(i)
                i -= 1
            i += 1
        #calc averages and variance
        avg_humidity_fitness = []
        avg_humidity_data2 = []
        std_humidity_fitness = []
        std_humidity_data2 = []
        for i in range(len(humidity_xs)):
            avg_humidity_fitness.append(np.average(humidity_fitness[i]))
            avg_humidity_data2.append(np.average(humidity_data2[i]))
            std_humidity_fitness.append(np.std(humidity_fitness[i]))
            std_humidity_data2.append(np.std(humidity_data2[i]))

        ax11.clear() 
        ax11.plot(humidity_xs, avg_humidity_fitness, color=accent_color)
        ax11.set(xlabel='Humidity', ylabel='Average Fitness', title='Humidity vs Average Circuit Fitness')
        ax13.clear() 
        ax13.plot(humidity_xs, avg_humidity_data2, color=accent_color)

        ax15.clear() 
        ax15.plot(humidity_xs, std_humidity_fitness, color=accent_color)
        ax15.set(xlabel='Humidity', ylabel='Standard Deviation of Fitness', title='Humidity vs Standard Deviation of Circuit Fitness')
        ax17.clear() 
        ax17.plot(humidity_xs, std_humidity_data2, color=accent_color)

        if config.is_pulse_func():
            ax12.set(xlabel='Temperature', ylabel='Average Pulses', title='Temperature vs Average Pulses')
            ax13.set(xlabel='Humidity', ylabel='Average Pulses', title='Humidity vs Average Pulses')
            ax16.set(xlabel='Temperature', ylabel='Standard Deviation of Pulses', title='Temperature vs Standard Deviation of Pulses')
            ax17.set(xlabel='Humidity', ylabel='Standard Deviation of Pulses', title='Humidity vs Standard Deviation of Pulses')
        else:
            ax12.set(xlabel='Temperature', ylabel='Average of Mean Voltages (Normalized)', title='Temperature vs Average Circuit Voltage per Trial')
            ax13.set(xlabel='Humidity', ylabel='Average of Mean Voltages (Normalized)', title='Humidity vs AVerage Circuit Voltage per Trial')
            ax16.set(xlabel='Temperature', ylabel='Standard Deviation of of Mean Voltages (Normalized)', title='Temperature vs Standard Deviation of Average Circuit Voltage per Trial')
            ax17.set(xlabel='Humidity', ylabel='Standard Deviation of of Mean Voltages (Normalized)', title='Humidity vs Standard Deviation of Average Circuit Voltage per Trial')

        if(config.get_save_plots()):
            fig3.savefig(plots_dir.joinpath("3_sensitivity_avg_temp_humidity.png"))
            fig4.savefig(plots_dir.joinpath("4_sensitivity_std_temp_humidity.png"))

    def animate_change_over_time(i):
        xs = []
        ys = []
        ts = []
        cs = []
        hs = []
        ts, xs, ys, cs, hs = get_data()
        if len(ts) == 0:
            return
        
        data = []
        for i in range(8):
            data.append([])

        bufs = []
        for i in range(4):
            bufs.append([])

        buf_length = min(len(ts), int(len(ts)/100))
        time_points = []
        j = 0
        for i in range(len(ts)):
            bufs[0].append(xs[i])
            bufs[1].append(ys[i])
            bufs[2].append(cs[i])
            bufs[3].append(hs[i])

            j = (j+1) % buf_length
            if j == 0:
                for k in range(4):
                    data[k].append(np.average(bufs[k]))
                    data[k+4].append(np.std(bufs[k]))

                bufs = []
                for k in range(4):
                    bufs.append([])
                time_points.append(ts[i])


        for i in range(12):
            time_axes[i].clear()

        time_axes[0].plot(time_points, data[0], color=accent_color)
        time_axes[0].set(xlabel="Trial", ylabel="Fitness")
        time_axes[3].plot(time_points, data[1], color=accent_color)
        time_axes[3].set(xlabel="Trial", ylabel="Data 2")
        time_axes[6].plot(time_points, data[4], color=accent_color)
        time_axes[6].set(xlabel="Trial", ylabel="Standard Deviation of Fitness")
        time_axes[9].plot(time_points, data[5], color=accent_color)
        time_axes[9].set(xlabel="Trial", ylabel="Standard Deviation of Data 2")

        for i in range(4):
            time_axes[3*i + 1].plot(time_points, data[2], color='tab:red')
            time_axes[3*i + 1].set(ylabel="Temperature")
            time_axes[3*i + 2].plot(time_points, data[3], color='tab:cyan')
            time_axes[3*i + 2].set(ylabel="Humidity")


        if(config.get_save_plots()):
            fig5.savefig(plots_dir.joinpath("5_change_over_time.png"))

    plots_dir = config.get_plots_directory()

    formal = False
    if len(sys.argv) > 1 and sys.argv[1] == 'formal':
        formal = True 
        plots_dir = plots_dir.joinpath("Formal")
        accent_color = "black"
        heatmap_color = 'Blues'
        plot = lambda fig, function : function(0)
    else:
        style.use('dark_background')
        accent_color = "white"
        heatmap_color = 'viridis'
        plot = lambda fig, function : animation.FuncAnimation(fig, function, interval=FRAME_INTERVAL, cache_frame_data=False)

    if not exists(plots_dir):
        mkdir(plots_dir)

    fig = plt.figure(figsize=(9,7))
    ax2 = fig.add_subplot(2, 2, 1)
    ax3 = fig.add_subplot(2, 2, 2)
    ax4 = fig.add_subplot(2, 2, 3)
    ax5 = fig.add_subplot(2, 2, 4)
    ani = animation.FuncAnimation(fig, animate_sensitivity, interval=FRAME_INTERVAL)
    fig.tight_layout(pad=5.0)

    if(config.reading_temp_humidity()):
        fig2 = plt.figure(figsize=(9,7))
        ax6 = fig2.add_subplot(2, 2, 1)
        ax7 = fig2.add_subplot(2, 2, 2)
        ax8 = fig2.add_subplot(2, 2, 3)
        ax9 = fig2.add_subplot(2, 2, 4)
        ani3 = animation.FuncAnimation(fig2, animate_temp_humidity, interval=FRAME_INTERVAL)
        fig2.tight_layout(pad=5.0)

        fig3 = plt.figure(figsize=(9,7))
        ax10 = fig3.add_subplot(2, 2, 1)
        ax11 = fig3.add_subplot(2, 2, 2)
        ax12 = fig3.add_subplot(2, 2, 3)
        ax13 = fig3.add_subplot(2, 2, 4)

        fig4 = plt.figure(figsize=(9,7))
        ax14 = fig4.add_subplot(2, 2, 1)
        ax15 = fig4.add_subplot(2, 2, 2)
        ax16 = fig4.add_subplot(2, 2, 3)
        ax17 = fig4.add_subplot(2, 2, 4)

        ani4= animation.FuncAnimation(fig3, animate_avg_temp_humidity, interval=FRAME_INTERVAL)
        fig3.tight_layout(pad=5.0)
        fig4.tight_layout(pad=5.0)

        fig5 = plt.figure(figsize=(9,7))
        time_axes = []
        for i in range(4):
            ax_a = fig5.add_subplot(2, 2, i+1)
            time_axes.append(ax_a)
            for j in range(2):
                time_axes.append(ax_a.twinx())
        
        ani5= animation.FuncAnimation(fig5, animate_change_over_time, interval=FRAME_INTERVAL)
        fig5.tight_layout(pad=5.0)



    plt.subplots_adjust(hspace=0.50)
    plt.show(block=(not formal))
    if formal:
        exit()

# only run if this is the main method.
if (__name__ == "__main__"):
    run()