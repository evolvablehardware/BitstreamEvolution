=======
Circuit
=======

A Circuit represents an FPGA configuration that can be compiled and uploaded to
physical hardware. The :class:`~BitstreamEvolutionProtocols.Circuit` protocol
requires a single method, ``compile(fpga)``, which converts the circuit's
internal representation into a binary bitstream for a target FPGA.

Circuits may or may not be the same object as an Individual — they are identical
when the Individual directly represents a full circuit, but separate when
multiple Individuals are combined to form a single circuit for evaluation.

Implementations
===============

- :doc:`Circuit` — Abstract base providing shared constants (tile coordinates,
  routing types, column definitions) for ICE40-based circuits.
- :doc:`FileBasedCircuit` — The primary implementation: operates on IceStorm
  ``.asc`` files via memory-mapped I/O, supporting mutation, compilation
  (``icepack``), and upload (``iceprog``).
- :doc:`FullySimCircuit` — A simulated circuit for testing without physical
  hardware.

.. toctree::
    :maxdepth: 2
    :hidden:

    Circuit.rst
    FileBasedCircuit.rst
    FullySimCircuit.rst
