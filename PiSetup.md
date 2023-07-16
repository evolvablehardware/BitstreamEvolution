# Setup Instructions for Raspberry Pi
Pi tested on: CanaKit Raspberry Pi 4, 8GB RAM
### Equipment Used
- Raspberry Pi 4
- MicoSD card and MicroSD reader
    - I think there’s a way to boot with an USB instead, and this might help the Pi run faster
- Pi Power supply
- Monitor, microHDMI cable, keyboard, and mouse for initial set up
- Ethernet cable or wireless adaptor for non-wireless Pis

---

### Install Ubuntu on the Pi
Guide used: https://ubuntu.com/tutorials/how-to-install-ubuntu-desktop-on-raspberry-pi-4#1-overview

### Enable ssh on the Pi
Guide used: https://linuxize.com/post/how-to-enable-ssh-on-ubuntu-20-04/

### Install tmux
tmux is a terminal multiplexer that allows processes to continue running after a remote connection has been closed. As some of the steps in setting up took me hours to run, this is useful to have early on. More information on tmux [here](https://github.com/tmux/tmux/wiki).
```bash
sudo apt install tmux
```
To use tmux, start by running `tmux new` to create a new session. Then start the process inside the session. Once that is running, `Ctrl-b d` will detach the session and continue to run it in the background, even if the remote connection is closed. To reattach to a session, run `tmux attach`

### Dependencies - same as normal setup
```bash
sudo apt update && sudo apt upgrade  # Optional, but recommended 
sudo apt install build-essential clang bison flex libreadline-dev gawk tcl-dev libffi-dev \
libftdi-dev mercurial graphviz xdot pkg-config python3 python3-pip libboost-all-dev cmake make
```

### Other dependencies needed
Pip didn’t work on my setup for the python packages so I found this workaround.
```bash
sudo apt install git python3-serial python3-numpy python3-matplotlib python3-sortedcontainers
```

### Remove brltty to use microcontrollers
```bash
sudo apt remove brltty
```

### Configuring the BitstreamEvolution core - same as normal 
This did crash my Pi the first time I ran it, but worked once I powercycled and reran it. \
`sudo make` in the root directory of BitstreamEvolution

### Set up Arduino CLI
The first two commands are different from normal setup since Pis use ARM
```bash
wget https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_ARM64.tar.gz
tar -xf arduino-cli_latest_Linux_ARM64.tar.gz -z
./arduino-cli update
./arduino-cli upgrade
./arduino-cli core download arduino:avr
./arduino-cli core install arduino:avr
```

### Compile and upload - same as normal
I used `sudo dmesg | tail` to figure out the arduino’s device file. I had to add myself to the plugdev and dialout groups before I could upload to the arduino.
```bash
sudo usermod -a -G dialout USERNAME
sudo usermod -a -G plugdev USERNAME
./arduino-cli compile -b arduino:avr:nano [PATH TO PROJECT i.e. ~/BitstreamEvolution/data/ReadSignal/ReadSignal.ino]
./arduino-cli upload -b arduino:avr:nano -p /dev/ttyUSB# PATH/TO/SKETCH
```

### Running 
```bash
python3 src/evolve.py
```
I couldn’t get graphics to work on the ssh client. The best solution I have so far is downloading the workspace folder and the config file to a copy of the repo I have on my local machine. From there, I could run the plotting tool. The plots kept freezing, so this isn’t an ideal solution.
