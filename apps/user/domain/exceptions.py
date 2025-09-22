"""
Custom exceptions for the user app domain layer
"""


class UserNotFoundError(Exception):
    """Raised when a user is not found"""

    pass


class UserPermissionError(Exception):
    """Raised when a user doesn't have permission to perform an action"""

    pass


class UserValidationError(Exception):
    """Raised when user data fails validation"""

    pass


class UserAuthenticationError(Exception):
    """Raised when user authentication fails"""

    pass


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists"""

    pass
