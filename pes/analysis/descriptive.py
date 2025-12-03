"""
Descriptive statistics functions.

This module provides functions for computing descriptive statistics
on single samples and grouped data.

Implements REQ-3.8.1.1 (Descriptive Statistics).
"""

from typing import Dict, Any, List, Union, Optional
import numpy as np
from scipy import stats

from ..core.exceptions import AnalysisError
from .utils import validate_numeric_array, remove_nan


def descriptive_statistics(
    data: Union[List[float], np.ndarray],
    percentiles: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive descriptive statistics for a dataset.

    Args:
        data: Input data as list or array
        percentiles: Optional list of percentiles to compute (e.g., [25, 50, 75])
                    If None, computes quartiles (Q1, Q2, Q3)

    Returns:
        Dictionary containing:
            - count: Number of non-NaN values
            - mean: Arithmetic mean
            - median: Median (50th percentile)
            - std: Standard deviation (sample, ddof=1)
            - variance: Variance (sample, ddof=1)
            - min: Minimum value
            - max: Maximum value
            - q1: First quartile (25th percentile)
            - q2: Second quartile (50th percentile, median)
            - q3: Third quartile (75th percentile)
            - range: max - min
            - iqr: Interquartile range (q3 - q1)
            - Additional percentiles if specified

    Raises:
        AnalysisError: If data is invalid or empty

    Examples:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> stats = descriptive_statistics(data)
        >>> stats['mean']
        5.5
        >>> stats['median']
        5.5
        >>> stats['std']
        3.02...

    Implements:
        REQ-3.8.1.1 (Descriptive Statistics)
    """
    # Validate and clean data
    arr = validate_numeric_array(data, name='data', allow_empty=False)
    arr_clean = remove_nan(arr)

    if arr_clean.size == 0:
        raise AnalysisError("Cannot compute statistics on empty data (all NaN)")

    # Compute basic statistics
    result = {
        'count': int(arr_clean.size),
        'mean': float(np.mean(arr_clean)),
        'median': float(np.median(arr_clean)),
        'std': float(np.std(arr_clean, ddof=1)) if arr_clean.size > 1 else 0.0,
        'variance': float(np.var(arr_clean, ddof=1)) if arr_clean.size > 1 else 0.0,
        'min': float(np.min(arr_clean)),
        'max': float(np.max(arr_clean)),
    }

    # Compute quartiles
    if arr_clean.size >= 4:
        q1, q2, q3 = np.percentile(arr_clean, [25, 50, 75])
        result['q1'] = float(q1)
        result['q2'] = float(q2)
        result['q3'] = float(q3)
        result['iqr'] = float(q3 - q1)
    else:
        # Not enough data for meaningful quartiles
        result['q1'] = None
        result['q2'] = result['median']
        result['q3'] = None
        result['iqr'] = None

    # Compute range
    result['range'] = result['max'] - result['min']

    # Compute additional percentiles if requested
    if percentiles is not None:
        for p in percentiles:
            if 0 <= p <= 100:
                result[f'p{int(p)}'] = float(np.percentile(arr_clean, p))

    return result


def distribution_summary(
    data: Union[List[float], np.ndarray],
    include_skewness: bool = True,
    include_kurtosis: bool = True
) -> Dict[str, Any]:
    """
    Compute distribution summary including shape statistics.

    Args:
        data: Input data as list or array
        include_skewness: Whether to compute skewness
        include_kurtosis: Whether to compute kurtosis

    Returns:
        Dictionary containing basic descriptive statistics plus:
            - skewness: Measure of asymmetry (if requested)
            - kurtosis: Measure of tail heaviness (if requested)
            - is_normal_shapiro: Shapiro-Wilk normality test result (if n <= 5000)
            - is_normal_anderson: Anderson-Darling normality test result

    Raises:
        AnalysisError: If data is invalid or empty

    Examples:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> summary = distribution_summary(data)
        >>> 'skewness' in summary
        True
        >>> 'kurtosis' in summary
        True

    Notes:
        - Skewness: 0 = symmetric, >0 = right-skewed, <0 = left-skewed
        - Kurtosis: 0 = normal, >0 = heavy tails, <0 = light tails
        - Uses excess kurtosis (normal distribution = 0)

    Implements:
        REQ-3.8.1.1 (Descriptive Statistics)
    """
    # Start with basic descriptive statistics
    result = descriptive_statistics(data)

    # Clean data for shape statistics
    arr = validate_numeric_array(data, name='data')
    arr_clean = remove_nan(arr)

    # Need at least 3 observations for skewness/kurtosis
    if arr_clean.size < 3:
        if include_skewness:
            result['skewness'] = None
        if include_kurtosis:
            result['kurtosis'] = None
        result['is_normal_shapiro'] = None
        result['is_normal_anderson'] = None
        return result

    # Compute skewness
    if include_skewness:
        result['skewness'] = float(stats.skew(arr_clean))

    # Compute kurtosis (excess kurtosis where normal = 0)
    if include_kurtosis:
        result['kurtosis'] = float(stats.kurtosis(arr_clean))

    # Normality tests (if enough data)
    if arr_clean.size >= 3:
        # Shapiro-Wilk test (good for n <= 5000)
        if arr_clean.size <= 5000:
            statistic, p_value = stats.shapiro(arr_clean)
            result['is_normal_shapiro'] = bool(p_value > 0.05)
            result['shapiro_p_value'] = float(p_value)
        else:
            result['is_normal_shapiro'] = None
            result['shapiro_p_value'] = None

        # Anderson-Darling test
        anderson_result = stats.anderson(arr_clean, dist='norm')
        # Use 5% significance level (index 2 in critical_values)
        result['is_normal_anderson'] = bool(
            anderson_result.statistic < anderson_result.critical_values[2]
        )
        result['anderson_statistic'] = float(anderson_result.statistic)

    return result


def summarize_by_group(
    data: Union[List[float], np.ndarray],
    groups: Union[List[str], np.ndarray]
) -> Dict[str, Dict[str, Any]]:
    """
    Compute descriptive statistics for each group.

    Args:
        data: Data values
        groups: Group labels (same length as data)

    Returns:
        Dictionary mapping group names to descriptive statistics

    Raises:
        AnalysisError: If data and groups have different lengths

    Examples:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> groups = ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C']
        >>> summary = summarize_by_group(data, groups)
        >>> summary['A']['mean']
        2.0
        >>> summary['B']['mean']
        5.0
        >>> summary['C']['mean']
        8.0

    Use Case:
        Comparing performance across multiple experimental conditions

    Implements:
        REQ-3.8.1.1 (Descriptive Statistics)
    """
    # Validate inputs
    data_arr = validate_numeric_array(data, name='data')
    groups_arr = np.asarray(groups)

    if data_arr.size != groups_arr.size:
        raise AnalysisError(
            f"data and groups must have same length: {data_arr.size} vs {groups_arr.size}"
        )

    # Get unique groups
    unique_groups = np.unique(groups_arr)

    # Compute statistics for each group
    result = {}
    for group_name in unique_groups:
        mask = groups_arr == group_name
        group_data = data_arr[mask]

        # Skip empty groups
        if group_data.size == 0:
            continue

        # Compute descriptive statistics for this group
        try:
            group_stats = descriptive_statistics(group_data)
            result[str(group_name)] = group_stats
        except AnalysisError:
            # Skip groups with all NaN
            continue

    if len(result) == 0:
        raise AnalysisError("No valid groups found in data")

    return result
