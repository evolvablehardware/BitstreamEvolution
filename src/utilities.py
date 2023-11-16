import os

def wipe_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))