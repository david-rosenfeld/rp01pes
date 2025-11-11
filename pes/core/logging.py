"""
Logging utilities for the Preliminary Experiments System.

This module provides centralized logging configuration with support for
experiment-specific logging, multiple log levels, and structured output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ExperimentLogger:
    """
    Experiment-aware logger that provides structured logging for PES.
    
    This class wraps Python's logging module with experiment-specific
    context and structured output formatting.
    """
    
    def __init__(self, name: str, log_dir: Optional[Path] = None, level: int = logging.INFO):
        """
        Initialize an experiment logger.
        
        Args:
            name: Logger name (typically module name or experiment ID)
            log_dir: Directory for log files (None for console-only)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Create logger instance
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatter with timestamp and context
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler if log directory specified
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create log file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f"{name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            self.logger.info(f"Logging to file: {log_file}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        self._log_with_context(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional context."""
        self._log_with_context(logging.CRITICAL, message, kwargs)
    
    def _log_with_context(self, level: int, message: str, context: dict):
        """
        Internal method to log message with structured context.
        
        Args:
            level: Logging level
            message: Log message
            context: Dictionary of context key-value pairs
        """
        # If context provided, append it to message
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            message = f"{message} | {context_str}"
        
        # Log at appropriate level
        self.logger.log(level, message)
    
    def experiment_start(self, experiment_id: str, experiment_type: str):
        """
        Log the start of an experiment.
        
        Args:
            experiment_id: Unique experiment identifier
            experiment_type: Type of experiment (e.g., "model_selection")
        """
        self.info(
            f"Starting experiment: {experiment_id}",
            experiment_type=experiment_type,
            status="started"
        )
    
    def experiment_end(self, experiment_id: str, status: str, duration: float):
        """
        Log the end of an experiment.
        
        Args:
            experiment_id: Unique experiment identifier
            status: Completion status ("success", "failed", "skipped")
            duration: Execution duration in seconds
        """
        self.info(
            f"Completed experiment: {experiment_id}",
            status=status,
            duration_seconds=f"{duration:.2f}"
        )
    
    def llm_request(self, model: str, prompt_tokens: int, max_tokens: Optional[int] = None):
        """
        Log an LLM API request.
        
        Args:
            model: Model identifier
            prompt_tokens: Number of tokens in prompt
            max_tokens: Maximum tokens for response
        """
        self.debug(
            "LLM request",
            model=model,
            prompt_tokens=prompt_tokens,
            max_tokens=max_tokens or "default"
        )
    
    def llm_response(self, model: str, completion_tokens: int, total_tokens: int, duration: float):
        """
        Log an LLM API response.
        
        Args:
            model: Model identifier
            completion_tokens: Tokens in completion
            total_tokens: Total tokens used
            duration: Request duration in seconds
        """
        self.debug(
            "LLM response",
            model=model,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            duration_seconds=f"{duration:.2f}"
        )


def get_logger(name: str, log_dir: Optional[str] = None, level: str = "INFO") -> ExperimentLogger:
    """
    Factory function to create a logger instance.
    
    This is the primary way to create loggers throughout the system.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        log_dir: Directory for log files (None for console-only)
        level: Logging level as string ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    
    Returns:
        ExperimentLogger instance
    
    Example:
        >>> logger = get_logger(__name__, log_dir="logs", level="DEBUG")
        >>> logger.info("System initialized")
    """
    # Convert string level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    
    # Convert log_dir to Path if provided
    log_path = Path(log_dir) if log_dir else None
    
    return ExperimentLogger(name, log_path, log_level)
