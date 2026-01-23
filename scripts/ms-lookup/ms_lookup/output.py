"""JSON output formatting."""

import json
from typing import Any

from ms_lookup.errors import MsLookupError


def format_success(
    command: str,
    query: str,
    results: list[dict],
    metadata: dict,
    library: str | None = None,
) -> dict:
    """Format successful response."""
    response = {
        "success": True,
        "command": command,
        "query": query,
        "results": results,
        "metadata": metadata,
    }
    if library:
        response["library"] = library
    return response


def format_error(command: str, error: MsLookupError) -> dict:
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


def output_json(data: dict, pretty: bool = False) -> str:
    """Convert data to JSON string."""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)
