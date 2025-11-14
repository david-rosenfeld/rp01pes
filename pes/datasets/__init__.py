"""
Dataset management for COMET replication package.

This module provides functionality for loading and managing the six COMET
datasets used in the preliminary experiments.
"""

from .models import (
    Dataset,
    Requirement,
    SourceFile,
    TraceabilityLink,
    TraceabilityBundle
)

from .loader import (
    load_dataset,
    list_available_datasets,
    DATASET_METADATA
)

from .traceability import (
    generate_bundle,
    generate_bundles_for_dataset,
    format_bundle_text,
    get_bundle_statistics
)

from .ground_truth import (
    parse_ground_truth_file,
    validate_links,
    merge_duplicate_links
)


__all__ = [
    # Data models
    'Dataset',
    'Requirement',
    'SourceFile',
    'TraceabilityLink',
    'TraceabilityBundle',
    
    # Loading functions
    'load_dataset',
    'list_available_datasets',
    'DATASET_METADATA',
    
    # Traceability functions
    'generate_bundle',
    'generate_bundles_for_dataset',
    'format_bundle_text',
    'get_bundle_statistics',
    
    # Ground truth functions
    'parse_ground_truth_file',
    'validate_links',
    'merge_duplicate_links',
]