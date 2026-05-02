"""Input validation utilities."""

import re
from typing import Optional


def validate_work_order_id(work_order_id: str) -> bool:
    """
    Validate work order ID format.
    
    Args:
        work_order_id: Work order ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not work_order_id:
        return False
    
    # Basic validation: alphanumeric, hyphens, underscores
    # Adjust pattern based on actual Maximo work order format
    pattern = r'^[A-Z0-9\-_]{1,50}$'
    return bool(re.match(pattern, work_order_id.upper()))


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input by removing potentially harmful characters.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (optional)
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters and trim whitespace
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    sanitized = sanitized.strip()
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_report_format(format_str: str) -> bool:
    """
    Validate report format string.
    
    Args:
        format_str: Format string to validate
    
    Returns:
        True if valid format, False otherwise
    """
    valid_formats = ['pdf', 'docx', 'html']
    return format_str.lower() in valid_formats

# Made with Bob
