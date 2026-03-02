# Sphinx Website & CI/CD TODO

Tracks tasks for completing the auto-generated Sphinx documentation website and GitHub Actions pipeline.

**Last Updated**: 2026-03-01

See [sphinx_website_and_ci.md](../docs/sphinx_website_and_ci.md) for full architectural context.

---

## Pending

_All tasks have been completed._

---

## Completed

### Add Docstrings to Source Modules
Added module-level, class, and method docstrings to all 19 source files in `src/`. NumPy-format, terse style. Hardware files include verification notes.
- **Completed**: 2026-03-01

### Wire Test Results into the Website
- CI downloads JUnit XML artifacts and converts them to HTML via `junit2html`
- HTML is embedded in the dev site via iframe in `docs/sphinx/source/dev/test_results.rst`
- `tests_failed` tag is now wired: CI checks `needs.RunTests.result` and passes `-t tests_failed` to sphinx-build when tests fail
- CI status badge added to `index.rst`
- **Completed**: 2026-03-01

### Fix Import Path Fragility in `conf.py`
Replaced `os.path.join(os.getcwd(), ...)` with `pathlib.Path(__file__).resolve()` relative paths. Removed `import os`.
- **Completed**: 2026-03-01

### Add Quickstart / Tutorial Documentation
Created `docs/sphinx/source/quickstart.rst` with Prerequisites, Installation, Running Tests, Architecture overview, Running an Experiment (with TrivialImplementation example), Interpreting Results, and Next Steps.
- **Completed**: 2026-03-01

### Fix 404 Page Rendering in Subdirectories
Added `sphinx-notfound-page` extension to `pyproject.toml` and `conf.py`. Configured `notfound_urls_prefix = '/BitstreamEvolution/'`. Removed the TODO from `404.rst`.
- **Completed**: 2026-03-01

### Fix Broken Grid Card Substitutions in `conf.py`
Removed dead `develop_grid_card` and `testing_grid_card` code and commented-out `rst_prolog` line. Added proper `sphinx_design` grid cards directly in `index.rst`.
- **Completed**: 2026-03-01

### Write ICE40 Hardware Model Guide
Created `docs/sphinx/source/architecture/ice40_hardware.rst` covering tile grid, ASC format, routing types, compilation flow. Includes verification notes.
- **Completed**: 2026-03-01

### Write Microcontroller Serial Protocol Specification
Created `docs/sphinx/source/architecture/mcu_protocol.rst` covering serial config, waveform/pulse protocols, error handling. Includes verification notes.
- **Completed**: 2026-03-01

### Install Graphviz in CI Workflow
Added `sudo apt-get install -y graphviz` step to `build-website` job before Sphinx builds.
- **Completed**: 2026-03-01

### Add Dependency Caching to GitHub Actions
Added `actions/cache@v4` for `~/.cache/pypoetry` keyed on `poetry.lock` hash.
- **Completed**: 2026-03-01

### Fix Hardcoded `@main` in Reusable Workflow Reference
Kept `@main` (GitHub Actions requires static ref for `uses:`). Added explanatory comment in workflow file documenting this constraint.
- **Completed**: 2026-03-01

### Switch from `force_orphan` to Incremental Deploys
Removed `force_orphan: true` from `peaceiris/actions-gh-pages` step. Each deploy now creates a new commit preserving history.
- **Completed**: 2026-03-01

### Additional items discovered and completed
- Added missing RST stub for `src/tools/generate_configs.py`
- Removed stale dependency-annoyance TODO from `code/index.rst` (fixed by path resolution change)
- Added `.nojekyll` to deployed site to prevent GitHub Pages Jekyll processing
- Pinned Python version to 3.11 in `build-website` job
- Added `_static/test-results/` directory and test results page to dev site toctree