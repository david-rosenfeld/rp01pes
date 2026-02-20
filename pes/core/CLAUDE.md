# CLAUDE.md - Core Infrastructure

## Scope

Foundation components: configuration, logging, exceptions, base classes.

## Status

All components complete. Modify with care.

## Components

| File | Purpose | Stability |
|------|---------|-----------|
| `config.py` | YAML/JSON configuration loading | Stable |
| `logging.py` | Experiment-aware logging | Stable |
| `exceptions.py` | Exception hierarchy | Stable |
| `base_experiment.py` | Experiment template | Stable |

## Exception Hierarchy

All exceptions inherit from `PESError`:
- `ConfigurationError` - config loading/validation
- `DatasetError` - dataset loading/processing
- `LLMError` - LLM integration
- `ExperimentError` - experiment execution
- `StorageError` - data storage
- `AnalysisError` - statistical analysis

Use the appropriate exception type. Do not raise generic exceptions.

## ConfigurationManager API

```python
config.get("section.key")           # Dot notation access
config.get("key", default_value)    # With default
config.get_section("section")       # Get entire section
config.has("section.key")           # Check existence
config.validate_required_sections() # Validation
```

Supports both file-based and dict-based initialization for testing.

## BaseExperiment Contract

Subclasses must implement:
- `get_description()` - Return human-readable description
- `run()` - Execute experiment, return results dict

Provided by base class:
- `execute()` - Wraps run() with timing, logging, error handling
- Automatic result storage to JSON
- Status tracking and logging

## Logging Patterns

```python
from pes.core.logging import get_logger
logger = get_logger(__name__, log_dir="logs")

logger.info("Message")
logger.experiment_start("PE01")
logger.experiment_end("PE01", status="success")
logger.llm_request("gpt-4", prompt_tokens=100)
```

## Modification Rules

- Maintain backwards compatibility with existing experiments
- Add new methods rather than changing signatures
- Test changes against all implemented experiments
