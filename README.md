# Preliminary Experiments System (PES)

A modular Python framework for executing preliminary experiments investigating the impact of requirement traceability data on Large Language Model performance in specification-driven coding tasks.

**Status:** 9 of 10 experiments implemented and functional
**Python:** 3.9+

---

## Overview

PES runs 10 preliminary experiments (PE01--PE10) that determine optimal LLM configurations for a larger traceability study. The experiments cover language selection, model evaluation, temperature tuning, token limits, stop sequences, prompting strategies, control conditions, token budgets, and statistical power analysis.

PE03 (Agent Selection) is deferred pending a viable agentic integration path. The remaining 9 experiments execute end-to-end with either a built-in mock provider or real LLM backends.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: PyYAML, numpy, scipy, openai, anthropic, google-genai, and ollama.

### 2. Run All Experiments (Mock Provider)

The default configuration uses the mock provider, which requires no API keys and produces realistic traceability responses suitable for validating the experimental pipeline.

```bash
python run_all_experiments.py configs/config.yaml
```

This executes all 9 implemented experiments sequentially, prints a summary table, and saves a timestamped batch report to `results/`.

### 3. Run a Single Experiment

Each experiment has a standalone entry point:

```bash
python pe01.py configs/config.yaml   # PE01: Language Effect Assessment
python pe02.py configs/config.yaml   # PE02: Model Selection
python pe04.py configs/config.yaml   # PE04: Temperature Optimization
python pe05.py configs/config.yaml   # PE05: Max Token Determination
python pe06.py configs/config.yaml   # PE06: Stop Sequence Definition
python pe07.py configs/config.yaml   # PE07: Prompting Strategy Testing
python pe08.py configs/config.yaml   # PE08: Control Condition Determination
python pe09.py configs/config.yaml   # PE09: Token Budget Allocation
python pe10.py configs/config.yaml   # PE10: Power Analysis
```

---

## Using Real LLM Providers

PES supports four real LLM backends in addition to the mock provider:

| Provider | Package | API Key Environment Variable |
|----------|---------|------------------------------|
| OpenAI | `openai` | `OPENAI_API_KEY` |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` |
| Google Gemini | `google-genai` | `GOOGLE_API_KEY` |
| Ollama (local) | `ollama` | None (runs locally) |

To switch from mock to a real provider, edit the `model:` blocks in `configs/config.yaml`. For example:

```yaml
model:
  provider: "openai"
  model: "gpt-4"
  name: "GPT-4"
```

For local inference with no API keys, Ollama is the recommended path. See [OLLAMA.md](OLLAMA.md) for a detailed setup guide.

See [configs/CONFIGURATION.md](configs/CONFIGURATION.md) for the full configuration reference.

---

## Experiments

| ID | Name | Description | LLM Calls? |
|----|------|-------------|------------|
| PE01 | Language Effect Assessment | Compares Italian vs English requirement text to determine optimal language | Yes |
| PE02 | Model Selection | Evaluates candidate LLMs on benchmark tasks and selects optimal models per category | Yes |
| PE03 | Agent Selection | Evaluates agentic coding systems (deferred) | -- |
| PE04 | Temperature Optimization | Determines optimal temperature settings per task type (trace, recover, fill) | Yes |
| PE05 | Max Token Determination | Analyzes output length distributions to recommend max_tokens limits | Yes |
| PE06 | Stop Sequence Definition | Identifies and validates stop sequences per task type | Yes |
| PE07 | Prompt Strategy Comparison | Compares zero-shot, chain-of-thought, and few-shot strategies | Yes |
| PE08 | Control Condition Determination | Selects control conditions for prompt-based and agentic approaches | Yes |
| PE09 | Token Budget Allocation | Allocates token budget across prompt sections | No (dataset analysis) |
| PE10 | Power Analysis | Calculates required sample sizes for the main study | No (statistical) |

---

## Output

### Results

JSON files are saved to `results/` after each experiment run:

```
results/
  LanguageEffectExperiment_PE01_20260226_091055.json
  ModelSelectionExperiment_PE02_20260226_091055.json
  ...
  batch_run_20260226_091054.json          # Summary from run_all_experiments.py
```

Each JSON file contains the full experiment data: configuration used, raw results, statistical analysis, and recommendations.

### Logs

Detailed logs for each run are saved to `logs/`:

```
logs/
  TemperatureOptimizationExperiment.PE04_20260226_091055.log
```

---

## Datasets

PES uses the six COMET datasets for requirement traceability tasks:

| Dataset | Language | Requirements | Source Files | Links |
|---------|----------|-------------|--------------|-------|
| Albergate | Italian | 17 | 55 | 16 |
| EBT | English | 41 | 50 | 33 |
| LibEST | English | 52 | 35 | 47 |
| eTOUR | English | 58 | 116 | 58 |
| SMOS | Italian | 67 | 100 | 67 |
| iTrust | English | 131 | -- | -- |

Datasets are stored in the `datasets/` directory. See [pes/datasets/README.md](pes/datasets/README.md) for loading details and API documentation.

---

## Testing

```bash
python test_datasets.py    # Dataset module tests
python test_analysis.py    # Statistical analysis tests
python test_pe10.py        # PE10-specific tests
python test_pe05.py        # PE05-specific tests
```

All 9 implemented experiments can also be validated with the mock provider:

```bash
python run_all_experiments.py configs/config.yaml
```

---

## Project Structure

The codebase is organized as a Python package (`pes/`) with standalone experiment runners at the project root.

```
pe01.py .. pe10.py              Standalone experiment entry points
run_all_experiments.py          Batch runner for all experiments
configs/config.yaml             Central configuration file

pes/
  core/                         Configuration, logging, base classes
  llm/                          LLM provider abstraction (mock + 4 real)
  datasets/                     COMET dataset loading and bundle generation
  experiments/                  Experiment implementations (PE01-PE10)
  analysis/                     Statistical analysis and report generation
  agents/                       Agentic integration (Aider adapter, base agent)
```

For the complete file tree and descriptions, see [FILE_STRUCTURE.md](FILE_STRUCTURE.md).

---

## Dependencies

All dependencies are listed in `requirements.txt`:

```
PyYAML>=6.0.1          # Configuration management
numpy>=1.24.0          # Numerical operations
scipy>=1.10.0          # Statistical analysis
openai>=1.0.0          # OpenAI LLM provider
anthropic>=0.8.0       # Anthropic LLM provider
google-genai>=1.0.0    # Google Gemini LLM provider
ollama>=0.4.0          # Ollama local model provider
```

Only PyYAML, numpy, and scipy are required for mock-provider runs. The LLM provider packages are only needed when using the corresponding backend.

---

## Documentation

| File | Description |
|------|-------------|
| [README.md](README.md) | This file -- overview and quick start |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, components, and data flow |
| [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) | Detailed completion status and requirements mapping |
| [FILE_STRUCTURE.md](FILE_STRUCTURE.md) | Complete file tree with descriptions |
| [OLLAMA.md](OLLAMA.md) | Running experiments with local Ollama models |
| [configs/CONFIGURATION.md](configs/CONFIGURATION.md) | Configuration file reference |
| [pes/datasets/README.md](pes/datasets/README.md) | Dataset module user guide |
| [CONTINUATION_GUIDE.md](CONTINUATION_GUIDE.md) | Development workflow and session management |

---

## Configuration

All experiments are configured through `configs/config.yaml`. The file controls:

- Which LLM provider and model each experiment uses
- Dataset paths and selection
- Experiment-specific parameters (temperatures, token limits, strategies, etc.)
- Which experiments are enabled or disabled

See [configs/CONFIGURATION.md](configs/CONFIGURATION.md) for the complete reference.

---

## Report Generation

PES includes report generators for three output formats:

- **Markdown** -- GitHub-compatible tables and formatting
- **HTML** -- Interactive reports with Chart.js visualizations
- **LaTeX** -- ACM sigconf conference paper format

See the report generation module at `pes/analysis/reports/` for usage details.
