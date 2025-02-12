==============================================
Welcome to BitstreamEvolution's documentation!
==============================================

This is the |doc_version| documentation for BitstreamEvolution.

.. note:: 
   Currently we are trying to do a rewrite of the main repository to use new interfaces to make the codebase more modular. 
   Until this is done, the `develop` branch will be used for this process and modifications will be made to the `main` branch directly for pre-existing code.
   I also converted all todos in old_code to warnings to avoid cluttering up the todolist while refactoring.

.. todo::
   Run tests from the repository dev or main that was last pushed.

.. todo::
   Display results from test runs on website. Likely put this in the dev folder, only revealing on the dev branch.

.. toctree::
   :maxdepth: 2

   dev/index
   interface/index
   code/index
   old_code/index

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
   to do this, run: `sphinx-build -M  html source build -t dev`