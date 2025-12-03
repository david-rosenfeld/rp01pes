"""
PE10: Power Analysis

This experiment implements preliminary experiment 10 (PE10) from the research plan.
Conducts statistical power analysis to determine required sample sizes for experiments.

Implements REQ-3.6.10 (Power Analysis).
"""

from typing import Dict, Any, List, Union, Optional
import numpy as np

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..analysis import (
    estimate_variance_from_pilot,
    calculate_sample_size_t_test,
    calculate_power,
    effect_size_from_variance,
    apply_inflation_factor
)


class PowerAnalysisExperiment(BaseExperiment):
    """
    Power Analysis experiment.

    Conducts statistical power analysis to determine required sample sizes
    for all TaskTypes. Uses pilot data to estimate variance and calculates
    sample sizes needed to detect minimum effect sizes with 80% power at α=0.05.

    Implements REQ-3.6.10.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE10"):
        """
        Initialize Power Analysis experiment.

        Args:
            config: Configuration manager
            experiment_id: Experiment identifier (default: "PE10")
        """
        super().__init__(config, experiment_id)

        # Load experiment-specific configuration
        self.exp_config = config.get('experiments.poweranalysis', {})

        # Validate configuration
        self._validate_experiment_config()

        self.log_info("Power Analysis experiment initialized")

    def _validate_experiment_config(self) -> None:
        """
        Validate experiment-specific configuration.

        Raises:
            ExperimentError: If configuration is invalid
        """
        # Check for required fields
        if 'pilot_data' not in self.exp_config and 'task_types' not in self.exp_config:
            raise ExperimentError(
                "Power analysis experiment requires either 'pilot_data' or 'task_types' in configuration"
            )

    def get_description(self) -> str:
        """Get experiment description."""
        return "Conduct statistical power analysis determining required sample sizes"

    def run(self) -> Dict[str, Any]:
        """
        Execute Power Analysis experiment.

        This implements the PE10 workflow (REQ-3.6.10):
        1. Collect pilot data for all TaskTypes (or use provided data)
        2. Compute variance estimates for Δ scores per TaskType
        3. Define minimum effect sizes per TaskType
        4. Calculate required sample size (power=0.80, α=0.05)
        5. Apply inflation factor (10-20% for failures/timeouts)
        6. Output sample sizes per TaskType

        Returns:
            Dictionary containing experiment results:
                - task_types: List of TaskTypes analyzed
                - power_analysis_results: Per-TaskType analysis
                - summary: Summary statistics across all TaskTypes
                - recommendations: Sample size recommendations

        Implements REQ-3.6.10.1 through REQ-3.6.10.6
        """
        self.log_info("Starting power analysis experiment")

        # Step 1: Load or collect pilot data (REQ-3.6.10.1)
        pilot_data = self._load_pilot_data()
        task_types = list(pilot_data.keys())
        self.log_info(f"Analyzing {len(task_types)} TaskTypes")

        # Step 2: Analyze each TaskType
        power_analysis_results = {}

        for task_type in task_types:
            self.log_info(f"Analyzing TaskType: {task_type}")

            # Get pilot data for this TaskType
            task_pilot_data = pilot_data[task_type]

            # Perform power analysis for this TaskType
            result = self._analyze_task_type(task_type, task_pilot_data)
            power_analysis_results[task_type] = result

        # Step 3: Generate summary and recommendations
        summary = self._generate_summary(power_analysis_results)
        recommendations = self._generate_recommendations(power_analysis_results)

        # Compile results
        results = {
            'task_types': task_types,
            'power_analysis_results': power_analysis_results,
            'summary': summary,
            'recommendations': recommendations,
            'experiment_id': self.experiment_id
        }

        self.log_info("Power analysis experiment completed")
        return results

    def _load_pilot_data(self) -> Dict[str, Union[List[float], Dict[str, Any]]]:
        """
        Load pilot data from configuration or generate sample data.

        Implements REQ-3.6.10.1: Collect pilot data for all TaskTypes.

        Returns:
            Dictionary mapping TaskType to pilot data:
                - For paired comparisons: list of difference scores
                - For single groups: list of scores
                - Can also be dict with 'differences' or 'groups' keys
        """
        # Check if pilot data is provided in config
        if 'pilot_data' in self.exp_config:
            pilot_data = self.exp_config['pilot_data']
            self.log_info(f"Loaded pilot data from configuration")
            return pilot_data

        # Otherwise, use task_types from config with default assumptions
        task_types = self.exp_config.get('task_types', ['trace', 'recover', 'fill'])

        self.log_warning(
            "No pilot data provided - using example data for demonstration. "
            "In real experiments, provide actual pilot data."
        )

        # Generate example pilot data (differences between conditions)
        # These would come from actual pilot runs in practice
        example_data = {
            'trace': [0.05, 0.08, 0.03, 0.07, 0.06, 0.04, 0.09, 0.05],
            'recover': [0.10, 0.12, 0.08, 0.11, 0.09, 0.13, 0.10, 0.11],
            'fill': [0.06, 0.07, 0.05, 0.08, 0.06, 0.07, 0.05, 0.06]
        }

        # Use only the task types specified
        pilot_data = {tt: example_data.get(tt, [0.05, 0.07, 0.06, 0.08])
                      for tt in task_types}

        return pilot_data

    def _analyze_task_type(
        self,
        task_type: str,
        pilot_data: Union[List[float], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform power analysis for a single TaskType.

        Implements REQ-3.6.10.2 through REQ-3.6.10.5:
        - Compute variance estimates
        - Define minimum effect sizes
        - Calculate required sample size
        - Apply inflation factor

        Args:
            task_type: TaskType name
            pilot_data: Pilot data for this TaskType

        Returns:
            Dictionary with complete power analysis for this TaskType
        """
        # Step 2.1: Estimate variance from pilot data (REQ-3.6.10.2)
        variance_result = estimate_variance_from_pilot(pilot_data)

        self.log_info(
            f"  Variance estimate for {task_type}: {variance_result['variance_estimate']:.4f}"
        )

        # Step 2.2: Get minimum effect size (REQ-3.6.10.3)
        min_effect_size = self._get_minimum_effect_size(task_type)

        self.log_info(f"  Minimum effect size for {task_type}: {min_effect_size}")

        # Alternative: Calculate effect size from variance and expected difference
        if 'expected_difference' in self.exp_config.get(task_type, {}):
            expected_diff = self.exp_config[task_type]['expected_difference']
            effect_result = effect_size_from_variance(
                variance=variance_result['variance_estimate'],
                mean_difference=expected_diff
            )
            calculated_effect = effect_result['effect_size']

            self.log_info(
                f"  Calculated effect size from expected difference: {calculated_effect:.3f}"
            )
        else:
            calculated_effect = None

        # Step 2.3: Calculate required sample size (REQ-3.6.10.4)
        alpha = self.exp_config.get('alpha', 0.05)
        power = self.exp_config.get('power', 0.80)
        test_type = self.exp_config.get('test_type', 'two-sided')
        paired = self.exp_config.get('paired', True)

        sample_size_result = calculate_sample_size_t_test(
            effect_size=min_effect_size,
            alpha=alpha,
            power=power,
            test_type=test_type,
            paired=paired
        )

        self.log_info(
            f"  Required sample size for {task_type}: {sample_size_result['required_n']}"
        )

        # Step 2.4: Apply inflation factor (REQ-3.6.10.5)
        inflation_rate = self.exp_config.get('inflation_rate', 0.15)  # Default 15%

        inflated_result = apply_inflation_factor(
            sample_size=sample_size_result['required_n'],
            inflation_rate=inflation_rate
        )

        self.log_info(
            f"  Inflated sample size for {task_type}: {inflated_result['inflated_n']} "
            f"({inflation_rate*100:.0f}% inflation)"
        )

        # Calculate achieved power with inflated sample size
        power_check = calculate_power(
            n=inflated_result['inflated_n'],
            effect_size=min_effect_size,
            alpha=alpha,
            test_type=test_type,
            paired=paired
        )

        # Compile complete analysis for this TaskType
        return {
            'task_type': task_type,
            'pilot_data_summary': {
                'sample_size': variance_result['sample_size_used'],
                'variance_estimate': variance_result['variance_estimate'],
                'standard_deviation': variance_result['standard_deviation']
            },
            'effect_size': {
                'minimum_detectable': min_effect_size,
                'calculated_from_pilot': calculated_effect,
                'interpretation': self._interpret_effect_size(min_effect_size)
            },
            'sample_size_calculation': {
                'required_n': sample_size_result['required_n'],
                'target_power': power,
                'alpha': alpha,
                'test_type': test_type,
                'paired': paired
            },
            'inflation': {
                'original_n': inflated_result['original_n'],
                'inflated_n': inflated_result['inflated_n'],
                'inflation_rate': inflated_result['inflation_rate'],
                'additional_samples': inflated_result['additional_samples']
            },
            'achieved_power': power_check['power'],
            'recommendation': inflated_result['inflated_n']
        }

    def _get_minimum_effect_size(self, task_type: str) -> float:
        """
        Get minimum effect size to detect for a TaskType.

        Implements REQ-3.6.10.3: Define minimum effect sizes per TaskType.

        Args:
            task_type: TaskType name

        Returns:
            Cohen's d effect size (typically 0.3-0.5 for "small to medium")
        """
        # Check if task-specific effect size is configured
        task_config = self.exp_config.get(task_type, {})
        if 'min_effect_size' in task_config:
            return task_config['min_effect_size']

        # Check for global default
        if 'default_min_effect_size' in self.exp_config:
            return self.exp_config['default_min_effect_size']

        # Default to medium effect size (Cohen's d = 0.5)
        # This is a reasonable default for preliminary experiments
        return 0.5

    def _interpret_effect_size(self, effect_size: float) -> str:
        """
        Interpret Cohen's d effect size magnitude.

        Args:
            effect_size: Cohen's d value

        Returns:
            Interpretation string
        """
        if effect_size < 0.2:
            return "negligible"
        elif effect_size < 0.5:
            return "small"
        elif effect_size < 0.8:
            return "medium"
        else:
            return "large"

    def _generate_summary(
        self,
        power_analysis_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics across all TaskTypes.

        Args:
            power_analysis_results: Per-TaskType analysis results

        Returns:
            Summary dictionary with aggregate statistics
        """
        # Extract key metrics
        required_ns = [r['sample_size_calculation']['required_n']
                      for r in power_analysis_results.values()]
        inflated_ns = [r['inflation']['inflated_n']
                      for r in power_analysis_results.values()]
        achieved_powers = [r['achieved_power']
                          for r in power_analysis_results.values()]

        return {
            'total_task_types': len(power_analysis_results),
            'sample_size_range': {
                'min_required': min(required_ns),
                'max_required': max(required_ns),
                'mean_required': np.mean(required_ns),
                'min_inflated': min(inflated_ns),
                'max_inflated': max(inflated_ns),
                'mean_inflated': np.mean(inflated_ns)
            },
            'power_summary': {
                'min_achieved_power': min(achieved_powers),
                'max_achieved_power': max(achieved_powers),
                'mean_achieved_power': np.mean(achieved_powers)
            }
        }

    def _generate_recommendations(
        self,
        power_analysis_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate recommendations for sample sizes.

        Implements REQ-3.6.10.6: Output sample sizes per TaskType.

        Args:
            power_analysis_results: Per-TaskType analysis results

        Returns:
            Recommendations dictionary
        """
        recommendations = {
            'per_task_type': {},
            'overall': {}
        }

        # Per-TaskType recommendations
        for task_type, result in power_analysis_results.items():
            recommendations['per_task_type'][task_type] = {
                'recommended_n': result['recommendation'],
                'minimum_n': result['sample_size_calculation']['required_n'],
                'expected_power': result['achieved_power'],
                'rationale': (
                    f"Need {result['recommendation']} samples to detect "
                    f"effect size of {result['effect_size']['minimum_detectable']:.2f} "
                    f"with {result['sample_size_calculation']['target_power']:.0%} power "
                    f"(includes {result['inflation']['inflation_rate']:.0%} inflation for failures)"
                )
            }

        # Overall recommendations
        max_inflated_n = max(r['inflation']['inflated_n']
                            for r in power_analysis_results.values())

        recommendations['overall'] = {
            'conservative_n': max_inflated_n,
            'rationale': (
                f"Use {max_inflated_n} samples for all TaskTypes to ensure "
                f"adequate power across all conditions"
            )
        }

        return recommendations
