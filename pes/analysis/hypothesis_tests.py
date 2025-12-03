"""
Statistical hypothesis testing functions.

This module provides functions for performing various statistical
hypothesis tests including parametric and non-parametric tests.

Implements REQ-3.8.1.3 (Hypothesis Testing).
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
    check_equal_length
)


def paired_t_test(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    alpha: float = 0.05,
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided'
) -> Dict[str, Any]:
    """
    Perform paired t-test on two related samples.

    Tests whether the means of two related samples differ significantly.

    Args:
        group1: First sample (e.g., Italian scores)
        group2: Second sample (e.g., English scores)
        alpha: Significance level (default: 0.05)
        alternative: Alternative hypothesis:
                    'two-sided': means differ
                    'less': mean of group1 < mean of group2
                    'greater': mean of group1 > mean of group2

    Returns:
        Dictionary containing:
            - statistic: t-statistic
            - p_value: P-value for the test
            - degrees_of_freedom: Degrees of freedom
            - significant: Whether result is significant at alpha level
            - alpha: Significance level used
            - alternative: Alternative hypothesis
            - mean_difference: Mean of (group1 - group2)
            - confidence_interval: (lower, upper) CI for mean difference

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> italian = [0.85, 0.78, 0.92, 0.88, 0.75]
        >>> english = [0.90, 0.82, 0.95, 0.91, 0.80]
        >>> result = paired_t_test(italian, english)
        >>> result['significant']
        False  # Example result

    Use Case:
        PE01 - Comparing Italian vs English requirement performance

    Implements:
        REQ-3.8.1.3 (Hypothesis Testing)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    # Check equal length
    check_equal_length(arr1, arr2, test_name='Paired t-test')

    # Remove NaN pairs
    arr1_clean, arr2_clean = remove_nan_paired(arr1, arr2)

    # Check minimum sample size
    check_minimum_sample_size(arr1_clean, min_size=2, test_name='Paired t-test')

    # Perform paired t-test
    statistic, p_value = stats.ttest_rel(arr1_clean, arr2_clean, alternative=alternative)

    # Compute mean difference and confidence interval
    differences = arr1_clean - arr2_clean
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)
    n = len(differences)
    df = n - 1

    # Confidence interval for mean difference
    if alternative == 'two-sided':
        t_critical = stats.t.ppf(1 - alpha / 2, df)
        margin = t_critical * std_diff / np.sqrt(n)
        ci_lower = mean_diff - margin
        ci_upper = mean_diff + margin
    elif alternative == 'less':
        t_critical = stats.t.ppf(1 - alpha, df)
        ci_lower = -np.inf
        ci_upper = mean_diff + t_critical * std_diff / np.sqrt(n)
    else:  # 'greater'
        t_critical = stats.t.ppf(1 - alpha, df)
        ci_lower = mean_diff - t_critical * std_diff / np.sqrt(n)
        ci_upper = np.inf

    return {
        'statistic': float(statistic),
        'p_value': float(p_value),
        'degrees_of_freedom': int(df),
        'significant': bool(p_value < alpha),
        'alpha': float(alpha),
        'alternative': alternative,
        'mean_difference': float(mean_diff),
        'confidence_interval': (float(ci_lower), float(ci_upper)),
        'sample_size': int(n)
    }


def independent_t_test(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    alpha: float = 0.05,
    equal_var: bool = True,
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided'
) -> Dict[str, Any]:
    """
    Perform independent samples t-test.

    Tests whether the means of two independent samples differ significantly.

    Args:
        group1: First sample
        group2: Second sample
        alpha: Significance level
        equal_var: Assume equal variances (True = Student's t-test,
                  False = Welch's t-test)
        alternative: Alternative hypothesis

    Returns:
        Dictionary containing:
            - statistic: t-statistic
            - p_value: P-value
            - degrees_of_freedom: Degrees of freedom
            - significant: Whether significant at alpha
            - alpha: Significance level
            - alternative: Alternative hypothesis
            - equal_var: Whether equal variance was assumed

    Raises:
        AnalysisError: If data is invalid or insufficient

    Implements:
        REQ-3.8.1.3 (Hypothesis Testing)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    # Remove NaN
    arr1_clean = remove_nan(arr1)
    arr2_clean = remove_nan(arr2)

    # Check minimum sizes
    check_minimum_sample_size(arr1_clean, min_size=2, test_name='Independent t-test')
    check_minimum_sample_size(arr2_clean, min_size=2, test_name='Independent t-test')

    # Perform independent t-test
    result = stats.ttest_ind(
        arr1_clean, arr2_clean,
        equal_var=equal_var,
        alternative=alternative
    )

    return {
        'statistic': float(result.statistic),
        'p_value': float(result.pvalue),
        'degrees_of_freedom': float(result.df) if hasattr(result, 'df') else None,
        'significant': bool(result.pvalue < alpha),
        'alpha': float(alpha),
        'alternative': alternative,
        'equal_var': bool(equal_var),
        'sample_size_1': int(len(arr1_clean)),
        'sample_size_2': int(len(arr2_clean))
    }


def wilcoxon_test(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    alpha: float = 0.05,
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided'
) -> Dict[str, Any]:
    """
    Perform Wilcoxon signed-rank test on paired samples.

    Non-parametric test for paired samples. Use when normality
    assumption is violated.

    Args:
        group1: First sample
        group2: Second sample
        alpha: Significance level
        alternative: Alternative hypothesis

    Returns:
        Dictionary containing:
            - statistic: Wilcoxon statistic
            - p_value: P-value
            - significant: Whether significant at alpha
            - alpha: Significance level
            - alternative: Alternative hypothesis

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> # Non-normal data
        >>> group1 = [1, 2, 3, 100, 5]
        >>> group2 = [2, 3, 4, 101, 6]
        >>> result = wilcoxon_test(group1, group2)

    Use Case:
        PE01 - Alternative to paired t-test for non-normal distributions

    Implements:
        REQ-3.8.1.3 (Hypothesis Testing)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    # Check equal length
    check_equal_length(arr1, arr2, test_name='Wilcoxon test')

    # Remove NaN pairs
    arr1_clean, arr2_clean = remove_nan_paired(arr1, arr2)

    # Check minimum sample size
    check_minimum_sample_size(arr1_clean, min_size=3, test_name='Wilcoxon test')

    # Perform Wilcoxon test
    statistic, p_value = stats.wilcoxon(
        arr1_clean, arr2_clean,
        alternative=alternative
    )

    return {
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant': bool(p_value < alpha),
        'alpha': float(alpha),
        'alternative': alternative,
        'sample_size': int(len(arr1_clean))
    }


def mann_whitney_u_test(
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    alpha: float = 0.05,
    alternative: Literal['two-sided', 'less', 'greater'] = 'two-sided'
) -> Dict[str, Any]:
    """
    Perform Mann-Whitney U test on independent samples.

    Non-parametric test for independent samples. Use when normality
    assumption is violated.

    Args:
        group1: First sample
        group2: Second sample
        alpha: Significance level
        alternative: Alternative hypothesis

    Returns:
        Dictionary containing:
            - statistic: U statistic
            - p_value: P-value
            - significant: Whether significant at alpha
            - alpha: Significance level
            - alternative: Alternative hypothesis

    Raises:
        AnalysisError: If data is invalid or insufficient

    Implements:
        REQ-3.8.1.3 (Hypothesis Testing)
    """
    # Validate inputs
    arr1 = validate_numeric_array(group1, name='group1', min_size=2)
    arr2 = validate_numeric_array(group2, name='group2', min_size=2)

    # Remove NaN
    arr1_clean = remove_nan(arr1)
    arr2_clean = remove_nan(arr2)

    # Check minimum sizes
    check_minimum_sample_size(arr1_clean, min_size=2, test_name='Mann-Whitney U test')
    check_minimum_sample_size(arr2_clean, min_size=2, test_name='Mann-Whitney U test')

    # Perform Mann-Whitney U test
    statistic, p_value = stats.mannwhitneyu(
        arr1_clean, arr2_clean,
        alternative=alternative
    )

    return {
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant': bool(p_value < alpha),
        'alpha': float(alpha),
        'alternative': alternative,
        'sample_size_1': int(len(arr1_clean)),
        'sample_size_2': int(len(arr2_clean))
    }


def one_way_anova(
    groups: List[Union[List[float], np.ndarray]],
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform one-way ANOVA on multiple groups.

    Tests whether the means of multiple independent groups differ significantly.

    Args:
        groups: List of samples (one per group)
        alpha: Significance level

    Returns:
        Dictionary containing:
            - F_statistic: F-statistic
            - p_value: P-value
            - significant: Whether significant at alpha
            - alpha: Significance level
            - num_groups: Number of groups
            - total_n: Total sample size

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> temp_0 = [0.88, 0.85, 0.90, 0.87]
        >>> temp_1 = [0.82, 0.80, 0.85, 0.83]
        >>> temp_2 = [0.75, 0.78, 0.72, 0.76]
        >>> result = one_way_anova([temp_0, temp_1, temp_2])
        >>> result['significant']
        True  # Example

    Use Case:
        PE04 - Comparing multiple temperature settings

    Implements:
        REQ-3.8.1.3 (Hypothesis Testing)
    """
    # Validate we have at least 2 groups
    if len(groups) < 2:
        raise AnalysisError("ANOVA requires at least 2 groups")

    # Validate and clean each group
    cleaned_groups = []
    for i, group in enumerate(groups):
        arr = validate_numeric_array(group, name=f'group{i}', min_size=2)
        arr_clean = remove_nan(arr)
        check_minimum_sample_size(arr_clean, min_size=2, test_name='ANOVA')
        cleaned_groups.append(arr_clean)

    # Perform one-way ANOVA
    F_statistic, p_value = stats.f_oneway(*cleaned_groups)

    # Compute total sample size
    total_n = sum(len(g) for g in cleaned_groups)

    return {
        'F_statistic': float(F_statistic),
        'p_value': float(p_value),
        'significant': bool(p_value < alpha),
        'alpha': float(alpha),
        'num_groups': int(len(cleaned_groups)),
        'total_n': int(total_n),
        'group_sizes': [int(len(g)) for g in cleaned_groups]
    }


def normality_test(
    data: Union[List[float], np.ndarray],
    alpha: float = 0.05,
    method: Literal['shapiro', 'normaltest'] = 'shapiro'
) -> Dict[str, Any]:
    """
    Test whether data follows a normal distribution.

    Args:
        data: Sample data
        alpha: Significance level
        method: Test method:
               'shapiro': Shapiro-Wilk test (good for n <= 5000)
               'normaltest': D'Agostino-Pearson test (good for n > 20)

    Returns:
        Dictionary containing:
            - statistic: Test statistic
            - p_value: P-value
            - is_normal: Whether data appears normal (p > alpha)
            - alpha: Significance level
            - method: Test method used

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> data = np.random.normal(0, 1, 100)
        >>> result = normality_test(data)
        >>> result['is_normal']
        True  # Likely true for normal data

    Use Case:
        Check assumptions before parametric tests

    Implements:
        REQ-3.8.1.3 (Hypothesis Testing)
    """
    # Validate input
    arr = validate_numeric_array(data, name='data', min_size=3)
    arr_clean = remove_nan(arr)

    # Check minimum sample size
    if method == 'shapiro':
        check_minimum_sample_size(arr_clean, min_size=3, test_name='Shapiro-Wilk test')
        if arr_clean.size > 5000:
            raise AnalysisError(
                "Shapiro-Wilk test is designed for n <= 5000. "
                "Use method='normaltest' for larger samples."
            )
        statistic, p_value = stats.shapiro(arr_clean)

    elif method == 'normaltest':
        check_minimum_sample_size(arr_clean, min_size=20, test_name="D'Agostino-Pearson test")
        statistic, p_value = stats.normaltest(arr_clean)

    else:
        raise AnalysisError(f"Unknown normality test method: {method}")

    return {
        'statistic': float(statistic),
        'p_value': float(p_value),
        'is_normal': bool(p_value > alpha),
        'alpha': float(alpha),
        'method': method,
        'sample_size': int(len(arr_clean))
    }
