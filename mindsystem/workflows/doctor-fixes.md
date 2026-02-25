<purpose>
Apply fixes for doctor health check failures. Each step targets one check category,
runs only if that check failed, and commits atomically.
</purpose>

<process>

<step name="fix_subsystems">
**Only if Subsystem Vocabulary failed.**

If subsystems array is empty (State A):

1. Scan all artifacts for existing values:

```bash
ms-tools scan-artifact-subsystems --values-only
```

2. Read `.planning/PROJECT.md` and `.planning/ROADMAP.md`.

3. Derive 5-12 canonical subsystem identifiers from:
   - Unique values found in artifacts
   - Project domain from PROJECT.md
   - Phase structure from ROADMAP.md

   Rules:
   - Lowercase, single-word or hyphenated (e.g., "auth", "real-time", "ui")
   - Merge synonyms into one canonical value (pick shortest/most common)
   - Cover all existing usage plus obvious gaps
   - Include infrastructure-level subsystems if relevant (api, database, infra, testing)

4. Present the proposed list with merge mappings (e.g., "authentication" -> "auth").

5. Use AskUserQuestion:
   - header: "Subsystems"
   - question: "These subsystems were derived from your project. Look good?"
   - options:
     - "Looks good" — accept and apply
     - "Add/remove some" — iterate on the list
     - "Start over" — re-derive from scratch

6. After confirmation: update `config.json` (subsystems as first field), standardize existing artifact `subsystem:` fields using Edit tool.

If subsystems exist but artifacts have mismatches (State B):

1. Classify each artifact as OK/MISMATCH/MISSING.
2. For MISMATCH: propose closest canonical value.
3. For MISSING: propose based on artifact content/path.
4. Apply fixes using Edit tool.

Commit:

```bash
git add .planning/config.json
git add .planning/phases/*/*-SUMMARY.md 2>/dev/null
git add .planning/adhoc/*-SUMMARY.md 2>/dev/null
git add .planning/debug/*.md 2>/dev/null
git add .planning/debug/resolved/*.md 2>/dev/null
git add .planning/todos/*.md 2>/dev/null
git add .planning/todos/done/*.md 2>/dev/null
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): fix subsystem vocabulary

Standardized subsystem configuration and artifact values.
EOF
)"
```
</step>

<step name="fix_milestone_dirs">
**Only if Milestone Directory Structure failed.**

For each flat file like `milestones/v0.1-ROADMAP.md`:

1. Extract version prefix (e.g., `v0.1`).
2. Create directory if it doesn't exist: `mkdir -p .planning/milestones/v0.1`
3. `git mv` the file, stripping the version prefix from the filename:
   `git mv .planning/milestones/v0.1-ROADMAP.md .planning/milestones/v0.1/ROADMAP.md`

**Note:** New milestones use slug-based directories (e.g., `milestones/mvp/`, `milestones/push-notifications/`). Old v-prefixed directories from previous format are valid and handled.

Commit:

```bash
git add .planning/milestones/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): restructure milestone directories

Moved flat milestone files into versioned directories.
EOF
)"
```
</step>

<step name="fix_milestone_naming">
**Only if Milestone Naming Convention failed.**

1. **Build mapping** — run `ms-tools scan-milestone-naming`, parse JSON output.

2. **Resolve slugs** — For each versioned dir, match to MILESTONES.md name mapping:
   - Standard dirs: version matches directly (v0.1 → "MVP" → slug "mvp")
   - Nested dirs: match sub-directory name to the milestone name in MILESTONES.md (v2.0.0/quests → "Quests Feature" → slug "quests-feature")
   - Derive short slugs from names (Claude proposes, user confirms)

3. **Present mapping** to user with AskUserQuestion:

   ```
   | Current Directory       | Milestone Name       | Proposed Slug    |
   |-------------------------|----------------------|------------------|
   | v0.1/                   | MVP                  | mvp              |
   | v0.2/                   | Infrastructure       | infrastructure   |
   | (active)                | Demo Release         | demo-release     |
   ```

   Options: "Looks good" / "Edit slugs" / "Skip"

4. **Rename directories:**
   - Standard: `git mv .planning/milestones/v0.1 .planning/milestones/mvp`
   - Nested: `git mv .planning/milestones/v2.0.0/quests .planning/milestones/quests-feature` for each sub-dir, then `rmdir .planning/milestones/v2.0.0` to remove empty parent

5. **Update archived milestone files** (inside each renamed dir):
   - `PHASE-SUMMARIES.md`: `# Phase Summaries: v0.1` → `# Phase Summaries: MVP`
   - `ROADMAP.md`: `# Milestone v0.1: Name` → `# Milestone: Name`
   - `REQUIREMENTS.md`: `# Requirements Archive: v0.1 Name` → `# Requirements Archive: Name`
   - `MILESTONE-AUDIT.md`: YAML `milestone: v0.1` → `milestone: mvp` (use slug)
   - `CONTEXT.md`: `# Milestone Context: v0.1 Name` → `# Milestone Context: Name`

6. **Update MILESTONES.md:**
   - Strip version prefix from headers: `## v0.1 MVP (Shipped:...)` → `## MVP (Shipped:...)`
   - Preserve all other content (git ranges, stats, accomplishments)

7. **Update active .planning files:**
   - `PROJECT.md`: Replace `— v0.1` with `— MVP` in validated requirements, strip version from `## Current Milestone:` header, update `Shipped v0.2 with...` → `Shipped Infrastructure with...`
   - `STATE.md`: Replace version refs with names (`v0.3 Demo Release` → `Demo Release`)
   - `ROADMAP.md`: Strip version from `**Milestone:** v0.3 Demo Release` → `**Milestone:** Demo Release`
   - `MILESTONE-CONTEXT.md`: Strip version from header
   - `REQUIREMENTS.md`: Strip version from `**Milestone:**` line. For deferred sections (`### v0.4 — On-Device Hardening`), use AskUserQuestion to confirm replacement names or keep description-only format (`### On-Device Hardening (deferred)`)

8. **Rules:**
   - Do NOT modify git range references (`**Git range:** feat(01-01) → ...`)
   - Do NOT modify git commit messages quoted in MILESTONES.md
   - Preserve shipped dates, stats, phase ranges
   - Use Edit tool for targeted replacements (not bulk find-replace)

9. **Commit:**

```bash
git add .planning/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): migrate milestone naming from versions to slugs

Renamed milestone directories from version-based (v0.1/, v2.0.0/) to
name-based slugs (mvp/, quests-feature/). Updated all planning file references.
EOF
)"
```
</step>

<step name="fix_phase_archival">
**Only if Phase Archival failed.**

Parse MILESTONES.md for completed milestones and their phase ranges (`**Phases completed:** X-Y`).

For each completed milestone with orphaned phases in `.planning/phases/`:

1. Determine the version and phase range from MILESTONES.md.
2. Ensure the milestone directory exists: `mkdir -p .planning/milestones/{slug}`
3. Run the archive script:

```bash
ms-tools archive-milestone-phases <start> <end> <slug>
```

This simultaneously:
- Consolidates PHASE-SUMMARIES.md (fixes Phase Summaries check)
- Deletes raw artifacts (CONTEXT, DESIGN, RESEARCH, SUMMARY, UAT, VERIFICATION)
- Moves phase directories to milestone archive

**If MILESTONES.md doesn't have parseable phase ranges:** Use AskUserQuestion to ask the user for the phase range for each milestone.

After archive completes, clean up leftover PLAN files in archived phases (fixes PLAN Cleanup check):

```bash
find .planning/milestones/*/phases/ -name "*-PLAN.md" -delete 2>/dev/null
```

Commit:

```bash
git add .planning/phases/ .planning/milestones/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): archive completed milestone phases

Consolidated summaries, deleted raw artifacts, moved phase directories.
EOF
)"
```
</step>

<step name="fix_plan_cleanup">
**Only if PLAN Cleanup failed AND fix_phase_archival did not already handle it.**

Delete leftover PLAN files in completed phase directories:

```bash
find .planning/milestones/*/phases/ -name "*-PLAN.md" -delete 2>/dev/null
```

For any leftover PLANs in `phases/` belonging to completed milestones (identified by the scan), delete those too.

Commit:

```bash
git add .planning/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): clean up leftover PLAN files

Removed PLAN files from completed phase directories.
EOF
)"
```
</step>

<step name="fix_knowledge">
**Only if Knowledge Files failed.**

Spawn a `general-purpose` subagent (Task tool) to generate knowledge files retroactively. Provide the subagent with:

- Subsystem vocabulary from config.json
- Instructions to read all PHASE-SUMMARIES.md from `milestones/*/PHASE-SUMMARIES.md` AND any remaining SUMMARY files in `phases/`
- The knowledge template at `~/.claude/mindsystem/templates/knowledge.md`
- Instructions to read any existing knowledge files and merge (rewrite semantics — current state, not append)
- Instructions to create `.planning/knowledge/` directory if missing
- Instructions to write `.planning/knowledge/{subsystem}.md` for each missing subsystem

After subagent completes, verify files exist:

```bash
ls .planning/knowledge/*.md
```

Commit:

```bash
git add .planning/knowledge/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): generate knowledge files

Created per-subsystem knowledge files from phase summaries.
EOF
)"
```
</step>

</process>
