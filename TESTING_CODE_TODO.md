# Testing Code TODO

This document tracks the plan for expanding test coverage in BitstreamEvolution.

## Current State (January 2026)

### Test Coverage Summary

**Total: 219 tests (206 passing, 4 skipped, 9 xfailed known bugs)**

| Module | Test File | Tests | Status |
|--------|-----------|-------|--------|
| `evolve.py` (CLI args) | `test/test_evolve_terminal_args.py` | 28 | ✅ Good (refactored) |
| `evolve.py` (E2E) | `test/test_evolve.py` | 12 | ✅ Complete |
| `Config.py` | `test/test_config.py` | 55 | ✅ Complete |
| `ConfigBuilder.py` | `test/test_config_builder.py` | 4 | ✅ Good |
| `CircuitPopulation.py` | `test/test_circuit_population.py` | 21 | ✅ Complete |
| `Evolution.py` | `test/test_evolution.py` | 12 | ✅ Complete |
| `Logger.py` | `test/test_logger.py` | 11 | ✅ Complete |
| `FullySimCircuit.py` | `test/Circuit/test_fully_sim_circuit_refactored.py` | 12 | ✅ Complete (proper fixtures) |
| `FullySimCircuit.py` | `test/Circuit/test_fully_sim_circuit.py` | 5 | ⚠️ Legacy (module-level state) |
| `multi_evolve.py` | `test/test_multi_evolve.py` | 8 | ✅ Good |
| `SimHardwareCircuit.py` | `test/Circuit/test_hardware_sim_circuit.py` | 4 | ✅ Refactored (skipped without IceStorm) |
| `IntrinsicCircuit.py` | `test/Circuit/test_intrinsic_circuit.py` | 1 | ✅ Refactored |
| `PulseCountFitnessFunction` | `test/Circuit/test_pulse_count_func.py` | 2 | ✅ Good |
| `VarMaxFitnessFunction` | `test/Circuit/test_var_max_func.py` | 2 | ✅ Good |
| `ToneDiscriminatorFitnessFunction` | `test/Circuit/test_tone_discriminator_func.py` | 13 | ✅ **NEW** |
| Integration Tests | `test/test_integration.py` | 14 | ✅ **NEW** |

### Remaining Gaps (Untested)

| Module | Lines | Priority | Notes |
|--------|-------|----------|-------|
| `FileBasedCircuit.py` | ~300 | 🟡 Medium | ABC for file-based circuits |
| `Microcontroller.py` | ~460 | 🟢 Low | Hardware-dependent |
| `tools/*` scripts | ~500 | 🟢 Low | Utility scripts |

---

## Phase 1: High Priority Tests

### 1.1 End-to-End Evolution Tests
**File**: `test/test_evolve.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (12 tests):
- [x] Evolution completes N generations without crashing (FULLY_SIM mode)
- [x] Workspace files created correctly
- [x] Print-only mode works
- [x] Config loading tests (simulation_mode, population_size, generations)
- [x] Different selection methods work (FIT_PROP_SEL, RANK_PROP_SEL, SINGLE_ELITE, FRAC_ELITE)
- [x] Different fitness functions work (VARIANCE)
- [x] CLASSIC_TOURN marked xfail (bug: accesses .get_fitness() on None)

### 1.2 Config.py Tests
**File**: `test/test_config.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (55 tests):
- [x] All simulation modes validated (FULLY_SIM, SIM_HARDWARE, FULLY_INTRINSIC, INTRINSIC_SENSITIVITY)
- [x] All fitness functions validated (VARIANCE, PULSE_COUNT, TOLERANT_PULSE_COUNT, etc.)
- [x] GA parameters type checking (population_size, mutation_probability, crossover_probability, elitism_fraction)
- [x] All selection types validated (SINGLE_ELITE, FRAC_ELITE, CLASSIC_TOURN, FIT_PROP_SEL, RANK_PROP_SEL, MAP_ELITES)
- [x] Initialization modes validated (CLONE_SEED, CLONE_SEED_MUTATE, RANDOM, EXISTING_POPULATION)
- [x] Stopping conditions (generations, target_fitness)
- [x] Logging configuration (log_level, save_log, save_plots, directory paths)
- [x] Hardware configuration (routing, serial_baud, fpga, usb_path)
- [x] 2 tests marked xfail (bug: Config.__log_warning fails when logger not added)

### 1.3 CircuitPopulation.py Tests
**File**: `test/test_circuit_population.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (21 tests):
- [x] Population initializes with correct selection method
- [x] Selection method assignment verified for all types
- [x] Population creates correct number of circuits
- [x] Population works with different sizes (5, 10, 20)
- [x] Evolution runs correct number of generations
- [x] Population size remains constant after evolution
- [x] Circuits have fitness values after population
- [x] Best circuit has highest fitness (sorted list)
- [x] Elite count calculation verified
- [x] Epoch tracking (initial=0, increments correctly)
- [x] 1 test marked xfail (bug: UNIQUE diversity measure calls get_sim_bitstream which doesn't exist)

---

## Phase 2: Medium Priority Tests

### 2.1 Evolution.py Orchestrator Tests
**File**: `test/test_evolution.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (12 tests):
- [x] Evolution can be instantiated
- [x] Evolution has evolve and validate_arguments methods
- [x] validate_arguments accepts None and valid directories
- [x] validate_arguments rejects invalid directories
- [x] Print-only mode doesn't create population or logger
- [x] 3 tests marked xfail (WorkspaceFormatter expects files not in test env)

### 2.2 Logger.py Tests
**File**: `test/test_logger.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (11 tests):
- [x] Logger creates log files on initialization
- [x] Logger adds itself to config
- [x] log_event respects log level
- [x] log_info, log_warning, log_error format correctly
- [x] log_monitor writes to file
- [x] log_generation logs best circuit info
- [x] 1 test marked xfail (bug: datetime with colons fails on Windows)

### 2.3 ToneDiscriminatorFitnessFunction Tests
**File**: `test/Circuit/test_tone_discriminator_func.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (13 tests):
- [x] Can instantiate and inherits from FitnessFunction
- [x] calculate_fitness returns average of measurements
- [x] Edge cases (single value, zero measurements, perfect score)
- [x] Parametrized tests with various input combinations
- [x] attach() correctly sets data filepath and microcontroller
- [x] Fitness values stay within valid range [0, 1]

---

## Phase 3: Test Infrastructure Improvements

### 3.1 Refactor Circuit Tests to Use Fixtures
**File**: `test/Circuit/test_fully_sim_circuit_refactored.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (12 tests):
- [x] Zero bitstream has zero fitness
- [x] All-ones bitstream has non-zero fitness
- [x] Fitness is always numeric
- [x] Full mutation flips all bits
- [x] Zero mutation preserves bits
- [x] Randomization to all-ones and all-zeros
- [x] Single-point crossover at various positions
- [x] Bitstream injection and retrieval
- [x] 1 test marked xfail (get_bitstream returns reference, not copy)

### 3.2 Add Explicit Test Markers
**Status**: ✅ Completed

All new tests use explicit markers:
- `@pytest.mark.immediate` - Unit tests, mocked tests (<10s)
- `@pytest.mark.short` - Small evolution runs, integration tests (<60s)
- `@pytest.mark.long` - Full evolution experiments (>1min)

### 3.3 Implement Seeded Randomness
**Status**: ❌ Not started

Per CLAUDE.md: "For stochastic operations, implement seeded randomness for reproducible results."

Options:
1. Create a `SeededRandom` wrapper class
2. Pass seed to numpy random generator
3. Use pytest fixtures to control random state

---

## Phase 4: Integration Tests

### 4.1 Component Integration Tests
**File**: `test/test_integration.py`
**Status**: ✅ Completed (January 2026)

Tests implemented (14 tests):
- [x] Config creates correct population size
- [x] Config elitism_fraction affects population behavior
- [x] Config generations controls evolution length
- [x] Population integrity maintained through evolution
- [x] All circuits have valid fitness after evolution
- [x] Circuits remain sorted by fitness after evolution
- [x] Different selection methods complete evolution (FIT_PROP_SEL, RANK_PROP_SEL, SINGLE_ELITE, FRAC_ELITE)
- [x] ConfigBuilder creates valid, usable config
- [x] Full pipeline runs to completion
- [x] Best circuit tracking throughout evolution

---

## Test File Structure (Current)

```
test/
├── conftest.py                         # Marker auto-assignment, shared fixtures
├── test_evolve.py                      # ✅ End-to-end evolution tests
├── test_evolve_terminal_args.py        # ✅ Refactored (shlex parsing)
├── test_config_builder.py              # ✅ Existing
├── test_config.py                      # ✅ Config accessor tests
├── test_multi_evolve.py                # ✅ Existing
├── test_circuit_population.py          # ✅ Selection/population tests
├── test_evolution.py                   # ✅ Orchestrator tests
├── test_logger.py                      # ✅ Logging tests
├── test_integration.py                 # ✅ Integration tests
├── test_utils.py                       # ✅ Existing
└── Circuit/
    ├── test_fully_sim_circuit.py       # ⚠️ Legacy (module-level state)
    ├── test_fully_sim_circuit_refactored.py # ✅ Proper fixtures
    ├── test_hardware_sim_circuit.py    # ✅ Refactored (skips without IceStorm)
    ├── test_intrinsic_circuit.py       # ✅ Refactored
    ├── test_pulse_count_func.py        # ✅ Fixed attach() signature
    ├── test_var_max_func.py            # ✅ Fixed attach() signature
    └── test_tone_discriminator_func.py # ✅ NEW
```

---

## Running Tests

```bash
# All tests
pytest test/

# By marker
pytest -m immediate             # Fast tests (<10 sec)
pytest -m "immediate or short"  # Dev branch tests
pytest -m long                  # Long-running tests

# Specific file
pytest test/test_config.py

# With coverage (if pytest-cov installed)
pytest --cov=src test/
```

---

## Progress Tracking

| Phase | Task | Status | Date |
|-------|------|--------|------|
| 1.1 | End-to-end evolution tests | ✅ Completed | January 2026 |
| 1.2 | Config.py tests | ✅ Completed | January 2026 |
| 1.3 | CircuitPopulation.py tests | ✅ Completed | January 2026 |
| 2.1 | Evolution.py tests | ✅ Completed | January 2026 |
| 2.2 | Logger.py tests | ✅ Completed | January 2026 |
| 2.3 | ToneDiscriminator tests | ✅ Completed | January 2026 |
| 3.1 | Refactor circuit tests | ✅ Completed | January 2026 |
| 3.2 | Add explicit markers | ✅ Completed | January 2026 |
| 3.3 | Seeded randomness | ❌ Not started | |
| 4.1 | Integration tests | ✅ Completed | January 2026 |
| - | Legacy test fixes (terminal args, hardware/intrinsic circuits) | ✅ Completed | January 2026 |

## Bugs Discovered During Testing

The new tests uncovered the following bugs in the codebase:

1. **CLASSIC_TOURN selection with small populations** ([CircuitPopulation.py:813](src/CircuitPopulation.py#L813))
   - `ckt2.get_fitness()` called on `None` when population size is small
   - Test: `test_evolve.py::TestEvolutionWithDifferentSelections::test_selection_methods_complete[CLASSIC_TOURN]`

2. **Config.__log_warning fails without logger** ([Config.py:1017](src/Config.py#L1017))
   - `__log_warning` assumes `__logger` exists, but it's optional via `add_logger()`
   - Tests: `test_config.py::TestStoppingConditionConfig::test_generations_ignore_returns_none`, `test_target_fitness_ignore_returns_none`

3. **UNIQUE diversity measure with FullySimCircuit** ([CircuitPopulation.py:1238](src/CircuitPopulation.py#L1238))
   - `count_unique()` calls `get_sim_bitstream()` which doesn't exist on `FullySimCircuit`
   - Test: `test_circuit_population.py::TestCircuitPopulationDiversity::test_diversity_measure_unique_computes[UNIQUE]`

4. **WorkspaceFormatter expects files not present in test environment** ([WorkspaceFormatter.py:76](src/WorkspaceFormatter.py#L76))
   - `format_workspace()` tries to read `builtconfig.ini` from a path that doesn't exist during tests
   - Tests: `test_evolution.py::TestEvolutionExecution::*`

5. **Logger.save_workspace uses colons in filename** ([Logger.py:218](src/Logger.py#L218))
   - Datetime format includes colons which are invalid in Windows filenames
   - Test: `test_logger.py::TestLoggerWorkspace::test_save_workspace_copies_directory`

6. **get_bitstream returns reference, not copy** ([FullySimCircuit.py](src/Circuit/FullySimCircuit.py))
   - Modifying the returned bitstream modifies the internal state
   - Test: `test_fully_sim_circuit_refactored.py::TestFullySimCircuitBitstream::test_get_bitstream_returns_copy`

---

## Notes

- **Always use `FULLY_SIM` mode** for automated tests - hardware is slow and errors waste time
- Tests should be deterministic where possible (use seeded random)
- Follow existing patterns in `test_evolve_terminal_args.py` for parametrized tests
- Use Sphinx reST format for test docstrings
