#!/bin/bash
#
# generate-adhoc-patch.sh
# Generates a patch file from an adhoc commit, excluding documentation and generated files.
#
# Usage: ./scripts/generate-adhoc-patch.sh <commit-hash> <output-path>
# Example: ./scripts/generate-adhoc-patch.sh abc123f .planning/adhoc/2026-01-26-fix-bug.patch

set -e

# --- Configuration ---
# Same exclusions as generate-phase-patch.sh
EXCLUSIONS=(
  # Documentation
  '.planning'

  # Flutter/Dart generated
  '*.g.dart'
  '*.freezed.dart'
  '*.gr.dart'
  'generated'
  '.dart_tool'

  # Next.js/TypeScript generated
  'node_modules'
  '.next'
  'dist'
  'build'
  '*.d.ts'
  '.turbo'

  # Common build artifacts
  '*.lock'
)

# --- Parse arguments ---
COMMIT_HASH="$1"
OUTPUT_PATH="$2"

# --- Validation ---
if [ -z "$COMMIT_HASH" ] || [ -z "$OUTPUT_PATH" ]; then
  echo "Error: Commit hash and output path required"
  echo "Usage: $0 <commit-hash> <output-path>"
  exit 1
fi

# --- Find git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 1
fi
cd "$GIT_ROOT"

# --- Verify commit exists ---
if ! git rev-parse "$COMMIT_HASH" >/dev/null 2>&1; then
  echo "Error: Commit $COMMIT_HASH not found"
  exit 1
fi

# --- Build exclusion arguments ---
EXCLUDE_ARGS=""
for pattern in "${EXCLUSIONS[@]}"; do
  EXCLUDE_ARGS="$EXCLUDE_ARGS ':!$pattern'"
done

# --- Generate diff from parent commit to specified commit ---
eval "git diff \"${COMMIT_HASH}^\" \"$COMMIT_HASH\" -- . $EXCLUDE_ARGS" > "$OUTPUT_PATH"

# --- Check result ---
if [ ! -s "$OUTPUT_PATH" ]; then
  rm -f "$OUTPUT_PATH"
  echo "No implementation changes outside excluded patterns"
  echo "Patch skipped"
  exit 0
fi

PATCH_LINES=$(wc -l < "$OUTPUT_PATH" | tr -d ' ')
echo "Generated: $OUTPUT_PATH ($PATCH_LINES lines)"
