"""Tests for ms-tools.py pure logic layer and scan-planning-context integration."""

import argparse
import datetime
import importlib.util
import io
import json
from pathlib import Path
from unittest import mock

import pytest

# ---------------------------------------------------------------------------
# Import ms-tools.py (hyphenated filename requires importlib)
# ---------------------------------------------------------------------------

_spec = importlib.util.spec_from_file_location(
    "ms_tools", Path(__file__).parent / "ms-tools.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

slugify = _mod.slugify
normalize_phase = _mod.normalize_phase
in_range = _mod.in_range
parse_frontmatter = _mod.parse_frontmatter
build_exclude_pathspecs = _mod.build_exclude_pathspecs
PATCH_EXCLUSIONS = _mod.PATCH_EXCLUSIONS
_extract_phase_number = _mod._extract_phase_number
_is_adjacent_phase = _mod._is_adjacent_phase
_score_summary = _mod._score_summary
_resolve_transitive_requires = _mod._resolve_transitive_requires
_aggregate_from_summaries = _mod._aggregate_from_summaries
_has_readiness_section = _mod._has_readiness_section
_scan_summaries = _mod._scan_summaries
_scan_debug_docs = _mod._scan_debug_docs
_scan_adhoc_summaries = _mod._scan_adhoc_summaries
_scan_todos = _mod._scan_todos
_scan_knowledge_files = _mod._scan_knowledge_files
_detect_versioned_milestone_dirs = _mod._detect_versioned_milestone_dirs
_parse_milestone_name_mapping = _mod._parse_milestone_name_mapping
_SafeEncoder = _mod._SafeEncoder
cmd_set_last_command = _mod.cmd_set_last_command

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_PLANNING = Path(__file__).parent / "fixtures" / "scan-context" / ".planning"

# Set to True, run once, review expected-output.json, then set back to False.
REGENERATE_GOLDEN = False


# ===================================================================
# Part 1: Pure Function Unit Tests
# ===================================================================


class TestSlugify:
    def test_basic_name(self):
        assert slugify("Push Notifications") == "push-notifications"

    def test_ampersand_stripped(self):
        assert slugify("Auth & Payments") == "auth-payments"

    def test_uppercase(self):
        assert slugify("MVP") == "mvp"

    def test_underscores(self):
        assert slugify("push_notifications") == "push-notifications"

    def test_consecutive_hyphens(self):
        assert slugify("auth -- payments") == "auth-payments"

    def test_leading_trailing_hyphens(self):
        assert slugify("-hello-world-") == "hello-world"

    def test_special_characters(self):
        assert slugify("v2.0 New Features!") == "v20-new-features"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_already_slug(self):
        assert slugify("push-notifications") == "push-notifications"


class TestNormalizePhase:
    def test_single_digit(self):
        assert normalize_phase("5") == "05"

    def test_decimal(self):
        assert normalize_phase("2.1") == "02.1"

    def test_already_padded(self):
        assert normalize_phase("02.1") == "02.1"

    def test_empty_string(self):
        assert normalize_phase("") == ""

    def test_non_numeric(self):
        assert normalize_phase("abc") == "abc"

    def test_leading_zero_large(self):
        assert normalize_phase("007") == "07"

    def test_two_digit(self):
        assert normalize_phase("12") == "12"

    def test_zero(self):
        assert normalize_phase("0") == "00"

    def test_already_padded_integer(self):
        assert normalize_phase("05") == "05"


class TestInRange:
    def test_inside(self):
        assert in_range("03", 1, 5) is True

    def test_at_start_boundary(self):
        assert in_range("01", 1, 5) is True

    def test_at_end_boundary(self):
        assert in_range("05", 1, 5) is True

    def test_decimal_inside(self):
        assert in_range("05.1", 3, 5) is True

    def test_decimal_outside(self):
        assert in_range("06.0", 3, 5) is False

    def test_below_range(self):
        assert in_range("00", 1, 5) is False

    def test_above_range(self):
        assert in_range("10", 1, 5) is False

    def test_non_numeric(self):
        assert in_range("abc", 1, 5) is False

    def test_decimal_at_upper_edge(self):
        # 5.999 is within range end+0.999
        assert in_range("05.9", 3, 5) is True


class TestExtractPhaseNumber:
    def test_phase_with_name(self):
        assert _extract_phase_number("05-auth") == 5

    def test_decimal_phase(self):
        assert _extract_phase_number("02.1-setup") == 2

    def test_empty_string(self):
        assert _extract_phase_number("") is None

    def test_non_numeric(self):
        assert _extract_phase_number("auth") is None

    def test_bare_number(self):
        assert _extract_phase_number("07") == 7


class TestIsAdjacentPhase:
    def test_n_minus_1(self):
        assert _is_adjacent_phase(6, 5) is True

    def test_n_minus_2(self):
        assert _is_adjacent_phase(6, 4) is True

    def test_equal(self):
        assert _is_adjacent_phase(6, 6) is False

    def test_n_minus_3(self):
        assert _is_adjacent_phase(6, 3) is False

    def test_n_plus_1(self):
        assert _is_adjacent_phase(6, 7) is False


class TestScoreSummary:
    """Test _score_summary relevance scoring."""

    def test_high_via_affects(self):
        fm = {"affects": ["06-ui"], "subsystem": "", "requires": [], "tags": [], "phase": "05-auth"}
        score, reasons = _score_summary(fm, "06", 6, [], [])
        assert score == "HIGH"
        assert any("affects" in r for r in reasons)

    def test_high_via_subsystem(self):
        fm = {"affects": [], "subsystem": "auth", "requires": [], "tags": [], "phase": "03"}
        score, reasons = _score_summary(fm, "06", 6, ["auth"], [])
        assert score == "HIGH"
        assert any("subsystem" in r for r in reasons)

    def test_high_via_requires(self):
        fm = {"affects": [], "subsystem": "", "requires": [{"phase": "06-ui"}], "tags": [], "phase": "03"}
        score, reasons = _score_summary(fm, "06", 6, [], [])
        assert score == "HIGH"
        assert any("requires" in r for r in reasons)

    def test_medium_via_tags(self):
        fm = {"affects": [], "subsystem": "", "requires": [], "tags": ["jwt", "config"], "phase": "01"}
        score, reasons = _score_summary(fm, "06", 6, [], ["jwt"])
        assert score == "MEDIUM"
        assert any("tags" in r for r in reasons)

    def test_medium_via_adjacent(self):
        fm = {"affects": [], "subsystem": "", "requires": [], "tags": [], "phase": "05-auth"}
        score, reasons = _score_summary(fm, "06", 6, [], [])
        assert score == "MEDIUM"
        assert any("adjacent" in r for r in reasons)

    def test_low_default(self):
        fm = {"affects": [], "subsystem": "database", "requires": [], "tags": ["postgres"], "phase": "02-infra"}
        score, reasons = _score_summary(fm, "06", 6, [], [])
        assert score == "LOW"

    def test_string_affects_coercion(self):
        """affects as string instead of list."""
        fm = {"affects": "06-ui", "subsystem": "", "requires": [], "tags": [], "phase": "05"}
        score, _ = _score_summary(fm, "06", 6, [], [])
        assert score == "HIGH"

    def test_none_affects(self):
        fm = {"affects": None, "subsystem": "", "requires": None, "tags": None, "phase": "01"}
        score, _ = _score_summary(fm, "06", 6, [], [])
        assert score == "LOW"

    def test_high_trumps_medium(self):
        """When both HIGH and MEDIUM signals present, result is HIGH."""
        fm = {"affects": ["06-ui"], "subsystem": "", "requires": [], "tags": ["jwt"], "phase": "05-auth"}
        score, reasons = _score_summary(fm, "06", 6, [], ["jwt"])
        assert score == "HIGH"
        # Both reasons should be present
        assert any("affects" in r for r in reasons)
        assert any("tags" in r for r in reasons)

    def test_requires_string_in_list(self):
        """requires as list of strings instead of list of dicts."""
        fm = {"affects": [], "subsystem": "", "requires": ["06-ui"], "tags": [], "phase": "03"}
        score, reasons = _score_summary(fm, "06", 6, [], [])
        assert score == "HIGH"


class TestResolveTransitiveRequires:
    def test_direct_affects(self):
        summaries = [
            {"frontmatter": {"phase": "05-auth", "affects": ["06-ui"], "requires": []}},
        ]
        result = _resolve_transitive_requires(summaries, "06")
        assert "05-auth" in result

    def test_one_hop_chain(self):
        """05-auth affects 06, and requires 04-setup -> 04-setup should be in chain."""
        summaries = [
            {"frontmatter": {"phase": "05-auth", "affects": ["06-ui"], "requires": ["04-setup"]}},
            {"frontmatter": {"phase": "04-setup", "affects": [], "requires": []}},
        ]
        result = _resolve_transitive_requires(summaries, "06")
        assert "05-auth" in result
        assert "04-setup" in result

    def test_no_matches(self):
        summaries = [
            {"frontmatter": {"phase": "02-infra", "affects": [], "requires": []}},
        ]
        result = _resolve_transitive_requires(summaries, "06")
        assert len(result) == 0

    def test_string_affects_coercion(self):
        summaries = [
            {"frontmatter": {"phase": "05-auth", "affects": "06-ui", "requires": []}},
        ]
        result = _resolve_transitive_requires(summaries, "06")
        assert "05-auth" in result

    def test_dict_requires(self):
        summaries = [
            {"frontmatter": {"phase": "05-auth", "affects": ["06-ui"], "requires": [{"phase": "04-setup"}]}},
        ]
        result = _resolve_transitive_requires(summaries, "06")
        assert "04-setup" in result


class TestAggregateFromSummaries:
    def test_skips_low(self):
        summaries = [
            {"relevance": "LOW", "frontmatter": {
                "tech-stack": {"added": ["redis"], "patterns": []},
                "patterns-established": [], "key-files": {}, "key-decisions": [],
            }},
        ]
        result = _aggregate_from_summaries(summaries)
        assert result["tech_stack_added"] == []

    def test_collects_high_and_medium(self):
        summaries = [
            {"relevance": "HIGH", "frontmatter": {
                "tech-stack": {"added": ["jose"], "patterns": ["jwt-auth"]},
                "patterns-established": ["Token rotation"],
                "key-files": {"created": ["src/auth.ts"], "modified": ["src/config.ts"]},
                "key-decisions": ["Use JWT"],
            }},
            {"relevance": "MEDIUM", "frontmatter": {
                "tech-stack": {"added": ["dotenv"], "patterns": []},
                "patterns-established": [],
                "key-files": {"created": ["src/config.ts"], "modified": []},
                "key-decisions": ["Use dotenv"],
            }},
        ]
        result = _aggregate_from_summaries(summaries)
        assert "jose" in result["tech_stack_added"]
        assert "dotenv" in result["tech_stack_added"]
        assert "Token rotation" in result["patterns_established"]
        assert "src/auth.ts" in result["key_files_created"]
        assert "Use JWT" in result["key_decisions"]
        assert "Use dotenv" in result["key_decisions"]

    def test_deduplication(self):
        summaries = [
            {"relevance": "HIGH", "frontmatter": {
                "tech-stack": {"added": ["jose"], "patterns": []},
                "patterns-established": ["P1"],
                "key-files": {"created": ["f.ts"], "modified": []},
                "key-decisions": ["D1"],
            }},
            {"relevance": "HIGH", "frontmatter": {
                "tech-stack": {"added": ["jose"], "patterns": []},
                "patterns-established": ["P1"],
                "key-files": {"created": ["f.ts"], "modified": []},
                "key-decisions": ["D1"],
            }},
        ]
        result = _aggregate_from_summaries(summaries)
        assert result["tech_stack_added"] == ["jose"]
        assert result["patterns_established"] == ["P1"]
        assert result["key_files_created"] == ["f.ts"]
        assert result["key_decisions"] == ["D1"]

    def test_string_coercion(self):
        """String values instead of lists should be coerced."""
        summaries = [
            {"relevance": "HIGH", "frontmatter": {
                "tech-stack": {"added": "single-lib", "patterns": "single-pattern"},
                "patterns-established": "single-established",
                "key-files": {"created": "single-file.ts", "modified": "mod-file.ts"},
                "key-decisions": "single-decision",
            }},
        ]
        result = _aggregate_from_summaries(summaries)
        assert "single-lib" in result["tech_stack_added"]
        assert "single-pattern" in result["patterns_established"]
        assert "single-established" in result["patterns_established"]
        assert "single-file.ts" in result["key_files_created"]
        assert "mod-file.ts" in result["key_files_modified"]
        assert "single-decision" in result["key_decisions"]

    def test_none_fields(self):
        """None values for optional fields should not crash."""
        summaries = [
            {"relevance": "HIGH", "frontmatter": {
                "tech-stack": None,
                "patterns-established": None,
                "key-files": None,
                "key-decisions": None,
            }},
        ]
        result = _aggregate_from_summaries(summaries)
        assert result["tech_stack_added"] == []
        assert result["patterns_established"] == []
        assert result["key_files_created"] == []
        assert result["key_decisions"] == []


class TestBuildExcludePathspecs:
    def test_all_start_with_colon_bang(self):
        specs = build_exclude_pathspecs()
        for spec in specs:
            assert spec.startswith(":!"), f"Expected ':!' prefix, got: {spec}"

    def test_count_matches_exclusions(self):
        specs = build_exclude_pathspecs()
        assert len(specs) == len(PATCH_EXCLUSIONS)


class TestParseFrontmatter:
    def test_valid_yaml(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\ntitle: Hello\ntags: [a, b]\n---\n\n# Content\n")
        result = parse_frontmatter(f)
        assert result == {"title": "Hello", "tags": ["a", "b"]}

    def test_no_frontmatter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Just a heading\n\nSome content.\n")
        assert parse_frontmatter(f) is None

    def test_malformed_yaml(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\n: invalid: yaml: [[\n---\n\nContent\n")
        assert parse_frontmatter(f) is None

    def test_empty_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("")
        assert parse_frontmatter(f) is None

    def test_date_value(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\ndate: 2026-01-15\n---\n\nContent\n")
        result = parse_frontmatter(f)
        assert result is not None
        # YAML parses bare dates as datetime.date objects
        import datetime
        assert result["date"] == datetime.date(2026, 1, 15)

    def test_list_value(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nitems:\n  - one\n  - two\n  - three\n---\n\nContent\n")
        result = parse_frontmatter(f)
        assert result == {"items": ["one", "two", "three"]}

    def test_empty_frontmatter(self, tmp_path):
        """Empty frontmatter (no content between ---) doesn't match the regex."""
        f = tmp_path / "test.md"
        f.write_text("---\n---\n\nContent\n")
        assert parse_frontmatter(f) is None

    def test_empty_frontmatter_with_newline(self, tmp_path):
        """Frontmatter with only a newline between --- returns empty dict."""
        f = tmp_path / "test.md"
        f.write_text("---\n\n---\n\nContent\n")
        result = parse_frontmatter(f)
        assert result == {}

    def test_nonexistent_file(self, tmp_path):
        f = tmp_path / "nonexistent.md"
        assert parse_frontmatter(f) is None


class TestHasReadinessSection:
    def test_present_with_content(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nphase: '05'\n---\n\n## Next Phase Readiness\n\n- Need auth provider\n- Token refresh missing\n")
        assert _has_readiness_section(f) is True

    def test_empty_section(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nphase: '05'\n---\n\n## Next Phase Readiness\n\n## Another Section\n")
        assert _has_readiness_section(f) is False

    def test_absent(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\nphase: '05'\n---\n\n## Summary\n\nSome content.\n")
        assert _has_readiness_section(f) is False

    def test_nonexistent_file(self, tmp_path):
        f = tmp_path / "nonexistent.md"
        assert _has_readiness_section(f) is False


# ===================================================================
# Part 2: Golden-File Integration Test
# ===================================================================


def _build_scan_output(planning: Path) -> dict:
    """Build the same output dict that cmd_scan_planning_context produces."""
    target_phase = "06"
    target_num = 6
    subsystems = ["auth"]
    keywords = ["jwt", "ui"]
    parse_errors: list[dict] = []

    summaries, summaries_src = _scan_summaries(
        planning, target_phase, target_num, subsystems, keywords, parse_errors
    )
    debug_learnings, debug_src = _scan_debug_docs(planning, parse_errors)
    adhoc_learnings, adhoc_src = _scan_adhoc_summaries(planning, parse_errors)
    completed_todos, completed_src = _scan_todos(planning, "done", parse_errors)
    pending_todos, pending_src = _scan_todos(planning, "", parse_errors)
    knowledge_files, knowledge_src = _scan_knowledge_files(planning, subsystems)

    aggregated = _aggregate_from_summaries(summaries)

    return {
        "success": True,
        "target": {
            "phase": target_phase,
            "phase_name": "",
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


def _normalize_paths(obj, base: Path):
    """Recursively replace absolute paths with relative paths for stable comparison."""
    base_str = str(base)
    if isinstance(obj, str):
        return obj.replace(base_str, "<FIXTURE>")
    if isinstance(obj, list):
        return [_normalize_paths(item, base) for item in obj]
    if isinstance(obj, dict):
        return {k: _normalize_paths(v, base) for k, v in obj.items()}
    return obj


GOLDEN_FILE = Path(__file__).parent / "fixtures" / "scan-context" / "expected-output.json"


class TestGoldenFile:
    """Full JSON comparison of scan-planning-context output against golden file."""

    def test_golden_file(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        normalized = _normalize_paths(output, FIXTURE_PLANNING.parent)

        if REGENERATE_GOLDEN:
            GOLDEN_FILE.write_text(
                json.dumps(normalized, indent=2, cls=_SafeEncoder) + "\n",
                encoding="utf-8",
            )
            pytest.skip("Golden file regenerated — review and set REGENERATE_GOLDEN = False")

        expected = json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))
        assert normalized == expected, (
            "Output differs from golden file. "
            "Set REGENERATE_GOLDEN = True and re-run to update."
        )


class TestScanIntegrationTargeted:
    """Targeted assertions against fixture data."""

    def test_summary_relevance_scores(self):
        parse_errors: list[dict] = []
        summaries, _ = _scan_summaries(
            FIXTURE_PLANNING, "06", 6, ["auth"], ["jwt", "ui"], parse_errors
        )
        by_phase = {s["frontmatter"]["phase"]: s for s in summaries}

        assert by_phase["02-infra"]["relevance"] == "LOW"
        assert by_phase["05-auth"]["relevance"] == "HIGH"
        # 04-setup: upgraded from MEDIUM to HIGH via transitive requires
        assert by_phase["04-setup"]["relevance"] == "HIGH"

    def test_transitive_requires_upgrade(self):
        """04-setup gets upgraded to HIGH because 05-auth affects 06 and requires 04-setup."""
        parse_errors: list[dict] = []
        summaries, _ = _scan_summaries(
            FIXTURE_PLANNING, "06", 6, ["auth"], ["jwt", "ui"], parse_errors
        )
        setup = next(s for s in summaries if s["frontmatter"]["phase"] == "04-setup")
        assert setup["relevance"] == "HIGH"
        assert any("transitive" in r for r in setup["match_reasons"])

    def test_aggregated_includes_high_and_medium(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        agg = output["aggregated"]

        # From 05-auth (HIGH) and 04-setup (upgraded to HIGH)
        assert "jose" in agg["tech_stack_added"]
        assert "bcrypt" in agg["tech_stack_added"]
        assert "dotenv" in agg["tech_stack_added"]

        # 02-infra is LOW, so postgres should NOT be in aggregated
        assert "postgres" not in agg["tech_stack_added"]

    def test_debug_learnings_collected(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        assert len(output["debug_learnings"]) == 1
        debug = output["debug_learnings"][0]
        assert debug["subsystem"] == "auth"
        assert "clock skew" in debug["root_cause"].lower()

    def test_adhoc_learnings_collected(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        assert len(output["adhoc_learnings"]) == 2
        # Flat file (old format with learnings field)
        auth_adhoc = next(a for a in output["adhoc_learnings"] if a["subsystem"] == "auth")
        assert len(auth_adhoc["learnings"]) == 2
        # Subdirectory file (phase-style with key-decisions fallback)
        api_adhoc = next(a for a in output["adhoc_learnings"] if a["subsystem"] == "api")
        assert len(api_adhoc["learnings"]) == 2
        assert "duplicate route handlers" in api_adhoc["learnings"][0].lower()

    def test_pending_todos_collected(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        assert len(output["pending_todos"]) == 1
        assert output["pending_todos"][0]["title"] == "Add logout endpoint"

    def test_completed_todos_collected(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        assert len(output["completed_todos"]) == 1
        assert output["completed_todos"][0]["title"] == "Set up database migrations"

    def test_knowledge_files_matched(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        knowledge = output["knowledge_files"]
        assert len(knowledge) == 1
        assert knowledge[0]["subsystem"] == "auth"
        assert knowledge[0]["matched"] is True

    def test_readiness_warnings_on_05_auth(self):
        parse_errors: list[dict] = []
        summaries, _ = _scan_summaries(
            FIXTURE_PLANNING, "06", 6, ["auth"], ["jwt", "ui"], parse_errors
        )
        auth_summary = next(s for s in summaries if s["frontmatter"]["phase"] == "05-auth")
        assert auth_summary["has_readiness_warnings"] is True

    def test_no_parse_errors(self):
        output = _build_scan_output(FIXTURE_PLANNING)
        assert output["sources"]["parse_errors"] == []


# ===================================================================
# Part 3: Milestone Naming Detection Tests
# ===================================================================


class TestDetectVersionedMilestoneDirs:
    """Test _detect_versioned_milestone_dirs detection logic."""

    def test_standard_dirs(self, tmp_path):
        """v0.1/, v0.2/ with .md files detected as standard."""
        planning = tmp_path / ".planning"
        ms = planning / "milestones"
        (ms / "v0.1").mkdir(parents=True)
        (ms / "v0.1" / "ROADMAP.md").write_text("# Roadmap")
        (ms / "v0.2").mkdir(parents=True)
        (ms / "v0.2" / "ROADMAP.md").write_text("# Roadmap")

        result = _detect_versioned_milestone_dirs(planning)
        assert len(result) == 2
        assert result[0]["version"] == "v0.1"
        assert result[0]["type"] == "standard"
        assert result[0]["sub"] is None
        assert result[1]["version"] == "v0.2"
        assert result[1]["type"] == "standard"

    def test_nested_dirs(self, tmp_path):
        """v2.0.0/ with sub-dirs and no .md files detected as nested."""
        planning = tmp_path / ".planning"
        ms = planning / "milestones"
        v200 = ms / "v2.0.0"
        (v200 / "quests").mkdir(parents=True)
        (v200 / "quests" / "ROADMAP.md").write_text("# Roadmap")
        (v200 / "sanctuary").mkdir(parents=True)
        (v200 / "sanctuary" / "ROADMAP.md").write_text("# Roadmap")

        result = _detect_versioned_milestone_dirs(planning)
        assert len(result) == 2
        assert result[0]["version"] == "v2.0.0"
        assert result[0]["sub"] == "quests"
        assert result[0]["type"] == "nested"
        assert result[1]["sub"] == "sanctuary"
        assert result[1]["type"] == "nested"

    def test_mixed_standard_and_nested(self, tmp_path):
        """v2.0.0/quests/ (nested) + v2.2.0/ (standard) both detected."""
        planning = tmp_path / ".planning"
        ms = planning / "milestones"
        # Nested
        v200 = ms / "v2.0.0"
        (v200 / "quests").mkdir(parents=True)
        (v200 / "quests" / "ROADMAP.md").write_text("# Roadmap")
        # Standard
        (ms / "v2.2.0").mkdir(parents=True)
        (ms / "v2.2.0" / "ROADMAP.md").write_text("# Roadmap")

        result = _detect_versioned_milestone_dirs(planning)
        assert len(result) == 2
        nested = [r for r in result if r["type"] == "nested"]
        standard = [r for r in result if r["type"] == "standard"]
        assert len(nested) == 1
        assert nested[0]["sub"] == "quests"
        assert len(standard) == 1
        assert standard[0]["version"] == "v2.2.0"

    def test_slug_dirs_ignored(self, tmp_path):
        """mvp/, blast-pass/ are not flagged."""
        planning = tmp_path / ".planning"
        ms = planning / "milestones"
        (ms / "mvp").mkdir(parents=True)
        (ms / "mvp" / "ROADMAP.md").write_text("# Roadmap")
        (ms / "blast-pass").mkdir(parents=True)
        (ms / "blast-pass" / "ROADMAP.md").write_text("# Roadmap")

        result = _detect_versioned_milestone_dirs(planning)
        assert result == []

    def test_no_milestones_dir(self, tmp_path):
        """No milestones/ directory returns empty."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)

        result = _detect_versioned_milestone_dirs(planning)
        assert result == []

    def test_empty_milestones_dir(self, tmp_path):
        """Empty milestones/ directory returns empty."""
        planning = tmp_path / ".planning"
        (planning / "milestones").mkdir(parents=True)

        result = _detect_versioned_milestone_dirs(planning)
        assert result == []

    def test_phases_subdir_excluded_from_nested(self, tmp_path):
        """phases/ sub-directory inside v-dir is excluded from nested detection."""
        planning = tmp_path / ".planning"
        ms = planning / "milestones"
        v01 = ms / "v0.1"
        (v01 / "phases" / "01-setup").mkdir(parents=True)
        # Has .md files, so it's standard despite having phases/ sub-dir
        (v01 / "ROADMAP.md").write_text("# Roadmap")

        result = _detect_versioned_milestone_dirs(planning)
        assert len(result) == 1
        assert result[0]["type"] == "standard"


class TestParseMilestoneNameMapping:
    """Test _parse_milestone_name_mapping parsing logic."""

    def test_standard_headers(self, tmp_path):
        """Parses ## v0.1 MVP (Shipped: ...) correctly."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)
        (planning / "MILESTONES.md").write_text(
            "# Milestones\n\n"
            "## v0.1 MVP (Shipped: 2026-01-15)\n\n"
            "Some content.\n"
        )

        result = _parse_milestone_name_mapping(planning)
        assert len(result) == 1
        assert result[0]["version"] == "v0.1"
        assert result[0]["name"] == "MVP"
        assert result[0]["slug"] == "mvp"

    def test_multi_word_names(self, tmp_path):
        """Parses multi-word names with special chars."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)
        (planning / "MILESTONES.md").write_text(
            "# Milestones\n\n"
            "## v0.1 MVP - POSitive Plus SDK Integration (Shipped: 2026-01-15)\n\n"
        )

        result = _parse_milestone_name_mapping(planning)
        assert len(result) == 1
        assert result[0]["name"] == "MVP - POSitive Plus SDK Integration"
        assert result[0]["slug"] == "mvp-positive-plus-sdk-integration"

    def test_duplicate_version(self, tmp_path):
        """Two v2.0.0 entries (like ForgeBlast) both extracted."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)
        (planning / "MILESTONES.md").write_text(
            "# Milestones\n\n"
            "## v2.0.0 Quests Feature (Shipped: 2026-01-01)\n\n"
            "Content.\n\n"
            "## v2.0.0 Sanctuary (Shipped: 2026-02-01)\n\n"
            "Content.\n"
        )

        result = _parse_milestone_name_mapping(planning)
        assert len(result) == 2
        versions = [r["version"] for r in result]
        assert versions == ["v2.0.0", "v2.0.0"]
        names = [r["name"] for r in result]
        assert "Quests Feature" in names
        assert "Sanctuary" in names

    def test_no_versioned_headers(self, tmp_path):
        """New-format headers without version prefix are not matched."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)
        (planning / "MILESTONES.md").write_text(
            "# Milestones\n\n"
            "## MVP (Shipped: 2026-01-15)\n\n"
            "Content.\n"
        )

        result = _parse_milestone_name_mapping(planning)
        assert result == []

    def test_current_milestone_from_project(self, tmp_path):
        """Parses ## Current Milestone: v0.3 Demo Release from PROJECT.md."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)
        (planning / "PROJECT.md").write_text(
            "# Project\n\n"
            "## Current Milestone: v0.3 Demo Release\n\n"
            "Content.\n"
        )

        result = _parse_milestone_name_mapping(planning)
        assert len(result) == 1
        assert result[0]["version"] == "v0.3"
        assert result[0]["name"] == "Demo Release"
        assert result[0]["slug"] == "demo-release"
        assert result[0].get("current") is True

    def test_no_files(self, tmp_path):
        """No MILESTONES.md or PROJECT.md returns empty."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)

        result = _parse_milestone_name_mapping(planning)
        assert result == []

    def test_started_status(self, tmp_path):
        """Parses Started: status headers too."""
        planning = tmp_path / ".planning"
        planning.mkdir(parents=True)
        (planning / "MILESTONES.md").write_text(
            "# Milestones\n\n"
            "## v0.2 Infrastructure (Started: 2026-02-01)\n\n"
        )

        result = _parse_milestone_name_mapping(planning)
        assert len(result) == 1
        assert result[0]["version"] == "v0.2"
        assert result[0]["name"] == "Infrastructure"


# ---------------------------------------------------------------------------
# Tests: cmd_set_last_command
# ---------------------------------------------------------------------------


def _make_args(command_string: str) -> argparse.Namespace:
    return argparse.Namespace(command_string=command_string)


class TestSetLastCommand:
    """Tests for the set-last-command subcommand."""

    def _patch_git_root(self, tmp_path):
        return mock.patch.object(_mod, "find_git_root", return_value=tmp_path)

    def test_replaces_existing_last_command(self, tmp_path):
        state = tmp_path / ".planning" / "STATE.md"
        state.parent.mkdir(parents=True)
        state.write_text(
            "# State\n"
            "Status: In progress\n"
            "Last Command: ms:old-cmd | 2025-01-01 00:00\n"
            "Phase: 10\n"
        )

        with self._patch_git_root(tmp_path):
            cmd_set_last_command(_make_args("ms:plan-phase 10"))

        text = state.read_text()
        assert "ms:plan-phase 10 |" in text
        assert "ms:old-cmd" not in text
        # Verify only one Last Command line
        assert text.count("Last Command:") == 1

    def test_inserts_after_status_when_missing(self, tmp_path):
        state = tmp_path / ".planning" / "STATE.md"
        state.parent.mkdir(parents=True)
        state.write_text(
            "# State\n"
            "Status: In progress\n"
            "Phase: 10\n"
        )

        with self._patch_git_root(tmp_path):
            cmd_set_last_command(_make_args("ms:execute-phase 10"))

        text = state.read_text()
        assert "Last Command: ms:execute-phase 10 |" in text
        # Should appear after Status line
        lines = text.splitlines()
        status_idx = next(i for i, l in enumerate(lines) if l.startswith("Status:"))
        last_cmd_idx = next(i for i, l in enumerate(lines) if l.startswith("Last Command:"))
        assert last_cmd_idx == status_idx + 1

    def test_missing_state_file_warns(self, tmp_path, capsys):
        with self._patch_git_root(tmp_path):
            cmd_set_last_command(_make_args("ms:plan-phase 10"))

        captured = capsys.readouterr()
        assert "Warning: STATE.md not found" in captured.err
        assert captured.out == ""

    def test_missing_both_lines_warns(self, tmp_path, capsys):
        state = tmp_path / ".planning" / "STATE.md"
        state.parent.mkdir(parents=True)
        original = "# State\nPhase: 10\n"
        state.write_text(original)

        with self._patch_git_root(tmp_path):
            cmd_set_last_command(_make_args("ms:adhoc"))

        captured = capsys.readouterr()
        assert "Warning:" in captured.err
        # File should be unchanged
        assert state.read_text() == original

    def test_timestamp_format(self, tmp_path):
        state = tmp_path / ".planning" / "STATE.md"
        state.parent.mkdir(parents=True)
        state.write_text("# State\nStatus: Idle\nLast Command: old\n")

        fake_dt = mock.MagicMock()
        fake_dt.datetime.now.return_value.strftime.return_value = "2026-02-24 14:30"
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod, "datetime", fake_dt):
            cmd_set_last_command(_make_args("ms:verify-work 10"))

        text = state.read_text()
        assert "Last Command: ms:verify-work 10 | 2026-02-24 14:30" in text


# ===================================================================
# Part 4: UAT File Management Tests
# ===================================================================

UATFile = _mod.UATFile
cmd_uat_init = _mod.cmd_uat_init
cmd_uat_update = _mod.cmd_uat_update
cmd_uat_status = _mod.cmd_uat_status

# Shared fixture: a complete UAT.md matching the template format
UAT_FIXTURE = """\
---
status: testing
phase: 05-auth
source: [05-01-SUMMARY.md]
started: '2026-02-24 10:00'
updated: '2026-02-24 10:30'
current_batch: 2
mocked_files: [auth_service.dart]
pre_work_stash: null
---

## Progress

total: 5
tested: 3
passed: 2
issues: 1
fixing: 0
pending: 2
skipped: 0

## Current Batch

batch: 2 of 3
name: "Error States"
mock_type: error_state
tests: [3, 4]
status: testing

## Tests

### 1. Login with valid credentials
expected: User sees dashboard after entering valid email/password
mock_required: false
mock_type: null
result: pass

### 2. View profile page
expected: Profile shows user name and email
mock_required: false
mock_type: null
result: pass

### 3. Login with invalid password
expected: Error banner shows "Invalid credentials"
mock_required: true
mock_type: error_state
result: issue
reported: "Shows generic error instead of specific message"
severity: major
fix_status: applied
fix_commit: abc1234
retry_count: 0

### 4. Login with expired token
expected: Redirect to login page with session expired message
mock_required: true
mock_type: error_state
result: [pending]

### 5. Premium feature access
expected: Shows upgrade prompt for free users
mock_required: true
mock_type: premium_user
result: [pending]

## Fixes Applied

- commit: abc1234
  test: 3
  description: "Fixed error message to show specific auth error"
  files: [auth_service.dart, login_page.dart]

## Batches

### Batch 1: No Mocks Required
tests: [1, 2]
status: complete
mock_type: null
passed: 2
issues: 0

### Batch 2: Error States
tests: [3, 4]
status: testing
mock_type: error_state

### Batch 3: Premium Features
tests: [5]
status: pending
mock_type: premium_user

## Assumptions
"""

# Minimal UAT.md with empty fixes/assumptions
UAT_MINIMAL = """\
---
status: testing
phase: 03-setup
source: [03-01-SUMMARY.md]
started: '2026-02-24 10:00'
updated: '2026-02-24 10:00'
current_batch: 1
mocked_files: []
pre_work_stash: null
---

## Progress

total: 2
tested: 0
passed: 0
issues: 0
fixing: 0
pending: 2
skipped: 0

## Current Batch

batch: 1 of 1
name: "No Mocks"
mock_type: null
tests: [1, 2]
status: pending

## Tests

### 1. Basic setup check
expected: App starts without errors
mock_required: false
mock_type: null
result: [pending]

### 2. Config loads
expected: Config values appear in settings
mock_required: false
mock_type: null
result: [pending]

## Fixes Applied

## Batches

### Batch 1: No Mocks
tests: [1, 2]
status: pending
mock_type: null

## Assumptions
"""


class TestUATFileParse:
    """Test UATFile.parse with complete and minimal fixtures."""

    def test_parse_complete_file(self):
        uat = UATFile.parse(UAT_FIXTURE)
        assert uat.frontmatter["status"] == "testing"
        assert uat.frontmatter["phase"] == "05-auth"
        assert uat.frontmatter["current_batch"] == 2
        assert uat.frontmatter["mocked_files"] == ["auth_service.dart"]
        assert len(uat.tests) == 5
        assert len(uat.batches) == 3
        assert len(uat.fixes) == 1
        assert len(uat.assumptions) == 0

    def test_parse_minimal_file(self):
        uat = UATFile.parse(UAT_MINIMAL)
        assert uat.frontmatter["phase"] == "03-setup"
        assert len(uat.tests) == 2
        assert len(uat.batches) == 1
        assert len(uat.fixes) == 0
        assert len(uat.assumptions) == 0

    def test_parse_test_with_issue_fields(self):
        uat = UATFile.parse(UAT_FIXTURE)
        t3 = next(t for t in uat.tests if t["num"] == "3")
        assert t3["result"] == "issue"
        assert "Shows generic error" in t3["reported"]
        assert t3["severity"] == "major"
        assert t3["fix_status"] == "applied"
        assert t3["fix_commit"] == "abc1234"
        assert t3["retry_count"] == "0"

    def test_parse_progress(self):
        uat = UATFile.parse(UAT_FIXTURE)
        assert uat.progress["total"] == "5"
        assert uat.progress["passed"] == "2"
        assert uat.progress["pending"] == "2"

    def test_parse_current_batch(self):
        uat = UATFile.parse(UAT_FIXTURE)
        assert uat.current_batch["batch"] == "2 of 3"
        assert uat.current_batch["mock_type"] == "error_state"
        assert uat.current_batch["status"] == "testing"

    def test_parse_fixes(self):
        uat = UATFile.parse(UAT_FIXTURE)
        fix = uat.fixes[0]
        assert fix["commit"] == "abc1234"
        assert fix["test"] == "3"
        assert "Fixed error message" in fix["description"]

    def test_parse_batches(self):
        uat = UATFile.parse(UAT_FIXTURE)
        b1 = uat.batches[0]
        assert b1["name"] == "No Mocks Required"
        assert b1["status"] == "complete"
        assert b1["passed"] == "2"


class TestUATFileRoundtrip:
    """Test parse -> serialize roundtrip."""

    def test_roundtrip_preserves_structure(self):
        uat = UATFile.parse(UAT_FIXTURE)
        output = uat.serialize()
        # Re-parse the output
        uat2 = UATFile.parse(output)
        assert len(uat2.tests) == len(uat.tests)
        assert len(uat2.batches) == len(uat.batches)
        assert len(uat2.fixes) == len(uat.fixes)
        assert uat2.frontmatter["phase"] == "05-auth"
        # Test names preserved
        for t1, t2 in zip(uat.tests, uat2.tests):
            assert t1["name"] == t2["name"]
            assert t1["result"] == t2["result"]

    def test_roundtrip_minimal(self):
        uat = UATFile.parse(UAT_MINIMAL)
        output = uat.serialize()
        uat2 = UATFile.parse(output)
        assert len(uat2.tests) == 2
        assert len(uat2.fixes) == 0
        assert len(uat2.assumptions) == 0


class TestUATFileRecalcProgress:
    """Test recalc_progress with various result combinations."""

    def test_all_pending(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.recalc_progress()
        assert uat.progress["total"] == "2"
        assert uat.progress["pending"] == "2"
        assert uat.progress["tested"] == "0"
        assert uat.progress["passed"] == "0"

    def test_mixed_results(self):
        uat = UATFile.parse(UAT_FIXTURE)
        uat.recalc_progress()
        assert uat.progress["total"] == "5"
        assert uat.progress["passed"] == "2"
        # Test 3 has fix_status=applied → fixing
        assert uat.progress["fixing"] == "1"
        assert uat.progress["pending"] == "2"

    def test_verified_fix_counts_as_passed(self):
        uat = UATFile.parse(UAT_FIXTURE)
        # Change test 3's fix_status to verified
        t3 = next(t for t in uat.tests if t["num"] == "3")
        t3["fix_status"] = "verified"
        uat.recalc_progress()
        assert uat.progress["passed"] == "3"  # 2 pass + 1 verified
        assert uat.progress["fixing"] == "0"

    def test_blocked_counts_as_pending(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.tests[0]["result"] = "blocked"
        uat.recalc_progress()
        assert uat.progress["pending"] == "2"  # 1 blocked + 1 [pending]
        assert uat.progress["tested"] == "0"

    def test_skipped(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.tests[0]["result"] = "skipped"
        uat.recalc_progress()
        assert uat.progress["skipped"] == "1"
        assert uat.progress["pending"] == "1"
        assert uat.progress["tested"] == "1"


class TestUATFileMutations:
    """Test update_test, update_batch, update_session."""

    def test_update_test(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.update_test(1, {"result": "pass"})
        t1 = next(t for t in uat.tests if t["num"] == "1")
        assert t1["result"] == "pass"

    def test_update_test_not_found(self):
        uat = UATFile.parse(UAT_MINIMAL)
        with pytest.raises(ValueError, match="Test 99 not found"):
            uat.update_test(99, {"result": "pass"})

    def test_update_batch(self):
        uat = UATFile.parse(UAT_FIXTURE)
        uat.update_batch(1, {"passed": "3", "issues": "0"})
        b1 = next(b for b in uat.batches if b["num"] == "1")
        assert b1["passed"] == "3"

    def test_update_session(self):
        uat = UATFile.parse(UAT_FIXTURE)
        uat.update_session({"status": "fixing"})
        assert uat.frontmatter["status"] == "fixing"

    def test_update_session_mocked_files(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.update_session({"mocked_files": "a.dart,b.dart"})
        assert uat.frontmatter["mocked_files"] == ["a.dart", "b.dart"]

    def test_update_session_clear_mocked_files(self):
        uat = UATFile.parse(UAT_FIXTURE)
        uat.update_session({"mocked_files": ""})
        assert uat.frontmatter["mocked_files"] == []

    def test_update_session_current_batch_syncs(self):
        uat = UATFile.parse(UAT_FIXTURE)
        uat.update_session({"current_batch": "3"})
        assert uat.frontmatter["current_batch"] == 3
        assert uat.current_batch["batch"] == "3 of 3"
        assert "Premium" in uat.current_batch["name"]


class TestUATFileAppendFix:
    """Test append_fix new and in-place update."""

    def test_append_new_fix(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.append_fix({
            "commit": "def567",
            "test": 1,
            "description": "Fixed setup",
            "files": ["setup.dart"],
        })
        assert len(uat.fixes) == 1
        assert uat.fixes[0]["commit"] == "def567"
        assert uat.fixes[0]["files"] == "[setup.dart]"

    def test_append_fix_same_test_updates_in_place(self):
        uat = UATFile.parse(UAT_FIXTURE)
        assert len(uat.fixes) == 1
        uat.append_fix({
            "commit": "new999",
            "test": 3,
            "description": "Better fix for auth error",
            "files": ["auth_service.dart"],
        })
        # Still 1 fix, updated in place
        assert len(uat.fixes) == 1
        assert uat.fixes[0]["commit"] == "new999"
        assert "Better fix" in uat.fixes[0]["description"]

    def test_append_assumption(self):
        uat = UATFile.parse(UAT_MINIMAL)
        uat.append_assumption({
            "test": 2,
            "name": "Config loads",
            "expected": "Config values appear",
            "reason": "No config file available",
        })
        assert len(uat.assumptions) == 1
        assert uat.assumptions[0]["test"] == "2"


class TestCmdUatInit:
    """Tests for uat-init command."""

    def _patch_git_root(self, tmp_path):
        return mock.patch.object(_mod, "find_git_root", return_value=tmp_path)

    def test_creates_file_from_valid_json(self, tmp_path, capsys):
        # Create phase dir
        phase_dir = tmp_path / ".planning" / "phases" / "05-auth"
        phase_dir.mkdir(parents=True)

        input_json = json.dumps({
            "source": ["05-01-SUMMARY.md"],
            "tests": [
                {"name": "Login works", "expected": "User sees dashboard", "mock_required": False, "mock_type": None},
                {"name": "Logout works", "expected": "User sees login page", "mock_required": False, "mock_type": None},
            ],
            "batches": [
                {"name": "No Mocks", "mock_type": None, "tests": [1, 2]},
            ],
        })

        args = argparse.Namespace(phase="5")
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod.sys, "stdin", io.StringIO(input_json)):
            cmd_uat_init(args)

        captured = capsys.readouterr()
        assert "2 tests" in captured.out
        assert "1 batches" in captured.out

        uat_path = phase_dir / "05-auth-UAT.md"
        assert uat_path.is_file()
        content = uat_path.read_text()
        assert "Login works" in content
        assert "Logout works" in content

    def test_auto_creates_phase_dir(self, tmp_path, capsys):
        (tmp_path / ".planning" / "phases").mkdir(parents=True)

        input_json = json.dumps({
            "source": [],
            "tests": [{"name": "Test", "expected": "Works"}],
            "batches": [{"name": "B1", "tests": [1]}],
        })

        args = argparse.Namespace(phase="99")
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod.sys, "stdin", io.StringIO(input_json)):
            cmd_uat_init(args)

        captured = capsys.readouterr()
        assert "1 tests" in captured.out
        assert (tmp_path / ".planning" / "phases" / "99").is_dir()

    def test_invalid_json_exits(self, tmp_path):
        (tmp_path / ".planning" / "phases" / "05-auth").mkdir(parents=True)

        args = argparse.Namespace(phase="5")
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod.sys, "stdin", io.StringIO("not json")), \
             pytest.raises(SystemExit) as exc:
            cmd_uat_init(args)
        assert exc.value.code == 1

    def test_stdout_contains_path_and_counts(self, tmp_path, capsys):
        phase_dir = tmp_path / ".planning" / "phases" / "03-setup"
        phase_dir.mkdir(parents=True)

        input_json = json.dumps({
            "source": ["03-01-SUMMARY.md"],
            "tests": [
                {"name": "T1", "expected": "E1"},
                {"name": "T2", "expected": "E2"},
                {"name": "T3", "expected": "E3"},
            ],
            "batches": [
                {"name": "B1", "tests": [1, 2]},
                {"name": "B2", "tests": [3]},
            ],
        })

        args = argparse.Namespace(phase="3")
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod.sys, "stdin", io.StringIO(input_json)):
            cmd_uat_init(args)

        captured = capsys.readouterr()
        assert "3 tests" in captured.out
        assert "2 batches" in captured.out
        assert "03-setup-UAT.md" in captured.out


class TestCmdUatUpdate:
    """Tests for uat-update command."""

    def _patch_git_root(self, tmp_path):
        return mock.patch.object(_mod, "find_git_root", return_value=tmp_path)

    def _setup_uat(self, tmp_path, content=UAT_FIXTURE):
        phase_dir = tmp_path / ".planning" / "phases" / "05-auth"
        phase_dir.mkdir(parents=True)
        uat_path = phase_dir / "05-auth-UAT.md"
        uat_path.write_text(content)
        return uat_path

    def test_update_test_result_pass(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path)

        args = argparse.Namespace(
            phase="5", test=4, batch=None, session=False,
            append_fix=False, append_assumption=False,
            fields=["result=pass"],
        )
        with self._patch_git_root(tmp_path):
            cmd_uat_update(args)

        captured = capsys.readouterr()
        assert "Updated test 4" in captured.out
        assert "Progress:" in captured.out

        uat = UATFile.parse(uat_path.read_text())
        t4 = next(t for t in uat.tests if t["num"] == "4")
        assert t4["result"] == "pass"

    def test_update_test_issue_with_fields(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path)

        args = argparse.Namespace(
            phase="5", test=4, batch=None, session=False,
            append_fix=False, append_assumption=False,
            fields=["result=issue", "severity=major", "fix_status=investigating", "retry_count=0"],
        )
        with self._patch_git_root(tmp_path):
            cmd_uat_update(args)

        uat = UATFile.parse(uat_path.read_text())
        t4 = next(t for t in uat.tests if t["num"] == "4")
        assert t4["result"] == "issue"
        assert t4["severity"] == "major"
        assert t4["fix_status"] == "investigating"

    def test_update_batch_complete(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path)

        args = argparse.Namespace(
            phase="5", test=None, batch=2, session=False,
            append_fix=False, append_assumption=False,
            fields=["status=complete", "passed=1", "issues=1"],
        )
        with self._patch_git_root(tmp_path):
            cmd_uat_update(args)

        uat = UATFile.parse(uat_path.read_text())
        b2 = next(b for b in uat.batches if b["num"] == "2")
        assert b2["status"] == "complete"
        assert b2["passed"] == "1"

    def test_update_session_frontmatter(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path)

        args = argparse.Namespace(
            phase="5", test=None, batch=None, session=True,
            append_fix=False, append_assumption=False,
            fields=["status=fixing"],
        )
        with self._patch_git_root(tmp_path):
            cmd_uat_update(args)

        uat = UATFile.parse(uat_path.read_text())
        assert uat.frontmatter["status"] == "fixing"

    def test_append_fix_from_stdin(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path)

        fix_json = json.dumps({
            "commit": "xyz789",
            "test": 4,
            "description": "Fixed token expiry redirect",
            "files": ["auth_middleware.dart"],
        })

        args = argparse.Namespace(
            phase="5", test=None, batch=None, session=False,
            append_fix=True, append_assumption=False,
            fields=[],
        )
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod.sys, "stdin", io.StringIO(fix_json)):
            cmd_uat_update(args)

        uat = UATFile.parse(uat_path.read_text())
        assert len(uat.fixes) == 2
        assert uat.fixes[1]["commit"] == "xyz789"

    def test_append_assumption_from_stdin(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path)

        assumption_json = json.dumps({
            "test": 5,
            "name": "Premium feature access",
            "expected": "Shows upgrade prompt",
            "reason": "No premium account available",
        })

        args = argparse.Namespace(
            phase="5", test=None, batch=None, session=False,
            append_fix=False, append_assumption=True,
            fields=[],
        )
        with self._patch_git_root(tmp_path), \
             mock.patch.object(_mod.sys, "stdin", io.StringIO(assumption_json)):
            cmd_uat_update(args)

        uat = UATFile.parse(uat_path.read_text())
        assert len(uat.assumptions) == 1
        assert uat.assumptions[0]["test"] == "5"

    def test_progress_auto_recalculated(self, tmp_path, capsys):
        uat_path = self._setup_uat(tmp_path, UAT_MINIMAL)

        args = argparse.Namespace(
            phase="3", test=1, batch=None, session=False,
            append_fix=False, append_assumption=False,
            fields=["result=pass"],
        )

        # Adjust path for phase 03-setup
        phase_dir = tmp_path / ".planning" / "phases" / "03-setup"
        phase_dir.mkdir(parents=True, exist_ok=True)
        (phase_dir / "03-setup-UAT.md").write_text(UAT_MINIMAL)

        with self._patch_git_root(tmp_path):
            cmd_uat_update(args)

        uat = UATFile.parse((phase_dir / "03-setup-UAT.md").read_text())
        assert uat.progress["passed"] == "1"
        assert uat.progress["tested"] == "1"
        assert uat.progress["pending"] == "1"


class TestCmdUatStatus:
    """Tests for uat-status command."""

    def _patch_git_root(self, tmp_path):
        return mock.patch.object(_mod, "find_git_root", return_value=tmp_path)

    def _setup_uat(self, tmp_path, content=UAT_FIXTURE):
        phase_dir = tmp_path / ".planning" / "phases" / "05-auth"
        phase_dir.mkdir(parents=True)
        uat_path = phase_dir / "05-auth-UAT.md"
        uat_path.write_text(content)
        return uat_path

    def test_outputs_valid_json(self, tmp_path, capsys):
        self._setup_uat(tmp_path)

        args = argparse.Namespace(phase="5")
        with self._patch_git_root(tmp_path):
            cmd_uat_status(args)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "testing"
        assert output["current_batch"] == 2
        assert output["total_batches"] == 3
        assert output["progress"]["total"] == 5
        assert output["progress"]["passed"] == 2
        assert isinstance(output["mocked_files"], list)

    def test_fixing_tests_listed(self, tmp_path, capsys):
        self._setup_uat(tmp_path)

        args = argparse.Namespace(phase="5")
        with self._patch_git_root(tmp_path):
            cmd_uat_status(args)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        # Test 3 has fix_status=applied
        assert len(output["fixing_tests"]) == 1
        assert output["fixing_tests"][0]["num"] == 3
        assert output["fixing_tests"][0]["fix_status"] == "applied"
        assert output["fixing_tests"][0]["fix_commit"] == "abc1234"

    def test_fixing_tests_without_commit(self, tmp_path, capsys):
        """Tests with fix_status=investigating have empty fix_commit."""
        uat_path = self._setup_uat(tmp_path)
        # Change test 3 to investigating (no fix_commit yet)
        content = uat_path.read_text()
        content = content.replace("fix_status: applied", "fix_status: investigating")
        content = content.replace("fix_commit: abc1234\n", "")
        uat_path.write_text(content)

        args = argparse.Namespace(phase="5")
        with self._patch_git_root(tmp_path):
            cmd_uat_status(args)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["fixing_tests"][0]["fix_commit"] == ""

    def test_missing_file_exits(self, tmp_path):
        (tmp_path / ".planning" / "phases" / "05-auth").mkdir(parents=True)

        args = argparse.Namespace(phase="5")
        with self._patch_git_root(tmp_path), \
             pytest.raises(SystemExit) as exc:
            cmd_uat_status(args)
        assert exc.value.code == 1
