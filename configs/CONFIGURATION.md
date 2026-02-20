# Configuration File Reference

**File:** `config.yaml`
**Version:** 1.0
**Last Updated:** 2026-01-20

This document provides a detailed description of the configuration file structure for the Preliminary Experiments System (PES).

---

## Table of Contents

1. [Overview](#overview)
2. [File Format](#file-format)
3. [Top-Level Structure](#top-level-structure)
4. [Section: execution](#section-execution)
5. [Section: output](#section-output)
6. [Section: models](#section-models)
7. [Section: datasets](#section-datasets)
8. [Section: experiments](#section-experiments)
   - [language_effect (PE01)](#language_effect-pe01)
   - [model_selection (PE02)](#model_selection-pe02)
   - [agent_selection (PE03)](#agent_selection-pe03)
   - [temperature_optimization (PE04)](#temperature_optimization-pe04)
   - [max_token_determination (PE05)](#max_token_determination-pe05)
   - [stop_sequence (PE06)](#stop_sequence-pe06)
   - [prompt_strategy (PE07)](#prompt_strategy-pe07)
   - [control_condition (PE08)](#control_condition-pe08)
   - [token_budget (PE09)](#token_budget-pe09)
   - [power_analysis (PE10)](#power_analysis-pe10)
9. [Accessing Configuration in Code](#accessing-configuration-in-code)
10. [Requirements Traceability](#requirements-traceability)

---

## Overview

The configuration file controls all aspects of the Preliminary Experiments System, including:

- **Execution settings**: Logging, execution mode
- **Output settings**: Result directory and formats
- **Model configurations**: LLM provider settings and API credentials
- **Dataset configurations**: Paths to COMET datasets
- **Experiment configurations**: Parameters for each of the 10 preliminary experiments (PE01-PE10)

The configuration is externalized to allow changing parameters without modifying code, as required by REQ-3.1.

---

## File Format

The system supports two equivalent configuration formats:

| Format | Extensions | Specification |
|--------|------------|---------------|
| YAML | `.yaml`, `.yml` | YAML 1.2 |
| JSON | `.json` | RFC 8259 |

Both formats produce identical behavior (REQ-3.1.1.3). YAML is preferred for human readability.

**Example Loading:**
```python
from pes.core.config import load_config

config = load_config("configs/config.yaml")
# or
config = load_config("configs/config.json")
```

---

## Top-Level Structure

The configuration file has five top-level sections:

```yaml
execution:     # Runtime settings (REQ-3.1.3.4)
  ...

output:        # Output format settings (REQ-3.1.3.5)
  ...

models:        # LLM provider configurations (REQ-3.1.3.2)
  ...

datasets:      # Dataset paths and metadata (REQ-3.1.3.3)
  ...

experiments:   # Experiment-specific parameters (REQ-3.1.3.1)
  ...
```

---

## Section: execution

**Purpose:** Controls runtime behavior of the system.
**Requirement:** REQ-3.1.3.4 (Execution Configuration Section)

```yaml
execution:
  log_dir: "logs"
  log_level: "INFO"
  mode: "sequential"
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `log_dir` | string | No | `"logs"` | Directory path where log files are written. Created automatically if it doesn't exist. |
| `log_level` | string | No | `"INFO"` | Minimum logging level. Valid values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `mode` | string | No | `"sequential"` | Execution mode for running experiments. Valid values: `sequential`, `parallel`, `selective` |

### Execution Modes

| Mode | Description | Status |
|------|-------------|--------|
| `sequential` | Run experiments one after another in order | ✅ Implemented |
| `parallel` | Run independent experiments concurrently | ❌ Not implemented |
| `selective` | Run only specified experiments | ⚠️ Via individual scripts |

---

## Section: output

**Purpose:** Controls where and how results are saved.
**Requirement:** REQ-3.1.3.5 (Output Configuration Section)

```yaml
output:
  directory: "results"
  formats:
    - "json"
    - "csv"
    - "markdown"
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `directory` | string | No | `"results"` | Directory path where experiment results are saved. Created automatically if it doesn't exist. |
| `formats` | list | No | `["json"]` | Output formats to generate for results. |

### Supported Output Formats

| Format | Description | Status |
|--------|-------------|--------|
| `json` | Structured JSON files with full results | ✅ Implemented |
| `csv` | Tabular data export | ⚠️ Config only |
| `markdown` | Human-readable reports | ⚠️ Config only |
| `html` | Web-based reports | ❌ Not implemented |
| `pdf` | Printable reports | ❌ Not implemented |

---

## Section: models

**Purpose:** Defines LLM provider configurations with authentication and parameters.
**Requirement:** REQ-3.1.3.2 (Model Configuration Section)

```yaml
models:
  mock:
    provider: "mock"
    model: "mock-model-1.0"
    temperature: 0.7

  gpt4:
    provider: "openai"
    model: "gpt-4"
    api_key: "YOUR_OPENAI_API_KEY_HERE"
    temperature: 0.7
    max_tokens: 2000
    cost_per_1k_prompt_tokens: 0.03
    cost_per_1k_completion_tokens: 0.06
```

### Model Entry Structure

Each model is defined as a named entry under `models:`. The key becomes the model identifier.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | string | **Yes** | LLM provider type. Valid values: `mock`, `openai`, `anthropic`, `google` |
| `model` | string | **Yes** | Model identifier (provider-specific). Examples: `gpt-4`, `claude-sonnet-4`, `gemini-pro` |
| `api_key` | string | Conditional | API key for authentication. Required for real providers, not needed for `mock`. |
| `temperature` | float | No | Sampling temperature (0.0-2.0). Default varies by experiment. |
| `max_tokens` | integer | No | Maximum tokens in response. Default: provider determines. |
| `cost_per_1k_prompt_tokens` | float | No | Cost tracking: dollars per 1000 prompt tokens. |
| `cost_per_1k_completion_tokens` | float | No | Cost tracking: dollars per 1000 completion tokens. |

### Pre-configured Models

| Key | Provider | Model | Notes |
|-----|----------|-------|-------|
| `mock` | mock | mock-model-1.0 | Testing without API calls |
| `gpt4` | openai | gpt-4 | Requires API key |
| `gpt35` | openai | gpt-3.5-turbo | Requires API key |
| `claude_sonnet` | anthropic | claude-sonnet-4 | Requires API key |
| `gemini` | google | gemini-pro | Requires API key |

### Provider Implementation Status

| Provider | Status | SDK Required |
|----------|--------|--------------|
| `mock` | ✅ Implemented | None |
| `openai` | ❌ Not implemented | `openai` |
| `anthropic` | ❌ Not implemented | `anthropic` |
| `google` | ❌ Not implemented | `google-generativeai` |

---

## Section: datasets

**Purpose:** Defines paths and metadata for COMET datasets.
**Requirement:** REQ-3.1.3.3 (Dataset Configuration Section)

```yaml
datasets:
  libeest:
    name: "LibEST"
    base_path: "data/LibEST"
    language: "C"
    requirements_dir: "requirements"
    source_dir: "src"
    ground_truth_file: "ground.txt"
    link_types: ["Rq→Src"]
```

### Dataset Entry Structure

Each dataset is defined as a named entry under `datasets:`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Human-readable dataset name |
| `base_path` | string | **Yes** | Path to dataset root directory |
| `language` | string | **Yes** | Programming language of source code. Values: `Java`, `C`, `Python` |
| `requirements_dir` | string | **Yes** | Subdirectory containing requirement files |
| `source_dir` | string | **Yes** | Subdirectory containing source code files |
| `tests_dir` | string | No | Subdirectory containing test files (if applicable) |
| `ground_truth_file` | string | **Yes** | Filename of traceability ground truth file |
| `link_types` | list | **Yes** | Types of traceability links present. Values: `Rq→Src`, `UC→Src`, `Rq→Test` |

### Supported COMET Datasets

| Key | Name | Language | Requirement Type | Links |
|-----|------|----------|------------------|-------|
| `albergate` | Albergate | Italian | Requirements (Rq) | 16 |
| `ebt` | EBT | English | Requirements (Rq) | 33 |
| `libest` | LibEST | English | Requirements (Rq) | 47 |
| `etour` | eTOUR | English | Use Cases (UC) | 58 |
| `smos` | SMOS | Italian | Use Cases (UC) | 67 |
| `itrust` | iTrust | English | Use Cases (UC) | 0* |

*iTrust has nested directory structure not fully indexed.

---

## Section: experiments

**Purpose:** Configures parameters for each of the 10 preliminary experiments.
**Requirement:** REQ-3.1.3.1 (Experiment Configuration Section)

Each experiment has its own subsection with experiment-specific parameters.

---

### language_effect (PE01)

**Purpose:** Assess impact of requirement language (Italian vs. English) on model performance.
**Requirement:** REQ-3.6.1

```yaml
experiments:
  language_effect:
    enabled: true
    dataset: "albergate"
    models: ["GPT-4", "Claude-Sonnet"]
    task_type: "trace"
    sample_size: 10
    significance_level: 0.05
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment. Default: `true` |
| `dataset` | string | **Yes** | Dataset to use (must have Italian text). Recommended: `albergate` or `smos` |
| `models` | list | **Yes** | List of model names to test (references `model_selection.candidate_models`) |
| `task_type` | string | **Yes** | Task type to use for comparison. Values: `trace`, `recover`, `fill` |
| `sample_size` | integer | No | Number of requirements to sample. Default: `10` |
| `significance_level` | float | No | Alpha level for statistical tests. Default: `0.05` |

**Output:** Recommendation on whether to use Italian, translate to English, or analyze separately.

---

### model_selection (PE02)

**Purpose:** Select optimal prompt-based models from candidate pool.
**Requirement:** REQ-3.6.2

```yaml
experiments:
  model_selection:
    enabled: true
    models_per_category: 2
    candidate_models:
      - name: "GPT-4"
        provider: "mock"
        model: "gpt-4"
        category: "closed-source"
        temperature: 0.7
        max_tokens: 2000
        cost_per_1k_prompt_tokens: 0.03
        cost_per_1k_completion_tokens: 0.06
      # ... more models
    benchmark_task:
      description: "Simple Python function generation"
      prompt: |
        Write a Python function...
      evaluation_criteria:
        correctness: "Function exists and handles basic case"
        documentation: "Includes docstring"
        error_handling: "Handles empty list"
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment. Default: `true` |
| `models_per_category` | integer | No | Number of top models to select per category. Default: `2` |
| `candidate_models` | list | **Yes** | List of model configurations to evaluate |
| `benchmark_task` | object | **Yes** | Task definition for model evaluation |

#### candidate_models Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Display name for the model |
| `provider` | string | **Yes** | Provider type: `mock`, `openai`, `anthropic`, `google` |
| `model` | string | **Yes** | Model identifier |
| `category` | string | **Yes** | Classification: `closed-source` or `open-source` |
| `temperature` | float | No | Sampling temperature |
| `max_tokens` | integer | No | Maximum output tokens |
| `cost_per_1k_prompt_tokens` | float | No | Cost per 1000 prompt tokens |
| `cost_per_1k_completion_tokens` | float | No | Cost per 1000 completion tokens |

#### benchmark_task Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | **Yes** | Human-readable task description |
| `prompt` | string | **Yes** | The prompt to send to each model |
| `evaluation_criteria` | object | **Yes** | Key-value pairs defining evaluation criteria |

---

### agent_selection (PE03)

**Purpose:** Select optimal agentic systems and backend models.
**Requirement:** REQ-3.6.3
**Status:** ⚠️ Stub implementation only

```yaml
experiments:
  agent_selection:
    enabled: true
    agents_per_category: 2
    candidate_agents:
      - name: "Agent-A"
        category: "closed-source"
        backend_models: ["gpt-4", "claude-sonnet"]
      - name: "Agent-B"
        category: "open-source"
        backend_models: ["llama-3-70b"]
    benchmark_task:
      description: "Simple bug fix task"
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `agents_per_category` | integer | No | Number of top agents to select per category |
| `candidate_agents` | list | **Yes** | List of agent configurations |
| `benchmark_task` | object | **Yes** | Task definition for agent evaluation |

#### candidate_agents Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Agent identifier |
| `category` | string | **Yes** | Classification: `closed-source` or `open-source` |
| `backend_models` | list | **Yes** | List of backend models to test with this agent |

**Note:** Requires REQ-3.3 (Agentic System Integration) which is not yet implemented.

---

### temperature_optimization (PE04)

**Purpose:** Determine optimal temperature values for each task type.
**Requirement:** REQ-3.6.4

```yaml
experiments:
  temperature_optimization:
    enabled: true
    correctness_tasks: ["bug_fix", "documentation"]
    exploratory_tasks: ["new_feature", "test_generation"]
    correctness_temperatures: [0.0, 0.1, 0.2]
    exploratory_temperatures: [0.5, 0.6, 0.7]
    sample_size_per_temperature: 5
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `correctness_tasks` | list | **Yes** | Task types requiring high accuracy (low temperature) |
| `exploratory_tasks` | list | **Yes** | Task types benefiting from creativity (higher temperature) |
| `correctness_temperatures` | list | **Yes** | Temperature values to test for correctness tasks |
| `exploratory_temperatures` | list | **Yes** | Temperature values to test for exploratory tasks |
| `sample_size_per_temperature` | integer | No | Samples to run per temperature value. Default: `5` |

**Output:** Recommended temperature per task type.

---

### max_token_determination (PE05)

**Purpose:** Determine appropriate max_tokens limits for each task type.
**Requirement:** REQ-3.6.5

```yaml
experiments:
  max_token_determination:
    enabled: true
    task_types: ["new_feature", "bug_fix", "test_generation", "documentation"]
    sample_size: 20
    percentiles: [50, 75, 90, 95, 99]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `task_types` | list | **Yes** | Task types to analyze |
| `sample_size` | integer | No | Number of samples per task type. Default: `20` |
| `percentiles` | list | No | Percentiles to compute for distribution analysis. Default: `[50, 75, 90, 95, 99]` |

**Output:** Recommended max_tokens setting per task type, or "no limit" if appropriate.

---

### stop_sequence (PE06)

**Purpose:** Design and validate stop sequences for each task type.
**Requirement:** REQ-3.6.6
**Status:** ⚠️ Stub implementation only

```yaml
experiments:
  stop_sequence:
    enabled: true
    task_types: ["new_feature", "bug_fix", "test_generation", "documentation"]
    candidate_sequences:
      new_feature: ["```\n\n", "END_OF_CODE"]
      bug_fix: ["```\n\n", "END_OF_FIX"]
      test_generation: ["```\n\n", "END_OF_TESTS"]
      documentation: ["```\n\n", "END_OF_DOC"]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `task_types` | list | **Yes** | Task types to configure |
| `candidate_sequences` | object | **Yes** | Map of task type to list of candidate stop sequences |

**Output:** Validated stop sequences per task type.

---

### prompt_strategy (PE07)

**Purpose:** Compare prompting strategies to find optimal approach.
**Requirement:** REQ-3.6.7

```yaml
experiments:
  prompt_strategy:
    enabled: true
    strategies:
      - "zero-shot"
      - "zero-shot-cot"
      - "few-shot-cot"
    sample_size: 10
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `strategies` | list | **Yes** | Prompting strategies to compare |
| `sample_size` | integer | No | Samples per strategy. Default: `10` |

#### Available Strategies

| Strategy | Description |
|----------|-------------|
| `zero-shot` | Direct prompt without examples |
| `zero-shot-cot` | Zero-shot with chain-of-thought reasoning |
| `few-shot-cot` | Examples provided with chain-of-thought |

**Output:** Best-performing strategy with example prompts per task type.

---

### control_condition (PE08)

**Purpose:** Determine appropriate control condition (no traceability links).
**Requirement:** REQ-3.6.8
**Status:** ⚠️ Stub implementation only

```yaml
experiments:
  control_condition:
    enabled: true
    variants:
      - "full_codebase"
      - "expanded_file_list"
    expansion_factors: [2, 3, 5]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `variants` | list | **Yes** | Control condition variants to test |
| `expansion_factors` | list | No | Multipliers for expanded file list variant |

#### Control Variants

| Variant | Description |
|---------|-------------|
| `full_codebase` | Provide access to entire codebase |
| `expanded_file_list` | Provide more files than treatment but not all |

**Output:** Recommended control condition per model type.

---

### token_budget (PE09)

**Purpose:** Determine optimal token budget allocation across prompt sections.
**Requirement:** REQ-3.6.9

```yaml
experiments:
  token_budget:
    enabled: true
    total_budget: 8000
    sections:
      persona: 100
      instruction: 500
      requirement: 1000
      traceability_bundle: 4000
      file_list: 2000
      output_specification: 400
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `total_budget` | integer | **Yes** | Total token budget for prompts |
| `sections` | object | **Yes** | Initial token allocation per section |

#### Prompt Sections

| Section | Description | Typical Allocation |
|---------|-------------|-------------------|
| `persona` | System/role definition | 1-2% |
| `instruction` | Task instructions | 5-10% |
| `requirement` | Requirement/use case text | 10-15% |
| `traceability_bundle` | Traceability data and context | 40-50% |
| `file_list` | Available source files | 20-30% |
| `output_specification` | Expected output format | 3-5% |

**Output:** Finalized token budget allocation scheme.

---

### power_analysis (PE10)

**Purpose:** Conduct statistical power analysis to determine required sample sizes.
**Requirement:** REQ-3.6.10

```yaml
experiments:
  power_analysis:
    enabled: true
    power_target: 0.80
    alpha: 0.05
    effect_sizes:
      new_feature: 0.5
      bug_fix: 0.3
      test_generation: 0.5
      documentation: 0.3
    inflation_factor: 1.15
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Whether to run this experiment |
| `power_target` | float | No | Target statistical power. Default: `0.80` |
| `alpha` | float | No | Significance level. Default: `0.05` |
| `effect_sizes` | object | **Yes** | Minimum detectable effect size per task type |
| `inflation_factor` | float | No | Multiplier to account for failures. Default: `1.15` (15%) |

#### Effect Size Interpretation (Cohen's d)

| Value | Interpretation |
|-------|----------------|
| 0.2 | Small effect |
| 0.5 | Medium effect |
| 0.8 | Large effect |

**Output:** Required sample sizes per task type for main experiments.

---

## Accessing Configuration in Code

### Loading Configuration

```python
from pes.core.config import load_config, ConfigurationManager

# Load from file
config = load_config("configs/config.yaml")

# Or create from dictionary (for testing)
config = ConfigurationManager(config_dict={
    'experiments': {
        'power_analysis': {
            'power_target': 0.80,
            'alpha': 0.05
        }
    }
})
```

### Accessing Values

```python
# Get single value with dot notation
log_level = config.get("execution.log_level")  # Returns "INFO"

# Get with default
api_key = config.get("models.gpt4.api_key", "not-set")

# Get entire section
exp_config = config.get_section("experiments")

# Check if key exists
if config.has("models.gpt4"):
    # Use gpt4 model
    pass

# Validate required sections
config.validate_required_sections("execution", "models", "experiments")
```

### In Experiments

```python
from pes.core.base_experiment import BaseExperiment

class MyExperiment(BaseExperiment):
    def run(self):
        # Access experiment-specific config
        sample_size = self.config.get("experiments.my_experiment.sample_size", 10)

        # Access model config
        models = self.config.get_section("models")

        return {"sample_size": sample_size}
```

---

## Requirements Traceability

| Configuration Section | Requirements |
|----------------------|--------------|
| Overall structure | REQ-3.1.1 (Format Support), REQ-3.1.3 (Hierarchy) |
| `execution` | REQ-3.1.3.4 (Execution Configuration) |
| `output` | REQ-3.1.3.5 (Output Configuration) |
| `models` | REQ-3.1.3.2 (Model Configuration), REQ-3.2.3 (LLM Parameters) |
| `datasets` | REQ-3.1.3.3 (Dataset Configuration), REQ-3.4 (Dataset Management) |
| `experiments` | REQ-3.1.3.1 (Experiment Configuration) |
| `experiments.language_effect` | REQ-3.6.1 |
| `experiments.model_selection` | REQ-3.6.2 |
| `experiments.agent_selection` | REQ-3.6.3 |
| `experiments.temperature_optimization` | REQ-3.6.4 |
| `experiments.max_token_determination` | REQ-3.6.5 |
| `experiments.stop_sequence` | REQ-3.6.6 |
| `experiments.prompt_strategy` | REQ-3.6.7 |
| `experiments.control_condition` | REQ-3.6.8 |
| `experiments.token_budget` | REQ-3.6.9 |
| `experiments.power_analysis` | REQ-3.6.10 |

---

## Notes

1. **API Keys:** All API keys in the default configuration are placeholders (`YOUR_*_API_KEY_HERE`). Replace with actual keys before running experiments with real providers.

2. **Paths:** All paths are relative to the project root directory unless specified as absolute paths.

3. **Mock Provider:** Use `provider: "mock"` for development and testing without incurring API costs.

4. **Extending:** To add new models or experiments, follow the existing structure patterns.
