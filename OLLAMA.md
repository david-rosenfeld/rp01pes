# Running Experiments with Local Models via Ollama

This guide explains how to run the Preliminary Experiments System (PES) using
local LLM models served by [Ollama](https://ollama.com/), eliminating the need
for paid API keys. All experiments execute against a model running on your own
machine.

---

## Prerequisites

- **Python 3.9+** installed
- **Ollama** installed and running ([download](https://ollama.com/download))
- **This repository** cloned with datasets in the `datasets/` directory
- **Sufficient RAM** for the model you choose (see table below)

---

## Step 1: Install Python Dependencies

From the project root directory:

```bash
pip install -r requirements.txt
```

This installs all required packages including the `ollama` Python client.

---

## Step 2: Choose and Pull a Model

Ollama hosts a registry of open-source models. For the code traceability tasks
in these experiments, code-specialized models perform best.

### Recommended Models

| Model | Pull Command | Download Size | RAM Needed | Notes |
|-------|-------------|---------------|------------|-------|
| `qwen2.5-coder:7b` | `ollama pull qwen2.5-coder:7b` | 4.7 GB | ~5 GB | Fast, good for quick testing |
| `qwen2.5-coder:14b` | `ollama pull qwen2.5-coder:14b` | 9.0 GB | ~10 GB | Best quality/speed tradeoff |
| `qwen2.5-coder:32b` | `ollama pull qwen2.5-coder:32b` | 20 GB | ~22 GB | Best quality, needs 64GB RAM |
| `codellama:13b` | `ollama pull codellama:13b` | 7.4 GB | ~9 GB | Meta's code-focused model |
| `deepseek-coder-v2:16b` | `ollama pull deepseek-coder-v2:16b` | 8.9 GB | ~10 GB | Strong code understanding |
| `mistral:7b` | `ollama pull mistral:7b` | 4.1 GB | ~5 GB | General purpose baseline |

**RAM guideline:** You need the model size plus 3-5 GB for the OS and Python.
On a 32 GB machine, models up to 14b parameters work comfortably.

Pull your chosen model:

```bash
ollama pull qwen2.5-coder:14b
```

Wait for the download to complete. Verify the model is available:

```bash
ollama list
```

You should see your model in the output:

```
NAME                    ID              SIZE      MODIFIED
qwen2.5-coder:14b      9ec8897f747e    9.0 GB    1 minute ago
```

---

## Step 3: Verify the Ollama Server is Running

Ollama runs as a background service. Verify it is responding:

```bash
ollama --version
```

If you get a version number (e.g., `ollama version is 0.16.2`), the server is
running. If not, start it:

- **Windows:** Ollama starts automatically as a system tray application.
  Launch it from the Start menu if it is not running.
- **macOS:** Launch the Ollama application.
- **Linux:** Run `ollama serve` in a separate terminal.

The server listens on `http://localhost:11434` by default.

---

## Step 4: Configure Experiments to Use Ollama

Edit `configs/config.yaml` to point experiments at your local model. Replace
`provider: "mock"` with `provider: "ollama"` and set the model name.

### Option A: Run All Experiments with One Local Model

Change every `model:` block under `experiments:` from mock to ollama. For
example, to use `qwen2.5-coder:14b` for PE04 (Temperature Optimization):

**Before (mock):**
```yaml
  temperatureoptimization:
    enabled: true
    model:
      provider: "mock"
      name: "mock-model"
      response_mode: "realistic"
```

**After (ollama):**
```yaml
  temperatureoptimization:
    enabled: true
    model:
      provider: "ollama"
      model: "qwen2.5-coder:14b"
      name: "Qwen-Coder-14B"
```

Apply this change to the `model:` blocks in these experiment sections:
- `temperatureoptimization` (PE04)
- `maxtokendetermination` (PE05)
- `stop_sequence` (PE06)
- `promptstrategy` (PE07)
- `control_condition` (PE08)

For PE01 (`language_effect`), update each model in the `models:` list:

```yaml
  language_effect:
    models:
      - name: "Qwen-Coder-14B-A"
        provider: "ollama"
        model: "qwen2.5-coder:14b"
      - name: "Qwen-Coder-7B"
        provider: "ollama"
        model: "qwen2.5-coder:7b"
      - name: "Mistral-7B"
        provider: "ollama"
        model: "mistral:7b"
```

For PE02 (`model_selection`), update entries in `candidate_models:`:

```yaml
    candidate_models:
      - name: "Qwen-Coder-14B"
        provider: "ollama"
        model: "qwen2.5-coder:14b"
        category: "open-source"
        temperature: 0.7
        max_tokens: 2000
        cost_per_1k_prompt_tokens: 0.0
        cost_per_1k_completion_tokens: 0.0
```

### Option B: Mix Local and Mock Models

You can use Ollama for some models and keep `mock` for others. Each model entry
is independent. This is useful for quick testing -- run one real model alongside
mock baselines.

### Note on PE09 and PE10

PE09 (Token Budget) and PE10 (Power Analysis) do not call any LLM. They run
purely statistical computations and work with any configuration.

---

## Step 5: Run the Experiments

### Run All Experiments at Once

```bash
python run_all_experiments.py configs/config.yaml
```

This executes PE01, PE02, PE04-PE10 in sequence (PE03 is deferred) and prints
a summary table at the end.

### Run a Single Experiment

Each experiment has its own standalone script:

```bash
python pe01.py configs/config.yaml   # Language Effect Assessment
python pe02.py configs/config.yaml   # Model Selection
python pe04.py configs/config.yaml   # Temperature Optimization
python pe05.py configs/config.yaml   # Max Token Determination
python pe06.py configs/config.yaml   # Stop Sequence Definition
python pe07.py configs/config.yaml   # Prompting Strategy Testing
python pe08.py configs/config.yaml   # Control Condition Determination
python pe09.py configs/config.yaml   # Token Budget Allocation
python pe10.py configs/config.yaml   # Power Analysis
```

---

## Step 6: Understand the Output

### Console Output

Each experiment logs progress to the console. You will see lines like:

```
2026-02-26 09:10:55 - TemperatureOptimizationExperiment.PE04 - INFO - Testing TaskType: trace (category: correctness)
2026-02-26 09:10:55 - TemperatureOptimizationExperiment.PE04 - INFO -   Testing temperature: 0.0
```

When using `run_all_experiments.py`, a summary table prints at the end:

```
======================================================================
  EXECUTION SUMMARY
======================================================================
  Total experiments: 9
  Completed:         9
  Failed:            0
  Total duration:    342.15s

  Experiment   Status       Duration   Key Finding
  ------------ ------------ ---------- ----------------------------------
  PE01         COMPLETED    45.23s     Decision: Use original language (Italian)
  PE02         COMPLETED    92.10s     Selected 4 models: ...
  PE04         COMPLETED    67.44s     Optimal temperatures: trace=0.0, ...
  ...
======================================================================
```

### Result Files

All results are saved as JSON to the `results/` directory:

```
results/
  LanguageEffectExperiment_PE01_20260226_091055.json
  ModelSelectionExperiment_PE02_20260226_091055.json
  TemperatureOptimizationExperiment_PE04_20260226_091055.json
  MaxTokenDeterminationExperiment_PE05_20260226_091055.json
  StopSequenceExperiment_PE06_20260226_091055.json
  PromptStrategyExperiment_PE07_20260226_091055.json
  ControlConditionExperiment_PE08_20260226_091055.json
  TokenBudgetExperiment_PE09_20260226_091055.json
  PowerAnalysisExperiment_PE10_20260226_091055.json
  batch_run_20260226_091054.json          # Summary of the batch run
```

Each JSON file contains the full experiment data: configuration used, raw
results, statistical analysis, and recommendations.

### Log Files

Detailed logs for each run are saved to the `logs/` directory:

```
logs/
  TemperatureOptimizationExperiment.PE04_20260226_091055.log
```

### What Each Experiment Produces

| Experiment | Output |
|------------|--------|
| **PE01** | Statistical comparison of Italian vs English requirement performance; recommendation on which language to use |
| **PE02** | Ranked list of models by composite score (quality + speed + cost); top N selected per category |
| **PE04** | Optimal temperature setting per task type, with ANOVA significance tests |
| **PE05** | Recommended max_tokens limit per task type based on output length distributions |
| **PE06** | Validated stop sequences per task type with false positive rates |
| **PE07** | Best prompting strategy (zero-shot, zero-shot + CoT, few-shot + CoT) with accuracy comparison |
| **PE08** | Recommended control condition variant (full codebase vs expanded file list) per model type |
| **PE09** | Token budget allocation scheme across prompt sections (persona, instruction, requirement, etc.) |
| **PE10** | Required sample sizes per task type for the main study (power = 0.80, alpha = 0.05) |

---

## Performance Expectations

With Ollama running locally, experiments are significantly slower than the mock
provider because every LLM call involves real model inference.

### Approximate Timings (qwen2.5-coder:14b on CPU)

| Experiment | Mock Provider | Local Model (est.) |
|------------|--------------|-------------------|
| PE01 | < 1s | 5-15 min |
| PE02 | < 1s | 10-30 min |
| PE04 | < 1s | 15-45 min |
| PE05 | < 1s | 5-15 min |
| PE06 | < 1s | 5-15 min |
| PE07 | < 1s | 5-15 min |
| PE08 | < 1s | 5-15 min |
| PE09 | < 1s | No LLM calls |
| PE10 | < 1s | No LLM calls |
| **Full batch** | **~1s** | **~1-3 hours** |

The first request after pulling a model is slower (~30-60s) because Ollama
loads the model weights into memory. Subsequent requests within the same session
are faster (~5-15s each depending on prompt length and max_tokens).

**Tip:** If you have a CUDA-compatible GPU, Ollama will use it automatically
and inference will be 5-10x faster than CPU-only.

---

## Troubleshooting

### "Model not found" error

```
LLMError: Model 'qwen2.5-coder:14b' not found. Pull it with: ollama pull qwen2.5-coder:14b
```

Run the suggested `ollama pull` command and try again.

### Connection refused

```
ConnectionError: Failed to connect to localhost:11434
```

The Ollama server is not running. Start it (see Step 3).

### Out of memory / very slow inference

The model is too large for your available RAM. Switch to a smaller variant:

```bash
ollama pull qwen2.5-coder:7b
```

Update the `model:` field in `configs/config.yaml` accordingly.

### Experiment timeout

Some experiments make many LLM calls. If a single call hangs, check that
Ollama is still responsive:

```bash
ollama run qwen2.5-coder:14b "Hello"
```

If this works, the experiment may just need more time. Local inference is
inherently slower than API-based providers.

### Using a Remote Ollama Server

If Ollama runs on a different machine (e.g., a GPU server), set the `host`
field in the model config:

```yaml
    model:
      provider: "ollama"
      model: "qwen2.5-coder:14b"
      host: "http://192.168.1.100:11434"
```
