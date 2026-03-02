# Result Library Migration TODO

Tracks migrating from the `result` library to the `returns` library throughout the codebase.

**See**: [result_returns_migration.md](../docs/result_returns_migration.md) for rationale and API mapping.

**Last Updated**: 2026-02-27

---

## Why This Matters

`BitstreamEvolutionProtocols.py` (the source of truth for all interfaces) uses `returns.result.Success/Failure`.
Files that implement those protocols use `result.Ok/Err`. These are **two different PyPI packages** with
incompatible APIs. A `Success()` will not pass `is_ok()`, causing real test failures and silent runtime bugs.

Example failure: `test_TrivialCircuit_ImplementsCompile` fails because `TrivialCircuit.compile()` returns
`Success(None)` but `FileBasedCircuit` callers expect `is_ok()` to return True for it.

---

## Checklist

### Source Files

- [x] `src/Circuit/Circuit.py` (line 6)
  - Change: `from result import Result` → `from returns.result import Result`
  - Note: `compile()` return type annotation only, no Ok/Err created here

- [ ] `src/Circuit/FileBasedCircuit.py` (line 11)
  - Change: `from result import Result, Ok, Err` → `from returns.result import Result, Success, Failure`
  - Change: all `Ok(...)` → `Success(...)`, all `Err(...)` → `Failure(...)`

- [ ] `src/Hardware/Microcontroller.py` (line 6)
  - Change: `from result import Ok, Err` → `from returns.result import Success, Failure`
  - Change: all `Ok(...)` → `Success(...)`, all `Err(...)` → `Failure(...)`

- [ ] `src/EvaluateFitness/EvaluateFitness.py` (line 4)
  - Change: `from result import is_ok` → `from returns.result import Success`
  - Change: `if is_ok(m.result):` → `if isinstance(m.result, Success):`
  - Change: `m.result.ok_value` → `m.result.unwrap()`
  - Change: `m.result.err_value` → `m.result.failure()`

### Dependencies

- [ ] `pyproject.toml`: Remove `result` from dependencies after all files migrated
- [ ] Verify `returns = "^0.26"` (or current) remains in dependencies

### Tests

- [ ] Remove any test workarounds that set `measurement.result = Ok(data)` directly
  - These exist because tests had to use `result.Ok` to satisfy `EvaluateFitness.is_ok()` check
  - After migration, tests can use `measurement.record_measurement_result(data)` which uses `Success`

### Verify No Regressions

- [ ] Run `pytest -m "immediate"` - should have 0 failures
- [ ] Confirm `test_TrivialCircuit_ImplementsCompile` passes (currently known failure)
- [ ] Run `poetry run mypy src/` - check for new type errors

---

## Questions to Answer Before Starting

1. Does `returns.result.Result` have the same type annotation behavior as `result.Result`?
   - Yes: both are generic `Result[T, E]` - annotations should be compatible

2. Are there any other callers of `FileBasedCircuit.compile()` or `Microcontroller` results that use `result` API?
   - Search for `.ok_value`, `.err_value`, `is_ok(` across the codebase before migrating

3. Does `TrivialImplementation.py` already use `returns`?
   - Yes, `TrivialCircuit.compile()` returns `Success(None)` - no change needed there

---

## Notes

- Do files one at a time to keep changes reviewable
- Each file change is independent and safe to do in isolation
- `FileBasedCircuit.py` likely has the most Ok/Err callsites - do last or be careful