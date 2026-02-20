"""
OpenAI LLM provider implementation.

Supports: GPT-4, GPT-4-Turbo, GPT-3.5-Turbo, GPT-5 (when available)
"""

from typing import Dict, Any, Optional, List
import openai
from openai import OpenAI, RateLimitError as OpenAIRateLimitError

from .base import BaseLLMProvider, LLMResponse
from .retry import with_retry, RetryConfig, RateLimitError
from ..core.exceptions import LLMError


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider.

    Configuration:
        api_key: OpenAI API key (required)
        model: Model identifier (default: gpt-4)
        api_base: Optional custom API base URL
        organization: Optional organization ID
    """

    def _validate_config(self) -> None:
        """Validate OpenAI-specific configuration."""
        if not self.api_key:
            raise LLMError("OpenAI provider requires 'api_key' in configuration")

        if not self.model:
            self.model = "gpt-4"

        # Initialize client
        self.client = OpenAI(
            api_key=self.api_key,
            organization=self.config.get('organization'),
            base_url=self.config.get('api_base')
        )

    @with_retry()
    def _make_request(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Make request to OpenAI API."""
        try:
            # Build messages (chat completion format)
            messages = [{"role": "user", "content": prompt}]

            # Add system message if provided
            system_prompt = kwargs.get('system_prompt')
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop_sequences,
                **{k: v for k, v in kwargs.items() if k != 'system_prompt'}
            )

            # Extract response data
            choice = response.choices[0]
            usage = response.usage

            return LLMResponse(
                text=choice.message.content,
                model=response.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                finish_reason=choice.finish_reason,
                duration_seconds=0.0,  # Set by caller
                metadata={
                    'provider': 'openai',
                    'response_id': response.id,
                    'system_fingerprint': response.system_fingerprint
                }
            )

        except OpenAIRateLimitError as e:
            # Extract retry-after if available
            retry_after = getattr(e, 'retry_after', None)
            raise RateLimitError(f"OpenAI rate limit: {e}", retry_after) from e

        except openai.APIError as e:
            raise LLMError(f"OpenAI API error: {e}") from e
