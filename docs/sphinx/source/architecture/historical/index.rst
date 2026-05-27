Historical Architectures
========================

.. toctree::
   :maxdepth: 2
   :hidden:

   initial_proposal
   early_design_ideas

This section is an archive for all previous architectures used by this project. The
:doc:`main architecture page </architecture/index>` always reflects the most current design.
As diagrams or architectural decisions become outdated or superseded, a snapshot of them should
be moved here.

Entries are ordered from **most recently archived to oldest**. Each entry includes a brief
description of the architecture and the reason it was retired or replaced.

Timeline
--------

Initial Proposal
~~~~~~~~~~~~~~~~

*Created prior to implementation and not updated.*

.. button-ref:: initial_proposal
   :ref-type: doc
   :color: primary
   :shadow:

The first formal architecture proposal. Introduced the protocol-based, modular design that
shaped the current architecture: separate protocols for hardware, measurement generation,
fitness evaluation, and reproduction, all orchestrated by a central evolution loop. Also
includes a pulse-count worked example tracing one complete run from initialization through
termination. The original slide presentation is linked from the archived page. Archived once
the implementation matured and the main architecture page transitioned to documenting the
live design rather than the proposal.

Early Design Ideas
~~~~~~~~~~~~~~~~~~

*Informed the initial proposal.*

.. button-ref:: early_design_ideas
   :ref-type: doc
   :color: primary
   :shadow:

A first attempt at sketching a formal architecture: a procedural, monolithic flowchart
covering the full experiment lifecycle (settings collection, hardware configuration, fitness
evaluation, population evolution, and experiment saving). Stages were loosely coupled through
a shared ``Logger`` rather than through protocol interfaces. This sketch motivated the more
structured initial proposal.

Proof-of-Concept Code
~~~~~~~~~~~~~~~~~~~~~

*Predates the initial proposal.*

The original codebase had no formal architecture. It was structured in a vaguely class-like way
with the sole goal of proving that evolutionary computation on FPGAs was feasible — it simply
needed to work. As the codebase grew, coordinating even small changes became increasingly
difficult, because there was no principled separation of concerns or well-defined interfaces.
This accumulation of friction was the primary motivation for the initial architecture proposal,
which set out to make the system modular and adaptable to a broader range of experimental
configurations.

No formal diagrams exist for this era; the structure can be inferred from early git history.
