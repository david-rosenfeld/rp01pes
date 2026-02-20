# CLAUDE.md - Statistical Analysis

## Scope

Statistical functions for experiment analysis.

## Status

Complete. All REQ-3.8.1 requirements satisfied.

## Functional Categories

### Descriptive Statistics
- `descriptive_statistics()` - mean, median, std, quartiles
- `distribution_summary()` - with skewness, kurtosis, normality
- `summarize_by_group()` - group comparisons

### Hypothesis Tests
- `paired_t_test()` - paired samples
- `independent_t_test()` - independent samples
- `wilcoxon_test()` - non-parametric paired
- `mann_whitney_u_test()` - non-parametric independent
- `one_way_anova()` - multiple group comparison
- `normality_test()` - check assumptions

### Effect Sizes
- `cohens_d()` - standardized mean difference
- `cliffs_delta()` - non-parametric effect size
- `confidence_interval()` - CI for means
- `paired_difference_ci()` - CI for paired differences

### Power Analysis
- `estimate_variance_from_pilot()` - PE10 step 1
- `calculate_sample_size_t_test()` - PE10 step 4
- `calculate_power()` - verify power for given n
- `effect_size_from_variance()` - PE10 step 3
- `apply_inflation_factor()` - PE10 step 5

### Correlation
- `pearson_correlation()` - linear relationships
- `spearman_correlation()` - monotonic relationships
- `correlation_matrix()` - multiple variables

## Output Format

All functions return JSON-serializable dictionaries:
```python
{
    "statistic": 2.45,
    "p_value": 0.023,
    "interpretation": "significant",
    ...
}
```

## Usage Pattern

```python
from pes.analysis import normality_test, paired_t_test, wilcoxon_test

# Check assumptions first
if normality_test(data)['is_normal']:
    result = paired_t_test(group1, group2)
else:
    result = wilcoxon_test(group1, group2)
```

## Dependencies

- numpy >= 1.24.0
- scipy >= 1.10.0

## Adding Functions

1. Implement in appropriate submodule
2. Return JSON-serializable dict
3. Include interpretation fields
4. Add comprehensive docstring with type hints
5. Export from `__init__.py`
6. Add test cases to `test_analysis.py`
7. Validate against known statistical software
