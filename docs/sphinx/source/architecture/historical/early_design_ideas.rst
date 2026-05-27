Early Design Ideas
==================

This page documents one of the early attempts at conceptualizing a formal
architecture for BitstreamEvolution, predating the current protocol-based
design. The diagram represents a more procedural, monolithic approach where
major stages were loosely coupled through a shared ``Logger`` rather than
through formally defined protocol interfaces.

This architecture was superseded by the initial proposal, which introduced
clearer separation of concerns through protocol-based interfaces.

Top-Level Experiment Flow
-------------------------

The overall experiment lifecycle proceeds as follows. A single run starts
with settings collection and hardware configuration, generates an initial
population, then repeatedly evaluates fitness and evolves the population
until a stopping criterion is met. After saving the experiment, the user
can optionally begin a new one.

A ``Logger`` object is threaded through all major stages, collecting data
at each step for later analysis.

.. mermaid::

   flowchart TD
       START([START]) --> CollectSettings["Collect Settings"]
       CollectSettings --> ConfigHW["Configure Hardware"]
       ConfigHW --> GenInitPop["Generate Initial Population"]
       GenInitPop --> Pop["Population"]
       Pop --> EvalFit

       subgraph EvolutionLoop["Evolution Loop"]
           direction TB
           EvalFit["Evaluate Fitness"]
           PopFit["Population w/ Fitness"]
           EvolvePop["Evolve Population"]
           ContEvol{"Continue\nEvolution?"}

           EvalFit --> PopFit
           PopFit --> EvolvePop
           EvolvePop --> ContEvol
           ContEvol -->|"Yes"| EvalFit
       end

       ContEvol -->|"No"| SaveExp["Save Experiment"]
       SaveExp --> StartNew{"Start New\nExperiment?"}
       StartNew -->|"Yes"| CollectSettings
       StartNew -->|"No"| STOP([STOP])

       Logger["Logger"] -.-> CollectSettings
       Logger -.-> ConfigHW
       Logger -.-> EvalFit
       Logger -.-> EvolvePop
       Logger -.-> SaveExp

Evaluate Fitness
----------------

Fitness evaluation processes each individual in the population one at a time.
The individual's representation is compiled into a circuit, uploaded to FPGA
hardware, the result is read back, and a fitness score is computed and stored.

.. mermaid::

   flowchart TD
       PopIn["Population"] --> Circuit["Circuit"]
       Circuit --> Compile["Compile"]
       Compile --> CompiledInfo["Compiled Info"]
       CompiledInfo --> Upload["Upload"]
       Upload --> FitnessInfo["Fitness Info"]
       FitnessInfo --> ComputeFitness["Compute Fitness"]
       ComputeFitness --> Fitness["Fitness"]
       Fitness --> StoreFitness["Store Fitness"]
       StoreFitness --> PopOut["Population w/ Fitness"]

Evolve Population
-----------------

Population evolution consists of two sub-stages: a selection-and-mutation
phase, followed by assembly of the next generation.

**Selection Method**: The current population (with fitnesses) is divided into
sub-populations. Each sub-population is independently mutated to produce new
candidate sub-populations. This allows multiple evolutionary pressures to run
in parallel before being recombined.

**Generate New Population**: The mutated sub-populations are altered (individuals
added or removed as needed), then merged and subjected to a final mutation step
to produce the next generation's population.

.. mermaid::

   flowchart TD
       PopFitIn["Population w/ Fitness"]

       subgraph SelectionMethod["Selection Method"]
           direction LR
           SubPopA["Population w/ Fitness"]
           SubPopDots["..."]
           SubPopB["Population w/ Fitness"]
           MutateA["Mutate"]
           MutateB["Mutate"]
           OutA["Population w/ Fitness"]
           OutDots["..."]
           OutB["Population w/ Fitness"]

           SubPopA --> MutateA --> OutA
           SubPopDots ~~~ OutDots
           SubPopB --> MutateB --> OutB
       end

       subgraph GenNewPop["Generate New Population"]
           direction TB
           AlterPop["Alter Sub-Populations\n(copy / remove entries)"]
           CombinePop["Combine Populations"]
           MutateFinal["Mutate"]
           FinalPop["Population"]

           AlterPop --> CombinePop --> MutateFinal --> FinalPop
       end

       PopFitIn --> SubPopA
       PopFitIn --> SubPopB
       OutA --> AlterPop
       OutB --> AlterPop
       FinalPop --> PopOut["Population"]

Original Diagram
----------------

.. image:: ../images/EarlyDesignIdea.png
