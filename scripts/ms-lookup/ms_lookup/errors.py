"""Error codes and error handling."""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for CLI responses."""

    MISSING_API_KEY = "MISSING_API_KEY"
    LIBRARY_NOT_FOUND = "LIBRARY_NOT_FOUND"
    API_ERROR = "API_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"


class MsLookupError(Exception):
    """Base exception for ms-lookup errors."""

    def __init__(self, code: ErrorCode, message: str, suggestions: list[str] | None = None):
        self.code = code
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)
