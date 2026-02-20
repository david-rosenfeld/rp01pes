# CLAUDE.md - PES Package

## Scope

Main Python package for the Preliminary Experiments System.

## Package Structure

```
pes/
├── core/        # Infrastructure (config, logging, base classes)
├── llm/         # LLM provider abstraction
├── datasets/    # COMET dataset loading
├── experiments/ # PE01-PE10 implementations
├── analysis/    # Statistical analysis functions
├── agents/      # Agentic system integration (TODO)
├── storage/     # Data persistence (TODO)
└── utils/       # Shared utilities (TODO)
```

## Import Conventions

Use relative imports within subpackages:
```python
from ..core.base_experiment import BaseExperiment
from ..llm.factory import get_provider
```

Use absolute imports from outside pes:
```python
from pes.core.config import load_config
from pes.datasets import load_dataset
```

## Module Boundaries

- `core/` provides infrastructure; other modules depend on it
- `llm/` is independent except for core exceptions
- `datasets/` is independent except for core exceptions
- `analysis/` is independent; uses only numpy/scipy
- `experiments/` integrates all other modules

## Adding New Modules

1. Create subdirectory with `__init__.py`
2. Export public API from `__init__.py`
3. Add CLAUDE.md with module-specific rules
4. Update `IMPLEMENTATION_STATUS.md`

## Status References

See `../IMPLEMENTATION_STATUS.md` for:
- Which modules are complete vs TODO
- Which experiments are implemented
- Current test coverage
