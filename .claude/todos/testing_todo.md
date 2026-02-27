# Testing TODO

Progress tracker for implementing tests from [test_plan.md](../docs/test_plan.md).

**Last Updated**: 2026-02-27

---

## Phase 1: Protocol Compliance (Priority: High)

### 1.8 Population Class
- [x] `test_Population_rejects_duplicate_individuals` - Uniqueness constraint (pre-existing in test_population.py)
- [x] `test_Population_set_fitness_raises_on_missing_individual` - ValueError handling
- [x] `test_Population_sort_raises_on_unevaluated` - TypeError when fitness is None
- [x] `test_Population_iteration_yields_tuples` - Correct iteration format
- [x] `test_Population_length` - `__len__` returns correct count
- [x] `test_Population_fitness_length_mismatch` - Defaults to None when mismatch

### 1.9 Measurement Class
- [x] `test_Measurement_initial_result_is_failure` - Starts as Failure(MeasurementNotTaken)
- [x] `test_Measurement_record_success` - Sets result to Success(value)
- [x] `test_Measurement_record_error` - Sets result to Failure(exception)
- [x] `test_Measurement_record_FPGA_used` - Updates FPGA_used field
- [x] `test_Measurement_generic_types` - C and M type parameters work
- [x] `test_Measurement_stores_constructor_args` - Constructor args stored as attributes

### 1.1 GenDataFactory Edge Cases
- [x] `test_GenDataIncrementer_ZeroGenerations` - max_gen_num = 0
- [x] `test_GenDataIncrementer_SingleGeneration` - max_gen_num = 1
- [x] `test_GenDataIncrementer_return_type_validation` - Returns GenData|None

### 1.2 Fitness Protocol
- [x] `test_float_satisfies_Fitness_protocol` - float works as Fitness
- [x] `test_int_satisfies_Fitness_protocol` - int works as Fitness
- [x] `test_custom_Fitness_class` - Custom class with comparison operators

---

## Phase 2: Interface Integration (Priority: High)

### 1.5 CircuitFactory Protocol
- [x] `test_CircuitFactory_returns_correct_structure` - dict[Circuit, list[tuple[Population, Individual]]]
- [x] `test_CircuitFactory_handles_empty_population` - Empty population list
- [x] `test_CircuitFactory_population_individual_tracking` - Correct mapping

### 1.11 GenerateMeasurements Protocol
- [x] `test_GenerateMeasurements_return_structure` - Correct return type
- [x] `test_GenerateMeasurements_factory_integration` - Correctly uses CircuitFactory
- [x] `test_GenerateMeasurements_multiple_populations` - Handles list of populations
- [x] `test_GenerateMeasurements_empty_input` - Handles empty input

### 1.10 EvaluatePopulationFitness Protocol
- [x] `test_EvaluatePopulationFitness_modifies_in_place` - Population modified, not returned
- [x] `test_EvaluatePopulationFitness_measurement_mapping` - Correct fitness to individual
- [x] `test_EvaluatePopulationFitness_handles_errors` - Measurement Failure handling
- [x] `test_EvaluatePopulationFitness_multiple_measurements` - All processed

### 1.6 Reproducer Protocol
- [x] `test_Reproducer_returns_new_population` - Returns new Population object
- [x] `test_Reproducer_input_unchanged` - Original population not modified
- [x] `test_Reproducer_returns_unevaluated_population` - Fitnesses are None

### 1.13 FitnessEvaluator Protocol
- [x] `test_FitnessEvaluator_lifecycle` - start_eval/end_eval called
- [x] `test_FitnessEvaluator_calculate_success_called` - For successful measurements
- [x] `test_FitnessEvaluator_calculate_error_called` - For failed measurements

---

## Phase 3: Concrete Implementations (Priority: Medium)

### 3.1 FileBasedCircuit
- [x] `test_FileBasedCircuit_init_creates_asc_file` - Creates from template (skipped if seed-hardware.asc missing)
- [x] `test_FileBasedCircuit_get_bitstream` - Returns list[bool]
- [x] `test_FileBasedCircuit_set_bitstream` - Modifies hardware file
- [x] `test_FileBasedCircuit_get_set_roundtrip` - Roundtrip bitstream
- [x] `test_FileBasedCircuit_copy_from` - Copies from another circuit
- [x] `test_FileBasedCircuit_get_file_attribute_default` - Default attribute value
- [x] `test_FileBasedCircuit_set_and_get_file_attribute` - Attribute storage

### 3.3 Microcontroller (mocked serial)
- [x] `test_Microcontroller_init` - Initializes serial connection
- [x] `test_Microcontroller_get_available_FPGAs` - Returns configured FPGA
- [x] `test_Microcontroller_request_measurement_waveform` - WAVEFORM flow
- [x] `test_Microcontroller_request_measurement_oscillations` - OSCILLATIONS flow
- [x] `test_Microcontroller_measure_signal` - Parses MCU response
- [x] `test_Microcontroller_measure_pulses` - Multiple samples
- [x] `test_Microcontroller_timeout_recovery` - Error handling

### 3.4 EvalPulseCountFitness
- [x] `test_EvalPulseCountFitness_perfect_match` - Returns 1.0
- [x] `test_EvalPulseCountFitness_zero_pulses` - Returns 0.0
- [x] `test_EvalPulseCountFitness_multiple_samples` - Uses min fitness
- [x] `test_EvalPulseCountFitness_negative_difference` - Handled correctly
- [x] `test_EvalPulseCountFitness_error_returns_zero` - Returns 0

### 3.5 EvalVarMaxFitness
- [x] `test_EvalVarMaxFitness_constant_data` - Variance = 0
- [x] `test_EvalVarMaxFitness_high_variance` - High variance data
- [x] `test_EvalVarMaxFitness_single_element` - Single element
- [x] `test_EvalVarMaxFitness_error_returns_zero` - Returns 0
- [x] `test_EvalVarMaxFitness_start_end_eval_lifecycle` - Epoch tracking

### 3.2 BitstreamIndividual (additional)
- [x] `test_BitstreamIndividual_init_bitstream_size` - Correct size
- [x] `test_BitstreamIndividual_copy_from` - Deep copy
- [x] `test_BitstreamIndividual_crossover_at_zero` - Edge case
- [x] `test_BitstreamIndividual_crossover_at_end` - Edge case

---

## Phase 4: End-to-End Integration (Priority: Medium)

### 2.1 Evolution Pipeline
- [x] `test_evolution_pipeline_integration` - Full run with real components

### 2.2 CircuitFactory to Measurement
- [x] `test_circuit_factory_to_measurements_integration` - Factory -> Measurements

### 2.3 Measurement to Fitness
- [x] `test_measurement_to_fitness_integration` - Measurements -> Fitness evaluation
- [x] `test_measurement_to_fitness_with_unevaluated` - Unevaluated default fitness
- [x] `test_full_trivial_pipeline_single_generation` - Full single generation cycle

---

## Known Issues

### `result` vs `returns` library incompatibility
- `Measurement` (BitstreamEvolutionProtocols.py) uses `returns.result.Success/Failure`
- `EvaluateFitness` (EvaluateFitness.py) uses `result.is_ok()` which expects `result.Ok/Err`
- Tests that go through `EvaluateFitness.evaluate()` must set `measurement.result = Ok(data)` directly
- Pre-existing tests `test_varmax_fitness` and `test_pulse_fitness` were affected; fixed with `result.Ok()`
- Three pre-existing test failures remain unrelated to this test plan:
  - `test_file_based_circuit_factory` - relative path `data/seed-hardware.asc` not found
  - `test_TrivialCircuit_ImplementsCompile` - `result`/`returns` pattern match incompatibility
  - `test_TrivialHardware_evaluates_measurements` - `asyncio.create_task` without event loop

### `pyproject.toml` configuration fix
- Renamed `[tool.pytest.marker_groups]` to `[tool.pytest_marker_groups]` to resolve pytest conflict
  between `[tool.pytest]` (native TOML) and `[tool.pytest.ini_options]` (INI format)
- Updated `conftest.py` to read from the new key

---

## Test File Mapping

| Test File | Tests Added | Phase |
|-----------|------------|-------|
| test/test_population.py | 5 new tests | Phase 1 |
| test/test_Measurement.py | 6 new tests (new file) | Phase 1 |
| test/test_BitstreamEvolutionProtocols.py | 6 new tests | Phase 1 |
| test/test_interface_integration.py | 17 new tests (new file) | Phase 2 |
| test/test_FitnessEval.py | 11 new tests + 2 fixed | Phase 3 |
| test/test_BitstreamIndividual.py | 4 new tests | Phase 3 |
| test/test_FileBasedCircuit.py | 7 new tests (new file) | Phase 3 |
| test/test_Microcontroller.py | 7 new tests (new file) | Phase 3 |
| test/test_end_to_end.py | 5 new tests (new file) | Phase 4 |

**Total: 68 new tests across 9 files**

---

## Notes

- All new tests use `@pytest.mark.immediate` (default) unless marked otherwise
- Integration evolution pipeline test uses `@pytest.mark.short`
- FileBasedCircuit tests are `skipIf` seed-hardware.asc is not at expected path
- Microcontroller tests mock `serial.Serial` to avoid hardware dependency
- Mock external dependencies (serial, file I/O for hardware tests)
- Reference [test_plan.md](../docs/test_plan.md) for detailed test specifications