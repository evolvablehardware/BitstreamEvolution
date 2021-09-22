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
