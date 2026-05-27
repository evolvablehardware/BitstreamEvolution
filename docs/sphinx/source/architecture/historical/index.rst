Historical Architectures
========================

.. toctree::
   :maxdepth: 2
   :hidden:

   early_design_ideas

This section is an archive for all previous architectures used by this project. The
:doc:`main architecture page </architecture/index>` always reflects the most current design.
As diagrams or architectural decisions become outdated or superseded, a snapshot of them should
be moved here.

Entries are ordered from **most recently archived to oldest**. Each entry includes a brief
description of the architecture and the reason it was retired or replaced.

Timeline
--------

Initial Proposal *(pending archive)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The initial architecture proposal — its slides, diagrams, and worked examples — is currently
still hosted on the main architecture page under the "Initial Proposal" section. Once a newer
architecture supersedes it, that material should be moved here as the top archive entry.

Early Design Ideas
~~~~~~~~~~~~~~~~~~

*Predates the initial proposal.*

:doc:`early_design_ideas`

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
