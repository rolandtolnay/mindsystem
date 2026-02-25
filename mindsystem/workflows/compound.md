<purpose>
Compound code changes into per-subsystem knowledge files on demand. Handles work done outside the Mindsystem pipeline — direct Claude Code sessions, manual edits, merged branches.
</purpose>

<process>

<step name="parse_input" priority="first">
Parse `$ARGUMENTS` to determine input mode:

```bash
# Validate active project
if [ ! -f .planning/config.json ]; then
  echo "ERROR: No active Mindsystem project found (.planning/config.json missing)"
  echo ""
  echo "Options:"
  echo "- Initialize project: /ms:new-project"
  exit 1
fi
```

**Mode detection:**
- If `$ARGUMENTS` empty: **description mode** — deduce from conversation context. Summarize what was discussed/changed in the current session.
- If matches git SHA pattern (7-40 hex chars), contains `..`, or starts with `HEAD`: **git mode**
- If matches existing file path (`test -e "$ARGUMENTS"`): **file mode**
- Otherwise: **description mode** — treat `$ARGUMENTS` as free-text description
</step>

<step name="resolve_change_context">
Gather lightweight change context based on input mode. Keep main context lean — only stats and summaries.

**Git mode:**
```bash
# Stats only — full diff read by compounder
git show --stat <ref>        # single commit
git diff --stat <range>      # range
```
Capture the ref/range string for passing to compounder.

**File mode:**
```bash
git log --oneline -5 -- <path>
```
Capture file path for passing to compounder.

**Description mode (including no-args):**
Spawn 1 Explore agent to find relevant code changes. If changes span multiple unrelated areas, spawn a second agent for the additional area. They return:
- Which files changed or are relevant
- Which subsystems are likely affected
- Concise summary of changes

Thoroughness: "medium".
</step>

<step name="determine_subsystems">
Read config.json subsystems and match changes:

```bash
jq -r '.subsystems[]' .planning/config.json 2>/dev/null
```

**Git/file mode:** Match file paths from diff stats against subsystem names via keyword matching.

**Description mode:** Use Explore agent findings for subsystem matching.

**Detect potential new subsystems:** Changes in file areas that don't match any existing subsystem.

**First-run handling:** If no subsystems in config.json and no knowledge files exist, propose a subsystem name derived from the project domain.
</step>

<step name="confirm_with_user">
Present findings and confirm before spawning compounder:

- Affected subsystems list
- Proposed new subsystems (if any)
- Change summary (1-3 lines)

AskUserQuestion: "Compound knowledge for these subsystems?" with options:
- Confirm
- Adjust (let me modify the list)
- Cancel
</step>

<step name="spawn_compounder">
Spawn ms-compounder via Task tool with:
- Input mode (`git`, `file`, or `description`)
- Change reference (git ref/range, file path, or description + exploration findings)
- Confirmed affected subsystems list
- Config.json subsystem vocabulary

Agent reads changes, reads affected knowledge files, writes updates, returns report.
</step>

<step name="finalize">
**Update config.json** (if new subsystems were confirmed in step 4):
```bash
# Add new subsystem to config.json
jq '.subsystems += ["new-subsystem"]' .planning/config.json > tmp.$$.json && mv tmp.$$.json .planning/config.json
```

**Commit changes:**
```bash
git add .planning/knowledge/*.md
# Only add config.json if modified
git add .planning/config.json 2>/dev/null
git commit -m "$(cat <<'EOF'
docs: compound knowledge from <description>
EOF
)"
```

**Set last command:**
```bash
ms-tools set-last-command "ms:compound $ARGUMENTS"
```

**Report:** Subsystems updated, entries added/changed/removed, new subsystems created (if any).
</step>

All three finalize actions (commit, set-last-command, report) must execute — do not stop after the compounder returns.

</process>
