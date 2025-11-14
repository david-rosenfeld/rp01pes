"""
Dataset loading for COMET replication package.

This module provides functions to load and parse COMET datasets, including
requirements, source code, and traceability links.
"""

from pathlib import Path
from typing import Dict, Optional, List
import logging

from .models import Dataset, Requirement, SourceFile
from .ground_truth import parse_ground_truth_file, validate_links, merge_duplicate_links
from ..core.exceptions import DatasetError


logger = logging.getLogger(__name__)


# Dataset metadata - structure and configuration for each COMET dataset
DATASET_METADATA = {
    'albergate': {
        'name': 'Albergate',
        'language': 'italian',
        'requirements_dir': 'requirements',
        'source_dir': 'source_code',
        'ground_truth_file': 'ground.txt',
        'link_type': 'Rq→Src',
        'source_extension': '.java',
        'req_count': 17  # Expected count for validation
    },
    'ebt': {
        'name': 'EBT',
        'language': 'english',
        'requirements_file': 'requirements.txt',  # Single file, not directory
        'source_dir': 'source_code',
        'ground_truth_file': 'code_ground.txt',
        'link_type': 'Rq→Src',
        'source_extension': '.java',
        'req_count': 41
    },
    'libest': {
        'name': 'LibEST',
        'language': 'english',
        'requirements_dir': 'requirements',
        'source_dir': 'source_code',
        'ground_truth_files': ['req_to_code_ground.txt', 'req_to_test_ground.txt'],
        'link_types': ['Rq→Src', 'Rq→Test'],
        'source_extension': '.c',
        'req_count': 52
    },
    'etour': {
        'name': 'eTOUR',
        'language': 'english',
        'requirements_dir': 'use_cases',  # Use cases, not requirements
        'source_dir': 'source_code',
        'ground_truth_file': 'ground.txt',
        'link_type': 'UC→Src',
        'source_extension': '.java',
        'req_count': 89
    },
    'smos': {
        'name': 'SMOS',
        'language': 'italian',
        'requirements_dir': 'use_cases',  # Use cases, not requirements
        'source_dir': 'source_code',
        'ground_truth_file': 'ground.txt',
        'link_type': 'UC→Src',
        'source_extension': '.java',
        'req_count': 85
    },
    'itrust': {
        'name': 'iTrust',
        'language': 'english',
        'requirements_dir': 'use_cases',  # Use cases, not requirements
        'source_dir': 'source_code',
        'ground_truth_file': 'ground.txt',
        'link_type': 'UC→Src',
        'source_extension': '.java',
        'req_count': 35
    }
}


def load_dataset(name: str, config: Dict) -> Dataset:
    """
    Load a COMET dataset by name.
    
    Args:
        name: Dataset name (case-insensitive: 'albergate', 'ebt', 'libest', etc.)
        config: Configuration dictionary containing:
            - base_path: Base directory containing all datasets
            - Additional dataset-specific config (optional)
    
    Returns:
        Dataset object with loaded requirements, source files, and links
    
    Raises:
        DatasetError: If dataset cannot be loaded
    
    Example:
        >>> dataset = load_dataset('albergate', {'base_path': './datasets/'})
        >>> print(f"Loaded {len(dataset.requirements)} requirements")
    """
    name_lower = name.lower()
    
    if name_lower not in DATASET_METADATA:
        available = ', '.join(DATASET_METADATA.keys())
        raise DatasetError(
            f"Unknown dataset: {name}. Available datasets: {available}"
        )
    
    metadata = DATASET_METADATA[name_lower]
    base_path = Path(config.get('base_path', './datasets'))
    dataset_path = base_path / metadata['name']
    
    if not dataset_path.exists():
        raise DatasetError(
            f"Dataset directory not found: {dataset_path}\n"
            f"Make sure datasets are downloaded to {base_path}"
        )
    
    logger.info(f"Loading dataset: {metadata['name']} from {dataset_path}")
    
    # Create dataset object
    dataset = Dataset(
        name=metadata['name'],
        base_path=dataset_path,
        language=metadata['language'],
        metadata=metadata
    )
    
    # Load requirements
    if 'requirements_file' in metadata:
        # Single file format (like EBT)
        req_file = dataset_path / metadata['requirements_file']
        dataset.requirements = _load_requirements_from_file(req_file, metadata['language'])
    else:
        # Directory format (most datasets)
        dataset.requirements = _load_requirements(
            dataset_path / metadata['requirements_dir'],
            metadata['language']
        )
    
    logger.info(f"Loaded {len(dataset.requirements)} requirements")
    
    # Load source files
    source_dirs = metadata.get('source_dir', 'code')
    if not isinstance(source_dirs, list):
        source_dirs = [source_dirs]
    
    for source_dir in source_dirs:
        source_path = dataset_path / source_dir
        if source_path.exists():
            source_files = _load_source_files(source_path)
            dataset.source_files.update(source_files)
    
    # Also check for 'test' directory (LibEST has this)
    test_path = dataset_path / 'test'
    if test_path.exists():
        test_files = _load_source_files(test_path)
        dataset.source_files.update(test_files)
    
    logger.info(f"Loaded {len(dataset.source_files)} source files")
    
    # Load traceability links
    ground_truth_files = metadata.get('ground_truth_files', [metadata.get('ground_truth_file')])
    link_types = metadata.get('link_types', [metadata.get('link_type', 'Rq→Src')])
    
    if not isinstance(ground_truth_files, list):
        ground_truth_files = [ground_truth_files]
    if not isinstance(link_types, list):
        link_types = [link_types]
    
    all_links = []
    for gt_file, link_type in zip(ground_truth_files, link_types):
        if gt_file:
            gt_path = dataset_path / gt_file
            if gt_path.exists():
                links = parse_ground_truth_file(gt_path, link_type)
                all_links.extend(links)
            else:
                logger.warning(f"Ground truth file not found: {gt_path}")
    
    # Merge duplicate links
    all_links = merge_duplicate_links(all_links)
    
    # Validate links
    available_requirements = set(dataset.requirements.keys())
    available_files = set(dataset.source_files.keys())
    
    valid_links, warnings = validate_links(all_links, available_requirements, available_files)
    
    for warning in warnings:
        logger.warning(warning)
    
    dataset.traceability_links = valid_links
    
    logger.info(f"Loaded {len(dataset.traceability_links)} valid traceability links "
                f"({len(all_links) - len(valid_links)} invalid)")
    
    # Validation check
    expected_count = metadata.get('req_count')
    actual_count = len(dataset.requirements)
    if expected_count and actual_count != expected_count:
        logger.warning(
            f"Requirement count mismatch for {metadata['name']}: "
            f"expected {expected_count}, got {actual_count}"
        )
    
    return dataset


def _load_requirements(requirements_dir: Path, language: str) -> Dict[str, Requirement]:
    """
    Load all requirement files from a directory.
    
    Args:
        requirements_dir: Directory containing requirement .txt files
        language: Language of the requirements
    
    Returns:
        Dictionary mapping requirement IDs to Requirement objects
    """
    requirements = {}
    
    if not requirements_dir.exists():
        logger.warning(f"Requirements directory not found: {requirements_dir}")
        return requirements
    
    # Find all .txt or .TXT files
    req_files = list(requirements_dir.glob('*.txt')) + list(requirements_dir.glob('*.TXT'))
    
    for req_file in req_files:
        try:
            # Read file content
            with open(req_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Extract requirement ID from filename (remove .txt extension)
            req_id = req_file.stem
            
            # Create Requirement object
            req = Requirement(
                req_id=req_id,
                file_path=req_file,
                content=content,
                language=language
            )
            
            requirements[req_id] = req
            
        except Exception as e:
            logger.error(f"Failed to load requirement {req_file.name}: {e}")
    
    return requirements


def _load_requirements_from_file(file_path: Path, language: str) -> Dict[str, Requirement]:
    """
    Load requirements from a single tab-separated file.
    
    Format: RQ<id>\t<requirement text>
    
    Args:
        file_path: Path to requirements file
        language: Language of the requirements
    
    Returns:
        Dictionary mapping requirement IDs to Requirement objects
    """
    requirements = {}
    
    if not file_path.exists():
        logger.warning(f"Requirements file not found: {file_path}")
        return requirements
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Split on tab
                parts = line.split('\t', 1)
                if len(parts) != 2:
                    logger.warning(f"Malformed line {line_num} in {file_path.name}")
                    continue
                
                req_id, content = parts
                
                # Create Requirement object
                req = Requirement(
                    req_id=req_id,
                    file_path=file_path,
                    content=content,
                    language=language
                )
                
                requirements[req_id] = req
        
        logger.info(f"Loaded {len(requirements)} requirements from {file_path.name}")
        
    except Exception as e:
        logger.error(f"Failed to load requirements from {file_path}: {e}")
    
    return requirements


def _load_source_files(source_dir: Path) -> Dict[str, SourceFile]:
    """
    Load all source files from a directory.
    
    Args:
        source_dir: Directory containing source code files
    
    Returns:
        Dictionary mapping file names to SourceFile objects
    """
    source_files = {}
    
    if not source_dir.exists():
        logger.warning(f"Source directory not found: {source_dir}")
        return source_files
    
    # Find all source files (common extensions)
    extensions = ['.java', '.c', '.cpp', '.h', '.py', '.js']
    
    for ext in extensions:
        for source_file in source_dir.glob(f'*{ext}'):
            try:
                # Create SourceFile object (content loaded lazily)
                src = SourceFile(
                    file_name=source_file.name,
                    file_path=source_file
                )
                
                source_files[source_file.name] = src
                
            except Exception as e:
                logger.error(f"Failed to load source file {source_file.name}: {e}")
    
    return source_files


def list_available_datasets(base_path: str = './datasets') -> List[str]:
    """
    List all available COMET datasets in the base path.
    
    Args:
        base_path: Base directory to search for datasets
    
    Returns:
        List of available dataset names
    """
    base = Path(base_path)
    available = []
    
    for dataset_name, metadata in DATASET_METADATA.items():
        dataset_path = base / metadata['name']
        if dataset_path.exists():
            available.append(dataset_name)
    
    return available
