"""
Configuration management for the Muzik application.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: Optional[str] = None) -> None:
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self.config_data: Dict[str, Any] = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment."""
        # Default configuration
        self.config_data = {
            "app": {
                "name": "Muzik",
                "version": "0.1.0",
                "debug": False,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "display": {
                "colors": True,
                "unicode": True,
            },
        }
        
        # Load from config file if provided
        if self.config_file and Path(self.config_file).exists():
            self._load_from_file(self.config_file)
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self._merge_config(self.config_data, file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "MUZIK_DEBUG": ("app", "debug", bool),
            "MUZIK_LOG_LEVEL": ("logging", "level", str),
            "MUZIK_COLORS": ("display", "colors", bool),
        }
        
        for env_var, (section, key, value_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if value_type == bool:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                self.config_data[section][key] = value
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'app.name')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'app.name')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_file: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config_file: Optional path to save config (uses default if not provided)
        """
        if not config_file:
            config_file = self.config_file or "config.yaml"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Could not save config to {config_file}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config_data.copy() 