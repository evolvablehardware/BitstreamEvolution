Hardware Architecture
=====================


This section covers hardware-specific implementation details: which hardware was chosen, why it
was chosen, and low-level specifics of how the hardware interface is implemented. It is **not**
the right place to look to understand how the overall evolution system operates. For that, see
the :doc:`main architecture page </architecture/index>`.

The pages here are reference material for anyone working directly with the physical hardware
layer — for example, modifying the serial communication protocol, adding support for new FPGA
hardware, or understanding device-level constraints that influenced design decisions.

.. toctree::
   :maxdepth: 1

   ice40_hardware.rst
   mcu_protocol.rst
