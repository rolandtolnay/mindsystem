<script_extraction>

## Principles for Extracting Bash from Prompts into ms-tools

When a workflow or agent has inline bash that consumes context, use these principles to decide what to extract and how to design the subcommand boundary.

### Evaluate by Total Context Cost, Not Line Count

The real cost of inline bash is **bash lines + surrounding English explanation**. A 1-line `git stash pop` that needs 4 lines explaining conflict resolution strategy costs 5 lines total. A 12-line conditional commit block with 6 lines explaining amend safety costs 18 lines. Evaluate extraction value by the total block — everything the prompt has to explain — not just the bash.

### Self-Contained Operations, Not Git Wrappers

A subcommand that reads its own inputs from existing state (UAT frontmatter, config, git status) is worth more than a dumb wrapper requiring the workflow to pass data. Design subcommands to own their data flow:

- **Good:** `uat-stash-mocks` reads `mocked_files` and `current_batch` from UAT.md internally
- **Bad:** `uat-stash-mocks --files a.dart,b.dart --name mocks-batch-2` (workflow must extract and pass data)

Self-contained commands eliminate both the bash AND the data-passing instructions from the prompt.

### Bundle What Always Happens Together

If operations are always sequential with no judgment in between, they're one subcommand:

- `git checkout -- <files>` + clear `mocked_files` in UAT.md = `uat-revert-mocks`
- `git stash pop` + conflict resolution with `--theirs` + update `mocked_files` + drop stash = `uat-pop-mocks`
- `git add` + amend-or-new decision + `git commit` + record hash in UAT = `uat-fix-commit`

If judgment or user input happens between operations, they must be separate subcommands.

### Extraction Threshold

Extract when:
- Bash block appears 2+ times across the workflow (duplication)
- Single occurrence but total context cost (bash + explanation) exceeds ~8 lines
- Logic has edge cases (conflict handling, amend safety) that require explanatory prose

Do NOT extract when:
- 1-line bash appearing once with no edge cases (`git status --porcelain`, `grep -c ...`)
- The result requires immediate judgment interpretation (the prompt needs to reason about the output)
- Maintenance cost (implementation + tests) exceeds context savings

### No-Op Gracefully

Subcommands that find nothing to do (no mocked files, no stash to pop) exit 0 with a stderr message. This lets the workflow call them unconditionally without guard logic:

```
# Workflow says this simply:
ms-tools uat-stash-mocks $PHASE
# Instead of:
if [ -n "$MOCKED_FILES" ]; then git stash push -m "mocks-batch-$N" -- $MOCKED_FILES; fi
```

The conditional logic moves into the script. The prompt stays clean.

### JSON Output for Downstream Consumption

Subcommands that produce data for the next workflow step output structured JSON. This eliminates parsing instructions from the prompt:

```json
{"hash": "abc1234", "amend": true}
```

The workflow reads the JSON directly instead of `FIX_HASH=$(git rev-parse --short HEAD)` + downstream variable threading.

### Track Ephemeral State in Existing Artifacts

When a subcommand creates state that another subcommand needs later (stash refs, temporary markers), store it in the nearest existing artifact (UAT.md frontmatter, config.json) rather than inventing new state files. This keeps the system's state surface area minimal.

</script_extraction>
