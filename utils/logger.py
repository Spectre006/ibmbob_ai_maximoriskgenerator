"""Logging configuration and utilities."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from config.settings import settings


def setup_logger(
    name: str = "maximo_jha",
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional, uses settings if not provided)
        level: Log level (optional, uses settings if not provided)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    log_file_path = log_file or settings.log_file
    if log_file_path:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "maximo_jha") -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Set up logger if not already configured
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


# Create default logger instance
default_logger = setup_logger()

# Made with Bob
