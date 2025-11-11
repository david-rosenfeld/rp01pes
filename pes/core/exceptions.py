"""
Custom exception classes for the Preliminary Experiments System.

This module defines exception classes used throughout PES for handling
various error conditions in a structured manner.
"""


class PESError(Exception):
    """
    Base exception class for all PES errors.
    
    This serves as the parent class for all custom exceptions in the system,
    allowing for broad exception catching when needed.
    """
    pass


class ConfigurationError(PESError):
    """Exception raised for configuration-related errors."""
    pass


class DatasetError(PESError):
    """Exception raised for dataset loading or processing errors."""
    pass


class LLMError(PESError):
    """Exception raised for LLM integration errors."""
    pass


class ExperimentError(PESError):
    """Exception raised during experiment execution."""
    pass


class StorageError(PESError):
    """Exception raised for data storage and retrieval errors."""
    pass


class AnalysisError(PESError):
    """Exception raised during statistical analysis or reporting."""
    pass
