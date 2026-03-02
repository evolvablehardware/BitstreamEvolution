=============
API Reference
=============

This section contains auto-generated documentation for every module in the
BitstreamEvolution codebase. The source of truth for the system's design is
:doc:`BitstreamEvolutionProtocols`, which defines the ``Protocol`` classes
(interfaces) that all concrete implementations satisfy.

Core Interfaces
===============

All major components are defined as Python ``Protocol`` classes so that
implementations can be swapped freely. The table below summarises each
interface and where to find its implementations.

.. list-table::
   :header-rows: 1
   :widths: 22 50 28

   * - Interface
     - Purpose
     - Implementations
   * - :class:`~BitstreamEvolutionProtocols.Individual`
     - The atomic unit of evolution — a genome that can be mutated and
       recombined. Specifies essentially nothing beyond identity, allowing
       any representation (bitstreams, integers, trees, etc.).
     - :doc:`Individual/index`
   * - :class:`~BitstreamEvolutionProtocols.Circuit`
     - An FPGA configuration compiled from one or more Individuals. Provides
       a ``compile()`` method that produces a binary bitstream for a target
       FPGA via the IceStorm toolchain.
     - :doc:`Circuit/index`
   * - :class:`~BitstreamEvolutionProtocols.Fitness`
     - A comparable result of evaluating a Circuit. Supports the standard
       comparison operators (``<``, ``>``, ``==``, ``<=``, ``>=``) so that
       most numeric types (``int``, ``float``) work out of the box.
     - Any comparable type
   * - :class:`~BitstreamEvolutionProtocols.Hardware`
     - Async interface to one or more physical FPGAs. Compiles a Circuit,
       uploads it, takes a measurement, and returns the result. Designed
       for future server-client concurrency across multiple devices.
     - :doc:`Hardware/index`
   * - :class:`~BitstreamEvolutionProtocols.CircuitFactory`
     - Converts a list of Populations into a mapping of Circuits to the
       Individuals that contribute to each one. Handles the one-to-one or
       many-to-one relationship between Individuals and Circuits.
     - See :doc:`TrivialImplementation`
   * - :class:`~BitstreamEvolutionProtocols.Reproducer`
     - Selection and mutation strategy. Takes a Population and returns a new
       Population of offspring for the next generation.
     - See :doc:`TrivialImplementation`
   * - :class:`~BitstreamEvolutionProtocols.GenerateInitialPopulation`
     - Factory that produces the initial Population before evolution begins.
     - :doc:`Population/index`
   * - :class:`~BitstreamEvolutionProtocols.EvaluatePopulationFitness`
     - Assigns fitness values to every Individual in a Population given a
       list of Measurements.
     - :doc:`EvaluateFitness/index`
   * - :class:`~BitstreamEvolutionProtocols.GenerateMeasurements`
     - Decides which Measurements to take for a set of Populations and
       returns them mapped to the Individuals they affect.
     - :doc:`GenerateMeasurements/index`
   * - :class:`~BitstreamEvolutionProtocols.GenDataFactory`
     - Manages generation metadata. Produces the initial ``GenData``,
       increments it each generation, and signals termination by returning
       ``None``.
     - ``GenDataIncrementer`` in :doc:`BitstreamEvolutionProtocols`

Supporting Types
================

- :class:`~BitstreamEvolutionProtocols.Population` — Holds a list of
  ``(Individual, Fitness | None)`` pairs with sorting and iteration support.
- :class:`~BitstreamEvolutionProtocols.Measurement` — Bundles a Circuit, a
  ``DataRequest`` type, sample count, and a ``Result`` that is filled after
  hardware evaluation.
- :class:`~BitstreamEvolutionProtocols.GenData` — Minimal generation metadata
  (currently just ``generation_number``).
- :class:`~BitstreamEvolutionProtocols.FPGA_Compilation_Data` — Target FPGA
  model and device ID, passed to ``Circuit.compile()``.
- :class:`~BitstreamEvolutionProtocols.DataRequest` — Enum selecting the
  measurement type (``WAVEFORM``, ``OSCILLATIONS``).

Orchestration
=============

- :doc:`Evolution` — The main loop that wires all of the above together:
  generates an initial population, then repeatedly evaluates fitness and
  reproduces until the ``GenDataFactory`` signals completion.
- :doc:`TrivialImplementation` — A self-contained reference implementation
  that exercises the full protocol stack using integer-valued circuits
  (no hardware required). Useful for testing and as a starting template.

Module Reference
================

.. toctree::
    :maxdepth: 2

    BitstreamEvolutionProtocols.rst
    Evolution.rst
    TrivialImplementation.rst
    Circuit/index.rst
    EvaluateFitness/index.rst
    GenerateMeasurements/index.rst
    Hardware/index.rst
    Individual/index.rst
    Population/index.rst
    Directories.rst
    Logger.rst
    PlotConfig.rst
    PlotDataRecorder.rst
    PlotEvolutionLive.rst
    utilities.rst


==========================
Documentation of Old Tools
==========================

.. toctree::
    tools/pulse_histogram
    tools/reconstruct
    tools/generate_configs
