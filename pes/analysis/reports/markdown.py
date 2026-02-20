# pes/analysis/reports/markdown.py

"""Markdown report generator."""

from pathlib import Path
from typing import List

from .base import BaseReportGenerator
from .schemas import ExperimentReport, TableData, StatisticalResult


class MarkdownReportGenerator(BaseReportGenerator):
    """
    Generate publication-quality Markdown reports.

    Output is compatible with GitHub, Pandoc, and academic tools.
    """

    @property
    def file_extension(self) -> str:
        return "md"

    def generate(self, report: ExperimentReport) -> Path:
        """Generate Markdown report."""
        lines = []

        # Title and metadata
        lines.append(f"# {report.experiment_name}")
        lines.append("")
        lines.append(f"**Experiment ID:** {report.experiment_id}")
        lines.append(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(report.summary)
        lines.append("")

        # Key Findings
        lines.append("### Key Findings")
        lines.append("")
        for finding in report.key_findings:
            lines.append(f"- {finding}")
        lines.append("")

        # Recommendations
        lines.append("### Recommendations")
        lines.append("")
        for rec in report.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

        # Methodology
        lines.append("## Methodology")
        lines.append("")
        lines.append(report.methodology)
        lines.append("")
        lines.append(f"**Sample Size:** {report.sample_size}")
        lines.append(f"**Models Tested:** {', '.join(report.models_tested)}")
        lines.append("")

        # Results - Tables
        lines.append("## Results")
        lines.append("")

        for table in report.tables:
            lines.extend(self._render_table(table))
            lines.append("")

        # Statistical Results
        lines.append("### Statistical Analysis")
        lines.append("")
        lines.extend(self._render_statistical_results(report.statistical_results))
        lines.append("")

        # Discussion
        lines.append("## Discussion")
        lines.append("")
        lines.append(report.discussion)
        lines.append("")

        # Limitations
        lines.append("### Limitations")
        lines.append("")
        for limitation in report.limitations:
            lines.append(f"- {limitation}")
        lines.append("")

        # Write to file
        output_path = self._get_output_path(report)
        output_path.write_text("\n".join(lines))

        return output_path

    def _render_table(self, table: TableData) -> List[str]:
        """Render table as Markdown."""
        lines = []

        if table.title:
            lines.append(f"**Table: {table.title}**")
            lines.append("")

        # Header row
        lines.append("| " + " | ".join(table.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(table.headers)) + " |")

        # Data rows
        for row in table.rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        if table.caption:
            lines.append("")
            lines.append(f"*{table.caption}*")

        return lines

    def _render_statistical_results(self, results: List[StatisticalResult]) -> List[str]:
        """Render statistical results as formatted text."""
        lines = []

        for result in results:
            line = f"**{result.test_name}:** "
            line += f"statistic = {result.statistic:.3f}, "
            line += f"*p* = {result.p_value:.4f}"

            if result.effect_size is not None:
                line += f", effect size = {result.effect_size:.3f}"
                if result.effect_interpretation:
                    line += f" ({result.effect_interpretation})"

            if result.confidence_interval:
                line += f", 95% CI [{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]"

            lines.append(line)
            lines.append("")

        return lines
