"""
Utility functions for statistical analysis.

This module provides helper functions for data validation, cleaning,
and formatting used throughout the analysis module.
"""

from typing import List, Tuple, Union, Optional, Any
import numpy as np
from ..core.exceptions import AnalysisError


def validate_numeric_array(
    data: Union[List[float], np.ndarray],
    name: str = 'data',
    allow_empty: bool = False,
    min_size: Optional[int] = None
) -> np.ndarray:
    """
    Validate and convert input data to a numeric numpy array.

    Args:
        data: Input data as list or array
        name: Descriptive name for error messages
        allow_empty: Whether to allow empty arrays
        min_size: Minimum required size (None for no minimum)

    Returns:
        Validated numpy array

    Raises:
        AnalysisError: If data is invalid

    Examples:
        >>> validate_numeric_array([1, 2, 3], name='scores')
        array([1., 2., 3.])

        >>> validate_numeric_array([], allow_empty=False)
        AnalysisError: data cannot be empty
    """
    # Handle None input
    if data is None:
        raise AnalysisError(f"{name} cannot be None")

    # Convert to numpy array
    try:
        arr = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise AnalysisError(f"{name} must contain numeric values: {e}")

    # Check if empty
    if arr.size == 0:
        if not allow_empty:
            raise AnalysisError(f"{name} cannot be empty")
        return arr

    # Check minimum size
    if min_size is not None and arr.size < min_size:
        raise AnalysisError(
            f"{name} must have at least {min_size} elements, got {arr.size}"
        )

    # Check for all NaN
    if np.all(np.isnan(arr)):
        raise AnalysisError(f"{name} contains only NaN values")

    # Check for infinite values
    if np.any(np.isinf(arr)):
        raise AnalysisError(f"{name} contains infinite values")

    return arr


def remove_nan_paired(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove pairs where either value is NaN.

    Args:
        group1: First group of paired data
        group2: Second group of paired data

    Returns:
        Tuple of (cleaned_group1, cleaned_group2)

    Raises:
        AnalysisError: If groups have different lengths

    Examples:
        >>> g1 = [1.0, 2.0, np.nan, 4.0]
        >>> g2 = [5.0, np.nan, 7.0, 8.0]
        >>> remove_nan_paired(g1, g2)
        (array([1., 4.]), array([5., 8.]))
    """
    arr1 = np.asarray(group1, dtype=float)
    arr2 = np.asarray(group2, dtype=float)

    if arr1.size != arr2.size:
        raise AnalysisError(
            f"Paired groups must have same length: {arr1.size} vs {arr2.size}"
        )

    # Find non-NaN pairs
    mask = ~(np.isnan(arr1) | np.isnan(arr2))

    return arr1[mask], arr2[mask]


def check_minimum_sample_size(
    data: Union[List[float], np.ndarray],
    min_size: int,
    test_name: str
) -> None:
    """
    Check if data meets minimum sample size requirement.

    Args:
        data: Input data
        min_size: Minimum required sample size
        test_name: Name of test for error message

    Raises:
        AnalysisError: If sample size is insufficient

    Examples:
        >>> check_minimum_sample_size([1, 2, 3], min_size=2, test_name='t-test')
        None  # Passes

        >>> check_minimum_sample_size([1], min_size=2, test_name='t-test')
        AnalysisError: t-test requires at least 2 samples, got 1
    """
    arr = np.asarray(data, dtype=float)

    # Count non-NaN values
    n = np.sum(~np.isnan(arr))

    if n < min_size:
        raise AnalysisError(
            f"{test_name} requires at least {min_size} samples, got {n}"
        )


def format_p_value(p_value: float, threshold: float = 0.001) -> str:
    """
    Format p-value for reporting.

    Args:
        p_value: P-value to format
        threshold: Threshold for "<" notation

    Returns:
        Formatted p-value string

    Examples:
        >>> format_p_value(0.0456)
        '0.046'

        >>> format_p_value(0.0003)
        '<0.001'

        >>> format_p_value(0.123456)
        '0.123'
    """
    if p_value < threshold:
        return f"<{threshold}"
    else:
        return f"{p_value:.3f}"


def interpret_effect_size(value: float, metric: str = 'cohens_d') -> str:
    """
    Interpret effect size magnitude.

    Args:
        value: Effect size value (absolute)
        metric: Type of effect size ('cohens_d' or 'cliffs_delta')

    Returns:
        Interpretation string

    Examples:
        >>> interpret_effect_size(0.15, metric='cohens_d')
        'negligible'

        >>> interpret_effect_size(0.65, metric='cohens_d')
        'medium'

        >>> interpret_effect_size(0.25, metric='cliffs_delta')
        'small'
    """
    abs_value = abs(value)

    if metric == 'cohens_d':
        # Cohen's d thresholds (Cohen, 1988)
        if abs_value < 0.2:
            return 'negligible'
        elif abs_value < 0.5:
            return 'small'
        elif abs_value < 0.8:
            return 'medium'
        else:
            return 'large'

    elif metric == 'cliffs_delta':
        # Cliff's Delta thresholds (Romano et al., 2006)
        if abs_value < 0.147:
            return 'negligible'
        elif abs_value < 0.33:
            return 'small'
        elif abs_value < 0.474:
            return 'medium'
        else:
            return 'large'

    else:
        raise AnalysisError(f"Unknown effect size metric: {metric}")


def check_equal_length(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    test_name: str = "test"
) -> None:
    """
    Check if two groups have equal length (for paired tests).

    Args:
        group1: First group
        group2: Second group
        test_name: Name of test for error message

    Raises:
        AnalysisError: If groups have different lengths
    """
    arr1 = np.asarray(group1)
    arr2 = np.asarray(group2)

    if arr1.size != arr2.size:
        raise AnalysisError(
            f"{test_name} requires equal sample sizes for paired data: "
            f"{arr1.size} vs {arr2.size}"
        )


def remove_nan(data: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Remove NaN values from array.

    Args:
        data: Input data

    Returns:
        Array with NaN values removed

    Examples:
        >>> remove_nan([1.0, np.nan, 3.0, np.nan, 5.0])
        array([1., 3., 5.])
    """
    arr = np.asarray(data, dtype=float)
    return arr[~np.isnan(arr)]


def calculate_pooled_std(
    group1: np.ndarray,
    group2: np.ndarray
) -> float:
    """
    Calculate pooled standard deviation for two groups.

    Used in Cohen's d calculation for independent samples.

    Args:
        group1: First group
        group2: Second group

    Returns:
        Pooled standard deviation

    Formula:
        sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1 + n2 - 2))

    Examples:
        >>> g1 = np.array([1, 2, 3, 4, 5])
        >>> g2 = np.array([2, 3, 4, 5, 6])
        >>> calculate_pooled_std(g1, g2)
        1.58...
    """
    n1 = len(group1)
    n2 = len(group2)

    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)

    pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)

    return np.sqrt(pooled_var)
