# pes/analysis/reports/html.py

"""HTML report generator with interactive visualizations."""

from pathlib import Path

from .base import BaseReportGenerator
from .schemas import ExperimentReport
from .visualizations import generate_plot_html


class HTMLReportGenerator(BaseReportGenerator):
    """
    Generate HTML reports with embedded visualizations.

    Uses Chart.js for interactive plots.
    """

    @property
    def file_extension(self) -> str:
        return "html"

    def generate(self, report: ExperimentReport) -> Path:
        """Generate HTML report."""

        # Generate plot data
        plots_html = []
        for i, figure in enumerate(report.figures):
            plot_html = generate_plot_html(figure, f"chart_{i}")
            plots_html.append(plot_html)

        # Build HTML
        html = self._build_html(report, plots_html)

        # Write to file
        output_path = self._get_output_path(report)
        output_path.write_text(html)

        return output_path

    def _build_html(self, report: ExperimentReport, plots: list) -> str:
        """Build complete HTML document."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.experiment_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
               max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .chart-container {{ width: 100%; max-width: 800px; margin: 20px auto; }}
        .finding {{ background: #e8f6f3; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .recommendation {{ background: #fef9e7; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .stat-result {{ font-family: monospace; background: #f8f9fa; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{report.experiment_name}</h1>
    <p><strong>Experiment ID:</strong> {report.experiment_id}</p>
    <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M')}</p>

    <h2>Executive Summary</h2>
    <p>{report.summary}</p>

    <h3>Key Findings</h3>
    {"".join(f'<div class="finding">{f}</div>' for f in report.key_findings)}

    <h3>Recommendations</h3>
    {"".join(f'<div class="recommendation">{r}</div>' for r in report.recommendations)}

    <h2>Methodology</h2>
    <p>{report.methodology}</p>
    <p><strong>Sample Size:</strong> {report.sample_size}</p>
    <p><strong>Models Tested:</strong> {', '.join(report.models_tested)}</p>

    <h2>Results</h2>
    {self._render_tables_html(report.tables)}

    <h3>Visualizations</h3>
    {"".join(plots)}

    <h3>Statistical Analysis</h3>
    {self._render_stats_html(report.statistical_results)}

    <h2>Discussion</h2>
    <p>{report.discussion}</p>

    <h3>Limitations</h3>
    <ul>
        {"".join(f'<li>{l}</li>' for l in report.limitations)}
    </ul>
</body>
</html>'''

    def _render_tables_html(self, tables) -> str:
        """Render tables as HTML."""
        html_parts = []
        for table in tables:
            html = f"<h4>{table.title}</h4><table>"
            html += "<tr>" + "".join(f"<th>{h}</th>" for h in table.headers) + "</tr>"
            for row in table.rows:
                html += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
            html += "</table>"
            if table.caption:
                html += f"<p><em>{table.caption}</em></p>"
            html_parts.append(html)
        return "".join(html_parts)

    def _render_stats_html(self, results) -> str:
        """Render statistical results as HTML."""
        parts = []
        for r in results:
            text = f"<strong>{r.test_name}:</strong> "
            text += f"statistic = {r.statistic:.3f}, <em>p</em> = {r.p_value:.4f}"
            if r.effect_size:
                text += f", effect size = {r.effect_size:.3f}"
                if r.effect_interpretation:
                    text += f" ({r.effect_interpretation})"
            parts.append(f'<div class="stat-result">{text}</div>')
        return "".join(parts)
