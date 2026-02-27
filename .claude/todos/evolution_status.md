# Evolution.py Status

**Last Updated**: 2026-02-27

---

## Current Status

[Evolution.py](../../src/Evolution.py) carries the class-level warning:

> "NOT CURRENT VERSION, SHOULD BE REVISED USING TRIVIAL_EVOLUTION"

The file is still in the repository and is fully functional, but is not considered the canonical implementation. The reference implementation to compare against is `TrivialEvolution` in [TrivialImplementation.py](../../src/TrivialImplementation.py).

---

## What It Does Now

`Evolution` is a complete, working evolution loop that:
1. Initializes populations via `GenerateInitialPopulations`
2. Generates measurements via `GenerateMeasurements`
3. Runs all hardware measurements concurrently with `asyncio.gather()`
4. Evaluates fitness for each population
5. Reproduces the next generation
6. Records fitness data to `PlotDataRecorder`

The key differences from `TrivialEvolution`:
- Handles **multiple populations** (list of populations, not single)
- Uses real **async hardware** via `asyncio.gather()`
- Records data to `PlotDataRecorder` after each generation
- Has a TODO: diversity calculation (currently hardcoded to 0)

---

## Known Issues

1. **asyncio usage**: Line 42 uses `asyncio.run(asyncio.gather(*tasks))`. The comment notes this may need `asyncio.TaskGroup` instead (Python 3.11+ feature). The current approach creates a new event loop each generation.

2. **Measurement results**: `asyncio.gather()` returns results in the same order as inputs. The current code passes `results` (the gathered list) to `eval_population_fitness`, but `EvaluatePopulationFitness` expects a `list[Measurement]`. The `results` are `Measurement` objects (returned by `Hardware.request_measurement`), so this is correct — but it's non-obvious.

3. **Fitness type assumption**: Line 52 does `fits.append(f)` with a `# type: ignore`, assuming fitness is `float`. This will fail at runtime if a non-float `Fitness` implementation is used.

4. **No error handling**: If any hardware measurement fails (exception in asyncio.gather), the entire evolution loop crashes. No fallback or partial-failure handling.

---

## Proposed Resolutions

### Option A: Keep Evolution.py as the "real" implementation, update it

- Remove the "NOT CURRENT VERSION" warning
- Fix the asyncio issues (TaskGroup or keep gather with proper error handling)
- Add type annotation for fitness aggregation
- Add diversity calculation
- Align the `asyncio.gather` + `eval_population_fitness` wiring more clearly

### Option B: Delete Evolution.py, promote TrivialEvolution

- TrivialEvolution currently handles only a single population and no real hardware
- Would need to extend TrivialEvolution to support multiple populations and real hardware
- Cleaner: one evolution class, one code path

### Option C: Keep both with clear separation of roles

- `TrivialEvolution` = single-population, no hardware, for testing
- `Evolution` = multi-population, real hardware, for deployment
- Remove "NOT CURRENT VERSION" from Evolution.py, add clear docstrings to both

---

## Questions to Answer

1. Is multiple-population evolution a current use case, or is single-population sufficient?
2. Should asyncio.gather be replaced with TaskGroup? (TaskGroup has better error propagation)
3. What does "diversity" mean in this context — bitstring Hamming distance? Fitness variance?