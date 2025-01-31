"""
Monitor - NOT USED
------------------

Comments left describing previous use case:
- currently not being used for anything.
- This process was originally luanched by Logger
- The Logger class logged a header and then 23 ".\n" to the file
- Now, the Logger also handles logging to a log file specified by the config, so I don't think this class is needed

"""

# I am ignoring possible failures so sphinx can log file and because not expecting to use.
imports_work = True
try:
    from tailer import head
    from time import sleep
    from configparser import ConfigParser
except:
    imports_work = False



# currently not being used for anything.
# This process was originally luanched by Logger
# The Logger class logged a header and then 23 ".\n" to the file
# Now, the Logger also handles logging to a log file specified by the config, so I don't think this class is needed

def run():

    #Load from config
    config = ConfigParser()
    config.read("data/config.ini")
    MONITOR = str(config["LOGGING PARAMETERS"]["MONITOR_FILE"])

    """
    A high level monitor for a summary of the evolution experiment
    """
    while True:
        for line in head(open( MONITOR ), 22):
            print(line)
        sleep(.5)
        print('\033c')

if (__name__ == "__main__"):
    if imports_work:
        run()
    else:
        print("Tried to run, Imports failed, check if you have 'tailer' installed")