#!/bin/bash
#
# archive-milestone-files.sh
# Moves optional milestone files (audit, context, research) to the
# milestone archive directory. Skips silently if files don't exist.
#
# Usage: ./scripts/archive-milestone-files.sh <version>
# Example: ./scripts/archive-milestone-files.sh v1.0

set -e

# --- Validation ---
if [ -z "$1" ]; then
  echo "Error: Version argument required"
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION="$1"

# --- Find .planning from git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 1
fi

PLANNING_DIR="$GIT_ROOT/.planning"
MILESTONE_DIR="$PLANNING_DIR/milestones/$VERSION"

if [ ! -d "$MILESTONE_DIR" ]; then
  echo "Error: Milestone directory not found at $MILESTONE_DIR"
  echo "Run archive_milestone step first to create it"
  exit 1
fi

# --- Move files ---
ARCHIVED=0

# Milestone audit
if [ -f "$PLANNING_DIR/${VERSION}-MILESTONE-AUDIT.md" ]; then
  mv "$PLANNING_DIR/${VERSION}-MILESTONE-AUDIT.md" "$MILESTONE_DIR/MILESTONE-AUDIT.md"
  echo "Archived: ${VERSION}-MILESTONE-AUDIT.md → MILESTONE-AUDIT.md"
  ARCHIVED=$((ARCHIVED + 1))
fi

# Milestone context
if [ -f "$PLANNING_DIR/MILESTONE-CONTEXT.md" ]; then
  mv "$PLANNING_DIR/MILESTONE-CONTEXT.md" "$MILESTONE_DIR/CONTEXT.md"
  echo "Archived: MILESTONE-CONTEXT.md → CONTEXT.md"
  ARCHIVED=$((ARCHIVED + 1))
fi

# Research directory
if [ -d "$PLANNING_DIR/research" ]; then
  mv "$PLANNING_DIR/research" "$MILESTONE_DIR/research"
  echo "Archived: research/ → research/"
  ARCHIVED=$((ARCHIVED + 1))
fi

if [ "$ARCHIVED" -eq 0 ]; then
  echo "No optional files to archive (audit, context, research all absent)"
else
  echo ""
  echo "Archived $ARCHIVED item(s) to milestones/$VERSION/"
fi

exit 0
