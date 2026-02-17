#!/bin/bash
#
# gather-milestone-stats.sh
# Gathers milestone readiness status and statistics from the filesystem
# and git history. Outputs structured text for the LLM to present.
#
# Usage: ./scripts/gather-milestone-stats.sh <start_phase> <end_phase>
# Example: ./scripts/gather-milestone-stats.sh 1 6

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

# --- Helper: check if phase number is in range (supports decimals like 02.1) ---
in_range() {
  local phase_num="$1"
  echo "$phase_num" | awk -v s="$START" -v e="$END" '{
    val = $1 + 0
    if (val >= s && val <= e + 0.999) exit 0
    else exit 1
  }'
}

# ============================================================
# READINESS
# ============================================================
echo "=== Readiness ==="
echo ""

PHASE_COUNT=0
PLAN_COUNT=0
COMPLETE=0
INCOMPLETE_LIST=""
PHASE_DETAILS=""

for dir in "$PHASES_DIR"/*/; do
  [ -d "$dir" ] || continue
  dirname=$(basename "$dir")
  phase_num="${dirname%%-*}"
  phase_name="${dirname#*-}"

  if in_range "$phase_num"; then
    PHASE_COUNT=$((PHASE_COUNT + 1))
    phase_plans=0
    phase_complete=0

    for plan in "$dir"/*-PLAN.md; do
      [ -f "$plan" ] || continue
      PLAN_COUNT=$((PLAN_COUNT + 1))
      phase_plans=$((phase_plans + 1))
      plan_base=$(basename "$plan" -PLAN.md)
      summary="$dir/${plan_base}-SUMMARY.md"
      if [ -f "$summary" ]; then
        COMPLETE=$((COMPLETE + 1))
        phase_complete=$((phase_complete + 1))
      else
        INCOMPLETE_LIST+="  $(basename "$dir")/$(basename "$plan")"$'\n'
      fi
    done

    PHASE_DETAILS+="- Phase $phase_num: $phase_name ($phase_complete/$phase_plans plans)"$'\n'
  fi
done

echo "Phases: $PHASE_COUNT (range $START-$END)"
echo "Plans: $PLAN_COUNT total, $COMPLETE complete"
echo ""
echo "$PHASE_DETAILS"

if [ "$COMPLETE" -eq "$PLAN_COUNT" ] && [ "$PLAN_COUNT" -gt 0 ]; then
  echo "Status: READY"
else
  INCOMPLETE=$((PLAN_COUNT - COMPLETE))
  echo "Incomplete ($INCOMPLETE):"
  echo "$INCOMPLETE_LIST"
  echo "Status: NOT READY"
fi

# ============================================================
# GIT STATS
# ============================================================
echo ""
echo "=== Git Stats ==="
echo ""

# Collect commits matching Mindsystem phase convention: feat(XX-YY), fix(XX-YY), etc.
ALL_COMMITS=""
for i in $(seq "$START" "$END"); do
  phase=$(printf "%02d" "$i")
  commits=$(git log --all --format="%H %ai %s" --grep="($phase-" 2>/dev/null || true)
  if [ -n "$commits" ]; then
    ALL_COMMITS+="$commits"$'\n'
  fi
done

# Also capture decimal phase commits (e.g., 02.1 inserted phases)
for dir in "$PHASES_DIR"/*/; do
  [ -d "$dir" ] || continue
  dirname=$(basename "$dir")
  phase_num="${dirname%%-*}"
  case "$phase_num" in
    *.*) # Decimal phase — not captured by seq
      if in_range "$phase_num"; then
        commits=$(git log --all --format="%H %ai %s" --grep="($phase_num-" 2>/dev/null || true)
        if [ -n "$commits" ]; then
          ALL_COMMITS+="$commits"$'\n'
        fi
      fi
      ;;
  esac
done

# Remove empty lines, deduplicate, sort by date
ALL_COMMITS=$(echo "$ALL_COMMITS" | grep -v '^$' | sort -u -k2,3)

if [ -n "$ALL_COMMITS" ]; then
  COMMIT_COUNT=$(echo "$ALL_COMMITS" | wc -l | tr -d ' ')
  FIRST_LINE=$(echo "$ALL_COMMITS" | head -1)
  LAST_LINE=$(echo "$ALL_COMMITS" | tail -1)
  FIRST_HASH=$(echo "$FIRST_LINE" | awk '{print $1}')
  LAST_HASH=$(echo "$LAST_LINE" | awk '{print $1}')
  FIRST_DATE=$(echo "$FIRST_LINE" | awk '{print $2}')
  LAST_DATE=$(echo "$LAST_LINE" | awk '{print $2}')
  FIRST_MSG=$(echo "$FIRST_LINE" | cut -d' ' -f4-)
  LAST_MSG=$(echo "$LAST_LINE" | cut -d' ' -f4-)

  # Calculate days
  DAYS=$(python3 -c "from datetime import date; print((date.fromisoformat('$LAST_DATE') - date.fromisoformat('$FIRST_DATE')).days)" 2>/dev/null || echo "?")

  echo "Commits: $COMMIT_COUNT"
  echo "Git range: ${FIRST_HASH:0:7}..${LAST_HASH:0:7}"
  echo "First: $FIRST_DATE — $FIRST_MSG"
  echo "Last:  $LAST_DATE — $LAST_MSG"
  echo "Timeline: $DAYS days ($FIRST_DATE → $LAST_DATE)"

  # Diff stats for the range
  DIFFSTAT=$(git diff --shortstat "${FIRST_HASH}^..${LAST_HASH}" 2>/dev/null || true)
  if [ -n "$DIFFSTAT" ]; then
    echo "Changes:$DIFFSTAT"
  fi
else
  echo "No commits found matching phase patterns (expected 'feat(XX-YY): ...')"
  echo "Determine git range manually from git log"
fi

echo ""
exit 0
