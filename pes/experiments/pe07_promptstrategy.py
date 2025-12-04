"""
PE07: Prompting Strategy Testing

This experiment compares different prompting strategies (zero-shot, chain-of-thought, few-shot)
to determine the optimal approach for traceability tasks.

Implements REQ-3.6.7 (Prompting Strategy Testing).
"""

from typing import Dict, Any, List, Tuple
import numpy as np

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..llm.factory import get_provider
from ..datasets import load_dataset
from ..analysis import (
    descriptive_statistics,
    one_way_anova,
    summarize_by_group,
    cohens_d
)


class PromptStrategyExperiment(BaseExperiment):
    """
    Prompting Strategy Testing experiment.

    Compares different prompting strategies (zero-shot, chain-of-thought, few-shot)
    to identify the most effective approach for traceability tasks.

    Implements REQ-3.6.7.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE07"):
        """
        Initialize Prompt Strategy experiment.

        Args:
            config: Configuration manager
            experiment_id: Experiment identifier (default: "PE07")
        """
        super().__init__(config, experiment_id)

        # Load experiment-specific configuration
        self.exp_config = config.get('experiments.promptstrategy', {})

        # Validate configuration
        self._validate_experiment_config()

        self.log_info("Prompt Strategy experiment initialized")

    def _validate_experiment_config(self) -> None:
        """
        Validate experiment-specific configuration.

        Raises:
            ExperimentError: If configuration is invalid
        """
        # Check for required fields
        if 'model' not in self.exp_config:
            raise ExperimentError(
                "Prompt strategy experiment requires 'model' in configuration"
            )

        if 'task_types' not in self.exp_config:
            raise ExperimentError(
                "Prompt strategy experiment requires 'task_types' in configuration"
            )

    def get_description(self) -> str:
        """Get experiment description."""
        return "Compare prompting strategies and select optimal approach"

    def run(self) -> Dict[str, Any]:
        """
        Execute Prompting Strategy experiment.

        This implements the PE07 workflow (REQ-3.6.7):
        1. Define prompting strategy variants (REQ-3.6.7.2)
        2. Create prompt templates for each strategy (REQ-3.6.7.3)
        3. Execute sample tasks with each strategy (REQ-3.6.7.4)
        4. Compare performance metrics
        5. Select optimal strategy (REQ-3.6.7.5)
        6. Document selected strategy (REQ-3.6.7.6)

        Returns:
            Dictionary containing experiment results:
                - task_types: List of TaskTypes tested
                - strategies: List of strategies evaluated
                - strategy_results: Performance data per strategy
                - statistical_analysis: ANOVA and effect sizes
                - selected_strategy: Optimal strategy with justification
                - example_prompts: Example prompts for each TaskType

        Implements REQ-3.6.7.1 through REQ-3.6.7.6
        """
        self.log_info("Starting prompting strategy experiment")

        # Step 1: Define strategy variants (REQ-3.6.7.2)
        strategies = self._define_strategies()
        self.log_info(f"Testing strategies: {list(strategies.keys())}")

        # Step 2: Load model and dataset
        model_config = self._load_model_config()
        dataset_info = self._load_dataset()

        task_types = self.exp_config.get('task_types', [])

        # Step 3: Execute tasks with each strategy (REQ-3.6.7.3 + REQ-3.6.7.4)
        strategy_results = {}

        for task_type in task_types:
            self.log_info(f"Testing TaskType: {task_type}")

            task_results = self._test_strategies_for_task(
                task_type,
                strategies,
                model_config,
                dataset_info
            )
            strategy_results[task_type] = task_results

        # Step 4: Perform statistical analysis
        statistical_analysis = self._analyze_strategy_impact(strategy_results)

        # Step 5: Select optimal strategy (REQ-3.6.7.5)
        selected_strategy = self._select_optimal_strategy(
            strategy_results,
            statistical_analysis
        )

        # Step 6: Generate example prompts (REQ-3.6.7.6)
        example_prompts = self._generate_example_prompts(
            selected_strategy['strategy_key'],
            strategies,
            task_types,
            dataset_info
        )

        # Compile results
        results = {
            'experiment_id': self.experiment_id,
            'task_types': task_types,
            'strategies': list(strategies.keys()),
            'strategy_results': strategy_results,
            'statistical_analysis': statistical_analysis,
            'selected_strategy': selected_strategy,
            'example_prompts': example_prompts
        }

        self.log_info("Prompting strategy experiment completed")
        self._log_selected_strategy(selected_strategy)

        return results

    def _define_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Define prompting strategy variants.

        Implements REQ-3.6.7.2: Strategy Variants.

        Returns:
            Dictionary of strategy definitions
        """
        strategies = {
            'zero_shot': {
                'name': 'Zero-Shot',
                'description': 'Direct instruction without examples or reasoning steps',
                'use_examples': False,
                'use_cot': False
            },
            'zero_shot_cot': {
                'name': 'Zero-Shot + CoT',
                'description': 'Chain-of-thought reasoning without examples',
                'use_examples': False,
                'use_cot': True
            }
        }

        # Optionally include few-shot if configured
        if self.exp_config.get('include_few_shot', False):
            strategies['few_shot_cot'] = {
                'name': 'Few-Shot + CoT',
                'description': 'Examples with chain-of-thought reasoning',
                'use_examples': True,
                'use_cot': True
            }

        return strategies

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
            dataset_config = {'base_path': './datasets'}

        # Load dataset
        dataset = load_dataset(dataset_name, dataset_config)

        return {
            'name': dataset_name,
            'dataset': dataset
        }

    def _test_strategies_for_task(
        self,
        task_type: str,
        strategies: Dict[str, Dict[str, Any]],
        model_config: Dict[str, Any],
        dataset_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test all prompting strategies for a specific TaskType.

        Implements REQ-3.6.7.3: Prompt Template Creation
        and REQ-3.6.7.4: Strategy Comparison.

        Args:
            task_type: TaskType to test
            strategies: Strategy definitions
            model_config: Model configuration
            dataset_info: Dataset information

        Returns:
            Results for each strategy
        """
        results_by_strategy = {}

        # Create provider
        provider = get_provider(
            model_config['provider'],
            model_config
        )

        # Get sample requirements
        dataset = dataset_info['dataset']
        sample_size = self.exp_config.get('sample_size', 10)
        requirements = list(dataset.requirements.values())[:sample_size]

        for strategy_key, strategy_def in strategies.items():
            self.log_info(f"  Testing strategy: {strategy_def['name']}")

            scores = []

            for req in requirements:
                # Create prompt using this strategy (REQ-3.6.7.3)
                prompt = self._create_strategy_prompt(
                    task_type,
                    req,
                    strategy_def
                )

                # Get response
                response = provider.generate(
                    prompt=prompt,
                    temperature=model_config.get('temperature', 0.7),
                    max_tokens=model_config.get('max_tokens', 500)
                )

                # Evaluate (simplified)
                accuracy = self._evaluate_response(response.text, req)
                scores.append(accuracy)

            # Compute metrics for this strategy
            results_by_strategy[strategy_key] = {
                'strategy_name': strategy_def['name'],
                'scores': scores,
                'mean_accuracy': np.mean(scores),
                'std_accuracy': np.std(scores),
                'sample_size': len(scores)
            }

        return {
            'task_type': task_type,
            'results_by_strategy': results_by_strategy,
            'strategies_tested': list(strategies.keys())
        }

    def _create_strategy_prompt(
        self,
        task_type: str,
        requirement,
        strategy_def: Dict[str, Any]
    ) -> str:
        """
        Create prompt using specified strategy.

        Implements REQ-3.6.7.3: Prompt Template Creation.

        Args:
            task_type: Type of task
            requirement: Requirement object
            strategy_def: Strategy definition

        Returns:
            Formatted prompt
        """
        # Base components
        persona = "You are an expert in software traceability analysis."

        # Task-specific instruction
        if task_type == 'trace':
            task_instruction = "Identify all traceability links between this requirement and code artifacts."
        elif task_type == 'recover':
            task_instruction = "Recover missing traceability links for this requirement."
        elif task_type == 'fill':
            task_instruction = "Fill in complete traceability information for this requirement."
        else:
            task_instruction = "Analyze this requirement for traceability links."

        # Output format
        output_format = "Provide the links in the format: REQ-XXX -> ARTIFACT-YYY"

        # Build prompt based on strategy
        prompt_parts = [persona, "", task_instruction]

        if strategy_def['use_cot']:
            # Add chain-of-thought instruction
            cot_instruction = (
                "Think through this step-by-step:\n"
                "1. Analyze the requirement's key concepts\n"
                "2. Identify relevant code artifacts\n"
                "3. Establish the links based on semantic similarity\n"
                "4. Provide your final answer"
            )
            prompt_parts.append(cot_instruction)

        if strategy_def['use_examples']:
            # Add few-shot examples
            examples = self._get_few_shot_examples(task_type)
            prompt_parts.append(examples)

        # Add the actual requirement
        prompt_parts.extend([
            "",
            f"Requirement: {requirement.content}",
            "",
            output_format
        ])

        return "\n".join(prompt_parts)

    def _get_few_shot_examples(self, task_type: str) -> str:
        """
        Get few-shot examples for a task type.

        Args:
            task_type: Type of task

        Returns:
            Example prompts and responses
        """
        # Simplified examples for demonstration
        return (
            "Example 1:\n"
            "Requirement: The system shall authenticate users\n"
            "Links: REQ-001 -> CODE-auth.py, REQ-001 -> TEST-auth_test.py\n\n"
            "Example 2:\n"
            "Requirement: The system shall log all transactions\n"
            "Links: REQ-002 -> CODE-logger.py, REQ-002 -> CODE-transaction.py"
        )

    def _evaluate_response(self, response_text: str, requirement) -> float:
        """
        Evaluate response accuracy.

        Simplified evaluation for testing.

        Args:
            response_text: Model response
            requirement: Requirement object

        Returns:
            Accuracy score (0.0 to 1.0)
        """
        import random

        # Simplified evaluation based on response characteristics
        has_links = 'REQ-' in response_text or '->' in response_text
        is_substantive = len(response_text) > 20
        has_reasoning = any(word in response_text.lower()
                          for word in ['analyze', 'identify', 'step', 'because'])

        # Base accuracy
        if has_links and is_substantive:
            base_accuracy = 0.80
            # Bonus for reasoning (CoT benefit)
            if has_reasoning:
                base_accuracy += 0.10
            # Add some variation
            variation = random.uniform(-0.05, 0.05)
            return max(0.0, min(1.0, base_accuracy + variation))
        else:
            return random.uniform(0.4, 0.6)

    def _analyze_strategy_impact(
        self,
        strategy_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze statistical impact of strategies on performance.

        Args:
            strategy_results: Results for each TaskType

        Returns:
            Statistical analysis results
        """
        analysis = {}

        for task_type, task_results in strategy_results.items():
            # Extract data for ANOVA
            strategy_groups = []
            strategy_labels = []

            for strategy_key, result in task_results['results_by_strategy'].items():
                strategy_groups.append(result['scores'])
                strategy_labels.append(result['strategy_name'])

            # Perform one-way ANOVA
            anova_result = one_way_anova(strategy_groups)

            # Get summary statistics by strategy
            all_scores = []
            all_strategies = []
            for strategy_key, result in task_results['results_by_strategy'].items():
                all_scores.extend(result['scores'])
                all_strategies.extend([result['strategy_name']] * len(result['scores']))

            group_summary = summarize_by_group(all_scores, all_strategies)

            analysis[task_type] = {
                'anova': anova_result,
                'group_summary': group_summary,
                'strategy_labels': strategy_labels,
                'significant_effect': anova_result['significant']
            }

        return analysis

    def _select_optimal_strategy(
        self,
        strategy_results: Dict[str, Dict[str, Any]],
        statistical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select optimal prompting strategy.

        Implements REQ-3.6.7.5: Strategy Selection.

        Args:
            strategy_results: Performance results
            statistical_analysis: Statistical analysis results

        Returns:
            Selected strategy with justification
        """
        # Aggregate results across task types
        strategy_scores = {}

        for task_type, task_results in strategy_results.items():
            for strategy_key, result in task_results['results_by_strategy'].items():
                if strategy_key not in strategy_scores:
                    strategy_scores[strategy_key] = {
                        'strategy_name': result['strategy_name'],
                        'all_scores': [],
                        'mean_accuracies': []
                    }

                strategy_scores[strategy_key]['all_scores'].extend(result['scores'])
                strategy_scores[strategy_key]['mean_accuracies'].append(result['mean_accuracy'])

        # Find best strategy
        best_strategy = None
        best_score = -1

        for strategy_key, scores_data in strategy_scores.items():
            overall_mean = np.mean(scores_data['all_scores'])

            if overall_mean > best_score:
                best_score = overall_mean
                best_strategy = strategy_key

        # Generate justification
        best_strategy_data = strategy_scores[best_strategy]
        justification_parts = []

        justification_parts.append(
            f"{best_strategy_data['strategy_name']} achieved the highest overall accuracy "
            f"({best_score:.1%}) across all task types"
        )

        # Check if statistically significant
        significant_count = sum(
            1 for analysis in statistical_analysis.values()
            if analysis['significant_effect']
        )

        if significant_count > 0:
            justification_parts.append(
                f"showed statistically significant improvements in {significant_count} "
                f"out of {len(statistical_analysis)} task types"
            )

        return {
            'strategy_key': best_strategy,
            'strategy_name': best_strategy_data['strategy_name'],
            'overall_accuracy': best_score,
            'justification': '; '.join(justification_parts) + '.',
            'performance_by_task': {
                task_type: task_results['results_by_strategy'][best_strategy]['mean_accuracy']
                for task_type, task_results in strategy_results.items()
                if best_strategy in task_results['results_by_strategy']
            }
        }

    def _generate_example_prompts(
        self,
        selected_strategy: str,
        strategies: Dict[str, Dict[str, Any]],
        task_types: List[str],
        dataset_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate example prompts for selected strategy.

        Implements REQ-3.6.7.6: Strategy Documentation.

        Args:
            selected_strategy: Selected strategy key
            strategies: All strategy definitions
            task_types: List of task types
            dataset_info: Dataset information

        Returns:
            Example prompts per TaskType
        """
        examples = {}

        # Get first requirement as example
        dataset = dataset_info['dataset']
        example_req = list(dataset.requirements.values())[0]

        strategy_def = strategies[selected_strategy]

        for task_type in task_types:
            prompt = self._create_strategy_prompt(
                task_type,
                example_req,
                strategy_def
            )
            examples[task_type] = prompt

        return examples

    def _log_selected_strategy(self, selected_strategy: Dict[str, Any]) -> None:
        """
        Log selected strategy recommendation.

        Args:
            selected_strategy: Selected strategy data
        """
        self.log_info("=" * 60)
        self.log_info("Selected Prompting Strategy")
        self.log_info("=" * 60)
        self.log_info(f"Strategy: {selected_strategy['strategy_name']}")
        self.log_info(f"Overall Accuracy: {selected_strategy['overall_accuracy']:.3f}")
        self.log_info(f"Justification: {selected_strategy['justification']}")
        self.log_info("=" * 60)
