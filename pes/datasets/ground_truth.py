"""
Ground truth file parsing for COMET datasets.

This module handles parsing of ground.txt files that define traceability links
between requirements and source files.
"""

from pathlib import Path
from typing import List, Tuple
import logging

from .models import TraceabilityLink


logger = logging.getLogger(__name__)


def parse_ground_truth_file(file_path: Path, link_type: str = "Rq→Src") -> List[TraceabilityLink]:
    """
    Parse a ground truth file and return traceability links.
    
    Ground truth files have different formats across datasets:
    - Albergate format: "REQ.txt FILE.java" (one file per line)
    - LibEST format: "REQ.txt FILE1.c FILE2.c FILE3.c" (multiple files per line)
    
    Args:
        file_path: Path to the ground truth file
        link_type: Type of link (e.g., 'Rq→Src', 'Rq→Test', 'UC→Src')
    
    Returns:
        List of TraceabilityLink objects
    
    Raises:
        FileNotFoundError: If ground truth file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {file_path}")
    
    links = []
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse line: first token is requirement ID, rest are file names
            tokens = line.split()
            
            if len(tokens) < 2:
                logger.warning(f"Malformed line {line_num} in {file_path.name}: {line}")
                continue
            
            req_id = tokens[0]
            target_files = tokens[1:]
            
            # Some datasets include .txt extension in ground truth, others don't
            # Normalize by removing .txt if present
            if req_id.endswith('.txt'):
                req_id = req_id[:-4]
            
            link = TraceabilityLink(
                source_id=req_id,
                target_files=target_files,
                link_type=link_type
            )
            
            links.append(link)
    
    logger.info(f"Parsed {len(links)} traceability links from {file_path.name}")
    
    return links


def validate_links(links: List[TraceabilityLink], 
                   available_requirements: set,
                   available_files: set) -> Tuple[List[TraceabilityLink], List[str]]:
    """
    Validate traceability links against available requirements and files.
    
    Args:
        links: List of traceability links to validate
        available_requirements: Set of available requirement IDs
        available_files: Set of available source file names
    
    Returns:
        Tuple of (valid_links, warnings)
        - valid_links: Links that passed validation
        - warnings: List of warning messages for invalid links
    """
    valid_links = []
    warnings = []
    
    for link in links:
        # Check if source requirement exists
        req_id = link.source_id
        req_id_with_txt = f"{req_id}.txt"
        
        if req_id not in available_requirements and req_id_with_txt not in available_requirements:
            warnings.append(f"Link source not found: {req_id}")
            continue
        
        # Check if target files exist
        valid_targets = []
        for target_file in link.target_files:
            if target_file in available_files:
                valid_targets.append(target_file)
            else:
                warnings.append(f"Link target not found: {req_id} → {target_file}")
        
        # Keep link if at least one target is valid
        if valid_targets:
            link.target_files = valid_targets
            valid_links.append(link)
        else:
            warnings.append(f"Link has no valid targets: {req_id}")
    
    return valid_links, warnings


def merge_duplicate_links(links: List[TraceabilityLink]) -> List[TraceabilityLink]:
    """
    Merge duplicate links for the same requirement.
    
    Some ground truth files may have multiple lines for the same requirement.
    This function merges them into single links with all target files.
    
    Args:
        links: List of traceability links (may contain duplicates)
    
    Returns:
        List of merged traceability links (no duplicates)
    """
    # Group links by source ID
    link_map = {}
    
    for link in links:
        source_id = link.source_id
        
        if source_id in link_map:
            # Merge target files (avoiding duplicates)
            existing_targets = set(link_map[source_id].target_files)
            new_targets = set(link.target_files)
            link_map[source_id].target_files = list(existing_targets | new_targets)
        else:
            link_map[source_id] = link
    
    return list(link_map.values())
