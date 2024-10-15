"""
Pulse Histogram
===============

This program that takes an experiment, looks at all pulse counts, and generates a histogram.
This was used to see the number of time-outs vs. number of 0s vs. number of times close to target. 

This program is ment purely to assist with analysis or finding and explaining errors.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider


def run():

    print('Starting up...')

    f = open('./workspace/pulselivedata.log', 'r')
    lines = f.readlines()
    f.close()

    # Keep a track of each generation's pulse counts, and the overall ones
    gens = [] # Contains an entry list for each generation
    overall = [] # Contains numbers, where each number is a single pulse count recorded measure

    for line in lines:
        _, counts_str = line.split(':')
        counts = [int(x) for x in counts_str.split(',')]
        gens.append(counts)
        overall = overall + counts

    # Data is all loaded
    print('Data loaded')

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.5)

    ax_gen = fig.add_axes([0.2, 0.2, 0.7, 0.13])
    ax_button = fig.add_axes([0.3, 0.1, 0.4, 0.05])
    gen_slider = Slider(ax=ax_gen, label='Generation', valmin=1, valmax=len(gens), valinit=1, valstep=1)
    toggle_button = Button(ax=ax_button, label='Show Overall')

    width = 5000

    gen = 0
    def update(new_gen):
        gen = new_gen - 1
        data = gens[gen]
        rerender(data)

    def rerender(data):
        ax.clear()
        bins = np.arange(-width, max(data) + width, width)
        ax.hist(data, bins)

    def button_click(event):
        rerender(overall)

    gen_slider.on_changed(update)
    toggle_button.on_clicked(button_click)

    #bins = np.arange(-width, max(gens[0]) + width, width)
    #ax.hist(gens[0], bins)
    #plt.axvline(x = 50000, color='r')

    rerender(gens[0])

    plt.show()

if (__name__ == "__main__"):
    run()