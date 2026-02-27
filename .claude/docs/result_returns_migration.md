# `result` vs `returns` Library Migration

## Background

The codebase currently uses **two incompatible Python libraries** for Result types:

| Library (PyPI name) | Import | Types used | Used in |
|---------------------|--------|-----------|---------|
| `returns` | `from returns.result import ...` | `Result`, `Success`, `Failure` | `BitstreamEvolutionProtocols.py`, `TrivialImplementation.py` |
| `result` | `from result import ...` | `Result`, `Ok`, `Err`, `is_ok` | `Circuit/Circuit.py`, `Circuit/FileBasedCircuit.py`, `Hardware/Microcontroller.py`, `EvaluateFitness/EvaluateFitness.py` |

These two packages have **incompatible APIs**. A `Success()` from `returns` will fail an `is_ok()` check from `result`, and vice versa. This causes silent failures and requires workarounds in tests.

## Decision: Migrate to `returns`

The protocols in `BitstreamEvolutionProtocols.py` define the canonical interface, and they use `returns.result`. Since protocols set the contract, all implementations should use the same library.

**Target state**: Every file uses `from returns.result import Result, Success, Failure`.

## API Mapping

| `result` (old) | `returns` (new) |
|----------------|-----------------|
| `Ok(value)` | `Success(value)` |
| `Err(exception)` | `Failure(exception)` |
| `is_ok(r)` | `isinstance(r, Success)` |
| `r.ok_value` | `r.unwrap()` |
| `r.err_value` | `r.failure()` |
| `Result[T, E]` | `Result[T, E]` (same type annotation) |

## Files to Migrate

See [result_returns_todo.md](../todos/result_returns_todo.md) for the tracking checklist.

## Notes

- Both libraries are listed in `pyproject.toml` dependencies. After migration, remove `result` from dependencies.
- The `# type: ignore` comments on `result` imports can be removed after migration.
- `returns` also provides `Result.from_value()`, `@safe` decorator, and container chaining if those patterns prove useful later.
- Relevant known issue documented in [testing_todo.md](../todos/testing_todo.md) under "Known Issues".