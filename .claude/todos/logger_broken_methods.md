# Logger.py: Broken Methods and Design Issues

**Last Updated**: 2026-02-27

**File**: [src/Logger.py](../../src/Logger.py)

---

## The Broken Method

`Logger.log_generation()` (lines 141-164) calls methods that do not exist on `Population`:

```python
def log_generation(self, population, epoch_time):
    current_best_circuit = population.get_current_best_circuit()      # does not exist
    overall_best_circuit = population.get_overall_best_circuit_info()  # does not exist
    population.get_best_epoch()                                         # does not exist
    population.get_current_epoch()                                      # does not exist
```

`Population` (defined in [BitstreamEvolutionProtocols.py](../../src/BitstreamEvolutionProtocols.py)) only has:
- `__init__`, `__iter__`, `__len__`
- `set_fitness_by_index`, `set_fitness`, `set_fitness_of_unevaluated_individuals`, `sort`

**Impact**: `log_generation()` will crash with `AttributeError` at runtime if called. It is unclear whether this method is currently called anywhere.

---

## What the Method Was Supposed to Do

Based on the log output strings, `log_generation()` was intended to:
1. Print a separator (triple `DOUBLE_HLINE`)
2. Log the overall best circuit seen so far (name, epoch it was found, fitness)
3. Log the best circuit of the current epoch (name, fitness, time taken)

This requires tracking across generations — information that `Population` doesn't hold and wasn't designed to hold.

---

## Proposed Solutions

### Option A: Delete `log_generation()`

If this logging isn't currently used, remove it. It cannot be called safely. The information it displays (best circuit across all time, best of current epoch) would need to be tracked elsewhere if desired.

### Option B: Rewrite with information passed in

Change the signature to accept pre-computed values rather than calling Population methods:

```python
def log_generation(self, epoch: int, epoch_time: float,
                   current_best_name: str, current_best_fitness: float,
                   overall_best_name: str, overall_best_epoch: int, overall_best_fitness: float):
    ...
```

The caller (e.g., `Evolution.run()`) would be responsible for tracking and computing this.

### Option C: Extend Population to track history

Add `get_current_best()` and similar methods to Population. This is a significant design change — Population currently has no concept of "epochs" or "best across time."

---

## Other Logger Issues (Lower Priority)

1. **Hard-coded workspace paths** (lines 111-121): Creates files like `workspace/alllivedata.log` with no configurable base path. These paths must exist relative to the working directory when the program runs.

2. **Platform-specific process launching** (lines 89-100): Launches `gnome-terminal` to display plots. This only works on Linux with GNOME. On Windows or macOS, this will fail silently (OSError caught and logged).

3. **`TODO: Utilize Python logging library`** (line 52): The Logger class reimplements what Python's built-in `logging` module provides (levels, formatting, file output). Consider replacing with `logging.getLogger()`.

4. **`__init_monitor()` is always called** (line 139): The commented-out guard `# if config.get_launch_monitor():` means `__init_monitor()` always runs, which means `gnome-terminal` launch is always attempted.