# pes/analysis/reports/factory.py

"""Report generator factory."""

from pathlib import Path
from typing import Dict, Type, Optional

from .base import BaseReportGenerator
from .markdown import MarkdownReportGenerator
from .html import HTMLReportGenerator
from .latex import LaTeXReportGenerator


_GENERATOR_REGISTRY: Dict[str, Type[BaseReportGenerator]] = {
    'markdown': MarkdownReportGenerator,
    'md': MarkdownReportGenerator,
    'html': HTMLReportGenerator,
    'latex': LaTeXReportGenerator,
    'tex': LaTeXReportGenerator,
}


def get_report_generator(
    format_name: str,
    output_dir: Path,
    template_dir: Optional[Path] = None
) -> BaseReportGenerator:
    """
    Factory function to create report generator.

    Args:
        format_name: Output format ("markdown", "html", "latex")
        output_dir: Directory for generated reports
        template_dir: Optional directory for custom templates

    Returns:
        Configured report generator

    Raises:
        ValueError: If format not supported
    """
    format_name = format_name.lower()

    if format_name not in _GENERATOR_REGISTRY:
        available = ', '.join(_GENERATOR_REGISTRY.keys())
        raise ValueError(f"Unknown format: {format_name}. Available: {available}")

    generator_class = _GENERATOR_REGISTRY[format_name]
    return generator_class(output_dir, template_dir)


def generate_all_formats(
    report,
    output_dir: Path,
    formats: list = None
) -> Dict[str, Path]:
    """
    Generate report in multiple formats.

    Args:
        report: ExperimentReport data
        output_dir: Base output directory
        formats: List of formats (default: ['markdown', 'html', 'latex'])

    Returns:
        Dict mapping format -> generated file path
    """
    if formats is None:
        formats = ['markdown', 'html', 'latex']

    results = {}
    for fmt in formats:
        generator = get_report_generator(fmt, output_dir)
        path = generator.generate(report)
        results[fmt] = path

    return results
