from shutil import copytree, rmtree, copy
from datetime import date
import os

#get folder name
today = date.today()
folder_name = "FPGA_" + str(today.strftime("%m_%d_%Y"))

# copy the contents of workspace to the new folder
try:
    copytree("workspace", folder_name)
except OSError as error:
    print(error) 

#go through and remove files of 0 bytes
for filename in os.listdir(folder_name):
    path = folder_name + "/" + filename
    if path.endswith(".log") and os.stat(path).st_size == 0:
        os.remove(path)

#remove directories we don't want included
try:
    rmtree(folder_name + "/experiment_bin")
except OSError as error:
    pass

try:
    rmtree(folder_name + "/experiment_data")
except OSError as error:
    pass

#create readme and add config to it
readme = open(folder_name + "/README.md", "w")
source = open(folder_name + "/builtconfig.ini", "r").read()
lines = source.split('\n')
for line in lines:
    if line.startswith("["):
        readme.write("#### ")
    readme.write(line)
    readme.write("  \n")


readme.write("-----\n");

#add plots to the config
for filename in os.listdir(folder_name+"/plots"):
    path = folder_name + "/plots/" + filename
    if path.endswith(".png") and os.stat(path).st_size != 0:
        readme.write("![" + filename + "](plots/" + filename + ")\n")
readme.close()