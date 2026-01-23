# Workflow: Diagnose Mindsystem Issue

<purpose>
Systematically investigate why something in Mindsystem isn't working as expected.
</purpose>

<process>

## Step 1: Categorize the Issue

**Ask:** What type of issue is this?

| Category | Symptoms | Likely Location |
|----------|----------|-----------------|
| Command not found | `/ms:X` doesn't work | Installation, `commands/ms/` |
| Command wrong behavior | Runs but does unexpected thing | `commands/ms/X.md`, `workflows/*.md` |
| Agent fails | Subagent errors or wrong output | `agents/ms-*.md` |
| Plan execution issue | Tasks fail, wrong commits, no SUMMARY | `workflows/execute-plan.md`, `agents/ms-executor.md` |
| Wave execution issue | Plans not parallel, wrong order | `workflows/execute-phase.md`, plan frontmatter |
| Verification gaps | Verifier reports gaps that exist | `agents/ms-verifier.md`, `references/goal-backward.md` |
| Checkpoint handling | Checkpoints not pausing, wrong format | `references/checkpoints.md`, executor |
| State corruption | STATE.md wrong, position incorrect | `templates/state.md`, workflow state updates |
| Template wrong | Output file has wrong structure | `templates/*.md` |

## Step 2: Locate Relevant Files

Based on category, read the source files (relative to repo root):

**Command issues:**
```
commands/ms/{command}.md
```

**Workflow issues:**
```
mindsystem/workflows/{workflow}.md
```

**Agent issues:**
```
agents/ms-{agent}.md
```

**Template issues:**
```
mindsystem/templates/{template}.md
```

**Reference issues:**
```
mindsystem/references/{reference}.md
```

## Step 3: Trace the Flow

For behavior issues, trace the execution path:

1. **Command** → What does `allowed-tools` include? What @-references does it load?
2. **Workflow** → What steps does it follow? What does each step do?
3. **Agent** → What's its `<execution_flow>`? What are `<success_criteria>`?
4. **Template** → What's the expected output structure?

## Step 4: Identify the Gap

Compare expected behavior vs actual:

- **Expected:** What should happen based on the code?
- **Actual:** What's actually happening?
- **Gap:** Where does the divergence occur?

## Step 5: Propose Fix

Based on gap:

| Gap Type | Fix Location |
|----------|--------------|
| Missing step | Add to workflow process |
| Wrong logic | Modify workflow/agent step |
| Missing tool | Add to command `allowed-tools` |
| Wrong template | Modify template structure |
| Missing reference | Add @-reference to workflow |
| Documentation mismatch | Update docs to match behavior |

</process>

<common_issues>
## Common Issues and Fixes

### Command & Installation Issues

**"Command not working after install"**
- **Check:** `ls ~/.claude/commands/ms/` exists
- **Fix:** Re-run `npx mindsystem-cc`

**"Command works locally but not globally"**
- **Check:** Which installation is active (`.claude/` vs `~/.claude/`)
- **Fix:** Check `--local` flag, ensure correct scope

### Agent Execution Issues

**"Agent spawns but fails immediately"**
- **Check:** Agent has required tools for its operations
- **Check:** @-references in prompt exist and are correct paths
- **Fix:** Add missing tools or fix paths

**"Agent completes but output is wrong"**
- **Check:** Agent's `<execution_flow>` matches expected behavior
- **Check:** `<success_criteria>` is being verified
- **Fix:** Update agent logic or criteria

### Wave Execution Issues

**"Wave execution runs sequentially not parallel"**
- **Check:** Plans have correct `wave` in frontmatter
- **Check:** `depends_on` is correct (too many dependencies = sequential)
- **Fix:** Fix wave assignment in plan-phase workflow

**"Wrong wave assigned to plan"**
- **Check:** `files_modified` declarations for conflicts
- **Check:** `depends_on` transitive dependencies
- **Fix:** Review dependency analysis in plan-phase

### State Management Issues

**"STATE.md not updating"**
- **Check:** Executor has Write tool
- **Check:** STATE.md update step in execute-plan.md
- **Fix:** Ensure state update runs after SUMMARY creation

**"STATE.md position incorrect"**
- **Check:** Phase/plan tracking logic
- **Check:** SUMMARY.md parsing for completion
- **Fix:** Update position calculation

### Checkpoint Issues

**"Checkpoints not pausing execution"**
- **Check:** Task has `type="checkpoint:*"` attribute
- **Check:** Executor checkpoint handling in execution_flow
- **Fix:** Ensure checkpoint detection in executor

**"Checkpoint return format wrong"**
- **Check:** checkpoint-return.md template
- **Check:** Executor uses template correctly
- **Fix:** Update template or executor formatting

**"Continuation after checkpoint fails"**
- **Check:** continuation-prompt.md template
- **Check:** Orchestrator fills template correctly
- **Fix:** Update continuation handling

### Verification Issues

**"Verifier reports false gaps"**
- **Check:** must_haves derivation is correct
- **Check:** Artifact paths match actual files
- **Check:** Wiring verification patterns
- **Fix:** Update goal-backward derivation

**"Verifier misses actual gaps (stubs pass)"**
- **Check:** Stub detection patterns in verification-patterns.md
- **Check:** Substantive checks are running
- **Fix:** Add stronger stub detection

### Git Issues

**"Commits not created per task"**
- **Check:** Executor commits after each task
- **Check:** git staging logic
- **Fix:** Update executor commit flow

**"Commit format wrong"**
- **Check:** git-integration.md specification
- **Check:** Executor commit message generation
- **Fix:** Update commit format in executor

### Context Issues

**"Plan runs out of context"**
- **Check:** Task count (should be 2-3 max)
- **Check:** File count per task
- **Fix:** Split into smaller plans

**"Quality degrades mid-plan"**
- **Check:** Context usage (~50% target)
- **Check:** TDD plans (~40% target)
- **Fix:** Split plan, reduce scope

### Template Issues

**"Output file has wrong structure"**
- **Check:** Template file structure
- **Check:** Workflow/agent uses template correctly
- **Fix:** Update template or consumer

**"Missing sections in output"**
- **Check:** Template has all required sections
- **Check:** Consumer populates all sections
- **Fix:** Add missing sections
</common_issues>

<debugging_commands>
## Useful Debugging Commands

```bash
# Check installation
ls -la ~/.claude/commands/ms/
ls -la .claude/commands/ms/

# Check specific command
cat commands/ms/{command}.md

# Check workflow
cat mindsystem/workflows/{workflow}.md

# Check agent
cat agents/ms-{agent}.md

# Check template
cat mindsystem/templates/{template}.md

# Check plan structure
cat .planning/phases/XX-name/XX-NN-PLAN.md | head -30

# Check STATE.md
cat .planning/STATE.md

# Check recent commits
git log --oneline -20

# Check for stubs in file
grep -E "TODO|FIXME|placeholder|not implemented" src/path/file.ts
```
</debugging_commands>

<success_criteria>
Diagnosis complete when:
- Root cause identified
- Specific file(s) needing change identified
- Proposed fix described
</success_criteria>
