"""
PE09: Token Budget Allocation

This experiment determines optimal token budget allocation across prompt sections
by measuring section sizes and testing allocation schemes.

Implements REQ-3.6.9 (Token Budget Allocation).
"""

from typing import Dict, Any, List
import numpy as np

from ..core.base_experiment import BaseExperiment
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError
from ..datasets import load_dataset
from ..analysis import descriptive_statistics


class TokenBudgetExperiment(BaseExperiment):
    """
    Token Budget Allocation experiment.

    Analyzes token usage across prompt sections and determines optimal
    allocation schemes to fit within model context limits.

    Implements REQ-3.6.9.
    """

    def __init__(self, config: ConfigurationManager, experiment_id: str = "PE09"):
        """
        Initialize Token Budget Allocation experiment.

        Args:
            config: Configuration manager
            experiment_id: Experiment identifier (default: "PE09")
        """
        super().__init__(config, experiment_id)

        # Load experiment-specific configuration
        self.exp_config = config.get('experiments.tokenbudget', {})

        # Validate configuration
        self._validate_experiment_config()

        self.log_info("Token Budget Allocation experiment initialized")

    def _validate_experiment_config(self) -> None:
        """
        Validate experiment-specific configuration.

        Raises:
            ExperimentError: If configuration is invalid
        """
        # Check for required fields
        if 'total_budget' not in self.exp_config:
            raise ExperimentError(
                "Token budget experiment requires 'total_budget' in configuration"
            )

    def get_description(self) -> str:
        """Get experiment description."""
        return "Determine optimal token budget allocation across prompt sections"

    def run(self) -> Dict[str, Any]:
        """
        Execute Token Budget Allocation experiment.

        This implements the PE09 workflow (REQ-3.6.9):
        1. Define prompt sections to measure
        2. Measure token counts per section (REQ-3.6.9.2)
        3. Design allocation schemes (REQ-3.6.9.3)
        4. Test schemes for truncation (REQ-3.6.9.4)
        5. Adjust if needed (REQ-3.6.9.5)
        6. Output finalized budget (REQ-3.6.9.6)

        Returns:
            Dictionary containing experiment results:
                - total_budget: Total token budget
                - prompt_sections: List of sections measured
                - section_measurements: Token counts per section
                - allocation_schemes: Candidate allocation schemes
                - truncation_analysis: Testing results
                - final_allocation: Recommended token budget
                - budget_configuration: Per-section token limits

        Implements REQ-3.6.9.1 through REQ-3.6.9.6
        """
        self.log_info("Starting token budget allocation experiment")

        # Get total budget
        total_budget = self.exp_config['total_budget']

        # Step 1: Define prompt sections
        sections = self._define_prompt_sections()
        self.log_info(f"Prompt sections: {list(sections.keys())}")

        # Step 2: Measure token counts per section (REQ-3.6.9.2)
        dataset_info = self._load_dataset()
        section_measurements = self._measure_section_tokens(sections, dataset_info)

        # Step 3: Design allocation schemes (REQ-3.6.9.3)
        allocation_schemes = self._design_allocation_schemes(
            total_budget,
            section_measurements
        )

        # Step 4: Test schemes for truncation (REQ-3.6.9.4)
        truncation_analysis = self._test_truncation(
            allocation_schemes,
            section_measurements
        )

        # Step 5: Adjust if needed and select final (REQ-3.6.9.5)
        final_allocation = self._select_and_adjust_allocation(
            allocation_schemes,
            truncation_analysis,
            total_budget
        )

        # Step 6: Output budget configuration (REQ-3.6.9.6)
        budget_configuration = self._generate_budget_config(
            final_allocation,
            section_measurements
        )

        # Compile results
        results = {
            'experiment_id': self.experiment_id,
            'total_budget': total_budget,
            'prompt_sections': list(sections.keys()),
            'section_measurements': section_measurements,
            'allocation_schemes': allocation_schemes,
            'truncation_analysis': truncation_analysis,
            'final_allocation': final_allocation,
            'budget_configuration': budget_configuration
        }

        self.log_info("Token budget allocation experiment completed")
        self._log_final_allocation(budget_configuration)

        return results

    def _define_prompt_sections(self) -> Dict[str, str]:
        """
        Define prompt sections to measure.

        Returns:
            Dictionary of section names and descriptions
        """
        return {
            'persona': 'System role and expertise declaration',
            'instruction': 'Task-specific instructions',
            'requirement': 'Requirement or use case text',
            'traceability_bundle': 'Related code artifacts and context',
            'file_list': 'List of available source files',
            'output_specification': 'Expected output format and constraints'
        }

    def _load_dataset(self) -> Dict[str, Any]:
        """
        Load dataset for token measurement.

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

    def _measure_section_tokens(
        self,
        sections: Dict[str, str],
        dataset_info: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Measure token counts for each prompt section.

        Implements REQ-3.6.9.2: Section Token Measurement.

        Args:
            sections: Section definitions
            dataset_info: Dataset information

        Returns:
            Token measurements per section
        """
        dataset = dataset_info['dataset']
        sample_size = self.exp_config.get('sample_size', 20)

        measurements = {}

        # Get sample requirements
        requirements = list(dataset.requirements.values())[:sample_size]

        # Measure each section
        for section_name in sections.keys():
            self.log_info(f"  Measuring section: {section_name}")

            token_counts = []

            for req in requirements:
                # Generate section content
                content = self._generate_section_content(
                    section_name,
                    req,
                    dataset
                )

                # Estimate tokens (simple word count approximation)
                # In production, would use tiktoken or similar
                token_count = self._estimate_tokens(content)
                token_counts.append(token_count)

            # Compute statistics
            stats = descriptive_statistics(token_counts)

            measurements[section_name] = {
                'token_counts': token_counts,
                'mean': stats['mean'],
                'median': stats['median'],
                'std': stats['std'],
                'min': stats['min'],
                'max': stats['max'],
                'percentile_95': float(np.percentile(token_counts, 95)),
                'sample_size': len(token_counts)
            }

        return measurements

    def _generate_section_content(
        self,
        section_name: str,
        requirement,
        dataset
    ) -> str:
        """
        Generate representative content for a section.

        Args:
            section_name: Section to generate
            requirement: Requirement object
            dataset: Dataset object

        Returns:
            Section content
        """
        if section_name == 'persona':
            return "You are an expert in software traceability analysis."

        elif section_name == 'instruction':
            return (
                "Identify all traceability links between this requirement and code artifacts. "
                "Analyze the requirement's key concepts, identify relevant code artifacts, "
                "and establish links based on semantic similarity."
            )

        elif section_name == 'requirement':
            return requirement.content

        elif section_name == 'traceability_bundle':
            # Simulate a traceability bundle with code context
            source_files = list(dataset.source_files.values())[:5]
            bundle_parts = []
            for sf in source_files:
                # Use first 200 chars of each file as example
                preview = sf.content[:200] if len(sf.content) > 200 else sf.content
                bundle_parts.append(f"File: {sf.file_name}\n{preview}")
            return "\n\n".join(bundle_parts)

        elif section_name == 'file_list':
            # List of available files
            source_files = list(dataset.source_files.values())[:20]
            return "\n".join([f"- {sf.file_name}" for sf in source_files])

        elif section_name == 'output_specification':
            return (
                "Provide your answer in the following format:\n"
                "REQ-XXX -> ARTIFACT-YYY\n"
                "Include confidence scores for each link."
            )

        return ""

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Simple approximation: 1 token ≈ 0.75 words
        In production, would use tiktoken.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        words = len(text.split())
        return int(words / 0.75)

    def _design_allocation_schemes(
        self,
        total_budget: int,
        section_measurements: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Design candidate allocation schemes.

        Implements REQ-3.6.9.3: Allocation Scheme Design.

        Args:
            total_budget: Total token budget
            section_measurements: Measured token counts

        Returns:
            Candidate allocation schemes
        """
        schemes = {}

        # Scheme 1: Proportional to observed usage
        total_observed = sum(m['mean'] for m in section_measurements.values())
        proportional = {}
        for section, stats in section_measurements.items():
            proportion = stats['mean'] / total_observed
            proportional[section] = {
                'percentage': proportion * 100,
                'tokens': int(total_budget * proportion)
            }
        schemes['proportional'] = {
            'name': 'Proportional',
            'description': 'Allocate based on observed usage patterns',
            'allocations': proportional
        }

        # Scheme 2: Context-focused (50% for traceability bundle)
        context_focused = {
            'persona': {'percentage': 5, 'tokens': int(total_budget * 0.05)},
            'instruction': {'percentage': 10, 'tokens': int(total_budget * 0.10)},
            'requirement': {'percentage': 15, 'tokens': int(total_budget * 0.15)},
            'traceability_bundle': {'percentage': 50, 'tokens': int(total_budget * 0.50)},
            'file_list': {'percentage': 10, 'tokens': int(total_budget * 0.10)},
            'output_specification': {'percentage': 10, 'tokens': int(total_budget * 0.10)}
        }
        schemes['context_focused'] = {
            'name': 'Context-Focused',
            'description': '50% to traceability bundle, balanced rest',
            'allocations': context_focused
        }

        # Scheme 3: Balanced
        balanced = {
            'persona': {'percentage': 5, 'tokens': int(total_budget * 0.05)},
            'instruction': {'percentage': 15, 'tokens': int(total_budget * 0.15)},
            'requirement': {'percentage': 20, 'tokens': int(total_budget * 0.20)},
            'traceability_bundle': {'percentage': 40, 'tokens': int(total_budget * 0.40)},
            'file_list': {'percentage': 10, 'tokens': int(total_budget * 0.10)},
            'output_specification': {'percentage': 10, 'tokens': int(total_budget * 0.10)}
        }
        schemes['balanced'] = {
            'name': 'Balanced',
            'description': 'Balanced allocation across all sections',
            'allocations': balanced
        }

        return schemes

    def _test_truncation(
        self,
        allocation_schemes: Dict[str, Dict[str, Any]],
        section_measurements: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Test allocation schemes for truncation.

        Implements REQ-3.6.9.4: Truncation Testing.

        Args:
            allocation_schemes: Candidate schemes
            section_measurements: Measured token counts

        Returns:
            Truncation analysis results
        """
        analysis = {}

        for scheme_name, scheme in allocation_schemes.items():
            self.log_info(f"  Testing scheme: {scheme['name']}")

            truncation_results = {}

            for section, allocation in scheme['allocations'].items():
                measurements = section_measurements[section]

                # Check how often this allocation would truncate
                truncated_count = sum(
                    1 for count in measurements['token_counts']
                    if count > allocation['tokens']
                )

                truncation_rate = truncated_count / measurements['sample_size']

                # Check if 95th percentile fits
                fits_95th = allocation['tokens'] >= measurements['percentile_95']

                truncation_results[section] = {
                    'allocated_tokens': allocation['tokens'],
                    'mean_tokens': measurements['mean'],
                    'max_tokens': measurements['max'],
                    'truncation_rate': truncation_rate,
                    'truncated_count': truncated_count,
                    'fits_95th_percentile': fits_95th,
                    'headroom': allocation['tokens'] - measurements['mean']
                }

            # Overall truncation assessment
            total_truncation_rate = np.mean([
                r['truncation_rate'] for r in truncation_results.values()
            ])

            analysis[scheme_name] = {
                'scheme_name': scheme['name'],
                'section_results': truncation_results,
                'total_truncation_rate': total_truncation_rate,
                'acceptable': total_truncation_rate <= 0.05  # 5% threshold
            }

        return analysis

    def _select_and_adjust_allocation(
        self,
        allocation_schemes: Dict[str, Dict[str, Any]],
        truncation_analysis: Dict[str, Dict[str, Any]],
        total_budget: int
    ) -> Dict[str, Any]:
        """
        Select and adjust final allocation scheme.

        Implements REQ-3.6.9.5: Adjustment and Validation.

        Args:
            allocation_schemes: Candidate schemes
            truncation_analysis: Truncation test results
            total_budget: Total token budget

        Returns:
            Final allocation scheme
        """
        # Find acceptable schemes
        acceptable_schemes = [
            (name, analysis)
            for name, analysis in truncation_analysis.items()
            if analysis['acceptable']
        ]

        if not acceptable_schemes:
            # No scheme is acceptable - need adjustment
            self.log_warning("No scheme meets truncation threshold, adjusting...")

            # Start with the best scheme and adjust
            best_scheme_name = min(
                truncation_analysis.keys(),
                key=lambda k: truncation_analysis[k]['total_truncation_rate']
            )

            # Adjust by increasing allocations for problematic sections
            adjusted_scheme = self._adjust_scheme(
                allocation_schemes[best_scheme_name],
                truncation_analysis[best_scheme_name],
                total_budget
            )

            return {
                'scheme_name': f"{adjusted_scheme['name']} (Adjusted)",
                'allocations': adjusted_scheme['allocations'],
                'was_adjusted': True,
                'original_scheme': best_scheme_name
            }

        else:
            # Select best acceptable scheme (lowest truncation)
            best_scheme_name, best_analysis = min(
                acceptable_schemes,
                key=lambda x: x[1]['total_truncation_rate']
            )

            return {
                'scheme_name': allocation_schemes[best_scheme_name]['name'],
                'allocations': allocation_schemes[best_scheme_name]['allocations'],
                'was_adjusted': False,
                'truncation_rate': best_analysis['total_truncation_rate']
            }

    def _adjust_scheme(
        self,
        scheme: Dict[str, Any],
        analysis: Dict[str, Any],
        total_budget: int
    ) -> Dict[str, Any]:
        """
        Adjust allocation scheme to reduce truncation.

        Args:
            scheme: Scheme to adjust
            analysis: Truncation analysis
            total_budget: Total budget

        Returns:
            Adjusted scheme
        """
        # Identify sections with high truncation
        adjustments_needed = {
            section: result['truncation_rate']
            for section, result in analysis['section_results'].items()
            if result['truncation_rate'] > 0.05
        }

        # Increase allocation for problematic sections
        adjusted_allocations = scheme['allocations'].copy()

        # Redistribute: take from sections with excess, give to those truncating
        # Simplified: increase each problematic section by 20%
        for section in adjustments_needed.keys():
            old_tokens = adjusted_allocations[section]['tokens']
            new_tokens = int(old_tokens * 1.2)
            adjusted_allocations[section]['tokens'] = new_tokens
            adjusted_allocations[section]['percentage'] = (new_tokens / total_budget) * 100

        return {
            'name': scheme['name'],
            'allocations': adjusted_allocations
        }

    def _generate_budget_config(
        self,
        final_allocation: Dict[str, Any],
        section_measurements: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate final budget configuration.

        Implements REQ-3.6.9.6: Budget Configuration Output.

        Args:
            final_allocation: Selected allocation scheme
            section_measurements: Section measurements

        Returns:
            Budget configuration
        """
        config = {
            'scheme_name': final_allocation['scheme_name'],
            'was_adjusted': final_allocation['was_adjusted'],
            'per_section_limits': {}
        }

        for section, allocation in final_allocation['allocations'].items():
            measurements = section_measurements[section]

            config['per_section_limits'][section] = {
                'max_tokens': allocation['tokens'],
                'percentage': allocation['percentage'],
                'typical_usage': measurements['mean'],
                'headroom': allocation['tokens'] - measurements['mean'],
                'guidance': self._generate_section_guidance(
                    section,
                    allocation['tokens'],
                    measurements
                )
            }

        return config

    def _generate_section_guidance(
        self,
        section: str,
        allocated_tokens: int,
        measurements: Dict[str, Any]
    ) -> str:
        """
        Generate guidance for a section's token budget.

        Args:
            section: Section name
            allocated_tokens: Allocated tokens
            measurements: Section measurements

        Returns:
            Guidance text
        """
        headroom_pct = ((allocated_tokens - measurements['mean']) / measurements['mean']) * 100

        if headroom_pct > 50:
            return f"Generous allocation with {headroom_pct:.0f}% headroom"
        elif headroom_pct > 20:
            return f"Adequate allocation with {headroom_pct:.0f}% headroom"
        elif headroom_pct > 0:
            return f"Tight allocation with only {headroom_pct:.0f}% headroom"
        else:
            return f"WARNING: Allocation below mean usage by {abs(headroom_pct):.0f}%"

    def _log_final_allocation(self, budget_configuration: Dict[str, Any]) -> None:
        """
        Log final token budget allocation.

        Args:
            budget_configuration: Final budget configuration
        """
        self.log_info("=" * 60)
        self.log_info("Final Token Budget Allocation")
        self.log_info("=" * 60)
        self.log_info(f"Scheme: {budget_configuration['scheme_name']}")
        self.log_info("")

        for section, config in budget_configuration['per_section_limits'].items():
            self.log_info(
                f"{section}: {config['max_tokens']} tokens "
                f"({config['percentage']:.1f}%)"
            )
            self.log_info(f"  {config['guidance']}")

        self.log_info("=" * 60)
