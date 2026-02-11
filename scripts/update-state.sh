#!/bin/bash
#
# update-state.sh
# Updates .planning/STATE.md Plan and Status lines based on plan progress.
# Idempotent — same arguments produce the same result.
#
# Usage: ./scripts/update-state.sh <completed_plan_count> <total_plans>
# Example: ./scripts/update-state.sh 2 4
#          (2 of 4 plans complete)
#

set -e

# --- Validation ---
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Error: Two arguments required"
  echo "Usage: $0 <completed_plan_count> <total_plans>"
  exit 1
fi

COMPLETED="$1"
TOTAL="$2"

if ! [[ "$COMPLETED" =~ ^[0-9]+$ ]] || ! [[ "$TOTAL" =~ ^[0-9]+$ ]]; then
  echo "Error: Both arguments must be numeric"
  echo "Usage: $0 <completed_plan_count> <total_plans>"
  exit 1
fi

if [ "$COMPLETED" -gt "$TOTAL" ]; then
  echo "Error: Completed ($COMPLETED) cannot exceed total ($TOTAL)"
  exit 1
fi

# --- Find STATE.md from git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 1
fi

STATE_FILE="$GIT_ROOT/.planning/STATE.md"
if [ ! -f "$STATE_FILE" ]; then
  echo "Error: STATE.md not found at $STATE_FILE"
  exit 1
fi

# --- Update Plan line ---
sed -i '' "s/^Plan:.*/Plan: $COMPLETED of $TOTAL complete in current phase/" "$STATE_FILE"

# --- Update Status line ---
if [ "$COMPLETED" -eq "$TOTAL" ]; then
  sed -i '' "s/^Status:.*/Status: All plans executed, pending verification/" "$STATE_FILE"
else
  sed -i '' "s/^Status:.*/Status: In progress — plan $COMPLETED of $TOTAL complete/" "$STATE_FILE"
fi

echo "STATE.md updated: $COMPLETED of $TOTAL plans complete"
exit 0
