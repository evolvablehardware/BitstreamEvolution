"""Sphinx extension that renders JUnit XML test results as native tables.

Provides two directives:

``.. junit-results:: path/to/file.xml``
    Renders a per-version summary + detail table from a single JUnit XML file.

``.. junit-overview::``
    Reads multiple JUnit XML files and renders a cross-version summary table
    with links to the per-version sections. Accepts ``:files:`` (semicolon-
    separated ``label;path`` pairs) and ``:link-prefix:`` options.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


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


def _make_row(col_nodes: list[nodes.Node], css_class: str = "") -> nodes.row:
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


# ── junit-overview directive ─────────────────────────────────────────

class JUnitOverviewDirective(Directive):
    """Cross-version summary table with links to per-version sections."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        # semicolon-separated "label;path" pairs, one per line
        "files": directives.unchanged_required,
        # prefix for internal anchor links (e.g. "python-")
        "link-prefix": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        src_dir = Path(env.srcdir)
        prefix = self.options.get("link-prefix", "python-")

        raw_files = self.options.get("files", "")
        entries: list[tuple[str, str]] = []
        for line in raw_files.strip().splitlines():
            line = line.strip()
            if ";" in line:
                label, path = line.split(";", 1)
                entries.append((label.strip(), path.strip()))

        if not entries:
            para = nodes.paragraph()
            para += nodes.emphasis(text="No test result files configured.")
            return [para]

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

        for label, rel_path in entries:
            xml_path = (src_dir / rel_path).resolve()
            suites = _parse_suites(xml_path)

            if suites is None:
                # File missing or unparseable — show placeholder row
                link_para = nodes.paragraph()
                link_para += nodes.Text(f"{label} — ")
                link_para += nodes.emphasis(text="no results")
                row = _make_row(
                    [link_para, "—", "—", "—", "—", "—", "—"],
                    css_class="junit-skip",
                )
                tbody += row
                continue

            stats = _aggregate(suites)

            # Build the label cell as an internal link
            anchor_id = prefix + label.replace(" ", "-").replace(".", "-").lower()
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

        return [table]


# ── junit-results directive ──────────────────────────────────────────

class JUnitResultsDirective(Directive):
    """Render a JUnit XML file as a summary row + detail table."""

    has_content = False
    required_arguments = 1  # path to the XML file
    optional_arguments = 0
    option_spec = {
        "title": directives.unchanged,
    }

    def _build_summary_table(self, stats: dict) -> nodes.table:
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

    def _build_detail_table(self, suites: list[ET.Element]) -> nodes.table:
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

                # Prepend suite name if it adds context
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

        result_nodes.append(self._build_summary_table(stats))
        result_nodes.append(self._build_detail_table(suites))

        return result_nodes


# ── Extension setup ──────────────────────────────────────────────────

def setup(app: Sphinx) -> dict:
    app.add_directive("junit-results", JUnitResultsDirective)
    app.add_directive("junit-overview", JUnitOverviewDirective)
    app.add_css_file("css/junit.css")
    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
