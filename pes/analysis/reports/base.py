# pes/analysis/reports/base.py

"""Abstract base class for report generators."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .schemas import ExperimentReport


class BaseReportGenerator(ABC):
    """
    Abstract base class for report generators.

    All format-specific generators inherit from this class.
    """

    def __init__(self, output_dir: Path, template_dir: Optional[Path] = None):
        """
        Initialize report generator.

        Args:
            output_dir: Directory for generated reports
            template_dir: Directory containing templates (optional)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = template_dir

    @abstractmethod
    def generate(self, report: ExperimentReport) -> Path:
        """
        Generate report from data.

        Args:
            report: ExperimentReport data

        Returns:
            Path to generated report file
        """
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return file extension for this format."""
        pass

    def _get_output_path(self, report: ExperimentReport) -> Path:
        """Generate output path for report."""
        filename = f"{report.experiment_id}_{report.generated_at.strftime('%Y%m%d')}"
        return self.output_dir / f"{filename}.{self.file_extension}"
