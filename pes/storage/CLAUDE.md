# CLAUDE.md - Data Storage

## Scope

Persistence layer for experiment results and intermediate data.

## Status

**TODO** - Not yet implemented.

Currently using direct JSON file writes from `BaseExperiment`.

## Planned Components

- Result storage with versioning
- Intermediate checkpoint saves
- Resume capability for long experiments
- Query interface for analysis

## Current Workaround

Results saved directly by `BaseExperiment.execute()`:
```python
results_path = f"results/{experiment_name}_{timestamp}.json"
```

## Implementation Guidelines

When implementing:

1. Maintain backwards compatibility with existing JSON format
2. Add metadata (timestamps, versions, configs)
3. Support incremental saves for long experiments
4. Enable result querying without loading full files
5. Consider SQLite for structured queries

## File Locations

- Results: `results/` directory
- Logs: `logs/` directory
- Checkpoints: `results/checkpoints/` (proposed)
