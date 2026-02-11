<purpose>
Execute small work items discovered during verification or debugging without the overhead of phase insertion.

Provides "describe → quick plan → execute → verify → log" flow for work that's too small for a phase but needs tracking.
</purpose>

<scope_guard>
**Maximum scope: 2 tasks**

If work requires more than 2 tasks, REFUSE with:
```
This work requires [N] tasks (max: 2 for adhoc work).

Use `/ms:insert-phase [current_phase] [description]` instead.
```

If work requires architectural changes, REFUSE with:
```
This work requires architectural changes.

Use `/ms:insert-phase` for proper planning and context tracking.
```
</scope_guard>

<required_reading>
Read STATE.md before any operation to load project context.

@~/.claude/mindsystem/templates/adhoc-summary.md
</required_reading>

<process>

<step name="parse_arguments" priority="first">
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
</step>

<step name="validate_project">
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

Load project context:
- Current phase (for related_phase in adhoc artifacts)
- Accumulated decisions (constraints on this work)
- Blockers/concerns (things to watch for)
</step>

<step name="analyze_scope">
Quick analysis of what tasks are needed:

1. Identify files that need modification
2. Determine discrete tasks required
3. Check for architectural implications

**Task estimation:**
- Single file, simple change → 1 task
- Multiple files, related change → 1-2 tasks
- Multiple files, different concerns → likely >2 tasks

**Architectural check:**
- New patterns or abstractions → architectural
- Changes to core interfaces → architectural
- Cross-cutting concerns → architectural

**Decision point:**

If tasks > 2:
```
This work requires approximately [N] tasks:
1. [task description]
2. [task description]
3. [task description]
...

Adhoc work is limited to 2 tasks maximum.

**Suggestion:** `/ms:insert-phase [current_phase] [description]`
```

If architectural:
```
This work involves architectural changes:
- [what makes it architectural]

Adhoc work handles small, isolated fixes — not structural changes.

**Suggestion:** `/ms:insert-phase [current_phase] [description]`
```

If ≤2 tasks and not architectural: PROCEED
</step>

<step name="create_adhoc_directory">
Ensure adhoc directory exists:

```bash
mkdir -p .planning/adhoc
```
</step>

<step name="create_lightweight_plan">
Generate timestamp and slug:

```bash
timestamp=$(date "+%Y-%m-%d")
slug=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
plan_file=".planning/adhoc/${timestamp}-${slug}-PLAN.md"
```

Create minimal PLAN.md:

```markdown
# Adhoc: [User's description]

**Subsystem:** [subsystem or "general"] | **Type:** execute

## Context
[User's description of what needs to be done and why]

## Changes

### 1. [Action-oriented name]
**Files:** `[file paths]`

[What to do, what to avoid and WHY]

[### 2. if needed, same structure]

## Verification
- [How to verify the work is complete]

## Must-Haves
- [ ] [Observable outcome 1]
- [ ] [Observable outcome 2]
```

Write to file:
```bash
echo "Plan created: $plan_file"
```
</step>

<step name="execute_tasks">
Execute each task inline (no subagent for small work).

For each task:
1. Read current file state (use Explore subagent if context gathering needed)
2. Make changes
3. Run verify command
4. Track files modified

**Deviation rules apply:**
- Rule 1 (Bug): Auto-fix bugs found during execution
- Rule 2 (Critical): Auto-fix security/data issues
- Rule 3 (Blocking): Auto-fix missing dependencies, typos

**Rule 4 (Architectural) triggers STOP:**
If execution reveals architectural changes needed:
```
STOP: Architectural changes required

During execution, discovered:
- [what architectural change is needed]

This exceeds adhoc scope.

Work completed so far:
- [list completed tasks]

**Next steps:**
1. Commit partial work (if valuable)
2. Use `/ms:insert-phase` for remaining work
```

Use AskUserQuestion to confirm how to proceed.
</step>

<step name="lightweight_verification">
Verify the work is complete:

1. Run verify commands from each task
2. Check files exist/changed as expected
3. Run relevant tests if specified in verify

**Not required for adhoc:**
- Full goal-backward verification
- Cross-system integration checks
- Regression test suite

Keep verification focused on the specific changes made.
</step>

<step name="code_review">
Read code review agent from config:

```bash
CODE_REVIEW=$(cat .planning/config.json 2>/dev/null | jq -r '.code_review.adhoc // .code_review.phase // empty')
```

**If CODE_REVIEW = "skip":**
Skip to create_adhoc_summary.

**If CODE_REVIEW = empty/null:**
Use default: `CODE_REVIEW="ms-code-simplifier"`

**Otherwise:**
Use CODE_REVIEW value directly as agent name.

1. **Get modified files:**
   ```bash
   git diff --name-only HEAD | grep -E '\.(dart|ts|tsx|js|jsx|swift|kt|py|go|rs)$'
   ```

2. **Spawn code review agent with adhoc scope:**
   ```
   Task(
     prompt="
     <objective>
     Review code modified in adhoc work.
     Preserve all functionality. Improve clarity and consistency.
     </objective>

     <scope>
     Files to analyze:
     {MODIFIED_FILES}
     </scope>

     <output>
     After review and simplifications, run static analysis and tests.
     Report what was improved and verification results.
     </output>
     ",
     subagent_type="{CODE_REVIEW}"
   )
   ```

3. **Track review changes:**
   - If changes made: Set `CODE_REVIEW_APPLIED=true`
   - Reviewed files will be included in the adhoc commit
   - Note in SUMMARY.md that code review was applied
</step>

<step name="create_adhoc_summary">
Create SUMMARY.md (see @~/.claude/mindsystem/templates/adhoc-summary.md for full template):

```bash
summary_file=".planning/adhoc/${timestamp}-${slug}-SUMMARY.md"

# Read subsystems for categorization
jq -r '.subsystems[]' .planning/config.json 2>/dev/null
```

```markdown
---
type: adhoc
description: [description]
completed: [ISO timestamp]
duration: [X min]
related_phase: [phase or "none"]
subsystem: [select from config.json subsystems based on work performed]
tags: [searchable keywords from work context]
files_modified:
  - [path/to/file1.ts]
  - [path/to/file2.ts]
commit: [hash - filled after commit]
learnings:
  - [optional: include only when work revealed non-obvious insights. Skip for routine fixes.]
---

# Adhoc: [Description]

**[Substantive one-liner describing what was done]**

## What Was Done

- [accomplishment 1]
- [accomplishment 2]

## Files Modified

- `[path]`: [what changed]
- `[path]`: [what changed]

## Verification

- [what was verified and result]
```

Write to file.
</step>

<step name="update_state">
Update STATE.md with adhoc work entry:

1. Read current STATE.md
2. Find or create "### Recent Adhoc Work" under "## Accumulated Context"
3. Add entry at top of list
4. Keep last 5 entries (remove older ones from list, files remain in .planning/adhoc/)

Format:
```markdown
### Recent Adhoc Work

- [YYYY-MM-DD]: [description] (.planning/adhoc/[filename]-SUMMARY.md)
```

If section doesn't exist, add after "### Pending Todos" section:

```markdown
### Recent Adhoc Work

- [YYYY-MM-DD]: [description] (.planning/adhoc/[filename]-SUMMARY.md)

*See `.planning/adhoc/` for full history*
```
</step>

<step name="git_commit">
Single commit for all changes (including simplifications if applied):

```bash
# Add all modified files (code + reviewed files)
git add [code files modified]
git add [reviewed files if CODE_REVIEW_APPLIED]
git add "$plan_file"
git add "$summary_file"
git add .planning/STATE.md

# Determine commit type
# feat: new functionality
# fix: bug fix, correction
commit_type="fix"  # or "feat" based on nature of work

# Include code review note if applied
if [ "$CODE_REVIEW_APPLIED" = "true" ]; then
  review_note="Includes code review pass."
else
  review_note=""
fi

git commit -m "$(cat <<'EOF'
${commit_type}(adhoc): [description]

Files: [count] modified
${review_note}
EOF
)"

# Capture commit hash
commit_hash=$(git rev-parse --short HEAD)
```

Update SUMMARY.md with commit hash in frontmatter.
</step>

<step name="generate_adhoc_patch">
Generate patch file from the adhoc commit:

```bash
patch_file=".planning/adhoc/${timestamp}-${slug}.patch"

~/.claude/mindsystem/scripts/generate-adhoc-patch.sh "$commit_hash" "$patch_file"
```

If patch generated (file exists and non-empty):
- Update SUMMARY.md frontmatter to include `patch_file: [path]`

If skipped (no implementation changes outside exclusions):
- Leave patch_file field empty or omit from SUMMARY.md
</step>

<step name="completion">
Report completion:

```
Adhoc work complete: [description]

**Commit:** [hash]
**Duration:** [X min]
**Files modified:** [count]

Artifacts:
- Plan: .planning/adhoc/[timestamp]-[slug]-PLAN.md
- Summary: .planning/adhoc/[timestamp]-[slug]-SUMMARY.md
- Patch: .planning/adhoc/[timestamp]-[slug].patch (if generated)

STATE.md updated with adhoc entry.

---

Continue with current work or check project status:
- `/ms:progress` — see project status
- `/ms:execute-phase` — continue phase execution
```
</step>

</process>

<deviation_rules>
Adhoc work uses the same deviation rules as plan execution:

**Rule 1 - Bug in plan:** Auto-fix
**Rule 2 - Missing critical:** Auto-fix
**Rule 3 - Blocking issue:** Auto-fix
**Rule 4 - Architectural change:** STOP and suggest /ms:insert-phase

Rule 4 is strict for adhoc work — architectural changes exceed adhoc scope by definition.
</deviation_rules>

<output_artifacts>
- `.planning/adhoc/{timestamp}-{slug}-PLAN.md` — lightweight plan
- `.planning/adhoc/{timestamp}-{slug}-SUMMARY.md` — completion summary
- `.planning/adhoc/{timestamp}-{slug}.patch` — implementation changes (if any)
- Updated `.planning/STATE.md` — adhoc entry in accumulated context
- Git commit with all changes
</output_artifacts>
