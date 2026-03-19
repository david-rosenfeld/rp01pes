"""
PE01: Language Effect Assessment

This experiment assesses model performance on Italian-language requirements
by running traceability tasks against the Albergate or SMOS datasets and
evaluating correctness against ground-truth trace links.

The output is a per-model accuracy profile (precision, recall, F1) that
the researcher uses to judge whether Italian requirements are usable as-is
or require translation / separate analysis.

Implements REQ-3.6.1 (Language Effect Assessment).
"""

import re
from typing import Dict, Any, List, Set

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..llm.factory import get_provider
from ..datasets import load_dataset
from ..analysis import (
    descriptive_statistics,
    confidence_interval
)


class LanguageEffectExperiment(BaseExperiment):
    """
    Language Effect Assessment experiment.

    Runs traceability tasks on Italian-language requirements and evaluates
    model responses against ground-truth trace links. Reports per-model
    and aggregate precision, recall, and F1 scores so the researcher can
    determine whether Italian requirements are usable as-is.

    Implements REQ-3.6.1.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE01"):
        """
        Initialize Language Effect Assessment experiment.

        Args:
            config: Configuration manager
            experiment_id: Experiment identifier (default: "PE01")
        """
        super().__init__(config, experiment_id)

        # Load experiment-specific configuration
        self.exp_config = config.get('experiments.language_effect', {})

        # Validate configuration
        self._validate_experiment_config()

        self.log_info("Language Effect experiment initialized")

    def _validate_experiment_config(self) -> None:
        """
        Validate experiment-specific configuration.

        Raises:
            ExperimentError: If configuration is invalid
        """
        if 'models' not in self.exp_config:
            raise ExperimentError(
                "Language effect experiment requires 'models' in configuration"
            )

        if 'dataset' not in self.exp_config:
            raise ExperimentError(
                "Language effect experiment requires 'dataset' in configuration"
            )

    def get_description(self) -> str:
        """Get experiment description."""
        return (
            "Assess model accuracy on Italian-language requirements "
            "using ground-truth trace link evaluation"
        )

    def run(self) -> Dict[str, Any]:
        """
        Execute Language Effect Assessment experiment.

        Workflow:
        1. Load Italian-language dataset with ground-truth trace links
        2. Select 2-3 models for testing
        3. For each model, run traceability tasks on sampled requirements
        4. Evaluate each response against ground truth (precision/recall/F1)
        5. Compute per-model and aggregate statistics
        6. Generate assessment of whether Italian requirements are usable

        Returns:
            Dictionary containing:
                - models_tested: List of models tested
                - per_model_results: Per-model accuracy profiles
                - aggregate_statistics: Overall F1/precision/recall stats
                - per_requirement_scores: Individual requirement scores
                - assessment: Usability assessment with rationale

        Implements REQ-3.6.1.1 through REQ-3.6.1.7
        """
        self.log_info("Starting language effect experiment")

        # Step 1: Load dataset (REQ-3.6.1.1)
        dataset = self._load_dataset()
        self.log_info(
            f"Loaded dataset: {dataset.name} "
            f"(language={dataset.language}, "
            f"{len(dataset.requirements)} requirements, "
            f"{len(dataset.traceability_links)} trace links)"
        )

        # Step 2: Select models (REQ-3.6.1.2)
        models = self._select_models()
        self.log_info(f"Testing {len(models)} models")

        # Step 3-4: Run tasks and evaluate against ground truth
        sample_size = self.exp_config.get('sample_size', 10)
        requirements = self._select_requirements(dataset, sample_size)
        self.log_info(f"Sampled {len(requirements)} requirements with trace links")

        per_model_results = []
        all_f1_scores = []  # Flat list across all models for aggregate stats

        for model_config in models:
            model_name = model_config['name']
            self.log_info(f"Testing model: {model_name}")

            model_result = self._test_model(model_config, dataset, requirements)
            per_model_results.append(model_result)
            all_f1_scores.extend(model_result['per_requirement_f1'])

            self.log_info(
                f"  {model_name}: F1={model_result['mean_f1']:.3f}, "
                f"precision={model_result['mean_precision']:.3f}, "
                f"recall={model_result['mean_recall']:.3f}"
            )

        # Step 5: Compute aggregate statistics (REQ-3.6.1.4)
        aggregate_stats = self._compute_aggregate_statistics(
            per_model_results, all_f1_scores
        )

        # Step 6: Generate assessment (REQ-3.6.1.7)
        threshold = self.exp_config.get('acceptability_threshold', 0.50)
        assessment = self._generate_assessment(
            per_model_results, aggregate_stats, threshold
        )

        self.log_info(f"Assessment: {assessment['decision']}")

        # Compile results
        results = {
            'experiment_id': self.experiment_id,
            'dataset': dataset.name,
            'dataset_language': dataset.language,
            'models_tested': [m['name'] for m in models],
            'sample_size': len(requirements),
            'requirements_tested': [r.req_id for r in requirements],
            'per_model_results': per_model_results,
            'aggregate_statistics': aggregate_stats,
            'assessment': assessment
        }

        self.log_info("Language effect experiment completed")
        return results

    def _load_dataset(self):
        """
        Load the Italian-language dataset.

        Returns:
            Dataset object

        Raises:
            ExperimentError: If dataset has no trace links
        """
        dataset_name = self.exp_config['dataset']
        base_path = self.config.get('datasets.base_path', './datasets')
        dataset = load_dataset(dataset_name, {'base_path': base_path})

        if not dataset.traceability_links:
            raise ExperimentError(
                f"Dataset '{dataset_name}' has no traceability links. "
                f"PE01 requires ground-truth links for evaluation."
            )

        if dataset.language.lower() != 'italian':
            self.log_warning(
                f"Dataset '{dataset_name}' is in {dataset.language}, not Italian. "
                f"PE01 is designed for Italian datasets (Albergate, SMOS)."
            )

        return dataset

    def _select_models(self) -> List[Dict[str, Any]]:
        """
        Select models for testing.

        Implements REQ-3.6.1.2: Test with 2-3 models.

        Returns:
            List of model configurations
        """
        model_refs = self.exp_config.get('models', [])

        resolved_models = []
        for model_ref in model_refs[:3]:  # Limit to 3 as per requirements
            if isinstance(model_ref, dict):
                resolved_models.append(model_ref)
            elif isinstance(model_ref, str):
                # Look up by name in top-level models section
                model_config = self.config.get(f'models.{model_ref}', None)
                if model_config and isinstance(model_config, dict):
                    model_config = dict(model_config)
                    model_config['name'] = model_ref
                    resolved_models.append(model_config)
                    continue

                # Try model_selection.candidate_models
                candidates = self.config.get(
                    'experiments.model_selection.candidate_models', []
                )
                for candidate in candidates:
                    if candidate.get('name', '').lower() == model_ref.lower():
                        resolved_models.append(candidate)
                        break
                else:
                    self.log_warning(
                        f"Could not resolve model reference: {model_ref}"
                    )

        if len(resolved_models) < 2:
            raise ExperimentError(
                "PE01 requires at least 2 models for testing. "
                f"Only {len(resolved_models)} could be resolved."
            )

        return resolved_models

    def _select_requirements(self, dataset, sample_size: int) -> list:
        """
        Select requirements that have ground-truth trace links.

        Only requirements with at least one trace link are useful for
        evaluation, so we filter for those first, then take up to
        sample_size.

        Args:
            dataset: Dataset object
            sample_size: Maximum number of requirements to sample

        Returns:
            List of Requirement objects with trace links
        """
        requirements_with_links = []
        for req_id, req in dataset.requirements.items():
            links = dataset.get_links_for_requirement(req_id)
            if links:
                requirements_with_links.append(req)

        if not requirements_with_links:
            raise ExperimentError(
                "No requirements with trace links found in dataset. "
                "Cannot evaluate without ground truth."
            )

        selected = requirements_with_links[:sample_size]

        if len(selected) < sample_size:
            self.log_warning(
                f"Only {len(selected)} requirements have trace links "
                f"(requested {sample_size})"
            )

        return selected

    def _test_model(
        self,
        model_config: Dict[str, Any],
        dataset,
        requirements: list
    ) -> Dict[str, Any]:
        """
        Test a single model on all sampled requirements.

        Args:
            model_config: Model configuration
            dataset: Dataset object
            requirements: List of Requirement objects to test

        Returns:
            Dictionary with per-requirement and aggregate scores
        """
        provider = get_provider(model_config['provider'], model_config)

        per_req_scores = []

        for req in requirements:
            # Get ground-truth linked files
            links = dataset.get_links_for_requirement(req.req_id)
            ground_truth_files = set()
            for link in links:
                ground_truth_files.update(link.target_files)

            # Build prompt
            prompt = self._build_prompt(req, dataset)

            # Get model response
            response = provider.generate(
                prompt=prompt,
                temperature=model_config.get('temperature', 0.7),
                max_tokens=model_config.get('max_tokens', 500)
            )

            # Extract predicted files from response
            predicted_files = self._extract_file_predictions(
                response.text, dataset
            )

            # Compute precision, recall, F1 against ground truth
            scores = self._compute_scores(predicted_files, ground_truth_files)
            scores['requirement_id'] = req.req_id
            scores['ground_truth_files'] = sorted(ground_truth_files)
            scores['predicted_files'] = sorted(predicted_files)

            per_req_scores.append(scores)

        # Aggregate across requirements for this model
        f1_scores = [s['f1'] for s in per_req_scores]
        precision_scores = [s['precision'] for s in per_req_scores]
        recall_scores = [s['recall'] for s in per_req_scores]

        return {
            'model': model_config['name'],
            'per_requirement_scores': per_req_scores,
            'per_requirement_f1': f1_scores,
            'mean_f1': sum(f1_scores) / len(f1_scores) if f1_scores else 0.0,
            'mean_precision': (
                sum(precision_scores) / len(precision_scores)
                if precision_scores else 0.0
            ),
            'mean_recall': (
                sum(recall_scores) / len(recall_scores)
                if recall_scores else 0.0
            ),
            'statistics': descriptive_statistics(f1_scores) if f1_scores else {}
        }

    def _build_prompt(self, requirement, dataset) -> str:
        """
        Build the traceability task prompt for a requirement.

        Provides the requirement text and code snippets from ALL source
        files in the dataset (not just linked ones), so the model must
        identify which files are linked.

        Args:
            requirement: Requirement object
            dataset: Dataset object

        Returns:
            Formatted prompt string
        """
        # Include code snippets from all source files (up to a limit)
        # so the model has to identify the correct ones
        code_snippets = []
        for file_name, source_file in list(dataset.source_files.items())[:20]:
            snippet = source_file.content[:300]
            code_snippets.append(f"// {file_name}\n{snippet}")

        code_context = '\n\n'.join(code_snippets) if code_snippets else (
            '[No source files available]'
        )

        return (
            f"Identify which source code files are linked to the following "
            f"requirement. List only the file names, one per line.\n\n"
            f"Requirement:\n{requirement.content}\n\n"
            f"Available source files:\n{code_context}\n\n"
            f"Linked files:"
        )

    def _extract_file_predictions(
        self,
        response_text: str,
        dataset
    ) -> Set[str]:
        """
        Extract predicted file names from the model's response.

        Looks for file names that match files known to exist in the
        dataset, plus common file-name patterns.

        Args:
            response_text: Raw model response text
            dataset: Dataset object (for known file names)

        Returns:
            Set of predicted file names
        """
        predicted = set()
        known_files = set(dataset.source_files.keys())

        # Strategy 1: Check for exact matches of known file names
        for file_name in known_files:
            if file_name in response_text:
                predicted.add(file_name)

        # Strategy 2: Regex for file-like patterns (e.g., Foo.java, bar.c)
        file_pattern = re.compile(
            r'\b([\w]+\.(?:java|c|h|py|js|cs|cpp|txt))\b',
            re.IGNORECASE
        )
        for match in file_pattern.finditer(response_text):
            candidate = match.group(1)
            # Only count files that exist in the dataset
            if candidate in known_files:
                predicted.add(candidate)

        return predicted

    def _compute_scores(
        self,
        predicted: Set[str],
        ground_truth: Set[str]
    ) -> Dict[str, float]:
        """
        Compute precision, recall, and F1 for a single requirement.

        Args:
            predicted: Set of predicted file names
            ground_truth: Set of ground-truth file names

        Returns:
            Dictionary with precision, recall, f1
        """
        if not ground_truth:
            # No ground truth -- can't evaluate
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

        if not predicted:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

        true_positives = len(predicted & ground_truth)
        precision = true_positives / len(predicted)
        recall = true_positives / len(ground_truth)

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def _compute_aggregate_statistics(
        self,
        per_model_results: List[Dict[str, Any]],
        all_f1_scores: List[float]
    ) -> Dict[str, Any]:
        """
        Compute aggregate statistics across all models and requirements.

        Args:
            per_model_results: List of per-model result dicts
            all_f1_scores: Flat list of all F1 scores

        Returns:
            Aggregate statistics dictionary
        """
        all_precision = []
        all_recall = []
        for model_result in per_model_results:
            for req_score in model_result['per_requirement_scores']:
                all_precision.append(req_score['precision'])
                all_recall.append(req_score['recall'])

        stats = {
            'n_observations': len(all_f1_scores),
            'n_models': len(per_model_results),
            'f1': descriptive_statistics(all_f1_scores) if all_f1_scores else {},
            'precision': (
                descriptive_statistics(all_precision) if all_precision else {}
            ),
            'recall': (
                descriptive_statistics(all_recall) if all_recall else {}
            ),
        }

        # Add 95% CI for mean F1 if we have enough data points
        if len(all_f1_scores) >= 2:
            stats['f1_confidence_interval'] = confidence_interval(
                all_f1_scores, confidence=0.95
            )

        return stats

    def _generate_assessment(
        self,
        per_model_results: List[Dict[str, Any]],
        aggregate_stats: Dict[str, Any],
        threshold: float
    ) -> Dict[str, Any]:
        """
        Generate usability assessment for Italian requirements.

        Args:
            per_model_results: Per-model results
            aggregate_stats: Aggregate statistics
            threshold: Minimum acceptable mean F1

        Returns:
            Assessment dictionary with decision and rationale
        """
        mean_f1 = aggregate_stats['f1'].get('mean', 0.0)
        f1_ci = aggregate_stats.get('f1_confidence_interval', {})
        ci_lower = f1_ci.get('lower_bound', None)

        # Per-model summary for the rationale
        model_summaries = []
        for mr in per_model_results:
            model_summaries.append(
                f"{mr['model']}: F1={mr['mean_f1']:.3f}"
            )
        model_summary_str = '; '.join(model_summaries)

        if mean_f1 >= threshold:
            decision = "Italian requirements are usable as-is"
            rationale = (
                f"Mean F1 across all models and requirements is {mean_f1:.3f}, "
                f"which meets the acceptability threshold of {threshold:.2f}. "
            )
            if ci_lower is not None:
                rationale += (
                    f"95% CI for mean F1: "
                    f"[{ci_lower:.3f}, {f1_ci.get('upper_bound', 0):.3f}]. "
                )
            rationale += (
                f"Per-model results: {model_summary_str}. "
                f"Models demonstrate adequate performance on Italian-language "
                f"requirements without translation."
            )
        else:
            decision = (
                "Italian requirements may need translation or separate analysis"
            )
            rationale = (
                f"Mean F1 across all models and requirements is {mean_f1:.3f}, "
                f"which is below the acceptability threshold of {threshold:.2f}. "
            )
            if ci_lower is not None:
                rationale += (
                    f"95% CI for mean F1: "
                    f"[{ci_lower:.3f}, {f1_ci.get('upper_bound', 0):.3f}]. "
                )
            rationale += (
                f"Per-model results: {model_summary_str}. "
                f"Consider translating Italian requirements to English or "
                f"analyzing Italian datasets separately from English ones."
            )

        return {
            'decision': decision,
            'rationale': rationale,
            'mean_f1': mean_f1,
            'threshold': threshold,
            'ci_lower': ci_lower,
            'per_model_f1': {
                mr['model']: mr['mean_f1'] for mr in per_model_results
            }
        }
