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

New milestones use slug-based directories (e.g., `milestones/mvp/`, `milestones/push-notifications/`). Old v-prefixed directories from previous format are valid and handled.

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
   - Derive slugs from names: lowercase, hyphenated (e.g., "Demo Release" → "demo-release"). Claude proposes, user confirms

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

<step name="fix_phase_dirs">
**Only if Phase Directory Naming failed or warned.**

1. Create any missing phase directories:

```bash
ms-tools create-phase-dirs
```

2. For non-canonical directories (reported as FAIL), rename using `git mv`:

Parse each non-canonical suggestion from the doctor check output (format: `{old} → git mv .planning/phases/{old} .planning/phases/{canonical}`) and execute the `git mv`.

Commit:

```bash
git add .planning/phases/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): fix phase directory naming

Created missing and renamed non-canonical phase directories.
EOF
)"
```
</step>

<step name="fix_knowledge">
**Only if Knowledge Files failed.**

### 1. Detect knowledge source

Run in main context before spawning agent:

```bash
SUMMARIES=$(ls .planning/milestones/*/PHASE-SUMMARIES.md .planning/phases/*/*-SUMMARY.md 2>/dev/null | wc -l | tr -d ' ')
HAS_CODEBASE_DOCS=$([ -d .planning/codebase ] && echo "yes" || echo "no")
HAS_PROJECT=$([ -f .planning/PROJECT.md ] && echo "yes" || echo "no")
```

If `SUMMARIES > 0`: **artifact mode**. If `SUMMARIES == 0`: **source code mode**.

### 2. Spawn subagent

Spawn a `general-purpose` subagent (Task tool) with the following structured prompt. Inject detected mode, subsystem list from config.json, and detection results (SUMMARIES, HAS_CODEBASE_DOCS, HAS_PROJECT) into the prompt.

---

**Prompt content for subagent:**

> **Task:** Generate `.planning/knowledge/{subsystem}.md` for each subsystem listed below.
>
> **Subsystems:** {inject list from config.json}
>
> **Knowledge template:** Read `~/.claude/mindsystem/templates/knowledge.md` for format reference.
>
> **Mode: {artifact | source code}**
>
> **If artifact mode:** Read all PHASE-SUMMARIES.md from `milestones/*/PHASE-SUMMARIES.md` and any remaining `*-SUMMARY.md` in `phases/`. {If HAS_CODEBASE_DOCS=yes: "Also read `.planning/codebase/ARCHITECTURE.md`, `STACK.md`, `STRUCTURE.md` for structural context."} {If HAS_PROJECT=yes: "Read `.planning/PROJECT.md` for product context."}
>
> **If source code mode:** No pipeline artifacts exist. {If HAS_CODEBASE_DOCS=yes: "Read `.planning/codebase/ARCHITECTURE.md`, `STACK.md`, `STRUCTURE.md` first for orientation, then dive into source code per subsystem."} {If HAS_CODEBASE_DOCS=no: "Explore from package manifests (package.json, pubspec.yaml, Cargo.toml, etc.) and directory structure to understand the codebase, then analyze source code per subsystem."} {If HAS_PROJECT=yes: "Read `.planning/PROJECT.md` for product context."}
>
> **Extraction guide — what to extract per subsystem:**
>
> | Source Signal | Target Knowledge Section |
> |--------------|------------------------|
> | Library/framework choices, version constraints | Decisions |
> | Component structure, data flow, API contracts | Architecture |
> | UI patterns, design tokens, interaction behaviors | Design |
> | Error handling patterns, edge cases, workarounds | Pitfalls |
> | Main modules, entry points, config files | Key Files |
>
> **Critical rules:**
> - Extract knowledge, not descriptions. "Has login endpoint" is a description. "POST /auth/login with bcrypt + JWT httpOnly cookie" is architecture knowledge.
> - Preserve rationale when visible in code comments or config. Do not fabricate reasons.
> - Do not fabricate specific numbers (limits, thresholds, counts) — read from source or omit.
> - Omit empty sections. No Design section if subsystem has no UI.
> - Edit to reflect current state — use `Edit` for existing knowledge files (targeted changes), `Write` only for new files.
> - Cross-reference between subsystems where relevant: "(see api subsystem)".
> - Decisions table: 5-10 words per cell. Source column: `"existing"` for source code mode, artifact reference for artifact mode.
> - Key files must reference actual paths verified to exist.
> - `mkdir -p .planning/knowledge/` before writing.
> - No commits.

---

### 3. Verify and commit

After subagent completes, verify files exist:

```bash
ls .planning/knowledge/*.md
```

Commit (use detected mode in message):

```bash
git add .planning/knowledge/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): generate knowledge files

Created per-subsystem knowledge files from {phase summaries|source code analysis}.
EOF
)"
```

Replace `{phase summaries|source code analysis}` with the appropriate phrase based on detected mode.
</step>

<step name="fix_roadmap_format">
**Only if Roadmap Format failed.**

Fix missing or malformed pre-work flags (Discuss/Design/Research) in incomplete phases.

1. Read `.planning/ROADMAP.md` and `.planning/PROJECT.md`.

2. For each incomplete phase with flag issues (from doctor-scan output), determine the correct pre-work flags by applying roadmapper principles:

   **Discussion** — Default Likely. Unlikely only when ALL of: fully mechanical (zero design decisions), zero ambiguity in scope or approach (version bump, rename-only refactor, config-only change, pure deletion/cleanup). When Likely, enumerate 2-4 phase-specific assumptions or open questions in the parenthetical reason.

   **Design** — Likely when ANY of: significant new UI work, novel interactions, visual success criteria, cross-platform UI. Unlikely when ALL of: no UI work, backend/API only, infrastructure/testing/deployment, exclusively established UI patterns.

   **Research** — Likely when ANY of: external APIs/services, new libraries/frameworks, unresolved architectural decisions, unclear technical approach. Unlikely when ALL of: established internal patterns, CRUD with known stack, well-documented conventions.

   Use the phase's Goal, Success Criteria, Requirements, and project context from PROJECT.md to make these assessments.

3. Present proposed flags per phase:

   ```
   ## Roadmap Format Fixes

   ### Phase 8: Week Navigation
   Current: Only **Research** flag present
   Proposed:
     **Discuss**: Likely (assumes carryover model unclear, week boundary behavior unspecified)
     **Discuss topics**: carryover rules, week start day preference
     **Design**: Likely (new navigation UI, week transition flow)
     **Design focus**: week picker, carryover modal
     **Research**: Likely (carryover) ← already present, keeping as-is

   ### Phase 9: Visual Polish
   Current: Only **Research** flag present
   Proposed:
     **Discuss**: Likely (JARVIS aesthetic interpretation ambiguous, typography priorities unclear)
     **Discuss topics**: aesthetic reference points, typography hierarchy
     **Design**: Likely (significant visual redesign)
     **Design focus**: color palette, component styling, typography system
     **Research**: Unlikely (established patterns) ← updating from current
   ```

4. Use AskUserQuestion:
   - header: "Roadmap format fixes"
   - question: "These pre-work flags were derived from phase goals and project context. Apply?"
   - options:
     - "Apply all" — update ROADMAP.md with all proposed flags
     - "Review each" — iterate per phase
     - "Skip" — leave as-is

5. Apply accepted changes using Edit tool. Insert flags in the standard order within each phase section:
   - After `**Success Criteria**` block (and any existing plan lines)
   - Before `Plans:` or next phase header
   - Standard format: `**Flag**: Likely/Unlikely (reason)` with detail lines for Likely flags
   - Preserve any existing valid flags — only add missing or fix malformed ones

6. Commit:

```bash
git add .planning/ROADMAP.md
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): fix roadmap pre-work flags

Added missing Discuss/Design/Research flags to incomplete phases.
EOF
)"
```
</step>

</process>
