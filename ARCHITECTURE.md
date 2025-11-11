# Preliminary Experiments System - Architecture Document

**Version:** 1.0  
**Date:** 2025-11-02  
**Status:** Foundation Complete, Extensions Needed

---

## System Overview

The Preliminary Experiments System (PES) is a modular Python framework for executing preliminary experiments investigating the impact of requirement traceability data on LLM performance in specification-driven coding tasks.

### Design Principles

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Extensibility**: New providers, experiments, and features can be added without modifying core code
3. **Configuration-Driven**: All parameters externalized in YAML/JSON files
4. **Provider-Agnostic**: Uniform interface across different LLM providers
5. **Comprehensive Logging**: Experiment-aware logging with structured output

---

## Directory Structure

```
/
├── pes/                          # Main package
│   ├── core/                     # Core infrastructure
│   │   ├── __init__.py
│   │   ├── exceptions.py         # Custom exception hierarchy
│   │   ├── logging.py            # Experiment-aware logging
│   │   ├── config.py             # Configuration management
│   │   └── base_experiment.py   # Base class for all experiments
│   │
│   ├── llm/                      # LLM integration layer
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract LLM interface + Mock provider
│   │   └── factory.py            # Provider registry and factory
│   │
│   ├── agents/                   # Agentic system integration (TODO)
│   │   └── __init__.py
│   │
│   ├── datasets/                 # Dataset management (TODO)
│   │   └── __init__.py
│   │
│   ├── experiments/              # Experiment implementations
│   │   ├── __init__.py
│   │   ├── pe02_model_selection.py  # COMPLETE implementation
│   │   ├── pe01_languageeffect.py   # STUB
│   │   ├── pe03_agentselection.py   # STUB
│   │   ├── pe04_temperatureoptimization.py  # STUB
│   │   ├── pe05_maxtokendetermination.py    # STUB
│   │   ├── pe06_stopsequence.py     # STUB
│   │   ├── pe07_promptstrategy.py   # STUB
│   │   ├── pe08_controlcondition.py # STUB
│   │   ├── pe09_tokenbudget.py      # STUB
│   │   └── pe10_poweranalysis.py    # STUB
│   │
│   ├── storage/                  # Data storage (TODO)
│   │   └── __init__.py
│   │
│   ├── analysis/                 # Analysis and reporting (TODO)
│   │   └── __init__.py
│   │
│   └── utils/                    # Utility functions (TODO)
│       └── __init__.py
│
├── pe01.py through pe10.py       # Standalone experiment programs
├── configs/                      # Configuration files
│   └── config.yaml               # Main configuration file
├── logs/                         # Log files (created at runtime)
├── results/                      # Experiment results (created at runtime)
└── data/                         # COMET datasets (TODO: Download)
```

---

## Core Components

### 1. Exception Hierarchy (`pes/core/exceptions.py`)

**Status:** ✅ COMPLETE

All exceptions inherit from `PESError`:
- `ConfigurationError`: Configuration loading/validation errors
- `DatasetError`: Dataset loading/processing errors
- `LLMError`: LLM integration errors
- `ExperimentError`: Experiment execution errors
- `StorageError`: Data storage/retrieval errors
- `AnalysisError`: Statistical analysis/reporting errors

### 2. Logging System (`pes/core/logging.py`)

**Status:** ✅ COMPLETE

Key Features:
- Experiment-aware logging with context
- Console and file output
- Structured logging with key-value pairs
- Special methods for experiment lifecycle events
- LLM request/response logging

**Usage:**
```python
from pes.core.logging import get_logger

logger = get_logger(__name__, log_dir="logs", level="INFO")
logger.info("Processing started")
logger.llm_request("gpt-4", prompt_tokens=100)
```

### 3. Configuration Management (`pes/core/config.py`)

**Status:** ✅ COMPLETE

Implements REQ-3.1 (Configuration Management):
- Loads YAML and JSON formats
- Dot-notation access to nested values
- Section validation
- Format equivalence guaranteed

**Usage:**
```python
from pes.core.config import load_config

config = load_config("config.yaml")
api_key = config.get("llm.openai.api_key")
exp_config = config.get_section("experiments")
```

### 4. Base Experiment Class (`pes/core/base_experiment.py`)

**Status:** ✅ COMPLETE

All experiments inherit from `BaseExperiment`:
- Common initialization and configuration
- Timing and error handling
- Result storage (JSON format)
- Status tracking
- Logging integration

**Key Methods:**
- `run()`: Abstract method - implement experiment logic
- `execute()`: Wraps run() with common functionality
- `get_description()`: Return human-readable description

---

## LLM Integration Layer

### Provider Architecture

**Status:** ✅ Foundation Complete, Providers TODO

The LLM layer provides a uniform interface across providers:

```
BaseLLMProvider (abstract)
    ├── MockLLMProvider (✅ complete - for testing)
    ├── OpenAIProvider (❌ TODO)
    ├── AnthropicProvider (❌ TODO)
    └── GoogleProvider (❌ TODO)
```

### Provider Interface (`pes/llm/base.py`)

**Key Components:**
1. `LLMResponse`: Standardized response format
2. `BaseLLMProvider`: Abstract base class
   - `generate()`: Main public interface
   - `_make_request()`: Provider-specific implementation
3. `MockLLMProvider`: Testing provider (no API calls)

### Provider Factory (`pes/llm/factory.py`)

**Functions:**
- `register_provider()`: Add new provider
- `get_provider()`: Instantiate provider by name
- `list_providers()`: Get available providers

**Usage:**
```python
from pes.llm.factory import get_provider

config = {'model': 'gpt-4', 'api_key': 'sk-...'}
provider = get_provider('openai', config)
response = provider.generate("Hello, world!")
```

---

## Experiment Implementations

### PE02: Model Selection (COMPLETE)

**File:** `pes/experiments/pe02_model_selection.py`  
**Status:** ✅ COMPLETE - Fully functional reference implementation

**Features:**
- Loads candidate models from config
- Executes benchmark task on each model
- Evaluates responses with simple heuristics
- Ranks models by composite score (quality + speed + cost)
- Selects top N per category
- Generates Markdown selection report

**Key Methods:**
- `_load_candidate_models()`: Load from config
- `_load_benchmark_task()`: Define benchmark
- `_test_model()`: Test single model
- `_evaluate_response()`: Score response
- `_rank_models()`: Compute composite scores
- `_select_top_models()`: Select top N per category
- `_generate_selection_report()`: Create Markdown report

### PE01, PE03-PE10 (STUBS)

**Status:** ❌ STUB - Framework only, logic TODO

Each stub includes:
- Class structure inheriting from `BaseExperiment`
- Configuration loading skeleton
- TODO comments with implementation steps
- Placeholder `run()` method returning stub results

**To implement a stub:**
1. Read the requirements (REQ-3.6.X) for that experiment
2. Follow the TODO items in the code
3. Use PE02 as a reference implementation pattern
4. Test with mock provider first before using real APIs

---

## Configuration Format

### Structure

```yaml
execution:
  log_dir: "logs"
  log_level: "INFO"
  mode: "sequential"

output:
  directory: "results"
  formats: ["json", "csv", "markdown"]

models:
  <model_name>:
    provider: "openai|anthropic|google|mock"
    model: "<model_identifier>"
    api_key: "<api_key>"
    temperature: 0.7
    max_tokens: 2000
    cost_per_1k_prompt_tokens: 0.03
    cost_per_1k_completion_tokens: 0.06

datasets:
  <dataset_name>:
    base_path: "data/<dataset>"
    language: "Java|C|Python"
    requirements_dir: "requirements"
    source_dir: "src"
    ground_truth_file: "ground.txt"
    link_types: ["Rq→Src", "UC→Src", "Rq→Test"]

experiments:
  <experiment_name>:
    enabled: true
    # Experiment-specific configuration
```

---

## Extending the System

### Adding a New LLM Provider

1. **Create provider module**: `pes/llm/<provider>_provider.py`
2. **Implement BaseLLMProvider**:
   ```python
   from .base import BaseLLMProvider, LLMResponse
   
   class MyProvider(BaseLLMProvider):
       def _validate_config(self):
           # Validate required fields
           pass
       
       def _make_request(self, prompt, **kwargs):
           # Call provider API
           # Return LLMResponse
           pass
   ```
3. **Register in factory**: `pes/llm/factory.py`
   ```python
   from .my_provider import MyProvider
   register_provider('myprovider', MyProvider)
   ```

### Adding a New Experiment

1. **Create experiment module**: `pes/experiments/peXX_<name>.py`
2. **Inherit from BaseExperiment**:
   ```python
   from ..core.base_experiment import BaseExperiment
   
   class MyExperiment(BaseExperiment):
       def get_description(self):
           return "My experiment description"
       
       def run(self):
           # Implement logic
           return results_dict
   ```
3. **Create standalone program**: `peXX.py` (follow pe02.py pattern)

### Adding Dataset Support

**TODO:** Implement `pes/datasets/` module with:
- Dataset loaders for COMET format
- Ground truth file parsing
- Traceability bundle generation
- Requirement/source code access

---

## Testing Strategy

### Current Testing

- Mock provider for testing without API calls
- Configuration loading tested manually
- PE02 tests full experiment execution flow

### Needed Testing (TODO)

1. Unit tests for each module
2. Integration tests for end-to-end flows
3. Provider-specific tests with real APIs
4. Dataset loader tests with COMET data

---

## Known Limitations

1. **No Real LLM Providers**: Only mock provider implemented
   - Action: Implement OpenAI, Anthropic, Google providers
   
2. **No Dataset Loading**: COMET dataset integration missing
   - Action: Implement dataset module
   
3. **Stub Experiments**: 9 of 10 experiments are stubs
   - Action: Implement each based on requirements
   
4. **No Statistical Analysis**: Analysis module empty
   - Action: Implement statistical tests, power analysis
   
5. **No Report Generation**: Only basic JSON output
   - Action: Implement Markdown, HTML, PDF reports
   
6. **No Parallel Execution**: Only sequential mode works
   - Action: Implement parallel execution engine

---

## Next Steps (Priority Order)

1. **Implement OpenAI Provider** - Most commonly needed
2. **Implement Dataset Module** - Required for all experiments
3. **Complete PE01 Implementation** - Language effect assessment
4. **Complete PE04 Implementation** - Temperature optimization
5. **Complete PE10 Implementation** - Power analysis
6. **Implement remaining experiments** - PE03, PE05-PE09
7. **Add statistical analysis** - Effect sizes, hypothesis tests
8. **Add report generation** - Markdown, HTML, PDF outputs

---

## Dependencies

### Current (Implemented)
- Python 3.9+
- PyYAML - Configuration parsing
- Standard library only

### Needed (TODO)
- openai - OpenAI API client
- anthropic - Anthropic API client
- google-generativeai - Google Gemini client
- numpy - Numerical computing
- scipy - Statistical analysis
- pandas - Data manipulation
- matplotlib - Visualization
- seaborn - Statistical visualization

---

## Key Design Decisions

### 1. Provider Abstraction
**Decision:** Abstract provider interface with factory pattern  
**Rationale:** Allows easy switching between providers and models  
**Location:** `pes/llm/base.py`, `pes/llm/factory.py`

### 2. Configuration-Driven
**Decision:** All parameters in external YAML/JSON  
**Rationale:** No code changes needed for different experiments  
**Location:** `pes/core/config.py`

### 3. Experiment Base Class
**Decision:** Common base class with template method pattern  
**Rationale:** Consistent execution, timing, logging, storage  
**Location:** `pes/core/base_experiment.py`

### 4. Standalone Programs
**Decision:** Each experiment has its own executable (pe01.py-pe10.py)  
**Rationale:** Easy to run individually, clear entry points  
**Location:** Root directory

### 5. Mock Provider First
**Decision:** Mock provider for development/testing  
**Rationale:** Can develop and test without API costs  
**Location:** `pes/llm/base.py:MockLLMProvider`

---

## Contact & Support

For questions about this architecture, refer to:
1. This document (ARCHITECTURE.md)
2. Requirements document (prelim_exp_requirements_md.md)
3. Implementation status (IMPLEMENTATION_STATUS.md)
4. Code comments and docstrings
