========
Hardware
========

The :class:`~BitstreamEvolutionProtocols.Hardware` protocol is the async
interface to physical FPGA devices. It compiles a Circuit, uploads it to an
FPGA, takes a measurement (waveform capture or pulse counting), and stores the
result on the :class:`~BitstreamEvolutionProtocols.Measurement` object.

The protocol is designed for future server-client concurrency: multiple FPGAs
can be driven in parallel via ``asyncio.gather()``, with per-device
serialization to respect the exclusive USB access required by ``iceprog``.

For details on the serial communication protocol, see
:doc:`/architecture/mcu_protocol`.

Implementations
===============

- :doc:`Microcontroller` — Serial-based implementation using pyserial to
  communicate with an MCU that bridges the host to an ICE40 FPGA. Supports
  waveform and pulse-count measurement modes.

.. toctree::
    :maxdepth: 2
    :hidden:

    Microcontroller.rst
