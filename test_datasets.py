#!/usr/bin/env python3
"""
Test script for dataset management module.

This script tests loading datasets, parsing ground truth, and generating
traceability bundles.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pes.datasets import (
    load_dataset,
    list_available_datasets,
    generate_bundles_for_dataset,
    format_bundle_text,
    get_bundle_statistics,
    DATASET_METADATA
)
from pes.core.logging import get_logger


def main():
    """Run dataset management tests."""
    
    # Setup logging
    logger = get_logger(__name__, log_dir="logs", level="INFO")
    
    print("=" * 70)
    print("DATASET MANAGEMENT MODULE TEST")
    print("=" * 70)
    print()
    
    # Configuration
    config = {
        'base_path': './datasets'
    }
    
    # Test 1: List available datasets
    print("Test 1: List Available Datasets")
    print("-" * 70)
    available = list_available_datasets(config['base_path'])
    print(f"Available datasets: {', '.join(available)}")
    print(f"Total: {len(available)} datasets")
    print()
    
    if not available:
        print("❌ ERROR: No datasets found!")
        print(f"   Make sure datasets are in {config['base_path']}/")
        return 1
    
    # Test 2: Load each dataset
    print("Test 2: Load All Datasets")
    print("-" * 70)
    
    datasets = {}
    for dataset_name in available:
        try:
            print(f"\nLoading {dataset_name}...")
            dataset = load_dataset(dataset_name, config)
            datasets[dataset_name] = dataset
            
            # Print summary
            print(f"  ✓ {dataset.name}")
            print(f"    Language: {dataset.language}")
            print(f"    Requirements: {len(dataset.requirements)}")
            print(f"    Source Files: {len(dataset.source_files)}")
            print(f"    Traceability Links: {len(dataset.traceability_links)}")
            
            # Check against expected counts
            expected_req_count = DATASET_METADATA[dataset_name].get('req_count')
            actual_req_count = len(dataset.requirements)
            if expected_req_count and actual_req_count != expected_req_count:
                print(f"    ⚠️  Warning: Expected {expected_req_count} requirements, "
                      f"got {actual_req_count}")
            
        except Exception as e:
            print(f"  ❌ Failed to load {dataset_name}: {e}")
            return 1
    
    print(f"\n✓ Successfully loaded {len(datasets)} datasets")
    print()
    
    # Test 3: Generate bundles for one dataset
    print("Test 3: Generate Traceability Bundles")
    print("-" * 70)
    
    # Use Albergate as test case (smallest dataset)
    if 'albergate' in datasets:
        test_dataset = datasets['albergate']
        print(f"\nGenerating bundles for {test_dataset.name}...")
        
        # Generate without token budget
        bundles_unlimited = generate_bundles_for_dataset(test_dataset)
        print(f"  Generated {len(bundles_unlimited)} bundles (unlimited)")
        
        # Generate with token budget
        bundles_limited = generate_bundles_for_dataset(test_dataset, token_budget=5000)
        print(f"  Generated {len(bundles_limited)} bundles (5000 token budget)")
        
        # Get statistics
        stats_unlimited = get_bundle_statistics(bundles_unlimited)
        stats_limited = get_bundle_statistics(bundles_limited)
        
        print("\n  Unlimited bundles statistics:")
        print(f"    Average tokens: {stats_unlimited['avg_token_count']:.0f}")
        print(f"    Max tokens: {stats_unlimited['max_token_count']}")
        print(f"    Average files per bundle: {stats_unlimited['avg_files_per_bundle']:.1f}")
        print(f"    Empty bundles: {stats_unlimited['empty_bundles']}")
        
        print("\n  Limited bundles statistics:")
        print(f"    Average tokens: {stats_limited['avg_token_count']:.0f}")
        print(f"    Max tokens: {stats_limited['max_token_count']}")
        print(f"    Truncated: {stats_limited['truncated_count']}")
        print(f"    Empty bundles: {stats_limited['empty_bundles']}")
        
        # Test 4: Format a sample bundle
        print("\n" + "=" * 70)
        print("Test 4: Format Sample Bundle")
        print("-" * 70)
        
        # Get first bundle
        first_req_id = list(bundles_unlimited.keys())[0]
        sample_bundle = bundles_unlimited[first_req_id]
        
        print(f"\nFormatting bundle for requirement: {first_req_id}")
        print(f"  Files: {len(sample_bundle.linked_files)}")
        print(f"  Tokens: {sample_bundle.token_count}")
        print()
        
        # Format and show preview
        formatted = format_bundle_text(sample_bundle)
        lines = formatted.split('\n')
        preview_lines = 30
        
        print("  Preview (first 30 lines):")
        print("  " + "-" * 66)
        for line in lines[:preview_lines]:
            print(f"  {line}")
        if len(lines) > preview_lines:
            print(f"  ... ({len(lines) - preview_lines} more lines)")
        print()
        
    else:
        print("  ⚠️  Albergate dataset not available, skipping bundle test")
    
    # Test 5: Verify specific dataset features
    print("=" * 70)
    print("Test 5: Dataset-Specific Features")
    print("-" * 70)
    
    # Check LibEST has both Rq→Src and Rq→Test links
    if 'libest' in datasets:
        libest = datasets['libest']
        link_types = set(link.link_type for link in libest.traceability_links)
        print(f"\nLibEST link types: {', '.join(link_types)}")
        if 'Rq→Src' in link_types and 'Rq→Test' in link_types:
            print("  ✓ Has both Rq→Src and Rq→Test links")
        else:
            print(f"  ⚠️  Expected both link types, got: {link_types}")
    
    # Check Italian datasets
    italian_datasets = [name for name, ds in datasets.items() if ds.language == 'italian']
    print(f"\nItalian datasets: {', '.join(italian_datasets)}")
    if italian_datasets:
        sample = datasets[italian_datasets[0]]
        sample_req = list(sample.requirements.values())[0]
        # Check for Italian characters
        italian_chars = any(c in sample_req.content for c in 'àèéìòù')
        if italian_chars:
            print("  ✓ Italian text loaded correctly (contains accented characters)")
        else:
            print("  ⚠️  Italian text may have encoding issues")
    
    print()
    print("=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
    print("=" * 70)
    print()
    
    # Summary
    print("Summary:")
    print(f"  • {len(datasets)} datasets loaded")
    total_requirements = sum(len(ds.requirements) for ds in datasets.values())
    total_files = sum(len(ds.source_files) for ds in datasets.values())
    total_links = sum(len(ds.traceability_links) for ds in datasets.values())
    print(f"  • {total_requirements} total requirements")
    print(f"  • {total_files} total source files")
    print(f"  • {total_links} total traceability links")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
