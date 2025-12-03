"""
Power analysis and sample size determination.

This module provides functions for statistical power analysis,
including sample size calculations and variance estimation.

Implements REQ-3.8.1.4 (Power Analysis Computation).
"""

from typing import Dict, Any, List, Union, Optional
import numpy as np
from scipy import stats
import math

from ..core.exceptions import AnalysisError
from .utils import validate_numeric_array, remove_nan, check_minimum_sample_size
from .descriptive import summarize_by_group


def estimate_variance_from_pilot(
    pilot_data: Union[List[float], np.ndarray, Dict[str, List[float]]],
    groups: Optional[Union[List[str], np.ndarray]] = None
) -> Dict[str, Any]:
    """
    Estimate variance from pilot data.

    Args:
        pilot_data: Pilot data as array or dict of groups
        groups: Group labels if pilot_data is array

    Returns:
        Dictionary containing:
            - variance_estimate: Estimated variance
            - standard_deviation: Standard deviation
            - sample_size_used: Sample size in pilot
            - by_group: Per-group statistics if groups provided

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> pilot_differences = [0.05, 0.08, 0.03, 0.07, 0.06, 0.04, 0.09]
        >>> result = estimate_variance_from_pilot(pilot_differences)
        >>> result['variance_estimate']
        0.000...  # Example

    Use Case:
        PE10 Step 1 - Estimate variance from pilot data

    Implements:
        REQ-3.8.1.4 (Power Analysis - Variance Estimation)
    """
    # Handle dict input (grouped data)
    if isinstance(pilot_data, dict):
        # Compute variance for each group
        group_stats = {}
        all_variances = []

        for group_name, group_data in pilot_data.items():
            arr = validate_numeric_array(group_data, name=f'group_{group_name}', min_size=2)
            arr_clean = remove_nan(arr)
            check_minimum_sample_size(arr_clean, min_size=2, test_name='Variance estimation')

            var = np.var(arr_clean, ddof=1)
            std = np.std(arr_clean, ddof=1)

            group_stats[group_name] = {
                'variance': float(var),
                'std': float(std),
                'n': int(len(arr_clean))
            }
            all_variances.append(var)

        # Pooled variance estimate
        pooled_variance = np.mean(all_variances)

        return {
            'variance_estimate': float(pooled_variance),
            'standard_deviation': float(np.sqrt(pooled_variance)),
            'sample_size_used': sum(g['n'] for g in group_stats.values()),
            'by_group': group_stats,
            'method': 'pooled_from_groups'
        }

    # Handle array input with optional groups
    arr = validate_numeric_array(pilot_data, name='pilot_data', min_size=2)

    if groups is not None:
        # Use summarize_by_group for grouped analysis
        groups_arr = np.asarray(groups)
        if arr.size != groups_arr.size:
            raise AnalysisError(
                f"pilot_data and groups must have same length: {arr.size} vs {groups_arr.size}"
            )

        summary = summarize_by_group(arr, groups_arr)

        # Compute pooled variance
        variances = [g['variance'] for g in summary.values()]
        pooled_variance = np.mean(variances)

        return {
            'variance_estimate': float(pooled_variance),
            'standard_deviation': float(np.sqrt(pooled_variance)),
            'sample_size_used': int(arr.size),
            'by_group': summary,
            'method': 'pooled_from_groups'
        }

    # Single group - compute variance directly
    arr_clean = remove_nan(arr)
    check_minimum_sample_size(arr_clean, min_size=2, test_name='Variance estimation')

    variance = np.var(arr_clean, ddof=1)
    std = np.std(arr_clean, ddof=1)

    return {
        'variance_estimate': float(variance),
        'standard_deviation': float(std),
        'sample_size_used': int(len(arr_clean)),
        'method': 'single_group'
    }


def calculate_sample_size_t_test(
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.80,
    test_type: str = 'two-sided',
    paired: bool = False
) -> Dict[str, Any]:
    """
    Calculate required sample size for t-test.

    Args:
        effect_size: Expected effect size (Cohen's d)
        alpha: Significance level (Type I error rate)
        power: Desired statistical power (1 - Type II error rate)
        test_type: 'two-sided', 'less', or 'greater'
        paired: Whether test is paired

    Returns:
        Dictionary containing:
            - required_n: Required sample size per group
            - power: Desired power
            - alpha: Significance level
            - effect_size: Effect size used
            - test_type: Type of test
            - paired: Whether paired

    Raises:
        AnalysisError: If parameters are invalid

    Examples:
        >>> result = calculate_sample_size_t_test(
        ...     effect_size=0.5,
        ...     alpha=0.05,
        ...     power=0.80
        ... )
        >>> result['required_n']
        64  # Example for medium effect

    Use Case:
        PE10 Step 4 - Determine required sample size

    Implements:
        REQ-3.8.1.4 (Power Analysis - Sample Size Calculation)
    """
    # Validate inputs
    if not 0 < alpha < 1:
        raise AnalysisError(f"alpha must be between 0 and 1, got {alpha}")

    if not 0 < power < 1:
        raise AnalysisError(f"power must be between 0 and 1, got {power}")

    if effect_size <= 0:
        raise AnalysisError(f"effect_size must be positive, got {effect_size}")

    if test_type not in ['two-sided', 'less', 'greater']:
        raise AnalysisError(f"test_type must be 'two-sided', 'less', or 'greater', got {test_type}")

    # Determine critical values
    if test_type == 'two-sided':
        z_alpha = stats.norm.ppf(1 - alpha / 2)
    else:
        z_alpha = stats.norm.ppf(1 - alpha)

    z_beta = stats.norm.ppf(power)

    # Calculate sample size using approximation formula
    # For paired t-test or one-sample t-test
    if paired:
        # n = ((z_alpha + z_beta) / effect_size)^2
        n = ((z_alpha + z_beta) / effect_size) ** 2
        n = math.ceil(n)

    else:
        # For independent t-test (two groups)
        # n = 2 * ((z_alpha + z_beta) / effect_size)^2
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        n = math.ceil(n)

    return {
        'required_n': int(n),
        'power': float(power),
        'alpha': float(alpha),
        'effect_size': float(effect_size),
        'test_type': test_type,
        'paired': bool(paired)
    }


def calculate_power(
    n: int,
    effect_size: float,
    alpha: float = 0.05,
    test_type: str = 'two-sided',
    paired: bool = False
) -> Dict[str, Any]:
    """
    Calculate statistical power for given sample size and effect size.

    Args:
        n: Sample size (per group for independent, total for paired)
        effect_size: Expected effect size (Cohen's d)
        alpha: Significance level
        test_type: 'two-sided', 'less', or 'greater'
        paired: Whether test is paired

    Returns:
        Dictionary containing:
            - power: Calculated statistical power
            - sample_size: Sample size used
            - effect_size: Effect size used
            - alpha: Significance level
            - test_type: Type of test

    Raises:
        AnalysisError: If parameters are invalid

    Examples:
        >>> result = calculate_power(n=64, effect_size=0.5, alpha=0.05)
        >>> result['power']
        0.80...  # Approximately 0.80

    Implements:
        REQ-3.8.1.4 (Power Analysis - Power Calculation)
    """
    # Validate inputs
    if n < 2:
        raise AnalysisError(f"n must be at least 2, got {n}")

    if effect_size <= 0:
        raise AnalysisError(f"effect_size must be positive, got {effect_size}")

    if not 0 < alpha < 1:
        raise AnalysisError(f"alpha must be between 0 and 1, got {alpha}")

    # Determine critical values
    if test_type == 'two-sided':
        z_alpha = stats.norm.ppf(1 - alpha / 2)
    else:
        z_alpha = stats.norm.ppf(1 - alpha)

    # Calculate non-centrality parameter
    if paired:
        delta = effect_size * np.sqrt(n)
    else:
        delta = effect_size * np.sqrt(n / 2)

    # Calculate power
    # power = P(reject H0 | H1 is true)
    # = P(Z > z_alpha - delta)
    z_beta = z_alpha - delta
    power = stats.norm.sf(z_beta)  # survival function = 1 - cdf

    return {
        'power': float(power),
        'sample_size': int(n),
        'effect_size': float(effect_size),
        'alpha': float(alpha),
        'test_type': test_type,
        'paired': bool(paired)
    }


def effect_size_from_variance(
    variance: float,
    mean_difference: float
) -> Dict[str, Any]:
    """
    Calculate effect size from variance and mean difference.

    Args:
        variance: Variance estimate
        mean_difference: Expected mean difference

    Returns:
        Dictionary containing:
            - effect_size: Cohen's d
            - interpretation: Effect size interpretation
            - variance: Variance used
            - mean_difference: Mean difference used

    Raises:
        AnalysisError: If variance is non-positive

    Examples:
        >>> result = effect_size_from_variance(variance=0.04, mean_difference=0.10)
        >>> result['effect_size']
        0.5  # Medium effect

    Use Case:
        PE10 Step 3 - Convert variance estimate to effect size

    Implements:
        REQ-3.8.1.4 (Power Analysis - Effect Size Calculation)
    """
    if variance <= 0:
        raise AnalysisError(f"variance must be positive, got {variance}")

    std = np.sqrt(variance)
    effect_size = abs(mean_difference) / std

    # Interpret effect size
    from .utils import interpret_effect_size
    interpretation = interpret_effect_size(effect_size, metric='cohens_d')

    return {
        'effect_size': float(effect_size),
        'interpretation': interpretation,
        'variance': float(variance),
        'standard_deviation': float(std),
        'mean_difference': float(mean_difference)
    }


def apply_inflation_factor(
    sample_size: int,
    inflation_rate: float = 0.15
) -> Dict[str, Any]:
    """
    Apply inflation factor to account for unusable runs.

    Args:
        sample_size: Required sample size
        inflation_rate: Inflation rate (e.g., 0.15 for 15%)

    Returns:
        Dictionary containing:
            - original_n: Original sample size
            - inflated_n: Inflated sample size
            - inflation_rate: Inflation rate used
            - additional_samples: Number of additional samples

    Raises:
        AnalysisError: If inflation_rate is invalid

    Examples:
        >>> result = apply_inflation_factor(sample_size=40, inflation_rate=0.15)
        >>> result['inflated_n']
        46  # 40 * 1.15 = 46

    Use Case:
        PE10 Step 5 - Account for failures and timeouts

    Implements:
        REQ-3.8.1.4 (Power Analysis - Inflation Factor)
        REQ-3.6.10.5 (10-20% inflation)
    """
    if not 0 <= inflation_rate < 1:
        raise AnalysisError(
            f"inflation_rate must be between 0 and 1, got {inflation_rate}"
        )

    if sample_size < 1:
        raise AnalysisError(f"sample_size must be at least 1, got {sample_size}")

    inflated_n = math.ceil(sample_size * (1 + inflation_rate))
    additional = inflated_n - sample_size

    return {
        'original_n': int(sample_size),
        'inflated_n': int(inflated_n),
        'inflation_rate': float(inflation_rate),
        'additional_samples': int(additional)
    }
