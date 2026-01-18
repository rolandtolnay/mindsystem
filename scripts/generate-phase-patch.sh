#!/bin/bash
#
# generate-phase-patch.sh
# Generates a patch file with all implementation changes from a phase,
# excluding documentation and generated files.
#
# Usage: ./scripts/generate-phase-patch.sh <phase_number>
# Example: ./scripts/generate-phase-patch.sh 04
#          ./scripts/generate-phase-patch.sh 4

set -e

# --- Configuration ---
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

# --- Validation ---
if [ -z "$1" ]; then
  echo "Error: Phase number required"
  echo "Usage: $0 <phase_number>"
  exit 1
fi

# --- Find git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 1
fi
cd "$GIT_ROOT"

# --- Normalize phase number (zero-pad if needed) ---
PHASE_INPUT="$1"
if [[ "$PHASE_INPUT" =~ ^[0-9]$ ]]; then
  PHASE_NUMBER=$(printf "%02d" "$PHASE_INPUT")
else
  PHASE_NUMBER="$PHASE_INPUT"
fi

echo "Generating patch for phase $PHASE_NUMBER..."

# --- Find phase commits ---
PHASE_COMMITS=$(git log --oneline | grep -E "\($PHASE_NUMBER-" | cut -d' ' -f1 || true)

if [ -z "$PHASE_COMMITS" ]; then
  echo "No phase commits found matching pattern ($PHASE_NUMBER-"
  echo "Patch skipped"
  exit 0
fi

COMMIT_COUNT=$(echo "$PHASE_COMMITS" | wc -l | tr -d ' ')
echo "Found $COMMIT_COUNT commit(s) for phase $PHASE_NUMBER"

# --- Determine base commit ---
EARLIEST_COMMIT=$(echo "$PHASE_COMMITS" | tail -1)
BASE_COMMIT=$(git rev-parse "${EARLIEST_COMMIT}^" 2>/dev/null || git rev-list --max-parents=0 HEAD)
echo "Base commit: $(git log --oneline -1 "$BASE_COMMIT")"

# --- Find output directory ---
PHASES_DIR=".planning/phases"
PHASE_DIR=$(find "$PHASES_DIR" -maxdepth 1 -type d -name "${PHASE_NUMBER}-*" 2>/dev/null | head -1)

if [ -z "$PHASE_DIR" ]; then
  PHASE_DIR="$PHASES_DIR"
  echo "No phase directory found, saving to $PHASES_DIR/"
else
  echo "Output directory: $PHASE_DIR/"
fi

# Ensure directory exists
mkdir -p "$PHASE_DIR"

# --- Build exclusion arguments ---
EXCLUDE_ARGS=""
for pattern in "${EXCLUSIONS[@]}"; do
  EXCLUDE_ARGS="$EXCLUDE_ARGS ':!$pattern'"
done

# --- Generate diff ---
PATCH_FILE="$PHASE_DIR/${PHASE_NUMBER}-changes.patch"

# Use eval to properly handle the exclusion patterns
eval "git diff \"$BASE_COMMIT\" HEAD -- . $EXCLUDE_ARGS" > "$PATCH_FILE"

# --- Check result ---
if [ ! -s "$PATCH_FILE" ]; then
  rm "$PATCH_FILE"
  echo "No implementation changes outside excluded patterns"
  echo "Patch skipped"
  exit 0
fi

PATCH_LINES=$(wc -l < "$PATCH_FILE" | tr -d ' ')
echo ""
echo "Generated: $PATCH_FILE ($PATCH_LINES lines)"
echo ""
echo "Review:  cat $PATCH_FILE"
echo "Apply:   git apply $PATCH_FILE"
echo "Discard: rm $PATCH_FILE"
