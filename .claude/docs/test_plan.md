# Test Plan: Interface Validation

This test plan focuses on validating that all protocol interfaces in `src/` are correctly implemented and used throughout the codebase.

## Current Test Coverage Summary

| Module | Test File | Coverage Status |
|--------|-----------|-----------------|
| BitstreamEvolutionProtocols | test_BitstreamEvolutionProtocols.py | Partial - GenDataIncrementer, Population basics |
| Population | test_population.py | Partial - set_fitness, sort, unevaluated |
| BitstreamIndividual | test_BitstreamIndividual.py | Good - randomize, mutate, crossover |
| PopulationInitialization | test_GenBitstreamPopulation.py | Good - strategies tested |
| FileBasedCircuitFactory | test_FileCircuitFactory.py | Basic - creates circuits |
| GenerateMeasurements | test_GenerateMeasurements.py | Basic - SimpleGenerateMeasurements |
| EvaluateFitness | test_FitnessEval.py | Basic - VarMax, PulseCount |
| TrivialImplementation | test_TrivialImplementation.py | Comprehensive reference |
| Circuit (FileBasedCircuit) | - | **NOT TESTED** |
| Hardware (Microcontroller) | - | **NOT TESTED** |
| Evolution | - | Only via TrivialEvolution |
| Logger | - | **NOT TESTED** |
| PlotDataRecorder | - | **NOT TESTED** (only mocked) |

---

## Part 1: Protocol Interface Tests

### 1.1 GenDataFactory Protocol
**File**: [BitstreamEvolutionProtocols.py:33-42](src/BitstreamEvolutionProtocols.py#L33-L42)

**Current Tests**: test_BitstreamEvolutionProtocols.py (lines 7-70)
- ✅ Instantiation returns GenData with generation_number=0
- ✅ Increments generation_number correctly
- ✅ Returns None when max reached (loop termination)
- ✅ Full loop execution test

**Missing Tests**:
- [ ] **Edge case**: max_gen_num = 0 (should return None immediately after first call)
- [ ] **Edge case**: max_gen_num = 1 (single generation)
- [ ] **Type validation**: Verify return type is GenData|None

```python
# Suggested test
def test_GenDataIncrementer_ZeroGenerations():
    inc = GenDataIncrementer(0)
    result = inc(None)
    assert result is not None  # First call should return gen 0
    result = inc(result)
    assert result is None  # Second call should terminate
```

---

### 1.2 Fitness Protocol
**File**: [BitstreamEvolutionProtocols.py:57-73](src/BitstreamEvolutionProtocols.py#L57-L73)

**Current Tests**: None directly (implicitly tested via Population.sort)

**Missing Tests**:
- [ ] **Comparison operators**: Test that `float` satisfies Fitness protocol
- [ ] **Comparison operators**: Test that `int` satisfies Fitness protocol
- [ ] **Custom Fitness**: Create mock Fitness class and verify protocol compliance

```python
# Suggested tests
def test_float_satisfies_Fitness_protocol():
    """Verify float works as Fitness type in Population"""
    pop = Population([Mock(), Mock()], [1.5, 2.5])
    pop.sort(lambda x: x, reverse=True)
    assert list(pop)[0][1] == 2.5

def test_int_satisfies_Fitness_protocol():
    """Verify int works as Fitness type in Population"""
    pop = Population([Mock(), Mock()], [1, 2])
    pop.sort(lambda x: x, reverse=True)
    assert list(pop)[0][1] == 2
```

---

### 1.3 Individual Protocol
**File**: [BitstreamEvolutionProtocols.py:75-80](src/BitstreamEvolutionProtocols.py#L75-L80)

**Current Tests**: Indirectly via BitstreamIndividual tests

**Missing Tests**:
- [ ] **Protocol compliance**: Verify BitstreamIndividual satisfies Individual protocol
- [ ] **Any object as Individual**: Verify arbitrary objects can be used as Individuals

```python
# Suggested test
def test_any_object_satisfies_Individual_protocol():
    """Protocol defines nothing, so any object should work"""
    pop = Population([1, "string", object()], None)
    assert len(pop) == 3
```

---

### 1.4 Circuit Protocol
**File**: [BitstreamEvolutionProtocols.py:94-108](src/BitstreamEvolutionProtocols.py#L94-L108)

**Current Tests**: test_TrivialImplementation.py (TrivialCircuit tests)

**Missing Tests**:
- [ ] **compile() signature**: Returns `Result[None, Exception]`
- [ ] **compile() success case**: Returns `Success(None)`
- [ ] **compile() failure case**: Returns `Failure(Exception)` (not raises)
- [ ] **FileBasedCircuit.compile()**: Test with mock FPGA data

```python
# Suggested tests
def test_Circuit_compile_returns_Result():
    ckt = TrivialCircuit(10)
    fpga = FPGA_Compilation_Data(FPGA_Model.ICE40, "test-id")
    result = ckt.compile(fpga)
    assert isinstance(result, Result)

def test_Circuit_compile_never_raises():
    """Circuit.compile should return errors, not raise them"""
    # FileBasedCircuit with invalid template should return Failure, not raise
    pass  # Requires FileBasedCircuit mock setup
```

---

### 1.5 CircuitFactory Protocol
**File**: [BitstreamEvolutionProtocols.py:169-182](src/BitstreamEvolutionProtocols.py#L169-L182)

**Current Tests**:
- test_TrivialImplementation.py:61-75 (TrivialCircuitFactory)
- test_FileCircuitFactory.py:9-36 (FileBasedCircuitFactory)

**Missing Tests**:
- [ ] **Return type validation**: dict[Circuit, list[tuple[Population, Individual]]]
- [ ] **Multiple populations**: Factory handles list with multiple populations
- [ ] **Empty population**: Factory handles empty population list
- [ ] **Population-Individual tracking**: Verify returned dict correctly maps circuits to source populations/individuals

```python
# Suggested tests
def test_CircuitFactory_returns_correct_structure():
    pop = Population([TrivialCircuit(1), TrivialCircuit(2)], None)
    result = TrivialCircuitFactory(pop)

    for circuit, dependants in result.items():
        assert isinstance(dependants, list)
        for (source_pop, individual) in dependants:
            assert source_pop is pop
            assert individual in [i for i, _ in pop]

def test_CircuitFactory_handles_multiple_populations():
    pop1 = Population([TrivialCircuit(1)], None)
    pop2 = Population([TrivialCircuit(2)], None)
    # Need factory that accepts list[Population]
    pass
```

---

### 1.6 Reproducer Protocol
**File**: [BitstreamEvolutionProtocols.py:184-186](src/BitstreamEvolutionProtocols.py#L184-L186)

**Current Tests**: test_TrivialImplementation.py:162-206 (TrivialReproduceWithMutation)

**Missing Tests**:
- [ ] **Return type**: Returns Population (not modifies in place)
- [ ] **Input unchanged**: Original population is not modified
- [ ] **Population size**: Various strategies for population size changes
- [ ] **Fitness reset**: Returned population has None fitnesses

```python
# Suggested tests
def test_Reproducer_returns_new_population():
    original = Generate_Population_From_Iterable(range(10), fitnesses_discovered=True)
    original_individuals = [i for i, _ in original]

    result = TrivialReproduceWithMutation(original, Random())

    assert result is not original
    # Original should be unchanged
    assert [i for i, _ in original] == original_individuals

def test_Reproducer_returns_unevaluated_population():
    pop = Generate_Population_From_Iterable(range(10), fitnesses_discovered=True)
    result = TrivialReproduceWithMutation(pop, Random())

    for _, fitness in result:
        assert fitness is None
```

---

### 1.7 GenerateInitialPopulation Protocol
**File**: [BitstreamEvolutionProtocols.py:188-190](src/BitstreamEvolutionProtocols.py#L188-L190)

**Current Tests**: test_TrivialImplementation.py:80-158

**Missing Tests**:
- [ ] **Callable with no args**: Protocol requires `() -> Population`
- [ ] **functools.partial compatibility**: Verify works with partial application
- [ ] **GenerateBitstreamPopulation**: Test that it satisfies protocol via `.generate()`

```python
# Suggested tests
def test_GenerateInitialPopulation_callable_interface():
    """Protocol is Callable[[], Population]"""
    gen = ft.partial(TrivialGenerateInitialPopulation,
                     population_size=10, random=Random(),
                     min_fitness=0, max_fitness=100)

    # Should be callable with no arguments
    result = gen()
    assert isinstance(result, Population)
```

---

### 1.8 Population Class
**File**: [BitstreamEvolutionProtocols.py:110-166](src/BitstreamEvolutionProtocols.py#L110-L166)

**Current Tests**: test_population.py (3 tests)

**Missing Tests**:
- [ ] **Uniqueness constraint**: Duplicate individuals raise ValueError
- [ ] **Iteration**: `__iter__` returns (Individual, Fitness|None) tuples
- [ ] **Length**: `__len__` returns correct count
- [ ] **set_fitness()**: ValueError when individual not found
- [ ] **sort() with None fitness**: Raises TypeError
- [ ] **Fitness length mismatch**: Handled correctly (defaults to None)

```python
# Suggested tests
def test_Population_rejects_duplicate_individuals():
    ind = Mock()
    with pytest.raises(ValueError, match="duplicate"):
        Population([ind, ind], None)

def test_Population_set_fitness_raises_on_missing_individual():
    pop = Population([Mock()], None)
    missing = Mock()
    with pytest.raises(ValueError):
        pop.set_fitness(missing, 1.0)

def test_Population_sort_raises_on_unevaluated():
    pop = Population([Mock(), Mock()], [1.0, None])
    with pytest.raises(TypeError):
        pop.sort(lambda x: x, False)

def test_Population_iteration_yields_tuples():
    ind = Mock()
    pop = Population([ind], [1.0])
    for item in pop:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert item[0] is ind
        assert item[1] == 1.0
```

---

### 1.9 Measurement Class
**File**: [BitstreamEvolutionProtocols.py:192-232](src/BitstreamEvolutionProtocols.py#L192-L232)

**Current Tests**: Indirectly via test_FitnessEval.py, test_GenerateMeasurements.py

**Missing Tests**:
- [ ] **Initial state**: result is Failure(MeasurementNotTaken)
- [ ] **record_measurement_result() success**: Sets result to Success(value)
- [ ] **record_measurement_result() error**: Sets result to Failure(exception)
- [ ] **record_FPGA_used()**: Updates FPGA_used field
- [ ] **Generic types**: Verify C and M type parameters work correctly

```python
# Suggested tests
def test_Measurement_initial_result_is_failure():
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    from returns.result import Failure
    assert isinstance(m.result, Failure)

def test_Measurement_record_success():
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    m.record_measurement_result([1, 2, 3])

    from returns.result import Success
    assert isinstance(m.result, Success)
    assert m.result.unwrap() == [1, 2, 3]

def test_Measurement_record_error():
    ckt = Mock(spec=Circuit)
    m = Measurement("fpga", DataRequest.WAVEFORM, ckt, 1)

    err = Exception("test error")
    m.record_measurement_result(err)

    from returns.result import Failure
    assert isinstance(m.result, Failure)
```

---

### 1.10 EvaluatePopulationFitness Protocol
**File**: [BitstreamEvolutionProtocols.py:234-236](src/BitstreamEvolutionProtocols.py#L234-L236)

**Current Tests**: test_FitnessEval.py (2 tests)

**Missing Tests**:
- [ ] **In-place modification**: Population is modified, not returned
- [ ] **Measurement-to-fitness mapping**: Correct fitness assigned to correct individual
- [ ] **Error handling**: Measurements with Failure results handled gracefully
- [ ] **Multiple measurements**: All measurements processed

```python
# Suggested tests
def test_EvaluatePopulationFitness_modifies_in_place():
    pop = Population([Mock()], None)
    ckt = Mock()
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.record_measurement_result([0, 2])

    evaluator = EvaluateFitness(EvalVarMaxFitness(Mock(spec=PlotDataRecorder)))
    evaluator.evaluate(pop, [measure])

    # Population should be modified
    assert pop.population_list[0][1] is not None

def test_EvaluatePopulationFitness_handles_measurement_errors():
    pop = Population([Mock()], None)
    ckt = Mock()
    measure = Measurement('fpga', DataRequest.WAVEFORM, ckt, 1)
    measure.record_measurement_result(Exception("Hardware failure"))

    evaluator = EvaluateFitness(EvalVarMaxFitness(Mock(spec=PlotDataRecorder)))
    evaluator.evaluate(pop, [measure])

    # Should assign error fitness (typically 0)
    assert pop.population_list[0][1] == 0
```

---

### 1.11 GenerateMeasurements Protocol
**File**: [BitstreamEvolutionProtocols.py:238-240](src/BitstreamEvolutionProtocols.py#L238-L240)

**Current Tests**: test_GenerateMeasurements.py (1 test), test_TrivialImplementation.py:231-253

**Missing Tests**:
- [ ] **Return type**: dict[Measurement, list[tuple[Population, Individual]]]
- [ ] **Factory integration**: Correctly uses CircuitFactory
- [ ] **Multiple populations**: Handles list of populations
- [ ] **Empty populations**: Handles empty input gracefully

```python
# Suggested tests
def test_GenerateMeasurements_return_structure():
    gen_meas = SimpleGenerateMeasurements('fpga', DataRequest.WAVEFORM, 1)
    factory = MockCircuitFactory()
    pop = Population([MockIndividual(1), MockIndividual(2)], None)

    result = gen_meas.generate(factory.generate, [pop])

    assert isinstance(result, dict)
    for measurement, dependants in result.items():
        assert isinstance(measurement, Measurement)
        assert isinstance(dependants, list)
        for (source_pop, individual) in dependants:
            assert source_pop is pop
```

---

### 1.12 Hardware Protocol
**File**: [BitstreamEvolutionProtocols.py:242-248](src/BitstreamEvolutionProtocols.py#L242-L248)

**Current Tests**: test_TrivialImplementation.py:266-275 (TrivialHardware)

**Missing Tests**:
- [ ] **Async interface**: request_measurement is async
- [ ] **Measurement return**: Returns the same Measurement object with result populated
- [ ] **get_available_FPGAs()**: Returns list of FPGA identifiers
- [ ] **Microcontroller**: Unit tests for real implementation (with mocked serial)

```python
# Suggested tests
@pytest.mark.asyncio
async def test_Hardware_request_measurement_is_async():
    hw = TrivialHardware(["FPGA1"])
    ckt = TrivialCircuit(10)
    measure = Trivial_Meas("fpga", DataRequest.NONE, ckt, 1)

    result = await hw.request_measurement(measure)

    assert result is measure
    assert result.FPGA_used is not None

def test_Hardware_get_available_FPGAs():
    hw = TrivialHardware(["FPGA1", "FPGA2"])
    fpgas = hw.get_available_FPGAs()

    assert isinstance(fpgas, list)
    assert len(fpgas) >= 1
```

---

### 1.13 FitnessEvaluator Protocol (Internal)
**File**: [EvaluateFitness/EvaluateFitness.py:6-13](src/EvaluateFitness/EvaluateFitness.py#L6-L13)

**Current Tests**: Indirectly via test_FitnessEval.py

**Missing Tests**:
- [ ] **start_eval() called**: Verify called before evaluation
- [ ] **end_eval() called**: Verify called after evaluation
- [ ] **calculate_success()**: Returns Fitness value
- [ ] **calculate_error()**: Returns Fitness value for error case

```python
# Suggested tests
def test_FitnessEvaluator_lifecycle():
    evaluator = Mock(spec=FitnessEvaluator)
    evaluator.calculate_success.return_value = 1.0

    ef = EvaluateFitness(evaluator)
    pop = Population([Mock()], None)
    measure = Measurement('fpga', DataRequest.WAVEFORM, Mock(), 1)
    measure.record_measurement_result([1, 2])

    ef.evaluate(pop, [measure])

    evaluator.start_eval.assert_called_once()
    evaluator.calculate_success.assert_called_once()
    evaluator.end_eval.assert_called_once()
```

---

### 1.14 PostConstructionStrategy Protocol
**File**: [PopulationInitialization.py:36-38](src/Population/PopulationInitialization.py#L36-L38)

**Current Tests**: test_GenBitstreamPopulation.py (3 tests)

**Missing Tests**:
- [ ] **Return value**: Returns the modified individual (may be same object)
- [ ] **NoPostConstructionStrategy**: Returns individual unchanged
- [ ] **MutateOncePostConstructionStrategy**: Calls mutate() once
- [ ] **RandomizeBitstreamPostConstructionStrategy**: Calls randomize()

```python
# Suggested tests
def test_PostConstructionStrategy_returns_individual():
    strategy = NoPostConstructionStrategy()
    ind = BitstreamIndividual(10, Random(), 0.5)

    result = strategy.run(ind)

    assert result is ind

def test_MutateOncePostConstructionStrategy_calls_mutate():
    strategy = MutateOncePostConstructionStrategy()
    ind = Mock(spec=BitstreamIndividual)

    strategy.run(ind)

    ind.mutate.assert_called_once()
```

---

## Part 2: Integration Tests

### 2.1 Evolution Pipeline Integration
**Missing**: End-to-end test with all real components (not mocks)

```python
@pytest.mark.short
def test_evolution_pipeline_integration():
    """Full evolution run with real components"""
    rand = Random(42)  # Deterministic seed

    gen_data_factory = GenDataIncrementer(5)  # 5 generations

    initial_pop = ft.partial(TrivialGenerateInitialPopulation,
                             population_size=10, random=rand,
                             min_fitness=0, max_fitness=100)

    reproducer = ft.partial(TrivialReproduceWithMutation, random=rand)

    evolution = TrivialEvolution(
        generation_data_factory=gen_data_factory,
        reproducer=reproducer,
        generate_intial_population=initial_pop
    )

    # Should complete without error
    evolution.run()
```

### 2.2 CircuitFactory to Measurement Pipeline
**Missing**: Test that CircuitFactory output correctly feeds into GenerateMeasurements

```python
def test_circuit_factory_to_measurements_integration():
    pop = Population([TrivialCircuit(1), TrivialCircuit(2)], None)

    circuits = TrivialCircuitFactory(pop)
    measurements = TrivialGenerateMeasurements(TrivialCircuitFactory, pop)

    # Each circuit should have exactly one measurement
    assert len(measurements) == len(circuits)

    # Each measurement should reference a circuit from the factory
    for measurement in measurements:
        assert measurement.circuit in circuits
```

### 2.3 Measurement to Fitness Pipeline
**Missing**: Test that measurements flow correctly through fitness evaluation

```python
def test_measurement_to_fitness_integration():
    # Setup
    ind1, ind2 = TrivialCircuit(10), TrivialCircuit(20)
    pop = Population([ind1, ind2], None)

    # Generate measurements
    measurements = TrivialGenerateMeasurements(TrivialCircuitFactory, pop)

    # Evaluate measurements (fake hardware)
    FakeHardwareTrivialEvaluateMeasurements(measurements.keys())

    # Apply to population
    TrivialEvaluatePopulationFitness(pop, measurements)

    # Verify fitnesses assigned correctly
    for ind, fit in pop:
        assert fit == ind.inherent_fitness
```

---

## Part 3: Concrete Implementation Tests

### 3.1 FileBasedCircuit
**File**: [Circuit/FileBasedCircuit.py](src/Circuit/FileBasedCircuit.py)
**Status**: NOT TESTED

**Required Tests**:
- [ ] `__init__`: Creates ASC file from template
- [ ] `compile()`: Calls icepack, uploads with iceprog, returns Result
- [ ] `get_bitstream()`: Returns list[bool] of correct length
- [ ] `set_bitstream()`: Modifies hardware file correctly
- [ ] `copy_from()`: Copies hardware file from another circuit
- [ ] `get_file_attribute()`/`set_file_attribute()`: Attribute storage works

### 3.2 BitstreamIndividual
**File**: [Individual/BitstreamIndividual.py](src/Individual/BitstreamIndividual.py)
**Status**: Partially tested in test_BitstreamIndividual.py

**Missing Tests**:
- [ ] `__init__`: Creates individual with correct bitstream size
- [ ] `copy_from()`: Deep copies bitstream from another individual
- [ ] Edge cases for crossover (crossover_point at 0, at end)

### 3.3 Microcontroller
**File**: [Hardware/Microcontroller.py](src/Hardware/Microcontroller.py)
**Status**: NOT TESTED

**Required Tests** (with mocked serial):
- [ ] `__init__`: Initializes serial connection
- [ ] `request_measurement()`: WAVEFORM request flow
- [ ] `request_measurement()`: OSCILLATIONS request flow
- [ ] `measure_signal()`: Parses MCU response correctly
- [ ] `measure_pulses()`: Handles multiple samples
- [ ] Error handling: Timeout recovery

### 3.4 EvalPulseCountFitness
**File**: [EvaluateFitness/EvalPulseCountFitness.py](src/EvaluateFitness/EvalPulseCountFitness.py)
**Status**: 1 test in test_FitnessEval.py

**Missing Tests**:
- [ ] Perfect match (pulses == target): Returns 1.0
- [ ] Zero pulses: Returns 0.0
- [ ] Multiple samples: Uses last sample
- [ ] Negative difference handling

### 3.5 EvalVarMaxFitness
**File**: [EvaluateFitness/EvalVarMaxFitness.py](src/EvaluateFitness/EvalVarMaxFitness.py)
**Status**: 1 test in test_FitnessEval.py

**Missing Tests**:
- [ ] Constant data (variance = 0)
- [ ] High variance data
- [ ] Empty data handling

### 3.6 PlotDataRecorder
**File**: [PlotDataRecorder.py](src/PlotDataRecorder.py)
**Status**: NOT TESTED (only used as Mock in other tests)

**Testing approach**: Use `pytest`'s `tmp_path` fixture plus `monkeypatch.chdir()` to redirect all
hard-coded `workspace/` path opens to a temporary directory.

**Required Tests**:
- [ ] `record_waveform(waveform)`: Writes correct CSV format (`i, value\n`) to `waveformlivedata.log`
- [ ] `record_generation(fits, epoch, diversity)`: Appends correct line format to `bestlivedata.log` and `violinlivedata.log`
- [ ] `record_generation` best/worst/avg calculation: Verifies sorted order and sum
- [ ] `record_waveform_heatmap(epoch, waveform)`: Appends `epoch:v1,v2,...\n` to `heatmaplivedata.log`
- [ ] `record_all_live_data(index, value, src_pop)`: Writes/updates correct line in `alllivedata.log`
- [ ] `record_all_live_data` index beyond current length: Pads file with empty lines first
- [ ] `reset()`: Resets `__ovr_best_fit` so subsequent `record_generation` uses new best

```python
# Suggested fixture
@pytest.fixture
def plot_recorder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "workspace").mkdir()
    return PlotDataRecorder()
```

### 3.7 FullySimCircuit
**File**: [Circuit/FullySimCircuit.py](src/Circuit/FullySimCircuit.py)
**Status**: NOT TESTED — **currently un-instantiable (broken)**

**Issue**: `FullySimCircuit` extends `Circuit` (ABC) but does not implement the `@abstractmethod compile()`.
This means `FullySimCircuit` **cannot be instantiated** with current code. It also uses `rand.integers()`
(NumPy's random API) rather than Python's `random.Random`.

**History**: This is legacy code predating the current protocol-based architecture. It was built for a
simulation-only evolution mode where circuits ran in-memory instead of on hardware.

**Recommendation**: **Do not add tests until the class is brought up to date.** Before testing:
1. Decide if `FullySimCircuit` is still needed (simulation-only use case)
2. If yes: implement `compile()` (probably returning `Success(None)`) and fix the `rand.integers()` call
3. If no: delete the file

### 3.8 Logger
**File**: [Logger.py](src/Logger.py)
**Status**: NOT TESTED — **testing deferred, redesign needed first**

**Issue**: `Logger` has multiple blocking problems (see [logger_broken_methods.md](../todos/logger_broken_methods.md)):
- `log_generation()` calls non-existent `Population` methods — crashes at runtime
- `__init__` hard-codes `workspace/` paths relative to CWD
- `__init_monitor()` launches `gnome-terminal` (Linux-only subprocess)

**Recommendation**: **Defer testing until Logger is redesigned.** Specifically:
1. Fix or remove `log_generation()` (see options in logger_broken_methods.md)
2. Make workspace path configurable (not hard-coded)
3. Consider migrating to Python's built-in `logging` module (TODO already in source)

After redesign, the simple log methods (`log_event`, `log_info`, `log_warning`, etc.) are straightforward
to test by capturing stdout/stderr with `capsys`.

---

## Part 4: Test Markers

Use pytest markers to categorize tests by execution time:

```python
@pytest.mark.immediate  # <10 seconds (default)
@pytest.mark.short      # <60 seconds
@pytest.mark.long       # >1 minute
```

**Recommendations**:
- All protocol interface tests: `immediate`
- Integration tests: `short`
- FileBasedCircuit tests (file I/O): `short`
- Full evolution runs: `long`

---

## Execution Plan

### Phase 1: Protocol Compliance (Priority: High)
1. Population class tests (1.8)
2. Measurement class tests (1.9)
3. GenDataFactory edge cases (1.1)
4. Fitness protocol tests (1.2)

### Phase 2: Interface Integration (Priority: High)
1. CircuitFactory return structure (1.5)
2. GenerateMeasurements integration (1.11)
3. EvaluatePopulationFitness behavior (1.10)
4. Reproducer behavior (1.6)

### Phase 3: Concrete Implementations (Priority: Medium)
1. FileBasedCircuit unit tests (3.1)
2. Microcontroller with mocked serial (3.3)
3. EvalPulseCountFitness edge cases (3.4)

### Phase 4: End-to-End (Priority: Medium)
1. Evolution pipeline integration (2.1)
2. Measurement pipeline integration (2.2, 2.3)

---

## Running the Tests

```bash
# Run all interface tests
pytest test/ -m "immediate"

# Run with coverage
pytest test/ --cov=src --cov-report=html

# Run specific test file
pytest test/test_BitstreamEvolutionProtocols.py -v

# Run tests matching pattern
pytest test/ -k "Population" -v
```
