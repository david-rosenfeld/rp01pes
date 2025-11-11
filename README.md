# Preliminary Experiments System (PES)

A modular Python framework for executing preliminary experiments investigating the impact of requirement traceability data on Large Language Model performance in specification-driven coding tasks.

**Version:** 1.0 (Foundation)  
**Status:** Core infrastructure complete, 1 of 10 experiments fully implemented  
**Date:** 2025-11-02

---

## Quick Start

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Install dependencies
pip install PyYAML
```

### Running Your First Experiment

```bash
# Run PE02 (Model Selection) with mock provider
python pe02.py configs/config.yaml

# View results
cat results/ModelSelectionExperiment_PE02_*.json

# View logs
cat logs/ModelSelectionExperiment.PE02_*.log
```

That's it! You've just run your first preliminary experiment.

---

## What's Included

### ✅ Complete and Functional

- **Core Infrastructure**: Configuration, logging, exceptions, base classes
- **LLM Integration**: Abstract interface + mock provider
- **PE02 Model Selection**: Fully implemented and tested

### ⚠️ Stub Implementations (Framework Only)

- PE01, PE03-PE10: Structure in place, logic needed

### ❌ TODO

- Real LLM providers (OpenAI, Anthropic, Google)
- Dataset loading, Statistical analysis, Report generation

---

## Documentation

- **📖 README.md** (this file) - Quick start
- **📖 ARCHITECTURE.md** - System design and components  
- **📋 IMPLEMENTATION_STATUS.md** - What's done, what's TODO, next steps
- **🔄 CONTINUATION_GUIDE.md** - How to continue in next sessions

---

## Key Commands

```bash
# Run experiments
python pe02.py configs/config.yaml

# View results
ls results/

# View logs
tail -f logs/*.log
```

---

## Next Steps

1. Read `IMPLEMENTATION_STATUS.md` to see what's ready
2. Follow `CONTINUATION_GUIDE.md` to continue development
3. Check `ARCHITECTURE.md` for system design

For detailed usage, examples, and development guide, see the full documentation files.
