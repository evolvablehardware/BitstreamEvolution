==================================
Bitstream Evolution's Architecture
==================================

The original code was designed in a vaguely class-like structure to prove the
concept, but once proven it became very challenging to change the code and
coordinate those changes, even in a small group. Thus, we created the following
general architecture to make the code more modular and easy to edit and use for
a broader range of applications.

Overview
========

BitstreamEvolution uses a **protocol-based architecture**: every major component
is defined as a Python ``Protocol`` class in
:doc:`/code/BitstreamEvolutionProtocols`, so that implementations can be swapped
without changing the orchestration code. The main loop
(:doc:`/code/Evolution`) wires these components together.

The data flow through a single generation looks like this:

1. A :class:`~BitstreamEvolutionProtocols.GenDataFactory` produces or
   increments the generation metadata and decides when to stop.
2. A :class:`~BitstreamEvolutionProtocols.CircuitFactory` converts the
   :class:`~BitstreamEvolutionProtocols.Population` of
   :class:`~BitstreamEvolutionProtocols.Individual` objects into
   :class:`~BitstreamEvolutionProtocols.Circuit` objects ready for hardware.
3. A :class:`~BitstreamEvolutionProtocols.GenerateMeasurements` strategy
   creates :class:`~BitstreamEvolutionProtocols.Measurement` objects — one per
   Circuit — describing what to measure.
4. The :class:`~BitstreamEvolutionProtocols.Hardware` interface compiles each
   Circuit (``icepack`` / ``iceprog``), uploads it to an FPGA, and fills the
   Measurement with raw data (waveform samples or pulse counts).
5. An :class:`~BitstreamEvolutionProtocols.EvaluatePopulationFitness` evaluator
   interprets the raw measurements and assigns
   :class:`~BitstreamEvolutionProtocols.Fitness` values to each Individual.
6. A :class:`~BitstreamEvolutionProtocols.Reproducer` performs selection and
   mutation to produce the next generation's Population.

For a working end-to-end example that exercises this entire pipeline with
integer-valued circuits (no hardware required), see
:doc:`/code/TrivialImplementation`.

General Structure
=================

Below is the best current description of our architecture. It is currently
pretty in-line with the initial proposal.

.. image:: images/initial_proposal/Arch_Proposal-7.png


Initial Proposal
================

Below are a series of slides from the initial proposal for the architecture.
These are non-final, but were going in the right direction.

To see this as the original presentation, `look here <https://docs.google.com/presentation/d/1QkHsh1EmpQeNTC4FLra8Vry-5Ln28tJxNxoWPVK5R3A/edit?usp=sharing>`_.

I then attempted to implement a basic example of it in the
:doc:`/code/TrivialImplementation` file.

Architecture Description
------------------------

.. image:: images/initial_proposal/Arch_Proposal-1.png

.. image:: images/initial_proposal/Arch_Proposal-2.png

.. image:: images/initial_proposal/Arch_Proposal-3.png

.. image:: images/initial_proposal/Arch_Proposal-4.png

.. image:: images/initial_proposal/Arch_Proposal-5.png

.. image:: images/initial_proposal/Arch_Proposal-6.png

.. image:: images/initial_proposal/Arch_Proposal-7.png

.. image:: images/initial_proposal/Arch_Proposal-8.png

.. image:: images/initial_proposal/Arch_Proposal-9.png

.. image:: images/initial_proposal/Arch_Proposal-10.png

.. image:: images/initial_proposal/Arch_Proposal-11.png

.. image:: images/initial_proposal/Arch_Proposal-12.png

.. image:: images/initial_proposal/Arch_Proposal-13.png

Architectural Example
---------------------

.. image:: images/initial_proposal/example/Arch_Example-1.png

.. image:: images/initial_proposal/example/Arch_Example-2.png

.. image:: images/initial_proposal/example/Arch_Example-3.png

.. image:: images/initial_proposal/example/Arch_Example-4.png

.. image:: images/initial_proposal/example/Arch_Example-5.png

.. image:: images/initial_proposal/example/Arch_Example-6.png

.. image:: images/initial_proposal/example/Arch_Example-7.png

.. image:: images/initial_proposal/example/Arch_Example-8.png

.. image:: images/initial_proposal/example/Arch_Example-9.png

.. image:: images/initial_proposal/example/Arch_Example-10.png

.. image:: images/initial_proposal/example/Arch_Example-11.png

.. image:: images/initial_proposal/example/Arch_Example-12.png


Hardware Documentation
======================

.. toctree::
    :maxdepth: 1

    ice40_hardware
    mcu_protocol

Early Design Ideas
==================

Below is one of the early attempts at conceptualizing an architecture for this
project:

.. image:: images/EarlyDesignIdea.png
