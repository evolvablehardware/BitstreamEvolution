-----------------------
Development Information
-----------------------

.. toctree::
    :maxdepth: 1
    :hidden:

    test_results

.. only:: dev

    .. seealso::
        :doc:`test_results` — Embedded CI test results from the latest build.

Link To Main Website
--------------------

Here is a section that should be replaced on main website, and visible on the dev branch.

Here is the link to the main website:
`MAIN WEBSITE <https://evolvablehardware.github.io/BitstreamEvolution/index.html>`_


How To Create The Website Manually
----------------------------------

The Webiste will be generated automatically by Github Actions, but this section is meant to remind me how I can create this sphinx website manually on my local computer.


.. code-block:: bash
    :caption: Installing Poetry & Compiling Website
    
    cd BitstreamEvolution/docs/sphinx

    poetry install --with dev
    
    poetry run make html

    cd build/html

    open_in_web_browser index.html



Below are some alternatives to the `poetry run make html` line above for slightly different goals:

.. code-block:: bash
    :caption: Installing using the Makefile or make.bat, implicitly running sphinx-build

    poetry run make html

.. code-block:: bash
    :caption: Creating the website to make the html website that is for public release

    poetry run sphinx-build -M html "source" "build" -t release

.. code-block:: bash
    :caption: Creating the website to make the html website that is for development use only

    poetry run sphinx-build -M html "source" "build" -t dev