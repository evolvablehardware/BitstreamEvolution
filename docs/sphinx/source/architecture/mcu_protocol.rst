MCU Serial Protocol
====================

.. note::

   This documentation was drafted from code analysis and may need verification
   against the MCU firmware.

Overview
--------

The host computer communicates with a microcontroller (MCU) over a serial link
to program an ICE40 FPGA and retrieve fitness-evaluation data. The MCU acts as
a bridge: the host sends a command byte indicating the type of measurement it
wants, and the MCU drives the FPGA and returns either a stream of ADC waveform
samples or a pulse count.

This protocol is implemented in :class:`Microcontroller`
(``src/Hardware/Microcontroller.py``) and conforms to the
:class:`Hardware` protocol defined in ``BitstreamEvolutionProtocols.py``.

Configuration
-------------

Connection parameters are bundled in the :class:`MicrocontrollerConfig`
dataclass:

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Field
     - Type
     - Description
   * - ``usb_path``
     - ``str``
     - Device path to the serial port (e.g. ``/dev/ttyUSB0``).
   * - ``serial_baud``
     - ``int``
     - Baud rate for the serial connection.
   * - ``read_timeout``
     - ``float``
     - Timeout in seconds for serial read operations.

Connection Setup
----------------

On construction, the ``Microcontroller`` class opens a persistent
``serial.Serial`` connection using the values from
``MicrocontrollerConfig``:

.. code-block:: python

   self.__serial = Serial(
       config.usb_path,
       config.serial_baud,
       timeout=config.read_timeout,
   )
   self.__serial.dtr = False

Setting **DTR low** is critical -- it prevents the MCU from resetting when the
serial port is opened, which is the default behaviour on many Arduino-compatible
boards.

DataRequest Types
-----------------

The type of measurement requested is encoded as a
:class:`DataRequest` enum (defined in ``BitstreamEvolutionProtocols.py``):

``DataRequest.WAVEFORM``
   Requests an ADC waveform capture. Dispatches to ``measure_signal()``.

``DataRequest.OSCILLATIONS``
   Requests one or more pulse-count readings. Dispatches to
   ``measure_pulses()``, which calls ``measure_pulses_once()`` repeatedly for
   the number of samples specified in the ``Measurement`` object.

Before either measurement type, the circuit is compiled for the FPGA via
``ckt.compile(fpga_data)`` using the IceStorm toolchain (``icepack`` /
``iceprog``).

Waveform Measurement Protocol
------------------------------

**Serial command:** ``b'2'``

.. note::

   This documentation was drafted from code analysis and may need verification
   against the MCU firmware. The exact sample count, sample rate, and ADC
   resolution should be confirmed with the firmware source.

Sequence:

1. The host flushes both input and output serial buffers.
2. The host sends ``b'2'`` to initiate ADC capture.
3. The host polls ``read_until()`` for the ``START\n`` delimiter, re-sending
   ``b'2'`` on each iteration until it arrives or the read timeout is exceeded.
4. After ``START\n``, the host reads lines one at a time. Each line contains a
   single integer ADC sample (samples are approximately 10 microseconds apart).
   Approximately 500 samples are expected.
5. The stream ends when the host receives ``FINISHED\n``.
6. If ``read_timeout`` is exceeded at any stage, reading is aborted and
   whatever samples have been collected so far are returned.

.. code-block:: text

   Host  --> MCU:  b'2'
   MCU   --> Host: START\n
   MCU   --> Host: <sample_0>\n
   MCU   --> Host: <sample_1>\n
   ...
   MCU   --> Host: <sample_N>\n
   MCU   --> Host: FINISHED\n

**Return value:** ``list[int]`` -- the parsed integer ADC samples, excluding
the ``START`` and ``FINISHED`` sentinel lines.

Pulse Count Measurement Protocol
----------------------------------

**Serial command:** ``b'1'``

.. note::

   This documentation was drafted from code analysis and may need verification
   against the MCU firmware. The pulse-counting window duration and any
   firmware-side filtering should be confirmed with the firmware source.

Sequence:

1. The host flushes both input and output serial buffers.
2. The host sends ``b'1'`` to initiate pulse counting.
3. The host calls ``read_until()`` in a loop, looking for a line that:

   - Is not empty (``b""``),
   - Does not contain ``:``, ``START``, ``FINISH``, or a space.

   This filtering is intended to skip MCU debug or status lines and isolate the
   numeric pulse count.

4. When a valid line is found, carriage-return and newline bytes are stripped
   and the result is parsed as an integer.

**Retry logic:** If the read timeout is exceeded, the host retries up to
**5 attempts** before giving up.

**Sentinel / error values:**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Value
     - Meaning
   * - ``-1``
     - Read timed out after exhausting all retry attempts.
   * - ``-1000``
     - The buffer was empty after the read loop completed (should never occur
       under normal conditions).
   * - ``-2``
     - The received bytes could not be parsed as an integer
       (``ValueError`` during ``int()`` conversion).

**Multi-sample collection:** ``measure_pulses(samples)`` calls
``measure_pulses_once()`` the requested number of times and concatenates the
results into a single ``list[int]``.

.. code-block:: text

   Host  --> MCU:  b'1'
   MCU   --> Host: <pulse_count>\n

Error Handling
--------------

The ``request_measurement()`` method wraps each measurement call in a
``try`` / ``except`` block. Results are stored on the ``Measurement`` object
using the ``returns`` library:

- **Success path:** ``measurement.result = Success(data)``
- **Failure path:** ``measurement.result = Failure(exception)``

Before any measurement is taken, the ``Measurement`` object is initialized with
``Failure(MeasurementNotTaken(...))`` so that unconsumed measurements are never
mistaken for successful reads.

Known Issues / TODOs
--------------------

The following issues are noted directly in the source code:

1. **Serial read/write optimization needed** -- The waveform reading loop
   (``measure_signal``) contains a ``# TODO`` comment indicating that the
   section reading samples between ``START`` and ``FINISHED`` could be
   optimized, likely by reading all available bytes at once rather than
   line-by-line.

2. **Poor regex / filtering in pulse count parsing** -- The pulse-count reader
   (``measure_pulses_once``) uses a chain of byte-string containment checks
   (``b":" not in p and b"START" not in p ...``) rather than a proper regular
   expression or structured parser. A ``# TODO`` in the source notes this
   "is currently doing a poor job at REGEXing the MCU serial return" and
   suggests it should handle transmission-loss artefacts (dropped or extra
   spaces, shifted colons, etc.) more robustly.

3. **Missing measurement type dispatch** -- ``request_measurement()`` contains
   a ``# TODO`` comment for additional ``elif`` branches to handle future
   ``DataRequest`` types beyond ``WAVEFORM`` and ``OSCILLATIONS``.
