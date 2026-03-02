# Architectural Patterns

## Protocol-Based Design

The codebase uses Python's `Protocol` classes (structural subtyping) rather than abstract base classes for most interfaces. This enables duck typing while maintaining type safety.

**Pattern location**: [BitstreamEvolutionProtocols.py:33-248](../src/BitstreamEvolutionProtocols.py#L33-L248)

**Key protocols**:
- `GenDataFactory` - Controls evolution loop termination
- `Circuit` - Hardware circuit compilation interface
- `CircuitFactory` - Converts individuals to circuits
- `Reproducer` - Creates next generation
- `GenerateInitialPopulation` - Population initialization
- `EvaluatePopulationFitness` - Fitness calculation
- `GenerateMeasurements` - Creates measurement requests
- `Hardware` - Async FPGA communication

**Usage**: Protocols are callable (use `__call__`) rather than named methods, enabling `functools.partial` for dependency injection.

```python
# Protocol defines callable interface
class GenDataFactory(Protocol):
    def __call__(self, gen_data: GenData|None) -> GenData|None: ...

# Can use functools.partial for configuration
initial_pop = ft.partial(TrivialGenerateInitialPopulation,
                         population_size=100, random=Random())
```

## Constructor-Based Dependency Injection

All major components receive dependencies through constructors, enabling testability and flexibility.

**Pattern location**: [Evolution.py:17-31](../src/Evolution.py#L17-L31)

```python
class Evolution:
    def __init__(self, gen_data_factory: GenDataFactory,
                 circuit_factory: CircuitFactory,
                 reproduce: Reproducer, ...):
```

**Testing benefit**: Inject mocks via constructor
```python
# From test_TrivialImplementation.py
evolution = TrivialEvolution(
    generation_data_factory=gen_data_factory,
    reproducer=reproducer,
    generate_intial_population=initial_pop
)
```

## Strategy Pattern

Behavior is swapped via strategy objects injected at construction time.

**Post-construction strategies** ([PopulationInitialization.py:36-97](../src/Population/PopulationInitialization.py#L36-L97)):
- `NoPostConstructionStrategy` - Clone seed (no modification)
- `MutateOncePostConstructionStrategy` - Clone then mutate
- `RandomizeBitstreamPostConstructionStrategy` - Full randomization

**Fitness evaluation strategies** ([EvaluateFitness/](../src/EvaluateFitness/)):
- `EvalPulseCountFitness` - Counts oscillations
- `EvalVarMaxFitness` - Measures variance

**Usage**:
```python
population_gen = GenerateBitstreamPopulation(
    post_construction_strategy=RandomizeBitstreamPostConstructionStrategy(),
    randomization_strategy=NoRandomizationStrategy(),
    ...
)
```

## Result Type for Error Handling

Uses `returns.result.Result[T, Exception]` instead of exceptions for compile and measurement operations.

**Pattern locations**:
- [BitstreamEvolutionProtocols.py:101-108](../src/BitstreamEvolutionProtocols.py#L101-L108) - Circuit.compile signature
- [FileBasedCircuit.py:57-74](../src/Circuit/FileBasedCircuit.py#L57-L74) - Returns `Success(None)` or `Failure(Exception)`
- [Microcontroller.py:27-45](../src/Hardware/Microcontroller.py#L27-L45) - Wraps results in Success/Failure

**Checking results**:
```python
from returns.result import Success
if isinstance(m.result, Success):
    data = m.result.unwrap()
else:
    err = m.result.failure()
```

## Wrapper/Adapter Pattern

Adapters convert between singular and plural interfaces.

**Pattern location**: [PopulationInitialization.py:24-34](../src/Population/PopulationInitialization.py#L24-L34)

```python
class GenerateSinglePopulationWrapper:
    """Wraps GenerateInitialPopulation (singular) to match
    GenerateInitialPopulations (plural) protocol"""
    def __init__(self, gen_func: GenerateInitialPopulation):
        self.__gen_func = gen_func
    def generate(self) -> list[Population]:
        return [self.__gen_func()]
```

## Generic Measurement Class

`Measurement` is generic over circuit type and measurement result type.

**Pattern location**: [BitstreamEvolutionProtocols.py:202-232](../src/BitstreamEvolutionProtocols.py#L202-L232)

```python
C = TypeVar("C", bound=Circuit)
M = TypeVar("M", bound=Any)

class Measurement(Generic[C, M]):
    def __init__(self, FPGA_request: str, data_request: DataRequest,
                 circuit_to_measure: Circuit, num_samples: int):
        self.result: Result[M, Exception] = Failure(MeasurementNotTaken(...))
```

## Async Hardware Operations

Hardware communication uses Python's `asyncio` for concurrent FPGA operations.

**Pattern location**: [Evolution.py:41-42](../src/Evolution.py#L41-L42)

```python
tasks = [self.__hardware.request_measurement(m) for m in measurements]
results = asyncio.run(asyncio.gather(*tasks))
```

**Hardware protocol**: [BitstreamEvolutionProtocols.py:242-248](../src/BitstreamEvolutionProtocols.py#L242-L248)
```python
class Hardware(Protocol):
    async def request_measurement(self, measurement: Measurement) -> Measurement: ...
```

## Population Invariants

`Population` enforces uniqueness of individuals at construction time.

**Pattern location**: [BitstreamEvolutionProtocols.py:121-131](../src/BitstreamEvolutionProtocols.py#L121-L131)

```python
def __init__(self, individuals: Iterable[Individual], fitnesses: ...):
    if len(set(ind)) != len(ind):
        raise ValueError("There are duplicate individuals...")
```

## Memory-Mapped File Access

`FileBasedCircuit` uses `mmap` for efficient hardware file manipulation.

**Pattern location**: [FileBasedCircuit.py:50-52](../src/Circuit/FileBasedCircuit.py#L50-L52)

```python
hardware_file = open(self.__hardware_filepath, "r+")
self._hardware_file = mmap(hardware_file.fileno(), 0)
```

## Per-Generation Stateful Fitness Evaluators

`EvalVarMaxFitness` (and potentially future evaluators) maintain state across the individuals within a single generation. This is intentional design for tracking the best result to record to `PlotDataRecorder`.

**Pattern location**: [EvaluateFitness/EvalVarMaxFitness.py](../src/EvaluateFitness/EvalVarMaxFitness.py)

**State held**:
- `__best_waveform` / `__best_waveform_fit` — the best waveform seen so far this generation (reset by `start_eval()`)
- `__epoch` — generation counter, incremented by `end_eval()`

**Lifecycle** (called by `EvaluateFitness.evaluate()`):
```python
evaluator.start_eval()           # resets best_waveform for this generation
for each measurement:
    evaluator.calculate_success(data, index, src_pop)  # updates best_waveform if better
evaluator.end_eval()             # records best_waveform heatmap, increments epoch
```

**Why this is intentional**: `PlotDataRecorder.record_waveform_heatmap()` takes an epoch number and the best waveform for that epoch. The evaluator tracks the best to hand off at `end_eval()`.

**Limitation**: The epoch counter is implicit — it increments automatically on each `end_eval()` call. If `end_eval()` is called extra times (e.g., during testing or after an error), the epoch counter drifts.

**Proposed alternative**: Pass the epoch number explicitly to `start_eval(epoch: int)` and remove the internal `__epoch` counter. The caller (e.g., `Evolution.run()`) already tracks the generation number via `GenData.generation_number`, so this information is available:

```python
# Current
evaluator.start_eval()
...
evaluator.end_eval()  # internally increments self.__epoch

# Proposed
evaluator.start_eval(epoch=gen_data.generation_number)
...
evaluator.end_eval()  # uses epoch passed in, no internal counter
```

This would make the evaluator fully stateless between generations (only state is within one generation), eliminating the drift risk.

## Testing Conventions

**Mock pattern**: Use `spec=` parameter to enforce protocol interface
```python
from unittest.mock import Mock
ckt = Mock(spec=FileBasedCircuit)
plot_data_recorder = Mock(spec=PlotDataRecorder)
```

**Fixture pattern**: Use pytest fixtures for reusable test data
```python
@pytest.fixture
def FPGA_compilation_data():
    yield FPGA_Compilation_Data(FPGA_Model.ICE40, "randomID")
```

**Parametrized tests**: Test multiple inputs systematically
```python
@pytest.mark.parametrize("size", [1, 2, 3, 6, 10, 100, 1000])
def test_population_size(size):
    ...
```
