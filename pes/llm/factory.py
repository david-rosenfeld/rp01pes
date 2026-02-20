"""
LLM provider factory and registry.

This module provides a registry of available LLM providers and
a factory function to instantiate providers based on configuration.
"""

from typing import Dict, Any, Type

from .base import BaseLLMProvider, MockLLMProvider
from ..core.exceptions import LLMError


# Registry of available providers
_PROVIDER_REGISTRY: Dict[str, Type[BaseLLMProvider]] = {
    'mock': MockLLMProvider,
}

# Conditionally register providers based on available dependencies
try:
    from .openai_provider import OpenAIProvider
    _PROVIDER_REGISTRY['openai'] = OpenAIProvider
except ImportError:
    pass

try:
    from .anthropic_provider import AnthropicProvider
    _PROVIDER_REGISTRY['anthropic'] = AnthropicProvider
except ImportError:
    pass

try:
    from .google_provider import GoogleProvider
    _PROVIDER_REGISTRY['google'] = GoogleProvider
except ImportError:
    pass

try:
    from .ollama_provider import OllamaProvider
    _PROVIDER_REGISTRY['ollama'] = OllamaProvider
except ImportError:
    pass


def register_provider(name: str, provider_class: Type[BaseLLMProvider]) -> None:
    """
    Register a new LLM provider.

    This allows dynamic addition of new provider implementations.

    Args:
        name: Provider name (e.g., "openai", "anthropic")
        provider_class: Provider class (must inherit from BaseLLMProvider)

    Raises:
        LLMError: If provider_class doesn't inherit from BaseLLMProvider
    """
    if not issubclass(provider_class, BaseLLMProvider):
        raise LLMError(
            f"Provider class must inherit from BaseLLMProvider, "
            f"got {provider_class.__name__}"
        )

    _PROVIDER_REGISTRY[name.lower()] = provider_class


def get_provider(provider_name: str, config: Dict[str, Any]) -> BaseLLMProvider:
    """
    Factory function to create LLM provider instance.

    This is the main way to instantiate LLM providers throughout the system.

    Args:
        provider_name: Name of provider ("openai", "anthropic", "mock", etc.)
        config: Provider configuration dictionary

    Returns:
        Instantiated provider

    Raises:
        LLMError: If provider not found

    Example:
        >>> config = {'model': 'gpt-4', 'api_key': 'sk-...'}
        >>> provider = get_provider('openai', config)
        >>> response = provider.generate("Hello, world!")
    """
    provider_name = provider_name.lower()

    if provider_name not in _PROVIDER_REGISTRY:
        available = ', '.join(_PROVIDER_REGISTRY.keys())
        raise LLMError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {available}"
        )

    provider_class = _PROVIDER_REGISTRY[provider_name]
    return provider_class(config)


def list_providers() -> list:
    """
    Get list of available provider names.

    Returns:
        List of registered provider names
    """
    return list(_PROVIDER_REGISTRY.keys())
