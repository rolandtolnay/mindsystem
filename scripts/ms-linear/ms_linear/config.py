"""Configuration and environment variables."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from ms_linear.errors import ErrorCode, MsLinearError

# API Configuration
LINEAR_API_URL = "https://api.linear.app/graphql"


@dataclass
class LinearConfig:
    """Linear project configuration from .linear.json."""

    team_id: str
    project_id: str | None = None
    default_priority: int = 3
    default_labels: list[str] | None = None

    def __post_init__(self) -> None:
        if self.default_labels is None:
            self.default_labels = []


def get_api_key() -> str:
    """Get LINEAR_API_KEY from environment."""
    api_key = os.environ.get("LINEAR_API_KEY", "")
    if not api_key:
        raise MsLinearError(
            code=ErrorCode.MISSING_API_KEY,
            message="LINEAR_API_KEY environment variable not set",
            suggestions=[
                "Set LINEAR_API_KEY in your shell: export LINEAR_API_KEY='lin_api_...'",
                "Get your API key from Linear Settings > API > Personal API keys",
            ],
        )
    return api_key


def load_config(config_path: Path | None = None) -> LinearConfig:
    """Load configuration from .linear.json.

    Searches upward from current directory if no path specified.
    """
    if config_path is None:
        config_path = find_config_file()

    if config_path is None or not config_path.exists():
        raise MsLinearError(
            code=ErrorCode.MISSING_CONFIG,
            message=".linear.json not found in project",
            suggestions=[
                "Create .linear.json in your project root",
                'Required fields: {"teamId": "uuid", "projectId": "uuid"}',
                "Find IDs from Linear URLs or use `ms-linear states` to discover team",
            ],
        )

    try:
        with open(config_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise MsLinearError(
            code=ErrorCode.INVALID_CONFIG,
            message=f"Invalid JSON in .linear.json: {e}",
            suggestions=["Check .linear.json for syntax errors"],
        )

    if "teamId" not in data:
        raise MsLinearError(
            code=ErrorCode.INVALID_CONFIG,
            message="teamId is required in .linear.json",
            suggestions=['Add "teamId": "your-team-uuid" to .linear.json'],
        )

    return LinearConfig(
        team_id=data["teamId"],
        project_id=data.get("projectId"),
        default_priority=data.get("defaultPriority", 3),
        default_labels=data.get("defaultLabels", []),
    )


def find_config_file() -> Path | None:
    """Find .linear.json by searching upward from original working directory."""
    # Use MS_LINEAR_CWD if set (passed from wrapper script), otherwise fall back to cwd
    start_dir = os.environ.get("MS_LINEAR_CWD")
    current = Path(start_dir) if start_dir else Path.cwd()

    while current != current.parent:
        config_path = current / ".linear.json"
        if config_path.exists():
            return config_path
        current = current.parent

    # Check root
    root_config = current / ".linear.json"
    if root_config.exists():
        return root_config

    return None
