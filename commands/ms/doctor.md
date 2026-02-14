---
name: ms:doctor
description: Health check and fix project configuration
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Run health checks on project configuration. Detect and fix configuration issues.

V1 check: subsystem vocabulary setup and validation. Ensures `.planning/config.json` has a canonical `subsystems` array and all artifacts use values from it.

Idempotent — safe to run repeatedly.
</objective>

<context>
@.planning/config.json
</context>

<process>

<step name="check_planning_dir">
```bash
[ -d .planning ] && echo "EXISTS" || echo "MISSING"
```

If MISSING:

```
No .planning/ directory found.

Run `/ms:new-project` to initialize this project.
```

Exit.
</step>

<step name="ensure_config">
```bash
[ -f .planning/config.json ] && echo "EXISTS" || echo "MISSING"
```

If MISSING, create from template structure:

```json
{
  "subsystems": [],
  "code_review": {
    "adhoc": null,
    "phase": null,
    "milestone": null
  }
}
```

Write to `.planning/config.json`. Log: "Created config.json with empty subsystems."

Proceed to next step.
</step>

<step name="read_current_subsystems">
```bash
jq -r '.subsystems // [] | length' .planning/config.json
```

- If 0 → **State A**: no subsystems configured. Go to `audit_existing_usage`.
- If >0 → **State B**: subsystems exist. Go to `validate_vocabulary`.
</step>

<step name="audit_existing_usage">
**State A only.** Scan all artifact types for existing free-form `subsystem:` values.

```bash
echo "=== Phase SUMMARYs ==="
for f in .planning/phases/*/*-SUMMARY.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$val"
done

echo "=== Adhoc SUMMARYs ==="
for f in .planning/adhoc/*-SUMMARY.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$val"
done

echo "=== Debug docs ==="
for f in .planning/debug/*.md .planning/debug/resolved/*.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$val"
done

echo "=== Todos ==="
for f in .planning/todos/pending/*.md .planning/todos/done/*.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$val"
done
```

Collect all unique values found. Note count of artifacts scanned and values found.
</step>

<step name="derive_and_confirm">
**State A only.** Read `.planning/PROJECT.md` and `.planning/ROADMAP.md`.

Derive 5-12 canonical subsystem identifiers from:

1. Unique values found in `audit_existing_usage`
2. Project domain from PROJECT.md
3. Phase structure from ROADMAP.md

Rules:
- Lowercase, single-word or hyphenated (e.g., "auth", "real-time", "ui")
- Merge synonyms into one canonical value (pick shortest/most common)
- Cover all existing usage plus obvious gaps
- Include infrastructure-level subsystems if relevant (api, database, infra, testing)

Present the proposed list with merge mappings (e.g., "authentication" -> "auth").

Use AskUserQuestion:
- header: "Subsystems"
- question: "These subsystems were derived from your project. Look good?"
- options:
  - "Looks good" — accept and apply
  - "Add/remove some" — iterate on the list
  - "Start over" — re-derive from scratch

After confirmation:

1. Update `config.json` — set `subsystems` array as first field
2. If existing artifacts had free-form values, standardize each `subsystem:` field to the canonical value using the Edit tool (only modify the `subsystem:` line, never body content)
3. Commit all changes:

```bash
git add .planning/config.json
git add .planning/phases/*/*-SUMMARY.md 2>/dev/null
git add .planning/adhoc/*-SUMMARY.md 2>/dev/null
git add .planning/debug/*.md 2>/dev/null
git add .planning/debug/resolved/*.md 2>/dev/null
git add .planning/todos/pending/*.md 2>/dev/null
git add .planning/todos/done/*.md 2>/dev/null
```

```bash
git commit -m "$(cat <<'EOF'
chore: initialize subsystem vocabulary

Added subsystems array to config.json and standardized existing artifact values.
EOF
)"
```
</step>

<step name="validate_vocabulary">
**State B only.** Read canonical list from config.json:

```bash
jq -r '.subsystems[]' .planning/config.json
```

Scan all artifacts for `subsystem:` values. Extract from YAML frontmatter:

```bash
echo "=== Phase SUMMARYs ==="
for f in .planning/phases/*/*-SUMMARY.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$f: $val"
done

echo "=== Adhoc SUMMARYs ==="
for f in .planning/adhoc/*-SUMMARY.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$f: $val"
done

echo "=== Debug docs ==="
for f in .planning/debug/*.md .planning/debug/resolved/*.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$f: $val"
done

echo "=== Todos ==="
for f in .planning/todos/pending/*.md .planning/todos/done/*.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  [ -n "$val" ] && echo "$f: $val"
done
```

Classify each artifact's `subsystem:` value:
- **OK** — value is in canonical list
- **MISMATCH** — value exists but not in canonical list
- **MISSING** — no `subsystem:` field found

Display results grouped by status. If all OK:

```
## Subsystem Vocabulary

PASS — all N artifacts use canonical subsystem values.
```

Go to `report`.

If MISMATCH or MISSING found, use AskUserQuestion:
- header: "Fix issues"
- question: "Found N issues (X mismatches, Y missing). How to proceed?"
- options:
  - "Fix all" — apply best-match canonical values to all issues
  - "Review each" — present each issue individually for decision
  - "Skip" — leave as-is

For fixes:
- MISMATCH: propose closest canonical value (fuzzy match on prefix/synonym)
- MISSING: propose based on artifact content/path context

Apply fixes using Edit tool. Commit:

```bash
git add .planning/phases/*/*-SUMMARY.md 2>/dev/null
git add .planning/adhoc/*-SUMMARY.md 2>/dev/null
git add .planning/debug/*.md 2>/dev/null
git add .planning/debug/resolved/*.md 2>/dev/null
git add .planning/todos/pending/*.md 2>/dev/null
git add .planning/todos/done/*.md 2>/dev/null
```

```bash
git commit -m "$(cat <<'EOF'
chore: fix subsystem vocabulary mismatches

Standardized artifact subsystem values to canonical vocabulary.
EOF
)"
```
</step>

<step name="report">
Final summary:

```
## Doctor Report

| Check                  | Result      | Details                    |
|------------------------|-------------|----------------------------|
| Subsystem vocabulary   | PASS / INIT | N artifacts, M subsystems  |

All checks passed.
```

- **PASS**: subsystems were already configured and all artifacts validated
- **INIT**: subsystems were initialized during this run
- Include artifact count (how many scanned) and subsystem count
</step>

</process>

<success_criteria>
- [ ] State A: config.json updated, existing artifacts standardized to canonical values, changes committed
- [ ] State B issues: offers fix/review/skip, applies fixes, commits
- [ ] Final report displayed with check name, result, and artifact/subsystem counts
- [ ] State A: derives canonical list from audit + project context, confirms with user before applying
- [ ] State B: all artifacts scanned and classified; reports PASS if all OK
</success_criteria>
