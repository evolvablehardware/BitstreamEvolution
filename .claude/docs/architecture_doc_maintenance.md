# Architecture Documentation Maintenance

Guide for keeping the architecture docs current and knowing when to prompt the user to update them.

---

## When to Prompt for an Architecture Update

Suggest updating the architecture page when you observe any of the following in the codebase:

- **New protocols or major interfaces** added to `BitstreamEvolutionProtocols.py`
- **Evolution loop stage changes**: a stage added, removed, reordered, or renamed in `Evolution.py`
- **Hardware communication model changes**: new FPGA access modes, batch API changes, or new `Measurement` fields
- **Major refactors** that change how components interact (e.g., `GenerateMeasurements` now takes new inputs)
- **New data structures** that pass between evolution stages

When prompting the user, suggest:
1. Which section of the main architecture page should be updated or added
2. Whether any existing content is now outdated enough to archive

---

## Architecture Page Structure

`docs/sphinx/source/architecture/index.rst` holds the **current design** only.

| Section | Contents |
|---------|----------|
| Overview | Numbered list of data-flow steps through one generation; cross-refs to protocol docs |
| General Structure | Mermaid flowchart of the main loop |
| Component descriptions | One `===` section per evolution stage with a mermaid diagram and prose |
| Initial Proposal (pointer) | One-line `:doc:` link to the archived page |
| Early Design Ideas (pointer) | One-line `:doc:` link to the archived page |

Component description sections currently on the main page:

- Hardware Controller (two diagrams: batch API view and internal mechanics)
- Measurement Data Structure
- Individual Data Structure
- Population Representation
- Generation Metadata (i.e. 'Gen. Info')
- Experiment Structure
- Generation Info Factory (a.k.a. 'Incrementer')
- Generate Measurements / Evaluate Measurements / Evaluate Fitness / Reproduce / Generate Circuit
- Architectural Example (full worked pulse-count run, eight subsections)

---

## What Gets Archived vs. Updated In-Place

| Situation | Action |
|-----------|--------|
| A component's diagram is superseded by a new design | Update the diagram in-place on the main page |
| An entire architecture or proposal era is superseded | Archive to `historical/` |
| A new major proposal replaces the current design | Move current main-page content to `historical/`, rewrite the main page |
| Minor prose correction or clarification | Edit in-place |

**Rule of thumb**: if a future reader would be confused by outdated content sitting next to current content, archive it. If it is just an update to the same design, edit it in-place.

---

## How to Archive Content

1. **Create the page**: new `.rst` file in `docs/sphinx/source/architecture/historical/`. Match the heading style of `early_design_ideas.rst` — `===` for the page title, `---` for sections, `~~~` for subsections.

2. **Add to toctree**: in `historical/index.rst`, add the filename (no `.rst`) to the `.. toctree::` block. **Most recent archive goes at the top of the list.**

3. **Add timeline entry**: in `historical/index.rst`, under the `Timeline` section, add a new `~~~` entry **above** all existing entries (most recent first). Pattern:

   ```rst
   Entry Title
   ~~~~~~~~~~~

   *Brief context phrase (e.g. "Predates the current implementation.")*

   .. button-ref:: filename
      :ref-type: doc
      :color: primary
      :shadow:

   One paragraph: what this was, what it contributed, and why it was archived.
   ```

4. **Update main page**: replace the archived content with a one-line `:doc:` pointer. See the existing "Initial Proposal" and "Early Design Ideas" sections in `architecture/index.rst` as the pattern.

5. **Rebuild and verify**: `cd docs/sphinx && make html` (or `poetry run sphinx-build -b html source build/html`) — must be zero warnings before considering the task complete.

---

## Mermaid Diagram Conventions

The architecture page uses Mermaid (`sphinxcontrib-mermaid`) for all diagrams. Prefer Mermaid over static images for new diagrams.

**Node shapes**:
- `["text"]` — data node (population, measurement list, config)
- `[["text"]]` — process/subroutine node (algorithms, strategies)
- `{"text"}` — decision node (branching logic)
- `(["text"])` — terminal node (start/end/exit)
- `((" "))` — anonymous start node

**Arrow styles**:
- `==>` — primary data flow (thick)
- `-->` — secondary/config input (thin)
- `-.->` — reference/query (dashed, e.g. FPGA pool consulted by controller)

**Subgraph external inputs**:
- Inputs that are "consumed by" a subgraph process should point at the **subgraph boundary** using the subgraph ID as the edge target, not an internal node
- Exception: inputs whose entry point *is* semantically meaningful (e.g., Gen Info → first decision node of the Incrementer) may point directly at that internal node

**Autosectionlabel conflict avoidance**:
- The `autosectionlabel` extension creates a label from every section title in the build
- Duplicate titles anywhere within the same file cause build warnings
- The Architectural Example uses gerund forms ("Generating Measurements", "Evaluating Fitness", "Reproducing") to avoid clashing with the identically-named component-description sections
- When adding new sections, check for existing titles that could conflict and use a distinct phrasing if needed