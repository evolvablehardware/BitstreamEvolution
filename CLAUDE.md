# BitstreamEvolution

Genetic algorithm toolchain for evolving FPGA bitstreams on Lattice iCE40HX1K hardware. Circuits are evolved to optimize fitness functions (oscillator frequency, signal variance, tone discrimination) for evolvable hardware research.

**Repository**: https://github.com/evolvablehardware/BitstreamEvolution
**License**: GPL-3.0

## Tech Stack

- **Python 3.10+** - Primary language (supports 3.10, 3.11, 3.12, 3.13)
- **Poetry** - Dependency management
- **Ruff** - Linting and formatting
- **Pyright** - Static type checking
- **pytest** - Testing framework
- **Sphinx** - Documentation (reST docstring format)
- **Project IceStorm** - FPGA toolchain (yosys, arachne-pnr, icepack, iceprog)
- **Arduino** - Microcontroller firmware for fitness measurement
- **Key libraries**: numpy, matplotlib, pyserial, sortedcontainers, toml

## Project Structure

```
src/
├── evolve.py                 # Entry point - run evolution experiments
├── Evolution.py              # Orchestrator - coordinates all components
├── CircuitPopulation.py      # Population management, selection algorithms
├── Config.py                 # Configuration management
├── ConfigBuilder.py          # Config inheritance/composition
├── Microcontroller.py        # Serial communication with Arduino
├── Logger.py                 # Experiment logging
├── PlotEvolutionLive.py      # Real-time visualization
├── Circuit/                  # Circuit implementations (ABC pattern)
│   ├── Circuit.py            # ABC defining circuit interface
│   ├── IntrinsicCircuit.py   # Real FPGA evaluation
│   ├── SimHardwareCircuit.py # Hardware simulation
│   ├── FullySimCircuit.py    # Full software simulation
│   ├── FitnessFunction.py    # Fitness function ABC
│   └── *FitnessFunction.py   # Concrete fitness strategies
└── tools/                    # Utility scripts

data/
├── default_config.ini        # Configuration template
├── example_configs/          # Example configurations
├── ReadSignal/               # Arduino firmware
└── seed-hardware*.asc        # FPGA bitstream templates

test/
├── res/inputs/               # Test config files
└── res/expected_out/         # Expected outputs
```

## Build & Run Commands

### Setup
```bash
poetry install --with dev     # Install dependencies
make all                      # Full setup: init + icestorm tools + udev rules
make init                     # Create workspace directories and default config
make icestorm-tools           # Build FPGA toolchain (icestorm, arachne-pnr, yosys)
```

### Run Evolution
```bash
python src/evolve.py                          # Standard run
python src/evolve.py -c path/to/config.ini    # Custom config
python src/evolve.py -d "experiment notes"    # With description
python src/evolve.py -o /output/directory     # Custom output
```

### Testing
```bash
pytest test/                    # All tests
pytest -m immediate             # Fast tests (<10 sec)
pytest -m "immediate or short"  # Dev branch tests
pytest -m long                  # Long-running tests (main branch)
```

### Utilities
```bash
python src/tools/reconstruct.py [generation#]  # Reconstruct generation
python src/tools/pulse_histogram.py            # View pulse histogram
```

### Cleanup
```bash
make clean            # Remove tools and workspace
make clean-workspace  # Remove workspace only
```

## Simulation Modes

| Mode | Config Value | Use Case |
|------|--------------|----------|
| `FULLY_SIM` | `simulation_mode = FULLY_SIM` | **Testing, development** |
| `SIM_HARDWARE` | `simulation_mode = SIM_HARDWARE` | Simulated hardware behavior |
| `FULLY_INTRINSIC` | `simulation_mode = FULLY_INTRINSIC` | Real FPGA hardware |

**Always use `FULLY_SIM` for automated testing** - hardware is slow and errors waste significant time.

## Code Style

### Type Annotations
This project uses typed Python. All new code should include type annotations.

### Docstrings (Sphinx reST)
```python
def example_function(param1: str, param2: int) -> bool:
    """
    Short description of function.

    :param param1: Description of param1
    :param param2: Description of param2
    :returns: Description of return value
    :raises ValueError: When something is invalid
    """
```

### Architecture Patterns
- New circuit types: inherit from `Circuit` or `FileBasedCircuit` ABC
- New fitness functions: inherit from `FitnessFunction` ABC
- Configs use hierarchical INI: Specific → Base → `data/default_config.ini`

## Testing Guidelines

### Test Markers
- `@pytest.mark.immediate`: <10 seconds (runs on develop PRs)
- `@pytest.mark.short`: <60 seconds (runs on develop PRs)
- `@pytest.mark.long`: >1 minute (runs on main PRs)

### What to Test
1. Evolution completes N generations without crashing
2. Fitness values improve over generations
3. Config combinations work correctly
4. Output files created in expected formats
5. Specific fitness functions (e.g., max-ones) produce expected results

### Deterministic Testing
For stochastic operations, implement seeded randomness for reproducible results. This needs implementation - consider a random replacement object or seeded random for testing.

### Hardware Integration Tests (Planned)
When hardware is available, integration tests should verify end-to-end functionality before long experiments.

## Critical Areas - Human Review Required

### Bitstream Files (.asc)
Any modifications to `.asc` file handling or bitstream format require **extreme caution** and **mandatory human review**. Errors waste significant hardware testing time.

### Arduino Code (`data/ReadSignal/`, `data/oscillate/`)
Changes to Arduino sketches require **human review**. This code handles real-time signal measurement on the microcontroller.

## Git Workflow

### Branching
- Work on `develop` branch
- Merge to `main` for releases

### Commit Format (Conventional Commits)
```
feat: add new fitness function for frequency detection
fix: correct pulse counting overflow in Arduino sketch
test: add FULLY_SIM evolution completion test
docs: update configuration reference
refactor: extract common mutation logic
```

## Hardware Configuration

- **FPGA**: Lattice iCE40HX1K
- **Microcontroller**: Arduino Nano (5V)
- **Toolchain**: IceStorm (yosys, arachne-pnr, icepack, iceprog)

## Current Priorities

1. **Testing**: Expand test coverage using `FULLY_SIM` mode
2. **Documentation**: Extend Sphinx documentation
3. **Type Safety**: Add type annotations throughout codebase
4. **Fork Preparation**: Keep codebase clean and tested - a fork for a newer iCE40 model is planned

## Code Quality Baseline (January 2026)

Current state for tracking improvement progress:

| Tool | Count | Notes |
|------|-------|-------|
| Ruff Lint | 84 errors | Down from 1132 (93% reduction) |
| Ruff Format | 0 files | All formatted |
| Pyright | 122 errors | Type checking issues |

### Remaining Issues
- **SIM115**: Use context managers for file operations (~74 occurrences)
- **SIM102**: Nested if statements that could be combined
- **E711**: `== None` comparisons (use `is None`)
- **B007**: Unused loop variables
- **Types**: Module used as type instead of class (pyright)

See `docs/CODE_QUALITY_TODO.md` for detailed tracking.

### Code Quality Commands
```bash
ruff check src/                # Lint
ruff check src/ --fix          # Auto-fix lint issues
ruff format src/               # Format code
ruff format --check src/       # Check formatting
pyright src/                   # Type check
```

## Additional Documentation

| Topic | File |
|-------|------|
| Full setup guide | `README.md` |
| Raspberry Pi setup | `PiSetup.md` |
| Example configurations | `data/example_configs/` |
| API documentation | `docs/sphinx/` |
