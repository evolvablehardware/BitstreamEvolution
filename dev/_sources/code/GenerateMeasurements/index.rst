=====================
Generate Measurements
=====================

Before fitness can be evaluated, the system must decide *which* measurements to
take and map them back to the Individuals whose fitness they affect.

The :class:`~BitstreamEvolutionProtocols.GenerateMeasurements` protocol defines
this step: given a :class:`~BitstreamEvolutionProtocols.CircuitFactory` and a
list of Populations, it returns a dictionary mapping each new
:class:`~BitstreamEvolutionProtocols.Measurement` to the ``(Population,
Individual)`` pairs it will inform.

Implementations
===============

- :doc:`GenerateMeasurements` — Standard implementation that uses the
  CircuitFactory to build Circuits, then creates one Measurement per Circuit.

.. toctree::
    :maxdepth: 2
    :hidden:

    GenerateMeasurements.rst
