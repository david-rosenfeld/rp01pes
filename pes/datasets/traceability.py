"""
Traceability bundle generation for LLM prompts.

This module generates traceability bundles that combine requirements with
their linked source files, formatted for consumption by LLMs.
"""

from typing import Dict, List, Optional
import logging

from .models import Dataset, Requirement, SourceFile, TraceabilityBundle, TraceabilityLink


logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    Uses a simple approximation: 1 token ≈ 4 characters.
    This is rough but sufficient for initial implementation.
    
    For more accurate counting, integrate tiktoken or similar library later.
    
    Args:
        text: Text to estimate tokens for
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def generate_bundle(requirement: Requirement,
                   links: List[TraceabilityLink],
                   source_files: Dict[str, SourceFile],
                   token_budget: Optional[int] = None) -> TraceabilityBundle:
    """
    Generate a traceability bundle for a single requirement.
    
    Args:
        requirement: The requirement at the center of the bundle
        links: Traceability links for this requirement
        source_files: Available source files (dict mapping filename to SourceFile)
        token_budget: Optional maximum token count for the bundle
    
    Returns:
        TraceabilityBundle containing the requirement and linked files
    """
    # Collect all linked files
    linked_file_names = set()
    for link in links:
        linked_file_names.update(link.target_files)
    
    # Get actual SourceFile objects
    linked_files = []
    for file_name in linked_file_names:
        if file_name in source_files:
            linked_files.append(source_files[file_name])
        else:
            logger.warning(f"Linked file not found: {file_name} for requirement {requirement.req_id}")
    
    # Calculate initial token count
    req_tokens = estimate_tokens(requirement.content)
    file_tokens = sum(estimate_tokens(f.content) for f in linked_files)
    total_tokens = req_tokens + file_tokens
    
    truncated = False
    
    # Apply token budget if specified
    if token_budget and total_tokens > token_budget:
        logger.info(f"Bundle for {requirement.req_id} exceeds budget "
                   f"({total_tokens} > {token_budget}), truncating files")
        
        # Keep requirement, truncate files
        available_tokens = token_budget - req_tokens
        
        if available_tokens <= 0:
            # Can't fit anything, return empty bundle
            logger.warning(f"Requirement alone exceeds budget for {requirement.req_id}")
            linked_files = []
            total_tokens = req_tokens
            truncated = True
        else:
            # Truncate files to fit budget
            # Strategy: Include files until we run out of budget
            kept_files = []
            used_tokens = req_tokens
            
            for src_file in linked_files:
                file_tokens = estimate_tokens(src_file.content)
                if used_tokens + file_tokens <= token_budget:
                    kept_files.append(src_file)
                    used_tokens += file_tokens
                else:
                    # Could truncate individual file here, for now just skip
                    logger.debug(f"Skipping {src_file.file_name} to fit budget")
                    truncated = True
            
            linked_files = kept_files
            total_tokens = used_tokens
    
    bundle = TraceabilityBundle(
        requirement=requirement,
        linked_files=linked_files,
        token_count=total_tokens,
        truncated=truncated
    )
    
    return bundle


def generate_bundles_for_dataset(dataset: Dataset,
                                 token_budget: Optional[int] = None,
                                 only_requirements: Optional[List[str]] = None) -> Dict[str, TraceabilityBundle]:
    """
    Generate traceability bundles for all requirements in a dataset.
    
    Args:
        dataset: The dataset to generate bundles for
        token_budget: Optional maximum token count per bundle
        only_requirements: Optional list of requirement IDs to generate bundles for
                          (if None, generates for all requirements)
    
    Returns:
        Dictionary mapping requirement IDs to TraceabilityBundle objects
    """
    bundles = {}
    
    # Determine which requirements to process
    if only_requirements:
        requirements_to_process = {req_id: req for req_id, req in dataset.requirements.items()
                                   if req_id in only_requirements}
    else:
        requirements_to_process = dataset.requirements
    
    logger.info(f"Generating bundles for {len(requirements_to_process)} requirements "
                f"from {dataset.name}")
    
    for req_id, requirement in requirements_to_process.items():
        # Get links for this requirement
        links = dataset.get_links_for_requirement(req_id)
        
        # Generate bundle
        bundle = generate_bundle(
            requirement=requirement,
            links=links,
            source_files=dataset.source_files,
            token_budget=token_budget
        )
        
        bundles[req_id] = bundle
    
    # Log statistics
    total_bundles = len(bundles)
    truncated_count = sum(1 for b in bundles.values() if b.truncated)
    empty_count = sum(1 for b in bundles.values() if len(b.linked_files) == 0)
    
    logger.info(f"Generated {total_bundles} bundles: "
                f"{truncated_count} truncated, {empty_count} with no files")
    
    return bundles


def format_bundle_text(bundle: TraceabilityBundle,
                      include_metadata: bool = True) -> str:
    """
    Format a traceability bundle as text for LLM consumption.
    
    Args:
        bundle: The bundle to format
        include_metadata: Whether to include metadata headers
    
    Returns:
        Formatted text string ready for LLM prompts
    """
    parts = []
    
    if include_metadata:
        parts.append(f"=== Requirement: {bundle.requirement.req_id} ===")
        parts.append(f"Language: {bundle.requirement.language}")
        parts.append(f"Linked Files: {len(bundle.linked_files)}")
        parts.append("")
    
    # Add requirement content
    parts.append("--- Requirement Text ---")
    parts.append(bundle.requirement.content.strip())
    parts.append("")
    
    # Add linked source files
    if bundle.linked_files:
        parts.append("--- Linked Source Files ---")
        parts.append("")
        
        for src_file in bundle.linked_files:
            parts.append(f"=== File: {src_file.file_name} ===")
            parts.append(src_file.content.strip())
            parts.append("")
    else:
        parts.append("--- No Linked Source Files ---")
        parts.append("")
    
    if bundle.truncated:
        parts.append("⚠️  Note: This bundle was truncated to fit token budget.")
        parts.append("")
    
    return "\n".join(parts)


def get_bundle_statistics(bundles: Dict[str, TraceabilityBundle]) -> Dict:
    """
    Calculate statistics about a collection of bundles.
    
    Args:
        bundles: Dictionary of bundles
    
    Returns:
        Dictionary containing statistics
    """
    if not bundles:
        return {
            'total_bundles': 0,
            'avg_token_count': 0,
            'max_token_count': 0,
            'min_token_count': 0,
            'truncated_count': 0,
            'empty_bundles': 0,
            'avg_files_per_bundle': 0
        }
    
    token_counts = [b.token_count for b in bundles.values()]
    file_counts = [len(b.linked_files) for b in bundles.values()]
    
    stats = {
        'total_bundles': len(bundles),
        'avg_token_count': sum(token_counts) / len(token_counts),
        'max_token_count': max(token_counts),
        'min_token_count': min(token_counts),
        'truncated_count': sum(1 for b in bundles.values() if b.truncated),
        'empty_bundles': sum(1 for b in bundles.values() if len(b.linked_files) == 0),
        'avg_files_per_bundle': sum(file_counts) / len(file_counts)
    }
    
    return stats
