"""
PE02: Model Selection - Prompt-Based

This experiment implements preliminary experiment 2 (PE02) from the research plan,
which selects optimal prompt-based models from a candidate set.

Implements REQ-3.6.2 (Model Selection - Prompt-Based).
"""

from typing import Dict, Any, List
import time

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..llm.factory import get_provider
from ..llm.base import BaseLLMProvider


class ModelSelectionExperiment(BaseExperiment):
    """
    Model Selection experiment for prompt-based models.
    
    This experiment tests multiple candidate models on a benchmark task,
    ranks them by performance, and selects the top models for main experiments.
    
    Implements REQ-3.6.2.* requirements.
    """
    
    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE02"):
        """
        Initialize model selection experiment.
        
        Args:
            config: Configuration manager
            experiment_id: Experiment identifier (default: "PE02")
        """
        super().__init__(config, experiment_id)
        
        # Load experiment configuration
        self.exp_config = config.get('experiments.model_selection', {})
        
        # Validate configuration
        self._validate_experiment_config()
    
    def _validate_experiment_config(self) -> None:
        """
        Validate experiment-specific configuration.
        
        Raises:
            ExperimentError: If configuration is invalid
        """
        # Check for required fields
        if 'candidate_models' not in self.exp_config:
            raise ExperimentError(
                "Model selection experiment requires 'candidate_models' in configuration"
            )
        
        if 'benchmark_task' not in self.exp_config:
            raise ExperimentError(
                "Model selection experiment requires 'benchmark_task' in configuration"
            )
    
    def get_description(self) -> str:
        """Get experiment description."""
        return (
            "Model Selection - Prompt-Based: Tests multiple candidate models on a "
            "benchmark task, ranks them by performance, and selects top models."
        )
    
    def run(self) -> Dict[str, Any]:
        """
        Execute model selection experiment.
        
        This implements the core logic of PE02:
        1. Load candidate models
        2. Execute benchmark task on each model
        3. Evaluate and rank models
        4. Select top models
        5. Generate selection report
        
        Returns:
            Dictionary containing experiment results:
                - candidates_tested: Number of models tested
                - rankings: Ranked list of models with scores
                - selected_models: Top selected models
                - benchmark_task: Task definition
                - detailed_results: Per-model results
        
        Implements REQ-3.6.2.1 through REQ-3.6.2.7
        """
        self.log_info("Starting model selection experiment")
        
        # Step 1: Load candidate models (REQ-3.6.2.2)
        candidate_models = self._load_candidate_models()
        self.log_info(f"Loaded {len(candidate_models)} candidate models")
        
        # Step 2: Load benchmark task (REQ-3.6.2.3)
        benchmark_task = self._load_benchmark_task()
        self.log_info(f"Benchmark task: {benchmark_task['description']}")
        
        # Step 3: Test each model on benchmark (REQ-3.6.2.4)
        model_results = []
        for i, model_config in enumerate(candidate_models, 1):
            self.log_info(
                f"Testing model {i}/{len(candidate_models)}: {model_config['name']}"
            )
            
            result = self._test_model(model_config, benchmark_task)
            model_results.append(result)
        
        # Step 4: Rank models (REQ-3.6.2.5)
        rankings = self._rank_models(model_results)
        self.log_info("Model ranking complete")
        
        # Step 5: Select top models (REQ-3.6.2.6)
        selected_models = self._select_top_models(rankings)
        self.log_info(f"Selected {len(selected_models)} top models")
        
        # Step 6: Generate selection documentation (REQ-3.6.2.7)
        selection_report = self._generate_selection_report(
            rankings,
            selected_models,
            benchmark_task
        )
        
        # Compile results
        results = {
            'candidates_tested': len(candidate_models),
            'rankings': rankings,
            'selected_models': selected_models,
            'benchmark_task': benchmark_task,
            'detailed_results': model_results,
            'selection_report': selection_report
        }
        
        self.log_info("Model selection experiment completed")
        return results
    
    def _load_candidate_models(self) -> List[Dict[str, Any]]:
        """
        Load candidate models from configuration.
        
        Implements REQ-3.6.2.2: Test up to 10 candidate models.
        
        Returns:
            List of model configuration dictionaries
        """
        candidates = self.exp_config.get('candidate_models', [])
        
        # Validate model configurations
        validated_models = []
        for model_config in candidates[:10]:  # Limit to 10 as per requirement
            if 'name' not in model_config or 'provider' not in model_config:
                self.log_warning(f"Skipping invalid model config: {model_config}")
                continue
            validated_models.append(model_config)
        
        if not validated_models:
            raise ExperimentError("No valid candidate models found in configuration")
        
        return validated_models
    
    def _load_benchmark_task(self) -> Dict[str, Any]:
        """
        Load benchmark task definition.
        
        Implements REQ-3.6.2.3: Execute simple benchmark task consistently.
        
        Returns:
            Benchmark task dictionary with:
                - description: Task description
                - prompt: Prompt template
                - expected_output: Expected output pattern or criteria
                - evaluation_criteria: How to evaluate responses
        """
        benchmark = self.exp_config.get('benchmark_task', {})
        
        # Set defaults if not specified
        if 'description' not in benchmark:
            benchmark['description'] = "Simple code generation task"
        
        if 'prompt' not in benchmark:
            # Default benchmark: simple Python function generation
            benchmark['prompt'] = (
                "Write a Python function called 'calculate_sum' that takes "
                "a list of numbers and returns their sum. Include a docstring "
                "and handle edge cases."
            )
        
        if 'evaluation_criteria' not in benchmark:
            benchmark['evaluation_criteria'] = {
                'correctness': 'Function exists and handles basic case',
                'documentation': 'Includes docstring',
                'error_handling': 'Handles empty list'
            }
        
        return benchmark
    
    def _test_model(
        self,
        model_config: Dict[str, Any],
        benchmark_task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test a single model on the benchmark task.
        
        Implements REQ-3.6.2.4: Evaluate each model and record metrics.
        
        Args:
            model_config: Model configuration
            benchmark_task: Benchmark task definition
        
        Returns:
            Dictionary with test results:
                - model_name: Model identifier
                - provider: Provider name
                - response: Generated response
                - metrics: Performance metrics (accuracy, speed, quality)
                - error: Error message if failed
        """
        model_name = model_config['name']
        provider_name = model_config['provider']
        
        # Initialize result structure
        result = {
            'model_name': model_name,
            'provider': provider_name,
            'category': model_config.get('category', 'unknown'),
            'status': 'pending'
        }
        
        try:
            # Create provider instance
            provider_config = model_config.copy()
            provider = get_provider(provider_name, provider_config)
            
            # Generate response
            start_time = time.time()
            response = provider.generate(
                prompt=benchmark_task['prompt'],
                temperature=model_config.get('temperature', 0.7),
                max_tokens=model_config.get('max_tokens', 1000)
            )
            duration = time.time() - start_time
            
            # Evaluate response
            metrics = self._evaluate_response(response, benchmark_task)
            metrics['duration_seconds'] = duration
            metrics['cost_estimate'] = self._estimate_cost(response, model_config)
            
            # Update result
            result.update({
                'status': 'completed',
                'response': response.text,
                'metrics': metrics,
                'token_usage': {
                    'prompt_tokens': response.prompt_tokens,
                    'completion_tokens': response.completion_tokens,
                    'total_tokens': response.total_tokens
                }
            })
            
        except Exception as e:
            self.log_error(f"Model {model_name} failed: {str(e)}")
            result.update({
                'status': 'failed',
                'error': str(e)
            })
        
        return result
    
    def _evaluate_response(
        self,
        response: Any,
        benchmark_task: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Evaluate model response against benchmark criteria.
        
        Args:
            response: LLM response object
            benchmark_task: Benchmark task with evaluation criteria
        
        Returns:
            Dictionary of metric scores (0.0 to 1.0)
        """
        metrics = {}
        response_text = response.text.lower()
        
        # Simple heuristic evaluation (TODO: Replace with actual evaluation logic)
        # Check for function definition
        metrics['correctness'] = 1.0 if 'def calculate_sum' in response_text else 0.0
        
        # Check for docstring
        metrics['documentation'] = 1.0 if '"""' in response_text or "'''" in response_text else 0.0
        
        # Check for error handling
        metrics['error_handling'] = 1.0 if ('if' in response_text or 'try' in response_text) else 0.5
        
        # Overall quality score (average of criteria)
        metrics['quality_score'] = sum(metrics.values()) / len(metrics)
        
        return metrics
    
    def _estimate_cost(self, response: Any, model_config: Dict[str, Any]) -> float:
        """
        Estimate cost of the API call.
        
        Args:
            response: LLM response with token usage
            model_config: Model configuration with pricing info
        
        Returns:
            Estimated cost in USD
        """
        # Get pricing from config (default to $0 if not specified)
        cost_per_1k_prompt = model_config.get('cost_per_1k_prompt_tokens', 0.0)
        cost_per_1k_completion = model_config.get('cost_per_1k_completion_tokens', 0.0)
        
        # Calculate cost
        prompt_cost = (response.prompt_tokens / 1000) * cost_per_1k_prompt
        completion_cost = (response.completion_tokens / 1000) * cost_per_1k_completion
        
        return prompt_cost + completion_cost
    
    def _rank_models(self, model_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank models based on composite performance score.
        
        Implements REQ-3.6.2.5: Rank models within categories.
        
        Args:
            model_results: List of model test results
        
        Returns:
            Ranked list of models with scores
        """
        rankings = []
        
        for result in model_results:
            if result['status'] != 'completed':
                continue
            
            metrics = result['metrics']
            
            # Calculate composite score (weighted average)
            # Weights: quality=50%, speed=30%, cost=20%
            quality_score = metrics.get('quality_score', 0.0)
            
            # Normalize speed (faster is better, cap at 10 seconds)
            speed_score = max(0.0, 1.0 - (metrics.get('duration_seconds', 10) / 10))
            
            # Normalize cost (cheaper is better, cap at $0.10)
            cost_score = max(0.0, 1.0 - (metrics.get('cost_estimate', 0.1) / 0.1))
            
            composite_score = (
                0.5 * quality_score +
                0.3 * speed_score +
                0.2 * cost_score
            )
            
            rankings.append({
                'model_name': result['model_name'],
                'provider': result['provider'],
                'category': result['category'],
                'composite_score': composite_score,
                'quality_score': quality_score,
                'speed_score': speed_score,
                'cost_score': cost_score,
                'metrics': metrics
            })
        
        # Sort by composite score (descending)
        rankings.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Add rank numbers
        for i, ranking in enumerate(rankings, 1):
            ranking['rank'] = i
        
        return rankings
    
    def _select_top_models(self, rankings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Select top models for main experiments.
        
        Implements REQ-3.6.2.6: Select top 2 models from each category.
        
        Args:
            rankings: Ranked list of models
        
        Returns:
            List of selected models
        """
        # Get selection criteria from config
        models_per_category = self.exp_config.get('models_per_category', 2)
        
        # Group by category
        by_category = {}
        for ranking in rankings:
            category = ranking['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(ranking)
        
        # Select top N from each category
        selected = []
        for category, models in by_category.items():
            top_models = models[:models_per_category]
            selected.extend(top_models)
            
            self.log_info(
                f"Selected {len(top_models)} models from category: {category}"
            )
        
        return selected
    
    def _generate_selection_report(
        self,
        rankings: List[Dict[str, Any]],
        selected_models: List[Dict[str, Any]],
        benchmark_task: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable selection report.
        
        Implements REQ-3.6.2.7: Document selection rationale.
        
        Args:
            rankings: All model rankings
            selected_models: Selected models
            benchmark_task: Benchmark task definition
        
        Returns:
            Markdown-formatted report
        """
        report_lines = [
            "# Model Selection Report (PE02)",
            "",
            "## Benchmark Task",
            f"Description: {benchmark_task.get('description', 'N/A')}",
            "",
            "## Rankings",
            "",
            "| Rank | Model | Provider | Category | Composite Score | Quality | Speed | Cost |",
            "|------|-------|----------|----------|----------------|---------|-------|------|"
        ]
        
        # Add ranking rows
        for ranking in rankings[:10]:  # Top 10
            report_lines.append(
                f"| {ranking['rank']} "
                f"| {ranking['model_name']} "
                f"| {ranking['provider']} "
                f"| {ranking['category']} "
                f"| {ranking['composite_score']:.3f} "
                f"| {ranking['quality_score']:.3f} "
                f"| {ranking['speed_score']:.3f} "
                f"| {ranking['cost_score']:.3f} |"
            )
        
        report_lines.extend([
            "",
            "## Selected Models",
            "",
            "The following models were selected for main experiments:",
            ""
        ])
        
        # Add selected models
        for model in selected_models:
            report_lines.append(
                f"- **{model['model_name']}** ({model['category']}) "
                f"- Score: {model['composite_score']:.3f}"
            )
        
        report_lines.extend([
            "",
            "## Selection Criteria",
            "",
            "Models were ranked using a composite score:",
            "- Quality: 50% weight",
            "- Speed: 30% weight",
            "- Cost: 20% weight",
            "",
            f"Top {len(selected_models)} models selected across all categories."
        ])
        
        return "\n".join(report_lines)
