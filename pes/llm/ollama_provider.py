"""
Ollama provider for local open-source models.

Supports: Llama 3, Magicoder, Mistral, and other Ollama-compatible models
"""

from typing import Dict, Any, Optional, List
import ollama
from ollama import ResponseError

from .base import BaseLLMProvider, LLMResponse
from .retry import with_retry, RateLimitError
from ..core.exceptions import LLMError


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider for local model inference.

    Configuration:
        model: Model name (e.g., llama3:70b, magicoder)
        host: Ollama server URL (default: http://localhost:11434)
    """

    def _validate_config(self) -> None:
        """Validate Ollama-specific configuration."""
        if not self.model:
            raise LLMError("Ollama provider requires 'model' in configuration")

        # Configure host
        self.host = self.config.get('host', 'http://localhost:11434')

        # Initialize client
        self.client = ollama.Client(host=self.host)

        # Verify model is available
        try:
            self.client.show(self.model)
        except ResponseError as e:
            if 'not found' in str(e).lower():
                raise LLMError(
                    f"Model '{self.model}' not found. "
                    f"Pull it with: ollama pull {self.model}"
                ) from e
            raise

    @with_retry()
    def _make_request(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Make request to Ollama API."""
        try:
            # Build options
            options = {'temperature': temperature}
            if max_tokens:
                options['num_predict'] = max_tokens
            if stop_sequences:
                options['stop'] = stop_sequences

            # Make API call
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options=options
            )

            # Estimate tokens (Ollama provides this in some versions)
            prompt_tokens = response.get('prompt_eval_count', len(prompt.split()))
            completion_tokens = response.get('eval_count', len(response['response'].split()))

            return LLMResponse(
                text=response['response'],
                model=response.get('model', self.model),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                finish_reason='stop' if response.get('done') else 'length',
                duration_seconds=response.get('total_duration', 0) / 1e9,
                metadata={
                    'provider': 'ollama',
                    'load_duration': response.get('load_duration', 0) / 1e9,
                    'eval_duration': response.get('eval_duration', 0) / 1e9
                }
            )

        except ResponseError as e:
            raise LLMError(f"Ollama error: {e}") from e
