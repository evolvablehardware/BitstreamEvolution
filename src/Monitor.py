from tailer import head
from time import sleep
from configparser import ConfigParser

# currently not being used for anything.
# This process was originally luanched by Logger
# The Logger class logged a header and then 23 ".\n" to the file
# Now, the Logger also handles logging to a log file specified by the config, so I don't think this class is needed

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