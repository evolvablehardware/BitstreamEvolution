from shutil import copytree, rmtree
from datetime import date
import os

from Config import Config

class WorkspaceFormatter:
    def __init__(self, config: Config, experiment_explanation):
        self.__config = config
        self.__exp_explnation = experiment_explanation

    def __create_folder(self):
        #get folder name
        today = date.today()
        folder_name = "FPGA_" + str(today.strftime("%m_%d_%Y"))

        # copy the contents of workspace to the new folder
        try:
            copytree("workspace", folder_name, dirs_exist_ok=True)
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

        if(not self.__config.get_using_configurable_io()):
            try:
                rmtree(folder_name + "/template")
            except OSError as error:
                pass
        
        if(self.__config.get_init_mode() != "EXISTING_POPULATION"):
            try:
                rmtree(folder_name + "/source_populations")
            except OSError as error:
                pass

        return folder_name
    
    def __gen_readme(self, folder_name):
        #create readme and add experiment explanation
        readme = open(folder_name + "/README.md", "w")
        readme.write(self.__exp_explnation)
        readme.write("  \n");
        readme.write("-----\n");

        #add plots to the readme
        for filename in sorted(os.listdir(folder_name+"/plots")):
            path = folder_name + "/plots/" + filename
            if path.endswith(".png") and os.stat(path).st_size != 0:
                readme.write("![" + filename + "](plots/" + filename + ")\n")
        readme.write("-----\n");

        #add config
        source = open(folder_name + "/builtconfig.ini", "r").read()
        lines = source.split('\n')
        for line in lines:
            if line.startswith("["):
                readme.write("#### ")
                readme.write(line)
                readme.write("  \n")
                readme.write("| Param | Value |  \n")
                readme.write("|---|---|  \n")
            elif " = " in line:
                parts = line.split(" = ")
                readme.write(parts[0])
                readme.write(" | ")
                readme.write(parts[1])
                readme.write("  \n")

        readme.close()

    def format_workspace(self):
        folder_name = self.__create_folder()
        self.__gen_readme(folder_name)
