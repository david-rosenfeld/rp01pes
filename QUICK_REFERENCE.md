# Quick Reference

## Run Everything

```bash
pip install -r requirements.txt
python run_all_experiments.py configs/config.yaml
```

Results go to `results/`. Logs go to `logs/`.

---

## Run a Single Experiment

```bash
python pe01.py configs/config.yaml   # Language Effect
python pe02.py configs/config.yaml   # Model Selection
python pe04.py configs/config.yaml   # Temperature Optimization
python pe05.py configs/config.yaml   # Max Token Determination
python pe06.py configs/config.yaml   # Stop Sequence
python pe07.py configs/config.yaml   # Prompt Strategy
python pe08.py configs/config.yaml   # Control Condition
python pe09.py configs/config.yaml   # Token Budget
python pe10.py configs/config.yaml   # Power Analysis
```

PE03 (Agent Selection) is deferred.

---

## Switch to a Real LLM Provider

Edit `configs/config.yaml`. Change `provider: "mock"` to one of:

| Provider | Config Value | Requires |
|----------|-------------|----------|
| Mock | `"mock"` | Nothing |
| OpenAI | `"openai"` | `OPENAI_API_KEY` env var |
| Anthropic | `"anthropic"` | `ANTHROPIC_API_KEY` env var |
| Google | `"google"` | `GOOGLE_API_KEY` env var |
| Ollama | `"ollama"` | Ollama running locally |

Example config block:

```yaml
model:
  provider: "ollama"
  model: "qwen2.5-coder:14b"
  name: "Qwen-Coder-14B"
```

For local models with no API keys, see [OLLAMA.md](OLLAMA.md).

---

## Run Tests

```bash
python test_datasets.py    # Dataset loading
python test_analysis.py    # Statistical functions
python test_pe10.py        # Power analysis
python test_pe05.py        # Max token determination
```

---

## Project Layout

```
pe01.py .. pe10.py          Experiment entry points
run_all_experiments.py      Batch runner
configs/config.yaml         Central configuration

pes/core/                   Config, logging, base classes
pes/llm/                    LLM providers (mock + OpenAI/Anthropic/Google/Ollama)
pes/datasets/               COMET dataset loading and bundles
pes/experiments/            Experiment implementations
pes/analysis/               Statistics and report generation
```

---

## Key Code Patterns

**Load config and run an experiment:**

```python
from pes.core.config import load_config
from pes.experiments.pe04_temperatureoptimization import TemperatureOptimizationExperiment

config = load_config("configs/config.yaml")
experiment = TemperatureOptimizationExperiment(config, experiment_id="PE04")
results = experiment.execute()
```

**Load a dataset:**

```python
from pes.datasets import load_dataset, generate_bundles_for_dataset

dataset = load_dataset('albergate', {'base_path': './datasets'})
bundles = generate_bundles_for_dataset(dataset, token_budget=5000)
```

**Use an LLM provider:**

```python
from pes.llm.factory import get_provider

provider = get_provider('mock', config)
response = provider.generate(prompt)
```

**Run a statistical test:**

```python
from pes.analysis import paired_t_test, cohens_d

result = paired_t_test(group1, group2)
effect = cohens_d(group1, group2, paired=True)
```

---

## Documentation Map

| What | Where |
|------|-------|
| Overview and quick start | [README.md](README.md) |
| System architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Implementation status | [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) |
| File tree | [FILE_STRUCTURE.md](FILE_STRUCTURE.md) |
| Local model setup | [OLLAMA.md](OLLAMA.md) |
| Configuration reference | [configs/CONFIGURATION.md](configs/CONFIGURATION.md) |
| Dataset module guide | [pes/datasets/README.md](pes/datasets/README.md) |

---

## Current Status

- 9/10 experiments implemented and passing with mock provider
- 4 real LLM providers available (OpenAI, Anthropic, Google, Ollama)
- 6 COMET datasets loaded (366 requirements, 356 source files, 163 links)
- Statistical analysis module with 21 functions
- Report generation in Markdown, HTML, and LaTeX
- PE03 deferred (requires agentic system integration)

---

## Common Issues

**"Module not found"** -- Run from the project root directory where `pes/` is located.

**"Config not found"** -- Pass the config path explicitly: `python pe02.py configs/config.yaml`

**"Model not found" (Ollama)** -- Pull the model first: `ollama pull qwen2.5-coder:14b`

**Slow Ollama inference** -- First request loads the model (~30-60s). Use a smaller model if RAM is limited. See [OLLAMA.md](OLLAMA.md).
