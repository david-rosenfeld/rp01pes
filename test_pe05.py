#!/usr/bin/env python3
"""
Test suite for PE05: Max Token Determination

Tests the Max Token Determination experiment with mock data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pes.core.config import ConfigurationManager
from pes.experiments.pe05_maxtokendetermination import MaxTokenDeterminationExperiment


def test_pe05_basic():
    """Test PE05 with basic configuration."""
    print("=" * 70)
    print("Test: PE05 Basic Execution")
    print("=" * 70)

    config_dict = {
        'experiments': {
            'maxtokendetermination': {
                'model': {
                    'provider': 'mock',
                    'name': 'mock-model',
                    'response_mode': 'realistic',
                    'temperature': 0.7
                },
                'dataset': 'albergate',
                'task_types': ['trace', 'recover'],
                'sample_size': 15,
                'candidate_limits': [100, 200, 300, 500, 1000],
                'max_truncation_rate': 0.05
            }
        },
        'logging': {
            'level': 'INFO',
            'format': 'simple'
        }
    }

    config = ConfigurationManager(config_dict=config_dict)

    # Create and run experiment
    experiment = MaxTokenDeterminationExperiment(config)
    print(f"Description: {experiment.get_description()}")
    print()

    results = experiment.run()

    # Display results
    print()
    print("-" * 70)
    print("Results Summary:")
    print("-" * 70)

    for task_type in results['task_types']:
        print(f"\nTaskType: {task_type}")

        # Distribution stats
        stats = results['distribution_statistics'][task_type]
        print(f"  Token Length Distribution:")
        print(f"    Mean: {stats['mean']:.1f}")
        print(f"    Median: {stats['median']:.1f}")
        print(f"    95th percentile: {stats['percentile_95']:.1f}")
        print(f"    Max: {stats['max']:.1f}")

        # Recommendation
        rec = results['recommendations'][task_type]
        if rec['max_tokens'] is None:
            print(f"  Recommendation: No explicit limit")
        else:
            print(f"  Recommendation: {rec['max_tokens']} tokens")
        print(f"  Justification: {rec['justification']}")

    print()
    print("[PASS] PE05 basic test completed successfully")
    print()


def test_pe05_high_variability():
    """Test PE05 with configuration that simulates high output variability."""
    print("=" * 70)
    print("Test: PE05 with High Variability")
    print("=" * 70)

    config_dict = {
        'experiments': {
            'maxtokendetermination': {
                'model': {
                    'provider': 'mock',
                    'name': 'mock-model-variable',
                    'response_mode': 'realistic'
                },
                'dataset': 'ebt',
                'task_types': ['fill'],
                'sample_size': 20,
                'candidate_limits': [50, 100, 200, 500, 1000, 2000],
                'max_truncation_rate': 0.10  # Allow 10% truncation
            }
        },
        'logging': {
            'level': 'ERROR'  # Suppress output
        }
    }

    config = ConfigurationManager(config_dict=config_dict)
    experiment = MaxTokenDeterminationExperiment(config)
    results = experiment.run()

    # Validate structure
    assert 'task_types' in results
    assert 'token_measurements' in results
    assert 'distribution_statistics' in results
    assert 'truncation_analysis' in results
    assert 'recommendations' in results

    # Validate recommendations
    for task_type in results['task_types']:
        rec = results['recommendations'][task_type]
        assert 'max_tokens' in rec
        assert 'recommendation_type' in rec
        assert 'justification' in rec
        assert rec['recommendation_type'] in ['specific_limit', 'no_limit']

    print()
    print("[PASS] PE05 high variability test completed successfully")
    print()


def test_pe05_results_structure():
    """Test that PE05 results have correct structure."""
    print("=" * 70)
    print("Test: PE05 Results Structure Validation")
    print("=" * 70)

    config_dict = {
        'experiments': {
            'maxtokendetermination': {
                'model': {'provider': 'mock'},
                'task_types': ['trace'],
                'sample_size': 10
            }
        },
        'logging': {'level': 'ERROR'}
    }

    config = ConfigurationManager(config_dict=config_dict)
    experiment = MaxTokenDeterminationExperiment(config)
    results = experiment.run()

    # Validate top-level structure
    assert 'experiment_id' in results, "Missing 'experiment_id'"
    assert 'task_types' in results, "Missing 'task_types'"
    assert 'token_measurements' in results, "Missing 'token_measurements'"
    assert 'distribution_statistics' in results, "Missing 'distribution_statistics'"
    assert 'truncation_analysis' in results, "Missing 'truncation_analysis'"
    assert 'recommendations' in results, "Missing 'recommendations'"

    # Validate per-task structure
    for task_type in results['task_types']:
        # Token measurements
        assert task_type in results['token_measurements']
        measurements = results['token_measurements'][task_type]
        assert 'task_type' in measurements
        assert 'sample_size' in measurements
        assert 'token_lengths' in measurements
        assert len(measurements['token_lengths']) > 0

        # Distribution statistics
        assert task_type in results['distribution_statistics']
        stats = results['distribution_statistics'][task_type]
        required_stats = ['mean', 'median', 'std', 'min', 'max',
                         'q1', 'q3', 'percentile_95', 'percentile_99']
        for stat in required_stats:
            assert stat in stats, f"Missing stat: {stat}"

        # Truncation analysis
        assert task_type in results['truncation_analysis']
        analysis = results['truncation_analysis'][task_type]
        assert 'limits_tested' in analysis
        assert 'limit_analysis' in analysis

        # Recommendations
        assert task_type in results['recommendations']
        rec = results['recommendations'][task_type]
        assert 'max_tokens' in rec
        assert 'recommendation_type' in rec
        assert 'justification' in rec

    print()
    print("[PASS] PE05 results structure validation completed successfully")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("PE05: Max Token Determination - Test Suite")
    print("=" * 70 + "\n")

    try:
        test_pe05_basic()
        test_pe05_high_variability()
        test_pe05_results_structure()

        print("=" * 70)
        print("All PE05 tests passed!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n[FAIL] Test assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
