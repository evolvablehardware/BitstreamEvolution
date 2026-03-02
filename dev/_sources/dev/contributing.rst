============
Contributing
============

Thank you for your interest in contributing to BitstreamEvolution! This guide
covers how to set up a development environment, make changes, and submit them
for review.

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

This gives you access to pytest, mypy, Sphinx, and all related tools.

Running Tests
=============

Before committing, make sure the test suite passes:

.. code-block:: bash

    # Run fast tests (default, < 10 seconds)
    poetry run pytest

    # Run fast and medium tests
    poetry run pytest -m "immediate or short"

    # Run the full suite including long tests
    poetry run pytest -m "immediate or short or long"

See ``pytest --markers`` for all available timing markers.

Type Checking
=============

Run mypy to catch type errors:

.. code-block:: bash

    poetry run mypy src/

Commit Message Guidelines
=========================

Write clear, descriptive commit messages:

- Use the imperative mood in the subject line (e.g., "Add pulse count evaluator"
  not "Added pulse count evaluator")
- Keep the subject line under 72 characters
- If needed, add a blank line followed by a more detailed description

Examples::

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

4. CI will run tests across multiple Python versions automatically. Make sure
   all checks pass.

Code Style and Conventions
==========================

- **Docstrings**: Use `NumPy-style <https://numpydoc.readthedocs.io/en/latest/format.html>`_
  docstrings for all public classes and functions.
- **Architecture**: The codebase uses Python ``Protocol`` classes to define
  interfaces. See :doc:`/code/BitstreamEvolutionProtocols` for all core protocols.
- **Error handling**: Use the `returns <https://returns.readthedocs.io/>`_ library
  (``Success`` / ``Failure``) for operations that can fail, rather than raising
  exceptions.
- **Testing**: Write tests using pytest. Use ``unittest.mock.Mock(spec=ProtocolClass)``
  to mock protocol implementations.

Questions?
==========

Open an issue on the
`GitHub repository <https://github.com/evolvablehardware/BitstreamEvolution/issues>`_
if you have questions, find bugs, or want to discuss a feature idea.
