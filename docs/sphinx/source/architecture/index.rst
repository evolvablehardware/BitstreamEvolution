==================================
Bitstream Evolution's Architecture
==================================

The original code was designed in a vaguely class-like structure to prove the
concept, but once proven it became very challenging to change the code and
coordinate those changes, even in a small group. Thus, we created the following
general architecture to make the code more modular and easy to edit and use for
a broader range of applications.

Overview
========

BitstreamEvolution uses a **protocol-based architecture**: every major component
is defined as a Python ``Protocol`` class in
:doc:`/code/BitstreamEvolutionProtocols`, so that implementations can be swapped
without changing the orchestration code. The main loop
(:doc:`/code/Evolution`) wires these components together.

The data flow through a single generation looks like this:

1. A :class:`~BitstreamEvolutionProtocols.GenDataFactory` produces or
   increments the generation metadata and decides when to stop.
2. A :class:`~BitstreamEvolutionProtocols.CircuitFactory` converts the
   :class:`~BitstreamEvolutionProtocols.Population` of
   :class:`~BitstreamEvolutionProtocols.Individual` objects into
   :class:`~BitstreamEvolutionProtocols.Circuit` objects ready for hardware.
3. A :class:`~BitstreamEvolutionProtocols.GenerateMeasurements` strategy
   creates :class:`~BitstreamEvolutionProtocols.Measurement` objects — one per
   Circuit — describing what to measure.
4. The :class:`~BitstreamEvolutionProtocols.Hardware` interface compiles each
   Circuit (``icepack`` / ``iceprog``), uploads it to an FPGA, and fills the
   Measurement with raw data (waveform samples or pulse counts).
5. An :class:`~BitstreamEvolutionProtocols.EvaluatePopulationFitness` evaluator
   interprets the raw measurements and assigns
   :class:`~BitstreamEvolutionProtocols.Fitness` values to each Individual.
6. A :class:`~BitstreamEvolutionProtocols.Reproducer` performs selection and
   mutation to produce the next generation's Population.

For a working end-to-end example that exercises this entire pipeline with
integer-valued circuits (no hardware required), see
:doc:`/code/TrivialImplementation`.

General Structure
=================

Below is the best current description of our architecture. It is currently
pretty in-line with the initial proposal.

.. mermaid::

   flowchart TD
       A([Run Evolution]) --> B["Generate Initial Population"]
       B -->|"Population + Gen. Info"| C["Evolution Generation Info Incrementer"]
       C -->|"None returned"| X([Exit])
       C -->|"Population + New Gen. Info"| D["Generate Measurements"]
       D -->|"Gen. Info + List Of Measurements"| E["Evaluate Measurements"]
       E -->|"Gen. Info + List Of Measurements"| F["Evaluate Fitnesses"]
       D -->|"Population"| F
       F -->|"Gen. Info + Population w/ fitness"| G["Reproduce"]
       G -->|"Gen. Info + New Population"| C


Initial Proposal
================

Below are a series of slides from the initial proposal for the architecture.
These are non-final, but were going in the right direction.

To see this as the original presentation, `look here <https://docs.google.com/presentation/d/1QkHsh1EmpQeNTC4FLra8Vry-5Ln28tJxNxoWPVK5R3A/edit?usp=sharing>`_.

I then attempted to implement a basic example of it in the
:doc:`/code/TrivialImplementation` file.

Architecture Description
------------------------

.. image:: images/initial_proposal/Arch_Proposal-1.png

.. image:: images/initial_proposal/Arch_Proposal-2.png

.. mermaid::

   flowchart TD
       input["Measurement (input)"]
       subgraph Hardware
           ctrl["Logic: Hardware Controller"]
           fpga1["FPGA Info"]
           fpga2["FPGA Info"]
           fpgan["..."]
       end
       out1["Measurement"]
       out2["Measurement"]
       completed["Completed Measurements"]

       input -->|"Request Measurement"| ctrl
       ctrl -->|"Perform Measurement"| fpga1
       ctrl -->|"Perform Measurement"| fpga2
       ctrl -->|"Perform Measurement"| fpgan
       fpga1 --> out1
       fpga2 --> out2
       out1 -->|"Request Completed Measurements"| completed
       out2 --> completed

.. image:: images/initial_proposal/Arch_Proposal-3.png

.. mermaid::

   flowchart TD
       subgraph Measurement
           FR["FPGA Request"]
           DR["Data Request"]
           subgraph Circuit["Circuit (to evaluate)"]
               CI["Constructed from Individuals"]
           end
           FU["FPGA Used: Hardware_UUID:FPGA_UUID"]
           MR["Measurement Result: Data or Errors"]
       end

.. image:: images/initial_proposal/Arch_Proposal-4.png

.. mermaid::

   flowchart TD
       subgraph Individual
           desc["Highly Implementation Dependent (Probably mostly data)"]
       end

.. image:: images/initial_proposal/Arch_Proposal-5.png

.. mermaid::

   flowchart TD
       subgraph Population
           ind1["Individuals"]
       end
       subgraph PopWithFitness["Population w/ fitness"]
           ind2["Individuals"]
           fit["Fitnesses"]
       end

.. image:: images/initial_proposal/Arch_Proposal-6.png

.. mermaid::

   flowchart TD
       subgraph EvolutionGenerationInfo["Evolution Generation Info"]
           gennum["Generation #"]
           etc["..."]
       end

.. image:: images/initial_proposal/Arch_Proposal-7.png

.. mermaid::

   flowchart TD
       A([Run Evolution]) --> B["Generate Initial\nPopulation"]
       B -->|"Population + Gen. Info"| C["Evolution Generation\nInfo Incrementer"]
       C -->|"None returned"| X([Exit])
       C -->|"Population + New Gen. Info"| D["Generate\nMeasurements"]
       D -->|"Gen. Info + List Of Measurements"| E["Evaluate\nMeasurements"]
       E -->|"Gen. Info + List Of Measurements"| F["Evaluate\nFitnesses"]
       F -->|"Gen. Info + Population w/ fitness"| G["Reproduce"]
       G -->|"New Population"| C

.. image:: images/initial_proposal/Arch_Proposal-8.png

.. mermaid::

   flowchart TD
       old["Evolution Generation Info (OLD)"]
       op["Old Population"]
       np["New Population"]
       ci["Config Info (partial)"]
       etc["etc..."]
       incr["Evolution Generation\nInfo Incrementer"]
       new["Evolution Generation Info (NEW)"]

       old --> incr
       op --> incr
       np --> incr
       ci --> incr
       etc --> incr
       incr --> new

.. image:: images/initial_proposal/Arch_Proposal-9.png

.. mermaid::

   flowchart TD
       pop["Population"]
       geninfo["Evolution Generation Info"]
       gen["Generate Measurements"]
       list["List Of Measurements"]

       pop --> gen
       geninfo --> gen
       gen --> list

.. image:: images/initial_proposal/Arch_Proposal-10.png

.. mermaid::

   flowchart TD
       list["List Of Measurements"]
       eval["Evaluate Measurements\n(Done by Hardware Object)"]
       result["List Of Measurements w/ Results"]

       list --> eval
       eval --> result

.. image:: images/initial_proposal/Arch_Proposal-11.png

.. mermaid::

   flowchart TD
       pop["Population"]
       meas["List Of Measurements"]
       geninfo["Evolution Generation Info"]
       eval["Evaluate Fitnesses"]
       result["Population w/ fitness"]

       pop --> eval
       meas --> eval
       geninfo --> eval
       eval --> result

.. image:: images/initial_proposal/Arch_Proposal-12.png

.. mermaid::

   flowchart TD
       popfit["Population w/ fitness"]
       geninfo["Evolution Generation Info"]
       reprod["Reproduce"]
       newpop["New Population"]

       popfit --> reprod
       geninfo --> reprod
       reprod --> newpop

.. image:: images/initial_proposal/Arch_Proposal-13.png

.. mermaid::

   flowchart TD
       ind["Individual(s)"]
       gen["Generate Circuit"]
       circ["Circuit"]
       note["(Put into a Measurement Object)"]

       ind --> gen
       gen --> circ
       circ -.-> note

Architectural Example
---------------------

.. image:: images/initial_proposal/example/Arch_Example-1.png

.. image:: images/initial_proposal/example/Arch_Example-2.png

.. mermaid::

   flowchart TD
       subgraph GenInitPop["Generate Initial Population"]
           rand["Randomly Generate Individual"]
           measure["Measure Pulse Count"]
           check{"Non-zero pulses?"}
           indiv["Individual (valid)"]
           mutate["Perform Mutation"]
           rand --> measure --> check
           check -->|"No"| rand
           check -->|"Yes"| indiv --> mutate
       end
       start((" ")) --> rand
       mutate --> popout["Population: A, B, C, D\n(Fitness: None)"]

.. image:: images/initial_proposal/example/Arch_Example-3.png

.. mermaid::

   flowchart TD
       geninfoin["Gen Info input: None (first run)"]
       prevpop["Prev. Population: None"]
       nextpop["Next Population: A, B, C, D\n(Fitness: None)"]
       config["Config Info"]
       subgraph Incr["Evolution Generation Info Incrementer"]
           isnone{"Generation Info is None?"}
           initgen["Generate Initial Gen Info"]
           genchk{"Generation Number < 500"}
           isnone -->|"True"| initgen
           isnone -->|"False"| genchk
           increment["New Gen Info: Gen # = 0"]
           retnone["Return None"]
           genchk -->|"True"| increment
           genchk -->|"False"| retnone
       end
       geninfoin --> isnone
       prevpop --> isnone
       nextpop --> isnone
       config --> genchk
       initgen --> out["Gen Info: Generation # = 0"]
       

.. image:: images/initial_proposal/example/Arch_Example-4.png

.. mermaid::

   flowchart TD
       pop4["Population: A, B, C, D (Fitness: None)"]
       geninfo4["Evolution Generation Info"]
       config4["Config Info"]
       subgraph GenMeas["Generate Measurements"]
           translate["Translate Individuals to Circuits"]
           foreach["For Each Circuit:\nGenerate Measurement"]
           returnlist["Return List"]
           translate --> foreach --> returnlist
       end
       pop4 --> translate
       geninfo4 --> foreach
       config4 --> foreach
       returnlist --> mout["Measurements: A, B, C, D\n(Result: Err — Unevaluated)"]

.. image:: images/initial_proposal/example/Arch_Example-5.png

.. mermaid::

   flowchart TD
       minput["Measurements: A, B, C, D (unevaluated)"]
       subgraph EvalMeas["Evaluate Measurements"]
           pass["Pass each Measurement to FPGA\n(via Hardware Object)"]
           update["Update Measurement with\ndata from FPGA"]
           collect["Collect all measurements\nand return as list"]
           pass --> update --> collect
       end
       minput --> pass
       collect --> mresult["Measurements: A, B, C, D (with results)\ne.g. A: Ok(4_000 Pulses), C: Err(Serial Failure)"]

.. image:: images/initial_proposal/example/Arch_Example-6.png

.. mermaid::

   flowchart TD
       meas6["Measurements: A, B, C, D (with results)"]
       pop6["Population: A, B, C, D (Fitness: None)"]
       geninfo6["Evolution Generation Info"]
       config6["Config Info"]
       subgraph EvalFit["Evaluate Fitness"]
           correlate["Correlate individuals to\nassociated measurements"]
           foreach6["For Each Individual:\nRead Measurement(s)"]
           iferror["Fitness = 0"]
           ifsuccess["Apply fitness function"]
           putpop["Put into population"]
           correlate --> foreach6
           foreach6 -->|"If Error"| iferror
           foreach6 -->|"If Success"| ifsuccess
           iferror --> putpop
           ifsuccess --> putpop
       end
       meas6 --> correlate
       pop6 --> correlate
       geninfo6 --> foreach6
       config6 --> foreach6
       putpop --> fitout["Population: A=0.98, B=0.86, C=0.00, D=0.05"]

.. image:: images/initial_proposal/example/Arch_Example-7.png

.. mermaid::

   flowchart TD
       pop7["Population: A=0.98, B=0.86, C=0.00, D=0.05"]
       geninfo7["Evolution Generation Info"]
       config7["Config Info"]
       subgraph Reprod["Reproduction"]
           select["Select top 50%\n(A, B)"]
           dup["Duplicate Individuals"]
           elites["Don't mutate Elites\n(A, B)"]
           mutated["Mutate Copy\n(A', B')"]
           create["Create new population"]
           select --> dup
           dup -->|"One Copy"| elites
           dup -->|"Other Copy"| mutated
           elites --> create
           mutated --> create
       end
       pop7 --> select
       geninfo7 --> create
       config7 --> create
       create --> repout["Population: A, B, A', B' (Fitness: None)"]

.. image:: images/initial_proposal/example/Arch_Example-8.png

.. image:: images/initial_proposal/example/Arch_Example-9.png

.. mermaid::

   flowchart TD
       geninfoin9["Gen Info input: Generation # = 0"]
       prevpop9["Prev. Population: A=0.98, B=0.86, C=0.00, D=0.05"]
       nextpop9["Next Population: A, B, A', B' (Fitness: None)"]
       config9["Config Info"]
       subgraph Incr9["Evolution Generation Info Incrementer"]
           isnone9{"Gen Info is None?"}
           initgen9["Generate Initial Gen Info"]
           genchk9{"Gen # < 500"}
           increment9["New Gen Info: (Gen #)++"]
           retnone9["Return None"]
           isnone9 -->|"True"| initgen9
           isnone9 -->|"False"| genchk9
           genchk9 -->|"True"| increment9
           genchk9 -->|"False"| retnone9
       end
       geninfoin9 --> isnone9
       prevpop9 --> isnone9
       nextpop9 --> isnone9
       config9 --> genchk9
       increment9 --> out9["Gen Info: Generation # = 1"]

.. image:: images/initial_proposal/example/Arch_Example-10.png

.. image:: images/initial_proposal/example/Arch_Example-11.png

.. mermaid::

   flowchart TD
       geninfoin11["Gen Info input: Generation # = 500"]
       prevpop11["Prev. Population (with fitnesses)"]
       nextpop11["Next Population (evolved, Fitness: None)"]
       config11["Config Info"]
       subgraph Incr11["Evolution Generation Info Incrementer"]
           isnone11{"Gen Info is None?"}
           initgen11["Generate Initial Gen Info"]
           genchk11{"Gen # < 500"}
           increment11["New Gen Info: (Gen #)++"]
           retnone11["Return None"]
           isnone11 -->|"True"| initgen11
           isnone11 -->|"False"| genchk11
           genchk11 -->|"True"| increment11
           genchk11 -->|"False"| retnone11
       end
       geninfoin11 --> isnone11
       prevpop11 --> isnone11
       nextpop11 --> isnone11
       config11 --> genchk11
       retnone11 --> out11(["None — Evolution complete"])

.. image:: images/initial_proposal/example/Arch_Example-12.png


Hardware Documentation
======================

.. toctree::
    :maxdepth: 1

    ice40_hardware
    mcu_protocol

Early Design Ideas
==================

Below is one of the early attempts at conceptualizing an architecture for this
project:

.. image:: images/EarlyDesignIdea.png
