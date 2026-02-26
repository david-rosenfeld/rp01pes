"""
PE08: Control Condition Data Determination

Implements REQ-3.6.8 (Control Condition Data Determination).
"""

from typing import Dict, Any, List
import random

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..llm.factory import get_provider
from ..datasets import load_dataset, generate_bundles_for_dataset


class ControlConditionExperiment(BaseExperiment):
    """
    Control Condition Data Determination experiment.

    Implements REQ-3.6.8.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE08"):
        super().__init__(config, experiment_id)
        self.exp_config = config.get('experiments.control_condition', {})
        self.log_info("Control Condition experiment initialized")

    def get_description(self) -> str:
        return "Determine appropriate control condition data (no traceability links)"

    def run(self) -> Dict[str, Any]:
        """
        Execute Control Condition Determination experiment.

        Returns:
            Dictionary containing recommended control variants per model type
        """
        self.log_info("Starting control condition experiment")

        # Load configuration
        variants = self.exp_config.get('variants', ['full_codebase', 'expanded_file_list'])
        expansion_factors = self.exp_config.get('expansion_factors', [2, 3, 5])
        sample_size = self.exp_config.get('sample_size', 10)
        model_types = self.exp_config.get('test_separately', ['prompt_based', 'agentic'])

        # Load dataset
        dataset_name = self.exp_config.get('dataset', 'ebt')
        dataset = load_dataset(dataset_name,
            {'base_path': self.config.get('datasets.base_path', './datasets')})

        # Generate traceability bundles (ground truth)
        bundles = generate_bundles_for_dataset(dataset)

        # Get provider
        model_config = self.config.get('experiments.control_condition.model',
            self.config.get('models.mock', {'provider': 'mock'}))
        provider = get_provider(model_config.get('provider', 'mock'), model_config)

        results = {'variants': {}, 'recommendations': {}}

        for model_type in model_types:
            self.log_info(f"Testing control conditions for model type: {model_type}")

            variant_results = {}

            # Test full_codebase variant
            if 'full_codebase' in variants:
                metrics = self._test_variant(
                    'full_codebase', None,
                    provider, dataset, bundles, sample_size, model_type
                )
                variant_results['full_codebase'] = metrics
                self.log_info(f"  full_codebase: correctness={metrics['correctness']:.3f}")

            # Test expanded file list variants
            if 'expanded_file_list' in variants:
                for factor in expansion_factors:
                    variant_name = f'expanded_{factor}x'
                    metrics = self._test_variant(
                        'expanded_file_list', factor,
                        provider, dataset, bundles, sample_size, model_type
                    )
                    variant_results[variant_name] = metrics
                    self.log_info(f"  {variant_name}: correctness={metrics['correctness']:.3f}")

            # Select best variant
            best_variant, rationale = self._select_best_variant(variant_results)

            results['variants'][model_type] = variant_results
            results['recommendations'][model_type] = {
                'selected_variant': best_variant,
                'rationale': rationale,
                'metrics': variant_results.get(best_variant, {})
            }

        self.log_info("Control condition experiment completed")
        return results

    def _test_variant(
        self,
        variant_type: str,
        expansion_factor: int,
        provider,
        dataset,
        bundles: Dict,
        sample_size: int,
        model_type: str
    ) -> Dict[str, float]:
        """
        Test a control condition variant.

        Returns metrics: completion_rate, correctness, localization_accuracy, avg_time
        """
        sample_bundles = list(bundles.items())[:sample_size]

        completions = 0
        correct = 0
        localization_scores = []
        times = []

        for req_id, bundle in sample_bundles:
            # Prepare control condition input
            if variant_type == 'full_codebase':
                # Include all source files
                context_files = list(dataset.source_files.keys())
            else:
                # Expanded file list: linked files + extra
                ground_truth_files = [sf.file_name for sf in bundle.linked_files]
                extra_count = len(ground_truth_files) * (expansion_factor - 1)
                all_files = list(dataset.source_files.keys())
                extra_files = [f for f in all_files if f not in ground_truth_files]
                random.shuffle(extra_files)
                context_files = ground_truth_files + extra_files[:extra_count]

            # Create task
            requirement = dataset.requirements.get(req_id)
            if not requirement:
                continue

            prompt = self._create_control_task(
                requirement, context_files, dataset, model_type
            )

            # Execute
            import time
            start = time.time()
            response = provider.generate(prompt=prompt, max_tokens=1000)
            elapsed = time.time() - start
            times.append(elapsed)

            # Check completion
            if response.text and len(response.text.strip()) > 10:
                completions += 1

            # Evaluate correctness
            ground_truth_files = [sf.file_name for sf in bundle.linked_files]
            is_correct, predicted_files = self._evaluate_correctness(
                response.text, ground_truth_files, requirement
            )
            if is_correct:
                correct += 1

            # Localization accuracy
            loc_accuracy = self._calculate_localization_accuracy(
                predicted_files, ground_truth_files
            )
            localization_scores.append(loc_accuracy)

        n = len(sample_bundles)
        return {
            'completion_rate': completions / n if n > 0 else 0.0,
            'correctness': correct / n if n > 0 else 0.0,
            'localization_accuracy': sum(localization_scores) / n if n > 0 else 0.0,
            'avg_execution_time': sum(times) / n if n > 0 else 0.0,
            'sample_size': n
        }

    def _create_control_task(
        self,
        requirement,
        context_files: List[str],
        dataset,
        model_type: str
    ) -> str:
        """Create task prompt for control condition."""
        # Build file context
        file_context = []
        for filename in context_files[:20]:  # Limit to prevent context overflow
            if filename in dataset.source_files:
                content = dataset.source_files[filename].content[:500]
                file_context.append(f"// {filename}\n{content}\n")

        return f"""You are given a software requirement and a codebase.
Identify which files need to be modified to implement this requirement.

REQUIREMENT:
{requirement.content}

CODEBASE FILES:
{chr(10).join(file_context)}

TASK:
List the files that should be modified to implement this requirement.
Format: one filename per line.
"""

    def _evaluate_correctness(
        self,
        response: str,
        ground_truth_files: List[str],
        requirement
    ) -> tuple:
        """
        Evaluate if response correctly identifies files.

        Returns:
            (is_correct, predicted_files)
        """
        # Extract file references from response
        predicted_files = []
        for line in response.split('\n'):
            line = line.strip()
            # Look for file-like patterns
            if '.' in line and any(ext in line.lower() for ext in ['.java', '.py', '.js', '.cs']):
                # Clean up the line
                for word in line.split():
                    if '.' in word:
                        # Remove punctuation
                        clean = word.strip(',:;()[]{}"\'-')
                        if clean:
                            predicted_files.append(clean)

        # Check if any ground truth files were identified
        if not ground_truth_files:
            # No ground truth means any reasonable response is "correct"
            return len(predicted_files) > 0, predicted_files

        overlap = set(predicted_files) & set(ground_truth_files)
        # Consider correct if at least 50% of ground truth identified
        is_correct = len(overlap) >= len(ground_truth_files) * 0.5

        return is_correct, predicted_files

    def _calculate_localization_accuracy(
        self,
        predicted_files: List[str],
        ground_truth_files: List[str]
    ) -> float:
        """Calculate localization accuracy score."""
        if not ground_truth_files:
            return 1.0 if not predicted_files else 0.0

        correct_predictions = set(predicted_files) & set(ground_truth_files)
        return len(correct_predictions) / len(ground_truth_files)

    def _select_best_variant(
        self,
        variant_results: Dict[str, Dict]
    ) -> tuple:
        """
        Select best control variant.

        Criteria:
        - correctness < 100% (not trivial)
        - correctness > 20% (not impossible)
        - meaningful challenge level
        """
        candidates = []

        for name, metrics in variant_results.items():
            correctness = metrics['correctness']

            # Filter out trivial (100%) and impossible (<20%)
            if 0.20 < correctness < 1.0:
                candidates.append((name, metrics, correctness))

        if not candidates:
            # Fall back to any variant
            best = min(variant_results.items(),
                      key=lambda x: abs(x[1]['correctness'] - 0.5))
            return best[0], "No ideal variant found; selected closest to 50% correctness"

        # Pick variant closest to 50% correctness (balanced challenge)
        best = min(candidates, key=lambda x: abs(x[2] - 0.5))
        rationale = (
            f"Selected {best[0]} with {best[2]*100:.1f}% correctness, "
            f"providing meaningful challenge without being impossible"
        )

        return best[0], rationale
