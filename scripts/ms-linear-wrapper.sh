#!/bin/bash
# Wrapper script for ms-linear CLI
# Handles uv/pip installation transparently

# Source uv environment if available
if [ -f "$HOME/.local/bin/env" ]; then
  source "$HOME/.local/bin/env"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGINAL_CWD="$(pwd)"
cd "$SCRIPT_DIR/ms-linear"

if command -v uv &> /dev/null; then
  # Prefer uv if available (faster)
  uv sync --quiet 2>/dev/null
  MS_LINEAR_CWD="$ORIGINAL_CWD" uv run python -m ms_linear "$@"
else
  # Fall back to pip
  pip install -q -e . 2>/dev/null
  MS_LINEAR_CWD="$ORIGINAL_CWD" python3 -m ms_linear "$@"
fi
