#!/bin/bash
# Wrapper script for gsd-lookup CLI
# Handles uv/pip installation transparently

# Source uv environment if available
if [ -f "$HOME/.local/bin/env" ]; then
  source "$HOME/.local/bin/env"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/gsd-lookup"

if command -v uv &> /dev/null; then
  # Prefer uv if available (faster)
  uv sync --quiet 2>/dev/null
  uv run python -m gsd_lookup "$@"
else
  # Fall back to pip
  pip install -q -e . 2>/dev/null
  python3 -m gsd_lookup "$@"
fi
