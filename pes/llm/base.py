"""
Abstract LLM interface for provider-agnostic model interactions.

This module defines the abstract base class for LLM providers,
implementing REQ-3.2 (LLM Integration Layer).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

from ..core.logging import get_logger
from ..core.exceptions import LLMError

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """
    Standardized LLM response structure.
    
    This class provides a uniform response format regardless of provider,
    implementing REQ-3.2.4 (Response Processing).
    """
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str
    duration_seconds: float
    metadata: Dict[str, Any]


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM provider implementations must inherit from this class and
    implement the required abstract methods. This provides a uniform
    interface for interacting with different LLM APIs.
    
    Implements REQ-3.2.1 (LLM Abstraction Layer).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LLM provider.
        
        Args:
            config: Provider configuration dictionary containing:
                - api_key: API authentication key
                - model: Model identifier
                - api_base: Optional API base URL
                - Additional provider-specific parameters
        """
        self.config = config
        self.model = config.get('model')
        self.api_key = config.get('api_key')
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Validate required configuration
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate provider-specific configuration.
        
        Raises:
            LLMError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Make API request to LLM provider.
        
        This method must be implemented by each provider to handle
        provider-specific API calls.
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse object
        
        Raises:
            LLMError: If API request fails
        """
        pass
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text completion from prompt.
        
        This is the main public interface for text generation, providing
        a uniform API across all providers.
        
        Implements REQ-3.2.3 (LLM Request Parameters).
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: List of stop sequences
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse object containing generated text and metadata
        
        Raises:
            LLMError: If generation fails
        """
        # Validate parameters
        if not isinstance(prompt, str) or not prompt.strip():
            raise LLMError("Prompt must be a non-empty string")
        
        if not (0.0 <= temperature <= 2.0):
            raise LLMError(f"Temperature must be between 0.0 and 2.0, got {temperature}")
        
        # Log request
        prompt_token_estimate = len(prompt.split()) * 1.3  # Rough estimate
        self.logger.llm_request(
            self.model,
            int(prompt_token_estimate),
            max_tokens
        )
        
        # Record start time
        start_time = time.time()
        
        try:
            # Make provider-specific request
            response = self._make_request(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop_sequences=stop_sequences,
                **kwargs
            )
            
            # Record duration
            duration = time.time() - start_time
            response.duration_seconds = duration
            
            # Log response
            self.logger.llm_response(
                response.model,
                response.completion_tokens,
                response.total_tokens,
                duration
            )
            
            return response
            
        except Exception as e:
            # Log error
            self.logger.error(f"LLM generation failed: {str(e)}")
            raise LLMError(f"Generation failed: {e}") from e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured model.
        
        Returns:
            Dictionary with model information:
                - provider: Provider name
                - model: Model identifier
                - capabilities: List of capabilities
        """
        return {
            'provider': self.__class__.__name__,
            'model': self.model,
            'capabilities': ['text_generation']
        }


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider for testing without API calls.
    
    This provider returns synthetic responses without making actual API calls,
    useful for testing and development.
    """
    
    def _validate_config(self) -> None:
        """Validate mock provider config (minimal validation)."""
        if not self.model:
            self.model = "mock-model-1.0"
    
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate mock response.
        
        Args:
            prompt: Input prompt
            **kwargs: Ignored parameters
        
        Returns:
            Mock LLMResponse
        """
        # Generate synthetic response
        response_text = f"[MOCK RESPONSE] This is a simulated response to the prompt: {prompt[:50]}..."
        
        # Estimate tokens
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response_text.split())
        
        return LLMResponse(
            text=response_text,
            model=self.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            finish_reason="stop",
            duration_seconds=0.1,
            metadata={'provider': 'mock'}
        )
