"""
PE06: Stop Sequence Definition

Implements REQ-3.6.6 (Stop Sequence Definition).
"""

from typing import Dict, Any, List, Tuple
import re

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..llm.factory import get_provider
from ..datasets import load_dataset


class StopSequenceExperiment(BaseExperiment):
    """
    Stop Sequence Definition experiment.

    Implements REQ-3.6.6.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE06"):
        super().__init__(config, experiment_id)
        self.exp_config = config.get('experiments.stop_sequence', {})
        self.log_info("Stop Sequence experiment initialized")

    def get_description(self) -> str:
        return "Design and validate stop sequences for each TaskType"

    def run(self) -> Dict[str, Any]:
        """
        Execute Stop Sequence Definition experiment.

        Returns:
            Dictionary containing validated stop sequences per TaskType
        """
        self.log_info("Starting stop sequence experiment")

        # Load configuration
        task_types = self.exp_config.get('task_types',
            ['new_feature', 'bug_fix', 'test_generation', 'documentation'])
        sample_size = self.exp_config.get('sample_size', 20)
        candidate_sequences = self.exp_config.get('candidate_sequences', {})
        fp_threshold = self.exp_config.get('false_positive_threshold', 0.05)

        # Get provider
        model_config = self.config.get('experiments.stop_sequence.model',
            self.config.get('models.mock', {'provider': 'mock'}))
        provider = get_provider(model_config.get('provider', 'mock'), model_config)

        # Load dataset for sample tasks
        dataset_name = self.exp_config.get('dataset', 'albergate')
        dataset = load_dataset(dataset_name,
            {'base_path': self.config.get('datasets.base_path', './datasets')})

        results = {'task_types': {}, 'recommendations': {}}

        for task_type in task_types:
            self.log_info(f"Testing stop sequences for TaskType: {task_type}")

            # Get candidate sequences for this task type
            sequences = candidate_sequences.get(task_type, ['```\n\n', 'END_OF_CODE'])

            # Generate ground truth outputs (without stop sequences)
            ground_truth = self._generate_ground_truth_outputs(
                provider, dataset, task_type, sample_size
            )

            # Test each candidate sequence
            sequence_results = {}
            for seq in sequences:
                metrics = self._evaluate_sequence(ground_truth, seq)
                sequence_results[seq] = metrics

                self.log_info(
                    f"  Sequence '{repr(seq)}': "
                    f"FPR={metrics['fpr']:.3f}, Precision={metrics['precision']:.3f}"
                )

            # Select best sequence (highest score, below FP threshold)
            best_seq, best_metrics = self._select_best_sequence(
                sequence_results, fp_threshold
            )

            results['task_types'][task_type] = sequence_results
            results['recommendations'][task_type] = {
                'selected_sequence': best_seq,
                'metrics': best_metrics,
                'all_candidates_tested': len(sequences)
            }

        self.log_info("Stop sequence experiment completed")
        return results

    def _generate_ground_truth_outputs(
        self,
        provider,
        dataset,
        task_type: str,
        sample_size: int
    ) -> List[Dict[str, Any]]:
        """
        Generate sample outputs without stop sequences.

        Each output is annotated with natural completion boundaries.
        """
        outputs = []

        # Get sample requirements
        requirements = list(dataset.requirements.values())[:sample_size]

        for req in requirements:
            # Create task prompt based on task type
            prompt = self._create_task_prompt(req, task_type)

            # Generate output without stop sequence
            response = provider.generate(prompt=prompt, max_tokens=500)

            # Detect natural completion boundary
            boundary_info = self._detect_completion_boundary(response.text, task_type)

            outputs.append({
                'requirement_id': req.req_id,
                'prompt': prompt,
                'full_output': response.text,
                'natural_boundary_index': boundary_info['index'],
                'has_natural_boundary': boundary_info['found'],
                'boundary_pattern': boundary_info['pattern']
            })

        return outputs

    def _create_task_prompt(self, requirement, task_type: str) -> str:
        """Create task prompt for the given task type."""
        prompts = {
            'new_feature': f"Implement the following requirement:\n{requirement.content}\n\nProvide the code:",
            'bug_fix': f"Fix the bug described in this requirement:\n{requirement.content}\n\nProvide the fix:",
            'test_generation': f"Write tests for this requirement:\n{requirement.content}\n\nProvide the tests:",
            'documentation': f"Document the following requirement:\n{requirement.content}\n\nProvide documentation:"
        }
        return prompts.get(task_type, prompts['new_feature'])

    def _detect_completion_boundary(self, text: str, task_type: str) -> Dict[str, Any]:
        """
        Detect natural completion boundary in output text.

        Natural boundaries are:
        - End of code block (```)
        - Empty line after last statement
        - Common ending patterns
        """
        # Patterns indicating natural completion
        patterns = {
            'code_block_end': r'```\s*\n\s*\n',
            'function_end': r'^\s*}\s*\n\s*\n',
            'class_end': r'^\s*}\s*$',
            'comment_end': r'#\s*(end|done|complete)',
            'docstring_end': r'"""\s*\n\s*\n',
        }

        best_match = {'found': False, 'index': len(text), 'pattern': None}

        for name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match and match.end() < best_match['index']:
                best_match = {
                    'found': True,
                    'index': match.end(),
                    'pattern': name
                }

        return best_match

    def _evaluate_sequence(
        self,
        ground_truth: List[Dict],
        stop_sequence: str
    ) -> Dict[str, float]:
        """
        Evaluate a stop sequence against ground truth outputs.

        Returns metrics: TP, FP, TN, FN, FPR, FNR, precision, recall, score
        """
        tp = fp = tn = fn = 0
        token_savings = []

        for output in ground_truth:
            text = output['full_output']
            boundary_idx = output['natural_boundary_index']
            has_boundary = output['has_natural_boundary']

            # Find where this stop sequence would truncate
            trunc_idx = text.find(stop_sequence)

            if trunc_idx == -1:
                # Sequence not found in output
                if has_boundary:
                    # Should have truncated but didn't
                    fn += 1
                else:
                    # Correctly didn't truncate
                    tn += 1
            else:
                # Sequence found
                if has_boundary and abs(trunc_idx - boundary_idx) <= 50:
                    # Truncated near natural boundary - True Positive
                    tp += 1
                    token_savings.append(len(text) - trunc_idx)
                elif trunc_idx < boundary_idx - 50:
                    # Truncated too early - False Positive
                    fp += 1
                else:
                    # Truncated but no natural boundary expected
                    # Consider as TP if output looks complete
                    tp += 1
                    token_savings.append(len(text) - trunc_idx)

        total = tp + fp + tn + fn

        # Calculate rates
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # Score: penalize false positives heavily
        score = (precision * recall) - (2 * fpr) if precision > 0 else -fpr

        return {
            'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
            'fpr': fpr, 'fnr': fnr,
            'precision': precision, 'recall': recall,
            'score': score,
            'avg_token_savings': sum(token_savings) / len(token_savings) if token_savings else 0
        }

    def _select_best_sequence(
        self,
        sequence_results: Dict[str, Dict],
        fp_threshold: float
    ) -> Tuple[str, Dict]:
        """Select best sequence: highest score below FP threshold."""

        valid_sequences = [
            (seq, metrics) for seq, metrics in sequence_results.items()
            if metrics['fpr'] <= fp_threshold
        ]

        if not valid_sequences:
            # No sequence meets threshold, pick one with lowest FPR
            best = min(sequence_results.items(), key=lambda x: x[1]['fpr'])
            return best

        # Pick highest score among valid
        best = max(valid_sequences, key=lambda x: x[1]['score'])
        return best
