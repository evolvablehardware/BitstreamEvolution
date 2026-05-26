==================================
Bitstream Evolution's Architecture
==================================

.. toctree::
   :maxdepth: 2
   :hidden:

   historical/index
   hardware/index

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


Hardware Controller
-------------------

.. mermaid::

   flowchart TD
        subgraph req[".request_Measurements()"]
            m1["Measurement (A) 
    (Circuit, FPGA Request, Data Request)"]
            m2["Measurement (B)"]
            me["Measurement (...)"]
        end
        hw["Hardware Object
    (async, one FPGA per Measurement)"]
        subgraph comp[".get_completed_Measurements()"]
            r1["Measurement (A)
    (FPGA Used + Ok(data))"]
            r2["Measurement (B)
    (FPGA Used + Err(failure))"]
            re["Measurement (...)"]
        end

    req ==> hw ==> comp

.. mermaid::

    flowchart TD
        m_in["Measurement (input)
    (Circuit, FPGA Request, Data Request)"]
        m_out["Measurement (output)
    (return FPGA Used + Result or Error)"]
        subgraph hw_obj["Hardware Object"]
            ctrl[["Hardware Controller Logic
    (selects one FPGA per Measurement based on FPGA Request field)"]]
            subgraph bank["FPGA Bank
    (local / remote / etc.)"]
                f_pool["FPGA Info (N available)"]
            end
        end

        m_in ==> ctrl
        f_pool -.->|"available
    pool"| ctrl
        ctrl ==>|"assigns to one FPGA,
    async evaluate"| m_out


The Hardware Object exposes a request/response API: callers submit a batch of Measurement
requests and retrieve completed results separately, allowing evaluations to proceed
asynchronously. Each Measurement carries an **FPGA Request** field that the Hardware Controller
uses to select an appropriate FPGA from its FPGA Bank — options include "don't care," requesting
specific FPGA UUIDs, or excluding certain UUIDs.

FPGAs in the bank may be accessed in different ways — directly connected via USB, hosted on a
remote server, or reached via a custom protocol — but the Hardware Object abstracts these
differences from callers.

When an FPGA completes (or fails) its evaluation, it writes two fields back into the Measurement:

- **FPGA Used**: the UUID of the FPGA that performed the evaluation, archived so results can be
  traced back to specific hardware.
- **Measurement Result**: either the collected data (**Ok**) or a description of the failure
  (**Err**) — stored as a Result type analogous to Rust's ``Result<T, E>``. Failure causes
  include no suitable FPGA available, a compilation error, or a hardware-level failure.

FPGAs are referenced in software using a ``<Hardware_UUID>:<FPGA_UUID>`` pair. This identifier
is not necessarily consistent between program runs but remains stable for the duration of a single
run. UUIDs can be correlated to uniquely identifiable information on the physical FPGA hardware
and stored to request measurements on specific hardware units.

Measurement Data Structure
--------------------------

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

The Measurement object contains four fields:

- **FPGA Request** (essentially an ENUM): controls FPGA selection — options are "don't care,"
  "request specific FPGA UUIDs," or "avoid specific FPGA UUIDs."
- **Data Request** (essentially an ENUM): specifies the type of measurement to be taken on the FPGA.
- **Measurement Result** (essentially a Result object): stores either the collected data, or a
  description of the failure — e.g. no satisfactory FPGA available, cannot perform the measurement,
  or cannot compile the Individual.
- **Measurement UUID**: intended to allow a single Individual evaluation to spawn multiple
  Measurements that can later be recombined; in practice, matching by Individual pointer may be
  sufficient.

Individual Data Structure
-------------------------

.. mermaid::

   flowchart TD
       subgraph Individual
           desc["Highly Implementation Dependent (Probably mostly data)"]
       end

An Individual stores the representation that is manipulated durring evolution to fully represent the things being evolved. 
It must be compilable into a form that can be loaded and run on an FPGA in order to be evaluated for its fitness. 
An open design question at proposal time was where to place the compilation logic — in the Individual itself, or in the Hardware controller —
and whether Individuals should be linked to a specific FPGA type or brand (subclass).

Population Representation
-------------------------

.. mermaid::

   flowchart TD
       subgraph Population
           ind1["Individuals"]
       end
       subgraph PopWithFitness["Population w/ fitness"]
           ind2["Individuals"]
           fit["Fitnesses"]
       end

The Population design deliberately avoids sub-populations with explicit links between them or to a parent population.
Each Population will always be dealt with as if it was the only one that exists in the processes that use it, even if 
one population is divided into multiple populations durring the course of an experiment and then recombined into one
population at the end of the experiment.
Conceptually it is a simple list with a few extra features, and could even be implemented as a
plain type alias (e.g. ``list[Individual] -> Population``).

Generation Metadata (i.e. 'Gen. Info')
--------------------------------------

.. mermaid::

   flowchart TD
       subgraph EvolutionGenerationInfo["Evolution Generation Info"]
           gennum["Generation #"]
           etc["..."]
       end

``EvolutionGenerationInfo`` holds the metadata for a particular generation of the evolution run
(e.g. the generation number). It is intended to be treated as **immutable** — a new instance is
produced each generation rather than mutating the existing one in place.

Experiment Structure
--------------------

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

These objects build and choreograph the entire evolution process as shown in the diagram above.
The orchestrator is provided with callable functions implementing each stage of evolution and is
responsible for wiring them together and driving the loop.

Generation Info Factory (a.k.a.'Incrementer')
---------------------------------------------

.. mermaid::

   flowchart TD
       old["Evolution Generation Info (OLD)"]
       op["Old Population"]
       np["New Population"]
       ci["Config Info (partial)"]
       etc["etc..."]
       incr[["Evolution Generation Info Incrementer"]]
       new["Evolution Generation Info (NEW)"]

       old ==> incr
       op --> incr
       np --> incr
       ci --> incr
       etc --> incr
       incr ==> new

The Incrementer takes in the old ``EvolutionGenerationInfo`` and decides what the next generation
looks like. When it returns ``None``, the evolution run is complete. It has access to both the old
and new population as well as partial config info, giving it enough context to make informed
decisions about when to terminate.

Generate Measurements
---------------------

.. mermaid::

   flowchart TD
       pop["Population"]
       geninfo["Evolution Generation Info"]
       gen[["Generate Measurements"]]
       list["List Of Measurements"]

       pop ==> gen
       geninfo --> gen
       gen ==> list

Converts a population of Individuals into a list of Measurements to be performed. The structure
of those measurements depends on the fitness function and evaluation approach being used.

Evaluate Measurements
---------------------

.. mermaid::

   flowchart TD
       list["List Of Measurements"]
       eval[["Evaluate Measurements (Done by Hardware Object)"]]
       result["List Of Measurements w/ Results"]

       list ==> eval
       eval ==> result

Fills in the ``Result`` field of each Measurement with the requested data. This step is performed
by the Hardware object, which dispatches each Measurement to an FPGA and collects the results.

Evaluate Fitness
----------------

.. mermaid::

   flowchart TD
       pop["Population"]
       meas["List Of Measurements"]
       geninfo["Evolution Generation Info"]
       eval[["Evaluate Fitnesses"]]
       result["Population w/ fitness"]

       pop ==> eval
       meas ==> eval
       geninfo --> eval
       eval ==> result

Interprets the completed measurement results and assigns fitness values to the corresponding
Individuals in the population.

Reproduce
---------

.. mermaid::

   flowchart TD
       popfit["Population w/ fitness"]
       geninfo["Evolution Generation Info"]
       reprod[["Reproduce"]]
       newpop["New Population"]

       popfit ==> reprod
       geninfo --> reprod
       reprod ==> newpop

Transforms the population-with-fitnesses into a new population for the next generation, using
the fitness values to guide selection and mutation.

Generate Circuit
----------------

.. mermaid::

   flowchart TD
       ind["Individual(s)"]
       gen[["Generate Circuit"]]
       subgraph meas["Measurement"]
       circ["Circuit"]
       end

       ind ==> gen
       gen ==> circ

Converts one or more Individuals into a Circuit that can be loaded onto an FPGA and evaluated.
The resulting Circuit is placed into a Measurement object. Note that Circuits may be
**specific to particular FPGAs**, or be composed of multiple individuals that are combined.

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
           foreach["For Each Circuit: Generate Measurement"]
           returnlist["Return List"]
           translate --> foreach --> returnlist
       end
       pop4 --> translate
       geninfo4 --> foreach
       config4 --> foreach
       returnlist --> mout["Measurements: A, B, C, D\n(Result: Err -- Unevaluated)"]

.. image:: images/initial_proposal/example/Arch_Example-5.png

.. mermaid::

   flowchart TD
       minput["Measurements: A, B, C, D (unevaluated)"]
       subgraph EvalMeas["Evaluate Measurements"]
           pass["Pass each Measurement to FPGA\n(via Hardware Object)"]
           update["Update Measurement with data from FPGA"]
           collect["Collect all measurements and return as list"]
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
       retnone11 --> out11(["None -- Evolution complete"])

.. image:: images/initial_proposal/example/Arch_Example-12.png


Early Design Ideas
==================

Below is one of the early attempts at conceptualizing an architecture for this
project:

.. image:: images/EarlyDesignIdea.png
