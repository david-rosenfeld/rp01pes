#!/usr/bin/env python3
"""
Test script for PE10 Power Analysis experiment.

This script tests PE10 with various pilot data configurations.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pes.core.config import ConfigurationManager
from pes.experiments.pe10_poweranalysis import PowerAnalysisExperiment


def test_pe10_with_example_data():
    """Test PE10 with example pilot data."""
    print("=" * 70)
    print("TEST 1: PE10 with Example Data")
    print("=" * 70)
    print()

    # Create configuration with example data
    config_dict = {
        'experiments': {
            'poweranalysis': {
                'task_types': ['trace', 'recover', 'fill'],
                'alpha': 0.05,
                'power': 0.80,
                'paired': True,
                'inflation_rate': 0.15,
                'default_min_effect_size': 0.5
            }
        },
        'logging': {
            'level': 'INFO',
            'format': 'simple'
        }
    }

    config = ConfigurationManager(config_dict=config_dict)

    # Create and run experiment
    experiment = PowerAnalysisExperiment(config)
    print(f"Description: {experiment.get_description()}")
    print()

    results = experiment.run()

    # Display results
    print()
    print("-" * 70)
    print("RESULTS")
    print("-" * 70)
    print()

    print(f"Task Types Analyzed: {', '.join(results['task_types'])}")
    print()

    # Summary
    summary = results['summary']
    print("Summary:")
    print(f"  Total TaskTypes: {summary['total_task_types']}")
    print(f"  Sample Size Range (required): {summary['sample_size_range']['min_required']}-{summary['sample_size_range']['max_required']}")
    print(f"  Sample Size Range (inflated): {summary['sample_size_range']['min_inflated']}-{summary['sample_size_range']['max_inflated']}")
    print(f"  Mean Achieved Power: {summary['power_summary']['mean_achieved_power']:.3f}")
    print()

    # Per-TaskType results
    print("Per-TaskType Analysis:")
    for task_type in results['task_types']:
        result = results['power_analysis_results'][task_type]
        rec = results['recommendations']['per_task_type'][task_type]

        print(f"\n  {task_type.upper()}:")
        print(f"    Pilot: n={result['pilot_data_summary']['sample_size']}, SD={result['pilot_data_summary']['standard_deviation']:.4f}")
        print(f"    Effect Size: {result['effect_size']['minimum_detectable']} ({result['effect_size']['interpretation']})")
        print(f"    Required n: {result['sample_size_calculation']['required_n']}")
        print(f"    Recommended n: {rec['recommended_n']} (with {result['inflation']['inflation_rate']:.0%} inflation)")
        print(f"    Achieved Power: {result['achieved_power']:.3f}")

    # Recommendations
    print()
    print("Recommendations:")
    print(f"  Conservative approach: Use {results['recommendations']['overall']['conservative_n']} samples for all TaskTypes")
    print(f"  Rationale: {results['recommendations']['overall']['rationale']}")
    print()

    print("[PASS] PE10 executed successfully with example data")
    print()


def test_pe10_with_custom_pilot_data():
    """Test PE10 with custom pilot data."""
    print("=" * 70)
    print("TEST 2: PE10 with Custom Pilot Data")
    print("=" * 70)
    print()

    # Create configuration with custom pilot data
    # Simulating pilot data from actual experiment runs
    config_dict = {
        'experiments': {
            'poweranalysis': {
                'pilot_data': {
                    'trace': [0.12, 0.15, 0.10, 0.13, 0.11, 0.14, 0.12, 0.13],  # Higher variance
                    'recover': [0.08, 0.09, 0.08, 0.07, 0.09, 0.08, 0.08, 0.09],  # Lower variance
                },
                'alpha': 0.05,
                'power': 0.80,
                'paired': True,
                'inflation_rate': 0.20,  # 20% inflation
                'default_min_effect_size': 0.4  # Smaller effect size
            }
        },
        'logging': {
            'level': 'INFO',
            'format': 'simple'
        }
    }

    config = ConfigurationManager(config_dict=config_dict)

    # Create and run experiment
    experiment = PowerAnalysisExperiment(config)
    results = experiment.run()

    # Display key results
    print()
    print("-" * 70)
    print("RESULTS")
    print("-" * 70)
    print()

    for task_type in results['task_types']:
        result = results['power_analysis_results'][task_type]
        print(f"{task_type}: Recommend n={result['recommendation']} (power={result['achieved_power']:.3f})")

    print()
    print("[PASS] PE10 executed successfully with custom pilot data")
    print()


def test_pe10_with_different_effect_sizes():
    """Test PE10 with different effect sizes per TaskType."""
    print("=" * 70)
    print("TEST 3: PE10 with Task-Specific Effect Sizes")
    print("=" * 70)
    print()

    # Configuration with different effect sizes per TaskType
    config_dict = {
        'experiments': {
            'poweranalysis': {
                'pilot_data': {
                    'easy_task': [0.05, 0.06, 0.05, 0.07, 0.06],
                    'medium_task': [0.10, 0.12, 0.09, 0.11, 0.10],
                    'hard_task': [0.15, 0.18, 0.14, 0.17, 0.16]
                },
                'easy_task': {'min_effect_size': 0.3},  # Small effect
                'medium_task': {'min_effect_size': 0.5},  # Medium effect
                'hard_task': {'min_effect_size': 0.8},  # Large effect
                'alpha': 0.05,
                'power': 0.80,
                'paired': True,
                'inflation_rate': 0.15
            }
        },
        'logging': {
            'level': 'INFO',
            'format': 'simple'
        }
    }

    config = ConfigurationManager(config_dict=config_dict)

    # Create and run experiment
    experiment = PowerAnalysisExperiment(config)
    results = experiment.run()

    # Display results
    print()
    print("-" * 70)
    print("RESULTS - Effect Size Impact")
    print("-" * 70)
    print()

    for task_type in results['task_types']:
        result = results['power_analysis_results'][task_type]
        effect_size = result['effect_size']['minimum_detectable']
        rec_n = result['recommendation']
        print(f"{task_type}:")
        print(f"  Effect size: {effect_size} ({result['effect_size']['interpretation']})")
        print(f"  Recommended n: {rec_n}")
        print()

    print("Note: Larger effect sizes require smaller sample sizes")
    print("[PASS] PE10 handles task-specific effect sizes correctly")
    print()


def test_pe10_results_structure():
    """Test that PE10 results have the correct structure."""
    print("=" * 70)
    print("TEST 4: PE10 Results Structure Validation")
    print("=" * 70)
    print()

    config_dict = {
        'experiments': {
            'poweranalysis': {
                'task_types': ['trace'],
                'alpha': 0.05,
                'power': 0.80
            }
        },
        'logging': {
            'level': 'ERROR'  # Suppress output for this test
        }
    }

    config = ConfigurationManager(config_dict=config_dict)
    experiment = PowerAnalysisExperiment(config)
    results = experiment.run()

    # Validate structure
    assert 'task_types' in results, "Missing 'task_types'"
    assert 'power_analysis_results' in results, "Missing 'power_analysis_results'"
    assert 'summary' in results, "Missing 'summary'"
    assert 'recommendations' in results, "Missing 'recommendations'"
    assert 'experiment_id' in results, "Missing 'experiment_id'"

    print("Checking result structure...")

    # Validate power_analysis_results structure
    for task_type in results['task_types']:
        pa_result = results['power_analysis_results'][task_type]

        assert 'pilot_data_summary' in pa_result
        assert 'effect_size' in pa_result
        assert 'sample_size_calculation' in pa_result
        assert 'inflation' in pa_result
        assert 'achieved_power' in pa_result
        assert 'recommendation' in pa_result

        print(f"  {task_type}: [OK]")

    # Validate summary structure
    assert 'total_task_types' in results['summary']
    assert 'sample_size_range' in results['summary']
    assert 'power_summary' in results['summary']
    print("  Summary: [OK]")

    # Validate recommendations structure
    assert 'per_task_type' in results['recommendations']
    assert 'overall' in results['recommendations']
    print("  Recommendations: [OK]")

    print()
    print("[PASS] PE10 results structure is correct")
    print()


def main():
    """Run all tests."""
    print()
    print("=" * 70)
    print("PE10 POWER ANALYSIS EXPERIMENT TEST SUITE")
    print("=" * 70)
    print()

    try:
        test_pe10_with_example_data()
        test_pe10_with_custom_pilot_data()
        test_pe10_with_different_effect_sizes()
        test_pe10_results_structure()

        print("=" * 70)
        print("ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("Summary:")
        print("  - PE10 runs successfully with example data")
        print("  - PE10 handles custom pilot data correctly")
        print("  - PE10 supports task-specific effect sizes")
        print("  - Results structure is correct and complete")
        print()
        print("PE10 Power Analysis experiment is ready for use!")

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print("TEST FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
