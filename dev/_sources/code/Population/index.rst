==========
Population
==========

A :class:`~BitstreamEvolutionProtocols.Population` holds a collection of
``(Individual, Fitness | None)`` pairs. It supports fitness assignment (by index
or by Individual reference), sorting by fitness, and iteration. All Individuals
in a Population must be unique objects.

Populations are created by a
:class:`~BitstreamEvolutionProtocols.GenerateInitialPopulation` factory at the
start of evolution, and by a :class:`~BitstreamEvolutionProtocols.Reproducer`
at the end of each generation.

Implementations
===============

- :doc:`PopulationInitialization` — Factories for creating initial populations,
  including ``GenerateBitstreamPopulation`` which produces populations of
  :class:`~Individual.BitstreamIndividual.BitstreamIndividual` with random or
  seeded bitstreams.

.. toctree::
    :maxdepth: 2
    :hidden:

    PopulationInitialization.rst
