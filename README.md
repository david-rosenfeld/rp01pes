# Preliminary Experiments System (PES)

A modular Python framework for executing preliminary experiments investigating the impact of requirement traceability data on Large Language Model performance in specification-driven coding tasks.

**Version:** 1.5 (Phase 4 Complete)
**Status:** 7 of 10 experiments fully implemented (~70% complete)
**Date:** 2025-12-03

---

## Quick Start

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Install dependencies
pip install PyYAML numpy scipy
```

### Running Experiments

All experiments follow the same command pattern:

```bash
python peXX.py configs/config.yaml
```

### Available Experiments (7/10)

#### ✅ **Working Experiments**

```bash
# PE02 - Model Selection (Reference Implementation)
python pe02.py configs/config.yaml

# PE01 - Language Effect Assessment
python pe01.py configs/config.yaml

# PE04 - Temperature Optimization
python pe04.py configs/config.yaml

# PE05 - Max Token Determination
python pe05.py configs/config.yaml

# PE07 - Prompt Strategy Comparison
python pe07.py configs/config.yaml

# PE09 - Token Budget Allocation
python pe09.py configs/config.yaml

# PE10 - Power Analysis (Statistical)
python pe10.py configs/config.yaml
```

#### ⚠️ **Stub Experiments** (Framework only)

```bash
# PE03 - Agent Selection (requires agentic system)
# PE06 - Stop Sequence Determination
# PE08 - Control Condition Selection
```

### Viewing Results

```bash
# List all results
ls results/

# View specific experiment result (JSON)
cat results/PowerAnalysisExperiment_PE10_*.json

# View experiment logs
cat logs/PowerAnalysisExperiment.PE10_*.log

# Watch logs in real-time
tail -f logs/*.log
```

---

## What's Included

### ✅ Complete and Functional

**Core Infrastructure:**
- Configuration management (YAML/JSON)
- Experiment-aware logging system
- Exception hierarchy
- Base experiment class with template pattern

**LLM Integration:**
- Abstract provider interface
- Mock provider (realistic traceability responses)
- Provider factory pattern

**Dataset Management:**
- All 6 COMET datasets (Albergate, EBT, LibEST, eTOUR, SMOS, iTrust)
- Ground truth traceability link parsing
- Traceability bundle generation with token budgets
- Italian and English text support

**Statistical Analysis:**
- Descriptive statistics (mean, median, std, quartiles)
- Hypothesis tests (t-test, Wilcoxon, ANOVA)
- Effect sizes (Cohen's d, Cliff's Delta)
- Power analysis for sample size determination
- Correlation analysis (Pearson, Spearman)

**Preliminary Experiments (7/10):**
- PE02: Model Selection
- PE01: Language Effect Assessment
- PE04: Temperature Optimization
- PE05: Max Token Determination
- PE07: Prompt Strategy Comparison
- PE09: Token Budget Allocation
- PE10: Power Analysis

### ⚠️ Partial/Stub Implementations

- PE03: Agent Selection (requires agentic system integration)
- PE06: Stop Sequence Determination
- PE08: Control Condition Selection

### ❌ TODO

- Real LLM providers (OpenAI, Anthropic, Google)
- Report generation (Markdown, HTML, PDF)
- Agentic system integration

---

## Experiment Descriptions

### PE01: Language Effect Assessment
Compares Italian vs English requirement text to determine optimal language for traceability tasks.

**Usage:**
```bash
python pe01.py configs/config.yaml
```

### PE02: Model Selection
Evaluates candidate LLM models on benchmark tasks and selects optimal models per category.

**Usage:**
```bash
python pe02.py configs/config.yaml
```

### PE04: Temperature Optimization
Determines optimal temperature settings for different TaskTypes (trace, recover, fill).

**Usage:**
```bash
python pe04.py configs/config.yaml
```

### PE05: Max Token Determination
Analyzes output length distributions to recommend max_tokens settings per TaskType.

**Usage:**
```bash
python pe05.py configs/config.yaml
```

### PE07: Prompt Strategy Comparison
Compares zero-shot, chain-of-thought, and few-shot prompting strategies.

**Usage:**
```bash
python pe07.py configs/config.yaml
```

### PE09: Token Budget Allocation
Determines optimal allocation of token budget across prompt sections (persona, instruction, context, etc.).

**Usage:**
```bash
python pe09.py configs/config.yaml
```

### PE10: Power Analysis
Calculates required sample sizes using statistical power analysis (power=0.80, α=0.05).

**Usage:**
```bash
python pe10.py configs/config.yaml
```

---

## Testing

### Run Test Suites

```bash
# Dataset module tests
python test_datasets.py

# Statistical analysis tests
python test_analysis.py

# PE10 tests
python test_pe10.py

# PE05 tests
python test_pe05.py
```

### What's Tested

- ✅ All 6 COMET datasets load successfully
- ✅ 21 statistical analysis functions
- ✅ All 7 working experiments with mock provider
- ✅ Traceability bundle generation
- ✅ Token budget enforcement

---

## Documentation

- **📖 README.md** (this file) - Quick start and command reference
- **📋 IMPLEMENTATION_STATUS.md** - Detailed status, what's done, next steps
- **📖 ARCHITECTURE.md** - System design and components
- **📖 pes/datasets/README.md** - Dataset module user guide

---

## Dependencies

### Required (Installed)

```
PyYAML>=6.0.1      # Configuration management
numpy>=1.24.0      # Numerical operations
scipy>=1.10.0      # Statistical analysis
```

### Optional (Future)

```
openai>=1.0.0              # OpenAI provider
anthropic>=0.8.0           # Anthropic provider
google-generativeai>=0.3.0 # Google provider
matplotlib>=3.7.0          # Visualization
seaborn>=0.12.0            # Statistical plots
```

---

## Project Status

**Completed:** 7/10 Preliminary Experiments (70%)
- ✅ Core infrastructure
- ✅ Dataset management (6 datasets)
- ✅ Statistical analysis module
- ✅ Mock LLM provider
- ✅ 7 experiments fully functional

**Remaining:** 3/10 Experiments (30%)
- ⚠️ PE03 (requires agentic system)
- ⚠️ PE06
- ⚠️ PE08

**Future Work:**
- Real LLM providers (OpenAI, Anthropic, Google)
- Report generation (Markdown, HTML, PDF)
- Agentic system integration

---

## Common Workflows

### Run a Single Experiment

```bash
# Run experiment
python pe05.py configs/config.yaml

# Check results
cat results/MaxTokenDeterminationExperiment_PE05_*.json
```

### Run Multiple Experiments

```bash
# Run all working experiments sequentially
for exp in pe01 pe02 pe04 pe05 pe07 pe09 pe10; do
    python ${exp}.py configs/config.yaml
done

# View all results
ls -lt results/
```

### Analyze Results

```bash
# View JSON results with pretty printing
python -m json.tool results/PowerAnalysisExperiment_PE10_*.json

# Extract specific fields
cat results/PE10_*.json | grep -A 5 "recommendations"
```

---

## Next Steps

1. **Read IMPLEMENTATION_STATUS.md** - See detailed completion status
2. **Run working experiments** - Try PE10, PE01, PE04, PE05, PE07, PE09
3. **Review experiment results** - Check results/ directory
4. **Implement remaining experiments** - PE03, PE06, PE08 (optional)
5. **Add real LLM providers** - OpenAI, Anthropic, Google (when ready)

---

## Support

For detailed information:
- System design → [ARCHITECTURE.md](ARCHITECTURE.md)
- Implementation details → [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
- Dataset usage → [pes/datasets/README.md](pes/datasets/README.md)
- Code documentation → See docstrings in source files

---

**Last Updated:** 2025-12-03 (Session 6 - Phase 4 Complete)
