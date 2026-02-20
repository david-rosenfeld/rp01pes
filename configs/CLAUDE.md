# CLAUDE.md - Configuration

## Scope

Configuration files for the Preliminary Experiments System.

## Reference

See `CONFIGURATION.md` for complete field documentation.

## Files

| File | Purpose |
|------|---------|
| `config.yaml` | Main configuration file |
| `CONFIGURATION.md` | Field reference documentation |

## Structure

```yaml
execution:    # Runtime settings
output:       # Result output settings
models:       # LLM provider configurations
datasets:     # COMET dataset paths
experiments:  # PE01-PE10 parameters
```

## Modification Rules

1. Edit `config.yaml` for parameter changes
2. Update `CONFIGURATION.md` when adding fields
3. Verify `pes/core/config.py` handles new fields
4. Test loading with `load_config()`

## Security

- API keys are placeholders: `YOUR_*_API_KEY_HERE`
- Never commit real API keys
- Use environment variables for production:
  ```yaml
  api_key: ${OPENAI_API_KEY}
  ```

## Format Support

Both YAML and JSON supported (REQ-3.1.1):
```python
config = load_config("configs/config.yaml")
config = load_config("configs/config.json")
```

## Adding Experiment Config

When adding new experiment parameters:

1. Add section under `experiments:` in config.yaml
2. Document all fields in CONFIGURATION.md
3. Include types, required/optional, defaults
4. Map to requirements (REQ-X.X.X)
