<purpose>
Execute discovered work with knowledge-aware planning, subagent execution, and knowledge consolidation.
</purpose>

<process>

<step name="parse_and_validate" priority="first">
Parse the work description from $ARGUMENTS:

```bash
if [ -z "$ARGUMENTS" ]; then
  echo "ERROR: Work description required"
  echo "Usage: /ms:adhoc <description>"
  echo "Example: /ms:adhoc Fix auth token not refreshing on 401"
  exit 1
fi

description="$ARGUMENTS"
```

Validate description is actionable (not vague like "fix stuff" or "make it work").

Verify active Mindsystem project:

```bash
if [ ! -f .planning/STATE.md ]; then
  echo "ERROR: No active Mindsystem project found (.planning/STATE.md missing)"
  echo ""
  echo "Options:"
  echo "- Initialize project: /ms:new-project"
  echo "- Capture as todo: /ms:add-todo [description]"
  exit 1
fi
```

Read STATE.md for project context (current phase, accumulated decisions, blockers).

**Ticket detection:** Check `task_tracker` in config.json. If configured and `$ARGUMENTS` matches the ticket ID pattern, lazy-load `~/.claude/mindsystem/references/{type}-cli.md` and follow its **Ticket Detection** process. If no tracker configured or no match, proceed with `$ARGUMENTS` as free-text.

```bash
TRACKER_TYPE=$(ms-tools config-get task_tracker.type)
TRACKER_CLI=$(ms-tools config-get task_tracker.cli)
```

**Todo detection:** If `$ARGUMENTS` matches a `.planning/todos/*.md` file path and the file exists, lazy-load `~/.claude/mindsystem/references/todo-file.md` and follow its **Todo Detection** process. Todo detection is independent of ticket detection — both can be inactive.
</step>

<step name="load_knowledge">
Read subsystems and match knowledge files to work description:

```bash
# Read subsystems from config
ms-tools config-get subsystems
```

Match keywords from work description against subsystem names. Read matching `.planning/knowledge/*.md` files (1-3 most relevant).

This knowledge informs both the exploration step (what to look for) and the plan (established patterns, pitfalls to avoid).
</step>

<step name="explore_codebase">
Spawn Explore agents with search focuses derived from work description + loaded knowledge.

Count: 1 for simple/focused work, 2-3 for work touching multiple areas.

Each agent receives:
- Specific search focus (e.g., "find auth token refresh logic", "find API client interceptors")
- Relevant knowledge context (patterns to look for, files known to be involved)
- Thoroughness: "medium" for most work, "very thorough" for unfamiliar areas
</step>

<step name="present_and_clarify">
Present exploration findings as a briefing with externalized assumptions, then cross the information asymmetry boundary with targeted questions.

**Part 1 — Briefing (always):**

Present a dense, specific summary:
- What changes and why (files, purpose)
- Claude's assumptions about expected behavior, scope boundaries, and approach — each marked with confidence: **high** / **medium** / **low** to focus user attention on uncertain areas
- Patterns and constraints from knowledge files and exploration

**Part 2 — AskUserQuestion:**

Governing principle: each question must save more context than it costs. A question that prevents a wrong assumption from reaching the executor saves an entire subagent context window.

- Q1 (always): Assumption validation — "Are these assumptions correct?" with options:
  - Looks right
  - Some corrections (let me clarify)
  - Let me reframe the task
- Additional questions (conditional): Only when exploration surfaced genuine behavioral ambiguity the user must resolve. Frame with implementation context discovered during exploration. Continue until scope is unambiguous — focused work may need one question; multi-area work may need several.

**What NOT to ask** (Claude determines these from exploration):
- Technical approach or patterns
- Error handling strategy
- Implementation details the user can't meaningfully influence
- Only ask about: user intent, expected behavior, scope boundaries

**Fast path:** All assumptions high-confidence + no ambiguity → collapse to single validation question.

**On corrections:** Absorb user feedback and proceed to planning. Do not re-present the full briefing.
</step>

<step name="select_and_load_skills">
**Select from all configured skills.**

```bash
DISCUSS_SKILLS=$(ms-tools config-get skills.discuss --default "[]")
DESIGN_SKILLS=$(ms-tools config-get skills.design --default "[]")
RESEARCH_SKILLS=$(ms-tools config-get skills.research --default "[]")
PLAN_SKILLS=$(ms-tools config-get skills.plan --default "[]")
```

Combine all arrays and deduplicate into a single list.

**If no skills configured across any phase:** Continue silently — adhoc is a fast path.

**If skills exist:** Analyze the task description and exploration findings against each unique skill. For each skill, assess whether it's relevant to the work at hand based on:
- Work description keywords and domain
- Subsystem(s) involved
- Types of files affected (from exploration step)

Present via AskUserQuestion with `multiSelect: true`:
- header: "Skills"
- question: "Which skills should inform this work?"
- Each unique skill as an option, append "(recommended)" to skills judged relevant
- Include "None — skip skill loading" option
- Free-text field for unlisted skills

**After selection:** Invoke selected skills via the Skill tool. Extract relevant implementation conventions for the adhoc planner — include as `<skill_context>` in the prompt sent to ms-adhoc-planner.
</step>

<step name="spawn_plan_writer">
Create per-execution subdirectory:

```bash
slug=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
exec_dir=".planning/adhoc/${slug}"
if [ -d "$exec_dir" ]; then
  echo "COLLISION: $exec_dir already exists from a previous adhoc execution"
  echo "Choose a more specific description or remove the existing directory"
  exit 1
fi
mkdir -p "$exec_dir"
```

Assemble context payload for ms-adhoc-planner:
- Work description
- Exploration findings (from Explore agents)
- Knowledge file contents (loaded in step 2)
- User decisions (from clarification step)
- STATE.md context (current phase, accumulated decisions)
- Subsystem list from config.json
- Output path: `${exec_dir}/${slug}-PLAN.md`
- Ticket context when detected (per loaded ticket reference)
- Todo context when detected (per loaded todo reference)

Spawn ms-adhoc-planner via Task tool. Receive completion report with plan path.
</step>

<step name="review_plan">
Read the generated plan at `${exec_dir}/${slug}-PLAN.md`.

Present a summary to the user:
- Number of Changes sections
- Key files affected
- Must-Haves checklist

**AskUserQuestion** with options:
- Approve and execute
- Request edits (let me describe)
- Abort

If edits requested, apply them directly to the plan file, then re-present and ask again. If aborted, clean up `${exec_dir}` and stop.
</step>

<step name="spawn_executor">
Record pre-execution HEAD for accurate diff scoping:

```bash
PRE_EXEC_HEAD=$(git rev-parse HEAD)
```

Spawn ms-executor via Task tool.

Provide in the prompt:
- Plan path: `${exec_dir}/${slug}-PLAN.md`
- SUMMARY output path: `${exec_dir}/${slug}-SUMMARY.md`
- Instruction to use phase-style SUMMARY format (with key-decisions, patterns-established, key-files, mock_hints frontmatter fields) for consolidator compatibility
- Commit scope: `"Use (${slug}) as commit scope for all task commits: {type}(${slug}): description"`
- Ticket commit instructions when detected (per loaded ticket reference)
- Todo commit instructions when detected (per loaded todo reference)

The executor reads the plan, executes tasks with atomic commits, creates SUMMARY.md, and returns completion report.
</step>

<step name="browser_verification">
Run browser verification prerequisites check:

```bash
ms-tools browser-check
```

**If exit 0 (READY):**

Ensure `${exec_dir}/${slug}-SUMMARY.md` is available (needed for journey derivation — may already be in context from executor report).

Read `~/.claude/mindsystem/references/browser-verification.md` and follow its sections in order:
1. **Auth Flow** — establish browser authentication
2. **Derive User Journeys** — transform SUMMARY into user journeys (single file: `${exec_dir}/${slug}-SUMMARY.md`)
3. **Spawn** — launch ms-browser-verifier with derived journeys, screenshots directory: `${exec_dir}/screenshots`
4. **Post-Verifier Handling** — route by report status

**If exit 1 (MISSING_DEPS):**

Parse output for missing items. Use AskUserQuestion:
- header: "Browser verification"
- question: "Browser verification prerequisites are missing. How to proceed?"
- options:
  - "Install missing dependencies" — follow install instructions from output
  - "Skip browser verification" — proceed to code_review

If user installs: re-run `ms-tools browser-check`.
If user skips: proceed to code_review.

**If exit 2 (SKIP):**

Proceed silently to code_review.
</step>

<step name="code_review">
Read code review agent from config:

```bash
CODE_REVIEW=$(ms-tools config-get code_review.adhoc)
[ -z "$CODE_REVIEW" ] && CODE_REVIEW=$(ms-tools config-get code_review.phase)
```

**If CODE_REVIEW = "skip":** Skip to generate_patch.

**If CODE_REVIEW = empty/null:** Use default: `CODE_REVIEW="ms-code-simplifier"`

**Otherwise:** Use CODE_REVIEW value directly as agent name.

1. Get modified files from executor's commits:
   ```bash
   CHANGED_FILES=$(git diff --name-only ${PRE_EXEC_HEAD}..HEAD | grep -E '\.(dart|ts|tsx|js|jsx|swift|kt|py|go|rs)$')
   ```

2. Spawn code review agent with adhoc scope.

3. If changes made: commit with message `refactor(adhoc): code review pass`.
</step>

<step name="generate_patch">
Generate a patch file capturing all adhoc changes:

```bash
ADHOC_COMMITS=$(git log --reverse --grep="(${slug})" --format="%H" ${PRE_EXEC_HEAD}..HEAD)
FIRST_COMMIT=$(echo "$ADHOC_COMMITS" | head -1)
LAST_COMMIT=$(echo "$ADHOC_COMMITS" | tail -1)
patch_file="${exec_dir}/${slug}-changes.patch"
if [ -n "$FIRST_COMMIT" ]; then
  ms-tools generate-adhoc-patch "$FIRST_COMMIT" "$patch_file" --end "$LAST_COMMIT"
fi
```

If no adhoc commits found or patch generation reports no changes, skip silently.
</step>

<step name="consolidate_knowledge">
Spawn ms-consolidator via Task tool.

Provide:
- Phase directory: `${exec_dir}` (the per-execution subdirectory)
- Phase identifier: "adhoc"

The consolidator reads `${slug}-SUMMARY.md`, extracts knowledge (key-decisions, patterns-established, key-files), updates `.planning/knowledge/*.md` files, and deletes `${slug}-PLAN.md`.
</step>

<step name="cleanup_and_report">
**Finalize ticket (when detected):** Follow the **Finalization**, **Commit Message Suffix**, and **Report Additions** sections from the loaded ticket reference.

**Finalize todo (when detected):** Follow the **Finalization**, **Commit Message Suffix**, and **Report Additions** sections from the loaded todo reference.

**Update STATE.md** "Recent Adhoc Work" section:
- Find or create "### Recent Adhoc Work" under "## Accumulated Context"
- Add entry at top: `- [YYYY-MM-DD]: [description] ({exec_dir}/${slug}-SUMMARY.md)`
- Keep last 5 entries (remove older ones from list)

**Update state and commit:**
```bash
# Use the slug (sanitized directory name), not the raw description or ticket IDs
ms-tools set-last-command "ms:adhoc ${slug}"
git add .planning/knowledge/*.md "${exec_dir}/${slug}-SUMMARY.md" .planning/STATE.md
# Only include patch if it was generated
[ -f "${exec_dir}/${slug}-changes.patch" ] && git add "${exec_dir}/${slug}-changes.patch"
git commit -m "$(cat <<EOF
docs(adhoc): consolidate knowledge from $description

Knowledge files updated, SUMMARY preserved.
EOF
)"
```

**Report completion:**
```
Adhoc work complete: [description]

**Commit:** [hash]
**Files modified:** [count]
**Knowledge updated:** [list of knowledge files]

Artifacts:
- Summary: {exec_dir}/${slug}-SUMMARY.md
- Patch: {exec_dir}/${slug}-changes.patch
- Knowledge: .planning/knowledge/[subsystem].md
```

```
---

Check `/ms:progress` to see project status and next steps.
```
</step>

</process>
