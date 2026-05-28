==============================
Building the Documentation
==============================

The documentation is built automatically by GitHub Actions on every push, but
you can also compile it locally to preview changes before pushing.

Prerequisites
-------------

Install all development dependencies (documentation tools, testing, linting):

.. code-block:: bash

    poetry install --with dev

Local Build
-----------

.. code-block:: bash
    :caption: Build and open the documentation locally

    cd BitstreamEvolution/docs/sphinx

    poetry run sphinx-build -M html source build

    # Then open docs/sphinx/build/html/index.html in your browser

Build Variants
--------------

Two tagged build variants control which content is visible:

.. list-table::
    :header-rows: 1
    :widths: 20 25 55

    * - Tag
      - Command
      - Effect
    * - ``release``
      - ``-t release``
      - Hides dev-only warnings, TODO lists, and the develop-branch notice. This is what GitHub Actions deploys to the main site.
    * - ``dev``
      - ``-t dev``
      - Shows TODO items, development warnings, and CI badge for the develop branch. Use this to preview the develop site locally.

.. code-block:: bash
    :caption: Release build (mirrors what is deployed to the main site)

    poetry run sphinx-build -M html source build -t release

.. code-block:: bash
    :caption: Dev build (mirrors what is deployed to the develop branch site)

    poetry run sphinx-build -M html source build -t dev

.. note::

    If no tag is passed, the build defaults to ``release`` behaviour for most
    content but will not match either variant exactly. Always use ``-t release``
    or ``-t dev`` when checking how content will appear on the deployed sites.
