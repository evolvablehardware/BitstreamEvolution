"""Sphinx extension that renders JUnit XML test results as native tables.

Provides three directives:

``.. junit-results:: path/to/file.xml``
    Renders a summary + detail table from a single JUnit XML file.

``.. junit-overview::``
    Reads multiple JUnit XML files and renders a cross-version summary table.
    Accepts ``:files:`` option or ``:directory:`` for auto-discovery.

``.. junit-test-results:: path/to/directory``
    Auto-discovers all ``test-results-*.xml`` files in the given directory,
    renders a cross-version overview table at the top, then a per-version
    section with summary + detail for each discovered file.  Files are
    grouped by Python version and test group (e.g.
    ``test-results-3.11-immediate-or-short.xml``).  This is the recommended
    single-directive approach — the page content adapts automatically when
    Python versions or test groups change in CI.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

# Matches test-results-3.11-immediate-or-short.xml
# Group 1 = version ("3.11"), Group 2 = group slug ("immediate-or-short")
_FILE_RE = re.compile(r"test-results-(\d+\.\d+)-(.+?)\.xml$")

# Fallback: matches the old merged format test-results-3.11.xml
_VERSION_ONLY_RE = re.compile(r"test-results-(\d+\.\d+)\.xml$")


# ── Helpers ──────────────────────────────────────────────────────────

def _parse_suites(xml_path: Path) -> list[ET.Element] | None:
    """Parse a JUnit XML file and return its top-level <testsuite> elements."""
    if not xml_path.exists():
        return None
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        logger.warning("junit_results: failed to parse %s: %s", xml_path, exc)
        return None

    root = tree.getroot()
    if root.tag == "testsuites":
        return list(root.findall("testsuite"))
    elif root.tag == "testsuite":
        return [root]
    return None


def _aggregate(suites: list[ET.Element]) -> dict[str, int | float]:
    """Aggregate counts across suites."""
    total = errors = failures = skipped = 0
    time_sum = 0.0
    for s in suites:
        total += int(s.get("tests", "0"))
        errors += int(s.get("errors", "0"))
        failures += int(s.get("failures", "0"))
        skipped += int(s.get("skipped", "0"))
        time_sum += float(s.get("time", "0"))
    passed = total - errors - failures - skipped
    return {
        "total": total,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "time": time_sum,
    }


def _discover_grouped_xml_files(
    directory: Path,
) -> list[tuple[str, list[tuple[str, Path]]]]:
    """Find test-results-*.xml files, return (version, [(group_slug, path)...]) pairs.

    Files matching ``test-results-{ver}-{group}.xml`` are grouped by version.
    Files matching the old ``test-results-{ver}.xml`` format are returned as
    a single group with slug ``""`` (empty string) for backwards compatibility.

    Returns a sorted list of ``(version, group_files)`` tuples.
    """
    if not directory.is_dir():
        return []

    by_version: dict[str, list[tuple[str, Path]]] = {}
    for f in sorted(directory.glob("test-results-*.xml")):
        m = _FILE_RE.search(f.name)
        if m:
            ver, group_slug = m.group(1), m.group(2)
            by_version.setdefault(ver, []).append((group_slug, f))
        else:
            m2 = _VERSION_ONLY_RE.search(f.name)
            if m2:
                ver = m2.group(1)
                by_version.setdefault(ver, []).append(("", f))

    return sorted(by_version.items(), key=lambda x: x[0])


def _discover_flat_xml_files(directory: Path) -> list[tuple[str, Path]]:
    """Find test-results-*.xml files and return flat (version, path) pairs.

    Used by the ``junit-overview`` directive which only needs a flat list.
    Multiple files for the same version are returned as separate entries.
    """
    if not directory.is_dir():
        return []
    results: list[tuple[str, Path]] = []
    for f in sorted(directory.glob("test-results-*.xml")):
        m = _FILE_RE.search(f.name)
        if m:
            results.append((m.group(1), f))
        else:
            m2 = _VERSION_ONLY_RE.search(f.name)
            if m2:
                results.append((m2.group(1), f))
    return results


def _slug_to_label(slug: str) -> str:
    """Convert a sanitized group slug back to a display label.

    ``"immediate-or-short"`` → ``"Immediate or Short"``
    ``""`` → ``"All Tests"``
    """
    if not slug:
        return "All Tests"
    return slug.replace("-", " ").title()


def _make_row(col_nodes: list[nodes.Node | str], css_class: str = "") -> nodes.row:
    """Build a table row from a list of cell content nodes."""
    row = nodes.row()
    if css_class:
        row["classes"].append(css_class)
    for node in col_nodes:
        entry = nodes.entry()
        if isinstance(node, str):
            entry += nodes.paragraph(text=node)
        else:
            entry += node
        row += entry
    return row


def _status_class(stats: dict) -> str:
    if stats["failures"] > 0 or stats["errors"] > 0:
        return "junit-fail"
    return "junit-pass"


def _version_to_anchor(version: str) -> str:
    """Convert a version string like '3.11' to a stable anchor ID."""
    return f"python-{version.replace('.', '-')}"


def _group_anchor_id(version: str, slug: str) -> str:
    """Create a stable anchor ID for a per-group sub-section."""
    if slug:
        return f"python-{version.replace('.', '-')}-{slug}"
    return _version_to_anchor(version)


def _build_overview_table(
    entries: list[tuple[str, dict | None]],
) -> nodes.table:
    """Build a cross-version summary table."""
    headers = ["Python Version", "Total", "Passed", "Failed",
                "Errors", "Skipped", "Time (s)"]
    table = nodes.table(classes=["junit-overview"])
    tgroup = nodes.tgroup(cols=len(headers))
    table += tgroup
    for _ in headers:
        tgroup += nodes.colspec(colwidth=1)

    thead = nodes.thead()
    tgroup += thead
    hrow = nodes.row()
    for h in headers:
        entry = nodes.entry()
        entry += nodes.paragraph(text=h)
        hrow += entry
    thead += hrow

    tbody = nodes.tbody()
    tgroup += tbody

    for version, stats in entries:
        anchor_id = _version_to_anchor(version)
        label = f"Python {version}"

        if stats is None:
            link_para = nodes.paragraph()
            link_para += nodes.Text(f"{label} — ")
            link_para += nodes.emphasis(text="no results")
            row = _make_row(
                [link_para, "—", "—", "—", "—", "—", "—"],
                css_class="junit-skip",
            )
        else:
            link_para = nodes.paragraph()
            ref = nodes.reference("", label, refuri=f"#{anchor_id}")
            link_para += ref
            row = _make_row(
                [
                    link_para,
                    str(stats["total"]),
                    str(stats["passed"]),
                    str(stats["failures"]),
                    str(stats["errors"]),
                    str(stats["skipped"]),
                    f"{stats['time']:.2f}",
                ],
                css_class=_status_class(stats),
            )
        tbody += row

    return table


def _build_summary_table(stats: dict) -> nodes.table:
    """Build a per-version summary table."""
    headers = ["Total", "Passed", "Failed", "Errors", "Skipped", "Time (s)"]
    values = [
        str(stats["total"]),
        str(stats["passed"]),
        str(stats["failures"]),
        str(stats["errors"]),
        str(stats["skipped"]),
        f"{stats['time']:.2f}",
    ]

    table = nodes.table(classes=["junit-summary"])
    tgroup = nodes.tgroup(cols=len(headers))
    table += tgroup
    for _ in headers:
        tgroup += nodes.colspec(colwidth=1)

    thead = nodes.thead()
    tgroup += thead
    hrow = nodes.row()
    for h in headers:
        entry = nodes.entry()
        entry += nodes.paragraph(text=h)
        hrow += entry
    thead += hrow

    tbody = nodes.tbody()
    tgroup += tbody
    row = _make_row(values, css_class=_status_class(stats))
    tbody += row
    return table


def _build_detail_table(suites: list[ET.Element]) -> nodes.table:
    """Detail table: Test Name, Status, Time, Message (4 cols)."""
    headers = ["Test Name", "Status", "Time (s)", "Message"]
    table = nodes.table(classes=["junit-detail"])
    tgroup = nodes.tgroup(cols=len(headers))
    table += tgroup
    for _ in headers:
        tgroup += nodes.colspec(colwidth=1)

    thead = nodes.thead()
    tgroup += thead
    hrow = nodes.row()
    for h in headers:
        entry = nodes.entry()
        entry += nodes.paragraph(text=h)
        hrow += entry
    thead += hrow

    tbody = nodes.tbody()
    tgroup += tbody

    for suite in suites:
        suite_name = suite.get("name", "")
        for case in suite.iter("testcase"):
            case_name = case.get("name", "unknown")
            time_val = case.get("time", "0")

            classname = case.get("classname", "")
            if classname and classname != suite_name:
                display_name = f"{classname}::{case_name}"
            else:
                display_name = case_name

            failure = case.find("failure")
            error = case.find("error")
            skip = case.find("skipped")

            if failure is not None:
                status, message = "FAILED", failure.get("message", "")[:200]
                css_class = "junit-fail"
            elif error is not None:
                status, message = "ERROR", error.get("message", "")[:200]
                css_class = "junit-error"
            elif skip is not None:
                status, message = "SKIPPED", skip.get("message", "")[:200]
                css_class = "junit-skip"
            else:
                status, message = "PASSED", ""
                css_class = "junit-pass"

            row = _make_row(
                [display_name, status, time_val, message],
                css_class=css_class,
            )
            tbody += row

    return table


# ── junit-test-results directive (auto-discovery) ────────────────────

class JUnitTestResultsDirective(Directive):
    """Auto-discover XML files and render a full test results page.

    Discovers files matching ``test-results-{ver}-{group}.xml`` (and the
    legacy ``test-results-{ver}.xml`` format), groups them by Python version,
    and renders:

    1. An **Overview** section with a cross-version summary table (aggregated
       across all test groups).
    2. A **Python {ver}** section for each version, containing a sub-section
       per test group with its own summary and detail tables.

    All sections use ``nodes.section()`` so they appear in the Sphinx TOC.

    Usage::

        .. junit-test-results:: _static/test-results
    """

    has_content = False
    required_arguments = 1  # directory path relative to source
    optional_arguments = 0
    option_spec = {}

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        src_dir = Path(env.srcdir)
        rel_dir = self.arguments[0]
        xml_dir = (src_dir / rel_dir).resolve()

        discovered = _discover_grouped_xml_files(xml_dir)

        if not discovered:
            para = nodes.paragraph()
            para += nodes.emphasis(
                text="No test results found. Results are populated by CI."
            )
            return [para]

        # ── Build data structures ──
        # overview_entries: one row per version, stats aggregated across groups
        # version_data: parsed per-group data for detail sections
        overview_entries: list[tuple[str, dict | None]] = []
        version_data: list[tuple[str, list[tuple[str, list[ET.Element], dict]]]] = []

        for version, group_files in discovered:
            all_suites: list[ET.Element] = []
            group_data: list[tuple[str, list[ET.Element], dict]] = []

            for slug, xml_path in group_files:
                suites = _parse_suites(xml_path)
                if suites:
                    stats = _aggregate(suites)
                    group_data.append((slug, suites, stats))
                    all_suites.extend(suites)

            if all_suites:
                agg_stats = _aggregate(all_suites)
                overview_entries.append((version, agg_stats))
                version_data.append((version, group_data))
            else:
                overview_entries.append((version, None))

        result_nodes: list[nodes.Node] = []

        # ── Overview section ──
        overview_section = nodes.section(ids=["test-results-overview"])
        overview_section += nodes.title(text="Overview")
        overview_section += _build_overview_table(overview_entries)
        result_nodes.append(overview_section)

        # ── Per-version sections ──
        for version, group_data in version_data:
            ver_anchor = _version_to_anchor(version)
            ver_section = nodes.section(ids=[ver_anchor])
            ver_section += nodes.title(text=f"Python {version}")

            if len(group_data) == 1 and group_data[0][0] == "":
                # Legacy single-file format — no sub-sections needed
                _, suites, stats = group_data[0]
                ver_section += _build_summary_table(stats)
                ver_section += _build_detail_table(suites)
            else:
                for slug, suites, stats in group_data:
                    group_anchor = _group_anchor_id(version, slug)
                    group_label = _slug_to_label(slug)
                    grp_section = nodes.section(ids=[group_anchor])
                    grp_section += nodes.title(
                        text=f"Python {version} — {group_label}"
                    )
                    grp_section += _build_summary_table(stats)
                    grp_section += _build_detail_table(suites)
                    ver_section += grp_section

            result_nodes.append(ver_section)

        return result_nodes


# ── junit-overview directive (explicit file list) ────────────────────

class JUnitOverviewDirective(Directive):
    """Cross-version summary table from an explicit file list or directory."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        "files": directives.unchanged,
        "directory": directives.unchanged,
        "link-prefix": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        src_dir = Path(env.srcdir)

        entries: list[tuple[str, Path]] = []

        # Option 1: auto-discover from directory
        directory = self.options.get("directory")
        if directory:
            xml_dir = (src_dir / directory.strip()).resolve()
            entries = _discover_flat_xml_files(xml_dir)

        # Option 2: explicit file list
        if not entries:
            raw_files = self.options.get("files", "")
            for line in raw_files.strip().splitlines():
                line = line.strip()
                if ";" in line:
                    label, path = line.split(";", 1)
                    m = re.search(r"(\d+\.\d+)", label)
                    version = m.group(1) if m else label.strip()
                    entries.append((version, (src_dir / path.strip()).resolve()))

        if not entries:
            para = nodes.paragraph()
            para += nodes.emphasis(text="No test result files found.")
            return [para]

        # Aggregate per version (may have multiple files per version)
        by_version: dict[str, list[ET.Element]] = {}
        for version, xml_path in entries:
            suites = _parse_suites(xml_path)
            if suites:
                by_version.setdefault(version, []).extend(suites)

        overview_entries: list[tuple[str, dict | None]] = []
        for version in sorted(by_version.keys()):
            overview_entries.append((version, _aggregate(by_version[version])))

        # Include versions with no results
        all_versions = sorted(set(v for v, _ in entries))
        for v in all_versions:
            if v not in by_version:
                overview_entries.append((v, None))
        overview_entries.sort(key=lambda x: x[0])

        return [_build_overview_table(overview_entries)]


# ── junit-results directive (single file) ────────────────────────────

class JUnitResultsDirective(Directive):
    """Render a JUnit XML file as a summary row + detail table."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "title": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        rel_path = self.arguments[0]
        src_dir = Path(env.srcdir)
        xml_path = (src_dir / rel_path).resolve()

        result_nodes: list[nodes.Node] = []

        title = self.options.get("title")
        if title:
            result_nodes.append(nodes.subtitle(text=title))

        if not xml_path.exists():
            para = nodes.paragraph()
            para += nodes.emphasis(
                text=f"No test results found at ``{rel_path}``. "
                     "Results are populated by CI."
            )
            result_nodes.append(para)
            return result_nodes

        suites = _parse_suites(xml_path)
        if suites is None or not suites:
            para = nodes.paragraph()
            para += nodes.emphasis(text="No test suites found in XML file.")
            result_nodes.append(para)
            return result_nodes

        stats = _aggregate(suites)
        result_nodes.append(_build_summary_table(stats))
        result_nodes.append(_build_detail_table(suites))
        return result_nodes


# ── Extension setup ──────────────────────────────────────────────────

def setup(app: Sphinx) -> dict:
    app.add_directive("junit-results", JUnitResultsDirective)
    app.add_directive("junit-overview", JUnitOverviewDirective)
    app.add_directive("junit-test-results", JUnitTestResultsDirective)
    app.add_css_file("css/junit.css")
    app.add_js_file("js/scrollspy-fix.js")
    return {
        "version": "0.5",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
