import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import configparser
import re
from Config import Config

"""
Static parameters can be found and changed in the config.ini file in the root project folder
DO NOT CHANGE THEM HERE
"""
config_parser = configparser.ConfigParser()
config_parser.read("data/config.ini")
config = Config(config_parser)

style.use('dark_background')

fig = plt.figure()
ax1 = fig.add_subplot(2,1,2)
ax1.set_xticks(range(1, config.get_population_size(), 1))
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
            x, y = line.split(',')
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
    if config.get_using_pulse_function() and not config.get_simulation_mode() == "FULLY_INTRINSIC":
        ax1.set_yscale('symlog')
        ax1.set_ylim([0, 1000000])
    # ax1.plot.stem(xs,ys,  color="green", use_line_collection=True)
    ax1.scatter(xs, ys)
    # plt.stem(xs, ys, markerfmt="bo", linefmt="b-", use_line_collection=True)
    # plt.plot(xs, ys, color="blue")
    ax1.set(xlabel='Circuit Number', ylabel='Fitness', title='Circuit Fitness this Generation')

# fig2 = plt.figure()
ax2 = fig.add_subplot(2,1,1)
def animate_epoch(i):
    graph_data = open('workspace/bestlivedata.log','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    zs = []
    ws = []
    for line in lines:
        if len(line) > 1:
            x, y, z, w = line.split(',')
            xs.append(int(x))
            ys.append(float(y))
            zs.append(float(z))
            ws.append(float(w))
    ax2.clear()
    # ax2.set_yscale('symlog')
    ax2.plot(xs, ys, color="green")
    ax2.plot(xs, zs, color="red")
    ax2.plot(xs, ws, color="yellow")
    ax2.set(xlabel='Generation', ylabel='Fitness', title='Best Circuit Fitness per Generation')

#ax3 = fig.add_subplot(2,1,2)
def animate_waveform(i):    
    graph_data = open('workspace/waveformlivedata.log','r').read()
    lines = graph_data.split('\n')
    pulse_trigger = [400]*500
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(',')
            xs.append(int(x))
            ys.append(float(y))
    ax3.clear()
    ax3.set_ylim([0, 1000])
    ax3.plot(pulse_trigger, "r--")
    ax3.plot(xs, ys, color="blue")
    ax3.set(xlabel='Time (50 mS Total)', ylabel='Voltage (normalized)', title='Current Hardware Waveform')

ani2 = animation.FuncAnimation(fig, animate_epoch)
if not config.get_using_pulse_function():
    # fig3 = plt.figure()
    # ani3 = animation.FuncAnimation(fig, animate_waveform, interval=200)
    pass
ani = animation.FuncAnimation(fig, animate_generation)

plt.subplots_adjust(hspace=0.50)
plt.show()
