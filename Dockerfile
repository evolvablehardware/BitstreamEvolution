# Base {{{
FROM ubuntu:latest AS base

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive \
  apt-get install -y --no-install-recommends \
  ca-certificates \
  clang \
  curl \
  libffi-dev \
  libftdi-dev \
  libreadline-dev \
  tcl-dev \
  graphviz \
  xdot \
  git \
  pkg-config
# }}}

# Arduino-cli {{{
FROM base AS arduino
WORKDIR /

RUN apt-get update -qq && apt-get install -y --no-install-recommends wget
RUN wget https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz
RUN apt-get autoclean && apt-get clean && apt-get -y autoremove \
  && rm -rf /var/lib/apt/lists
RUN tar -xf arduino-cli_latest_Linux_64bit.tar.gz -z
RUN rm arduino-cli_latest_Linux_64bit.tar.gz
# }}}

# Dependencies {{{
FROM base AS dependencies
WORKDIR /tools

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive \
  apt-get install -y --no-install-recommends \
    bison \
    flex \
    gawk \
    gcc \
    g++ \
  && apt-get autoclean && apt-get clean && apt-get -y autoremove \
  && rm -rf /var/lib/apt/lists

RUN git clone https://github.com/cliffordwolf/icestorm.git /tools/icestorm
RUN git clone https://github.com/cseed/arachne-pnr.git /tools/arachne-pnr
RUN git clone https://github.com/YosysHQ/yosys.git /tools/yosys
RUN cd /tools/icestorm && make -j $(nproc) && make install
RUN cd /tools/arachne-pnr && make -j $(nproc)
RUN cd /tools/yosys && make -j $(nproc)
# # }}}
