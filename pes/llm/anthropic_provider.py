"""
Anthropic Claude provider implementation.

Supports: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku, Claude Sonnet 4
"""

from typing import Dict, Any, Optional, List
import anthropic
from anthropic import RateLimitError as AnthropicRateLimitError

from .base import BaseLLMProvider, LLMResponse
from .retry import with_retry, RateLimitError
from ..core.exceptions import LLMError


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude API provider.

    Configuration:
        api_key: Anthropic API key (required)
        model: Model identifier (default: claude-sonnet-4)
        max_tokens: Maximum tokens for response (required by Anthropic)
    """

    def _validate_config(self) -> None:
        """Validate Anthropic-specific configuration."""
        if not self.api_key:
            raise LLMError("Anthropic provider requires 'api_key' in configuration")

        if not self.model:
            self.model = "claude-sonnet-4-20250514"

        # Anthropic requires max_tokens
        self.default_max_tokens = self.config.get('max_tokens', 4096)

        # Initialize client
        self.client = anthropic.Anthropic(api_key=self.api_key)

    @with_retry()
    def _make_request(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Make request to Anthropic API."""
        try:
            # Use configured max_tokens if not specified
            if max_tokens is None:
                max_tokens = self.default_max_tokens

            # Build request
            request_kwargs = {
                'model': self.model,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': [{"role": "user", "content": prompt}]
            }

            # Add system prompt if provided
            system_prompt = kwargs.get('system_prompt')
            if system_prompt:
                request_kwargs['system'] = system_prompt

            # Add stop sequences if provided
            if stop_sequences:
                request_kwargs['stop_sequences'] = stop_sequences

            # Make API call
            response = self.client.messages.create(**request_kwargs)

            # Extract response data
            content_block = response.content[0]

            return LLMResponse(
                text=content_block.text,
                model=response.model,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                duration_seconds=0.0,
                metadata={
                    'provider': 'anthropic',
                    'response_id': response.id
                }
            )

        except AnthropicRateLimitError as e:
            raise RateLimitError(f"Anthropic rate limit: {e}") from e

        except anthropic.APIError as e:
            raise LLMError(f"Anthropic API error: {e}") from e
