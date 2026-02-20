# pes/analysis/reports/schemas.py

"""
Report data schemas for standardized report generation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TableData:
    """Data for a report table."""
    title: str
    headers: List[str]
    rows: List[List[Any]]
    caption: Optional[str] = None
    footnotes: List[str] = field(default_factory=list)


@dataclass
class FigureData:
    """Data for a report figure."""
    title: str
    figure_type: str  # "bar", "line", "scatter", "box", "heatmap"
    data: Dict[str, Any]
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    caption: Optional[str] = None


@dataclass
class StatisticalResult:
    """Formatted statistical test result."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float] = None
    effect_interpretation: Optional[str] = None
    confidence_interval: Optional[tuple] = None


@dataclass
class ExperimentReport:
    """
    Complete experiment report data.

    This schema is used by all report generators.
    """
    # Metadata
    experiment_id: str
    experiment_name: str
    generated_at: datetime

    # Executive summary
    summary: str
    key_findings: List[str]
    recommendations: List[str]

    # Methodology
    methodology: str
    sample_size: int
    models_tested: List[str]

    # Results
    tables: List[TableData]
    figures: List[FigureData]
    statistical_results: List[StatisticalResult]

    # Discussion
    discussion: str
    limitations: List[str]

    # Raw data reference
    raw_data_path: Optional[str] = None
