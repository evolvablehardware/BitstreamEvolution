# Code Quality Improvement Tracking

This document tracks remaining code quality issues and the plan to address them.

**Last Updated**: January 2026
**Current Status**: 0 ruff errors, 59 pyright errors ✅

## Progress Summary

| Phase | Status | Before | After |
|-------|--------|--------|-------|
| Auto-fix (safe) | Done | 1132 | 145 |
| Auto-fix (E711, E712, B007) | Done | 145 | 124 |
| Format all files | Done | 32 files | 0 files |
| Phase 1 quick wins | Done | 124 | 113 |
| Phase 2 manual fixes | Done | 113 | 84 |
| Phase 3 quick wins | Done | 84 | 87* |
| Phase 4 auto-fix | Done | 87 | 84 |
| Phase 5 manual fixes | Done | 84 | 63 |
| Phase 6 unused vars | Done | 63 | 30 |
| Phase 7 context managers | Done | 30 | 0 |
| Phase 8 type fixes | Done | 122 | 96 |
| Phase 9 optional types | Done | 96 | 77 |
| Phase 10 matplotlib types | Done | 77 | 59 |

*Note: Error count increased due to ruff version updates detecting new issues.

### Phase 10 Fixes Applied (Matplotlib Types)
- Fixed `set_xlim`/`set_ylim` to use tuples instead of lists in PlotEvolutionLive.py
- Fixed `set_ylim([0, None])` to `set_ylim(bottom=0)` pattern
- Added `isinstance()` type guards for `get_transfer_interval()` return values used in `range()` step
- Added `# type: ignore` comments for matplotlib edge cases:
  - FuncAnimation callbacks returning None instead of Iterable[Artist]
  - HostAxes `axis["right"]` subscript access
  - `get_aux_axes()` method not in standard Axes type stubs

### Phase 9 Fixes Applied (Pyright)
- Added class-level type annotations to FitnessFunction:
  - `_data_filepath: Path`, `_microcontroller: Microcontroller`, `_config: Config`, `_extra_data: dict[str, float]`
- Removed empty `__init__` from FitnessFunction (triggered B027)
- Removed redundant `FitnessFunction.__init__(self)` calls from subclasses
- Fixed return types:
  - `ToneDiscriminatorFitnessFunction.get_measurements()` now returns `[fitness]` instead of `fitness`
  - Fixed `PulseCountFitnessFunction.calculate_fitness()` type conversion
- Fixed bug: `CircuitLegacy.simple_measure_pulses()` was passing extra unused argument
- Fixed `PulseCountFitnessFunction._get_all_live_reported_value()` returning undefined `_data`

### Phase 8 Fixes Applied (Pyright)
- Fixed module-as-type pattern: Changed `import Config` to `from Config import Config` across 6 files
  - `Circuit/Circuit.py`, `Circuit/FileBasedCircuit.py`, `Circuit/FitnessFunction.py`
  - `Circuit/FullySimCircuit.py`, `Circuit/IntrinsicCircuit.py`, `Circuit/SimHardwareCircuit.py`
- Fixed possibly unbound variables:
  - `pulse_count` in CircuitLegacy.py (added default value)
  - `rows` in CircuitLegacy.py and FileBasedCircuit.py (converted to ternary)
- Fixed method signature mismatches:
  - `get_file_attribute(name)` - aligned parameter names across Circuit, FileBasedCircuit, CircuitLegacy, FullySimCircuit
  - Added `-> str | None` return type to `get_file_attribute`
  - `calculate_fitness(measurements)` - aligned parameter name in PulseCountFitnessFunction and VarMaxFitnessFunction

### Phase 7 Fixes Applied
- SIM115: Fixed all 30 remaining context manager issues across 9 files:
  - `CircuitPopulation.py`: 1 mmap pattern converted to context manager
  - `Circuit/CircuitLegacy.py`: 6 mmap patterns converted to context managers
  - `Circuit/FileBasedCircuit.py`: 2 mmap patterns + 1 `open().close()` → `Path.touch()`
  - `Logger.py`: 5 issues (1 readme write, 11 log file creates → loop with `Path.write_text("")`, 1 noqa for managed file)
  - `Microcontroller.py`: 4 functions converted to use `with` statements
  - `PlotEvolutionLive.py`: 12 `open().read()` → `Path.read_text()`
  - `PlotSensitivityLive.py`: 1 `open().read()` → `Path.read_text()`
  - `Monitor.py`: 1 context manager for file iteration
  - `tools/pulse_histogram.py`: 1 readlines pattern converted

### Phase 6 Fixes Applied
- F841: Fixed 22 unused variables (prefixed with `_` for intentional ones, removed dead code)
- RUF059: Fixed 3 unused unpacked variables (`z`, `cs`, `hs` → `_z`, `_cs`, `_hs`)
- E741: Renamed 2 ambiguous variables (`l` → `file_line`)
- RUF005: Converted 2 list concatenations to unpacking (`TERM_CMD + [...]` → `[*TERM_CMD, ...]`)
- SIM108: Converted 2 if-else blocks to ternary operators
- RUF013: Fixed implicit Optional (`str = None` → `str | None = None`)
- RUF015: Replaced `list(gen)[0]` with `next(iter(gen))`

### Phase 5 Fixes Applied
- E722: Replaced 10 bare `except:` with specific exception types (ValueError, TypeError, IndexError, ImportError)
- E731: Converted 4 lambda assignments to `def` functions in PlotEvolutionLive.py, PlotSensitivityLive.py
- SIM105: Converted 4 `try/except/pass` to `contextlib.suppress()` in WorkspaceFormatter.py
- SIM102: Combined 1 nested if statement in preflight_check.py
- B026: Fixed star-arg ordering in CircuitPopulation.py
- SIM110: Replaced for loop with `all()` in CircuitPopulation.py

### Phase 4 Fixes Applied
- F401: Removed unused import (auto-fixed)
- F541: Fixed f-string missing placeholders (auto-fixed)
- W293: Removed whitespace from blank lines in generate_configs.py (3 instances)

### Phase 3 Fixes Applied
- W291: Fixed trailing whitespace in generate_configs.py (2 instances)
- B007: All unused loop variables already fixed

### Phase 1 Fixes Applied
- F811: Removed duplicate `get_file_attribute` in Circuit.py
- F821 + B006: Fixed invalid type annotation in arg_parse_utils.py
- B008: Fixed mutable default `Evolution()` in multi_evolve.py
- F821: Fixed undefined `data` → `measurements` in ToneDiscriminatorFitnessFunction.py
- F821: Added missing `import re` in ToneDiscriminatorFitnessFunction.py

### Phase 2 Fixes Applied
- B007: Fixed 9 unused loop variables (`i` → `_`)
- B027: Added docstrings/code to 2 empty abstract methods
- SIM102: Combined 5 nested if statements with `and`
- SIM115: Added context managers in 11 files (test_utils, ConfigBuilder, Config, WorkspaceFormatter, ascTemplateBuilder, PulseCountFitnessFunction, VarMaxFitnessFunction, ToneDiscriminatorFitnessFunction)

---

## Ruff Issues - COMPLETE ✅

All 1132 ruff lint errors have been resolved through phases 1-7.

---

## Pyright Issues (59 remaining)

### ✅ Fixed: Module used as type
Changed `import Config` to `from Config import Config` pattern.

### ✅ Fixed: Possibly unbound variables
Added default values and used ternary operators.

### ✅ Fixed: Incompatible method overrides
Aligned parameter names and return types across class hierarchy.

### ✅ Fixed: FitnessFunction optional types
Added class-level type annotations for all attributes.

### ✅ Fixed: Matplotlib animation types
Used tuples for limits, type guards for intervals, type ignores for edge cases.

### Remaining Issues (~59 total)
Most remaining issues are in specialized areas:
- **CircuitPopulation.py** (~22): Operator issues with `Literal['IGNORE']`, attribute access on `list[Unknown]`
- **Config.py** (~6): Attribute access issues
- **Microcontroller.py** (~5): Possibly unbound variables
- **Monitor.py** (~4): Missing import `tailer`, possibly unbound variables
- **tools/*.py** (~10): Type mismatches in generators, add_axes arguments
- **Other files** (~12): Various argument type issues

---

## Recommended Fix Order

### Phase 11: CircuitPopulation Type Issues (Medium priority)
- [ ] Fix `Literal['IGNORE']` comparison issues with type guards
- [ ] Fix `list[Unknown]` attribute access with proper type annotations

### Phase 12: Remaining Type Issues (Low priority)
- [ ] Fix argument type mismatches with proper casts/guards
- [ ] Add missing type annotations where needed
- [ ] Consider `# type: ignore` for third-party library issues

---

## Commands Reference

```bash
# Check current status
ruff check src/ test/
pyright src/

# Fix specific rule
ruff check src/ --fix --select SIM102

# See issues by file
ruff check src/ --output-format=grouped

# Type check single file
pyright src/Config.py
```

---

## Notes

- **CircuitLegacy.py**: Large file (1300+ lines) with many issues. Consider whether this file is still needed or can be deprecated.
- **mmap usage**: Several files use `mmap` for performance. Context manager refactoring needs to preserve file handle lifetime.
- **Type annotations**: The module-as-type issue is systemic. A consistent pattern should be established before fixing.
