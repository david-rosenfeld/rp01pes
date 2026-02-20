# CLAUDE.md - Dataset Management

## Scope

COMET dataset loading, parsing, and traceability bundle generation.

## Status

Complete. All 6 datasets supported.

## Reference

See `README.md` in this directory for detailed usage guide.

## Supported Datasets

| Key | Language | Type | Status |
|-----|----------|------|--------|
| albergate | Italian | Rq | Complete |
| ebt | English | Rq | Complete |
| libest | English | Rq | Complete |
| etour | English | UC | Complete |
| smos | Italian | UC | Complete |
| itrust | English | UC | Partial* |

*iTrust has nested structure not fully indexed.

## Public API

```python
from pes.datasets import (
    load_dataset,
    generate_bundles_for_dataset,
    format_bundle_text,
    calculate_bundle_statistics
)
```

## Data Models

```python
Dataset          # Container for requirements, files, links
Requirement      # Single requirement/use case
SourceFile       # Source code file with content
TraceabilityLink # Ground truth link (requirement -> file)
TraceabilityBundle # LLM-ready prompt data
```

## Bundle Generation

```python
bundles = generate_bundles_for_dataset(
    dataset,
    token_budget=5000  # Optional: truncate to fit
)

for req_id, bundle in bundles.items():
    prompt_text = format_bundle_text(bundle)
```

## Text Encoding

- All files read with UTF-8 encoding
- Italian text (Albergate, SMOS) handled correctly
- Invalid characters replaced, not errored

## Modification Rules

- Maintain backwards compatibility with experiments using datasets
- New dataset formats require new loader functions
- Test with actual COMET data files
- Token estimation uses character-based approximation (no external libs)
