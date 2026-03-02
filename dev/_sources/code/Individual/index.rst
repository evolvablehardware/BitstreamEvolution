==========
Individual
==========

An Individual is the atomic unit of evolution — the genome that is mutated,
recombined, and selected across generations. The
:class:`~BitstreamEvolutionProtocols.Individual` protocol is intentionally
minimal (it specifies nothing beyond identity), allowing any genome
representation: boolean bitstreams, integers, trees, or arbitrary structures.

Individuals are held inside a :class:`~BitstreamEvolutionProtocols.Population`
and may be converted into one or more
:class:`~BitstreamEvolutionProtocols.Circuit` objects by a
:class:`~BitstreamEvolutionProtocols.CircuitFactory` for hardware evaluation.

Implementations
===============

- :doc:`BitstreamIndividual` — A genome represented as a list of boolean bits,
  with mutation (bit-flip) and crossover operators. Used by
  ``GenerateBitstreamPopulation`` for real FPGA experiments.

.. toctree::
    :maxdepth: 2
    :hidden:

    BitstreamIndividual.rst
