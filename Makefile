SHELL:=/bin/bash
.DEFAULT_GOAL:=all

LATTICE_FTDI_RULES='ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE="0660", GROUP="plugdev", TAG+="uaccess"'

.PHONY: all
all: init icestorm-tools udev-rules

.PHONY: clean
clean: clean-tools clean-workspace

.PHONY: clean-tools
clean-tools:
	rm -rf tools

.PHONY: clean-workspace
.ONESHELL:
clean-workspace:
	cd workspace
	rm -rf experiment_asc experiment_bin experiment_data analysis

.PHONY: init
init:
	python3 src/init.py

.PHONY: udev-rules
udev-rules:
	echo -e $(LATTICE_FTDI_RULES) > 53-lattice-ftdi.rules
	sudo mv 53-lattice-ftdi.rules /etc/udev/rules.d/

.PHONY: icestorm-tools
icestorm-tools: tools tools/icestorm tools/arachne-pnr tools/yosys

tools:
	mkdir tools

.PHONY: icestorm
icestorm: tools tools/icestorm

.PHONY: arachne-pnr
archne-pnr: tools tools/arachne-pnr

.PHONY: yosys
yosys: tools tools/yosys

.ONESHELL:
tools/icestorm: tools
	cd tools
	git clone https://github.com/cliffordwolf/icestorm.git icestorm
	cd icestorm
	make -j$(nproc)
	make install

.ONESHELL:
tools/arachne-pnr: tools
	cd tools
	git clone https://github.com/cseed/arachne-pnr.git arachne-pnr
	cd arachne-pnr
	make -j$(nproc)
	make install

.ONESHELL:
tools/yosys: tools
	cd tools
	git clone https://github.com/cliffordwolf/yosys.git yosys;\
	cd yosys
	git submodule update --init --recursive
	make -j$(nproc)
	make install
