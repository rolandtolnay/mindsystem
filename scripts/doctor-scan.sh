#!/bin/bash
#
# doctor-scan.sh
# Single-pass diagnostic scan of the .planning/ tree.
# Reports on 6 health check categories with structured output.
#
# Usage: ./scripts/doctor-scan.sh
#
# Exit codes:
#   0 — all checks pass
#   1 — one or more checks failed
#   2 — .planning/ or config.json missing (cannot scan)

set -e

# --- Find .planning from git root ---
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
  echo "Error: Not in a git repository"
  exit 2
fi

PLANNING="$GIT_ROOT/.planning"
if [ ! -d "$PLANNING" ]; then
  echo "Error: No .planning/ directory found"
  exit 2
fi

CONFIG="$PLANNING/config.json"
if [ ! -f "$CONFIG" ]; then
  echo "Error: No config.json found at $CONFIG"
  exit 2
fi

MILESTONES_FILE="$PLANNING/MILESTONES.md"
PHASES_DIR="$PLANNING/phases"
MILESTONES_DIR="$PLANNING/milestones"
KNOWLEDGE_DIR="$PLANNING/knowledge"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
FAILED_CHECKS=""

# --- Helper: record check result ---
record_result() {
  local status="$1"
  local name="$2"
  case "$status" in
    PASS) PASS_COUNT=$((PASS_COUNT + 1)) ;;
    FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)); FAILED_CHECKS="$FAILED_CHECKS $name" ;;
    SKIP) SKIP_COUNT=$((SKIP_COUNT + 1)) ;;
  esac
}

# ============================================================
# CHECK 1: Subsystem Vocabulary
# ============================================================
echo "=== Subsystem Vocabulary ==="

SUBSYSTEM_COUNT=$(jq -r '.subsystems // [] | length' "$CONFIG" 2>/dev/null || echo "0")

if [ "$SUBSYSTEM_COUNT" -eq 0 ]; then
  echo "Status: FAIL"
  echo "No subsystems array in config.json (or empty)"
  record_result "FAIL" "Subsystem Vocabulary"
else
  echo "Subsystems: $SUBSYSTEM_COUNT configured"
  jq -r '.subsystems[]' "$CONFIG" 2>/dev/null | sed 's/^/  - /'

  # Run artifact scan to check for mismatches
  SCAN_SCRIPT="$(dirname "$0")/scan-artifact-subsystems.sh"
  if [ -x "$SCAN_SCRIPT" ]; then
    CANONICAL=$(jq -r '.subsystems[]' "$CONFIG" 2>/dev/null)
    ARTIFACT_VALUES=$("$SCAN_SCRIPT" --values-only 2>/dev/null | grep -v '^===' | sort -u)
    MISMATCHES=""
    while IFS= read -r val; do
      [ -z "$val" ] && continue
      if ! echo "$CANONICAL" | grep -qx "$val"; then
        MISMATCHES="$MISMATCHES $val"
      fi
    done <<< "$ARTIFACT_VALUES"

    if [ -n "$MISMATCHES" ]; then
      echo "Status: FAIL"
      echo "Artifact values not in canonical list:$MISMATCHES"
      record_result "FAIL" "Subsystem Vocabulary"
    else
      ARTIFACT_COUNT=$("$SCAN_SCRIPT" --values-only 2>/dev/null | grep -v '^===' | wc -l | tr -d ' ')
      echo "Artifacts scanned: $ARTIFACT_COUNT (all OK)"
      echo "Status: PASS"
      record_result "PASS" "Subsystem Vocabulary"
    fi
  else
    echo "Status: PASS"
    echo "(scan-artifact-subsystems.sh not found — skipped artifact validation)"
    record_result "PASS" "Subsystem Vocabulary"
  fi
fi
echo ""

# ============================================================
# CHECK 2: Milestone Directory Structure
# ============================================================
echo "=== Milestone Directory Structure ==="

if [ ! -d "$MILESTONES_DIR" ]; then
  # No milestones directory at all — check if MILESTONES.md has entries
  if [ -f "$MILESTONES_FILE" ] && grep -q "^## " "$MILESTONES_FILE" 2>/dev/null; then
    echo "Status: FAIL"
    echo "MILESTONES.md has entries but no milestones/ directory"
    record_result "FAIL" "Milestone Directory Structure"
  else
    echo "Status: SKIP"
    echo "No completed milestones"
    record_result "SKIP" "Milestone Directory Structure"
  fi
else
  # Look for flat files matching v*-*.md directly in milestones/
  FLAT_FILES=""
  FLAT_COUNT=0
  for f in "$MILESTONES_DIR"/v*-*.md; do
    [ -f "$f" ] || continue
    FLAT_FILES="$FLAT_FILES  $(basename "$f")"$'\n'
    FLAT_COUNT=$((FLAT_COUNT + 1))
  done

  if [ "$FLAT_COUNT" -gt 0 ]; then
    echo "Status: FAIL"
    echo "Found $FLAT_COUNT flat file(s) in milestones/ (old format):"
    echo "$FLAT_FILES"
    # Check if corresponding versioned directories exist
    for f in "$MILESTONES_DIR"/v*-*.md; do
      [ -f "$f" ] || continue
      fname=$(basename "$f")
      # Extract version prefix: v0.1-ROADMAP.md -> v0.1
      version=$(echo "$fname" | sed 's/^\(v[0-9.]*\)-.*/\1/')
      if [ -d "$MILESTONES_DIR/$version" ]; then
        echo "  $fname → directory $version/ exists (can restructure)"
      else
        echo "  $fname → directory $version/ missing (need to create)"
      fi
    done
    record_result "FAIL" "Milestone Directory Structure"
  else
    # Count versioned directories
    DIR_COUNT=0
    for d in "$MILESTONES_DIR"/v*/; do
      [ -d "$d" ] || continue
      DIR_COUNT=$((DIR_COUNT + 1))
    done

    if [ "$DIR_COUNT" -eq 0 ]; then
      echo "Status: SKIP"
      echo "No completed milestones"
      record_result "SKIP" "Milestone Directory Structure"
    else
      echo "Status: PASS"
      echo "$DIR_COUNT versioned milestone directories"
      record_result "PASS" "Milestone Directory Structure"
    fi
  fi
fi
echo ""

# ============================================================
# CHECK 3: Phase Archival
# ============================================================
echo "=== Phase Archival ==="

if [ ! -f "$MILESTONES_FILE" ] || ! grep -q "Phases completed" "$MILESTONES_FILE" 2>/dev/null; then
  echo "Status: SKIP"
  echo "No completed milestones with phase ranges in MILESTONES.md"
  record_result "SKIP" "Phase Archival"
else
  ORPHAN_COUNT=0
  ORPHAN_LIST=""

  # Parse each milestone's phase range from MILESTONES.md
  while IFS= read -r line; do
    # Extract range like "1-6" or "7-8"
    range=$(echo "$line" | grep -o '[0-9]\+-[0-9]\+')
    [ -z "$range" ] && continue
    range_start=$(echo "$range" | cut -d'-' -f1)
    range_end=$(echo "$range" | cut -d'-' -f2)

    # Check if any phase directories in this range still exist in phases/
    for i in $(seq "$range_start" "$range_end"); do
      phase_prefix=$(printf "%02d" "$i")
      for dir in "$PHASES_DIR"/${phase_prefix}-*/; do
        [ -d "$dir" ] || continue
        dirname=$(basename "$dir")
        ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
        ORPHAN_LIST="$ORPHAN_LIST  $dirname (should be archived)"$'\n'
      done
    done
  done < <(grep "Phases completed" "$MILESTONES_FILE")

  if [ "$ORPHAN_COUNT" -gt 0 ]; then
    echo "Status: FAIL"
    echo "Found $ORPHAN_COUNT orphaned phase directories from completed milestones:"
    echo "$ORPHAN_LIST"
    record_result "FAIL" "Phase Archival"
  else
    echo "Status: PASS"
    echo "All completed milestone phases are archived"
    record_result "PASS" "Phase Archival"
  fi
fi
echo ""

# ============================================================
# CHECK 4: Knowledge Files
# ============================================================
echo "=== Knowledge Files ==="

if [ "$SUBSYSTEM_COUNT" -eq 0 ]; then
  echo "Status: SKIP"
  echo "No subsystems configured — knowledge check requires subsystem vocabulary"
  record_result "SKIP" "Knowledge Files"
elif [ ! -d "$KNOWLEDGE_DIR" ]; then
  echo "Status: FAIL"
  echo "Knowledge directory missing: .planning/knowledge/"
  echo "Expected files for $SUBSYSTEM_COUNT subsystems"
  record_result "FAIL" "Knowledge Files"
else
  MISSING_KNOWLEDGE=""
  MISSING_COUNT=0
  PRESENT_COUNT=0
  while IFS= read -r subsystem; do
    [ -z "$subsystem" ] && continue
    if [ -f "$KNOWLEDGE_DIR/$subsystem.md" ]; then
      PRESENT_COUNT=$((PRESENT_COUNT + 1))
    else
      MISSING_COUNT=$((MISSING_COUNT + 1))
      MISSING_KNOWLEDGE="$MISSING_KNOWLEDGE  $subsystem.md"$'\n'
    fi
  done < <(jq -r '.subsystems[]' "$CONFIG" 2>/dev/null)

  # Check for orphaned knowledge files (not in subsystem list)
  ORPHAN_KNOWLEDGE=""
  ORPHAN_K_COUNT=0
  for f in "$KNOWLEDGE_DIR"/*.md; do
    [ -f "$f" ] || continue
    fname=$(basename "$f" .md)
    if ! jq -r '.subsystems[]' "$CONFIG" 2>/dev/null | grep -qx "$fname"; then
      ORPHAN_K_COUNT=$((ORPHAN_K_COUNT + 1))
      ORPHAN_KNOWLEDGE="$ORPHAN_KNOWLEDGE  $fname.md (not in subsystems list)"$'\n'
    fi
  done

  if [ "$MISSING_COUNT" -gt 0 ] || [ "$ORPHAN_K_COUNT" -gt 0 ]; then
    echo "Status: FAIL"
    echo "Coverage: $PRESENT_COUNT/$SUBSYSTEM_COUNT subsystems have knowledge files"
    if [ "$MISSING_COUNT" -gt 0 ]; then
      echo "Missing:"
      echo "$MISSING_KNOWLEDGE"
    fi
    if [ "$ORPHAN_K_COUNT" -gt 0 ]; then
      echo "Orphaned:"
      echo "$ORPHAN_KNOWLEDGE"
    fi
    record_result "FAIL" "Knowledge Files"
  else
    echo "Status: PASS"
    echo "All $SUBSYSTEM_COUNT subsystems have knowledge files"
    record_result "PASS" "Knowledge Files"
  fi
fi
echo ""

# ============================================================
# CHECK 5: Phase Summaries
# ============================================================
echo "=== Phase Summaries ==="

if [ ! -d "$MILESTONES_DIR" ]; then
  echo "Status: SKIP"
  echo "No milestones directory"
  record_result "SKIP" "Phase Summaries"
else
  MISSING_SUMMARIES=""
  MISSING_S_COUNT=0
  CHECKED=0

  for d in "$MILESTONES_DIR"/v*/; do
    [ -d "$d" ] || continue
    CHECKED=$((CHECKED + 1))
    version=$(basename "$d")
    if [ ! -f "$d/PHASE-SUMMARIES.md" ]; then
      MISSING_S_COUNT=$((MISSING_S_COUNT + 1))
      MISSING_SUMMARIES="$MISSING_SUMMARIES  $version/PHASE-SUMMARIES.md"$'\n'
    fi
  done

  if [ "$CHECKED" -eq 0 ]; then
    echo "Status: SKIP"
    echo "No versioned milestone directories"
    record_result "SKIP" "Phase Summaries"
  elif [ "$MISSING_S_COUNT" -gt 0 ]; then
    echo "Status: FAIL"
    echo "Missing PHASE-SUMMARIES.md in $MISSING_S_COUNT milestone(s):"
    echo "$MISSING_SUMMARIES"
    record_result "FAIL" "Phase Summaries"
  else
    echo "Status: PASS"
    echo "All $CHECKED milestones have PHASE-SUMMARIES.md"
    record_result "PASS" "Phase Summaries"
  fi
fi
echo ""

# ============================================================
# CHECK 6: PLAN Cleanup
# ============================================================
echo "=== PLAN Cleanup ==="

if [ ! -f "$MILESTONES_FILE" ] || ! grep -q "Phases completed" "$MILESTONES_FILE" 2>/dev/null; then
  echo "Status: SKIP"
  echo "No completed milestones — active phase PLANs are expected"
  record_result "SKIP" "PLAN Cleanup"
else
  LEFTOVER_PLANS=""
  LEFTOVER_COUNT=0

  # Check phases/ for PLANs belonging to completed milestones
  while IFS= read -r line; do
    range=$(echo "$line" | grep -o '[0-9]\+-[0-9]\+')
    [ -z "$range" ] && continue
    range_start=$(echo "$range" | cut -d'-' -f1)
    range_end=$(echo "$range" | cut -d'-' -f2)

    for i in $(seq "$range_start" "$range_end"); do
      phase_prefix=$(printf "%02d" "$i")
      for plan in "$PHASES_DIR"/${phase_prefix}-*/*-PLAN.md; do
        [ -f "$plan" ] || continue
        LEFTOVER_COUNT=$((LEFTOVER_COUNT + 1))
        LEFTOVER_PLANS="$LEFTOVER_PLANS  $(echo "$plan" | sed "s|$GIT_ROOT/.planning/||")"$'\n'
      done
    done
  done < <(grep "Phases completed" "$MILESTONES_FILE")

  # Check archived milestone phase directories for leftover PLANs
  for d in "$MILESTONES_DIR"/v*/phases/*/; do
    [ -d "$d" ] || continue
    for plan in "$d"*-PLAN.md; do
      [ -f "$plan" ] || continue
      LEFTOVER_COUNT=$((LEFTOVER_COUNT + 1))
      LEFTOVER_PLANS="$LEFTOVER_PLANS  $(echo "$plan" | sed "s|$GIT_ROOT/.planning/||")"$'\n'
    done
  done

  if [ "$LEFTOVER_COUNT" -gt 0 ]; then
    echo "Status: FAIL"
    echo "Found $LEFTOVER_COUNT leftover PLAN file(s) in completed phases:"
    echo "$LEFTOVER_PLANS"
    record_result "FAIL" "PLAN Cleanup"
  else
    echo "Status: PASS"
    echo "No leftover PLAN files in completed phases"
    record_result "PASS" "PLAN Cleanup"
  fi
fi
echo ""

# ============================================================
# SUMMARY
# ============================================================
TOTAL=$((PASS_COUNT + FAIL_COUNT + SKIP_COUNT))
echo "=== Summary ==="
echo "Checks: $TOTAL total, $PASS_COUNT passed, $FAIL_COUNT failed, $SKIP_COUNT skipped"

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "Issues:$FAILED_CHECKS"
  exit 1
else
  echo "All checks passed"
  exit 0
fi
