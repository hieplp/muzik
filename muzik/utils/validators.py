"""
Validation utilities for the Muzik application.
"""

import re
from typing import Any, Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_required(value: Any, field_name: str) -> None:
    """
    Validate that a required field is not None or empty.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Raises:
        ValueError: If value is None or empty
    """
    if value is None:
        raise ValueError(f"{field_name} is required")

    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{field_name} cannot be empty")

    if isinstance(value, (list, dict, set)) and not value:
        raise ValueError(f"{field_name} cannot be empty")


def validate_length(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None,
                    field_name: str = "Value") -> None:
    """
    Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Name of the field for error messages
        
    Raises:
        ValueError: If length constraints are not met
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    length = len(value)

    if min_length is not None and length < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")

    if max_length is not None and length > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters long")


def validate_range(value: int, min_value: Optional[int] = None, max_value: Optional[int] = None,
                   field_name: str = "Value") -> None:
    """
    Validate numeric range.
    
    Args:
        value: Number to validate
        min_value: Minimum value
        max_value: Maximum value
        field_name: Name of the field for error messages
        
    Raises:
        ValueError: If range constraints are not met
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")

    if min_value is not None and value < min_value:
        raise ValueError(f"{field_name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{field_name} must be at most {max_value}")


def validate_choice(value: Any, choices: list, field_name: str = "Value") -> None:
    """
    Validate that value is one of the allowed choices.
    
    Args:
        value: Value to validate
        choices: List of allowed values
        field_name: Name of the field for error messages
        
    Raises:
        ValueError: If value is not in choices
    """
    if value not in choices:
        raise ValueError(f"{field_name} must be one of: {', '.join(map(str, choices))}")


def validate_file_exists(file_path: str) -> None:
    """
    Validate that a file exists.
    
    Args:
        file_path: Path to the file
        
    Raises:
        FileNotFoundError: If file does not exist
    """
    from pathlib import Path

    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")


def validate_directory_exists(dir_path: str) -> None:
    """
    Validate that a directory exists.
    
    Args:
        dir_path: Path to the directory
        
    Raises:
        FileNotFoundError: If directory does not exist
    """
    from pathlib import Path

    path = Path(dir_path)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {dir_path}")
