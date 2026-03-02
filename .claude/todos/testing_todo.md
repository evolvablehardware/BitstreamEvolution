# Testing TODO

Progress tracker for implementing tests from [test_plan.md](../docs/test_plan.md).

**Last Updated**: 2026-03-01

**Status**: All planned phases complete as of 2026-02-27 (68 new tests across 9 files).

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
- **Resolution tracked in**: [result_returns_todo.md](result_returns_todo.md)

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
- Reference [test_plan.md](../docs/test_plan.md) for detailed test specifications and future additions (PlotDataRecorder, Logger, FullySimCircuit)