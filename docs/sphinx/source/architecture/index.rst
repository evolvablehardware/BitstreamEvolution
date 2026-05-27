==================================
Bitstream Evolution's Architecture
==================================

.. toctree::
   :maxdepth: 2
   :hidden:

   historical/index
   hardware/index

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

.. mermaid::

   flowchart TD
       A([Run Evolution]) --> B["Generate Initial Population"]
       B -->|"Population + Gen. Info"| C["Evolution Generation Info Incrementer"]
       C -->|"None returned"| X([Exit])
       C -->|"Population + New Gen. Info"| D["Generate Measurements"]
       D -->|"Gen. Info + List Of Measurements"| E["Evaluate Measurements"]
       E -->|"Gen. Info + List Of Measurements"| F["Evaluate Fitnesses"]
       D -->|"Population"| F
       F -->|"Gen. Info + Population w/ fitness"| G["Reproduce"]
       G -->|"Gen. Info + New Population"| C


Initial Proposal
================

The current architecture is based almost entirely on the initial proposal. The archived
proposal is a useful reference for the overall design intent, but it is a snapshot —
any changes or refinements made during implementation are **not** reflected there.
Those differences will be documented here on this page instead.

.. button-ref:: historical/initial_proposal
   :ref-type: doc
   :color: primary
   :shadow:

