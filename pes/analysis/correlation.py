"""
Correlation analysis functions.

This module provides functions for computing correlation coefficients
and analyzing relationships between variables.

Implements REQ-3.8.1.5 (Correlation Analysis).
"""

from typing import Dict, Any, List, Union
import numpy as np
from scipy import stats

from ..core.exceptions import AnalysisError
from .utils import validate_numeric_array, remove_nan_paired, check_minimum_sample_size


def pearson_correlation(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate Pearson correlation coefficient.

    Measures linear relationship between two continuous variables.

    Args:
        x: First variable
        y: Second variable
        alpha: Significance level for hypothesis test

    Returns:
        Dictionary containing:
            - correlation: Pearson r coefficient (-1 to 1)
            - p_value: P-value for test of no correlation
            - significant: Whether correlation is significant
            - alpha: Significance level used
            - sample_size: Number of pairs used

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> x = [1, 2, 3, 4, 5]
        >>> y = [2, 4, 6, 8, 10]
        >>> result = pearson_correlation(x, y)
        >>> result['correlation']
        1.0  # Perfect positive correlation

    Notes:
        - r = 1: Perfect positive correlation
        - r = 0: No linear correlation
        - r = -1: Perfect negative correlation

    Use Case:
        Analyzing relationship between execution time and accuracy

    Implements:
        REQ-3.8.1.5 (Correlation Analysis - Pearson)
    """
    # Validate inputs
    arr_x = validate_numeric_array(x, name='x', min_size=2)
    arr_y = validate_numeric_array(y, name='y', min_size=2)

    # Remove NaN pairs
    x_clean, y_clean = remove_nan_paired(arr_x, arr_y)

    # Check minimum sample size (need at least 3 for meaningful correlation)
    check_minimum_sample_size(x_clean, min_size=3, test_name='Pearson correlation')

    # Calculate Pearson correlation
    correlation, p_value = stats.pearsonr(x_clean, y_clean)

    return {
        'correlation': float(correlation),
        'p_value': float(p_value),
        'significant': bool(p_value < alpha),
        'alpha': float(alpha),
        'sample_size': int(len(x_clean)),
        'method': 'pearson'
    }


def spearman_correlation(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate Spearman rank correlation coefficient.

    Non-parametric measure of monotonic relationship. Use when:
    - Data violates normality assumptions
    - Relationship is not linear but monotonic
    - Data is ordinal

    Args:
        x: First variable
        y: Second variable
        alpha: Significance level

    Returns:
        Dictionary containing:
            - correlation: Spearman rho coefficient (-1 to 1)
            - p_value: P-value for test
            - significant: Whether correlation is significant
            - alpha: Significance level used
            - sample_size: Number of pairs used

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> x = [1, 2, 3, 4, 100]  # Outlier
        >>> y = [2, 4, 5, 7, 9]
        >>> result = spearman_correlation(x, y)
        >>> result['correlation']
        1.0  # Perfect monotonic relationship despite outlier

    Use Case:
        Correlation with ordinal data or non-linear relationships

    Implements:
        REQ-3.8.1.5 (Correlation Analysis - Spearman)
    """
    # Validate inputs
    arr_x = validate_numeric_array(x, name='x', min_size=2)
    arr_y = validate_numeric_array(y, name='y', min_size=2)

    # Remove NaN pairs
    x_clean, y_clean = remove_nan_paired(arr_x, arr_y)

    # Check minimum sample size
    check_minimum_sample_size(x_clean, min_size=3, test_name='Spearman correlation')

    # Calculate Spearman correlation
    correlation, p_value = stats.spearmanr(x_clean, y_clean)

    return {
        'correlation': float(correlation),
        'p_value': float(p_value),
        'significant': bool(p_value < alpha),
        'alpha': float(alpha),
        'sample_size': int(len(x_clean)),
        'method': 'spearman'
    }


def correlation_matrix(
    data_dict: Dict[str, Union[List[float], np.ndarray]],
    method: str = 'pearson',
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate correlation matrix for multiple variables.

    Args:
        data_dict: Dictionary mapping variable names to data arrays
        method: 'pearson' or 'spearman'
        alpha: Significance level

    Returns:
        Dictionary containing:
            - correlation_matrix: 2D dict of correlations
            - p_value_matrix: 2D dict of p-values
            - variable_names: List of variable names
            - significant_pairs: List of significant correlations
            - method: Method used

    Raises:
        AnalysisError: If data is invalid or insufficient

    Examples:
        >>> data = {
        ...     'accuracy': [0.8, 0.85, 0.9, 0.82, 0.88],
        ...     'time': [10, 12, 15, 11, 14],
        ...     'tokens': [100, 120, 150, 110, 140]
        ... }
        >>> result = correlation_matrix(data, method='pearson')
        >>> 'accuracy' in result['correlation_matrix']
        True

    Use Case:
        Exploring relationships between multiple performance metrics

    Implements:
        REQ-3.8.1.5 (Correlation Analysis - Matrix)
    """
    # Validate method
    if method not in ['pearson', 'spearman']:
        raise AnalysisError(f"method must be 'pearson' or 'spearman', got {method}")

    # Validate data_dict
    if not isinstance(data_dict, dict) or len(data_dict) < 2:
        raise AnalysisError("data_dict must contain at least 2 variables")

    # Get variable names
    variable_names = list(data_dict.keys())

    # Validate and convert all arrays
    arrays = {}
    for var_name, var_data in data_dict.items():
        arr = validate_numeric_array(var_data, name=var_name, min_size=3)
        arrays[var_name] = arr

    # Check all arrays have same length
    lengths = [len(arr) for arr in arrays.values()]
    if len(set(lengths)) != 1:
        raise AnalysisError(
            f"All variables must have same length, got {dict(zip(variable_names, lengths))}"
        )

    # Initialize matrices
    n_vars = len(variable_names)
    corr_matrix = {}
    p_value_matrix = {}
    significant_pairs = []

    # Choose correlation function
    if method == 'pearson':
        corr_func = pearson_correlation
    else:
        corr_func = spearman_correlation

    # Compute pairwise correlations
    for i, var1 in enumerate(variable_names):
        corr_matrix[var1] = {}
        p_value_matrix[var1] = {}

        for j, var2 in enumerate(variable_names):
            if i == j:
                # Diagonal: correlation with self = 1
                corr_matrix[var1][var2] = 1.0
                p_value_matrix[var1][var2] = 0.0
            elif i < j:
                # Upper triangle: compute correlation
                result = corr_func(arrays[var1], arrays[var2], alpha=alpha)

                corr_matrix[var1][var2] = result['correlation']
                p_value_matrix[var1][var2] = result['p_value']

                # Record significant pairs
                if result['significant']:
                    significant_pairs.append({
                        'variable_1': var1,
                        'variable_2': var2,
                        'correlation': result['correlation'],
                        'p_value': result['p_value']
                    })
            else:
                # Lower triangle: copy from upper triangle (symmetric)
                corr_matrix[var1][var2] = corr_matrix[var2][var1]
                p_value_matrix[var1][var2] = p_value_matrix[var2][var1]

    return {
        'correlation_matrix': corr_matrix,
        'p_value_matrix': p_value_matrix,
        'variable_names': variable_names,
        'significant_pairs': significant_pairs,
        'method': method,
        'alpha': alpha,
        'sample_size': lengths[0]
    }
