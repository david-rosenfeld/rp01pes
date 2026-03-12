"""
Google Gemini provider implementation.

Supports: Gemini 2.5 Pro, Gemini 2.5 Flash
Uses the google-genai SDK (unified SDK for Google AI and Vertex AI).
"""

from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types
from .base import BaseLLMProvider, LLMResponse
from .retry import with_retry, RateLimitError
from ..core.exceptions import LLMError
class GoogleProvider(BaseLLMProvider):
    """
    Google Gemini API provider.

    Configuration:
        api_key: Google AI API key (required)
        model: Model identifier (default: gemini-2.5-pro)
    """

    def _validate_config(self) -> None:
        """Validate Google-specific configuration."""
        if not self.api_key:
            raise LLMError("Google provider requires 'api_key' in configuration")

        if not self.model:
            self.model = "gemini-2.5-pro"

        # Initialize client with API key
        self.client = genai.Client(api_key=self.api_key)

    @with_retry()
    def _make_request(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Make request to Google Gemini API."""
        try:
            # Build generation config
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                stop_sequences=stop_sequences
            )

            # Make API call
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            # Extract token counts (may not always be available)
            usage = getattr(response, 'usage_metadata', None)
            prompt_tokens = getattr(usage, 'prompt_token_count', 0) if usage else 0
            completion_tokens = getattr(usage, 'candidates_token_count', 0) if usage else 0

            # Get finish reason
            candidates = getattr(response, 'candidates', [])
            finish_reason = 'unknown'
            safety_ratings = []
            if candidates:
                finish_reason = getattr(candidates[0], 'finish_reason', 'unknown')
                if hasattr(finish_reason, 'name'):
                    finish_reason = finish_reason.name
                sr = getattr(candidates[0], 'safety_ratings', [])
                safety_ratings = [
                    {'category': getattr(r.category, 'name', str(r.category)),
                     'probability': getattr(r.probability, 'name', str(r.probability))}
                    for r in sr
                ] if sr else []

            return LLMResponse(
                text=response.text,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                finish_reason=finish_reason,
                duration_seconds=0.0,
                metadata={
                    'provider': 'google',
                    'safety_ratings': safety_ratings
                }
            )

        except Exception as e:
            err_msg = str(e).lower()
            if 'resource' in err_msg and 'exhaust' in err_msg or '429' in err_msg:
                raise RateLimitError(f"Google rate limit: {e}") from e
            raise LLMError(f"Google provider error: {e}") from e
