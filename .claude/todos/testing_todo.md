# Testing TODO

Progress tracker for implementing tests from [test_plan.md](../docs/test_plan.md).

**Last Updated**: 2026-01-14

---

## Phase 1: Protocol Compliance (Priority: High)

### 1.8 Population Class
- [ ] `test_Population_rejects_duplicate_individuals` - Uniqueness constraint
- [ ] `test_Population_set_fitness_raises_on_missing_individual` - ValueError handling
- [ ] `test_Population_sort_raises_on_unevaluated` - TypeError when fitness is None
- [ ] `test_Population_iteration_yields_tuples` - Correct iteration format
- [ ] `test_Population_length` - `__len__` returns correct count
- [ ] `test_Population_fitness_length_mismatch` - Defaults to None when mismatch

### 1.9 Measurement Class
- [ ] `test_Measurement_initial_result_is_failure` - Starts as Failure(MeasurementNotTaken)
- [ ] `test_Measurement_record_success` - Sets result to Success(value)
- [ ] `test_Measurement_record_error` - Sets result to Failure(exception)
- [ ] `test_Measurement_record_FPGA_used` - Updates FPGA_used field
- [ ] `test_Measurement_generic_types` - C and M type parameters work

### 1.1 GenDataFactory Edge Cases
- [ ] `test_GenDataIncrementer_ZeroGenerations` - max_gen_num = 0
- [ ] `test_GenDataIncrementer_SingleGeneration` - max_gen_num = 1
- [ ] `test_GenDataIncrementer_return_type_validation` - Returns GenData|None

### 1.2 Fitness Protocol
- [ ] `test_float_satisfies_Fitness_protocol` - float works as Fitness
- [ ] `test_int_satisfies_Fitness_protocol` - int works as Fitness
- [ ] `test_custom_Fitness_class` - Custom class with comparison operators

---

## Phase 2: Interface Integration (Priority: High)

### 1.5 CircuitFactory Protocol
- [ ] `test_CircuitFactory_returns_correct_structure` - dict[Circuit, list[tuple[Population, Individual]]]
- [ ] `test_CircuitFactory_handles_multiple_populations` - list with multiple populations
- [ ] `test_CircuitFactory_handles_empty_population` - Empty population list
- [ ] `test_CircuitFactory_population_individual_tracking` - Correct mapping

### 1.11 GenerateMeasurements Protocol
- [ ] `test_GenerateMeasurements_return_structure` - Correct return type
- [ ] `test_GenerateMeasurements_factory_integration` - Correctly uses CircuitFactory
- [ ] `test_GenerateMeasurements_multiple_populations` - Handles list of populations
- [ ] `test_GenerateMeasurements_empty_input` - Handles empty input

### 1.10 EvaluatePopulationFitness Protocol
- [ ] `test_EvaluatePopulationFitness_modifies_in_place` - Population modified, not returned
- [ ] `test_EvaluatePopulationFitness_measurement_mapping` - Correct fitness to individual
- [ ] `test_EvaluatePopulationFitness_handles_errors` - Measurement Failure handling
- [ ] `test_EvaluatePopulationFitness_multiple_measurements` - All processed

### 1.6 Reproducer Protocol
- [ ] `test_Reproducer_returns_new_population` - Returns new Population object
- [ ] `test_Reproducer_input_unchanged` - Original population not modified
- [ ] `test_Reproducer_returns_unevaluated_population` - Fitnesses are None

### 1.13 FitnessEvaluator Protocol
- [ ] `test_FitnessEvaluator_lifecycle` - start_eval/end_eval called
- [ ] `test_FitnessEvaluator_calculate_success_called` - For successful measurements
- [ ] `test_FitnessEvaluator_calculate_error_called` - For failed measurements

---

## Phase 3: Concrete Implementations (Priority: Medium)

### 3.1 FileBasedCircuit
- [ ] `test_FileBasedCircuit_init_creates_asc_file` - Creates from template
- [ ] `test_FileBasedCircuit_compile_returns_result` - Returns Result type
- [ ] `test_FileBasedCircuit_get_bitstream` - Returns list[bool]
- [ ] `test_FileBasedCircuit_set_bitstream` - Modifies hardware file
- [ ] `test_FileBasedCircuit_copy_from` - Copies from another circuit
- [ ] `test_FileBasedCircuit_get_set_file_attribute` - Attribute storage

### 3.3 Microcontroller (mocked serial)
- [ ] `test_Microcontroller_init` - Initializes serial connection
- [ ] `test_Microcontroller_request_measurement_waveform` - WAVEFORM flow
- [ ] `test_Microcontroller_request_measurement_oscillations` - OSCILLATIONS flow
- [ ] `test_Microcontroller_measure_signal` - Parses MCU response
- [ ] `test_Microcontroller_measure_pulses` - Multiple samples
- [ ] `test_Microcontroller_timeout_recovery` - Error handling

### 3.4 EvalPulseCountFitness
- [ ] `test_EvalPulseCountFitness_perfect_match` - Returns 1.0
- [ ] `test_EvalPulseCountFitness_zero_pulses` - Returns 0.0
- [ ] `test_EvalPulseCountFitness_multiple_samples` - Uses last sample
- [ ] `test_EvalPulseCountFitness_negative_difference` - Handled correctly

### 3.5 EvalVarMaxFitness
- [ ] `test_EvalVarMaxFitness_constant_data` - Variance = 0
- [ ] `test_EvalVarMaxFitness_high_variance` - High variance data
- [ ] `test_EvalVarMaxFitness_empty_data` - Empty data handling

### 3.2 BitstreamIndividual (additional)
- [ ] `test_BitstreamIndividual_init_bitstream_size` - Correct size
- [ ] `test_BitstreamIndividual_copy_from` - Deep copy
- [ ] `test_BitstreamIndividual_crossover_at_zero` - Edge case
- [ ] `test_BitstreamIndividual_crossover_at_end` - Edge case

---

## Phase 4: End-to-End Integration (Priority: Medium)

### 2.1 Evolution Pipeline
- [ ] `test_evolution_pipeline_integration` - Full run with real components

### 2.2 CircuitFactory to Measurement
- [ ] `test_circuit_factory_to_measurements_integration` - Factory → Measurements

### 2.3 Measurement to Fitness
- [ ] `test_measurement_to_fitness_integration` - Measurements → Fitness evaluation

---

## Completed Tests

_Move items here as they are implemented and passing._

### Phase 1
<!-- Example:
- [x] `test_Population_rejects_duplicate_individuals` - Added in commit abc123
-->

### Phase 2

### Phase 3

### Phase 4

---

## Notes

- All new tests should be added to existing test files where appropriate
- Use `@pytest.mark.immediate` for fast tests (<10s)
- Use `@pytest.mark.short` for tests <60s
- Use `@pytest.mark.long` for tests >1min
- Mock external dependencies (serial, file I/O for hardware tests)
- Reference [test_plan.md](../docs/test_plan.md) for detailed test specifications
