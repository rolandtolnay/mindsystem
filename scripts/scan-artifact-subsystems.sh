#!/bin/bash
#
# scan-artifact-subsystems.sh
# Scans all planning artifact types for `subsystem:` YAML frontmatter values.
#
# Usage: scan-artifact-subsystems.sh [--values-only]
#
#   --values-only   Print only subsystem values (one per line)
#   (default)       Print file<TAB>value pairs

set -e

VALUES_ONLY=false
if [ "$1" = "--values-only" ]; then
  VALUES_ONLY=true
fi

# --- Find .planning from git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 1
fi

PLANNING="$GIT_ROOT/.planning"

# --- Extract subsystem value from a file's YAML frontmatter ---
extract_subsystem() {
  sed -n '/^---$/,/^---$/p' "$1" | grep "^subsystem:" | sed 's/subsystem: *//'
}

# --- Scan a glob pattern and print results under a section header ---
scan_section() {
  local header="$1"
  shift
  echo "=== $header ==="
  for f in "$@"; do
    [ -f "$f" ] || continue
    val=$(extract_subsystem "$f")
    if [ -n "$val" ]; then
      if [ "$VALUES_ONLY" = true ]; then
        echo "$val"
      else
        echo "$f	$val"
      fi
    fi
  done
}

scan_section "Phase SUMMARYs" "$PLANNING"/phases/*/*-SUMMARY.md
scan_section "Adhoc SUMMARYs" "$PLANNING"/adhoc/*-SUMMARY.md
scan_section "Debug docs" "$PLANNING"/debug/*.md "$PLANNING"/debug/resolved/*.md
scan_section "Todos" "$PLANNING"/todos/pending/*.md "$PLANNING"/todos/done/*.md

exit 0
