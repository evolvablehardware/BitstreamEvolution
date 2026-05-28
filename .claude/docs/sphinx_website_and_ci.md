# Sphinx Website & GitHub Actions CI/CD

Documents the auto-generated Sphinx documentation website and the GitHub Actions pipeline that builds and deploys it.

**Last Updated**: 2026-03-01

---

## Deployment Overview

The website is hosted on **GitHub Pages** via a `gh-pages` branch. Two versions are deployed side-by-side:

| Version | URL (expected) | Source Branch | Sphinx Tag | Theme |
|---------|---------------|---------------|------------|-------|
| Release | `evolvablehardware.github.io/BitstreamEvolution/` | `main` | `-t release` | `sphinx_nefertiti` |
| Dev | `evolvablehardware.github.io/BitstreamEvolution/dev/` | `develop` | `-t dev` | `sphinx_book_theme` |

The deploy action (`peaceiris/actions-gh-pages@v3`) force-pushes an orphan commit to `gh-pages`, so each deploy replaces the entire site.

---

## GitHub Actions Pipeline (`initialize-push-workflows.yml`)

**Trigger**: Push to `main` or `develop`.

### Job 1: `PyprojectTOML`
- Calls reusable workflow `read-toml.yml` to extract config from `pyproject.toml`.
- Outputs: Python versions, pytest groups, test display settings, URLs.

### Job 2: `RunTests`
- **Depends on**: `PyprojectTOML`
- Matrix: Python 3.11-3.14 x pytest marker groups (`"immediate or short"`, `"long"`).
- Produces JUnit XML artifacts and posts results via `pmeier/pytest-results-action`.
- Uses dependency group: `poetry install --with gh_tests`

### Job 3: `build-website`
- **Depends on**: `RunTests` (but uses `if: always()` so it runs even if tests fail)
- Steps:
  1. Checkout `main` -> build with `-t release` -> copy to `.website/`
  2. Checkout `develop` -> build with `-t dev` -> copy to `.website/dev/`
  3. Deploy combined `.website/` to `gh-pages` branch
- Uses dependency group: `poetry install --with gh_docs --no-root`

### Environment Variables
```yaml
MAIN_BRANCH: 'main'
SECONDARY_BRANCH: 'develop'
TEMP_WEBSITE_FOLDER: '.website'
SECONDARY_SITE_DIRECTORY: 'dev'
```

---

## Sphinx Configuration (`docs/sphinx/source/conf.py`)

### Tag System
Tags control conditional content rendering:
- `dev` — Manually applied via `-t dev`; enables TODO display, uses dev theme/logo.
- `release` — Auto-applied if `dev` is not set.
- `html` — Always applied.
- `tests_failed` — Optional; switches logo to indicate test failures (not yet wired into CI).

### Key Extensions
| Extension | Purpose |
|-----------|---------|
| `autodoc` | Auto-generate API docs from docstrings |
| `napoleon` | NumPy-style docstring parsing |
| `todo` | TODO directives (only shown in dev builds) |
| `viewcode` | Source code links in API docs |
| `intersphinx` | Cross-links to Python, Sphinx, `returns` docs |
| `graphviz` | Diagrams (requires `dot` on PATH) |
| `inheritance_diagram` | Class hierarchy visualization |
| `sphinx_design` | Enhanced UI components (cards, grids, tabs) |
| `sphinxcontrib-mermaid` | Mermaid flowchart diagrams via `.. mermaid::` directive |

### Config Loaded from `pyproject.toml`
Under `[config.sphinx]`: project name, copyright, author, theme names, logo URLs.

### Path Setup
`conf.py` adds `src/` and the project root to `sys.path` so autodoc can import modules. This causes the import path dependency issue noted in `code/index.rst`.

---

## Documentation Source Structure

```
docs/sphinx/source/
├── conf.py               # Main Sphinx configuration
├── index.rst             # Landing page (release vs. develop indicator)
├── 404.rst               # Custom 404 (:orphan:)
├── architecture/
│   ├── index.rst         # Current architecture: overview, component diagrams, worked example
│   ├── images/           # Static diagram images (legacy; prefer mermaid for new diagrams)
│   ├── historical/
│   │   ├── index.rst     # Archive index with timeline (most recent → oldest)
│   │   ├── initial_proposal.rst   # First formal proposal (archived)
│   │   └── early_design_ideas.rst # Pre-proposal design sketches (archived)
│   └── hardware/
│       ├── index.rst     # Hardware architecture reference landing page
│       ├── ice40_hardware.rst
│       └── mcu_protocol.rst
├── code/
│   ├── index.rst         # API docs index (autodoc modules)
│   ├── BitstreamEvolutionProtocols.rst
│   ├── Evolution.rst
│   ├── TrivialImplementation.rst
│   ├── Circuit/          # Circuit module autodoc
│   ├── EvaluateFitness/  # Fitness evaluator autodoc
│   ├── GenerateMeasurements/
│   ├── Hardware/
│   ├── Individual/
│   ├── Population/
│   └── tools/            # pulse_histogram, reconstruct
└── dev/
    └── index.rst         # Dev-only build instructions
```

Total: ~32 RST files covering API autodoc for all `src/` modules.

---

## What Currently Works

1. **Dual-site deployment** — Main and develop branches build separately with different themes/tags and deploy to the same GitHub Pages site.
2. **Autodoc API generation** — All `src/` modules have corresponding RST stubs that invoke `.. automodule::`.
3. **Tag-based conditional content** — TODOs only appear on dev site; themes and logos switch per branch.
4. **Test matrix CI** — Tests run across Python versions with JUnit reporting.
5. **Config extraction from `pyproject.toml`** — Reusable workflow reads project metadata for CI.
6. **Architecture docs** — Current-design overview, per-component mermaid diagrams, a full worked example, and an archived historical section (`historical/`) with the initial proposal and early design ideas.
7. **Intersphinx** — Cross-links to Python stdlib, Sphinx, and `returns` library docs.

---

## What Is Missing or Incomplete

### High Priority

1. **Docstrings are missing from most source files** — Autodoc RST stubs exist but many modules lack docstrings, so the generated API pages are sparse or empty. This is tracked in [additional_documentation.md](../todos/additional_documentation.md).

2. **Test results not displayed on website** — There are TODOs in `index.rst` about displaying test results. The `tests_failed` tag exists in `conf.py` but is never set by the CI pipeline. The CI uploads JUnit XML artifacts but doesn't feed them back into the Sphinx build.

3. **Import path fragility** — `conf.py` uses relative `os.path.join(os.getcwd(), ...)` to find `src/`. The `code/index.rst` has a TODO about this being brittle when Sphinx runs from different directories. Works in CI but is error-prone locally.

### Medium Priority

4. **No usage/tutorial documentation** — The site has architecture docs and API reference but no user-facing guides (installation, quickstart, how to run an evolution experiment).

5. **404 page formatting** — A TODO in `404.rst` notes it doesn't render correctly in subdirectories (the `/dev/` path).

6. **Broken grid card substitutions in `conf.py`** — Lines 163-176 define `develop_grid_card` and `testing_grid_card` RST substitutions that are commented out in `rst_prolog`/`rst_epilog` and appear to have typos (e.g., `grig-item-card`).

7. **ICE40 hardware documentation** — Tracked in [additional_documentation.md](../todos/additional_documentation.md) but no RST page exists for it yet.

8. **Microcontroller protocol documentation** — Also tracked but not yet written.

### Low Priority

9. **`graphviz` requires `dot` on PATH** — CI runners may not have Graphviz installed. If any RST files use `.. graphviz::` directives, builds could fail. Currently no explicit `apt install graphviz` step in the workflow.

10. **Hardcoded workflow reference** — `read-toml.yml` is referenced as `evolvablehardware/BitstreamEvolution/.github/workflows/read-toml.yml@main`, which means the `main` branch version of the reusable workflow is always used even when `develop` is pushed.

11. **No build caching** — The CI installs Poetry and all dependencies from scratch on every run. Adding dependency caching would speed up builds.

12. **`force_orphan: true` loses deploy history** — Every deploy replaces the entire `gh-pages` branch with a single orphan commit, so there's no history of previous deployments.

---

## Suggested Next Steps (in priority order)

1. **Add docstrings to source modules** — This is the single highest-impact improvement since the autodoc infrastructure already exists. Focus on protocols and public APIs first.
2. **Wire test results into the website** — Either embed JUnit results in the Sphinx build (e.g., via a custom extension or static HTML include) or link to GitHub Actions summaries.
3. **Add a quickstart/tutorial page** — Even a brief RST page explaining how to install, configure, and run an experiment would make the docs much more useful.
4. **Fix the `tests_failed` tag pipeline** — Have the CI conditionally pass `-t tests_failed` to the Sphinx build when tests fail, so the logo changes.
5. **Install Graphviz in CI** if any diagrams use the `graphviz` directive.
6. **Add dependency caching** to the GitHub Actions workflow for faster builds.