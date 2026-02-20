# CLAUDE.md - Experiments

## Scope

Implementations of PE01-PE10 preliminary experiments.

## Status

| Experiment | Status | Reference |
|------------|--------|-----------|
| PE01 Language Effect | Complete | REQ-3.6.1 |
| PE02 Model Selection | Complete | REQ-3.6.2 |
| PE03 Agent Selection | Stub | REQ-3.6.3 |
| PE04 Temperature Opt | Complete | REQ-3.6.4 |
| PE05 Max Token | Complete | REQ-3.6.5 |
| PE06 Stop Sequence | Stub | REQ-3.6.6 |
| PE07 Prompt Strategy | Complete | REQ-3.6.7 |
| PE08 Control Condition | Stub | REQ-3.6.8 |
| PE09 Token Budget | Complete | REQ-3.6.9 |
| PE10 Power Analysis | Complete | REQ-3.6.10 |

## Reference Implementation

**PE02 (`pe02_model_selection.py`) is the canonical example.**

Study its structure before implementing new experiments.

## Implementation Pattern

```python
from ..core.base_experiment import BaseExperiment
from ..core.exceptions import ExperimentError

class MyExperiment(BaseExperiment):
    def get_description(self):
        return "Human-readable description"

    def run(self):
        # 1. Load configuration
        config = self.config.get_section("experiments.my_experiment")

        # 2. Load data (datasets, models)

        # 3. Execute experiment logic

        # 4. Perform statistical analysis

        # 5. Generate recommendations

        return {
            "status": "complete",
            "results": {...},
            "recommendations": {...}
        }
```

## Requirements Mapping

Each experiment maps to a requirements section (REQ-3.6.X).
Verify implementation covers all sub-requirements.

## Completing Stub Experiments

Stubs contain:
- Class structure
- Configuration loading skeleton
- TODO comments with implementation steps

To complete:
1. Read corresponding REQ-3.6.X requirements
2. Follow TODO items in the code
3. Use completed experiments as reference
4. Test with mock provider first
5. Create test file `test_peXX.py`
6. Update `IMPLEMENTATION_STATUS.md`

## Standalone Programs

Each experiment has `peXX.py` in project root:
```bash
python pe02.py configs/config.yaml
```

Follow this pattern for consistency.

## Statistical Integration

Use `pes.analysis` for statistical functions:
```python
from ..analysis import paired_t_test, cohens_d, one_way_anova
```

Do not implement statistical tests inline.
