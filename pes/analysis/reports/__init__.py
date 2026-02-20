# pes/analysis/reports/__init__.py

"""
Publication-quality report generation module.

Supports multiple output formats:
- Markdown: For documentation and GitHub compatibility
- HTML: Interactive reports with Chart.js visualizations
- LaTeX: Academic publication format (ACM sigconf)
"""

from .schemas import (
    TableData,
    FigureData,
    StatisticalResult,
    ExperimentReport,
)

from .base import BaseReportGenerator

from .markdown import MarkdownReportGenerator
from .html import HTMLReportGenerator
from .latex import LaTeXReportGenerator

from .factory import (
    get_report_generator,
    generate_all_formats,
)

from .visualizations import generate_plot_html


__all__ = [
    # Schemas
    'TableData',
    'FigureData',
    'StatisticalResult',
    'ExperimentReport',
    # Base
    'BaseReportGenerator',
    # Generators
    'MarkdownReportGenerator',
    'HTMLReportGenerator',
    'LaTeXReportGenerator',
    # Factory
    'get_report_generator',
    'generate_all_formats',
    # Visualizations
    'generate_plot_html',
]
