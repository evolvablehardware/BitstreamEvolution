==============================================
Welcome to BitstreamEvolution's Documentation!
==============================================

This is the |doc_branch| branch documentation for BitstreamEvolution.

.. only:: release

    .. image:: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml/badge.svg?branch=main
       :target: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml?query=branch%3Amain
       :alt: Main Branch CI Status

.. only:: dev

    .. button-link:: https://evolvablehardware.github.io/BitstreamEvolution/
       :color: primary
       :align: center
       :outline:

       View Release Documentation

    .. warning::

        **This is the development documentation** for the ``develop`` branch, which is
        actively being worked on by developers. It may contain incomplete features,
        experimental content, or issues not present on the
        `stable release site <https://evolvablehardware.github.io/BitstreamEvolution/>`_.

        This site also includes **TODO items** and **development notes** that are hidden
        on the release website. If you are looking for stable documentation, please visit
        the release site linked above.

    |  **Develop branch:**

    .. image:: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml/badge.svg?branch=develop
       :target: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml?query=branch%3Adevelop
       :alt: Develop Branch CI Status

    |  **Main branch:**

    .. image:: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml/badge.svg?branch=main
       :target: https://github.com/evolvablehardware/BitstreamEvolution/actions/workflows/initialize-push-workflows.yml?query=branch%3Amain
       :alt: Main Branch CI Status

.. note::
   Currently we are trying to do a rewrite of the main repository to use new interfaces to make the codebase more modular.
   Until this is done, the ``develop`` branch will be used for this process and modifications will be made to the ``main`` branch directly for pre-existing code.

.. grid:: 2
    :gutter: 3

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

        Protocol interfaces, implementations, and auto-generated module docs.

    .. grid-item-card:: Development
        :link: dev/index
        :link-type: doc

        Build instructions, test results, and contribution information.

----

The Evolvable Hardware Community
================================

BitstreamEvolution is one project developed by the Evolvable Hardware research group,
which explores the use of evolutionary computation on physical hardware.
Visit the community website to learn about other projects and ongoing research in this space.

.. button-link:: https://evolvablehardware.github.io/
   :color: secondary
   :align: center
   :outline:

   Evolvable Hardware Community Website

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
