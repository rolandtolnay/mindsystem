---
name: ms:config
description: Configure Mindsystem preferences — code reviewers, mockups, gitignore, git remote, task tracker
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>

Configure Mindsystem preferences for the current project.

Manages code reviewer agents, mockup preferences, .gitignore patterns for `.planning/` artifacts, git remote setup, and task tracker integration. Run anytime to reconfigure — idempotent.

</objective>

<process>

<step name="load_context">

**Load current state:**

```bash
# Check for existing config
[ -f .planning/config.json ] && cat .planning/config.json || echo "NO_CONFIG"

# Check for PROJECT.md (tech stack detection)
[ -f .planning/PROJECT.md ] && echo "HAS_PROJECT" || echo "NO_PROJECT"

# Check for STACK.md (precise tech detection)
[ -f .planning/codebase/STACK.md ] && echo "HAS_STACK" || echo "NO_STACK"

# Check git remote
git remote -v 2>/dev/null || echo "NO_REMOTE"
```

**Run this before proceeding.**

</step>

<step name="git_remote">

**Skip if remote already configured.**

If no remote exists:

Explain: "Your project has a local git repo but no remote. Want to create one on GitHub?"

Use AskUserQuestion:
- header: "Git remote"
- question: "Create a GitHub repository for this project?"
- options:
  - "Create with gh CLI" — Run `gh repo create` to set up remote and push
  - "Skip for now" — Continue without remote

If "Create with gh CLI":
- Derive repo name from directory name
- Show the command: `gh repo create [name] --source=. --push`
- Confirm with user before executing
- Execute via Bash tool

</step>

<step name="code_reviewers">

Show current code_review values from config.json (if loaded).

**Default reviewers:** adhoc=`ms-code-simplifier`, phase=`ms-code-simplifier`, milestone=`ms-code-reviewer`

Use AskUserQuestion:
- header: "Code review"
- question: "Which code reviewer configuration do you want?"
- options:
  - "Default" — ms-code-simplifier for adhoc/phase, ms-code-reviewer for milestone (Recommended)
  - "Skip code review" — Disable review for all tiers
  - "Custom" — I'll specify reviewers manually

If "Custom": ask for each tier (adhoc, phase, milestone) individually.

If "Skip code review": set all three values to `"skip"`.

Update config.json with selected values.

</step>

<step name="gitignore_patterns">

Check if `.gitignore` exists and current `.planning/` ignore patterns:

```bash
[ -f .gitignore ] && grep -n "planning" .gitignore || echo "NO_PLANNING_PATTERNS"
```

Explain: "We recommend committing `.planning/` to git — it's your project's memory (decisions, requirements, knowledge files). But some artifacts are large or environment-specific."

Use AskUserQuestion (multiSelect):
- header: "Gitignore"
- question: "Which `.planning/` artifacts should be git-ignored?"
- options:
  - "Phase patch files (`.planning/phases/**/*.patch`)" — Large binary diffs, regeneratable
  - "Design mockups (`.planning/phases/**/*.html`)" — Generated HTML mockups from design-phase

Apply selected patterns to `.gitignore`. Create the file if needed.

If no selections: skip gitignore changes.

</step>

<step name="mockup_preferences">

Read current value:

```bash
CURRENT=$(cat .planning/config.json 2>/dev/null | jq -r '.open_mockups // "auto"')
echo "Current open_mockups: $CURRENT"
```

Use AskUserQuestion:
- header: "Mockups"
- question: "How should mockup comparisons open after generation?"
- options:
  - "Auto-open (Recommended)" — Open comparison.html in browser automatically
  - "Ask first" — Prompt before opening
  - "Don't open" — Display path only, never auto-open

Map selection to config value:
- "Auto-open" → `"auto"`
- "Ask first" → `"ask"`
- "Don't open" → `"off"`

Update config.json with selected value via jq:

```bash
jq --arg v "$VALUE" '.open_mockups = $v' .planning/config.json > .planning/config.tmp && mv .planning/config.tmp .planning/config.json
```

</step>

<step name="task_tracker">

Read current value:

```bash
CURRENT=$(cat .planning/config.json 2>/dev/null | jq -r '.task_tracker.type // "not configured"')
echo "Current task_tracker: $CURRENT"
```

Use AskUserQuestion:
- header: "Task tracker"
- question: "Do you use a task tracker for this project?"
- options:
  - "Linear" — Integrate with Linear for ticket-driven adhoc work
  - "None / not yet" — Skip task tracker integration

If "Linear":

Use AskUserQuestion:
- header: "Linear CLI"
- question: "Path to Linear CLI script?"
- options:
  - "Default (`uv run ~/.claude/skills/linear/scripts/linear.py`) (Recommended)" — Standard Mindsystem Linear skill location
  - "Custom path" — I'll provide the CLI path

If "Default": set `cli` to `uv run ~/.claude/skills/linear/scripts/linear.py`
If "Custom path": ask user for path via AskUserQuestion.

Write to config.json:

```bash
jq '.task_tracker = {"type": "linear", "cli": $cli}' --arg cli "$CLI_PATH" .planning/config.json > .planning/config.tmp && mv .planning/config.tmp .planning/config.json
```

If "None / not yet":

```bash
jq '.task_tracker = null' .planning/config.json > .planning/config.tmp && mv .planning/config.tmp .planning/config.json
```

</step>

<step name="validation_summary">

Show final config state:

```
Configuration updated:

- Code reviewers: [adhoc / phase / milestone values]
- Mockup open: [auto / ask / off]
- Gitignore: [patterns added, or "no changes"]
- Git remote: [remote URL, or "none configured"]
- Task tracker: [type + cli path, or "none"]
```

Check subsystems in config.json. If empty or missing, note:
"Subsystems are derived during `/ms:new-project`. Run `/ms:doctor` to update or verify them."

</step>

<step name="commit">

**Skip if no changes made.**

```bash
git add .planning/config.json .gitignore
git commit -m "$(cat <<'EOF'
chore: configure mindsystem preferences
EOF
)"
```

</step>

<step name="done">

Present next steps:

**If PROJECT.md exists:**

```
---

## ▶ Next Up

`/ms:new-milestone` — Discover what to build next, create requirements and roadmap

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:doctor` — Verify subsystems and artifact health

---
```

**If no PROJECT.md:**

```
---

## ▶ Next Up

`/ms:new-project` — Initialize project with business context and vision

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:doctor` — Verify subsystems and artifact health

---
```

</step>

</process>

<success_criteria>

- [ ] Changes committed (if any)
- [ ] User routed to next step
- [ ] Gitignore patterns applied (if selected)
- [ ] Git remote offered (if missing)
- [ ] Validation summary displayed
- [ ] Config.json code_review values set (or preserved if skipped)
- [ ] Config.json open_mockups value set (or preserved if skipped)
- [ ] Config.json task_tracker value set (or preserved if skipped)

</success_criteria>
