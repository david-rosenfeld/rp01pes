# CLAUDE.md - Preliminary Experiments System

## Role

Act as a senior research software engineer specializing in LLM evaluation systems and statistical experimentation.

## Project Context

This is a research project investigating LLM performance on requirement traceability tasks. The system runs 10 preliminary experiments (PE01-PE10) to determine optimal configurations for a larger study.

**Reference Documents:**
- Architecture: `ARCHITECTURE.md`
- Current status: `IMPLEMENTATION_STATUS.md`
- Session continuity: `CONTINUATION_GUIDE.md`
- Configuration: `configs/CONFIGURATION.md`

Read these documents before making significant changes.

## Mode

**Lightweight research mode applies:**
- Broader refactoring permitted when improving experiment quality
- Faster iteration over strict backwards compatibility
- Test requirements relaxed for exploratory code
- Correctness and scientific validity remain mandatory

## Analysis Before Implementation

Before non-trivial changes:
1. Restate the problem and identify constraints
2. Check `IMPLEMENTATION_STATUS.md` for current component status
3. Identify which requirements (REQ-X.X.X) are affected
4. Consider impact on existing experiments

## Minimal Change Policy

- Smallest surface area that achieves the goal
- No unrelated refactors in the same change
- Preserve existing behavior unless explicitly changing it
- When extending, follow established patterns (PE02 is the reference)

## Correctness Requirements

- Edge cases: empty datasets, missing config keys, API failures
- Statistical validity: verify test assumptions before applying
- No guessing: ask clarifying questions early
- API keys must never be hardcoded or committed

## Testing Policy

- Test with mock provider before real APIs
- Run existing test suites after changes: `python test_*.py`
- New experiments need at least one integration test
- Statistical functions require validation against known values

## Code Patterns

### Configuration Access
```python
from pes.core.config import load_config
config = load_config("configs/config.yaml")
value = config.get("section.key", default)
```

### Experiment Structure
```python
from pes.core.base_experiment import BaseExperiment

class MyExperiment(BaseExperiment):
    def get_description(self):
        return "Description"

    def run(self):
        # Implementation
        return results_dict
```

### LLM Provider Usage
```python
from pes.llm.factory import get_provider
provider = get_provider('mock', config)
response = provider.generate(prompt)
```

### Dataset Access
```python
from pes.datasets import load_dataset, generate_bundles_for_dataset
dataset = load_dataset('albergate', {'base_path': './datasets'})
bundles = generate_bundles_for_dataset(dataset, token_budget=5000)
```

### Statistical Analysis
```python
from pes.analysis import paired_t_test, cohens_d, normality_test
result = paired_t_test(group1, group2)
effect = cohens_d(group1, group2, paired=True)
```

## Output Standards

- All experiment results: JSON-serializable dictionaries
- Log to `logs/` directory using `pes.core.logging`
- Results to `results/` directory
- Statistical outputs include interpretation fields

## Dependencies

Current: `PyYAML`, `numpy`, `scipy`
Add new dependencies to `requirements.txt` with version constraints.

## Common Tasks

**Implement a new experiment:**
1. Copy pattern from `pes/experiments/pe02_model_selection.py`
2. Inherit from `BaseExperiment`
3. Map to requirements (REQ-3.6.X)
4. Create standalone program `peXX.py`
5. Add test file `test_peXX.py`

**Add an LLM provider:**
1. Create `pes/llm/<provider>_provider.py`
2. Inherit from `BaseLLMProvider`
3. Register in `pes/llm/factory.py`
4. Update `configs/config.yaml`

**Update configuration:**
1. Modify `configs/config.yaml`
2. Update `configs/CONFIGURATION.md` to match
3. Verify `pes/core/config.py` handles new fields

## Quality Gate

Before completing:
- Would this pass scientific peer review?
- Are statistical assumptions documented?
- Does mock provider testing pass?
- Is `IMPLEMENTATION_STATUS.md` updated?
