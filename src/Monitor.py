from tailer import head
from time import sleep
from configparser import ConfigParser

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