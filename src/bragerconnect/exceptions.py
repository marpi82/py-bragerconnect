"""
Python library to connect BragerConnect and Home Assistant to work together.

Module exceptions
"""

class AuthError(Exception):
    """Raised when authentication was not succeded"""

class MessageException(Exception):
    """Raised when exception message received"""
