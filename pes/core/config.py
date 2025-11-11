"""
Configuration management for the Preliminary Experiments System.

This module provides loading, validation, and management of configuration
files in YAML or JSON format, implementing REQ-3.1.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import ConfigurationError
from .logging import get_logger

logger = get_logger(__name__)


class ConfigurationManager:
    """
    Manages configuration loading and validation for PES.
    
    This class implements REQ-3.1 (Configuration Management) with support
    for YAML and JSON formats, validation, and hierarchical structure.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path
        self.config = {}
        
        if config_path:
            self.load(config_path)
    
    def load(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Supports both YAML (.yaml, .yml) and JSON (.json) formats.
        Implements REQ-3.1.1.1, REQ-3.1.1.2, and REQ-3.1.1.3.
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            Loaded configuration dictionary
        
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        # Convert to Path object
        path = Path(config_path)
        
        # Check file exists
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        # Determine format from extension
        extension = path.suffix.lower()
        
        logger.info(f"Loading configuration from: {config_path}")
        
        try:
            # Load based on format
            if extension in ['.yaml', '.yml']:
                self.config = self._load_yaml(path)
            elif extension == '.json':
                self.config = self._load_json(path)
            else:
                raise ConfigurationError(
                    f"Unsupported configuration format: {extension}. "
                    f"Supported formats: .yaml, .yml, .json"
                )
            
            logger.info("Configuration loaded successfully")
            return self.config
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Error parsing configuration file: {e}")
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Implements REQ-3.1.1.1: Parse and load YAML 1.2 specification.
        
        Args:
            path: Path to YAML file
        
        Returns:
            Parsed configuration dictionary
        """
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            raise ConfigurationError(
                f"YAML configuration must be a mapping/dictionary, got {type(config).__name__}"
            )
        
        return config
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """
        Load JSON configuration file.
        
        Implements REQ-3.1.1.2: Parse and load JSON (RFC 8259).
        
        Args:
            path: Path to JSON file
        
        Returns:
            Parsed configuration dictionary
        """
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not isinstance(config, dict):
            raise ConfigurationError(
                f"JSON configuration must be an object/dictionary, got {type(config).__name__}"
            )
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Supports nested keys using dot notation (e.g., "llm.openai.api_key").
        
        Args:
            key: Configuration key (supports dot notation for nested values)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        # Split key by dots for nested access
        keys = key.split('.')
        value = self.config
        
        # Traverse nested structure
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (e.g., "experiments", "models", "datasets")
        
        Returns:
            Configuration section as dictionary
        
        Raises:
            ConfigurationError: If section doesn't exist
        """
        if section not in self.config:
            raise ConfigurationError(f"Configuration section '{section}' not found")
        
        section_config = self.config[section]
        if not isinstance(section_config, dict):
            raise ConfigurationError(f"Section '{section}' must be a dictionary")
        
        return section_config
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key (supports dot notation)
        
        Returns:
            True if key exists, False otherwise
        """
        try:
            value = self.get(key)
            return value is not None
        except:
            return False
    
    def validate_required_sections(self, *sections: str) -> None:
        """
        Validate that required configuration sections exist.
        
        Args:
            *sections: Section names that must be present
        
        Raises:
            ConfigurationError: If any required section is missing
        """
        missing = []
        for section in sections:
            if section not in self.config:
                missing.append(section)
        
        if missing:
            raise ConfigurationError(
                f"Missing required configuration sections: {', '.join(missing)}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get complete configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()


def load_config(config_path: str) -> ConfigurationManager:
    """
    Factory function to load configuration.
    
    This is the primary way to load configurations throughout the system.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        ConfigurationManager instance with loaded config
    
    Example:
        >>> config = load_config("config.yaml")
        >>> api_key = config.get("llm.openai.api_key")
    """
    return ConfigurationManager(config_path)
