"""
PE05: Max Token Determination

This experiment determines appropriate max token limits for each TaskType
by analyzing output length distributions from sample executions.

Implements REQ-3.6.5 (Max Token Determination).
"""

from typing import Dict, Any, List
import numpy as np

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..llm.factory import get_provider
from ..datasets import load_dataset
from ..analysis import descriptive_statistics


class MaxTokenDeterminationExperiment(BaseExperiment):
    """
    Max Token Determination experiment.

    Measures output token lengths across TaskTypes to determine appropriate
    max_tokens settings. Analyzes distributions and recommends either specific
    limits or no limit (provider default).

    Implements REQ-3.6.5.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE05"):
        """
        Initialize Max Token Determination experiment.

        Args:
            config: Configuration manager
            experiment_id: Experiment identifier (default: "PE05")
        """
        super().__init__(config, experiment_id)

        # Load experiment-specific configuration
        self.exp_config = config.get('experiments.maxtokendetermination', {})

        # Validate configuration
        self._validate_experiment_config()

        self.log_info("Max Token Determination experiment initialized")

    def _validate_experiment_config(self) -> None:
        """
        Validate experiment-specific configuration.

        Raises:
            ExperimentError: If configuration is invalid
        """
        # Check for required fields
        if 'model' not in self.exp_config:
            raise ExperimentError(
                "Max token determination experiment requires 'model' in configuration"
            )

        if 'task_types' not in self.exp_config:
            raise ExperimentError(
                "Max token determination experiment requires 'task_types' in configuration"
            )

    def get_description(self) -> str:
        """Get experiment description."""
        return "Determine appropriate max token limits for each TaskType"

    def run(self) -> Dict[str, Any]:
        """
        Execute Max Token Determination experiment.

        This implements the PE05 workflow (REQ-3.6.5):
        1. Execute sample tasks for each TaskType
        2. Measure output token lengths (REQ-3.6.5.2)
        3. Compute distribution statistics (REQ-3.6.5.3)
        4. Assess truncation risk at various limits (REQ-3.6.5.4)
        5. Recommend max_tokens per TaskType (REQ-3.6.5.5)
        6. Document justification (REQ-3.6.5.6)

        Returns:
            Dictionary containing experiment results:
                - task_types: List of TaskTypes analyzed
                - token_measurements: Token length data per TaskType
                - distribution_statistics: Statistical summaries
                - truncation_analysis: Risk assessment at various limits
                - recommendations: Max token recommendations with justification

        Implements REQ-3.6.5.1 through REQ-3.6.5.6
        """
        self.log_info("Starting max token determination experiment")

        # Step 1: Load model and dataset
        model_config = self._load_model_config()
        dataset_info = self._load_dataset()

        task_types = self.exp_config.get('task_types', [])

        # Step 2: Measure output lengths for each TaskType (REQ-3.6.5.2)
        token_measurements = {}
        for task_type in task_types:
            self.log_info(f"Measuring output lengths for TaskType: {task_type}")
            measurements = self._measure_output_lengths(
                task_type,
                model_config,
                dataset_info
            )
            token_measurements[task_type] = measurements

        # Step 3: Compute distribution statistics (REQ-3.6.5.3)
        distribution_statistics = self._compute_distribution_statistics(token_measurements)

        # Step 4: Assess truncation risk (REQ-3.6.5.4)
        truncation_analysis = self._assess_truncation_risk(
            token_measurements,
            distribution_statistics
        )

        # Step 5: Generate recommendations (REQ-3.6.5.5)
        recommendations = self._generate_recommendations(
            distribution_statistics,
            truncation_analysis
        )

        # Compile results
        results = {
            'experiment_id': self.experiment_id,
            'task_types': task_types,
            'token_measurements': token_measurements,
            'distribution_statistics': distribution_statistics,
            'truncation_analysis': truncation_analysis,
            'recommendations': recommendations
        }

        self.log_info("Max token determination experiment completed")
        self._log_recommendations(recommendations)

        return results

    def _load_model_config(self) -> Dict[str, Any]:
        """
        Load model configuration.

        Returns:
            Model configuration dictionary
        """
        model_config = self.exp_config['model'].copy()

        # Ensure required fields
        if 'provider' not in model_config:
            model_config['provider'] = 'mock'

        if 'name' not in model_config:
            model_config['name'] = 'mock-model'

        return model_config

    def _load_dataset(self) -> Dict[str, Any]:
        """
        Load dataset for testing.

        Returns:
            Dataset information dictionary
        """
        dataset_name = self.exp_config.get('dataset', 'albergate')

        # Get dataset configuration
        dataset_config = self.config.get('datasets', {})
        if not dataset_config:
            # Use default base path
            dataset_config = {'base_path': './datasets'}

        # Load dataset
        dataset = load_dataset(dataset_name, dataset_config)

        return {
            'name': dataset_name,
            'dataset': dataset
        }

    def _measure_output_lengths(
        self,
        task_type: str,
        model_config: Dict[str, Any],
        dataset_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Measure output token lengths for a TaskType.

        Implements REQ-3.6.5.2: Output Length Measurement.

        Args:
            task_type: TaskType to measure
            model_config: Model configuration
            dataset_info: Dataset information

        Returns:
            Dictionary with token length measurements
        """
        # Create provider
        provider = get_provider(
            model_config['provider'],
            model_config
        )

        # Get sample requirements from dataset
        dataset = dataset_info['dataset']
        sample_size = self.exp_config.get('sample_size', 20)

        # Get sample of requirements (limited to sample_size)
        requirements = list(dataset.requirements.values())[:sample_size]

        # Measure output lengths
        token_lengths = []
        for req in requirements:
            # Generate prompt based on task type
            prompt = self._create_task_prompt(task_type, req)

            # Get response (no max_tokens limit)
            response = provider.generate(
                prompt=prompt,
                temperature=model_config.get('temperature', 0.7)
                # Deliberately omit max_tokens to see natural length
            )

            # Record completion tokens
            token_lengths.append(response.completion_tokens)

        return {
            'task_type': task_type,
            'sample_size': len(token_lengths),
            'token_lengths': token_lengths
        }

    def _create_task_prompt(self, task_type: str, requirement) -> str:
        """
        Create prompt for task based on type.

        Args:
            task_type: Type of task (trace, recover, fill, etc.)
            requirement: Requirement object

        Returns:
            Formatted prompt
        """
        # Create task-specific prompts
        if task_type == 'trace':
            return f"Identify all trace links for this requirement:\n\n{requirement.content}"
        elif task_type == 'recover':
            return f"Recover missing trace links for this requirement:\n\n{requirement.content}"
        elif task_type == 'fill':
            return f"Fill in traceability information for this requirement:\n\n{requirement.content}"
        else:
            # Generic prompt
            return f"Analyze this requirement and provide trace links:\n\n{requirement.content}"

    def _compute_distribution_statistics(
        self,
        token_measurements: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute distribution statistics for token lengths.

        Implements REQ-3.6.5.3: Distribution Analysis.

        Args:
            token_measurements: Token length measurements

        Returns:
            Distribution statistics per TaskType
        """
        statistics = {}

        for task_type, measurements in token_measurements.items():
            token_lengths = measurements['token_lengths']

            # Compute descriptive statistics
            desc_stats = descriptive_statistics(token_lengths)

            # Add percentiles
            percentile_95 = float(np.percentile(token_lengths, 95))
            percentile_99 = float(np.percentile(token_lengths, 99))

            statistics[task_type] = {
                'mean': desc_stats['mean'],
                'median': desc_stats['median'],
                'std': desc_stats['std'],
                'min': desc_stats['min'],
                'max': desc_stats['max'],
                'q1': desc_stats['q1'],
                'q3': desc_stats['q3'],
                'percentile_95': percentile_95,
                'percentile_99': percentile_99,
                'sample_size': len(token_lengths)
            }

        return statistics

    def _assess_truncation_risk(
        self,
        token_measurements: Dict[str, Dict[str, Any]],
        distribution_statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess truncation risk at various token limits.

        Implements REQ-3.6.5.4: Truncation Risk Assessment.

        Args:
            token_measurements: Token length measurements
            distribution_statistics: Distribution statistics

        Returns:
            Truncation risk analysis
        """
        # Define candidate limits to test
        candidate_limits = self.exp_config.get(
            'candidate_limits',
            [100, 200, 300, 500, 1000, 2000]
        )

        analysis = {}

        for task_type, measurements in token_measurements.items():
            token_lengths = measurements['token_lengths']
            stats = distribution_statistics[task_type]

            limit_analysis = []

            for limit in candidate_limits:
                # Calculate truncation rate
                truncated = sum(1 for length in token_lengths if length > limit)
                truncation_rate = truncated / len(token_lengths)

                # Calculate how much longer the limit is compared to typical outputs
                headroom_vs_mean = (limit - stats['mean']) / stats['mean']
                headroom_vs_95th = (limit - stats['percentile_95']) / stats['percentile_95']

                limit_analysis.append({
                    'limit': limit,
                    'truncation_rate': truncation_rate,
                    'truncation_count': truncated,
                    'headroom_vs_mean': headroom_vs_mean,
                    'headroom_vs_95th': headroom_vs_95th,
                    'covers_95th_percentile': limit >= stats['percentile_95'],
                    'covers_99th_percentile': limit >= stats['percentile_99'],
                    'covers_max': limit >= stats['max']
                })

            analysis[task_type] = {
                'limits_tested': candidate_limits,
                'limit_analysis': limit_analysis
            }

        return analysis

    def _generate_recommendations(
        self,
        distribution_statistics: Dict[str, Any],
        truncation_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate max token recommendations.

        Implements REQ-3.6.5.5: Max Token Recommendation
        and REQ-3.6.5.6: Justification Documentation.

        Args:
            distribution_statistics: Distribution statistics
            truncation_analysis: Truncation risk analysis

        Returns:
            Recommendations with justifications
        """
        recommendations = {}

        # Get acceptable truncation threshold
        max_truncation_rate = self.exp_config.get('max_truncation_rate', 0.05)  # 5%

        for task_type, stats in distribution_statistics.items():
            analysis = truncation_analysis[task_type]

            # Find smallest limit that meets criteria
            recommended_limit = None
            justification_parts = []

            for limit_data in analysis['limit_analysis']:
                if limit_data['truncation_rate'] <= max_truncation_rate:
                    # This limit is acceptable
                    if recommended_limit is None:
                        recommended_limit = limit_data['limit']

                        # Build justification
                        justification_parts.append(
                            f"Limit of {recommended_limit} tokens covers "
                            f"{(1 - limit_data['truncation_rate']) * 100:.1f}% of observed outputs"
                        )

                        if limit_data['covers_95th_percentile']:
                            justification_parts.append(
                                f"exceeds 95th percentile ({stats['percentile_95']:.0f} tokens)"
                            )

                        if limit_data['covers_99th_percentile']:
                            justification_parts.append(
                                f"exceeds 99th percentile ({stats['percentile_99']:.0f} tokens)"
                            )

                        headroom_pct = limit_data['headroom_vs_mean'] * 100
                        justification_parts.append(
                            f"provides {headroom_pct:.0f}% headroom over mean ({stats['mean']:.0f} tokens)"
                        )

                        break

            # Decide on final recommendation
            if recommended_limit is None:
                # No limit meets criteria - recommend no explicit limit
                recommendation = {
                    'max_tokens': None,
                    'recommendation_type': 'no_limit',
                    'justification': (
                        f"Output lengths for {task_type} are highly variable "
                        f"(max: {stats['max']:.0f}, 99th percentile: {stats['percentile_99']:.0f}). "
                        f"Recommend using provider default to avoid truncation."
                    )
                }
            else:
                # Recommend specific limit
                recommendation = {
                    'max_tokens': recommended_limit,
                    'recommendation_type': 'specific_limit',
                    'justification': '; '.join(justification_parts) + '.',
                    'distribution_summary': {
                        'mean': stats['mean'],
                        'median': stats['median'],
                        'percentile_95': stats['percentile_95'],
                        'percentile_99': stats['percentile_99'],
                        'max': stats['max']
                    }
                }

            recommendations[task_type] = recommendation

        return recommendations

    def _log_recommendations(self, recommendations: Dict[str, Any]) -> None:
        """
        Log max token recommendations.

        Args:
            recommendations: Recommendation data
        """
        self.log_info("=" * 60)
        self.log_info("Max Token Recommendations")
        self.log_info("=" * 60)

        for task_type, rec in recommendations.items():
            if rec['max_tokens'] is None:
                self.log_info(f"{task_type}: No explicit limit (use provider default)")
            else:
                self.log_info(f"{task_type}: {rec['max_tokens']} tokens")

        self.log_info("=" * 60)
