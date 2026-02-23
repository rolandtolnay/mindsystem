---
name: ms:config
description: Configure Mindsystem preferences — code reviewers, gitignore, git remote
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>

Configure Mindsystem preferences for the current project.

Manages code reviewer agents, .gitignore patterns for `.planning/` artifacts, and git remote setup. Run anytime to reconfigure — idempotent.

</objective>

<process>

<step name="load_context">

**MANDATORY FIRST STEP — Load current state:**

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

**You MUST run the bash command above using the Bash tool before proceeding.**

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

**If PROJECT.md or STACK.md exists:** Detect tech stack and suggest appropriate reviewers:

- **Flutter/Dart:** adhoc=`ms-flutter-code-quality`, phase=`ms-flutter-code-quality`, milestone=`ms-flutter-reviewer`
- **All others:** adhoc=`ms-code-simplifier`, phase=`ms-code-simplifier`, milestone=null

**If no PROJECT.md or STACK.md:** Warn: "No PROJECT.md found — can't suggest reviewers based on tech stack. Run `/ms:new-project` first, or pick manually."

Use AskUserQuestion:
- header: "Code review"
- question: "Which code reviewer configuration do you want?"
- options:
  - "[Suggested based on stack]" — e.g., "Flutter reviewers (ms-flutter-code-quality)" (Recommended)
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

<step name="validation_summary">

Show final config state:

```
Configuration updated:

- Code reviewers: [adhoc / phase / milestone values]
- Gitignore: [patterns added, or "no changes"]
- Git remote: [remote URL, or "none configured"]
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

Present next steps (see ~/.claude/mindsystem/references/continuation-format.md):

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

- [ ] Config.json code_review values set (or preserved if skipped)
- [ ] Gitignore patterns applied (if selected)
- [ ] Git remote offered (if missing)
- [ ] Validation summary displayed
- [ ] Changes committed (if any)
- [ ] User routed to next step

</success_criteria>
