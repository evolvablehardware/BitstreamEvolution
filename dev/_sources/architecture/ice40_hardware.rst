ICE40 HX1K Hardware Model
=========================

.. note::

   This documentation was drafted from code analysis and may need verification
   against hardware datasheets.

This page documents how the BitstreamEvolution framework models and interacts
with the Lattice ICE40 HX1K FPGA. The primary implementation lives in
:py:class:`FileBasedCircuit` (see :file:`src/Circuit/FileBasedCircuit.py`),
which reads, mutates, compiles, and uploads bitstream configurations to physical
hardware through the IceStorm open-source toolchain.

ICE40 HX1K Overview
--------------------

The ICE40 HX1K is a low-power FPGA from the Lattice iCE40 family. It contains
1,280 logic cells arranged in a tile grid. The BitstreamEvolution project uses
this FPGA as the target for evolved digital circuits: genetic algorithm
individuals are represented as bitstream configurations that are uploaded to the
device and evaluated for fitness based on the resulting circuit behavior (e.g.,
oscillation counting or waveform analysis).

The IceStorm reverse-engineered toolchain provides full open-source support for
the ICE40 family, including an ASCII bitstream representation (``.asc`` files)
that the framework manipulates directly.

ASC File Format
----------------

The IceStorm ``.asc`` (ASCII) format is a human-readable representation of the
FPGA's configuration bitstream. ``FileBasedCircuit`` operates on these files
using memory-mapped I/O.

Tile Headers
^^^^^^^^^^^^

Each logic tile in the file is introduced by a header line of the form::

   .logic_tile X Y

where ``X`` and ``Y`` are the integer coordinates of the tile on the FPGA grid.
The framework locates tiles by scanning for the byte string ``b".logic_tile"``
and parsing the coordinates that follow.

Bit Rows
^^^^^^^^

After each ``.logic_tile`` header, subsequent lines contain rows of
space-delimited ``0`` and ``1`` characters representing the configuration bits
for that tile. Because the file is accessed through a memory-mapped buffer, bit
values are encountered as their ASCII byte codes:

.. list-table::
   :header-rows: 1

   * - Character
     - ASCII Code (byte value)
     - Logical Value
   * - ``'0'``
     - 48
     - ``False``
   * - ``'1'``
     - 49
     - ``True``

The ``get_bitstream`` and ``set_bitstream`` methods in ``FileBasedCircuit``
convert between these ASCII byte values and Python ``bool`` lists.

File Attributes (Metadata)
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``.asc`` format supports comment lines, which the framework repurposes for
metadata storage. A special comment line stores name-value pairs:

.. code-block:: text

   .comment FILE_ATTRIBUTES fitness={42.5} generation={100}

Attributes are encoded as ``name={value}`` pairs on a single ``.comment
FILE_ATTRIBUTES`` line. The ``get_file_attribute`` and ``set_file_attribute``
methods on ``FileBasedCircuit`` provide read/write access to these attributes.
If the comment line does not yet exist, ``set_file_attribute`` prepends one to
the file.

Tile Grid Structure
--------------------

.. note::

   This documentation was drafted from code analysis and may need verification
   against hardware datasheets. The tile coordinate ranges below are
   hard-coded in ``FileBasedCircuit.__tile_is_included`` and are specific to
   the ICE40 HX1K. A different iCE40 model (e.g., HX8K) would require
   different ranges.

Only a subset of the full tile grid is available for evolutionary modification.
The valid tile coordinates are defined as:

.. code-block:: python

   VALID_TILE_X = range(4, 10)   # X in {4, 5, 6, 7, 8, 9}
   VALID_TILE_Y = range(1, 17)   # Y in {1, 2, ..., 16}

Tiles outside these ranges are skipped during mutation and bitstream
extraction. The ``__tile_is_included`` method parses the ``X Y`` coordinates
from the ``.asc`` header following each ``.logic_tile`` tag and checks
membership in these ranges.

The method handles multi-digit coordinate values by locating the space between
``X`` and ``Y`` and the newline at the end of the header, then decoding the
byte slices as UTF-8 strings before converting to integers.

Routing Types
--------------

.. note::

   This documentation was drafted from code analysis and may need verification
   against hardware datasheets. The row selections below are noted in the
   source as "dated" and may not reflect the latest routing protocol.

Within each valid tile, only specific rows and columns of configuration bits are
subject to evolutionary modification. The set of modifiable rows is determined
by the **routing type**, configured per circuit at construction time.

MOORE
^^^^^

When ``routing_type == "MOORE"``, the modifiable rows within each tile are:

.. code-block:: python

   rows = [1, 2, 13]

This routing type exposes three rows for mutation, including row 13 which
provides access to additional routing resources.

NEWSE
^^^^^

When ``routing_type == "NEWSE"``, the modifiable rows are:

.. code-block:: python

   rows = [1, 2]

This is a more restricted routing type, limiting modification to only the first
two rows of each tile.

Accessed Columns
^^^^^^^^^^^^^^^^

In addition to the routing-type-determined rows, the specific columns available
for modification are supplied via the ``accessed_columns`` parameter at circuit
construction time. The framework iterates over every combination of modifiable
row and accessed column to reach individual bits:

.. code-block:: python

   pos = line_start + line_size * (row - 1) + int(col)

where ``line_start`` is the byte offset of the first data line in the tile, and
``line_size`` is the width of each line (including the trailing newline).

Compilation Flow
-----------------

The path from an evolved ``.asc`` file to a running FPGA configuration follows
these steps:

.. code-block:: text

   .asc file  -->  icepack  -->  .bin file  -->  iceprog  -->  FPGA

1. **Flush mmap** -- Before compilation, the memory-mapped file is flushed to
   ensure all in-memory mutations are written to disk:

   .. code-block:: python

      self._hardware_file.flush()

2. **icepack** -- The IceStorm ``icepack`` utility converts the ASCII ``.asc``
   file into a binary ``.bin`` bitstream:

   .. code-block:: python

      COMPILE_CMD = "icepack"
      run([COMPILE_CMD, self.__hardware_filepath, self.__bitstream_filepath])

3. **iceprog** -- The ``iceprog`` utility uploads the compiled ``.bin`` file to
   the target FPGA over USB. The ``-d`` flag selects a specific device when
   multiple FPGAs are connected:

   .. code-block:: python

      RUN_CMD = "iceprog"
      run([RUN_CMD, self.__bitstream_filepath, "-d", fpga.id])

4. **Settling delay** -- A one-second ``sleep(1)`` follows upload to allow the
   FPGA to initialize before fitness evaluation begins.

Memory-Mapped I/O
-------------------

``FileBasedCircuit`` uses Python's :py:mod:`mmap` module to memory-map the
``.asc`` hardware file. This avoids repeated file open/read/write/close cycles
during the many small, random-access mutations that occur across an
evolutionary run.

The memory-mapped file is created during ``__init__``:

.. code-block:: python

   hardware_file = open(self.__hardware_filepath, "r+")
   self._hardware_file = mmap(hardware_file.fileno(), 0)
   hardware_file.close()

Key considerations:

- **Read/write access** -- The file is opened in ``"r+"`` mode so the mmap
  supports both reading bit values and writing mutations back in place.
- **Flushing before compile** -- ``self._hardware_file.flush()`` is called
  before ``icepack`` runs to ensure the on-disk file reflects all pending
  changes.
- **Windows compatibility** -- The ``copy_from`` method closes the mmap before
  overwriting the underlying file with ``shutil.copyfile``, then re-opens and
  re-maps it. This is required because Windows locks files that have active
  memory mappings.
- **Byte-level access** -- Individual bits are accessed by index
  (``hardware_file[pos]``), returning integer byte values (48 or 49) that
  correspond to ASCII ``'0'`` and ``'1'``.
