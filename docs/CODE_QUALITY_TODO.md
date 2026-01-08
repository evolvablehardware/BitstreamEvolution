# Code Quality Improvement Tracking

This document tracks remaining code quality issues and the plan to address them.

**Last Updated**: January 2026
**Current Status**: 113 ruff errors, 122 pyright errors

## Progress Summary

| Phase | Status | Before | After |
|-------|--------|--------|-------|
| Auto-fix (safe) | Done | 1132 | 145 |
| Auto-fix (E711, E712, B007) | Done | 145 | 124 |
| Format all files | Done | 32 files | 0 files |
| Phase 1 quick wins | Done | 124 | 113 |
| Manual fixes | In Progress | 113 | - |
| Type annotations | Not Started | 122 | - |

### Phase 1 Fixes Applied
- F811: Removed duplicate `get_file_attribute` in Circuit.py
- F821 + B006: Fixed invalid type annotation in arg_parse_utils.py
- B008: Fixed mutable default `Evolution()` in multi_evolve.py
- F821: Fixed undefined `data` → `measurements` in ToneDiscriminatorFitnessFunction.py
- F821: Added missing `import re` in ToneDiscriminatorFitnessFunction.py

---

## Ruff Issues by Category (113 total)

### SIM115: Use context managers for file operations (~50 occurrences)
**Effort**: Medium | **Risk**: Low | **Priority**: High

Files affected:
- `CircuitPopulation.py` (1)
- `Circuit/CircuitLegacy.py` (12)
- `Circuit/FileBasedCircuit.py` (8)
- `Circuit/IntrinsicCircuit.py` (2)
- `Config.py` (8)
- `ConfigBuilder.py` (2)
- `Evolution.py` (1)
- `Logger.py` (5)
- `Microcontroller.py` (1)
- `PlotEvolutionLive.py` (3)
- `PlotSensitivityLive.py` (2)
- `ascTemplateBuilder.py` (4)
- `tools/pulse_histogram.py` (1)
- `test/test_utils.py` (2)

**Note**: Some file operations use `mmap` which requires the file handle to remain open. These need careful refactoring.

### SIM102: Nested if statements (~15 occurrences)
**Effort**: Low | **Risk**: Low | **Priority**: Medium

Can be combined with `and`:
```python
# Before
if condition1:
    if condition2:
        action()

# After
if condition1 and condition2:
    action()
```

Files: `CircuitPopulation.py`, `Circuit/CircuitLegacy.py`, `Circuit/FileBasedCircuit.py`, `Evolution.py`

### B007: Unused loop variables (~8 occurrences)
**Effort**: Low | **Risk**: None | **Priority**: Low

Replace `for i in range(n)` with `for _ in range(n)` when `i` is unused.

Files: `CircuitPopulation.py`, `Microcontroller.py`, `PlotEvolutionLive.py`, `PlotSensitivityLive.py`

### B008: Mutable default arguments (2 occurrences)
**Effort**: Low | **Risk**: Low | **Priority**: High

- `src/multi_evolve.py:75` - `Evolution()` as default
- `src/arg_parse_utils.py:10` - Dict as default

### B027: Empty method without @abstractmethod (1 occurrence)
**Effort**: Low | **Risk**: None | **Priority**: Low

- `src/Circuit/Circuit.py:50` - `set_file_attribute`

### F811: Redefinition of function (1 occurrence)
**Effort**: Medium | **Risk**: Medium | **Priority**: High

- `src/Circuit/Circuit.py:126` - `get_file_attribute` defined twice

### F821: Undefined names (2 occurrences)
**Effort**: Medium | **Risk**: High | **Priority**: High

- `src/arg_parse_utils.py:10` - Invalid type annotation syntax

### E402: Module imports not at top (2 occurrences)
**Effort**: Low | **Risk**: Low | **Priority**: Low

- `test/test_multi_evolve.py:14-15`

### W291: Trailing whitespace in docstrings (2 occurrences)
**Effort**: Low | **Risk**: None | **Priority**: Low

- `src/evolve.py:30`
- `src/multi_evolve.py:17`

### Other issues
- `SIM110`: Use `all()` instead of for loop (1)
- `B026`: Star-arg after keyword arg (1)
- `RUF013`: Implicit Optional (1)
- `B018`: Useless expression (1)

---

## Pyright Issues (122 total)

### Module used as type (~30 occurrences)
**Root Cause**: Type hints use `Config` (the module) instead of `Config.Config` (the class).

**Solution**: Either:
1. Change imports: `from Config import Config` → access as `Config`
2. Or use full path: `Config.Config` in type hints

Files: Most files in `src/Circuit/`

### Possibly unbound variables (~10 occurrences)
Variables that might not be defined in all code paths.

Files: `CircuitLegacy.py`, `FileBasedCircuit.py`

### Incompatible method overrides (~5 occurrences)
Method signatures don't match base class.

File: `FileBasedCircuit.py:388` - `get_file_attribute` parameter name mismatch

### Missing/incorrect type annotations (~40 occurrences)
Functions missing return types or parameter types.

### Argument type mismatches (~20 occurrences)
Wrong types passed to functions.

---

## Recommended Fix Order

### Phase 1: Quick Wins (Low effort, high impact)
- [ ] Fix W291 trailing whitespace (2 files)
- [ ] Fix B008 mutable defaults (2 files)
- [ ] Fix F811 redefinition (1 file)
- [ ] Fix F821 undefined names (1 file)
- [ ] Fix remaining B007 unused variables (4 files)

### Phase 2: Context Managers (Medium effort)
- [ ] Refactor simple `open()` calls to use `with` statements
- [ ] Identify `mmap` cases that need special handling
- [ ] Update test utilities

### Phase 3: Code Simplification
- [ ] Combine nested if statements (SIM102)
- [ ] Replace for loops with `all()` (SIM110)
- [ ] Fix star-arg ordering (B026)

### Phase 4: Type System (High effort)
- [ ] Fix module-as-type pattern across Circuit classes
- [ ] Add missing type annotations
- [ ] Fix method signature mismatches
- [ ] Add `| None` to optional parameters

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
