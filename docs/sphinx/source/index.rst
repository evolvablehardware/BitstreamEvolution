==============================================
Welcome to BitstreamEvolution's documentation!
==============================================

This is the |doc_version| documentation for BitstreamEvolution.

.. image:: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml/badge.svg
   :target: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml
   :alt: CI Status

.. note::
   Currently we are trying to do a rewrite of the main repository to use new interfaces to make the codebase more modular.
   Until this is done, the ``develop`` branch will be used for this process and modifications will be made to the ``main`` branch directly for pre-existing code.

.. grid:: 2

    .. grid-item-card:: Getting Started
        :link: quickstart
        :link-type: doc

        Installation, prerequisites, and running your first experiment.

    .. grid-item-card:: Architecture
        :link: architecture/index
        :link-type: doc

        System design, hardware model, and protocol specifications.

    .. grid-item-card:: API Reference
        :link: code/index
        :link-type: doc

        Auto-generated documentation from source code docstrings.

    .. grid-item-card:: Development
        :link: dev/index
        :link-type: doc

        Build instructions, test results, and contribution information.

.. toctree::
   :maxdepth: 2
   :hidden:

   quickstart
   dev/index
   architecture/index
   code/index

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

To Do List
==========
.. todolist::

.. important::
   Todo lists only appear if enabled. They will not be enabled on the main website, only develop.
   To do this, run: ``sphinx-build -M html source build -t dev``
