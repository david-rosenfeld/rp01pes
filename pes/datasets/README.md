# Dataset Management Module - User Guide

## Overview

The dataset management module provides comprehensive functionality for loading, parsing, and working with the six COMET datasets used in the Preliminary Experiments System.

## Quick Start

```python
from pes.datasets import load_dataset, generate_bundles_for_dataset

# Load a dataset
dataset = load_dataset('albergate', {'base_path': './datasets'})

print(f"Loaded: {dataset.name}")
print(f"Requirements: {len(dataset.requirements)}")
print(f"Source files: {len(dataset.source_files)}")
print(f"Links: {len(dataset.traceability_links)}")

# Generate traceability bundles
bundles = generate_bundles_for_dataset(dataset, token_budget=5000)

# Access a specific bundle
bundle = bundles['F-GES-01']
print(f"Bundle tokens: {bundle.token_count}")
print(f"Linked files: {len(bundle.linked_files)}")
```

## Available Datasets

| Dataset | Language | Requirements | Link Type | Source Language |
|---------|----------|--------------|-----------|-----------------|
| **Albergate** | Italian | 17 | Rq→Src | Java |
| **EBT** | English | 41 | Rq→Src | Java |
| **LibEST** | English | 52 | Rq→Src, Rq→Test | C |
| **eTOUR** | English | 89 (UC) | UC→Src | Java |
| **SMOS** | Italian | 85 (UC) | UC→Src | Java |
| **iTrust** | English | 35 (UC) | UC→Src | Java |

## Key Components

### 1. Dataset Loader

```python
from pes.datasets import load_dataset, list_available_datasets

# List what's available
available = list_available_datasets('./datasets')
print(f"Available: {', '.join(available)}")

# Load specific dataset
config = {'base_path': './datasets'}
dataset = load_dataset('libest', config)
```

### 2. Data Models

**Dataset**: Complete dataset with requirements, source files, and links
```python
dataset.name                    # "LibEST"
dataset.language                # "english"
dataset.requirements            # Dict[str, Requirement]
dataset.source_files            # Dict[str, SourceFile]
dataset.traceability_links      # List[TraceabilityLink]
```

**Requirement**: A single requirement
```python
req = dataset.requirements['RQ4']
req.req_id                      # "RQ4"
req.content                     # Full text
req.file_path                   # Path to file
req.language                    # "english"
```

**SourceFile**: A source code file (lazy-loaded)
```python
src = dataset.source_files['est_client.c']
src.file_name                   # "est_client.c"
src.content                     # File content (loaded on access)
src.extension                   # ".c"
```

**TraceabilityLink**: Link between requirement and files
```python
link.source_id                  # "RQ4"
link.target_files               # ["est_client.c", "est_server.c"]
link.link_type                  # "Rq→Src"
```

### 3. Traceability Bundles

```python
from pes.datasets import (
    generate_bundle,
    generate_bundles_for_dataset,
    format_bundle_text,
    get_bundle_statistics
)

# Generate bundles for entire dataset
bundles = generate_bundles_for_dataset(
    dataset,
    token_budget=5000,  # Optional limit
    only_requirements=['RQ4', 'RQ5']  # Optional filter
)

# Generate single bundle
req = dataset.requirements['RQ4']
links = dataset.get_links_for_requirement('RQ4')
bundle = generate_bundle(req, links, dataset.source_files, token_budget=5000)

# Format for LLM
formatted_text = format_bundle_text(bundle, include_metadata=True)

# Get statistics
stats = get_bundle_statistics(bundles)
print(f"Average tokens: {stats['avg_token_count']:.0f}")
print(f"Truncated: {stats['truncated_count']}")
```

## Usage in Experiments

### Example: PE01 (Language Effect)

```python
from pes.datasets import load_dataset
from pes.core.base_experiment import BaseExperiment

class LanguageEffectExperiment(BaseExperiment):
    def run(self):
        # Load Italian dataset
        albergate = load_dataset('albergate', self.config['datasets'])
        
        # Get Italian requirements
        italian_requirements = list(albergate.requirements.values())
        
        # Generate bundles
        bundles = generate_bundles_for_dataset(albergate)
        
        # Use bundles in LLM prompts...
        for req_id, bundle in bundles.items():
            prompt = format_bundle_text(bundle)
            # Send to LLM...
```

### Example: Accessing Specific Requirements

```python
# Load dataset
dataset = load_dataset('libest', {'base_path': './datasets'})

# Get specific requirement
req = dataset.requirements['RQ4']
print(f"Requirement: {req.content[:100]}...")

# Find its linked files
links = dataset.get_links_for_requirement('RQ4')
print(f"Linked to {len(links)} traceability links")

for link in links:
    print(f"  Files: {', '.join(link.target_files)}")
```

## Token Budgeting

The bundle generator supports token budgeting to fit within LLM context windows:

```python
# No budget - include everything
bundles_unlimited = generate_bundles_for_dataset(dataset)

# With budget - truncate as needed
bundles_limited = generate_bundles_for_dataset(dataset, token_budget=5000)

# Check what was truncated
for req_id, bundle in bundles_limited.items():
    if bundle.truncated:
        print(f"{req_id}: Truncated from {bundle.token_count} tokens")
```

**Token Estimation**: Currently uses simple approximation (1 token ≈ 4 characters). For more accurate counting, integrate `tiktoken` or similar library.

## Ground Truth Files

The module handles different ground truth formats:

**Format 1** (Albergate, SMOS, iTrust, eTOUR):
```
REQ1.txt source.java
REQ2.txt module/file.java
```

**Format 2** (LibEST):
```
REQ1.txt file1.c file2.c file3.c
```

**Format 3** (EBT - tab-separated):
```
RQ100	Requirement text here...
RQ101	Another requirement...
```

## Configuration

Add dataset configuration to `configs/config.yaml`:

```yaml
datasets:
  base_path: "./datasets"
  
  # Token budget (from PE09 results)
  token_budget:
    requirement: 2400
    traceability: 2800
    total: 5200
```

## Testing

Run the test script to verify all datasets load correctly:

```bash
python test_datasets.py
```

Expected output:
- All 6 datasets load successfully
- ~366 total requirements
- ~356 total source files
- ~163 traceability links

## Error Handling

The module handles common issues gracefully:

**Missing files**: Logs warnings but continues
```
Link target not found: RQ4 → missing_file.c
```

**Broken links**: Validates and filters invalid links
```
Link source not found: INVALID_REQ
```

**Encoding issues**: Uses `errors='replace'` for Italian text
```python
with open(file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
```

## Limitations & Future Improvements

### Current Limitations

1. **Token counting**: Simple approximation (1 token ≈ 4 chars)
   - Future: Integrate `tiktoken` for accurate counting

2. **Source file paths**: Some datasets have nested directories
   - Current: Logs warnings for broken paths
   - Future: Recursive directory traversal

3. **Requirements parsing**: Basic text extraction
   - Future: Parse structured metadata fields

### Planned Enhancements

- [ ] More accurate token counting (tiktoken integration)
- [ ] Caching for frequently accessed bundles
- [ ] Parallel loading for large datasets
- [ ] Export bundles to JSON/pickle for reuse
- [ ] Support for custom dataset formats

## Performance Considerations

**Lazy Loading**: Source file content is loaded only when accessed
```python
# This doesn't load content yet
src = dataset.source_files['large_file.java']

# Content loaded here (and cached)
content = src.content
```

**Memory Usage**: For typical datasets (~50 requirements, ~50 files):
- Requirements: ~100KB
- Source files (lazy): 0KB initial, ~1-2MB when accessed
- Bundles: ~2-5MB depending on configuration

## Troubleshooting

**Problem**: Dataset not found
```
DatasetError: Dataset directory not found: ./datasets/Albergate
```
**Solution**: Ensure datasets are in correct location. Check `base_path` in config.

**Problem**: No requirements loaded
```
Warning: Requirements directory not found: datasets/EBT/requirements
```
**Solution**: Check dataset structure. EBT uses a single file, not directory.

**Problem**: Italian text shows strange characters
```
Warning: Italian text may have encoding issues
```
**Solution**: Already handled with `encoding='utf-8', errors='replace'`. No action needed.

## API Reference

See individual module docstrings for detailed API documentation:
- `pes/datasets/loader.py` - Dataset loading functions
- `pes/datasets/models.py` - Data model classes
- `pes/datasets/traceability.py` - Bundle generation
- `pes/datasets/ground_truth.py` - Ground truth parsing

## Questions?

For implementation details, see:
- `ARCHITECTURE.md` - System design
- `IMPLEMENTATION_STATUS.md` - Current status
- Code comments and docstrings
