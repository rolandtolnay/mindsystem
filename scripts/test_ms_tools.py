"""Tests for ms-tools.py pure logic layer and scan-planning-context integration."""

import importlib.util
import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import ms-tools.py (hyphenated filename requires importlib)
# ---------------------------------------------------------------------------

_spec = importlib.util.spec_from_file_location(
    "ms_tools", Path(__file__).parent / "ms-tools.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

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
_SafeEncoder = _mod._SafeEncoder

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_PLANNING = Path(__file__).parent / "fixtures" / "scan-context" / ".planning"

# Set to True, run once, review expected-output.json, then set back to False.
REGENERATE_GOLDEN = False


# ===================================================================
# Part 1: Pure Function Unit Tests
# ===================================================================


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
    pending_todos, pending_src = _scan_todos(planning, "pending", parse_errors)
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
        assert len(output["adhoc_learnings"]) == 1
        adhoc = output["adhoc_learnings"][0]
        assert adhoc["subsystem"] == "auth"
        assert len(adhoc["learnings"]) == 2

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
