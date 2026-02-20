"""
Statistical analysis module for the Preliminary Experiments System.

This module provides comprehensive statistical analysis functions including:
- Descriptive statistics
- Hypothesis testing (t-tests, Wilcoxon, ANOVA)
- Effect size calculations (Cohen's d, Cliff's Delta)
- Power analysis and sample size determination
- Correlation analysis
- Publication-quality report generation (Markdown, HTML, LaTeX)

All functions return dictionaries for easy serialization and reporting.

Implements REQ-3.8.1 (Statistical Analysis Engine).
"""

# Import all public functions
from .descriptive import (
    descriptive_statistics,
    distribution_summary,
    summarize_by_group
)

from .hypothesis_tests import (
    paired_t_test,
    independent_t_test,
    wilcoxon_test,
    mann_whitney_u_test,
    one_way_anova,
    normality_test
)

from .effect_sizes import (
    cohens_d,
    cliffs_delta,
    confidence_interval,
    paired_difference_ci
)

from .power_analysis import (
    estimate_variance_from_pilot,
    calculate_sample_size_t_test,
    calculate_power,
    effect_size_from_variance,
    apply_inflation_factor
)

from .correlation import (
    pearson_correlation,
    spearman_correlation,
    correlation_matrix
)

# Report generation submodule
from . import reports

# Define public API
__all__ = [
    # Descriptive statistics
    'descriptive_statistics',
    'distribution_summary',
    'summarize_by_group',

    # Hypothesis tests
    'paired_t_test',
    'independent_t_test',
    'wilcoxon_test',
    'mann_whitney_u_test',
    'one_way_anova',
    'normality_test',

    # Effect sizes
    'cohens_d',
    'cliffs_delta',
    'confidence_interval',
    'paired_difference_ci',

    # Power analysis
    'estimate_variance_from_pilot',
    'calculate_sample_size_t_test',
    'calculate_power',
    'effect_size_from_variance',
    'apply_inflation_factor',

    # Correlation
    'pearson_correlation',
    'spearman_correlation',
    'correlation_matrix',

    # Reports submodule
    'reports',
]
