#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Mindsystem CLI tools.

Single-file CLI with subcommands for all mechanical operations:
phase discovery, state updates, artifact counting, diagnostics,
patch generation, archival, and planning context scanning.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# JSON encoder
# ---------------------------------------------------------------------------


class _SafeEncoder(json.JSONEncoder):
    """Handle YAML types that json.dump can't serialize (date, datetime)."""

    def default(self, o: object) -> Any:
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def find_git_root() -> Path:
    """Find the git repository root. Exit with error if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Not in a git repository", file=sys.stderr)
        sys.exit(1)


def find_planning_dir() -> Path:
    """Find .planning/ from git root. Exit with error if missing."""
    planning = find_git_root() / ".planning"
    if not planning.is_dir():
        print("Error: No .planning/ directory found", file=sys.stderr)
        sys.exit(1)
    return planning


def slugify(name: str) -> str:
    """Convert a milestone name to a URL-safe slug.

    Lowercase, replace spaces/underscores with hyphens, strip non-alphanumeric
    (except hyphens), collapse consecutive hyphens, trim edges.
    """
    s = name.lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-")
    return s


def find_planning_dir_optional() -> Path | None:
    """Find .planning/ from git root. Return None if missing."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        planning = Path(result.stdout.strip()) / ".planning"
        return planning if planning.is_dir() else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def normalize_phase(phase_str: str) -> str:
    """Normalize phase input: '5' -> '05', '05' -> '05', '2.1' -> '02.1'."""
    match = re.match(r"^(\d+)(?:\.(\d+))?$", phase_str)
    if not match:
        return phase_str
    integer = int(match.group(1))
    decimal = match.group(2)
    if decimal:
        return f"{integer:02d}.{decimal}"
    return f"{integer:02d}"


def find_phase_dir(planning: Path, phase: str) -> Path | None:
    """Find the phase directory matching a normalized phase number."""
    phases_dir = planning / "phases"
    if not phases_dir.is_dir():
        return None
    matches = sorted(phases_dir.glob(f"{phase}-*"))
    dirs = [m for m in matches if m.is_dir()]
    return dirs[0] if dirs else None


def run_git(*args: str) -> str:
    """Run a git command and return stdout. Raise on failure."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def parse_json_config(planning: Path) -> dict:
    """Read .planning/config.json."""
    config_path = planning / "config.json"
    if not config_path.is_file():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def in_range(phase_num: str, start: int, end: int) -> bool:
    """Check if a phase number (possibly decimal) is within start..end range."""
    try:
        val = float(phase_num)
        return start <= val <= end + 0.999
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# YAML frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None


# ---------------------------------------------------------------------------
# Patch generation helpers (shared between generate-phase-patch and
# generate-adhoc-patch)
# ---------------------------------------------------------------------------

PATCH_EXCLUSIONS = [
    # Documentation
    ".planning",
    # Flutter/Dart generated
    "*.g.dart",
    "*.freezed.dart",
    "*.gr.dart",
    "generated",
    ".dart_tool",
    # Next.js/TypeScript generated
    "node_modules",
    ".next",
    "dist",
    "build",
    "*.d.ts",
    ".turbo",
    # Common build artifacts
    "*.lock",
]


def build_exclude_pathspecs() -> list[str]:
    """Build git pathspec exclusion list."""
    return [f":!{p}" for p in PATCH_EXCLUSIONS]


# ===================================================================
# Subcommand: update-state
# ===================================================================


def cmd_update_state(args: argparse.Namespace) -> None:
    """Update .planning/STATE.md Plan and Status lines.

    Contract:
        Args: completed (int), total (int)
        Output: text — confirmation message
        Exit codes: 0 = success, 1 = STATE.md missing or completed > total
        Side effects: writes STATE.md
    """
    completed = args.completed
    total = args.total

    if completed > total:
        print(f"Error: Completed ({completed}) cannot exceed total ({total})", file=sys.stderr)
        sys.exit(1)

    state_file = find_git_root() / ".planning" / "STATE.md"
    if not state_file.is_file():
        print(f"Error: STATE.md not found at {state_file}", file=sys.stderr)
        sys.exit(1)

    text = state_file.read_text(encoding="utf-8")

    # Update Plan line
    text = re.sub(
        r"^Plan:.*$",
        f"Plan: {completed} of {total} complete in current phase",
        text,
        flags=re.MULTILINE,
    )

    # Update Status line
    if completed == total:
        status = "All plans executed, pending verification"
    else:
        status = f"In progress — plan {completed} of {total} complete"
    text = re.sub(r"^Status:.*$", f"Status: {status}", text, flags=re.MULTILINE)

    state_file.write_text(text, encoding="utf-8")
    print(f"STATE.md updated: {completed} of {total} plans complete")


# ===================================================================
# Subcommand: set-last-command
# ===================================================================


def cmd_set_last_command(args: argparse.Namespace) -> None:
    """Update .planning/STATE.md Last Command field with timestamp.

    Contract:
        Args: command_string (str) — e.g. "ms:plan-phase 10"
        Output: text — confirmation or warning
        Exit codes: 0 always (bookkeeping, not critical path)
        Side effects: writes STATE.md (if it exists)
    """
    command_string = args.command_string
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_line = f"Last Command: {command_string} | {now}"

    state_file = find_git_root() / ".planning" / "STATE.md"
    if not state_file.is_file():
        print("Warning: STATE.md not found, skipping Last Command update", file=sys.stderr)
        return

    text = state_file.read_text(encoding="utf-8")

    # Try replacing existing Last Command line
    updated, count = re.subn(
        r"^Last Command:.*$", new_line, text, count=1, flags=re.MULTILINE,
    )

    if count == 0:
        # Insert after Status: line
        updated, count = re.subn(
            r"^(Status:.*)$", rf"\1\n{new_line}", text, count=1, flags=re.MULTILINE,
        )
        if count == 0:
            print("Warning: No 'Last Command:' or 'Status:' line found in STATE.md", file=sys.stderr)
            return

    state_file.write_text(updated, encoding="utf-8")
    print(f"STATE.md Last Command: {command_string} | {now}")


# ===================================================================
# Subcommand: validate-execution-order
# ===================================================================


def cmd_validate_execution_order(args: argparse.Namespace) -> None:
    """Validate EXECUTION-ORDER.md against plan files in a phase directory.

    Contract:
        Args: phase_dir (str) — path to phase directory
        Output: text — PASS/FAIL message with plan count and wave count
        Exit codes: 0 = all plans matched, 1 = mismatch or missing files
        Side effects: read-only
    """
    phase_dir = Path(args.phase_dir)
    if not phase_dir.is_dir():
        print(f"FAIL: Directory does not exist: {phase_dir}")
        sys.exit(1)

    exec_order = phase_dir / "EXECUTION-ORDER.md"
    if not exec_order.is_file():
        print(f"FAIL: EXECUTION-ORDER.md not found in {phase_dir}")
        sys.exit(1)

    # Collect plan files on disk
    disk_plans = sorted(p.name for p in phase_dir.glob("*-PLAN.md"))
    if not disk_plans:
        print(f"FAIL: No *-PLAN.md files found in {phase_dir}")
        sys.exit(1)

    # Parse EXECUTION-ORDER.md for plan filenames
    exec_text = exec_order.read_text(encoding="utf-8")
    plan_pattern = re.compile(r"[0-9][0-9.]*-[0-9]+-PLAN\.md")
    order_plans = sorted(set(plan_pattern.findall(exec_text)))

    errors: list[str] = []

    # Check 1: Every disk plan is listed
    for plan in disk_plans:
        if plan not in order_plans:
            errors.append(f"  Missing from EXECUTION-ORDER.md: {plan}")

    # Check 2: Every listed plan exists on disk
    for plan in order_plans:
        if plan not in disk_plans:
            errors.append(f"  Listed in EXECUTION-ORDER.md but file missing: {plan}")

    if errors:
        print("FAIL: Plan/execution-order mismatch")
        for err in errors:
            print(err)
        sys.exit(1)

    # Check 3 (warning): File conflicts within waves
    current_wave = ""
    wave_count = 0
    current_wave_files: set[str] = set()

    for line in exec_text.splitlines():
        wave_match = re.match(r"^## Wave (\d+)", line)
        if wave_match:
            current_wave = wave_match.group(1)
            wave_count += 1
            current_wave_files = set()
        elif current_wave:
            plan_match = plan_pattern.search(line)
            if plan_match:
                plan_file = plan_match.group()
                plan_path = phase_dir / plan_file
                if plan_path.is_file():
                    plan_text = plan_path.read_text(encoding="utf-8")
                    for files_match in re.finditer(r"\*\*Files:\*\*(.+)", plan_text):
                        file_paths = files_match.group(1)
                        for fpath in file_paths.replace("`", "").split(","):
                            fpath = fpath.strip()
                            if fpath:
                                if fpath in current_wave_files:
                                    print(f"WARNING: File '{fpath}' appears in multiple plans within Wave {current_wave}")
                                else:
                                    current_wave_files.add(fpath)

    if wave_count == 0:
        print("FAIL: No '## Wave N' headers found in EXECUTION-ORDER.md")
        sys.exit(1)

    print(f"PASS: {len(disk_plans)} plans across {wave_count} waves")


# ===================================================================
# Subcommand: doctor-scan
# ===================================================================


def cmd_doctor_scan(args: argparse.Namespace) -> None:
    """Single-pass diagnostic scan of the .planning/ tree.

    Contract:
        Args: (none)
        Output: text — per-check PASS/FAIL/SKIP status and summary
        Exit codes: 0 = scan completed, 2 = missing .planning/ or config.json
        Side effects: read-only
    """
    git_root = find_git_root()
    planning = git_root / ".planning"

    if not planning.is_dir():
        print("Error: No .planning/ directory found")
        sys.exit(2)

    config_path = planning / "config.json"
    if not config_path.is_file():
        print(f"Error: No config.json found at {config_path}")
        sys.exit(2)

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(f"Error: Cannot parse {config_path}")
        sys.exit(2)

    milestones_file = planning / "MILESTONES.md"
    phases_dir = planning / "phases"
    milestones_dir = planning / "milestones"
    knowledge_dir = planning / "knowledge"

    pass_count = 0
    warn_count = 0
    fail_count = 0
    skip_count = 0
    failed_checks: list[str] = []

    def record(status: str, name: str) -> None:
        nonlocal pass_count, warn_count, fail_count, skip_count
        if status == "PASS":
            pass_count += 1
        elif status == "WARN":
            warn_count += 1
        elif status == "FAIL":
            fail_count += 1
            failed_checks.append(name)
        else:
            skip_count += 1

    def format_phase_prefix(phase: str) -> str:
        if "." in phase:
            int_part, dec_part = phase.split(".", 1)
            return f"{int(int_part):02d}.{dec_part}"
        return f"{int(phase):02d}"

    def parse_phase_numbers(line: str) -> list[str]:
        """Parse phase numbers from a 'Phases completed' line."""
        range_match = re.search(r"(\d+)-(\d+)", line)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            return [str(i) for i in range(start, end + 1)]
        return re.findall(r"\d+(?:\.\d+)?", line.split(":")[-1] if ":" in line else line)

    subsystems = config.get("subsystems", [])
    subsystem_count = len(subsystems)

    # ---- CHECK 1: Subsystem Vocabulary ----
    print("=== Subsystem Vocabulary ===")
    if subsystem_count == 0:
        print("Status: FAIL")
        print("No subsystems array in config.json (or empty)")
        record("FAIL", "Subsystem Vocabulary")
    else:
        print(f"Subsystems: {subsystem_count} configured")
        for s in subsystems:
            print(f"  - {s}")

        # Run artifact scan inline
        artifact_values = _scan_artifact_subsystem_values(planning)
        mismatches = [v for v in artifact_values if v not in subsystems]

        if mismatches:
            print("Status: FAIL")
            print(f"Artifact values not in canonical list: {' '.join(mismatches)}")
            record("FAIL", "Subsystem Vocabulary")
        else:
            print(f"Artifacts scanned: {len(artifact_values)} (all OK)")
            print("Status: PASS")
            record("PASS", "Subsystem Vocabulary")
    print()

    # ---- CHECK 2: Milestone Directory Structure ----
    print("=== Milestone Directory Structure ===")
    if not milestones_dir.is_dir():
        if milestones_file.is_file() and any(
            line.startswith("## ")
            for line in milestones_file.read_text(encoding="utf-8").splitlines()
        ):
            print("Status: FAIL")
            print("MILESTONES.md has entries but no milestones/ directory")
            record("FAIL", "Milestone Directory Structure")
        else:
            print("Status: SKIP")
            print("No completed milestones")
            record("SKIP", "Milestone Directory Structure")
    else:
        flat_files = sorted(milestones_dir.glob("v*-*.md"))
        if flat_files:
            print("Status: FAIL")
            print(f"Found {len(flat_files)} flat file(s) in milestones/ (old format):")
            for f in flat_files:
                version = re.match(r"(v[\d.]+)", f.name)
                ver = version.group(1) if version else "?"
                ver_dir = milestones_dir / ver
                if ver_dir.is_dir():
                    print(f"  {f.name} → directory {ver}/ exists (can restructure)")
                else:
                    print(f"  {f.name} → directory {ver}/ missing (need to create)")
            record("FAIL", "Milestone Directory Structure")
        else:
            ms_dirs = [d for d in milestones_dir.iterdir() if d.is_dir()]
            if not ms_dirs:
                print("Status: SKIP")
                print("No completed milestones")
                record("SKIP", "Milestone Directory Structure")
            else:
                print("Status: PASS")
                print(f"{len(ms_dirs)} milestone directories")
                record("PASS", "Milestone Directory Structure")
    print()

    # ---- CHECK 3: Phase Archival ----
    print("=== Phase Archival ===")
    if not milestones_file.is_file():
        print("Status: SKIP")
        print("No completed milestones with phase ranges in MILESTONES.md")
        record("SKIP", "Phase Archival")
    else:
        ms_text = milestones_file.read_text(encoding="utf-8")
        phase_lines = [l for l in ms_text.splitlines() if "Phases completed" in l]
        if not phase_lines:
            print("Status: SKIP")
            print("No completed milestones with phase ranges in MILESTONES.md")
            record("SKIP", "Phase Archival")
        else:
            orphans: list[str] = []
            for line in phase_lines:
                for phase_num in parse_phase_numbers(line):
                    prefix = format_phase_prefix(phase_num)
                    if phases_dir.is_dir():
                        for d in phases_dir.glob(f"{prefix}-*/"):
                            if d.is_dir():
                                orphans.append(f"  {d.name} (should be archived)")
            if orphans:
                print("Status: FAIL")
                print(f"Found {len(orphans)} orphaned phase directories from completed milestones:")
                for o in orphans:
                    print(o)
                record("FAIL", "Phase Archival")
            else:
                print("Status: PASS")
                print("All completed milestone phases are archived")
                record("PASS", "Phase Archival")
    print()

    # ---- CHECK 4: Knowledge Files ----
    print("=== Knowledge Files ===")
    if subsystem_count == 0:
        print("Status: SKIP")
        print("No subsystems configured — knowledge check requires subsystem vocabulary")
        record("SKIP", "Knowledge Files")
    elif not knowledge_dir.is_dir():
        print("Status: FAIL")
        print("Knowledge directory missing: .planning/knowledge/")
        print(f"Expected files for {subsystem_count} subsystems")
        record("FAIL", "Knowledge Files")
    else:
        missing = [s for s in subsystems if not (knowledge_dir / f"{s}.md").is_file()]
        orphaned = [
            f.stem
            for f in knowledge_dir.glob("*.md")
            if f.stem not in subsystems
        ]
        if missing or orphaned:
            present = subsystem_count - len(missing)
            print("Status: FAIL")
            print(f"Coverage: {present}/{subsystem_count} subsystems have knowledge files")
            if missing:
                print("Missing:")
                for m in missing:
                    print(f"  {m}.md")
            if orphaned:
                print("Orphaned:")
                for o in orphaned:
                    print(f"  {o}.md (not in subsystems list)")
            record("FAIL", "Knowledge Files")
        else:
            print("Status: PASS")
            print(f"All {subsystem_count} subsystems have knowledge files")
            record("PASS", "Knowledge Files")
    print()

    # ---- CHECK 5: Phase Summaries ----
    print("=== Phase Summaries ===")
    if not milestones_dir.is_dir():
        print("Status: SKIP")
        print("No milestones directory")
        record("SKIP", "Phase Summaries")
    else:
        ms_dirs = sorted(d for d in milestones_dir.iterdir() if d.is_dir())
        if not ms_dirs:
            print("Status: SKIP")
            print("No milestone directories")
            record("SKIP", "Phase Summaries")
        else:
            missing_summaries = [
                d.name for d in ms_dirs if not (d / "PHASE-SUMMARIES.md").is_file()
            ]
            if missing_summaries:
                print("Status: FAIL")
                print(f"Missing PHASE-SUMMARIES.md in {len(missing_summaries)} milestone(s):")
                for m in missing_summaries:
                    print(f"  {m}/PHASE-SUMMARIES.md")
                record("FAIL", "Phase Summaries")
            else:
                print("Status: PASS")
                print(f"All {len(ms_dirs)} milestones have PHASE-SUMMARIES.md")
                record("PASS", "Phase Summaries")
    print()

    # ---- CHECK 6: PLAN Cleanup ----
    print("=== PLAN Cleanup ===")
    if not milestones_file.is_file():
        print("Status: SKIP")
        print("No completed milestones — active phase PLANs are expected")
        record("SKIP", "PLAN Cleanup")
    else:
        ms_text = milestones_file.read_text(encoding="utf-8")
        phase_lines = [l for l in ms_text.splitlines() if "Phases completed" in l]
        if not phase_lines:
            print("Status: SKIP")
            print("No completed milestones — active phase PLANs are expected")
            record("SKIP", "PLAN Cleanup")
        else:
            leftovers: list[str] = []
            for line in phase_lines:
                for phase_num in parse_phase_numbers(line):
                    prefix = format_phase_prefix(phase_num)
                    if phases_dir.is_dir():
                        for d in phases_dir.glob(f"{prefix}-*/"):
                            if d.is_dir():
                                for plan in d.glob("*-PLAN.md"):
                                    rel = plan.relative_to(planning)
                                    leftovers.append(f"  {rel}")

            # Check archived milestone directories too
            if milestones_dir.is_dir():
                for ver_dir in milestones_dir.iterdir():
                    if not ver_dir.is_dir():
                        continue
                    archived_phases = ver_dir / "phases"
                    if archived_phases.is_dir():
                        for phase_d in archived_phases.iterdir():
                            if phase_d.is_dir():
                                for plan in phase_d.glob("*-PLAN.md"):
                                    rel = plan.relative_to(planning)
                                    leftovers.append(f"  {rel}")

            if leftovers:
                print("Status: FAIL")
                print(f"Found {len(leftovers)} leftover PLAN file(s) in completed phases:")
                for l in leftovers:
                    print(l)
                record("FAIL", "PLAN Cleanup")
            else:
                print("Status: PASS")
                print("No leftover PLAN files in completed phases")
                record("PASS", "PLAN Cleanup")
    print()

    # ---- CHECK 7: CLI Wrappers ----
    print("=== CLI Wrappers ===")
    wrapper_names = ["ms-tools", "ms-lookup", "ms-compare-mockups"]
    missing_wrappers = [w for w in wrapper_names if shutil.which(w) is None]
    if missing_wrappers:
        print("Status: FAIL")
        print(f"Not on PATH: {', '.join(missing_wrappers)}")
        print("Fix: re-run `npx mindsystem-cc` to regenerate wrappers and PATH hook")
        record("FAIL", "CLI Wrappers")
    else:
        print("Status: PASS")
        print(f"All {len(wrapper_names)} CLI wrappers found on PATH")
        record("PASS", "CLI Wrappers")
    print()

    # ---- CHECK 8: Milestone Naming Convention ----
    print("=== Milestone Naming Convention ===")
    if not milestones_dir.is_dir():
        print("Status: SKIP")
        print("No milestones directory")
        record("SKIP", "Milestone Naming Convention")
    else:
        ms_dirs = [d for d in milestones_dir.iterdir() if d.is_dir()]
        if not ms_dirs:
            print("Status: SKIP")
            print("No milestone directories")
            record("SKIP", "Milestone Naming Convention")
        else:
            versioned = _detect_versioned_milestone_dirs(planning)
            if versioned:
                print("Status: FAIL")
                print(f"Found {len(versioned)} version-prefixed milestone directories:")
                for v in versioned:
                    dirname = v["path"].split("/", 1)[1] if "/" in v["path"] else v["path"]
                    print(f"  {dirname} ({v['type']})")
                record("FAIL", "Milestone Naming Convention")
            else:
                print("Status: PASS")
                print("All milestone directories use name-based slugs")
                record("PASS", "Milestone Naming Convention")
    print()

    # ---- CHECK 9: Research API Keys ----
    print("=== Research API Keys ===")
    c7_key = os.environ.get("CONTEXT7_API_KEY", "")
    pplx_key = os.environ.get("PERPLEXITY_API_KEY", "")
    if c7_key and pplx_key:
        print("Status: PASS")
        print("All research API keys configured")
        record("PASS", "Research API Keys")
    else:
        print("Status: WARN")
        missing_keys: list[str] = []
        if not c7_key:
            missing_keys.append("CONTEXT7_API_KEY")
            print("CONTEXT7_API_KEY: not set")
            print("  Enables: library documentation lookup via Context7")
            print("  Without: falls back to WebSearch/WebFetch (less authoritative)")
            print("  Set up:  https://context7.com → copy API key → export CONTEXT7_API_KEY=<key>")
        if not pplx_key:
            missing_keys.append("PERPLEXITY_API_KEY")
            print("PERPLEXITY_API_KEY: not set")
            print("  Enables: deep research via Perplexity AI")
            print("  Without: falls back to WebSearch/WebFetch (less comprehensive)")
            print("  Set up:  https://perplexity.ai/settings/api → copy API key → export PERPLEXITY_API_KEY=<key>")
        record("WARN", "Research API Keys")
    print()

    # ---- SUMMARY ----
    total = pass_count + warn_count + fail_count + skip_count
    print("=== Summary ===")
    print(f"Checks: {total} total, {pass_count} passed, {warn_count} warned, {fail_count} failed, {skip_count} skipped")

    if fail_count > 0:
        print(f"Issues: {', '.join(failed_checks)}")
    elif warn_count > 0:
        print("No failures — warnings are informational")
    else:
        print("All checks passed")


# ===================================================================
# Subcommand: gather-milestone-stats
# ===================================================================


def cmd_gather_milestone_stats(args: argparse.Namespace) -> None:
    """Gather milestone readiness status and statistics.

    Contract:
        Args: start_phase (int), end_phase (int)
        Output: text — readiness status (READY/NOT READY) and git stats
        Exit codes: 0 = success, 1 = start > end or phases dir missing
        Side effects: read-only
    """
    start = args.start_phase
    end = args.end_phase

    if start > end:
        print(f"Error: Start phase ({start}) cannot exceed end phase ({end})", file=sys.stderr)
        sys.exit(1)

    git_root = find_git_root()
    phases_dir = git_root / ".planning" / "phases"
    if not phases_dir.is_dir():
        print(f"Error: Phases directory not found at {phases_dir}", file=sys.stderr)
        sys.exit(1)

    # ---- READINESS ----
    print("=== Readiness ===")
    print()

    phase_count = 0
    plan_count = 0
    complete = 0
    incomplete_list: list[str] = []
    phase_details: list[str] = []

    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        dirname = d.name
        phase_num = dirname.split("-", 1)[0]
        phase_name = dirname.split("-", 1)[1] if "-" in dirname else dirname

        if in_range(phase_num, start, end):
            phase_count += 1
            phase_plans = 0
            phase_complete = 0

            # Discover plans from both PLAN.md and SUMMARY.md files
            # (PLAN.md may be cleaned up after execution)
            plan_bases: set[str] = set()
            for plan in d.glob("*-PLAN.md"):
                plan_bases.add(plan.name.replace("-PLAN.md", ""))
            for summary in d.glob("*-SUMMARY.md"):
                plan_bases.add(summary.name.replace("-SUMMARY.md", ""))

            for plan_base in sorted(plan_bases):
                plan_count += 1
                phase_plans += 1
                summary = d / f"{plan_base}-SUMMARY.md"
                if summary.is_file():
                    complete += 1
                    phase_complete += 1
                else:
                    incomplete_list.append(f"  {dirname}/{plan_base}-PLAN.md")

            phase_details.append(f"- Phase {phase_num}: {phase_name} ({phase_complete}/{phase_plans} plans)")

    print(f"Phases: {phase_count} (range {start}-{end})")
    print(f"Plans: {plan_count} total, {complete} complete")
    print()
    for detail in phase_details:
        print(detail)
    print()

    if complete == plan_count and plan_count > 0:
        print("Status: READY")
    else:
        incomplete = plan_count - complete
        print(f"Incomplete ({incomplete}):")
        for item in incomplete_list:
            print(item)
        print("Status: NOT READY")

    # ---- GIT STATS ----
    print()
    print("=== Git Stats ===")
    print()

    all_commits: list[str] = []

    # Integer phases
    for i in range(start, end + 1):
        phase = f"{i:02d}"
        try:
            out = run_git("log", "--all", "--format=%H %ai %s", f"--grep=({phase}-")
            if out:
                all_commits.extend(out.splitlines())
        except subprocess.CalledProcessError:
            pass

    # Decimal phases
    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        phase_num = d.name.split("-", 1)[0]
        if "." in phase_num and in_range(phase_num, start, end):
            try:
                out = run_git("log", "--all", "--format=%H %ai %s", f"--grep=({phase_num}-")
                if out:
                    all_commits.extend(out.splitlines())
            except subprocess.CalledProcessError:
                pass

    # Deduplicate and sort by date
    seen: set[str] = set()
    unique_commits: list[str] = []
    for c in all_commits:
        hash_val = c.split()[0] if c.strip() else ""
        if hash_val and hash_val not in seen:
            seen.add(hash_val)
            unique_commits.append(c)
    unique_commits.sort(key=lambda x: x.split()[1] if len(x.split()) > 1 else "")

    if unique_commits:
        commit_count = len(unique_commits)
        first = unique_commits[0].split(maxsplit=3)
        last = unique_commits[-1].split(maxsplit=3)
        first_hash, first_date = first[0], first[1]
        last_hash, last_date = last[0], last[1]
        first_msg = first[3] if len(first) > 3 else ""
        last_msg = last[3] if len(last) > 3 else ""

        try:
            d1 = datetime.date.fromisoformat(first_date)
            d2 = datetime.date.fromisoformat(last_date)
            days = (d2 - d1).days
        except ValueError:
            days = "?"

        print(f"Commits: {commit_count}")
        print(f"Git range: {first_hash[:7]}..{last_hash[:7]}")
        print(f"First: {first_date} — {first_msg}")
        print(f"Last:  {last_date} — {last_msg}")
        print(f"Timeline: {days} days ({first_date} → {last_date})")

        try:
            diffstat = run_git("diff", "--shortstat", f"{first_hash}^..{last_hash}")
            if diffstat:
                print(f"Changes:{diffstat}")
        except subprocess.CalledProcessError:
            pass
    else:
        print("No commits found matching phase patterns (expected 'feat(XX-YY): ...')")
        print("Determine git range manually from git log")

    print()


# ===================================================================
# Subcommand: generate-phase-patch
# ===================================================================


def cmd_generate_phase_patch(args: argparse.Namespace) -> None:
    """Generate a patch file with implementation changes from a phase.

    Contract:
        Args: phase (str), --suffix (str, optional)
        Output: text — patch generation status and file path
        Exit codes: 0 = success (or no matching commits), 1 = git error
        Side effects: writes .patch file to phase directory
    """
    phase_input = args.phase
    suffix = args.suffix

    git_root = find_git_root()
    import os
    os.chdir(git_root)

    # Normalize phase number
    if re.match(r"^\d$", phase_input):
        phase_number = f"{int(phase_input):02d}"
    else:
        phase_number = phase_input

    # Determine commit pattern
    if suffix:
        if suffix == "uat-fixes":
            commit_pattern = f"\\({phase_number}-uat\\):"
            print(f"Generating UAT fixes patch for phase {phase_number}...")
        else:
            commit_pattern = f"\\({phase_number}-{suffix}\\):"
            print(f"Generating {suffix} patch for phase {phase_number}...")
    else:
        commit_pattern = f"\\({phase_number}-"
        print(f"Generating patch for phase {phase_number}...")

    # Find matching commits
    try:
        log_output = run_git("log", "--oneline")
    except subprocess.CalledProcessError:
        print("Error: Failed to read git log", file=sys.stderr)
        sys.exit(1)

    phase_commits = []
    for line in log_output.splitlines():
        if re.search(commit_pattern, line):
            phase_commits.append(line.split()[0])

    if not phase_commits:
        print(f"No commits found matching pattern: {commit_pattern}")
        print("Patch skipped")
        return

    print(f"Found {len(phase_commits)} commit(s)")

    # Determine base commit
    earliest_commit = phase_commits[-1]
    try:
        base_commit = run_git("rev-parse", f"{earliest_commit}^")
    except subprocess.CalledProcessError:
        base_commit = run_git("rev-list", "--max-parents=0", "HEAD")

    base_msg = run_git("log", "--oneline", "-1", base_commit)
    print(f"Base commit: {base_msg}")

    # Find output directory
    phases_dir = Path(".planning/phases")
    phase_dir_matches = sorted(phases_dir.glob(f"{phase_number}-*")) if phases_dir.is_dir() else []
    phase_dir = str(phase_dir_matches[0]) if phase_dir_matches else str(phases_dir)

    Path(phase_dir).mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {phase_dir}/")

    # Determine output filename
    if suffix:
        patch_file = f"{phase_dir}/{phase_number}-{suffix}.patch"
    else:
        patch_file = f"{phase_dir}/{phase_number}-changes.patch"

    # Generate diff
    exclude_args = build_exclude_pathspecs()
    if suffix:
        latest_commit = phase_commits[0]
        diff_args = ["diff", base_commit, latest_commit, "--", "."] + exclude_args
    else:
        diff_args = ["diff", base_commit, "HEAD", "--", "."] + exclude_args

    result = subprocess.run(
        ["git"] + diff_args,
        capture_output=True,
        text=True,
    )
    patch_content = result.stdout

    if not patch_content.strip():
        print("No implementation changes outside excluded patterns")
        print("Patch skipped")
        return

    Path(patch_file).write_text(patch_content, encoding="utf-8")
    line_count = len(patch_content.splitlines())

    print()
    print(f"Generated: {patch_file} ({line_count} lines)")
    print()
    print(f"Review:  cat {patch_file}")
    print(f"Apply:   git apply {patch_file}")
    print(f"Discard: rm {patch_file}")


# ===================================================================
# Subcommand: generate-adhoc-patch
# ===================================================================


def cmd_generate_adhoc_patch(args: argparse.Namespace) -> None:
    """Generate a patch file from an adhoc commit or commit range.

    Contract:
        Args: commit (str) — start commit hash, output (str) — output file path,
              end (str, optional) — end commit hash for range diffs
        Output: text — patch generation status and file path
        Exit codes: 0 = success (or no changes), 1 = commit not found
        Side effects: writes .patch file to output path
    """
    commit_hash = args.commit
    end_commit = getattr(args, "end", None) or commit_hash
    output_path = args.output

    git_root = find_git_root()
    import os
    os.chdir(git_root)

    # Verify commits exist
    for ref in {commit_hash, end_commit}:
        try:
            run_git("rev-parse", ref)
        except subprocess.CalledProcessError:
            print(f"Error: Commit {ref} not found", file=sys.stderr)
            sys.exit(1)

    exclude_args = build_exclude_pathspecs()
    diff_args = ["diff", f"{commit_hash}^", end_commit, "--", "."] + exclude_args

    result = subprocess.run(
        ["git"] + diff_args,
        capture_output=True,
        text=True,
    )

    if not result.stdout.strip():
        print("No implementation changes outside excluded patterns")
        print("Patch skipped")
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(result.stdout, encoding="utf-8")
    line_count = len(result.stdout.splitlines())
    print(f"Generated: {output_path} ({line_count} lines)")


# ===================================================================
# Subcommand: archive-milestone-phases
# ===================================================================


def cmd_archive_milestone_phases(args: argparse.Namespace) -> None:
    """Consolidate summaries, delete artifacts, move phase dirs to milestone archive.

    Contract:
        Args: start_phase (int), end_phase (int), milestone (str — slug)
        Output: text — per-stage counts and archive summary
        Exit codes: 0 = success, 1 = start > end or dirs missing
        Side effects: writes PHASE-SUMMARIES.md, deletes artifact files, moves phase dirs
    """
    start = args.start_phase
    end = args.end_phase
    milestone = args.milestone

    if start > end:
        print(f"Error: Start phase ({start}) cannot exceed end phase ({end})", file=sys.stderr)
        sys.exit(1)

    git_root = find_git_root()
    phases_dir = git_root / ".planning" / "phases"
    if not phases_dir.is_dir():
        print(f"Error: Phases directory not found at {phases_dir}", file=sys.stderr)
        sys.exit(1)

    milestone_dir = git_root / ".planning" / "milestones" / milestone
    if not milestone_dir.is_dir():
        print(f"Error: Milestone directory not found at {milestone_dir}", file=sys.stderr)
        print("Run archive_milestone step first to create it")
        sys.exit(1)

    # Stage 1: Consolidate summaries
    summaries_file = milestone_dir / "PHASE-SUMMARIES.md"
    summary_count = 0
    lines = [f"# Phase Summaries: {milestone}", ""]

    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        dirname = d.name
        phase_num = dirname.split("-", 1)[0]
        phase_name = dirname.split("-", 1)[1] if "-" in dirname else dirname

        if in_range(phase_num, start, end):
            summary_files = sorted(d.glob("*-SUMMARY.md"))
            if summary_files:
                lines.append(f"## Phase {phase_num}: {phase_name}")
                lines.append("")
                for f in summary_files:
                    plan_id = f.stem.replace("-SUMMARY", "")
                    lines.append(f"### {plan_id}")
                    lines.append("")
                    lines.append(f.read_text(encoding="utf-8"))
                    lines.append("")
                    summary_count += 1

    summaries_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Stage 1: Consolidated {summary_count} summaries to PHASE-SUMMARIES.md")

    # Stage 2: Delete artifacts
    deleted = 0
    artifact_patterns = [
        "*-CONTEXT.md", "*-DESIGN.md", "*-RESEARCH.md",
        "*-SUMMARY.md", "*-UAT.md", "*-VERIFICATION.md",
        "*-EXECUTION-ORDER.md",
    ]
    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        phase_num = d.name.split("-", 1)[0]
        if in_range(phase_num, start, end):
            for pattern in artifact_patterns:
                for f in d.glob(pattern):
                    f.unlink()
                    deleted += 1

    print(f"Stage 2: Deleted {deleted} artifact files")

    # Stage 3: Move phase directories
    archive_phases = milestone_dir / "phases"
    archive_phases.mkdir(exist_ok=True)
    moved = 0

    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        phase_num = d.name.split("-", 1)[0]
        if in_range(phase_num, start, end):
            shutil.move(str(d), str(archive_phases / d.name))
            moved += 1

    print(f"Stage 3: Moved {moved} phase directories to milestones/{milestone}/phases/")
    print()
    print(f"Archive complete: {summary_count} summaries, {deleted} artifacts deleted, {moved} dirs moved")


# ===================================================================
# Subcommand: archive-milestone-files
# ===================================================================


def cmd_archive_milestone_files(args: argparse.Namespace) -> None:
    """Move optional milestone files to the milestone archive directory.

    Contract:
        Args: milestone (str) — milestone slug (e.g., mvp, push-notifications)
        Output: text — per-file archive status
        Exit codes: 0 = success, 1 = milestone directory missing
        Side effects: moves audit, context, and research files to milestone dir
    """
    milestone = args.milestone

    git_root = find_git_root()
    planning_dir = git_root / ".planning"
    milestone_dir = planning_dir / "milestones" / milestone

    if not milestone_dir.is_dir():
        print(f"Error: Milestone directory not found at {milestone_dir}", file=sys.stderr)
        print("Run archive_milestone step first to create it")
        sys.exit(1)

    archived = 0

    # Milestone audit
    audit = planning_dir / "MILESTONE-AUDIT.md"
    if audit.is_file():
        shutil.move(str(audit), str(milestone_dir / "MILESTONE-AUDIT.md"))
        print("Archived: MILESTONE-AUDIT.md → MILESTONE-AUDIT.md")
        archived += 1

    # Milestone context
    context = planning_dir / "MILESTONE-CONTEXT.md"
    if context.is_file():
        shutil.move(str(context), str(milestone_dir / "CONTEXT.md"))
        print("Archived: MILESTONE-CONTEXT.md → CONTEXT.md")
        archived += 1

    # Research directory
    research = planning_dir / "research"
    if research.is_dir():
        shutil.move(str(research), str(milestone_dir / "research"))
        print("Archived: research/ → research/")
        archived += 1

    if archived == 0:
        print("No optional files to archive (audit, context, research all absent)")
    else:
        print()
        print(f"Archived {archived} item(s) to milestones/{milestone}/")


# ===================================================================
# Subcommand: scan-artifact-subsystems
# ===================================================================


def _scan_artifact_subsystem_values(planning: Path) -> list[str]:
    """Extract all subsystem values from planning artifacts (helper for doctor-scan)."""
    values: list[str] = []
    scan_globs = [
        ("phases", "*/*-SUMMARY.md"),
        ("adhoc", "*-SUMMARY.md"),
        ("debug", "*.md"),
        ("debug/resolved", "*.md"),
        ("todos", "*.md"),
        ("todos/done", "*.md"),
    ]
    for subdir, pattern in scan_globs:
        target = planning / subdir
        if target.is_dir():
            for f in sorted(target.glob(pattern)):
                fm = parse_frontmatter(f)
                if fm and fm.get("subsystem"):
                    values.append(fm["subsystem"])
    return values


def _detect_versioned_milestone_dirs(planning: Path) -> list[dict]:
    """Detect v-prefixed milestone directories that need migration.

    Returns list of dicts with keys: path, version, sub, type.
    - "standard": v-dir has .md files directly
    - "nested": v-dir has sub-directories (excluding phases/) and no direct .md files
    """
    milestones_dir = planning / "milestones"
    if not milestones_dir.is_dir():
        return []

    v_pattern = re.compile(r"^v\d+")
    results: list[dict] = []

    for entry in sorted(milestones_dir.iterdir()):
        if not entry.is_dir() or not v_pattern.match(entry.name):
            continue

        version = entry.name
        has_md_files = any(f.suffix == ".md" for f in entry.iterdir() if f.is_file())
        sub_dirs = [
            d for d in entry.iterdir()
            if d.is_dir() and d.name != "phases"
        ]

        if sub_dirs and not has_md_files:
            # Nested: each sub-dir is a separate entry
            for sub in sorted(sub_dirs):
                results.append({
                    "path": f"milestones/{version}/{sub.name}",
                    "version": version,
                    "sub": sub.name,
                    "type": "nested",
                })
        else:
            # Standard: v-dir itself is the milestone
            results.append({
                "path": f"milestones/{version}",
                "version": version,
                "sub": None,
                "type": "standard",
            })

    return results


def _parse_milestone_name_mapping(planning: Path) -> list[dict]:
    """Parse MILESTONES.md and PROJECT.md to build version→name→slug mapping.

    Returns list of dicts with keys: version, name, slug, and optionally current.
    """
    results: list[dict] = []

    # Parse MILESTONES.md shipped/started headers
    milestones_file = planning / "MILESTONES.md"
    if milestones_file.is_file():
        ms_text = milestones_file.read_text(encoding="utf-8")
        header_re = re.compile(
            r"^## (v[\d.]+)\s+(.+?)\s*\((?:Shipped|Started):?\s*[^)]+\)",
            re.MULTILINE,
        )
        for match in header_re.finditer(ms_text):
            version = match.group(1)
            name = match.group(2).strip()
            results.append({
                "version": version,
                "name": name,
                "slug": slugify(name),
            })

    # Parse PROJECT.md for current milestone
    project_file = planning / "PROJECT.md"
    if project_file.is_file():
        proj_text = project_file.read_text(encoding="utf-8")
        current_re = re.compile(
            r"^## Current Milestone:\s*(v[\d.]+)\s+(.+?)$",
            re.MULTILINE,
        )
        m = current_re.search(proj_text)
        if m:
            version = m.group(1)
            name = m.group(2).strip()
            results.append({
                "version": version,
                "name": name,
                "slug": slugify(name),
                "current": True,
            })

    return results


def cmd_scan_artifact_subsystems(args: argparse.Namespace) -> None:
    """Scan planning artifacts for subsystem YAML frontmatter values.

    Contract:
        Args: --values-only (flag, optional)
        Output: text — subsystem values grouped by artifact type
        Exit codes: 0 = success, 1 = .planning/ missing
        Side effects: read-only
    """
    planning = find_planning_dir()
    values_only = args.values_only

    sections = [
        ("Phase SUMMARYs", "phases", "*/*-SUMMARY.md"),
        ("Adhoc SUMMARYs", "adhoc", "*-SUMMARY.md"),
        ("Debug docs", "debug", "*.md"),
        ("Debug resolved", "debug/resolved", "*.md"),
        ("Pending Todos", "todos", "*.md"),
        ("Done Todos", "todos/done", "*.md"),
    ]

    for header, subdir, pattern in sections:
        print(f"=== {header} ===")
        target = planning / subdir
        if not target.is_dir():
            continue
        for f in sorted(target.glob(pattern)):
            fm = parse_frontmatter(f)
            if fm and fm.get("subsystem"):
                if values_only:
                    print(fm["subsystem"])
                else:
                    print(f"{f}\t{fm['subsystem']}")


# ===================================================================
# Subcommand: scan-milestone-naming
# ===================================================================


def cmd_scan_milestone_naming(args: argparse.Namespace) -> None:
    """Scan milestone directories for version-based naming needing migration.

    Contract:
        Args: (none)
        Output: JSON — versioned_dirs, name_mappings, current_milestone, needs_migration
        Exit codes: 0 = success, 2 = missing .planning/
        Side effects: read-only
    """
    planning = find_planning_dir()

    versioned_dirs = _detect_versioned_milestone_dirs(planning)
    name_mappings = _parse_milestone_name_mapping(planning)

    current_milestone = None
    non_current: list[dict] = []
    for m in name_mappings:
        if m.get("current"):
            current_milestone = {
                "version": m["version"],
                "name": m["name"],
                "slug": m["slug"],
            }
        else:
            non_current.append(m)

    result = {
        "versioned_dirs": versioned_dirs,
        "name_mappings": non_current,
        "current_milestone": current_milestone,
        "needs_migration": len(versioned_dirs) > 0,
    }

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


# ===================================================================
# Subcommand: find-phase
# ===================================================================


def cmd_find_phase(args: argparse.Namespace) -> None:
    """Find phase directory and validate against roadmap.

    Contract:
        Args: phase (str) — phase number (e.g., 5, 05, 2.1)
        Output: JSON — {phase, dir, name, exists_in_roadmap}
        Exit codes: 0 = success, 1 = not in git repo
        Side effects: read-only
    """
    phase_input = args.phase
    phase = normalize_phase(phase_input)

    git_root = find_git_root()
    planning = git_root / ".planning"

    result: dict[str, Any] = {
        "phase": phase,
        "dir": None,
        "name": None,
        "exists_in_roadmap": False,
    }

    if planning.is_dir():
        phase_dir = find_phase_dir(planning, phase)
        if phase_dir:
            result["dir"] = str(phase_dir.relative_to(git_root))
            name = phase_dir.name.split("-", 1)
            result["name"] = name[1] if len(name) > 1 else phase_dir.name

        # Check roadmap
        roadmap = planning / "ROADMAP.md"
        if roadmap.is_file():
            roadmap_text = roadmap.read_text(encoding="utf-8")
            # Match "Phase XX:" or "Phase XX " patterns
            if re.search(rf"Phase\s+{re.escape(phase)}[\s:]", roadmap_text):
                result["exists_in_roadmap"] = True

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


# ===================================================================
# Subcommand: list-artifacts
# ===================================================================


def cmd_list_artifacts(args: argparse.Namespace) -> None:
    """Count PLANs, SUMMARYs, and other artifacts per phase.

    Contract:
        Args: phase (str) — phase number
        Output: JSON — {phase, plans, summaries, has_context, has_design, ...}
        Exit codes: 0 = success, 1 = .planning/ missing
        Side effects: read-only
    """
    phase = normalize_phase(args.phase)
    planning = find_planning_dir()
    phase_dir = find_phase_dir(planning, phase)

    result: dict[str, Any] = {
        "phase": phase,
        "plans": 0,
        "summaries": 0,
        "has_context": False,
        "has_design": False,
        "has_research": False,
        "has_uat": False,
        "has_verification": False,
        "has_execution_order": False,
    }

    if phase_dir and phase_dir.is_dir():
        result["plans"] = len(list(phase_dir.glob("*-PLAN.md")))
        result["summaries"] = len(list(phase_dir.glob("*-SUMMARY.md")))
        result["has_context"] = any(phase_dir.glob("*-CONTEXT.md"))
        result["has_design"] = any(phase_dir.glob("*-DESIGN.md"))
        result["has_research"] = any(phase_dir.glob("*-RESEARCH.md"))
        result["has_uat"] = any(phase_dir.glob("*-UAT.md"))
        result["has_verification"] = any(phase_dir.glob("*-VERIFICATION.md"))
        result["has_execution_order"] = (phase_dir / "EXECUTION-ORDER.md").is_file()

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


# ===================================================================
# Subcommand: check-artifact
# ===================================================================


def cmd_check_artifact(args: argparse.Namespace) -> None:
    """Check if a specific artifact exists for a phase.

    Contract:
        Args: phase (str), type (str) — artifact type (CONTEXT, DESIGN, etc.)
        Output: JSON — {exists, path}
        Exit codes: 0 = success, 1 = .planning/ missing
        Side effects: read-only
    """
    phase = normalize_phase(args.phase)
    artifact_type = args.type.upper()
    planning = find_planning_dir()
    phase_dir = find_phase_dir(planning, phase)

    result: dict[str, Any] = {
        "exists": False,
        "path": None,
    }

    if phase_dir and phase_dir.is_dir():
        # Map artifact types to glob patterns
        patterns = {
            "CONTEXT": f"*-CONTEXT.md",
            "DESIGN": f"*-DESIGN.md",
            "RESEARCH": f"*-RESEARCH.md",
            "UAT": f"*-UAT.md",
            "VERIFICATION": f"*-VERIFICATION.md",
            "PLAN": f"*-PLAN.md",
            "SUMMARY": f"*-SUMMARY.md",
            "EXECUTION-ORDER": "EXECUTION-ORDER.md",
        }

        pattern = patterns.get(artifact_type)
        if pattern:
            matches = list(phase_dir.glob(pattern))
            if matches:
                result["exists"] = True
                result["path"] = str(matches[0].relative_to(find_git_root()))

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


# ===================================================================
# Subcommand: scan-planning-context
# ===================================================================


def _has_readiness_section(path: Path) -> bool:
    """Check if file has a non-empty '## Next Phase Readiness' section."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    idx = text.find("## Next Phase Readiness")
    if idx == -1:
        return False

    after = text[idx + len("## Next Phase Readiness"):]
    next_heading = re.search(r"\n## ", after)
    section = after[:next_heading.start()] if next_heading else after
    stripped = section.strip().strip("-").strip()
    return len(stripped) > 0


def _extract_phase_number(phase_str: str) -> int | None:
    """Extract integer phase number from phase string like '05-auth' or '05'."""
    match = re.match(r"^(\d+)", str(phase_str))
    return int(match.group(1)) if match else None


def _is_adjacent_phase(target_num: int, candidate_num: int) -> bool:
    """Check if candidate is within 2 phases before target (N-1, N-2)."""
    diff = target_num - candidate_num
    return 1 <= diff <= 2


def _score_summary(
    fm: dict[str, Any],
    target_phase: str,
    target_num: int | None,
    subsystems: list[str],
    keywords: list[str],
) -> tuple[str, list[str]]:
    """Score a SUMMARY's relevance to the target phase."""
    reasons: list[str] = []
    is_high = False
    is_medium = False

    # HIGH signals
    affects = fm.get("affects", []) or []
    if isinstance(affects, str):
        affects = [affects]
    for a in affects:
        if target_phase in str(a):
            reasons.append(f"affects contains '{target_phase}'")
            is_high = True

    fm_subsystem = fm.get("subsystem", "")
    if fm_subsystem and fm_subsystem in subsystems:
        reasons.append(f"same subsystem '{fm_subsystem}'")
        is_high = True

    requires = fm.get("requires", []) or []
    if isinstance(requires, list):
        for req in requires:
            if isinstance(req, dict):
                req_phase = str(req.get("phase", ""))
            else:
                req_phase = str(req)
            if target_phase in req_phase:
                reasons.append(f"requires references '{target_phase}'")
                is_high = True

    # MEDIUM signals
    fm_tags = fm.get("tags", []) or []
    if isinstance(fm_tags, str):
        fm_tags = [fm_tags]
    fm_tags_lower = {str(t).lower() for t in fm_tags}
    keywords_lower = {k.lower() for k in keywords}
    overlap = fm_tags_lower & keywords_lower
    if overlap:
        reasons.append(f"overlapping tags: {sorted(overlap)}")
        is_medium = True

    fm_phase = fm.get("phase", "")
    candidate_num = _extract_phase_number(str(fm_phase))
    if target_num is not None and candidate_num is not None:
        if _is_adjacent_phase(target_num, candidate_num):
            reasons.append(f"adjacent phase (N-{target_num - candidate_num})")
            is_medium = True

    if is_high:
        return ("HIGH", reasons)
    if is_medium:
        return ("MEDIUM", reasons)
    return ("LOW", reasons)


def _resolve_transitive_requires(
    summaries: list[dict[str, Any]],
    target_phase: str,
) -> set[str]:
    """Find all phases transitively required by the target phase."""
    required: set[str] = set()
    for s in summaries:
        fm = s.get("frontmatter", {})
        phase_name = str(fm.get("phase", ""))
        affects = fm.get("affects", []) or []
        if isinstance(affects, str):
            affects = [affects]
        if any(target_phase in str(a) for a in affects):
            required.add(phase_name)
            requires = fm.get("requires", []) or []
            if isinstance(requires, list):
                for req in requires:
                    if isinstance(req, dict):
                        req_phase = str(req.get("phase", ""))
                    else:
                        req_phase = str(req)
                    if req_phase:
                        required.add(req_phase)
    return required


def _scan_summaries(
    planning: Path,
    target_phase: str,
    target_num: int | None,
    subsystems: list[str],
    keywords: list[str],
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan phase summary files and score relevance."""
    phases_dir = planning / "phases"
    source_info: dict[str, Any] = {"dir": str(phases_dir), "scanned": 0, "skipped": None}

    if not phases_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    summary_files = sorted(phases_dir.glob("*/*-SUMMARY.md"))
    if not summary_files:
        source_info["skipped"] = "no SUMMARY.md files found"
        return [], source_info

    results: list[dict[str, Any]] = []
    for path in summary_files:
        source_info["scanned"] += 1
        fm = parse_frontmatter(path)
        if fm is None:
            parse_errors.append({"path": str(path), "error": "no valid frontmatter"})
            continue

        relevance, match_reasons = _score_summary(fm, target_phase, target_num, subsystems, keywords)
        readiness = _has_readiness_section(path)

        results.append({
            "path": str(path),
            "frontmatter": fm,
            "relevance": relevance,
            "match_reasons": match_reasons,
            "has_readiness_warnings": readiness,
        })

    transitive = _resolve_transitive_requires(results, target_phase)
    for entry in results:
        fm = entry["frontmatter"]
        phase_name = str(fm.get("phase", ""))
        if phase_name in transitive and entry["relevance"] != "HIGH":
            entry["relevance"] = "HIGH"
            entry["match_reasons"].append("in transitive requires chain")

    return results, source_info


def _scan_debug_docs(
    planning: Path,
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan resolved debug documents for learnings."""
    resolved_dir = planning / "debug" / "resolved"
    source_info: dict[str, Any] = {"dir": str(resolved_dir), "scanned": 0, "skipped": None}

    if not resolved_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    results: list[dict[str, Any]] = []
    for path in sorted(resolved_dir.glob("*.md")):
        source_info["scanned"] += 1
        fm = parse_frontmatter(path)
        if fm is None:
            parse_errors.append({"path": str(path), "error": "no valid frontmatter"})
            continue

        results.append({
            "path": str(path),
            "slug": path.stem,
            "subsystem": fm.get("subsystem", ""),
            "root_cause": fm.get("root_cause", ""),
            "resolution": fm.get("resolution", ""),
            "tags": fm.get("tags", []) or [],
            "phase": fm.get("phase", ""),
        })

    return results, source_info


def _scan_adhoc_summaries(
    planning: Path,
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan adhoc summary files for learnings."""
    adhoc_dir = planning / "adhoc"
    source_info: dict[str, Any] = {"dir": str(adhoc_dir), "scanned": 0, "skipped": None}

    if not adhoc_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    summary_files = sorted(adhoc_dir.glob("**/*-SUMMARY.md"))
    if not summary_files:
        source_info["skipped"] = "no adhoc SUMMARY.md files found"
        return [], source_info

    results: list[dict[str, Any]] = []
    for path in summary_files:
        source_info["scanned"] += 1
        fm = parse_frontmatter(path)
        if fm is None:
            parse_errors.append({"path": str(path), "error": "no valid frontmatter"})
            continue

        learnings = fm.get("learnings", []) or []
        if isinstance(learnings, str):
            learnings = [learnings]
        # Fallback: extract from key-decisions if learnings absent (phase-style SUMMARY)
        if not learnings:
            key_decisions = fm.get("key-decisions", []) or []
            if isinstance(key_decisions, str):
                key_decisions = [key_decisions]
            learnings = key_decisions

        results.append({
            "path": str(path),
            "subsystem": fm.get("subsystem", ""),
            "learnings": learnings,
            "related_phase": fm.get("related_phase", ""),
            "tags": fm.get("tags", []) or [],
        })

    return results, source_info


def _scan_todos(
    planning: Path,
    subdir: str,
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan todo files (done/ or root todos/) for metadata."""
    todo_dir = planning / "todos" / subdir if subdir else planning / "todos"
    source_info: dict[str, Any] = {"dir": str(todo_dir), "scanned": 0, "skipped": None}

    if not todo_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    md_files = sorted(todo_dir.glob("*.md"))
    if not md_files:
        label = f"{subdir}/" if subdir else "todos/"
        source_info["skipped"] = f"no .md files in {label}"
        return [], source_info

    results: list[dict[str, Any]] = []
    for path in md_files:
        source_info["scanned"] += 1
        fm = parse_frontmatter(path)
        if fm is None:
            parse_errors.append({"path": str(path), "error": "no valid frontmatter"})
            continue

        results.append({
            "path": str(path),
            "title": fm.get("title", path.stem),
            "subsystem": fm.get("subsystem", ""),
            "priority": fm.get("priority", ""),
            "estimate": fm.get("estimate", ""),
        })

    return results, source_info


def _scan_knowledge_files(
    planning: Path,
    subsystems: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """List knowledge files and match by subsystem."""
    knowledge_dir = planning / "knowledge"
    source_info: dict[str, Any] = {"dir": str(knowledge_dir), "scanned": 0, "skipped": None}

    if not knowledge_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    md_files = sorted(knowledge_dir.glob("*.md"))
    if not md_files:
        source_info["skipped"] = "no .md files in knowledge/"
        return [], source_info

    subsystems_lower = {s.lower() for s in subsystems}
    results: list[dict[str, Any]] = []
    for path in md_files:
        source_info["scanned"] += 1
        file_subsystem = path.stem.lower()
        matched = file_subsystem in subsystems_lower

        results.append({
            "path": str(path),
            "subsystem": path.stem,
            "matched": matched,
        })

    return results, source_info


def _aggregate_from_summaries(summaries: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Aggregate tech stack, patterns, key files, decisions from HIGH+MEDIUM summaries."""
    tech_added: list[str] = []
    patterns: list[str] = []
    key_files_created: list[str] = []
    key_files_modified: list[str] = []
    key_decisions: list[str] = []

    for entry in summaries:
        if entry["relevance"] == "LOW":
            continue
        fm = entry["frontmatter"]

        ts = fm.get("tech-stack", {}) or {}
        if isinstance(ts, dict):
            added = ts.get("added", []) or []
            if isinstance(added, str):
                added = [added]
            tech_added.extend(str(a) for a in added)
            pat = ts.get("patterns", []) or []
            if isinstance(pat, str):
                pat = [pat]
            patterns.extend(str(p) for p in pat)

        pe = fm.get("patterns-established", []) or []
        if isinstance(pe, str):
            pe = [pe]
        patterns.extend(str(p) for p in pe)

        kf = fm.get("key-files", {}) or {}
        if isinstance(kf, dict):
            created = kf.get("created", []) or []
            if isinstance(created, str):
                created = [created]
            key_files_created.extend(str(f) for f in created)
            modified = kf.get("modified", []) or []
            if isinstance(modified, str):
                modified = [modified]
            key_files_modified.extend(str(f) for f in modified)

        kd = fm.get("key-decisions", []) or []
        if isinstance(kd, str):
            kd = [kd]
        key_decisions.extend(str(d) for d in kd)

    return {
        "tech_stack_added": sorted(set(tech_added)),
        "patterns_established": sorted(set(patterns)),
        "key_files_created": sorted(set(key_files_created)),
        "key_files_modified": sorted(set(key_files_modified)),
        "key_decisions": list(dict.fromkeys(key_decisions)),
    }


def _format_markdown(output: dict[str, Any]) -> str:
    """Format scanner output as readable markdown for LLM consumption."""
    sections: list[str] = []
    agg = output.get("aggregated", {})

    patterns = agg.get("patterns_established", [])
    if patterns:
        lines = ["### Established Patterns"]
        lines.extend(f"- {p}" for p in patterns)
        sections.append("\n".join(lines))

    tech = agg.get("tech_stack_added", [])
    if tech:
        sections.append(f"### Tech Stack\n{', '.join(tech)}")

    decisions = agg.get("key_decisions", [])
    if decisions:
        lines = ["### Key Decisions"]
        lines.extend(f"- {d}" for d in decisions)
        sections.append("\n".join(lines))

    created = agg.get("key_files_created", [])
    modified = agg.get("key_files_modified", [])
    if created or modified:
        lines = ["### Key Files"]
        if created:
            lines.append("**Created:**")
            lines.extend(f"- `{f}`" for f in created)
        if modified:
            lines.append("**Modified:**")
            lines.extend(f"- `{f}`" for f in modified)
        sections.append("\n".join(lines))

    debug = output.get("debug_learnings", [])
    if debug:
        lines = ["### Debug Learnings"]
        for d in debug:
            slug = d.get("slug", "unknown")
            sub = d.get("subsystem", "")
            rc = d.get("root_cause", "")
            res = d.get("resolution", "")
            lines.append(f"- **{slug}** ({sub}): {rc} — Fix: {res}")
        sections.append("\n".join(lines))

    adhoc_entries = [a for a in output.get("adhoc_learnings", []) if a.get("learnings")]
    if adhoc_entries:
        lines = ["### Adhoc Learnings"]
        for a in adhoc_entries:
            sub = a.get("subsystem", "")
            path = a.get("path", "")
            label = sub or Path(path).stem if path else "unknown"
            lines.append(f"- **{label}**")
            for learning in a["learnings"]:
                lines.append(f"  - {learning}")
        sections.append("\n".join(lines))

    summaries = output.get("summaries", [])
    needs_read = [s for s in summaries if s.get("relevance") == "HIGH" and s.get("has_readiness_warnings")]
    other_relevant = [s for s in summaries if s.get("relevance") in ("HIGH", "MEDIUM") and not s.get("has_readiness_warnings")]

    if needs_read:
        lines = ["### Summaries Needing Full Read"]
        lines.extend(f"- `{s['path']}`" for s in needs_read)
        sections.append("\n".join(lines))

    if other_relevant:
        lines = ["### Other Relevant Summaries"]
        lines.extend(f"- `{s['path']}` [{s.get('relevance', '')}]" for s in other_relevant)
        sections.append("\n".join(lines))

    matched_knowledge = [k for k in output.get("knowledge_files", []) if k.get("matched")]
    if matched_knowledge:
        lines = ["### Knowledge Files to Read"]
        lines.extend(f"- `{k['path']}`" for k in matched_knowledge)
        sections.append("\n".join(lines))

    todos = output.get("pending_todos", [])
    if todos:
        lines = ["### Pending Todos"]
        for t in todos:
            title = t.get("title", "untitled")
            priority = t.get("priority", "")
            estimate = t.get("estimate", "")
            sub = t.get("subsystem", "")
            path = t.get("path", "")
            lines.append(f"- **{title}** [P{priority}|{estimate}] ({sub}) — `{path}`")
        sections.append("\n".join(lines))

    sources = output.get("sources", {})
    parse_errors = sources.get("parse_errors", [])
    info_lines = ["### Scanner Info"]
    for name, src in sources.items():
        if name == "parse_errors" or not isinstance(src, dict):
            continue
        scanned = src.get("scanned", 0)
        skipped = src.get("skipped")
        if skipped:
            info_lines.append(f"- {name}: skipped ({skipped})")
        else:
            info_lines.append(f"- {name}: {scanned} scanned")
    if parse_errors:
        info_lines.append("**Parse errors:**")
        for err in parse_errors:
            info_lines.append(f"- `{err.get('path', '')}`: {err.get('error', '')}")
    sections.append("\n".join(info_lines))

    return "\n\n".join(sections)


def cmd_scan_planning_context(args: argparse.Namespace) -> None:
    """Scan .planning/ artifacts and score relevance for plan-phase context assembly.

    Contract:
        Args: --phase (str, required), --phase-name (str), --subsystem (repeatable), --keywords (csv), --json (flag)
        Output: JSON (--json) or markdown — scored summaries, learnings, todos, knowledge, aggregated context
        Exit codes: 0 = success (empty result if no .planning/)
        Side effects: read-only
    """
    phase = normalize_phase(args.phase)
    phase_name = args.phase_name.strip() if args.phase_name else ""
    subsystems = [s for s in (args.subsystems or []) if s]
    keywords = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]

    if phase_name:
        name_words = [w for w in re.split(r"[-_\s]+", phase_name) if len(w) > 2]
        keywords.extend(name_words)

    target_num = _extract_phase_number(phase)

    planning = find_planning_dir_optional()
    if planning is None:
        if args.json:
            empty_src = {"dir": "", "scanned": 0, "skipped": ".planning/ not found"}
            output: dict[str, Any] = {
                "success": True,
                "target": {"phase": phase, "phase_name": phase_name, "subsystems": subsystems, "keywords": keywords},
                "sources": {
                    "summaries": empty_src, "debug_docs": empty_src, "adhoc_summaries": empty_src,
                    "completed_todos": empty_src, "pending_todos": empty_src, "knowledge_files": empty_src,
                    "parse_errors": [],
                },
                "summaries": [], "debug_learnings": [], "adhoc_learnings": [],
                "completed_todos": [], "pending_todos": [], "knowledge_files": [],
                "aggregated": {
                    "tech_stack_added": [], "patterns_established": [],
                    "key_files_created": [], "key_files_modified": [], "key_decisions": [],
                },
            }
            json.dump(output, sys.stdout, indent=2, cls=_SafeEncoder)
            sys.stdout.write("\n")
        else:
            print("No .planning/ directory found. No prior context available.")
        return

    parse_errors: list[dict[str, str]] = []

    summaries, summaries_src = _scan_summaries(planning, phase, target_num, subsystems, keywords, parse_errors)
    debug_learnings, debug_src = _scan_debug_docs(planning, parse_errors)
    adhoc_learnings, adhoc_src = _scan_adhoc_summaries(planning, parse_errors)
    completed_todos, completed_src = _scan_todos(planning, "done", parse_errors)
    pending_todos, pending_src = _scan_todos(planning, "", parse_errors)
    knowledge_files, knowledge_src = _scan_knowledge_files(planning, subsystems)

    aggregated = _aggregate_from_summaries(summaries)

    output = {
        "success": True,
        "target": {"phase": phase, "phase_name": phase_name, "subsystems": subsystems, "keywords": keywords},
        "sources": {
            "summaries": summaries_src, "debug_docs": debug_src, "adhoc_summaries": adhoc_src,
            "completed_todos": completed_src, "pending_todos": pending_src,
            "knowledge_files": knowledge_src, "parse_errors": parse_errors,
        },
        "summaries": summaries,
        "debug_learnings": debug_learnings,
        "adhoc_learnings": adhoc_learnings,
        "completed_todos": completed_todos,
        "pending_todos": pending_todos,
        "knowledge_files": knowledge_files,
        "aggregated": aggregated,
    }

    if args.json:
        json.dump(output, sys.stdout, indent=2, cls=_SafeEncoder)
        sys.stdout.write("\n")
    else:
        print(_format_markdown(output))


# ===================================================================
# UAT File Management
# ===================================================================

_TEST_HEADER_RE = re.compile(r"^###\s+(\d+)\.\s+(.+)$")
_BATCH_HEADER_RE = re.compile(r"^###\s+Batch\s+(\d+):\s+(.+)$")
_SECTION_HEADER_RE = re.compile(r"^##\s+(.+)$")
_KV_LINE_RE = re.compile(r"^(\w[\w_]*)\s*:\s*(.*)$")
_LIST_ITEM_START_RE = re.compile(r"^-\s+(\w[\w_]*)\s*:\s*(.*)$")
_LIST_ITEM_CONT_RE = re.compile(r"^\s+(\w[\w_]*)\s*:\s*(.*)$")

# Fields that get quoted in serialization per section
_QUOTED_FIELDS = {
    "current_batch": {"name"},
    "fixes": {"description"},
    "assumptions": {"name", "expected", "reason"},
    "tests": {"reported"},
}


def _ensure_quoted(value: str) -> str:
    """Add surrounding quotes if not already quoted."""
    if value.startswith('"') and value.endswith('"'):
        return value
    return f'"{value}"'


class UATFile:
    """Internal representation of UAT.md for programmatic manipulation."""

    def __init__(self) -> None:
        self.frontmatter: dict[str, Any] = {}
        self.progress: dict[str, str] = {}
        self.current_batch: dict[str, str] = {}
        self.tests: list[dict[str, str]] = []
        self.fixes: list[dict[str, str]] = []
        self.batches: list[dict[str, str]] = []
        self.assumptions: list[dict[str, str]] = []

    # --- Parsing ---

    @classmethod
    def parse(cls, text: str) -> "UATFile":
        """Parse UAT.md text into structured representation."""
        uat = cls()

        # Parse frontmatter
        fm_match = _FRONTMATTER_RE.match(text)
        if fm_match:
            try:
                uat.frontmatter = yaml.safe_load(fm_match.group(1)) or {}
            except yaml.YAMLError:
                uat.frontmatter = {}
            body = text[fm_match.end():]
        else:
            body = text

        # Split into sections by ## headers
        sections = cls._split_sections(body)

        for name, content in sections.items():
            if name == "Progress":
                uat.progress = cls._parse_kv_block(content)
            elif name == "Current Batch":
                uat.current_batch = cls._parse_kv_block(content)
            elif name == "Tests":
                uat.tests = cls._parse_tests(content)
            elif name == "Fixes Applied":
                uat.fixes = cls._parse_list_items(content)
            elif name == "Batches":
                uat.batches = cls._parse_batches(content)
            elif name == "Assumptions":
                uat.assumptions = cls._parse_list_items(content)

        return uat

    @staticmethod
    def _split_sections(body: str) -> dict[str, str]:
        """Split body text into {section_name: content} dict."""
        sections: dict[str, str] = {}
        current_name: str | None = None
        current_lines: list[str] = []

        for line in body.splitlines():
            m = _SECTION_HEADER_RE.match(line)
            if m:
                if current_name is not None:
                    sections[current_name] = "\n".join(current_lines)
                current_name = m.group(1).strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_name is not None:
            sections[current_name] = "\n".join(current_lines)

        return sections

    @staticmethod
    def _parse_kv_block(text: str) -> dict[str, str]:
        """Parse a block of key: value lines."""
        result: dict[str, str] = {}
        for line in text.splitlines():
            m = _KV_LINE_RE.match(line.strip())
            if m:
                result[m.group(1)] = m.group(2).strip()
        return result

    @staticmethod
    def _parse_tests(text: str) -> list[dict[str, str]]:
        """Parse ### N. Name sections into test dicts."""
        tests: list[dict[str, str]] = []
        current: dict[str, str] | None = None

        for line in text.splitlines():
            m = _TEST_HEADER_RE.match(line)
            if m:
                if current is not None:
                    tests.append(current)
                current = {"num": m.group(1), "name": m.group(2).strip()}
            elif current is not None:
                kv = _KV_LINE_RE.match(line.strip())
                if kv:
                    current[kv.group(1)] = kv.group(2).strip()

        if current is not None:
            tests.append(current)

        return tests

    @staticmethod
    def _parse_batches(text: str) -> list[dict[str, str]]:
        """Parse ### Batch N: Name sections into batch dicts."""
        batches: list[dict[str, str]] = []
        current: dict[str, str] | None = None

        for line in text.splitlines():
            m = _BATCH_HEADER_RE.match(line)
            if m:
                if current is not None:
                    batches.append(current)
                current = {"num": m.group(1), "name": m.group(2).strip()}
            elif current is not None:
                kv = _KV_LINE_RE.match(line.strip())
                if kv:
                    current[kv.group(1)] = kv.group(2).strip()

        if current is not None:
            batches.append(current)

        return batches

    @staticmethod
    def _parse_list_items(text: str) -> list[dict[str, str]]:
        """Parse - key: value list items (fixes, assumptions)."""
        items: list[dict[str, str]] = []
        current: dict[str, str] | None = None

        for line in text.splitlines():
            m = _LIST_ITEM_START_RE.match(line)
            if m:
                if current is not None:
                    items.append(current)
                current = {m.group(1): m.group(2).strip()}
            elif current is not None:
                m2 = _LIST_ITEM_CONT_RE.match(line)
                if m2:
                    current[m2.group(1)] = m2.group(2).strip()

        if current is not None:
            items.append(current)

        return items

    # --- Construction ---

    @classmethod
    def from_init_json(cls, data: dict, phase_name: str) -> "UATFile":
        """Construct from structured JSON input."""
        uat = cls()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        tests = data.get("tests", [])
        batches = data.get("batches", [])
        source = data.get("source", [])

        uat.frontmatter = {
            "status": "testing",
            "phase": phase_name,
            "source": source,
            "started": now,
            "updated": now,
            "current_batch": 1,
            "mocked_files": [],
            "pre_work_stash": None,
        }

        # Build tests
        for i, t in enumerate(tests, 1):
            uat.tests.append({
                "num": str(i),
                "name": t["name"],
                "expected": t["expected"],
                "mock_required": str(t.get("mock_required", False)).lower(),
                "mock_type": t.get("mock_type") or "null",
                "result": "[pending]",
            })

        # Build batches
        for i, b in enumerate(batches, 1):
            test_nums = "[" + ", ".join(str(n) for n in b["tests"]) + "]"
            uat.batches.append({
                "num": str(i),
                "name": b["name"],
                "tests": test_nums,
                "status": "pending",
                "mock_type": b.get("mock_type") or "null",
            })

        # Set first batch as current
        if batches:
            first = batches[0]
            test_nums = "[" + ", ".join(str(n) for n in first["tests"]) + "]"
            uat.current_batch = {
                "batch": f"1 of {len(batches)}",
                "name": _ensure_quoted(first["name"]),
                "mock_type": first.get("mock_type") or "null",
                "tests": test_nums,
                "status": "pending",
            }

        uat.recalc_progress()
        return uat

    # --- Mutations ---

    def update_test(self, num: int, fields: dict[str, str]) -> None:
        """Update fields on test N."""
        for t in self.tests:
            if t["num"] == str(num):
                t.update(fields)
                return
        raise ValueError(f"Test {num} not found")

    def update_batch(self, num: int, fields: dict[str, str]) -> None:
        """Update fields on batch N."""
        for b in self.batches:
            if b["num"] == str(num):
                b.update(fields)
                return
        raise ValueError(f"Batch {num} not found")

    def update_session(self, fields: dict[str, str]) -> None:
        """Update frontmatter fields."""
        for k, v in fields.items():
            if v == "":
                # Empty string means clear/null
                if k == "mocked_files":
                    self.frontmatter[k] = []
                else:
                    self.frontmatter[k] = None
            elif k == "mocked_files":
                self.frontmatter[k] = [f.strip() for f in v.split(",") if f.strip()]
            elif k == "current_batch":
                try:
                    batch_num = int(v)
                    self.frontmatter[k] = batch_num
                    self._sync_current_batch(batch_num)
                except ValueError:
                    self.frontmatter[k] = v
            else:
                self.frontmatter[k] = v

    def _sync_current_batch(self, batch_num: int) -> None:
        """Sync Current Batch section when frontmatter current_batch changes."""
        total = len(self.batches)
        for b in self.batches:
            if b["num"] == str(batch_num):
                name = b["name"]
                if not name.startswith('"'):
                    name = _ensure_quoted(name)
                self.current_batch = {
                    "batch": f"{batch_num} of {total}",
                    "name": name,
                    "mock_type": b.get("mock_type", "null"),
                    "tests": b.get("tests", "[]"),
                    "status": b.get("status", "pending"),
                }
                return

    def append_fix(self, fix_dict: dict) -> None:
        """Append to fixes. Update in-place if same test already has a fix."""
        test_num = str(fix_dict.get("test", ""))
        converted: dict[str, str] = {}
        for k, v in fix_dict.items():
            if isinstance(v, list):
                converted[k] = "[" + ", ".join(str(x) for x in v) + "]"
            elif k == "description":
                converted[k] = _ensure_quoted(str(v))
            else:
                converted[k] = str(v)

        for i, f in enumerate(self.fixes):
            if f.get("test") == test_num:
                self.fixes[i] = converted
                return
        self.fixes.append(converted)

    def append_assumption(self, assumption_dict: dict) -> None:
        """Append to assumptions."""
        converted: dict[str, str] = {}
        for k, v in assumption_dict.items():
            s = str(v)
            if k in ("name", "expected", "reason"):
                s = _ensure_quoted(s)
            converted[k] = s
        self.assumptions.append(converted)

    # --- Progress ---

    def recalc_progress(self) -> None:
        """Derive all progress counters from test results."""
        total = len(self.tests)
        pending = 0
        passed = 0
        issues = 0
        fixing = 0
        skipped = 0

        for t in self.tests:
            result = t.get("result", "[pending]")
            fix_status = t.get("fix_status", "")

            if result in ("[pending]", "blocked"):
                pending += 1
            elif result == "pass":
                passed += 1
            elif result == "issue":
                if fix_status == "verified":
                    passed += 1
                elif fix_status in ("investigating", "applied"):
                    fixing += 1
                else:
                    issues += 1
            elif result == "skipped":
                skipped += 1

        tested = total - pending
        self.progress = {
            "total": str(total),
            "tested": str(tested),
            "passed": str(passed),
            "issues": str(issues),
            "fixing": str(fixing),
            "pending": str(pending),
            "skipped": str(skipped),
        }

    def progress_summary(self) -> str:
        """One-line summary for stdout."""
        p = self.progress
        return (
            f"{p.get('tested', '0')}/{p.get('total', '0')} "
            f"({p.get('passed', '0')} pass, {p.get('issues', '0')} issue, "
            f"{p.get('fixing', '0')} fixing, {p.get('skipped', '0')} skip)"
        )

    # --- Serialization ---

    def serialize(self) -> str:
        """Rebuild full file from internal state."""
        self.recalc_progress()
        self.frontmatter["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        lines: list[str] = []

        # Frontmatter
        lines.append("---")
        fm_text = yaml.dump(
            self.frontmatter, default_flow_style=False, sort_keys=False,
        ).rstrip()
        lines.append(fm_text)
        lines.append("---")
        lines.append("")

        # Progress
        lines.append("## Progress")
        lines.append("")
        for k in ("total", "tested", "passed", "issues", "fixing", "pending", "skipped"):
            if k in self.progress:
                lines.append(f"{k}: {self.progress[k]}")
        lines.append("")

        # Current Batch
        lines.append("## Current Batch")
        lines.append("")
        for k in ("batch", "name", "mock_type", "tests", "status"):
            if k in self.current_batch:
                lines.append(f"{k}: {self.current_batch[k]}")
        lines.append("")

        # Tests
        lines.append("## Tests")
        lines.append("")
        test_field_order = (
            "expected", "mock_required", "mock_type", "result",
            "reported", "severity", "fix_status", "fix_commit",
            "retry_count", "reason",
        )
        for t in self.tests:
            lines.append(f"### {t['num']}. {t['name']}")
            for k in test_field_order:
                if k in t:
                    val = t[k]
                    if k in _QUOTED_FIELDS.get("tests", set()):
                        val = _ensure_quoted(val)
                    lines.append(f"{k}: {val}")
            lines.append("")

        # Fixes Applied
        lines.append("## Fixes Applied")
        lines.append("")
        fix_field_order = ("commit", "test", "description", "files")
        for fix in self.fixes:
            first = True
            for k in fix_field_order:
                if k in fix:
                    val = fix[k]
                    if k in _QUOTED_FIELDS.get("fixes", set()):
                        val = _ensure_quoted(val)
                    prefix = "- " if first else "  "
                    lines.append(f"{prefix}{k}: {val}")
                    first = False
            lines.append("")

        # Batches
        lines.append("## Batches")
        lines.append("")
        batch_field_order = ("tests", "status", "mock_type", "passed", "issues")
        for b in self.batches:
            lines.append(f"### Batch {b['num']}: {b['name']}")
            for k in batch_field_order:
                if k in b:
                    lines.append(f"{k}: {b[k]}")
            lines.append("")

        # Assumptions
        lines.append("## Assumptions")
        lines.append("")
        assumption_field_order = ("test", "name", "expected", "reason")
        for a in self.assumptions:
            first = True
            for k in assumption_field_order:
                if k in a:
                    val = a[k]
                    if k in _QUOTED_FIELDS.get("assumptions", set()):
                        val = _ensure_quoted(val)
                    prefix = "- " if first else "  "
                    lines.append(f"{prefix}{k}: {val}")
                    first = False
            lines.append("")

        return "\n".join(lines)


# ===================================================================
# Subcommand: uat-init
# ===================================================================


def cmd_uat_init(args: argparse.Namespace) -> None:
    """Create UAT.md from JSON stdin.

    Contract:
        Args: phase (str) — phase number
        Input: JSON on stdin with source, tests, batches
        Output: text — confirmation with path and counts
        Exit codes: 0 = success, 1 = invalid JSON
        Side effects: creates UAT.md file
    """
    phase = normalize_phase(args.phase)
    planning = find_planning_dir()

    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    phase_dir = find_phase_dir(planning, phase)
    if phase_dir is None:
        phases_dir = planning / "phases"
        phases_dir.mkdir(parents=True, exist_ok=True)
        phase_dir = phases_dir / phase
        phase_dir.mkdir(parents=True, exist_ok=True)

    phase_name = phase_dir.name
    uat = UATFile.from_init_json(data, phase_name)

    out_path = phase_dir / f"{phase_name}-UAT.md"
    out_path.write_text(uat.serialize(), encoding="utf-8")

    n_tests = len(uat.tests)
    n_batches = len(uat.batches)
    print(f"Created {out_path} with {n_tests} tests in {n_batches} batches")


# ===================================================================
# Subcommand: uat-update
# ===================================================================


def cmd_uat_update(args: argparse.Namespace) -> None:
    """Update UAT.md fields.

    Contract:
        Args: phase (str), mutually exclusive target flag, key=value pairs or JSON stdin
        Output: text — update label + progress summary
        Exit codes: 0 = success, 1 = file not found or invalid input
        Side effects: writes UAT.md
    """
    phase = normalize_phase(args.phase)
    planning = find_planning_dir()

    phase_dir = find_phase_dir(planning, phase)
    if phase_dir is None:
        print(f"Error: Phase directory not found for {phase}", file=sys.stderr)
        sys.exit(1)

    uat_path = phase_dir / f"{phase_dir.name}-UAT.md"
    if not uat_path.is_file():
        print(f"Error: UAT file not found: {uat_path}", file=sys.stderr)
        sys.exit(1)

    uat = UATFile.parse(uat_path.read_text(encoding="utf-8"))

    # Parse key=value pairs from remaining args
    fields: dict[str, str] = {}
    for kv in (args.fields or []):
        if "=" in kv:
            k, v = kv.split("=", 1)
            fields[k] = v

    label = ""

    if args.test is not None:
        uat.update_test(args.test, fields)
        label = f"Updated test {args.test}: " + ", ".join(f"{k}={v}" for k, v in fields.items())
    elif args.batch is not None:
        uat.update_batch(args.batch, fields)
        label = f"Updated batch {args.batch}: " + ", ".join(f"{k}={v}" for k, v in fields.items())
    elif args.session:
        uat.update_session(fields)
        label = f"Updated session: " + ", ".join(f"{k}={v}" for k, v in fields.items())
    elif args.append_fix:
        try:
            fix_data = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
        uat.append_fix(fix_data)
        label = f"Appended fix for test {fix_data.get('test', '?')}"
    elif args.append_assumption:
        try:
            assumption_data = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
        uat.append_assumption(assumption_data)
        label = f"Appended assumption for test {assumption_data.get('test', '?')}"

    uat_path.write_text(uat.serialize(), encoding="utf-8")
    print(f"{label} | Progress: {uat.progress_summary()}")


# ===================================================================
# Subcommand: uat-status
# ===================================================================


def cmd_uat_status(args: argparse.Namespace) -> None:
    """Output UAT status as JSON.

    Contract:
        Args: phase (str) — phase number
        Output: JSON — compact status for LLM resume
        Exit codes: 0 = success, 1 = file not found
        Side effects: read-only
    """
    phase = normalize_phase(args.phase)
    planning = find_planning_dir()

    phase_dir = find_phase_dir(planning, phase)
    if phase_dir is None:
        print(f"Error: Phase directory not found for {phase}", file=sys.stderr)
        sys.exit(1)

    uat_path = phase_dir / f"{phase_dir.name}-UAT.md"
    if not uat_path.is_file():
        print(f"Error: UAT file not found: {uat_path}", file=sys.stderr)
        sys.exit(1)

    uat = UATFile.parse(uat_path.read_text(encoding="utf-8"))
    uat.recalc_progress()

    fixing_tests = []
    pending_tests = []
    blocked_tests = []

    for t in uat.tests:
        num = int(t["num"])
        result = t.get("result", "[pending]")
        fix_status = t.get("fix_status", "")

        if fix_status in ("investigating", "applied"):
            fixing_tests.append({
                "num": num,
                "name": t["name"],
                "fix_status": fix_status,
                "fix_commit": t.get("fix_commit", ""),
                "retry_count": int(t.get("retry_count", "0")),
            })
        if result == "[pending]":
            pending_tests.append(num)
        elif result == "blocked":
            blocked_tests.append(num)

    output = {
        "status": uat.frontmatter.get("status", ""),
        "current_batch": uat.frontmatter.get("current_batch"),
        "total_batches": len(uat.batches),
        "progress": {k: int(v) for k, v in uat.progress.items()},
        "mocked_files": uat.frontmatter.get("mocked_files", []),
        "fixing_tests": fixing_tests,
        "pending_tests": pending_tests,
        "blocked_tests": blocked_tests,
        "pre_work_stash": uat.frontmatter.get("pre_work_stash"),
        "path": str(uat_path),
    }

    json.dump(output, sys.stdout, cls=_SafeEncoder)
    sys.stdout.write("\n")


# ===================================================================
# Argument parser setup
# ===================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ms-tools",
        description="Mindsystem CLI tools — unified subcommands for mechanical operations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- update-state ---
    p = subparsers.add_parser("update-state", help="Update STATE.md plan progress")
    p.add_argument("completed", type=int, help="Number of completed plans")
    p.add_argument("total", type=int, help="Total number of plans")
    p.set_defaults(func=cmd_update_state)

    # --- set-last-command ---
    p = subparsers.add_parser("set-last-command", help="Update STATE.md Last Command with timestamp")
    p.add_argument("command_string", help='Command that was run (e.g. "ms:plan-phase 10")')
    p.set_defaults(func=cmd_set_last_command)

    # --- validate-execution-order ---
    p = subparsers.add_parser("validate-execution-order", help="Validate EXECUTION-ORDER.md against plan files")
    p.add_argument("phase_dir", help="Phase directory path")
    p.set_defaults(func=cmd_validate_execution_order)

    # --- doctor-scan ---
    p = subparsers.add_parser("doctor-scan", help="Diagnostic scan of .planning/ tree")
    p.set_defaults(func=cmd_doctor_scan)

    # --- gather-milestone-stats ---
    p = subparsers.add_parser("gather-milestone-stats", help="Gather milestone readiness and git statistics")
    p.add_argument("start_phase", type=int, help="Start phase number")
    p.add_argument("end_phase", type=int, help="End phase number")
    p.set_defaults(func=cmd_gather_milestone_stats)

    # --- generate-phase-patch ---
    p = subparsers.add_parser("generate-phase-patch", help="Generate patch from phase commits")
    p.add_argument("phase", help="Phase number (e.g., 04 or 4)")
    p.add_argument("--suffix", default="", help="Filter commits and customize output filename")
    p.set_defaults(func=cmd_generate_phase_patch)

    # --- generate-adhoc-patch ---
    p = subparsers.add_parser("generate-adhoc-patch", help="Generate patch from an adhoc commit or range")
    p.add_argument("commit", help="Start commit hash")
    p.add_argument("output", help="Output path for the patch file")
    p.add_argument("--end", default=None, help="End commit hash for range diffs (default: same as commit)")
    p.set_defaults(func=cmd_generate_adhoc_patch)

    # --- archive-milestone-phases ---
    p = subparsers.add_parser("archive-milestone-phases", help="Archive phase dirs to milestone directory")
    p.add_argument("start_phase", type=int, help="Start phase number")
    p.add_argument("end_phase", type=int, help="End phase number")
    p.add_argument("milestone", help="Milestone slug (e.g., mvp, push-notifications)")
    p.set_defaults(func=cmd_archive_milestone_phases)

    # --- archive-milestone-files ---
    p = subparsers.add_parser("archive-milestone-files", help="Archive optional milestone files")
    p.add_argument("milestone", help="Milestone slug (e.g., mvp, push-notifications)")
    p.set_defaults(func=cmd_archive_milestone_files)

    # --- scan-artifact-subsystems ---
    p = subparsers.add_parser("scan-artifact-subsystems", help="Scan artifacts for subsystem values")
    p.add_argument("--values-only", action="store_true", help="Print only subsystem values")
    p.set_defaults(func=cmd_scan_artifact_subsystems)

    # --- scan-milestone-naming ---
    p = subparsers.add_parser("scan-milestone-naming", help="Scan for version-based milestone naming needing migration")
    p.set_defaults(func=cmd_scan_milestone_naming)

    # --- scan-planning-context ---
    p = subparsers.add_parser("scan-planning-context", help="Scan .planning/ and score relevance for plan-phase")
    p.add_argument("--phase", required=True, help='Phase number (e.g., "05" or "5" or "2.1")')
    p.add_argument("--phase-name", default="", help="Phase name for keyword matching")
    p.add_argument("--subsystem", action="append", default=[], dest="subsystems", help="Subsystem(s) for matching (repeatable)")
    p.add_argument("--keywords", default="", help="Comma-separated keywords for tag matching")
    p.add_argument("--json", action="store_true", help="Output raw JSON (default: formatted markdown)")
    p.set_defaults(func=cmd_scan_planning_context)

    # --- find-phase ---
    p = subparsers.add_parser("find-phase", help="Find phase directory and validate against roadmap")
    p.add_argument("phase", help="Phase number (e.g., 5, 05, 2.1)")
    p.set_defaults(func=cmd_find_phase)

    # --- list-artifacts ---
    p = subparsers.add_parser("list-artifacts", help="Count artifacts per phase")
    p.add_argument("phase", help="Phase number")
    p.set_defaults(func=cmd_list_artifacts)

    # --- check-artifact ---
    p = subparsers.add_parser("check-artifact", help="Check if specific artifact exists")
    p.add_argument("phase", help="Phase number")
    p.add_argument("type", help="Artifact type (CONTEXT, DESIGN, RESEARCH, UAT, VERIFICATION, PLAN, SUMMARY, EXECUTION-ORDER)")
    p.set_defaults(func=cmd_check_artifact)

    # --- uat-init ---
    p = subparsers.add_parser("uat-init", help="Create UAT.md from JSON stdin")
    p.add_argument("phase", help="Phase number (e.g., 5, 05, 2.1)")
    p.set_defaults(func=cmd_uat_init)

    # --- uat-update ---
    p = subparsers.add_parser("uat-update", help="Update UAT.md fields")
    p.add_argument("phase", help="Phase number")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--test", type=int, help="Test number to update")
    group.add_argument("--batch", type=int, help="Batch number to update")
    group.add_argument("--session", action="store_true", help="Update session/frontmatter fields")
    group.add_argument("--append-fix", action="store_true", help="Append fix (JSON from stdin)")
    group.add_argument("--append-assumption", action="store_true", help="Append assumption (JSON from stdin)")
    p.add_argument("fields", nargs="*", help="key=value pairs")
    p.set_defaults(func=cmd_uat_update)

    # --- uat-status ---
    p = subparsers.add_parser("uat-status", help="Output UAT status as JSON")
    p.add_argument("phase", help="Phase number")
    p.set_defaults(func=cmd_uat_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
