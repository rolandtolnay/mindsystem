"""Error codes and error handling."""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for CLI responses."""

    MISSING_API_KEY = "MISSING_API_KEY"
    MISSING_CONFIG = "MISSING_CONFIG"
    INVALID_CONFIG = "INVALID_CONFIG"
    ISSUE_NOT_FOUND = "ISSUE_NOT_FOUND"
    STATE_NOT_FOUND = "STATE_NOT_FOUND"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    API_ERROR = "API_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    INVALID_INPUT = "INVALID_INPUT"


class MsLinearError(Exception):
    """Base exception for ms-linear errors."""

    def __init__(self, code: ErrorCode, message: str, suggestions: list[str] | None = None):
        self.code = code
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)
