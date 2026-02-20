# CLAUDE.md - LLM Integration

## Scope

Provider abstraction layer for LLM APIs.

## Status

- Mock provider: Complete
- Real providers (OpenAI, Anthropic, Google): TODO

## Architecture

```
BaseLLMProvider (abstract)
├── MockLLMProvider (complete)
├── OpenAIProvider (TODO)
├── AnthropicProvider (TODO)
└── GoogleProvider (TODO)
```

## Provider Interface

All providers must implement:

```python
class MyProvider(BaseLLMProvider):
    def _validate_config(self):
        # Validate required config fields
        # Raise LLMError on invalid config

    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        # Call provider API
        # Return standardized LLMResponse
```

## LLMResponse Structure

```python
@dataclass
class LLMResponse:
    content: str           # Response text
    model: str             # Model identifier
    prompt_tokens: int     # Input token count
    completion_tokens: int # Output token count
    latency_ms: float      # Request duration
    raw_response: Any      # Provider-specific data
```

## Factory Usage

```python
from pes.llm.factory import get_provider, register_provider

# Get existing provider
provider = get_provider('mock', config_dict)

# Register new provider
register_provider('myprovider', MyProviderClass)
```

## MockLLMProvider Features

- `response_mode='realistic'` - Generates traceability-like responses
- `accuracy_bias` - Configurable base accuracy (default 0.85)
- Temperature-aware responses
- Deterministic based on prompt hashing

## Adding New Providers

1. Create `<provider>_provider.py`
2. Inherit from `BaseLLMProvider`
3. Implement `_validate_config()` and `_make_request()`
4. Handle rate limits with exponential backoff
5. Map provider errors to `LLMError`
6. Register in `factory.py`
7. Add config examples to `configs/CONFIGURATION.md`

## Security

- Never log full API keys
- Never hardcode credentials
- Read keys from config or environment variables
