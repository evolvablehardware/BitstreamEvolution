"""Sphinx extension that renders JUnit XML test results as native tables.

Provides the ``.. junit-results::`` directive which reads a JUnit XML file
and produces summary + detail tables directly in the Sphinx document tree.

Usage in RST::

    .. junit-results:: _static/test-results/test-results-3.11.xml
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


class JUnitResultsDirective(Directive):
    """Render a JUnit XML file as Sphinx tables."""

    has_content = False
    required_arguments = 1  # path to the XML file
    optional_arguments = 0
    option_spec = {
        "title": directives.unchanged,
    }

    # ------------------------------------------------------------------
    # Table-building helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_row(col_texts: list[str], *, is_header: bool = False) -> nodes.row:
        row = nodes.row()
        for text in col_texts:
            entry = nodes.entry()
            entry += nodes.paragraph(text=text)
            row += entry
        return row

    def _build_summary_table(
        self, suites: list[ET.Element]
    ) -> nodes.table:
        """Build a summary table aggregating counts across all suites."""
        total = errors = failures = skipped = 0
        time_sum = 0.0
        for suite in suites:
            total += int(suite.get("tests", "0"))
            errors += int(suite.get("errors", "0"))
            failures += int(suite.get("failures", "0"))
            skipped += int(suite.get("skipped", "0"))
            time_sum += float(suite.get("time", "0"))

        passed = total - errors - failures - skipped

        headers = ["Total", "Passed", "Failed", "Errors", "Skipped", "Time (s)"]
        values = [
            str(total),
            str(passed),
            str(failures),
            str(errors),
            str(skipped),
            f"{time_sum:.2f}",
        ]

        table = nodes.table(classes=["junit-summary"])
        tgroup = nodes.tgroup(cols=len(headers))
        table += tgroup
        for _ in headers:
            tgroup += nodes.colspec(colwidth=1)

        thead = nodes.thead()
        tgroup += thead
        thead += self._make_row(headers, is_header=True)

        tbody = nodes.tbody()
        tgroup += tbody
        row = self._make_row(values)

        # Add CSS classes based on results
        if failures > 0 or errors > 0:
            row["classes"].append("junit-fail")
        else:
            row["classes"].append("junit-pass")

        tbody += row
        return table

    def _build_detail_table(
        self, suites: list[ET.Element]
    ) -> nodes.table:
        """Build a detail table listing every test case."""
        headers = ["Test Suite", "Test Name", "Status", "Time (s)", "Message"]
        table = nodes.table(classes=["junit-detail"])
        tgroup = nodes.tgroup(cols=len(headers))
        table += tgroup
        for _ in headers:
            tgroup += nodes.colspec(colwidth=1)

        thead = nodes.thead()
        tgroup += thead
        thead += self._make_row(headers, is_header=True)

        tbody = nodes.tbody()
        tgroup += tbody

        for suite in suites:
            suite_name = suite.get("name", "unknown")
            for case in suite.iter("testcase"):
                case_name = case.get("name", "unknown")
                time_val = case.get("time", "0")

                # Determine status
                failure = case.find("failure")
                error = case.find("error")
                skip = case.find("skipped")

                if failure is not None:
                    status = "FAILED"
                    message = failure.get("message", "")[:120]
                    css_class = "junit-fail"
                elif error is not None:
                    status = "ERROR"
                    message = error.get("message", "")[:120]
                    css_class = "junit-error"
                elif skip is not None:
                    status = "SKIPPED"
                    message = skip.get("message", "")[:120]
                    css_class = "junit-skip"
                else:
                    status = "PASSED"
                    message = ""
                    css_class = "junit-pass"

                row = self._make_row(
                    [suite_name, case_name, status, time_val, message]
                )
                row["classes"].append(css_class)
                tbody += row

        return table

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        rel_path = self.arguments[0]

        # Resolve relative to the Sphinx source directory
        src_dir = Path(env.srcdir)
        xml_path = (src_dir / rel_path).resolve()

        result_nodes: list[nodes.Node] = []

        title = self.options.get("title")
        if title:
            result_nodes.append(
                nodes.subtitle(text=title)
            )

        if not xml_path.exists():
            msg = f"No test results found at ``{rel_path}``. Results are populated by CI."
            para = nodes.paragraph()
            para += nodes.emphasis(text=msg)
            result_nodes.append(para)
            return result_nodes

        try:
            tree = ET.parse(xml_path)
        except ET.ParseError as exc:
            logger.warning("junit_results: failed to parse %s: %s", xml_path, exc)
            para = nodes.paragraph()
            para += nodes.emphasis(text=f"Failed to parse test results: {exc}")
            result_nodes.append(para)
            return result_nodes

        root = tree.getroot()

        # Handle both <testsuites><testsuite>...</testsuite></testsuites>
        # and bare <testsuite>...</testsuite> formats
        if root.tag == "testsuites":
            suites = list(root.iter("testsuite"))
            # Filter out nested testsuites (only top-level children)
            suites = [s for s in root.findall("testsuite")]
        elif root.tag == "testsuite":
            suites = [root]
        else:
            para = nodes.paragraph()
            para += nodes.emphasis(
                text=f"Unexpected XML root element: {root.tag}"
            )
            result_nodes.append(para)
            return result_nodes

        if not suites:
            para = nodes.paragraph()
            para += nodes.emphasis(text="No test suites found in XML file.")
            result_nodes.append(para)
            return result_nodes

        # Summary
        result_nodes.append(nodes.paragraph(text="Summary"))
        result_nodes.append(self._build_summary_table(suites))

        # Detail
        result_nodes.append(nodes.paragraph(text="Test Details"))
        result_nodes.append(self._build_detail_table(suites))

        return result_nodes


def setup(app: Sphinx) -> dict:
    app.add_directive("junit-results", JUnitResultsDirective)
    app.add_css_file("css/junit.css")
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
