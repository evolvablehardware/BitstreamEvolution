import os
import math

def wipe_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

def determine_color(ratio, colors):
    if ratio == 1:
        return colors[len(colors) - 1]
    
    color_index = math.floor(len(colors) * ratio)
    c1 = colors[color_index]
    c2 = colors[color_index + 1]
    r = (c2[0] - c1[0]) * ratio + c1[0]
    g = (c2[1] - c1[1]) * ratio + c1[1]
    b = (c2[2] - c1[2]) * ratio + c1[2]
    return [r, g, b, 1]