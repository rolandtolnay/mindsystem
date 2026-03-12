---
name: ms:config
description: Configure Mindsystem preferences — code reviewers, mockups, browser verification, gitignore, git remote, task tracker
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>

Configure Mindsystem preferences for the current project.

Manages code reviewer agents, mockup preferences, browser verification, .gitignore patterns for `.planning/` artifacts, git remote setup, and task tracker integration. Run anytime to reconfigure — idempotent.

</objective>

<process>

<step name="load_context">

**Load current state:**

```bash
# Check for existing config
[ -f .planning/config.json ] && cat .planning/config.json || echo "NO_CONFIG"

# Check for PROJECT.md (tech stack detection)
[ -f .planning/PROJECT.md ] && echo "HAS_PROJECT" || echo "NO_PROJECT"

# Check git remote
git remote -v 2>/dev/null || echo "NO_REMOTE"
```

**Determine mode** from `code_review` values in config.json:

- **Setup mode** — all `code_review` values are null (or no config file): first-time configuration.
- **Edit mode** — any `code_review` value is non-null: reconfiguration.

</step>

<step name="route">

**Setup mode:** Proceed through all setting steps sequentially (git_remote → code_reviewers → gitignore_patterns → mockup_preferences → browser_verification → task_tracker). Then go to `validation_summary`.

**Edit mode:** Display all current settings with values from config.json, git remote, and .gitignore:

```
## Current Settings

1. **Git remote** — {remote URL or "none configured"}
2. **Code reviewers** — adhoc: {value or "not set"}, phase: {value or "not set"}, milestone: {value or "not set"}
3. **Gitignore** — {current .planning/ patterns or "no .planning/ patterns"}
4. **Mockups** — open: {auto / ask / off}
5. **Browser verification** — {enabled / disabled}
6. **Task tracker** — {type + cli path, or "none"}
```

Ask: "Which settings would you like to change? Enter the numbers (e.g. 1, 3, 5), 'all' to reconfigure everything, or 'done' if everything looks good."

- **"done"** → skip to `validation_summary` (no changes)
- **"all"** → proceed through all setting steps sequentially
- **Specific numbers** → proceed through only the corresponding setting steps, skip the rest

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

If "Custom": use AskUserQuestion for each tier (adhoc, phase, milestone) individually, offering available reviewer agents as options.

If "Skip code review": set all three values to `"skip"`.

Update config.json:

```bash
ms-tools config-set code_review --json '{"adhoc": "'"$ADHOC"'", "phase": "'"$PHASE"'", "milestone": "'"$MILESTONE"'"}'
```

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
  - "Browser screenshots (`.planning/phases/**/screenshots/`)" — Browser verification screenshots

Apply selected patterns to `.gitignore`. Create the file if needed:

```bash
echo '.planning/phases/**/*.patch' >> .gitignore       # if selected
echo '.planning/phases/**/*.html' >> .gitignore        # if selected
echo '.planning/phases/**/screenshots/' >> .gitignore  # if selected
```

If no selections: skip gitignore changes.

</step>

<step name="mockup_preferences">

Read current value:

```bash
CURRENT=$(ms-tools config-get open_mockups --default "auto")
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

Update config.json:

```bash
ms-tools config-set open_mockups "$VALUE"
```

</step>

<step name="browser_verification">

Read current value:

```bash
CURRENT=$(ms-tools config-get browser_verification.enabled --default "true")
echo "Current browser_verification.enabled: $CURRENT"
```

Use AskUserQuestion:
- header: "Browser verification"
- question: "Enable automated browser verification during execute-phase? (Tests your web UI after code changes)"
- options:
  - "Enabled (Recommended)" — Automatically test web UI after phase execution
  - "Disabled" — Skip browser verification

Map selection:
- "Enabled" → `true`
- "Disabled" → `false`

Update config.json:

```bash
ms-tools config-set browser_verification --json '{"enabled": true}'   # or false
```

</step>

<step name="task_tracker">

Read current value:

```bash
CURRENT=$(ms-tools config-get task_tracker.type --default "not configured")
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
ms-tools config-set task_tracker --json '{"type": "linear", "cli": "'"$CLI_PATH"'"}'
```

If "None / not yet":

```bash
ms-tools config-delete task_tracker
```

</step>

<step name="validation_summary">

Show final config state:

```
Configuration updated:

- Code reviewers: [adhoc / phase / milestone values]
- Mockup open: [auto / ask / off]
- Browser verification: [enabled / disabled]
- Gitignore: [patterns added, or "no changes"]
- Git remote: [remote URL, or "none configured"]
- Task tracker: [type + cli path, or "none"]
```

Check subsystems in config.json. If empty or missing, note:
"Subsystems are derived during `/ms:new-project`. Run `/ms:doctor` to update or verify them."

</step>

<step name="commit">

**Skip if no changes made.**

**Update state and commit:**

```bash
git add .planning/config.json .gitignore
git commit -m "chore: configure mindsystem preferences"
```

</step>

</process>

<success_criteria>

- [ ] Setup mode triggered when all code_review values null; edit mode otherwise
- [ ] Edit mode displays numbered settings with current values
- [ ] Only user-selected settings modified in edit mode
- [ ] Changes committed (if any)
- [ ] Gitignore patterns applied (if selected)
- [ ] Git remote offered (if missing)
- [ ] Validation summary displayed
- [ ] Terminates after commit/summary — no Next Up routing

</success_criteria>
