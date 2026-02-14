#!/bin/bash
#
# cleanup-phase-artifacts.sh
# Deletes raw phase artifacts (CONTEXT, DESIGN, RESEARCH, SUMMARY, UAT,
# VERIFICATION, EXECUTION-ORDER) from all phases in a milestone range.
# Knowledge files in .planning/knowledge/ are not touched.
#
# Usage: ./scripts/cleanup-phase-artifacts.sh <start_phase> <end_phase>
# Example: ./scripts/cleanup-phase-artifacts.sh 1 6

set -e

# --- Validation ---
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Error: Two arguments required"
  echo "Usage: $0 <start_phase> <end_phase>"
  exit 1
fi

START="$1"
END="$2"

if ! [[ "$START" =~ ^[0-9]+$ ]] || ! [[ "$END" =~ ^[0-9]+$ ]]; then
  echo "Error: Both arguments must be numeric"
  echo "Usage: $0 <start_phase> <end_phase>"
  exit 1
fi

if [ "$START" -gt "$END" ]; then
  echo "Error: Start phase ($START) cannot exceed end phase ($END)"
  exit 1
fi

# --- Find .planning from git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 1
fi

PHASES_DIR="$GIT_ROOT/.planning/phases"
if [ ! -d "$PHASES_DIR" ]; then
  echo "Error: Phases directory not found at $PHASES_DIR"
  exit 1
fi

# --- Delete artifacts from each phase in range ---
DELETED=0
for dir in "$PHASES_DIR"/*/; do
  [ -d "$dir" ] || continue
  dirname=$(basename "$dir")
  phase_num="${dirname%%-*}"
  # Strip leading zeros for numeric comparison
  phase_int=$((10#$phase_num))
  if [ "$phase_int" -ge "$START" ] && [ "$phase_int" -le "$END" ]; then
    for f in "$dir"/*-CONTEXT.md "$dir"/*-DESIGN.md "$dir"/*-RESEARCH.md \
             "$dir"/*-SUMMARY.md "$dir"/*-UAT.md "$dir"/*-VERIFICATION.md \
             "$dir"/*-EXECUTION-ORDER.md; do
      if [ -f "$f" ]; then
        rm -f "$f"
        DELETED=$((DELETED + 1))
      fi
    done
  fi
done

echo "Cleaned $DELETED artifact files from phases $START-$END"
exit 0
