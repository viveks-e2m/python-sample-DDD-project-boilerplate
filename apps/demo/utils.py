"""
Utility functions for the demo app
"""
import html
import re
import logging
from typing import Optional
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if it doesn't exist
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def validate_demo_priority(priority: int) -> bool:
    """
    Validate that the demo item priority is within acceptable range
    
    Args:
        priority (int): The priority value to validate
        
    Returns:
        bool: True if priority is valid, False otherwise
    """
    return 0 <= priority <= 10


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks
    
    Args:
        text (str): The text to sanitize
        
    Returns:
        str: The sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = html.escape(text)
    # Remove potentially dangerous characters
    clean_text = re.sub(r'[<>"\']', '', clean_text)
    return clean_text.strip()


def format_demo_item_response(demo_item) -> dict:
    """
    Format a demo item for API response
    
    Args:
        demo_item: The demo item to format
        
    Returns:
        dict: The formatted demo item
    """
    return {
        "id": demo_item.id,
        "title": demo_item.title,
        "description": demo_item.description,
        "priority": demo_item.priority,
        "created_by": demo_item.created_by,
        "created_at": demo_item.created_at.isoformat() if demo_item.created_at else None,
        "modified_at": demo_item.modified_at.isoformat() if demo_item.modified_at else None
    }


def audit_log(operation: str, user: str, item_id: Optional[int] = None, details: Optional[str] = None):
    """
    Log audit information for sensitive operations
    
    Args:
        operation (str): The operation being performed
        user (str): The user performing the operation
        item_id (int, optional): The ID of the item being operated on
        details (str, optional): Additional details about the operation
    """
    log_message = f"AUDIT: User '{user}' performed '{operation}'"
    if item_id:
        log_message += f" on item ID {item_id}"
    if details:
        log_message += f" - Details: {details}"
    
    logger.info(log_message)


class DemoAppException(Exception):
    """
    Custom exception class for demo app
    """
    pass


class DemoItemNotFound(DemoAppException):
    """
    Raised when a demo item is not found
    """
    pass


class DemoItemPermissionError(DemoAppException):
    """
    Raised when a user doesn't have permission to perform an action on a demo item
    """
    pass