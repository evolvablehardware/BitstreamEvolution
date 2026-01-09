# Installation Guide for Claude Code Users

This guide helps Claude Code users quickly set up BitstreamEvolution for development and testing.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Tested with 3.10, 3.11, 3.12, 3.13 |
| Poetry | Latest | Python dependency manager |
| Git | Any | For cloning the repository |

## Quick Start (FULLY_SIM - No Hardware Required)

FULLY_SIM mode runs the genetic algorithm with simulated fitness evaluation. No FPGA or Arduino hardware is needed.

### Windows

```powershell
# 1. Clone the repository (if not already done)
git clone https://github.com/evolvablehardware/BitstreamEvolution.git
cd BitstreamEvolution

# 2. Install Poetry (if not installed)
pip install poetry

# 3. Update lock file (if pyproject.toml was modified)
python -m poetry lock

# 4. Install dependencies
python -m poetry install --with dev

# 5. Create workspace directory
python -c "import os; os.makedirs('workspace', exist_ok=True)"

# 6. Run a FULLY_SIM experiment
python -m poetry run python src/evolve.py -c data/example_configs/sim.ini -d "Test run"
```

### Linux

```bash
# 1. Clone the repository (if not already done)
git clone https://github.com/evolvablehardware/BitstreamEvolution.git
cd BitstreamEvolution

# 2. Install Poetry (if not installed)
# Option A: pipx (recommended)
pipx install poetry
# Option B: Official installer
curl -sSL https://install.python-poetry.org | python3 -

# 3. Update lock file (if pyproject.toml was modified)
poetry lock

# 4. Install dependencies
poetry install --with dev

# 5. Initialize workspace (Linux has make support)
make init

# 6. Run a FULLY_SIM experiment
poetry run python src/evolve.py -c data/example_configs/sim.ini -d "Test run"
```

## Running an Experiment

### Basic Commands

```bash
# Run with default sim config (500 generations)
poetry run python src/evolve.py -c data/example_configs/sim.ini -d "Description"

# Run with custom config
poetry run python src/evolve.py -c path/to/your/config.ini -d "Description"

# Test mode (prints actions without running)
poetry run python src/evolve.py -c data/example_configs/sim.ini -p
```

### Quick Test Config

For faster verification, create a quick test config with fewer generations:

```ini
# data/example_configs/quick_test.ini
[TOP-LEVEL PARAMETERS]
simulation_mode = FULLY_SIM
base_config = data/default_config.ini

[GA PARAMETERS]
population_size = 10
generations = 10

[FITNESS PARAMETERS]
fitness_func = VARIANCE
```

Then run:
```bash
poetry run python src/evolve.py -c data/example_configs/quick_test.ini -d "Quick test"
```

## Verification

After running an experiment, check the `workspace/` directory:

| File/Directory | Purpose |
|----------------|---------|
| `log` | Detailed experiment log |
| `bestlivedata.log` | Best fitness per generation |
| `experiment_asc/` | Circuit bitstream files |
| `experiment_data/` | Measurement data |
| `builtconfig.ini` | Final resolved configuration |

## Full Hardware Setup (Linux Only)

For real FPGA experiments on Linux:

```bash
# Install system dependencies (Debian/Ubuntu)
sudo apt update
sudo apt install build-essential clang bison flex libreadline-dev gawk \
  tcl-dev libffi-dev libftdi-dev git pkg-config python3 python3-pip \
  libboost-all-dev cmake make

# Build FPGA toolchain (IceStorm)
make icestorm-tools

# Set up USB permissions
make udev-rules
sudo usermod -a -G dialout $USER

# Logout and login for group changes to take effect
```

### Arduino Setup

```bash
# Install Arduino CLI
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# Install Arduino core
arduino-cli update
arduino-cli core install arduino:avr

# Compile and upload firmware
arduino-cli compile -b arduino:avr:nano data/ReadSignal/ReadSignal.ino
arduino-cli upload -b arduino:avr:nano -p /dev/ttyUSB0 data/ReadSignal/ReadSignal.ino
```

## Troubleshooting

### Windows Issues

| Problem | Solution |
|---------|----------|
| `poetry` not found | Use `python -m poetry` instead |
| Lock file error | Run `python -m poetry lock` first |
| `python3` not found | Scripts may need editing; use `python` on Windows |
| Backup directory fails | Windows doesn't allow `:` in filenames; workspace backup may fail |

### Linux Issues

| Problem | Solution |
|---------|----------|
| Permission denied on USB | Run `make udev-rules` and add user to `dialout` group |
| `make` not found | Install build-essential: `sudo apt install build-essential` |
| Poetry not in PATH | Add `~/.local/bin` to PATH or use pipx |

### General Issues

| Problem | Solution |
|---------|----------|
| Module not found | Ensure you're using `poetry run python` |
| Config not found | Check path is relative to project root |
| Interactive prompt fails | Use `-d "description"` flag to avoid stdin prompt |

## Code Quality Commands

```bash
# Lint code
poetry run ruff check src/

# Auto-fix lint issues
poetry run ruff check src/ --fix

# Format code
poetry run ruff format src/

# Type check
poetry run pyright src/

# Run tests
poetry run pytest -m immediate        # Fast tests
poetry run pytest -m "immediate or short"  # All quick tests
```

## Claude Code Tips

### Useful Commands for Claude Code Sessions

```bash
# Check Python and Poetry are working
cmd.exe /c "python --version"          # Windows
python3 --version                       # Linux

# Run Poetry commands on Windows
cmd.exe /c "python -m poetry install --with dev"
cmd.exe /c "python -m poetry run python src/evolve.py -c data/example_configs/sim.ini -d 'Test'"

# Run Poetry commands on Linux
poetry install --with dev
poetry run python src/evolve.py -c data/example_configs/sim.ini -d "Test"
```

### Environment Notes

- **Windows (MSYS2/MinGW64)**: Use `cmd.exe /c "python ..."` for Python commands
- **Windows PATH**: Python scripts may be in user-local Scripts folder, not global PATH
- **Linux**: Standard Poetry commands work directly

### Simulation Modes

| Mode | Config Value | Use Case |
|------|--------------|----------|
| `FULLY_SIM` | `simulation_mode = FULLY_SIM` | Testing, development (no hardware) |
| `SIM_HARDWARE` | `simulation_mode = SIM_HARDWARE` | Simulated hardware behavior |
| `FULLY_INTRINSIC` | `simulation_mode = FULLY_INTRINSIC` | Real FPGA hardware |

**Always use `FULLY_SIM` for automated testing** - hardware experiments are slow.

## Additional Resources

| Resource | Location |
|----------|----------|
| Full documentation | `README.md` |
| Raspberry Pi setup | `PiSetup.md` |
| Example configs | `data/example_configs/` |
| API documentation | `docs/sphinx/` |
| Default config reference | `data/default_config.ini` |
