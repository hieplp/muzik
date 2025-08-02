"""
Logging configuration for the Muzik application.
"""

import logging
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logger(
        level: str = "INFO",
        verbose: bool = False,
        log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Setup application logger with rich formatting.
    
    Args:
        level: Logging level
        verbose: Enable verbose logging
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("muzik")
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create console handler with rich formatting
    console = Console()
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add console handler
    logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "muzik") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
