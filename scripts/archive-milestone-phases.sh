#!/bin/bash
#
# archive-milestone-phases.sh
# Consolidates phase summaries, deletes raw artifacts, and moves phase
# directories to the milestone archive.
#
# Usage: ./scripts/archive-milestone-phases.sh <start_phase> <end_phase> <version>
# Example: ./scripts/archive-milestone-phases.sh 1 6 v1.0

set -e

# --- Validation ---
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Error: Three arguments required"
  echo "Usage: $0 <start_phase> <end_phase> <version>"
  exit 1
fi

START="$1"
END="$2"
VERSION="$3"

if ! [[ "$START" =~ ^[0-9]+$ ]] || ! [[ "$END" =~ ^[0-9]+$ ]]; then
  echo "Error: start_phase and end_phase must be numeric"
  echo "Usage: $0 <start_phase> <end_phase> <version>"
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

MILESTONE_DIR="$GIT_ROOT/.planning/milestones/$VERSION"
if [ ! -d "$MILESTONE_DIR" ]; then
  echo "Error: Milestone directory not found at $MILESTONE_DIR"
  echo "Run archive_milestone step first to create it"
  exit 1
fi

# --- Helper: check if phase number is in range (supports decimals like 02.1) ---
in_range() {
  local phase_num="$1"
  echo "$phase_num" | awk -v s="$START" -v e="$END" '{
    # Strip leading zeros for comparison
    val = $1 + 0
    if (val >= s && val <= e + 0.999) exit 0
    else exit 1
  }'
}

# --- Stage 1: Consolidate summaries ---
SUMMARIES_FILE="$MILESTONE_DIR/PHASE-SUMMARIES.md"
SUMMARY_COUNT=0

echo "# Phase Summaries: $VERSION" > "$SUMMARIES_FILE"
echo "" >> "$SUMMARIES_FILE"

for dir in "$PHASES_DIR"/*/; do
  [ -d "$dir" ] || continue
  dirname=$(basename "$dir")
  phase_num="${dirname%%-*}"
  phase_name="${dirname#*-}"

  if in_range "$phase_num"; then
    has_summaries=false
    for f in "$dir"/*-SUMMARY.md; do
      [ -f "$f" ] || continue
      if [ "$has_summaries" = false ]; then
        echo "## Phase $phase_num: $phase_name" >> "$SUMMARIES_FILE"
        echo "" >> "$SUMMARIES_FILE"
        has_summaries=true
      fi
      plan_file=$(basename "$f")
      plan_id="${plan_file%-SUMMARY.md}"
      echo "### $plan_id" >> "$SUMMARIES_FILE"
      echo "" >> "$SUMMARIES_FILE"
      cat "$f" >> "$SUMMARIES_FILE"
      echo "" >> "$SUMMARIES_FILE"
      SUMMARY_COUNT=$((SUMMARY_COUNT + 1))
    done
  fi
done

echo "Stage 1: Consolidated $SUMMARY_COUNT summaries to PHASE-SUMMARIES.md"

# --- Stage 2: Delete artifacts ---
DELETED=0
for dir in "$PHASES_DIR"/*/; do
  [ -d "$dir" ] || continue
  dirname=$(basename "$dir")
  phase_num="${dirname%%-*}"

  if in_range "$phase_num"; then
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

echo "Stage 2: Deleted $DELETED artifact files"

# --- Stage 3: Move phase directories ---
mkdir -p "$MILESTONE_DIR/phases"
MOVED=0
for dir in "$PHASES_DIR"/*/; do
  [ -d "$dir" ] || continue
  dirname=$(basename "$dir")
  phase_num="${dirname%%-*}"

  if in_range "$phase_num"; then
    mv "$dir" "$MILESTONE_DIR/phases/$dirname"
    MOVED=$((MOVED + 1))
  fi
done

echo "Stage 3: Moved $MOVED phase directories to milestones/$VERSION/phases/"
echo ""
echo "Archive complete: $SUMMARY_COUNT summaries, $DELETED artifacts deleted, $MOVED dirs moved"
exit 0
