#This is a Makefile used to generate Sphinx Documentation
# commands need to be indented with a tab. 
# commands preceeded with an @ will only have their results printed when command is run (not the command run)
# ?= assigns the value only if it was not previously assigned.


# Set some variables first

SPHINX_SOURCEDIR        = sphinx/source

# You can set these variables from the command line, and also
# from the environment for the first two. 
SPHINX_WEBSITE_OPTS    ?=
SPHINX_WEBSITE_BUILD   ?= sphinx-build
WEBSITE_SOURCEDIR       = $(SPHINX_SOURCEDIR)
WEBSITE_BUILDDIR        = website



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
# Make directory on Linux system if not already exist, makes all subpaths, too.
# Build the Website to that directory

.PHONY: website
website:
	@echo "build website & create website directory"	
	@mkdir -p $(WEBSITE_BUILDDIR)
	$(SPHINX_WEBSITE_BUILD) -M html "$(WEBSITE_SOURCEDIR)" "$(WEBSITE_BUILDDIR)" $(SPHINX_WEBSITE_OPTS) $(O)

.PHONY: letter_pdf
letter_pdf:
	@echo "Create a .pdf document in the Letter Paper Size"

.PHONY: A4_pdf
A4_pdf:
	@echo "Create a .pdf document in the A4 Paper Size"

.PHONY: plain_text
plain_text:
	@echo "Create a plain_text document"

.PHONY: man
man:
	@echo "Create a man page"

# This holds all the documents that will be deleted when we call clean
.PHONY: clean
clean:
	rm -rf website

