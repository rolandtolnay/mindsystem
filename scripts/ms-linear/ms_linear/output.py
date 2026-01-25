"""JSON output formatting."""

import json
from typing import Any

from ms_linear.errors import MsLinearError


def format_success(
    command: str,
    result: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format successful response."""
    response: dict[str, Any] = {
        "success": True,
        "command": command,
        "result": result,
    }
    if metadata:
        response["metadata"] = metadata
    return response


def format_error(command: str, error: MsLinearError) -> dict[str, Any]:
    """Format error response."""
    error_dict: dict[str, Any] = {
        "code": error.code.value,
        "message": error.message,
    }
    if error.suggestions:
        error_dict["suggestions"] = error.suggestions

    return {
        "success": False,
        "command": command,
        "error": error_dict,
    }


def output_json(data: dict[str, Any], pretty: bool = False) -> str:
    """Convert data to JSON string."""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)
