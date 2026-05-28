==========================================
pyproject.toml Interpreter
==========================================

``interpret_pyproject.py`` is a small CLI script that acts as an adapter
between GitHub Actions workflows and ``pyproject.toml``. It reads configuration
values from the TOML file and outputs them as JSON so that workflows can consume
them without parsing TOML directly.

Why It Exists
=============

GitHub Actions workflows are YAML files that are awkward to maintain when they
contain hardcoded values (Python versions to test, pytest marker groups, etc.).
The traditional alternative is to duplicate those values in both the workflow
file and ``pyproject.toml``, which causes them to drift out of sync.

This script solves that by making ``pyproject.toml`` the **single source of
truth** for CI configuration. A developer who wants to add a new Python version
or change which test groups run in parallel only needs to edit ``pyproject.toml``
— they never need to open a workflow file.

The script also gives the workflow-to-TOML interface a stable name (the
``--flag`` arguments) that is independent of the TOML structure. If the key
path inside ``pyproject.toml`` ever changes, only this script needs updating,
not every workflow that uses the value.

How It Works
============

The script accepts one or more ``--flag`` arguments. For each flag it extracts
the corresponding value from ``pyproject.toml`` and collects it into a dict.
When done it prints the result as JSON:

- **One flag** → prints just the raw JSON-encoded value (e.g. a list or string)
- **Multiple flags** → prints a JSON object mapping flag names to values

.. code-block:: bash
    :caption: Examples

    # Single value — prints a JSON list
    poetry run python interpret_pyproject.py --python_versions
    # → ["3.11", "3.12", "3.13"]

    # Multiple values — prints a JSON object
    poetry run python interpret_pyproject.py --python_versions --pytest_testing_groups
    # → {"python_versions": ["3.11", ...], "pytest_testing_groups": [...]}

Available Flags
===============

.. list-table::
    :header-rows: 1
    :widths: 30 70

    * - Flag
      - Value extracted from ``pyproject.toml``
    * - ``--python_versions``
      - ``[tests.workflows] python-versions`` — the Python versions the CI matrix tests against
    * - ``--homepage``
      - ``[tool.poetry] homepage`` — the project homepage URL
    * - ``--repository``
      - ``[tool.poetry] repository`` — the GitHub repository URL
    * - ``--documentation``
      - ``[tool.poetry] documentation`` — the documentation site URL
    * - ``--pytest_testing_groups``
      - ``[tests.workflows] pytest-testing-groups`` — the list of pytest marker expressions run as separate CI jobs
    * - ``--test_results_display_selector``
      - ``[tests.workflows] test-results-display-selector`` — which result types to show in the CI report (``pytest -r`` format)
    * - ``--test_results_display_summary``
      - ``[tests.workflows] test-results-display-summary`` — whether to include a summary table in CI test results

How Workflows Use It
====================

The script is invoked via the reusable workflow
``.github/workflows/read-toml.yml``, which:

1. Converts the requested flag names (passed as a JSON list input) into
   ``--flag`` arguments for the script
2. Checks out the target branch
3. Installs the minimal ``gh_read_pyproject`` Poetry dependency group
   (just ``toml`` — no dev tools needed)
4. Runs the script and captures its JSON output as a workflow output
   called ``toml_values``

The main CI workflow (``initialize-push-workflows.yml``) calls
``read-toml.yml`` as its first job and then passes
``fromJson(needs.PyprojectTOML.outputs.toml_values)['key']`` wherever it
needs a configured value — for example to populate the Python version matrix
and the pytest marker groups.

.. important::

    ``read-toml.yml`` is pinned to ``@main`` in the workflow file because
    GitHub Actions requires a static ref for reusable workflows. This means
    **changes to** ``interpret_pyproject.py`` **or** ``read-toml.yml`` **on**
    ``develop`` **do not take effect in CI until they are merged to** ``main``.
    Keep this in mind when adding new flags or restructuring either file.

Dependencies
============

The script uses only ``toml`` and the Python standard library. This is
intentional — the ``gh_read_pyproject`` Poetry group installs the absolute
minimum needed so the checkout-and-read step in CI is as fast as possible.

.. code-block:: toml
    :caption: pyproject.toml — gh_read_pyproject group

    [tool.poetry.group.gh_read_pyproject.dependencies]
    toml = "^0.10"

Adding a New Value
==================

To expose a new configuration value to workflows:

1. Add the value under ``[tests.workflows]`` (or another appropriate section)
   in ``pyproject.toml``.

2. Register a new flag in ``interpret_pyproject.py``:

   .. code-block:: python

       create_value_identifier(parser, "my_new_value", "Description of the value.")

3. Add the extraction logic:

   .. code-block:: python

       if args.my_new_value:
           output["my_new_value"] = py_project_data["tests"]["workflows"]["my-new-value"]

4. Add ``"my_new_value"`` to the ``values`` list in any workflow job that
   needs it.

5. Merge to ``main`` before expecting CI to pick up the change (see the
   important note above).
