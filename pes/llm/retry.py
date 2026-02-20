"""
Rate limiting and retry logic for LLM providers.

Implements REQ-3.2.5 (Rate Limiting and Retry Logic).
"""

from typing import Callable, Type, Tuple
from functools import wraps
import time
import random

from ..core.logging import get_logger
from ..core.exceptions import LLMError

logger = get_logger(__name__)

# Try to import tenacity; if not available, use fallback
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False


class RateLimitError(LLMError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str, retry_after: float = None):
        super().__init__(message)
        self.retry_after = retry_after


class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 5,
        min_wait: float = 1.0,
        max_wait: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = None
    ):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (RateLimitError,)


def with_retry(config: RetryConfig = None):
    """
    Decorator to add retry logic to provider methods.

    Usage:
        @with_retry(RetryConfig(max_attempts=3))
        def _make_request(self, prompt, **kwargs):
            ...

    If tenacity is not installed, this decorator is a no-op.
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(config.max_attempts),
                wait=wait_exponential(
                    multiplier=config.min_wait,
                    max=config.max_wait,
                    exp_base=config.exponential_base
                ),
                retry=retry_if_exception_type(config.retryable_exceptions),
                before_sleep=before_sleep_log(logger, log_level=20)  # INFO
            )
            @wraps(func)
            def wrapper_with_retry(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper_with_retry
        else:
            # Fallback: no retry, just pass through
            @wraps(func)
            def wrapper_no_retry(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper_no_retry
    return decorator
