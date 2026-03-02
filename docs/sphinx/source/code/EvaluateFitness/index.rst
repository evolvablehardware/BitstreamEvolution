================
Evaluate Fitness
================

Fitness evaluators take a list of :class:`~BitstreamEvolutionProtocols.Measurement`
objects (already filled with raw hardware data) and assign
:class:`~BitstreamEvolutionProtocols.Fitness` values to every Individual in a
Population. Different evaluation strategies interpret the same raw data in
different ways.

The :class:`~BitstreamEvolutionProtocols.EvaluatePopulationFitness` protocol
defines the interface: ``__call__(population, measurements) -> None``, editing
the Population's fitness values in place.

Implementations
===============

- :doc:`EvaluateFitness` — Generic wrapper that delegates to a per-measurement
  fitness function.
- :doc:`EvalPulseCountFitness` — Computes fitness from the number of
  oscillation pulses measured on the FPGA output.
- :doc:`EvalVarMaxFitness` — Computes fitness from the variance and maximum
  amplitude of a captured waveform.

.. toctree::
    :maxdepth: 2
    :hidden:

    EvaluateFitness.rst
    EvalPulseCountFitness.rst
    EvalVarMaxFitness.rst
