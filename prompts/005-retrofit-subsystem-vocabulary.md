<objective>

Retrofit this existing Mindsystem project with the new subsystem vocabulary system.

Mindsystem now uses a controlled `subsystems` array in `config.json` to standardize categorization across all artifacts (SUMMARY.md, debug docs, adhoc summaries). Existing projects have free-form subsystem values that may be inconsistent ("auth" vs "authentication" vs "auth-system") — this prompt standardizes everything.

This is a one-time migration. After completion, all future artifacts will use the controlled vocabulary automatically.

</objective>

<context>

Read these files to understand the project:

@.planning/PROJECT.md
@.planning/config.json
@.planning/STATE.md
@.planning/ROADMAP.md

</context>

<process>

## Step 1: Audit existing subsystem usage

Scan all existing SUMMARY.md files for current subsystem values:

```bash
for f in .planning/phases/*/*-SUMMARY.md; do
  echo "=== $f ==="
  sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" 2>/dev/null
done
```

Also check adhoc summaries and debug docs:

```bash
for f in .planning/adhoc/*-SUMMARY.md; do
  [ -f "$f" ] && echo "=== $f ===" && sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" 2>/dev/null
done

for f in .planning/debug/*.md .planning/debug/resolved/*.md; do
  [ -f "$f" ] && echo "=== $f ===" && sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" 2>/dev/null
done
```

Collect all unique subsystem values found. Note any inconsistencies (e.g., "auth" and "authentication" referring to the same area).

## Step 2: Derive the canonical subsystems list

Based on:
1. The unique subsystem values found in Step 1
2. The project's domain from PROJECT.md
3. The phase structure from ROADMAP.md

Derive 5-12 canonical subsystem identifiers. Rules:
- Lowercase, single-word or hyphenated (e.g., "auth", "real-time", "ui")
- Merge synonyms into one canonical value (pick the shortest/most common)
- Cover all existing usage plus any obvious gaps
- Include infrastructure-level subsystems if the project has them (api, database, infra, testing)

Present the proposed list and the merge mapping (e.g., "authentication" → "auth", "auth-system" → "auth").

## Step 3: Update config.json

Read `.planning/config.json`. Add the `subsystems` array as the FIRST field (before `depth`):

```bash
cat .planning/config.json
```

Use the Edit tool to add the subsystems array. The result should look like:

```json
{
  "subsystems": ["auth", "api", "database", "ui", ...],
  "depth": "standard",
  ...
}
```

## Step 4: Standardize existing SUMMARY.md frontmatter

For each phase SUMMARY.md that has a `subsystem:` field:
- Replace the current value with the canonical value from Step 2
- If the value was already canonical, leave it unchanged

```bash
# List all summaries with their current subsystem
for f in .planning/phases/*/*-SUMMARY.md; do
  current=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  echo "$f -> $current"
done
```

Use the Edit tool on each file that needs updating. Only change the `subsystem:` line — do not modify any other content.

## Step 5: Standardize adhoc summaries (if any exist)

For each adhoc SUMMARY.md in `.planning/adhoc/`:
- If it has a `subsystem:` field, standardize to canonical value
- If it's missing `subsystem:`, `tags:`, and `learnings:` fields, add them after `related_phase:`

New fields to add (if missing):
```yaml
subsystem: [select canonical value based on work described]
tags: [derive 2-4 keywords from the summary content]
learnings:
  - [only if the summary reveals a non-obvious insight, otherwise omit or leave empty]
```

## Step 6: Standardize debug docs (if any exist)

For each debug doc in `.planning/debug/` and `.planning/debug/resolved/`:
- If missing the new frontmatter fields, add them after `updated:`

New fields to add (if missing):
```yaml
subsystem: [select canonical value based on the bug's domain]
tags: []
symptoms: []
root_cause: [extract from Resolution body if resolved]
resolution: [extract from Resolution body if resolved]
phase: [infer from file context or set "none"]
```

- If the doc is resolved and has a Resolution section, populate `root_cause` and `resolution` frontmatter from the body content (concise one-liners)
- Add `## Prevention` section after `## Resolution` if missing:
```markdown
## Prevention
<!-- OVERWRITE - populated during archive_session -->

prevention: [derive from resolution if obvious, otherwise leave empty]
```

## Step 7: Verify consistency

Run final verification:

```bash
# All subsystem values should now be in config.json
SUBSYSTEMS=$(jq -r '.subsystems[]' .planning/config.json)

echo "=== Config subsystems ==="
echo "$SUBSYSTEMS"

echo ""
echo "=== Phase summaries ==="
for f in .planning/phases/*/*-SUMMARY.md; do
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  if echo "$SUBSYSTEMS" | grep -qx "$val"; then
    echo "OK: $f -> $val"
  else
    echo "MISMATCH: $f -> $val (not in config.json)"
  fi
done

echo ""
echo "=== Adhoc summaries ==="
for f in .planning/adhoc/*-SUMMARY.md; do
  [ -f "$f" ] || continue
  val=$(sed -n '/^---$/,/^---$/p' "$f" | grep "^subsystem:" | sed 's/subsystem: *//')
  if [ -z "$val" ]; then
    echo "MISSING: $f (no subsystem field)"
  elif echo "$SUBSYSTEMS" | grep -qx "$val"; then
    echo "OK: $f -> $val"
  else
    echo "MISMATCH: $f -> $val (not in config.json)"
  fi
done
```

Fix any MISMATCH or MISSING entries before proceeding.

## Step 8: Commit

```bash
git add .planning/config.json
git add .planning/phases/*/*-SUMMARY.md
git add .planning/adhoc/*-SUMMARY.md 2>/dev/null
git add .planning/debug/*.md 2>/dev/null
git add .planning/debug/resolved/*.md 2>/dev/null

git commit -m "$(cat <<'EOF'
chore: retrofit subsystem vocabulary across project artifacts

- Added subsystems array to config.json
- Standardized subsystem values across all SUMMARY.md files
- Enriched adhoc summaries with subsystem/tags/learnings fields
- Enriched debug docs with subsystem/tags/symptoms/root_cause/resolution/phase fields
EOF
)"
```

</process>

<constraints>

- Only modify frontmatter fields — never change body content of summaries
- When adding missing fields, insert them at the correct position per template spec
- If config.json already has a `subsystems` array, extend it rather than replacing
- If no adhoc summaries or debug docs exist, skip those steps silently
- Use Edit tool for file modifications, not sed/awk via Bash

</constraints>

<verification>

Before declaring complete:

- [ ] `jq '.subsystems' .planning/config.json` returns a non-empty array
- [ ] `grep -r "^subsystem:" .planning/phases/ | sort -u` shows only values present in config.json
- [ ] No MISMATCH entries in Step 7 verification output
- [ ] All changes committed to git
- [ ] Existing SUMMARY.md body content is unchanged (only frontmatter modified)

</verification>

<success_criteria>

- config.json has `subsystems` array as first field with 5-12 canonical values
- All existing phase SUMMARY.md files use canonical subsystem values
- Adhoc summaries enriched with subsystem, tags, learnings (if adhoc dir exists)
- Debug docs enriched with 6 new frontmatter fields + Prevention section (if debug dir exists)
- Zero subsystem mismatches across all artifacts
- Single atomic commit documenting the retrofit

</success_criteria>
