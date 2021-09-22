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
