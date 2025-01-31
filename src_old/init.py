#!/usr/bin/python3

"""
init.py
-------

This program is run to initialize the workspace directory.

This program is not used over the course of a standard evolution run.

This program has been reviewed, and should be adequately documented.
"""

from configparser import ConfigParser
from pathlib import Path
from shutil import copyfile
import os

def run():

	config = ConfigParser()
	config.read("data/default_config.ini")

	# Set the default log directories.
	root = Path.cwd()
	workspace = root.joinpath("workspace")
	if not workspace.exists():
		workspace.mkdir()

	# Make each of the default logging directory targets, if they don't
	# already exist and set the config options
	log_dir_types = ["asc", "bin", "data"]
	for log_dir_type in log_dir_types:
		temp_log_dir = workspace.joinpath(log_dir_type)
		log_dir = workspace.joinpath("experiment_" + log_dir_type)
		if not log_dir.exists():
			log_dir.mkdir()
		if not temp_log_dir.exists():
			temp_log_dir.mkdir()
		config.set("LOGGING PARAMETERS", log_dir_type + "_dir", str(log_dir))

	# Set some of the other default config options.
	config.set("LOGGING PARAMETERS", "monitor_file", str(root.joinpath("data/monitor")))
	analysis = workspace.joinpath("analysis")
	config.set("LOGGING PARAMETERS", "analysis", str(analysis))
	if not analysis.exists():
		analysis.mkdir()

	# Create the default config file and copy to the working config file.
	data = root.joinpath("data")
	with open(data.joinpath("default_config.ini"), "w+") as default_config_file:
		config.write(default_config_file)
		default_config_file.flush()
		copyfile(
			data.joinpath("default_config.ini"),
			data.joinpath("config.ini")
		)

	# Make sure that user has permissions for workspace and data folder if running via sudo
	USERNAME=os.getlogin()
	os.system(f"chown -R {USERNAME} data")
	os.system(f"chown -R {USERNAME} workspace")

if (__name__ == "__main__"):
	run()
