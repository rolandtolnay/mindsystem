#!/bin/bash
#
# validate-execution-order.sh
# Validates EXECUTION-ORDER.md against plan files in a phase directory.
# Checks bidirectional consistency and warns about file conflicts within waves.
#
# Usage: ./scripts/validate-execution-order.sh <phase_directory>
# Example: ./scripts/validate-execution-order.sh .planning/phases/03-auth
#

set -e

# --- Validation ---
if [ -z "$1" ]; then
  echo "Error: Phase directory required"
  echo "Usage: $0 <phase_directory>"
  exit 1
fi

PHASE_DIR="$1"

if [ ! -d "$PHASE_DIR" ]; then
  echo "FAIL: Directory does not exist: $PHASE_DIR"
  exit 1
fi

EXEC_ORDER="$PHASE_DIR/EXECUTION-ORDER.md"
if [ ! -f "$EXEC_ORDER" ]; then
  echo "FAIL: EXECUTION-ORDER.md not found in $PHASE_DIR"
  exit 1
fi

# --- Collect plan files on disk ---
DISK_PLANS=$(ls -1 "$PHASE_DIR"/*-PLAN.md 2>/dev/null | xargs -I{} basename {} | sort)
DISK_COUNT=$(echo "$DISK_PLANS" | grep -c . 2>/dev/null || echo 0)

if [ "$DISK_COUNT" -eq 0 ]; then
  echo "FAIL: No *-PLAN.md files found in $PHASE_DIR"
  exit 1
fi

# --- Parse EXECUTION-ORDER.md for plan filenames ---
# Pattern matches phase-prefixed names like 03-01-PLAN.md, 16-01-PLAN.md, 72.1-01-PLAN.md
ORDER_PLANS=$(grep -oE '[0-9][0-9.]*-[0-9]+-PLAN\.md' "$EXEC_ORDER" | sort -u)
ORDER_COUNT=$(echo "$ORDER_PLANS" | grep -c . 2>/dev/null || echo 0)

# --- Check 1: Every disk plan is listed in EXECUTION-ORDER.md ---
ERRORS=""
while IFS= read -r plan; do
  [ -z "$plan" ] && continue
  if ! echo "$ORDER_PLANS" | grep -qx "$plan"; then
    ERRORS="${ERRORS}  Missing from EXECUTION-ORDER.md: $plan\n"
  fi
done <<< "$DISK_PLANS"

# --- Check 2: Every plan in EXECUTION-ORDER.md exists on disk ---
while IFS= read -r plan; do
  [ -z "$plan" ] && continue
  if ! echo "$DISK_PLANS" | grep -qx "$plan"; then
    ERRORS="${ERRORS}  Listed in EXECUTION-ORDER.md but file missing: $plan\n"
  fi
done <<< "$ORDER_PLANS"

if [ -n "$ERRORS" ]; then
  echo "FAIL: Plan/execution-order mismatch"
  printf "%b" "$ERRORS"
  exit 1
fi

# --- Check 3 (warning): File conflicts within waves ---
CURRENT_WAVE=""
WAVE_COUNT=0
CURRENT_WAVE_FILES=""

while IFS= read -r line; do
  if echo "$line" | grep -qE '^## Wave [0-9]+'; then
    CURRENT_WAVE=$(echo "$line" | grep -oE '[0-9]+')
    WAVE_COUNT=$((WAVE_COUNT + 1))
    CURRENT_WAVE_FILES=""
  elif [ -n "$CURRENT_WAVE" ]; then
    PLAN_FILE=$(echo "$line" | grep -oE '[0-9][0-9.]*-[0-9]+-PLAN\.md' || true)
    if [ -n "$PLAN_FILE" ] && [ -f "$PHASE_DIR/$PLAN_FILE" ]; then
      # Extract **Files:** lines from plan
      FILE_PATHS=$(grep -E '^\*\*Files:\*\*' "$PHASE_DIR/$PLAN_FILE" | sed 's/\*\*Files:\*\*//g' | tr ',' '\n' | sed 's/`//g; s/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$' || true)
      while IFS= read -r fpath; do
        [ -z "$fpath" ] && continue
        if echo "$CURRENT_WAVE_FILES" | grep -qF "|$fpath|"; then
          echo "WARNING: File '$fpath' appears in multiple plans within Wave $CURRENT_WAVE"
        else
          CURRENT_WAVE_FILES="${CURRENT_WAVE_FILES}|$fpath|"
        fi
      done <<< "$FILE_PATHS"
    fi
  fi
done < "$EXEC_ORDER"

# --- Handle edge case: no waves parsed ---
if [ "$WAVE_COUNT" -eq 0 ]; then
  echo "FAIL: No '## Wave N' headers found in EXECUTION-ORDER.md"
  exit 1
fi

echo "PASS: $DISK_COUNT plans across $WAVE_COUNT waves"
exit 0
