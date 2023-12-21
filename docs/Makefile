#This is a Makefile used to generate Sphinx Documentation
# commands need to be indented with a tab. 
# commands preceeded with an @ will only have their results printed when command is run


# Set some variables first

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build



# help set as first target so it is run by default
.PHONY: help
help:
        @echo "Please use \`make <target>' where <target> is one of"
        @echo "  clean      to remove build files"
        @echo "  all        to create all possible types of documentation"
        @echo "  website    to make the default website in the main website folder"

# This runs all possible builds
.PHONY: all
all: website

# This runs whenever we with to build the website
.PHONY website
website:
	@echo"build website & create website directory"


# This holds all the documents that will be deleted when we call clean
.PHONY: clean
clean:
rm -rf website
