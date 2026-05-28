# BitstreamEvolution

Evolutionary computation framework for FPGA bitstream evolution on ICE40 hardware.

## Project Purpose

This toolkit evolves digital circuits on FPGAs through genetic algorithms. Individuals represent bitstream configurations that are evaluated on physical hardware, with fitness determined by circuit behavior (oscillation counting, waveform analysis).

## Tech Stack

- **Language**: Python 3.11+
- **Package Manager**: Poetry
- **Testing**: pytest with custom markers (immediate/short/long)
- **Type Checking**: mypy
- **Hardware**: ICE40 FPGAs via IceStorm toolchain (`icepack`, `iceprog`)
- **Serial Communication**: pyserial for MCU communication
- **Result Types**: `returns` library for functional error handling

## Project Structure

```
src/
├── BitstreamEvolutionProtocols.py   # Core protocols/interfaces (start here)
├── Evolution.py                      # Main evolution loop orchestrator
├── TrivialImplementation.py          # Reference implementation for testing
├── Circuit/                          # Hardware circuit abstractions
│   ├── Circuit.py                    # Abstract base class
│   └── FileBasedCircuit.py           # ICE40 ASC file implementation
├── Individual/
│   └── BitstreamIndividual.py        # Genetic individual representation
├── Population/
│   └── PopulationInitialization.py   # Population factories and strategies
├── EvaluateFitness/                  # Fitness evaluation strategies
│   ├── EvaluateFitness.py            # Generic evaluator wrapper
│   ├── EvalPulseCountFitness.py      # Oscillation-based fitness
│   └── EvalVarMaxFitness.py          # Variance-based fitness
├── GenerateMeasurements/
│   └── GenerateMeasurements.py       # Measurement object factory
├── Hardware/
│   └── Microcontroller.py            # Serial FPGA communication
├── Logger.py                         # Logging with live plotting support
├── PlotDataRecorder.py               # Data collection for visualization
└── tools/                            # Utility scripts
test/
├── test_TrivialImplementation.py     # Comprehensive reference tests
├── test_BitstreamEvolutionProtocols.py
├── test_population.py
└── ...
```

## Essential Commands

```bash
# Install dependencies
poetry install                    # Default dependencies only
poetry install --with dev         # Include dev tools (docs, test, lint)

# Run tests
pytest                            # Run immediate tests (default, <10s)
pytest -m "immediate or short"    # Run tests under 60s
pytest -m "long"                  # Run long tests (>1min)
pytest --markers                  # View available markers

# Type checking
poetry run mypy src/

# Build documentation
cd docs/sphinx && make html
```

## Key Entry Points

- **Protocols**: [BitstreamEvolutionProtocols.py](src/BitstreamEvolutionProtocols.py) - All core interfaces
- **Evolution Loop**: [Evolution.py:33](src/Evolution.py#L33) - `run()` method
- **Reference Implementation**: [TrivialImplementation.py](src/TrivialImplementation.py) - Simplified testable version

## Testing Approach

Tests use pytest with three timing markers configured in [pyproject.toml:44-48](pyproject.toml#L44-L48):
- `immediate`: <10 seconds (default)
- `short`: <60 seconds
- `long`: >1 minute

Mocking pattern: Use `unittest.mock.Mock(spec=ProtocolClass)` for protocol implementations.

### AI Test Annotations

When writing or editing tests, always add an inline comment to the function signature:
- **New tests**: `def test_example():  # Written by AI`
- **Edited tests**: `def test_example():  # Edited by AI`

When editing an existing test, prompt the user with the proposed change and explain why it is being made before applying it.

## Configuration

- **pyproject.toml**: Poetry dependencies, pytest markers, Sphinx config
- **conftest.py**: Auto-applies default markers to unmarked tests
- **data/seed-hardware.asc**: Template ICE40 hardware file

## Additional Documentation

When working on specific areas, consult these files:

- [.claude/docs/architectural_patterns.md](.claude/docs/architectural_patterns.md) - Design patterns and conventions used throughout the codebase
- [.claude/docs/architecture_doc_maintenance.md](.claude/docs/architecture_doc_maintenance.md) - When and how to update the Sphinx architecture page; archiving guide; mermaid conventions
- [.claude/docs/test_plan.md](.claude/docs/test_plan.md) - Comprehensive test plan for interface validation and coverage gaps
- [.claude/todos/testing_todo.md](.claude/todos/testing_todo.md) - Progress tracker for test implementation
