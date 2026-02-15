#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Scan .planning/ artifacts and score relevance for plan-phase context assembly.

Deterministic collection and scoring of planning artifacts so the LLM
receives structured JSON and focuses on interpretation and judgment.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


class _SafeEncoder(json.JSONEncoder):
    """Handle YAML types that json.dump can't serialize (date, datetime)."""

    def default(self, o: object) -> Any:
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)


# ---------------------------------------------------------------------------
# Git root / .planning discovery
# ---------------------------------------------------------------------------


def find_planning_dir() -> Path | None:
    """Find .planning/ from git root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        git_root = Path(result.stdout.strip())
        planning = git_root / ".planning"
        return planning if planning.is_dir() else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# ---------------------------------------------------------------------------
# YAML frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a markdown file.

    Returns parsed dict or None if no frontmatter found.
    """
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


def has_readiness_section(path: Path) -> bool:
    """Check if file has a non-empty '## Next Phase Readiness' section."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    idx = text.find("## Next Phase Readiness")
    if idx == -1:
        return False

    # Grab content until next ## heading or end of file
    after = text[idx + len("## Next Phase Readiness") :]
    next_heading = re.search(r"\n## ", after)
    section = after[: next_heading.start()] if next_heading else after
    # Non-empty = has more than whitespace / dashes
    stripped = section.strip().strip("-").strip()
    return len(stripped) > 0


# ---------------------------------------------------------------------------
# Phase number helpers
# ---------------------------------------------------------------------------


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


def extract_phase_number(phase_str: str) -> int | None:
    """Extract integer phase number from phase string like '05-auth' or '05'."""
    match = re.match(r"^(\d+)", str(phase_str))
    return int(match.group(1)) if match else None


def is_adjacent_phase(target_num: int, candidate_num: int) -> bool:
    """Check if candidate is within 2 phases before target (N-1, N-2)."""
    diff = target_num - candidate_num
    return 1 <= diff <= 2


# ---------------------------------------------------------------------------
# Relevance scoring
# ---------------------------------------------------------------------------


def score_summary(
    fm: dict[str, Any],
    target_phase: str,
    target_num: int | None,
    subsystems: list[str],
    keywords: list[str],
) -> tuple[str, list[str]]:
    """Score a SUMMARY's relevance to the target phase.

    Returns (relevance, match_reasons) where relevance is HIGH/MEDIUM/LOW.
    """
    reasons: list[str] = []
    is_high = False
    is_medium = False

    # --- HIGH signals ---

    # Target phase appears in affects list
    affects = fm.get("affects", []) or []
    if isinstance(affects, str):
        affects = [affects]
    for a in affects:
        if target_phase in str(a):
            reasons.append(f"affects contains '{target_phase}'")
            is_high = True

    # Same subsystem
    fm_subsystem = fm.get("subsystem", "")
    if fm_subsystem and fm_subsystem in subsystems:
        reasons.append(f"same subsystem '{fm_subsystem}'")
        is_high = True

    # In requires chain (direct — transitive computed at caller level)
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

    # --- MEDIUM signals ---

    # Overlapping tags with keywords
    fm_tags = fm.get("tags", []) or []
    if isinstance(fm_tags, str):
        fm_tags = [fm_tags]
    fm_tags_lower = {str(t).lower() for t in fm_tags}
    keywords_lower = {k.lower() for k in keywords}
    overlap = fm_tags_lower & keywords_lower
    if overlap:
        reasons.append(f"overlapping tags: {sorted(overlap)}")
        is_medium = True

    # Adjacent phase (N-1, N-2)
    fm_phase = fm.get("phase", "")
    candidate_num = extract_phase_number(str(fm_phase))
    if target_num is not None and candidate_num is not None:
        if is_adjacent_phase(target_num, candidate_num):
            reasons.append(f"adjacent phase (N-{target_num - candidate_num})")
            is_medium = True

    if is_high:
        return ("HIGH", reasons)
    if is_medium:
        return ("MEDIUM", reasons)
    return ("LOW", reasons)


# ---------------------------------------------------------------------------
# Transitive requires resolution
# ---------------------------------------------------------------------------


def resolve_transitive_requires(
    summaries: list[dict[str, Any]],
    target_phase: str,
) -> set[str]:
    """Find all phases transitively required by the target phase.

    Build a reverse lookup: which phases provide things the target needs.
    """
    # Build provides index: phase_name -> list of provides
    provides_index: dict[str, list[str]] = {}
    for s in summaries:
        fm = s.get("frontmatter", {})
        phase_name = str(fm.get("phase", ""))
        provides = fm.get("provides", []) or []
        if isinstance(provides, str):
            provides = [provides]
        provides_index[phase_name] = [str(p) for p in provides]

    # Find which summaries have target in their affects
    required: set[str] = set()
    for s in summaries:
        fm = s.get("frontmatter", {})
        phase_name = str(fm.get("phase", ""))
        affects = fm.get("affects", []) or []
        if isinstance(affects, str):
            affects = [affects]
        if any(target_phase in str(a) for a in affects):
            required.add(phase_name)
            # Also add anything this phase requires (one hop)
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


# ---------------------------------------------------------------------------
# Directory scanners
# ---------------------------------------------------------------------------


def scan_summaries(
    planning: Path,
    target_phase: str,
    target_num: int | None,
    subsystems: list[str],
    keywords: list[str],
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan phase summary files and score relevance."""
    phases_dir = planning / "phases"
    source_info: dict[str, Any] = {
        "dir": str(phases_dir),
        "scanned": 0,
        "skipped": None,
    }

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

        relevance, match_reasons = score_summary(
            fm, target_phase, target_num, subsystems, keywords
        )
        readiness = has_readiness_section(path)

        results.append(
            {
                "path": str(path),
                "frontmatter": fm,
                "relevance": relevance,
                "match_reasons": match_reasons,
                "has_readiness_warnings": readiness,
            }
        )

    # Resolve transitive requires and upgrade scores
    transitive = resolve_transitive_requires(results, target_phase)
    for entry in results:
        fm = entry["frontmatter"]
        phase_name = str(fm.get("phase", ""))
        if phase_name in transitive and entry["relevance"] != "HIGH":
            entry["relevance"] = "HIGH"
            entry["match_reasons"].append(f"in transitive requires chain")

    return results, source_info


def scan_debug_docs(
    planning: Path,
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan resolved debug documents for learnings."""
    resolved_dir = planning / "debug" / "resolved"
    source_info: dict[str, Any] = {
        "dir": str(resolved_dir),
        "scanned": 0,
        "skipped": None,
    }

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

        results.append(
            {
                "path": str(path),
                "subsystem": fm.get("subsystem", ""),
                "root_cause": fm.get("root_cause", ""),
                "resolution": fm.get("resolution", ""),
                "tags": fm.get("tags", []) or [],
                "phase": fm.get("phase", ""),
            }
        )

    return results, source_info


def scan_adhoc_summaries(
    planning: Path,
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan adhoc summary files for learnings."""
    adhoc_dir = planning / "adhoc"
    source_info: dict[str, Any] = {
        "dir": str(adhoc_dir),
        "scanned": 0,
        "skipped": None,
    }

    if not adhoc_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    summary_files = sorted(adhoc_dir.glob("*-SUMMARY.md"))
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

        results.append(
            {
                "path": str(path),
                "subsystem": fm.get("subsystem", ""),
                "learnings": learnings,
                "related_phase": fm.get("related_phase", ""),
                "tags": fm.get("tags", []) or [],
            }
        )

    return results, source_info


def scan_todos(
    planning: Path,
    subdir: str,
    parse_errors: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan todo files (done/ or pending/) for metadata."""
    todo_dir = planning / "todos" / subdir
    source_info: dict[str, Any] = {
        "dir": str(todo_dir),
        "scanned": 0,
        "skipped": None,
    }

    if not todo_dir.is_dir():
        source_info["skipped"] = "directory not found"
        return [], source_info

    md_files = sorted(todo_dir.glob("*.md"))
    if not md_files:
        source_info["skipped"] = f"no .md files in {subdir}/"
        return [], source_info

    results: list[dict[str, Any]] = []
    for path in md_files:
        source_info["scanned"] += 1
        fm = parse_frontmatter(path)
        if fm is None:
            parse_errors.append({"path": str(path), "error": "no valid frontmatter"})
            continue

        results.append(
            {
                "path": str(path),
                "title": fm.get("title", path.stem),
                "subsystem": fm.get("subsystem", ""),
                "priority": fm.get("priority", ""),
                "phase_origin": fm.get("phase_origin", ""),
            }
        )

    return results, source_info


def scan_knowledge_files(
    planning: Path,
    subsystems: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """List knowledge files and match by subsystem."""
    knowledge_dir = planning / "knowledge"
    source_info: dict[str, Any] = {
        "dir": str(knowledge_dir),
        "scanned": 0,
        "skipped": None,
    }

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
        # Knowledge files use filename as subsystem identifier
        file_subsystem = path.stem.lower()
        matched = file_subsystem in subsystems_lower

        results.append(
            {
                "path": str(path),
                "subsystem": path.stem,
                "matched": matched,
            }
        )

    return results, source_info


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate_from_summaries(
    summaries: list[dict[str, Any]],
) -> dict[str, list[str]]:
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

        # tech-stack.added
        ts = fm.get("tech-stack", {}) or {}
        if isinstance(ts, dict):
            added = ts.get("added", []) or []
            if isinstance(added, str):
                added = [added]
            tech_added.extend(str(a) for a in added)

            # tech-stack.patterns
            pat = ts.get("patterns", []) or []
            if isinstance(pat, str):
                pat = [pat]
            patterns.extend(str(p) for p in pat)

        # patterns-established
        pe = fm.get("patterns-established", []) or []
        if isinstance(pe, str):
            pe = [pe]
        patterns.extend(str(p) for p in pe)

        # key-files
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

        # key-decisions
        kd = fm.get("key-decisions", []) or []
        if isinstance(kd, str):
            kd = [kd]
        key_decisions.extend(str(d) for d in kd)

    return {
        "tech_stack_added": sorted(set(tech_added)),
        "patterns_established": sorted(set(patterns)),
        "key_files_created": sorted(set(key_files_created)),
        "key_files_modified": sorted(set(key_files_modified)),
        "key_decisions": list(dict.fromkeys(key_decisions)),  # dedupe, preserve order
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan .planning/ artifacts and score relevance for plan-phase context assembly.",
    )
    parser.add_argument(
        "--phase",
        required=True,
        help='Phase number (e.g., "05" or "5" or "2.1")',
    )
    parser.add_argument(
        "--phase-name",
        default="",
        help="Phase name for keyword matching",
    )
    parser.add_argument(
        "--subsystem",
        action="append",
        default=[],
        dest="subsystems",
        help="Subsystem(s) for matching (repeatable)",
    )
    parser.add_argument(
        "--keywords",
        default="",
        help="Comma-separated keywords for tag matching",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    phase = normalize_phase(args.phase)
    phase_name = args.phase_name.strip()
    subsystems = [s for s in args.subsystems if s]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    # Add phase name words as keywords
    if phase_name:
        name_words = [w for w in re.split(r"[-_\s]+", phase_name) if len(w) > 2]
        keywords.extend(name_words)

    target_num = extract_phase_number(phase)

    planning = find_planning_dir()
    if planning is None:
        # No .planning/ directory — output valid JSON with all sources skipped
        output: dict[str, Any] = {
            "success": True,
            "target": {
                "phase": phase,
                "phase_name": phase_name,
                "subsystems": subsystems,
                "keywords": keywords,
            },
            "sources": {
                "summaries": {"dir": "", "scanned": 0, "skipped": ".planning/ not found"},
                "debug_docs": {"dir": "", "scanned": 0, "skipped": ".planning/ not found"},
                "adhoc_summaries": {"dir": "", "scanned": 0, "skipped": ".planning/ not found"},
                "completed_todos": {"dir": "", "scanned": 0, "skipped": ".planning/ not found"},
                "pending_todos": {"dir": "", "scanned": 0, "skipped": ".planning/ not found"},
                "knowledge_files": {"dir": "", "scanned": 0, "skipped": ".planning/ not found"},
                "parse_errors": [],
            },
            "summaries": [],
            "debug_learnings": [],
            "adhoc_learnings": [],
            "completed_todos": [],
            "pending_todos": [],
            "knowledge_files": [],
            "aggregated": {
                "tech_stack_added": [],
                "patterns_established": [],
                "key_files_created": [],
                "key_files_modified": [],
                "key_decisions": [],
            },
        }
        json.dump(output, sys.stdout, indent=2, cls=_SafeEncoder)
        sys.stdout.write("\n")
        return

    parse_errors: list[dict[str, str]] = []

    # Scan all sources
    summaries, summaries_src = scan_summaries(
        planning, phase, target_num, subsystems, keywords, parse_errors
    )
    debug_learnings, debug_src = scan_debug_docs(planning, parse_errors)
    adhoc_learnings, adhoc_src = scan_adhoc_summaries(planning, parse_errors)
    completed_todos, completed_src = scan_todos(planning, "done", parse_errors)
    pending_todos, pending_src = scan_todos(planning, "pending", parse_errors)
    knowledge_files, knowledge_src = scan_knowledge_files(planning, subsystems)

    # Aggregate from HIGH+MEDIUM summaries
    aggregated = aggregate_from_summaries(summaries)

    output = {
        "success": True,
        "target": {
            "phase": phase,
            "phase_name": phase_name,
            "subsystems": subsystems,
            "keywords": keywords,
        },
        "sources": {
            "summaries": summaries_src,
            "debug_docs": debug_src,
            "adhoc_summaries": adhoc_src,
            "completed_todos": completed_src,
            "pending_todos": pending_src,
            "knowledge_files": knowledge_src,
            "parse_errors": parse_errors,
        },
        "summaries": summaries,
        "debug_learnings": debug_learnings,
        "adhoc_learnings": adhoc_learnings,
        "completed_todos": completed_todos,
        "pending_todos": pending_todos,
        "knowledge_files": knowledge_files,
        "aggregated": aggregated,
    }

    json.dump(output, sys.stdout, indent=2, cls=_SafeEncoder)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
