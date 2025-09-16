"""
Custom exceptions for the demo app domain layer
"""

class DemoItemNotFoundError(Exception):
    """Raised when a demo item is not found"""
    pass


class DemoItemPermissionError(Exception):
    """Raised when a user doesn't have permission to perform an action on a demo item"""
    pass


class DemoItemValidationError(Exception):
    """Raised when demo item data fails validation"""
    pass