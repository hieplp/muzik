"""
Tests for the configuration module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from muzik.core.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.get("app.name") == "Muzik"
        assert config.get("app.version") == "0.1.0"
        assert config.get("app.debug") is False
        assert config.get("logging.level") == "INFO"
        assert config.get("display.colors") is True
    
    def test_set_and_get(self):
        """Test setting and getting configuration values."""
        config = Config()
        
        config.set("test.key", "test_value")
        assert config.get("test.key") == "test_value"
        
        config.set("nested.key.value", 123)
        assert config.get("nested.key.value") == 123
    
    def test_get_with_default(self):
        """Test getting configuration with default value."""
        config = Config()
        
        assert config.get("nonexistent.key", "default") == "default"
        assert config.get("nonexistent.key") is None
    
    def test_environment_variables(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        os.environ["MUZIK_DEBUG"] = "true"
        os.environ["MUZIK_LOG_LEVEL"] = "DEBUG"
        
        try:
            config = Config()
            
            assert config.get("app.debug") is True
            assert config.get("logging.level") == "DEBUG"
        finally:
            # Clean up
            del os.environ["MUZIK_DEBUG"]
            del os.environ["MUZIK_LOG_LEVEL"]
    
    def test_config_file(self):
        """Test loading configuration from file."""
        config_data = """
app:
  name: "Test App"
  debug: true
logging:
  level: "DEBUG"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_data)
            config_file = f.name
        
        try:
            config = Config(config_file=config_file)
            
            assert config.get("app.name") == "Test App"
            assert config.get("app.debug") is True
            assert config.get("logging.level") == "DEBUG"
        finally:
            Path(config_file).unlink()
    
    def test_save_config(self):
        """Test saving configuration to file."""
        config = Config()
        config.set("test.key", "test_value")
        
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            config.save(config_file)
            
            # Load the saved config
            loaded_config = Config(config_file=config_file)
            assert loaded_config.get("test.key") == "test_value"
        finally:
            Path(config_file).unlink()
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Config()
        config.set("test.key", "test_value")
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["test"]["key"] == "test_value" 