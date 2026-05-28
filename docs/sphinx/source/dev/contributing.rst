============
Contributing
============

This guide covers how to set up a development environment, make changes, and
submit them for review.

Getting Started
===============

1. **Fork** the repository on GitHub:
   https://github.com/evolvablehardware/BitstreamEvolution

2. **Clone** your fork locally:

   .. code-block:: bash

       git clone https://github.com/<your-username>/BitstreamEvolution.git
       cd BitstreamEvolution

3. **Create a feature branch** from ``develop``:

   .. code-block:: bash

       git checkout develop
       git checkout -b my-feature-branch

   All new work should branch from ``develop``, not ``main``.

Setting Up the Development Environment
=======================================

Install all development dependencies (documentation, testing, linting) with
Poetry:

.. code-block:: bash

    poetry install --with dev

This gives you access to ``pytest``, ``mypy``, ``Sphinx``, and all related tools.

Running Tests
=============

Tests are grouped into three timing categories using pytest markers:
(Timing categories are determined for the entire category.)

.. list-table::
    :header-rows: 1
    :widths: 15 15 70

    * - Marker
      - Max duration
      - When to run
    * - ``immediate``
      - < 10 seconds
      - Default. Applied automatically to any unmarked test. Run these before every commit.
    * - ``short``
      - < 60 seconds
      - Run these before opening a pull request.
    * - ``long``
      - > 1 minute
      - Typically run only in CI. Include hardware-in-the-loop or full evolution runs.

**Typical local workflow:**

.. code-block:: bash

    # Fast smoke-check while developing (default — runs all unmarked tests)
    poetry run pytest

    # Before opening a PR: run everything that finishes under a minute
    poetry run pytest -m "immediate or short"

    # Full suite including slow tests (CI runs this automatically)
    poetry run pytest -m "immediate or short or long"

**Useful flags:**

.. code-block:: bash

    # Verbose output — shows each test name and pass/fail
    poetry run pytest -v

    # Run only tests in a specific file
    poetry run pytest test/test_BitstreamEvolutionProtocols.py

    # Run tests whose name matches a pattern
    poetry run pytest -k "Population"

    # List all available markers and their descriptions
    poetry run pytest --markers

    # Stop after the first failure
    poetry run pytest -x

Writing Tests
=============

All committed code should be accompanied by tests. Tests live in the ``test/``
directory and follow the same module structure as ``src/``.

**Timing markers** — annotate every test with the appropriate marker so the CI
matrix can split fast and slow tests efficiently:

.. code-block:: python

    @pytest.mark.short
    def test_something_that_takes_a_few_seconds():
        ...

    # Unmarked tests automatically receive the `immediate` marker via conftest.py

**Mocking protocol implementations** — use ``unittest.mock.Mock(spec=...)``
when you need a stand-in for a protocol class. The ``spec`` argument ensures
the mock only exposes attributes that exist on the real protocol, catching
accidental use of non-existent methods at test time:

.. code-block:: python

    from unittest.mock import Mock
    from BitstreamEvolutionProtocols import Hardware

    hw = Mock(spec=Hardware)
    hw.get_available_FPGAs.return_value = ["FPGA1"]

**Contract tests** — if you are adding a new implementation of an existing
protocol, check ``test/contracts/`` for a contract test base class for that
protocol. Subclass it and provide a fixture for your implementation so the
shared contract tests run against it automatically.

.. todo::

    Expand this section with detailed test-writing guidance: fixture patterns,
    when to use ``tmp_path`` vs ``monkeypatch``, how to handle hardware-dependent
    tests, and worked examples for each protocol.

Type Checking
=============

Run mypy to catch type errors before committing:

.. code-block:: bash

    poetry run mypy src/

Commit Message Guidelines
=========================

- Use the imperative mood in the subject line (e.g., *"Add pulse count evaluator"*,
  not *"Added pulse count evaluator"*)
- Keep the subject line under 72 characters
- Add a blank line and a more detailed body when the change needs explanation

Example::

    Add variance-based fitness evaluator

    Implement EvalVarMaxFitness that computes fitness from the variance
    and maximum amplitude of waveform measurements.

Creating a Pull Request
=======================

1. **Push** your feature branch to your fork:

   .. code-block:: bash

       git push origin my-feature-branch

2. **Open a Pull Request** on GitHub targeting the ``develop`` branch
   (not ``main``).

3. In your PR description, explain:

   - What the change does
   - Why it is needed
   - How to test it

4. CI will run the full test suite across multiple Python versions automatically.
   All checks must pass before the PR can be merged.

Code Style and Conventions
==========================

- **Docstrings**: Use `NumPy-style <https://numpydoc.readthedocs.io/en/latest/format.html>`_
  docstrings for all public classes and functions.

- **Architecture**: The codebase uses Python ``Protocol`` classes to define
  interfaces. Read :doc:`/code/BitstreamEvolutionProtocols` before adding new
  abstractions.

- **Error handling**: Use the `returns <https://returns.readthedocs.io/>`_ library
  (``Success`` / ``Failure``) for operations that can fail, rather than raising
  exceptions. This is the same pattern as Rust's ``Result<T, E>`` type — callers
  are forced to handle both outcomes explicitly rather than relying on exceptions
  for control flow.

- **Testing**: Write tests using pytest. Place them in ``test/`` alongside existing
  tests for the same module. Use ``unittest.mock.Mock(spec=ProtocolClass)`` to
  mock protocol implementations.

Questions?
==========

Open an issue on the
`GitHub repository <https://github.com/evolvablehardware/BitstreamEvolution/issues>`_
if you have questions, find bugs, or want to discuss a feature idea.
