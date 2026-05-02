"""Data formatting utilities."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object (uses current time if None)
        format_str: Format string
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime(format_str)


def format_iso_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to ISO 8601 format.
    
    Args:
        dt: Datetime object (uses current time if None)
    
    Returns:
        ISO formatted datetime string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def format_work_order_id(work_order_id: str) -> str:
    """
    Format work order ID to standard format.
    
    Args:
        work_order_id: Raw work order ID
    
    Returns:
        Formatted work order ID
    """
    return work_order_id.upper().strip()


def format_hazard_list(hazards: List[Dict[str, Any]]) -> str:
    """
    Format hazard list for display.
    
    Args:
        hazards: List of hazard dictionaries
    
    Returns:
        Formatted hazard list as string
    """
    if not hazards:
        return "No hazards identified"
    
    formatted = []
    for idx, hazard in enumerate(hazards, 1):
        risk_level = hazard.get('risk_level', 'Unknown')
        description = hazard.get('description', 'No description')
        formatted.append(f"{idx}. [{risk_level}] {description}")
    
    return "\n".join(formatted)


def format_json_response(data: Any, indent: int = 2) -> str:
    """
    Format data as JSON string.
    
    Args:
        data: Data to format
        indent: Indentation level
    
    Returns:
        JSON formatted string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_duration_ms(duration_ms: float) -> str:
    """
    Format duration in milliseconds to human-readable format.
    
    Args:
        duration_ms: Duration in milliseconds
    
    Returns:
        Formatted duration string
    """
    if duration_ms < 1000:
        return f"{duration_ms:.0f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms / 1000:.2f}s"
    else:
        minutes = int(duration_ms / 60000)
        seconds = (duration_ms % 60000) / 1000
        return f"{minutes}m {seconds:.0f}s"

# Made with Bob
