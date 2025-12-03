# Implementation Plan: Phase 2 - Core Analysis Capabilities
## Statistical Analysis Module

**Date:** 2025-12-03
**Status:** Planning Phase - Awaiting Approval
**Estimated Time:** 3-4 hours

---

## Overview

Implement a comprehensive statistical analysis module (`pes/analysis/`) that provides reusable statistical functions for all experiments, particularly PE01, PE04, and PE10. This module will satisfy requirements REQ-3.8.1.* (Statistical Analysis Engine).

---

## Requirements Coverage

### Primary Requirements
- **REQ-3.8.1.1**: Descriptive Statistics (mean, median, std, min, max, quartiles)
- **REQ-3.8.1.2**: Comparative Statistics (paired differences, effect sizes, confidence intervals)
- **REQ-3.8.1.3**: Hypothesis Testing (t-tests, Wilcoxon, ANOVA)
- **REQ-3.8.1.4**: Power Analysis (sample size calculations)
- **REQ-3.8.1.5**: Correlation Analysis (Pearson, Spearman)

### Experiments That Will Use This Module
- **PE01**: Language Effect Assessment → needs t-test/Wilcoxon, effect sizes
- **PE04**: Temperature Optimization → needs descriptive stats, ANOVA
- **PE10**: Power Analysis → needs power calculations, variance estimates
- **Others**: Most experiments will benefit from descriptive statistics and reporting

---

## Architecture Decisions

### 1. Module Structure

```
pes/analysis/
├── __init__.py              # Public API exports
├── descriptive.py           # Descriptive statistics functions
├── hypothesis_tests.py      # Statistical hypothesis testing
├── effect_sizes.py          # Effect size calculations
├── power_analysis.py        # Power analysis and sample size
├── correlation.py           # Correlation analyses
└── utils.py                 # Helper functions (data validation, etc.)
```

**Rationale:**
- Modular organization allows selective imports
- Clear separation of concerns
- Easy to test individual components
- Follows existing project pattern (see `pes/datasets/` structure)
- Can add visualization later without disrupting core analysis

### 2. Error Handling

Use existing `pes.core.exceptions.AnalysisError` for all statistical errors.

**Rationale:**
- Consistent with existing exception hierarchy
- Already defined in `pes/core/exceptions.py:44`
- Allows experiments to catch analysis-specific errors

### 3. Dependencies

**New dependencies required:**
```python
numpy>=1.24.0      # Numerical operations
scipy>=1.10.0      # Statistical functions
```

**Rationale:**
- Industry-standard libraries for statistical computing
- scipy.stats provides comprehensive statistical test implementations
- numpy provides efficient array operations
- Both are stable, well-documented, cross-platform

### 4. API Design Philosophy

**Functional API with clear inputs/outputs:**
```python
# Example usage pattern
from pes.analysis import descriptive_statistics, paired_t_test, cohens_d

# Get descriptive stats
stats = descriptive_statistics([1.2, 3.4, 5.6, 7.8])
# Returns: {'mean': 4.5, 'median': 4.5, 'std': 2.7, ...}

# Perform hypothesis test
result = paired_t_test(group1, group2, alpha=0.05)
# Returns: {'statistic': 2.45, 'p_value': 0.03, 'significant': True, ...}

# Calculate effect size
effect = cohens_d(group1, group2)
# Returns: {'d': 0.65, 'interpretation': 'medium', ...}
```

**Rationale:**
- Simple function calls, no complex OOP overhead
- Returns dictionaries for easy JSON serialization (matches PE02 pattern)
- Type hints for all functions (follows PEP 484)
- Comprehensive docstrings (follows PEP 257)

---

## Detailed Implementation Plan

### File 1: `pes/analysis/descriptive.py`

**Purpose:** Descriptive statistics for single samples and distributions

**Functions to implement:**

1. **`descriptive_statistics(data, percentiles=None)`**
   - Input: List/array of numeric values, optional percentile list
   - Output: Dict with mean, median, std, variance, min, max, Q1, Q2, Q3, count
   - Handles: Empty data, NaN values, outliers
   - REQ: 3.8.1.1

2. **`distribution_summary(data, include_skewness=True, include_kurtosis=True)`**
   - Input: List/array of numeric values, flags for extended stats
   - Output: Dict with basic stats + skewness, kurtosis if requested
   - Handles: Non-normal distributions
   - REQ: 3.8.1.1

3. **`summarize_by_group(data, groups)`**
   - Input: Data values, group labels
   - Output: Dict mapping group names to descriptive statistics
   - Use case: Comparing performance across multiple conditions
   - REQ: 3.8.1.1

**Implementation approach:**
- Use numpy for calculations (mean, std, percentile)
- Use scipy.stats for skewness/kurtosis
- Add data validation (check for empty, all-NaN, infinite values)
- Return consistent dictionary format

**Testing approach:**
- Test with normal data, edge cases (empty, single value, all same)
- Verify calculations against known values
- Test with NaN/inf handling

---

### File 2: `pes/analysis/hypothesis_tests.py`

**Purpose:** Statistical hypothesis tests

**Functions to implement:**

1. **`paired_t_test(group1, group2, alpha=0.05, alternative='two-sided')`**
   - Input: Two paired samples, significance level, test direction
   - Output: Dict with statistic, p_value, degrees_of_freedom, significant, confidence_interval
   - Use case: PE01 comparing Italian vs English performance
   - REQ: 3.8.1.3
   - Uses: scipy.stats.ttest_rel

2. **`independent_t_test(group1, group2, alpha=0.05, equal_var=True, alternative='two-sided')`**
   - Input: Two independent samples, significance level, variance assumption, test direction
   - Output: Same format as paired_t_test
   - Use case: Comparing two different models
   - REQ: 3.8.1.3
   - Uses: scipy.stats.ttest_ind

3. **`wilcoxon_test(group1, group2, alpha=0.05, alternative='two-sided')`**
   - Input: Two paired samples, significance level, test direction
   - Output: Dict with statistic, p_value, significant
   - Use case: PE01 with non-normal distributions
   - REQ: 3.8.1.3
   - Uses: scipy.stats.wilcoxon

4. **`mann_whitney_u_test(group1, group2, alpha=0.05, alternative='two-sided')`**
   - Input: Two independent samples, significance level, test direction
   - Output: Dict with statistic, p_value, significant
   - Use case: Non-parametric alternative to independent t-test
   - REQ: 3.8.1.3
   - Uses: scipy.stats.mannwhitneyu

5. **`one_way_anova(groups, alpha=0.05)`**
   - Input: List of groups (each a list of values), significance level
   - Output: Dict with F_statistic, p_value, between_group_var, within_group_var, significant
   - Use case: PE04 comparing multiple temperature settings
   - REQ: 3.8.1.3
   - Uses: scipy.stats.f_oneway

6. **`normality_test(data, alpha=0.05, method='shapiro')`**
   - Input: Sample data, significance level, test method
   - Output: Dict with statistic, p_value, is_normal
   - Use case: Checking assumptions before parametric tests
   - Uses: scipy.stats.shapiro or scipy.stats.normaltest

**Implementation approach:**
- Wrapper functions around scipy.stats methods
- Add assumption checking (sample size, normality if needed)
- Consistent return format across all tests
- Include interpretation flags (significant: True/False)

**Testing approach:**
- Test with known datasets (verify against published results)
- Test edge cases (small samples, ties, identical groups)
- Verify p-value calculations

---

### File 3: `pes/analysis/effect_sizes.py`

**Purpose:** Effect size calculations for comparing conditions

**Functions to implement:**

1. **`cohens_d(group1, group2, paired=False)`**
   - Input: Two samples, whether they're paired
   - Output: Dict with d, interpretation, variance_pooled
   - Interpretation: negligible (<0.2), small (0.2-0.5), medium (0.5-0.8), large (>0.8)
   - Use case: PE01 quantifying language effect magnitude
   - REQ: 3.8.1.2
   - Formula: (mean1 - mean2) / pooled_std

2. **`cliffs_delta(group1, group2)`**
   - Input: Two samples (non-parametric)
   - Output: Dict with delta, interpretation, magnitude
   - Interpretation: negligible (<0.147), small (0.147-0.33), medium (0.33-0.474), large (>0.474)
   - Use case: PE01 with non-normal distributions
   - REQ: 3.8.1.2
   - Formula: Based on Mann-Whitney U

3. **`confidence_interval(data, confidence=0.95, method='t')`**
   - Input: Sample data, confidence level, method (t-distribution or bootstrap)
   - Output: Dict with mean, lower_bound, upper_bound, confidence_level
   - Use case: Reporting uncertainty in estimates
   - REQ: 3.8.1.2
   - Uses: scipy.stats.t.interval or bootstrap

4. **`paired_difference_ci(group1, group2, confidence=0.95)`**
   - Input: Two paired samples, confidence level
   - Output: Dict with mean_difference, lower_bound, upper_bound, confidence_level
   - Use case: PE01 confidence interval for language effect
   - REQ: 3.8.1.2

**Implementation approach:**
- Standard formulas for Cohen's d (pooled standard deviation)
- Cliff's Delta using rank-based approach
- Bootstrap confidence intervals as fallback for non-normal data
- Clear interpretation categories

**Testing approach:**
- Verify calculations against published examples
- Test with extreme cases (no effect, large effect)
- Validate interpretation categories

---

### File 4: `pes/analysis/power_analysis.py`

**Purpose:** Statistical power analysis and sample size determination

**Functions to implement:**

1. **`estimate_variance_from_pilot(pilot_data, groups=None)`**
   - Input: Pilot data (raw or by groups)
   - Output: Dict with variance_estimate, standard_deviation, sample_size_used
   - Use case: PE10 step 1 - estimate variance from pilot
   - REQ: 3.8.1.4

2. **`calculate_sample_size_t_test(effect_size, alpha=0.05, power=0.80, test_type='two-sided', paired=False)`**
   - Input: Expected effect size (Cohen's d), alpha, desired power, test type, pairing
   - Output: Dict with required_n, power, alpha, effect_size, test_type
   - Use case: PE10 step 4 - determine sample size
   - REQ: 3.8.1.4
   - Uses: statsmodels.stats.power or manual calculation

3. **`calculate_power(n, effect_size, alpha=0.05, test_type='two-sided', paired=False)`**
   - Input: Sample size, effect size, alpha, test type, pairing
   - Output: Dict with power, sample_size, effect_size, alpha
   - Use case: Checking power of completed study
   - REQ: 3.8.1.4

4. **`effect_size_from_variance(variance, mean_difference)`**
   - Input: Variance estimate, expected mean difference
   - Output: Dict with effect_size (Cohen's d), interpretation
   - Use case: PE10 step 3 - convert variance and difference to effect size
   - REQ: 3.8.1.4

5. **`apply_inflation_factor(sample_size, inflation_rate=0.15)`**
   - Input: Required sample size, inflation rate (default 15%)
   - Output: Dict with original_n, inflated_n, inflation_rate
   - Use case: PE10 step 5 - account for failures/timeouts
   - REQ: 3.8.1.4

**Implementation approach:**
- Use statsmodels.stats.power if available, fallback to manual formulas
- Clear formulas documented in docstrings
- Provide defaults matching research standards (power=0.80, alpha=0.05)
- Inflation factor based on REQ-3.6.10.5 (10-20%)

**Testing approach:**
- Verify against power analysis calculators (G*Power)
- Test with standard scenarios (small/medium/large effects)
- Validate inflation calculations

**Note:** May need to add `statsmodels` as dependency if manual calculations become complex. Will evaluate during implementation.

---

### File 5: `pes/analysis/correlation.py`

**Purpose:** Correlation analysis between variables

**Functions to implement:**

1. **`pearson_correlation(x, y, alpha=0.05)`**
   - Input: Two continuous variables, significance level
   - Output: Dict with correlation, p_value, significant, confidence_interval
   - Use case: Analyzing relationship between metrics
   - REQ: 3.8.1.5
   - Uses: scipy.stats.pearsonr

2. **`spearman_correlation(x, y, alpha=0.05)`**
   - Input: Two variables (ordinal or continuous), significance level
   - Output: Dict with correlation, p_value, significant
   - Use case: Non-parametric correlation
   - REQ: 3.8.1.5
   - Uses: scipy.stats.spearmanr

3. **`correlation_matrix(data_dict, method='pearson')`**
   - Input: Dict mapping variable names to data arrays, method
   - Output: Dict with correlation matrix, p_values matrix, variable_names
   - Use case: Exploring relationships between multiple metrics
   - REQ: 3.8.1.5

**Implementation approach:**
- Wrapper around scipy.stats correlation functions
- Add significance testing
- Return both correlation and p-value
- Matrix format for multiple variables

**Testing approach:**
- Test with known correlations (perfect, zero, negative)
- Verify p-values
- Test matrix function with multiple variables

---

### File 6: `pes/analysis/utils.py`

**Purpose:** Helper functions and data validation

**Functions to implement:**

1. **`validate_numeric_array(data, name='data', allow_empty=False, min_size=None)`**
   - Input: Data array, descriptive name, validation flags
   - Output: Validated numpy array or raises AnalysisError
   - Use case: Input validation for all analysis functions

2. **`remove_nan_paired(group1, group2)`**
   - Input: Two paired arrays
   - Output: Tuple of arrays with NaN pairs removed
   - Use case: Cleaning paired data before tests

3. **`check_minimum_sample_size(data, min_size, test_name)`**
   - Input: Data array, minimum required size, test name
   - Output: None if valid, raises AnalysisError if too small
   - Use case: Ensure sufficient data for statistical tests

4. **`format_p_value(p_value, threshold=0.001)`**
   - Input: P-value, reporting threshold
   - Output: Formatted string (e.g., "0.03" or "<0.001")
   - Use case: Report generation

5. **`interpret_effect_size(value, metric='cohens_d')`**
   - Input: Effect size value, metric type
   - Output: Interpretation string (e.g., "medium effect")
   - Use case: Human-readable reporting

**Implementation approach:**
- Comprehensive input validation
- Clear error messages with context
- Helper functions for common operations
- Formatting utilities for reports

---

### File 7: `pes/analysis/__init__.py`

**Purpose:** Public API and convenience exports

**Structure:**
```python
"""
Statistical analysis module for the Preliminary Experiments System.

This module provides comprehensive statistical analysis functions including:
- Descriptive statistics
- Hypothesis testing (t-tests, Wilcoxon, ANOVA)
- Effect size calculations (Cohen's d, Cliff's Delta)
- Power analysis and sample size determination
- Correlation analysis

All functions return dictionaries for easy serialization and reporting.
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

# Define public API
__all__ = [
    # Descriptive
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
]
```

---

## Testing Strategy

### Test File: `test_analysis.py`

Create comprehensive test suite similar to `test_datasets.py` pattern.

**Test structure:**
```python
def test_descriptive_statistics():
    """Test descriptive statistics calculations."""
    # Test with known values
    # Test edge cases (empty, single value)
    # Test with NaN handling

def test_paired_t_test():
    """Test paired t-test."""
    # Test with known dataset (verify against R/SPSS)
    # Test significance detection
    # Test edge cases

def test_cohens_d():
    """Test Cohen's d effect size."""
    # Test with known effect sizes
    # Test interpretation categories

def test_power_analysis():
    """Test sample size calculations."""
    # Test against G*Power results
    # Test standard scenarios

# ... more tests
```

**Testing approach:**
- Use known datasets with published results for validation
- Test edge cases (empty data, single values, identical groups)
- Verify p-values and interpretations
- Run tests with: `python test_analysis.py`

---

## Usage Examples

### Example 1: PE01 - Language Effect Assessment

```python
from pes.analysis import (
    descriptive_statistics,
    paired_t_test,
    wilcoxon_test,
    cohens_d,
    normality_test
)

# Scores for Italian and English versions
italian_scores = [0.85, 0.78, 0.92, 0.88, 0.75]
english_scores = [0.90, 0.82, 0.95, 0.91, 0.80]

# Check normality assumption
normality_italian = normality_test(italian_scores)
normality_english = normality_test(english_scores)

# Choose appropriate test
if normality_italian['is_normal'] and normality_english['is_normal']:
    test_result = paired_t_test(italian_scores, english_scores, alpha=0.05)
else:
    test_result = wilcoxon_test(italian_scores, english_scores, alpha=0.05)

# Calculate effect size
effect = cohens_d(italian_scores, english_scores, paired=True)

# Generate report
results = {
    'italian_stats': descriptive_statistics(italian_scores),
    'english_stats': descriptive_statistics(english_scores),
    'hypothesis_test': test_result,
    'effect_size': effect,
    'recommendation': 'Use English' if test_result['significant'] else 'Language does not matter'
}
```

### Example 2: PE04 - Temperature Optimization

```python
from pes.analysis import (
    descriptive_statistics,
    summarize_by_group,
    one_way_anova
)

# Performance at different temperatures
temp_0 = [0.88, 0.85, 0.90, 0.87]
temp_1 = [0.82, 0.80, 0.85, 0.83]
temp_2 = [0.75, 0.78, 0.72, 0.76]

# Compare temperatures
groups = [temp_0, temp_1, temp_2]
group_names = ['temp_0.0', 'temp_0.1', 'temp_0.2']

# Summary by group
summary = summarize_by_group(
    [val for group in groups for val in group],
    [name for name, group in zip(group_names, groups) for _ in group]
)

# ANOVA to test for differences
anova_result = one_way_anova(groups, alpha=0.05)

results = {
    'group_summary': summary,
    'anova': anova_result,
    'optimal_temperature': group_names[0]  # Highest mean
}
```

### Example 3: PE10 - Power Analysis

```python
from pes.analysis import (
    estimate_variance_from_pilot,
    effect_size_from_variance,
    calculate_sample_size_t_test,
    apply_inflation_factor
)

# Pilot data: differences between treatment and control
pilot_differences = [0.05, 0.08, 0.03, 0.07, 0.06, 0.04, 0.09]

# Step 1: Estimate variance
variance_est = estimate_variance_from_pilot(pilot_differences)

# Step 2: Define minimum effect size (domain knowledge)
min_effect_size = 0.5  # Medium effect

# Step 3: Calculate required sample size
sample_size = calculate_sample_size_t_test(
    effect_size=min_effect_size,
    alpha=0.05,
    power=0.80,
    test_type='two-sided',
    paired=True
)

# Step 4: Apply inflation factor for failures
final_sample = apply_inflation_factor(
    sample_size['required_n'],
    inflation_rate=0.15  # 15% inflation
)

results = {
    'variance_estimate': variance_est,
    'minimum_effect_size': min_effect_size,
    'required_sample_size': sample_size['required_n'],
    'inflated_sample_size': final_sample['inflated_n'],
    'recommendation': f"Collect {final_sample['inflated_n']} samples per condition"
}
```

---

## Implementation Checklist

### Phase 1: Setup and Dependencies
- [ ] Install numpy and scipy: `pip install numpy>=1.24.0 scipy>=1.10.0`
- [ ] Update requirements.txt or create one if missing
- [ ] Verify imports work in Python environment

### Phase 2: Core Implementation
- [ ] Create `pes/analysis/utils.py` (data validation - needed first)
- [ ] Create `pes/analysis/descriptive.py`
- [ ] Create `pes/analysis/hypothesis_tests.py`
- [ ] Create `pes/analysis/effect_sizes.py`
- [ ] Create `pes/analysis/power_analysis.py`
- [ ] Create `pes/analysis/correlation.py`
- [ ] Create `pes/analysis/__init__.py`

### Phase 3: Testing
- [ ] Create `test_analysis.py`
- [ ] Test each module with known datasets
- [ ] Test edge cases and error handling
- [ ] Verify all functions return correct dictionary format
- [ ] Run full test suite

### Phase 4: Documentation
- [ ] Add comprehensive docstrings to all functions
- [ ] Add type hints to all functions
- [ ] Create usage examples in docstrings
- [ ] Update IMPLEMENTATION_STATUS.md
- [ ] Add brief usage guide to pes/analysis/README.md (optional)

### Phase 5: Integration
- [ ] Import in experiment stubs (PE01, PE10) to verify API
- [ ] Test with simple data in experiments
- [ ] Verify error handling propagates correctly
- [ ] Verify JSON serialization of results

---

## Estimated Timeline

| Task | Time | Notes |
|------|------|-------|
| Setup + dependencies | 15 min | Install packages, verify |
| utils.py | 30 min | Validation functions |
| descriptive.py | 30 min | Basic stats, straightforward |
| hypothesis_tests.py | 60 min | Multiple tests, careful with assumptions |
| effect_sizes.py | 45 min | Cohen's d, Cliff's delta calculations |
| power_analysis.py | 60 min | Complex formulas, may need statsmodels |
| correlation.py | 30 min | Straightforward wrappers |
| __init__.py | 15 min | Exports and documentation |
| Testing | 45 min | Comprehensive test suite |
| Documentation | 15 min | Docstrings and guide |
| Integration check | 15 min | Verify with experiments |
| **TOTAL** | **4.5 hours** | Buffer included |

---

## Potential Issues and Mitigations

### Issue 1: statsmodels dependency for power analysis
**Problem:** May need statsmodels.stats.power for accurate power calculations
**Mitigation:**
- Start with manual formulas using scipy.stats.t
- Add statsmodels only if manual calculations become too complex
- Document limitation if using approximations

### Issue 2: Numerical instability with small samples
**Problem:** Some tests fail with n < 5
**Mitigation:**
- Add minimum sample size checks in utils.py
- Raise AnalysisError with clear message about insufficient data
- Document minimum requirements in docstrings

### Issue 3: Multiple comparison corrections
**Problem:** ANOVA may need post-hoc tests
**Mitigation:**
- Implement basic ANOVA first (sufficient for PE04)
- Add Bonferroni/Tukey corrections in future iteration if needed
- Document limitation in current implementation

### Issue 4: Bootstrap for confidence intervals
**Problem:** Bootstrap implementation could be time-consuming
**Mitigation:**
- Use t-distribution CI as primary method
- Defer bootstrap to future iteration
- Document as enhancement opportunity

---

## Success Criteria

1. ✅ All functions return consistent dictionary format
2. ✅ All functions have comprehensive docstrings with examples
3. ✅ All functions have type hints
4. ✅ Test suite passes with known datasets
5. ✅ Edge cases handled gracefully (empty data, NaN, etc.)
6. ✅ Can be imported and used in PE01, PE04, PE10 stubs
7. ✅ Error handling uses AnalysisError appropriately
8. ✅ Results are JSON-serializable for experiment storage
9. ✅ Satisfies all REQ-3.8.1.* requirements
10. ✅ Documentation updated in IMPLEMENTATION_STATUS.md

---

## Post-Implementation: Next Steps

After Phase 2 is complete:

1. **Update IMPLEMENTATION_STATUS.md**
   - Mark REQ-3.8.1 as complete
   - Update component status table
   - Document new dependencies

2. **Update experiments to use analysis module**
   - PE01: Add statistical comparison logic
   - PE04: Add ANOVA for temperature comparison
   - PE10: Add power analysis calculations

3. **Consider Phase 6: Enhanced Reporting**
   - Use analysis results for formatted reports
   - Generate statistical tables
   - Add visualizations of distributions

---

## Questions for Review

Before proceeding with implementation:

1. **statsmodels dependency:** Should we add it now or defer to later?
   - **Recommendation:** Start without it, add if needed during power analysis implementation

2. **Bootstrap methods:** Include in initial implementation or defer?
   - **Recommendation:** Defer to future enhancement, use t-distribution CIs

3. **Test data:** Should we include test datasets in repository?
   - **Recommendation:** Generate synthetic test data in test_analysis.py, don't commit large files

4. **API naming:** Any preference on function naming conventions?
   - **Recommendation:** Current plan uses descriptive snake_case, consistent with existing code

---

## Approval Required

This plan is ready for review. Once approved, implementation can begin immediately following the checklist above.

**Estimated completion time:** 3-4 hours of focused work
**Dependencies:** numpy, scipy (standard scientific Python libraries)
**Risk level:** Low (well-defined scope, standard libraries, clear requirements)
