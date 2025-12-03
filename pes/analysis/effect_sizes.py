"""
Effect size calculations.

This module provides functions for computing effect sizes and
confidence intervals for comparing experimental conditions.

Implements REQ-3.8.1.2 (Comparative Statistics - Effect Sizes).
"""

from typing import Dict, Any, List, Union, Literal
import numpy as np
from scipy import stats

from ..core.exceptions import AnalysisError
from .utils import (
    validate_numeric_array,
    remove_nan,
    remove_nan_paired,
    check_minimum_sample_size,
    check_equal_length,
    calculate_pooled_std,
    interpret_effect_size
)


def cohens_d(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    paired: bool = False
) -> Dict[str, Any]:
    """
    Calculate Cohen's d effect size.

    Measures the standardized difference between two means.

    Args:
        group1: First sample
        group2: Second sample
        paired: Whether samples are paired (uses within-subject std if True)

    Returns:
        Dictionary containing:
            - d: Cohen's d value
            - interpretation: Effect size interpretation
                ('negligible', 'small', 'medium', 'large')
            - pooled_std: Pooled standard deviation (if independent)
            - within_std: Within-subject standard deviation (if paired)

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> group1 = [0.85, 0.78, 0.92, 0.88, 0.75]
        >>> group2 = [0.90, 0.82, 0.95, 0.91, 0.80]
        >>> result = cohens_d(group1, group2, paired=True)
        >>> result['d']
        -0.65...  # Example
        >>> result['interpretation']
        'medium'

    Notes:
        Cohen's d interpretation (Cohen, 1988):
        - |d| < 0.2: negligible
        - 0.2 <= |d| < 0.5: small
        - 0.5 <= |d| < 0.8: medium
        - |d| >= 0.8: large

    Use Case:
        PE01 - Quantify language effect magnitude

    Implements:
        REQ-3.8.1.2 (Effect Sizes - Cohen's d)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    if paired:
        # Paired samples
        check_equal_length(arr1, arr2, test_name="Cohen's d (paired)")
        arr1_clean, arr2_clean = remove_nan_paired(arr1, arr2)
        check_minimum_sample_size(arr1_clean, min_size=2, test_name="Cohen's d")

        # Calculate difference scores
        differences = arr1_clean - arr2_clean
        mean_diff = np.mean(differences)
        std_diff = np.std(differences, ddof=1)

        # Cohen's d for paired samples
        d = mean_diff / std_diff

        result = {
            'd': float(d),
            'interpretation': interpret_effect_size(d, metric='cohens_d'),
            'within_std': float(std_diff),
            'mean_difference': float(mean_diff)
        }

    else:
        # Independent samples
        arr1_clean = remove_nan(arr1)
        arr2_clean = remove_nan(arr2)

        check_minimum_sample_size(arr1_clean, min_size=2, test_name="Cohen's d")
        check_minimum_sample_size(arr2_clean, min_size=2, test_name="Cohen's d")

        # Calculate means
        mean1 = np.mean(arr1_clean)
        mean2 = np.mean(arr2_clean)
        mean_diff = mean1 - mean2

        # Calculate pooled standard deviation
        pooled_std = calculate_pooled_std(arr1_clean, arr2_clean)

        # Cohen's d for independent samples
        d = mean_diff / pooled_std

        result = {
            'd': float(d),
            'interpretation': interpret_effect_size(d, metric='cohens_d'),
            'pooled_std': float(pooled_std),
            'mean_difference': float(mean_diff)
        }

    return result


def cliffs_delta(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray]
) -> Dict[str, Any]:
    """
    Calculate Cliff's Delta effect size.

    Non-parametric effect size measure based on ordinal comparisons.
    Use when data violates normality assumptions.

    Args:
        group1: First sample
        group2: Second sample

    Returns:
        Dictionary containing:
            - delta: Cliff's Delta value (range: -1 to 1)
            - interpretation: Effect size interpretation
                ('negligible', 'small', 'medium', 'large')
            - dominance: Proportion of pairs where group1 > group2

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> group1 = [1, 2, 3, 4, 5]
        >>> group2 = [2, 3, 4, 5, 6]
        >>> result = cliffs_delta(group1, group2)
        >>> result['delta']
        -0.48...  # Example

    Notes:
        Cliff's Delta interpretation (Romano et al., 2006):
        - |δ| < 0.147: negligible
        - 0.147 <= |δ| < 0.33: small
        - 0.33 <= |δ| < 0.474: medium
        - |δ| >= 0.474: large

    Formula:
        δ = (# pairs where x1 > x2 - # pairs where x1 < x2) / (n1 * n2)

    Use Case:
        PE01 - Non-parametric alternative to Cohen's d

    Implements:
        REQ-3.8.1.2 (Effect Sizes - Cliff's Delta)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    # Remove NaN
    arr1_clean = remove_nan(arr1)
    arr2_clean = remove_nan(arr2)

    check_minimum_sample_size(arr1_clean, min_size=2, test_name="Cliff's Delta")
    check_minimum_sample_size(arr2_clean, min_size=2, test_name="Cliff's Delta")

    # Calculate Cliff's Delta
    n1 = len(arr1_clean)
    n2 = len(arr2_clean)

    # Count pairs
    greater = 0
    less = 0

    for x1 in arr1_clean:
        for x2 in arr2_clean:
            if x1 > x2:
                greater += 1
            elif x1 < x2:
                less += 1
            # Ties are not counted

    # Cliff's Delta
    delta = (greater - less) / (n1 * n2)

    # Dominance (proportion where group1 > group2)
    dominance = greater / (n1 * n2)

    return {
        'delta': float(delta),
        'interpretation': interpret_effect_size(delta, metric='cliffs_delta'),
        'dominance': float(dominance),
        'greater_count': int(greater),
        'less_count': int(less),
        'tie_count': int(n1 * n2 - greater - less)
    }


def confidence_interval(
    data: Union[List[float], np.ndarray],
    confidence: float = 0.95,
    method: Literal['t', 'bootstrap'] = 't'
) -> Dict[str, Any]:
    """
    Calculate confidence interval for the mean.

    Args:
        data: Sample data
        confidence: Confidence level (e.g., 0.95 for 95% CI)
        method: Method to use:
               't': t-distribution (parametric)
               'bootstrap': Bootstrap resampling (future implementation)

    Returns:
        Dictionary containing:
            - mean: Sample mean
            - lower_bound: Lower confidence bound
            - upper_bound: Upper confidence bound
            - confidence_level: Confidence level used
            - margin_of_error: Half-width of CI

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> result = confidence_interval(data, confidence=0.95)
        >>> result['mean']
        5.5
        >>> result['lower_bound'] < result['upper_bound']
        True

    Implements:
        REQ-3.8.1.2 (Confidence Intervals)
    """
    # Validate input
    arr = validate_numeric_array(data, name='data', min_size=2)
    arr_clean = remove_nan(arr)

    check_minimum_sample_size(arr_clean, min_size=2, test_name='Confidence interval')

    if method == 't':
        # t-distribution method
        mean = np.mean(arr_clean)
        std = np.std(arr_clean, ddof=1)
        n = len(arr_clean)
        df = n - 1

        # Calculate t-critical value
        alpha = 1 - confidence
        t_critical = stats.t.ppf(1 - alpha / 2, df)

        # Calculate margin of error
        margin = t_critical * std / np.sqrt(n)

        return {
            'mean': float(mean),
            'lower_bound': float(mean - margin),
            'upper_bound': float(mean + margin),
            'confidence_level': float(confidence),
            'margin_of_error': float(margin),
            'standard_error': float(std / np.sqrt(n)),
            'sample_size': int(n)
        }

    elif method == 'bootstrap':
        # Bootstrap method (future implementation)
        raise AnalysisError("Bootstrap confidence intervals not yet implemented")

    else:
        raise AnalysisError(f"Unknown confidence interval method: {method}")


def paired_difference_ci(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    confidence: float = 0.95
) -> Dict[str, Any]:
    """
    Calculate confidence interval for paired differences.

    Args:
        group1: First sample
        group2: Second sample
        confidence: Confidence level

    Returns:
        Dictionary containing:
            - mean_difference: Mean of (group1 - group2)
            - lower_bound: Lower confidence bound
            - upper_bound: Upper confidence bound
            - confidence_level: Confidence level used
            - margin_of_error: Half-width of CI

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> italian = [0.85, 0.78, 0.92, 0.88, 0.75]
        >>> english = [0.90, 0.82, 0.95, 0.91, 0.80]
        >>> result = paired_difference_ci(italian, english)
        >>> result['mean_difference']
        -0.05

    Use Case:
        PE01 - Confidence interval for language effect

    Implements:
        REQ-3.8.1.2 (Confidence Intervals for Paired Differences)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    # Check equal length
    check_equal_length(arr1, arr2, test_name='Paired difference CI')

    # Remove NaN pairs
    arr1_clean, arr2_clean = remove_nan_paired(arr1, arr2)

    check_minimum_sample_size(arr1_clean, min_size=2, test_name='Paired difference CI')

    # Calculate differences
    differences = arr1_clean - arr2_clean

    # Use confidence_interval function on differences
    ci_result = confidence_interval(differences, confidence=confidence)

    return {
        'mean_difference': ci_result['mean'],
        'lower_bound': ci_result['lower_bound'],
        'upper_bound': ci_result['upper_bound'],
        'confidence_level': ci_result['confidence_level'],
        'margin_of_error': ci_result['margin_of_error'],
        'standard_error': ci_result['standard_error'],
        'sample_size': ci_result['sample_size']
    }
