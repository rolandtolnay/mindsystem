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
- Additional questions (conditional): Only when exploration surfaced genuine behavioral ambiguity the user must resolve. Frame with implementation context discovered during exploration. Typically 1-2 for focused work, 3-4 for multi-area work.

**What NOT to ask** (Claude determines these from exploration):
- Technical approach or patterns
- Error handling strategy
- Implementation details the user can't meaningfully influence
- Only ask about: user intent, expected behavior, scope boundaries

**Fast path:** All assumptions high-confidence + no ambiguity → collapse to single validation question.

**On corrections:** Absorb user feedback and proceed to planning. Do not re-present the full briefing.
</step>

<step name="spawn_plan_writer">
Create per-execution subdirectory:

```bash
timestamp=$(date "+%Y-%m-%d")
slug=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
exec_dir=".planning/adhoc/${timestamp}-${slug}"
mkdir -p "$exec_dir"
```

Assemble context payload for ms-adhoc-planner:
- Work description
- Exploration findings (from Explore agents)
- Knowledge file contents (loaded in step 2)
- User decisions (from clarification step)
- STATE.md context (current phase, accumulated decisions)
- Subsystem list from config.json
- Output path: `${exec_dir}/adhoc-01-PLAN.md`
- Ticket context when detected (per loaded ticket reference)
- Todo context when detected (per loaded todo reference)

Spawn ms-adhoc-planner via Task tool. Receive completion report with plan path.
</step>

<step name="review_plan">
Read the generated plan at `${exec_dir}/adhoc-01-PLAN.md`.

Present a summary to the user:
- Number of Changes sections
- Key files affected
- Must-Haves checklist

Allow the user to approve, request edits, or abort. If edits requested, apply them directly to the plan file.
</step>

<step name="spawn_executor">
Spawn ms-executor via Task tool.

Provide in the prompt:
- Plan path: `${exec_dir}/adhoc-01-PLAN.md`
- SUMMARY output path: `${exec_dir}/adhoc-01-SUMMARY.md`
- Instruction to use phase-style SUMMARY format (with key-decisions, patterns-established, key-files, mock_hints frontmatter fields) for consolidator compatibility
- Ticket commit instructions when detected (per loaded ticket reference)
- Todo commit instructions when detected (per loaded todo reference)

The executor reads the plan, executes tasks with atomic commits, creates SUMMARY.md, and returns completion report.
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
   ADHOC_COMMITS=$(git log --oneline --grep="(adhoc-" --format="%H")
   CHANGED_FILES=$(git diff --name-only $(echo "$ADHOC_COMMITS" | tail -1)^..HEAD | grep -E '\.(dart|ts|tsx|js|jsx|swift|kt|py|go|rs)$')
   ```

2. Spawn code review agent with adhoc scope.

3. If changes made: commit with message `refactor(adhoc): code review pass`.
</step>

<step name="generate_patch">
Generate a patch file capturing all adhoc changes:

```bash
ADHOC_COMMITS=$(git log --oneline --grep="(adhoc-" --format="%H")
FIRST_COMMIT=$(echo "$ADHOC_COMMITS" | tail -1)
LAST_COMMIT=$(echo "$ADHOC_COMMITS" | head -1)
patch_file="${exec_dir}/adhoc-01-changes.patch"
ms-tools generate-adhoc-patch "$FIRST_COMMIT" "$patch_file" --end "$LAST_COMMIT"
```

If no adhoc commits found or patch generation reports no changes, skip silently.
</step>

<step name="consolidate_knowledge">
Spawn ms-consolidator via Task tool.

Provide:
- Phase directory: `${exec_dir}` (the per-execution subdirectory)
- Phase identifier: "adhoc"

The consolidator reads `adhoc-01-SUMMARY.md`, extracts knowledge (key-decisions, patterns-established, key-files), updates `.planning/knowledge/*.md` files, and deletes `adhoc-01-PLAN.md`.
</step>

<step name="cleanup_and_report">
**Finalize ticket (when detected):** Follow the **Finalization**, **Commit Message Suffix**, and **Report Additions** sections from the loaded ticket reference.

**Finalize todo (when detected):** Follow the **Finalization**, **Commit Message Suffix**, and **Report Additions** sections from the loaded todo reference.

**Commit knowledge updates:**
```bash
git add .planning/knowledge/*.md "${exec_dir}/adhoc-01-SUMMARY.md" .planning/STATE.md
# Only include patch if it was generated
[ -f "${exec_dir}/adhoc-01-changes.patch" ] && git add "${exec_dir}/adhoc-01-changes.patch"
git commit -m "$(cat <<EOF
docs(adhoc): consolidate knowledge from $description

Knowledge files updated, SUMMARY preserved.
EOF
)"
```

**Update STATE.md** "Recent Adhoc Work" section:
- Find or create "### Recent Adhoc Work" under "## Accumulated Context"
- Add entry at top: `- [YYYY-MM-DD]: [description] ({exec_dir}/adhoc-01-SUMMARY.md)`
- Keep last 5 entries (remove older ones from list)

**Set last command:**
```bash
ms-tools set-last-command "ms:adhoc $ARGUMENTS"
```

**Report completion:**
```
Adhoc work complete: [description]

**Commit:** [hash]
**Files modified:** [count]
**Knowledge updated:** [list of knowledge files]

Artifacts:
- Summary: {exec_dir}/adhoc-01-SUMMARY.md
- Patch: {exec_dir}/adhoc-01-changes.patch
- Knowledge: .planning/knowledge/[subsystem].md
```

```
---

Continue with current work or check project status:
- `/ms:progress` — see project status
- `/ms:execute-phase` — continue phase execution
```
</step>

</process>
