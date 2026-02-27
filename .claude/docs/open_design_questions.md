# Open Design Questions

Unresolved design decisions captured from TODOs in the source code.

---

## 1. Mutation Interface

**Source**: [BitstreamEvolutionProtocols.py:10-18](../../src/BitstreamEvolutionProtocols.py#L10-L18)

**Question**: Where should mutation happen — on `Individual` objects or `Circuit` objects?

**Current state**: `BitstreamIndividual` has a `mutate()` method but there is no `Individual` protocol method for mutation. The `Reproducer` protocol doesn't specify how reproduction/mutation works internally.

**Analysis**:
- If `Individual` is the unit of evolution (it holds the bitstream), mutation should act on `Individual`
- `Circuit` is the evaluated representation — it's derived from `Individual` via `CircuitFactory`. Mutating a `Circuit` directly would bypass the Individual-Circuit separation.
- The 1:1 case: `CircuitFactory` copies the Individual's bitstream into the Circuit. If you mutate the Individual, the next `CircuitFactory` call picks up the change. This is the expected flow.

**Remaining question**: Should `Individual` protocol formally declare a `mutate()` method, or should `Reproducer` call `mutate()` on concrete Individual types it knows about?

**Options**:
- A: Add `mutate()` to `Individual` protocol — enforces the interface, but then ALL Individual implementations need it
- B: Leave `Individual` protocol empty — `Reproducer` implementations cast to the concrete type they expect
- C: Add a separate `Mutable` protocol that `BitstreamIndividual` satisfies — optional interface

**Implication for linking Individual to Circuit**: For 1:1 relationships, `CircuitFactory` calls `individual.get_bitstream()` (type: ignore) on the Individual, as seen in `FileBasedCircuitFactory`. This pattern works today but isn't enforced by the protocol.

---

## 2. Measurement Taking Protocol

**Source**: [BitstreamEvolutionProtocols.py:15-18](../../src/BitstreamEvolutionProtocols.py#L15-L18)

**Question**: Should `DataRequest` enum be replaced with a protocol for specifying what measurement to take?

**Current state**: `Measurement.data_request` is a `DataRequest` enum (`WAVEFORM`, `OSCILLATIONS`, `NONE`). `Microcontroller.request_measurement()` dispatches on this enum.

**Comment in source**:
> "Only thing is I think we need some protocol for taking/collecting a measurement. Potentially replacing the 'data_request' field in Measurement. This would have diff. implementations for VarMax, PulseCount, ToneDiscrimination, etc."

**Options**:
- A: Keep `DataRequest` enum — simple, hardcodes the supported measurement types
- B: Replace with a `MeasurementProtocol` — callable that takes a circuit+hardware and returns a measurement result. Extensible but adds complexity.
- C: Keep `DataRequest` enum but add new values as needed — incremental, no architectural change

---

## 3. FPGA Request Format

**Source**: [BitstreamEvolutionProtocols.py:214-215](../../src/BitstreamEvolutionProtocols.py#L214-L215)

**Question**: What is the format/type of `FPGA_request` in `Measurement`?

**Current state**: `Measurement.FPGA_request` is typed as `str`. The comment says:
> "Figure out the format for an FPGA Request, potentially also changing the type"

In practice, `Microcontroller` receives an FPGA identifier string (e.g., a USB port path like `/dev/ttyUSB0`) and uses it to select which hardware to communicate with. The `MicrocontrollerConfig.usb_path` field holds this.

**Options**:
- A: Keep as `str` — simple, works for the current single-FPGA case
- B: Use `FPGA_Compilation_Data` — already has `model` and `id` fields, could serve as the request type
- C: Create a dedicated `FPGARequest` type — most extensible, adds a new dataclass

---

## 4. Variadic Protocol Compatibility

**Source**: [BitstreamEvolutionProtocols.py:21-23](../../src/BitstreamEvolutionProtocols.py#L21-L23)

**Question**: Can a function with a fixed signature implement a protocol that accepts variadic arguments?

```
TODO: Check if a protocol *populations:Population can be implemented by a function with no such variable.
i.e. can val(p:int) match the type of vals(p:int, *populations:Population)?
```

**Context**: `GenerateInitialPopulation` (singular) and `GenerateInitialPopulations` (plural, used in `Evolution`) differ in that the plural version returns `list[Population]`. The question was about whether a no-population-arg function could satisfy the variadic version.

**Answer**: No — Python's Protocol structural subtyping does not allow this. A function `f(p: int)` does NOT satisfy `Callable[[int, *Population], ...]`. The `GenerateSinglePopulationWrapper` adapter exists specifically to bridge this gap.

**Status**: Question is answered, but the comment should be updated or removed.

---

## 5. Diversity Metric

**Source**: [Evolution.py:53](../../src/Evolution.py#L53)

**Question**: How should population diversity be calculated?

**Current state**: `PlotDataRecorder.record_generation()` accepts a `diversity: float` parameter, but `Evolution.run()` always passes `0` with a `# TODO: calculate diversity` comment.

**Options**:
- A: Hamming distance — mean pairwise bit-distance across all Individual bitstreams
- B: Fitness variance — standard deviation of fitness values in the population
- C: Unique phenotypes — fraction of distinct bitstreams in the population

---

## 6. Python 3.12 `Self` Type

**Source**: [BitstreamEvolutionProtocols.py:56-59](../../src/BitstreamEvolutionProtocols.py#L56-L59)

**Current state**:
```python
# TODO: Replace this with Self if update to python 3.12
F = TypeVar('F', bound='Fitness')
```

The `Fitness` protocol uses `F` to express that comparison operators must compare to the same type (not just any `Fitness`). In Python 3.12+, `Self` handles this more cleanly.

**Resolution**: When the project upgrades to Python 3.12+, replace `F = TypeVar('F', bound='Fitness')` with `from typing import Self` and update the `Fitness` protocol methods.