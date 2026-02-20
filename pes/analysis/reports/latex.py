# pes/analysis/reports/latex.py

"""LaTeX report generator for conference submission."""

from pathlib import Path

from .base import BaseReportGenerator
from .schemas import ExperimentReport


class LaTeXReportGenerator(BaseReportGenerator):
    """
    Generate LaTeX reports formatted for ICSE/FSE submission.

    Uses ACM conference template style.
    """

    @property
    def file_extension(self) -> str:
        return "tex"

    def generate(self, report: ExperimentReport) -> Path:
        """Generate LaTeX report."""

        latex = self._build_latex(report)

        output_path = self._get_output_path(report)
        output_path.write_text(latex)

        return output_path

    def _build_latex(self, report: ExperimentReport) -> str:
        """Build LaTeX document."""
        # Pre-compute list items to avoid backslash issues in f-strings
        limitations_items = self._render_itemize(report.limitations)
        findings_items = self._render_itemize(report.key_findings)
        recommendations_items = self._render_itemize(report.recommendations)

        return f'''\\documentclass[sigconf]{{acmart}}

\\begin{{document}}

\\title{{{report.experiment_name}}}

\\begin{{abstract}}
{report.summary}
\\end{{abstract}}

\\maketitle

\\section{{Introduction}}
% TODO: Add introduction

\\section{{Methodology}}
{self._escape_latex(report.methodology)}

\\textbf{{Sample Size:}} {report.sample_size}

\\textbf{{Models Tested:}} {', '.join(report.models_tested)}

\\section{{Results}}

{self._render_tables_latex(report.tables)}

\\subsection{{Statistical Analysis}}
{self._render_stats_latex(report.statistical_results)}

\\section{{Discussion}}
{self._escape_latex(report.discussion)}

\\subsection{{Limitations}}
\\begin{{itemize}}
{limitations_items}
\\end{{itemize}}

\\section{{Conclusion}}
\\textbf{{Key Findings:}}
\\begin{{itemize}}
{findings_items}
\\end{{itemize}}

\\textbf{{Recommendations:}}
\\begin{{itemize}}
{recommendations_items}
\\end{{itemize}}

\\end{{document}}
'''

    def _render_itemize(self, items: list) -> str:
        """Render list items for LaTeX itemize environment."""
        result = []
        for item in items:
            result.append("  \\item " + self._escape_latex(item))
        return "\n".join(result)

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _render_tables_latex(self, tables) -> str:
        """Render tables as LaTeX."""
        parts = []
        for table in tables:
            cols = 'l' * len(table.headers)
            latex = f'''\\begin{{table}}[h]
\\centering
\\caption{{{self._escape_latex(table.title)}}}
\\begin{{tabular}}{{{cols}}}
\\hline
{' & '.join(self._escape_latex(h) for h in table.headers)} \\\\
\\hline
'''
            for row in table.rows:
                latex += ' & '.join(self._escape_latex(str(c)) for c in row) + ' \\\\\n'
            latex += '''\\hline
\\end{tabular}
\\end{table}
'''
            parts.append(latex)
        return '\n'.join(parts)

    def _render_stats_latex(self, results) -> str:
        """Render statistical results as LaTeX."""
        lines = []
        for r in results:
            line = f"\\textbf{{{r.test_name}:}} "
            line += f"statistic = {r.statistic:.3f}, $p$ = {r.p_value:.4f}"
            if r.effect_size:
                line += f", effect size = {r.effect_size:.3f}"
                if r.effect_interpretation:
                    line += f" ({r.effect_interpretation})"
            lines.append(line + "\n\n")
        return ''.join(lines)
