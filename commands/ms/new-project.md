---
name: ms:new-project
description: Initialize a new project with deep context gathering and PROJECT.md
allowed-tools:
  - Read
  - Bash
  - Write
  - AskUserQuestion
---

<objective>

Initialize a new project through comprehensive context gathering.

This is the most leveraged moment in any project. Deep questioning here means better plans, better execution, better outcomes. The quality of PROJECT.md determines the quality of everything downstream.

Creates `.planning/` with PROJECT.md and config.json.

</objective>

<execution_context>

@~/.claude/mindsystem/references/principles.md
@~/.claude/mindsystem/references/questioning.md
@~/.claude/mindsystem/templates/project.md
@~/.claude/mindsystem/templates/config.json

</execution_context>

<process>

<step name="setup">

**MANDATORY FIRST STEP — Execute these checks before ANY user interaction:**

1. **Detect update mode:**
   ```bash
   [ -f .planning/PROJECT.md ] && echo "IS_UPDATE=true" || echo "IS_UPDATE=false"
   ```

2. **Initialize git repo in THIS directory** (required even if inside a parent repo):
   ```bash
   # Check if THIS directory is already a git repo root (handles .git file for worktrees too)
   if [ -d .git ] || [ -f .git ]; then
       echo "Git repo exists in current directory"
   else
       git init
       echo "Initialized new git repo"
   fi
   ```

3. **Detect existing code (brownfield detection):**
   ```bash
   # Check for existing code files
   CODE_FILES=$(find . -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.swift" -o -name "*.java" 2>/dev/null | grep -v node_modules | grep -v .git | head -20)
   HAS_PACKAGE=$([ -f package.json ] || [ -f requirements.txt ] || [ -f Cargo.toml ] || [ -f go.mod ] || [ -f Package.swift ] && echo "yes")
   IS_BROWNFIELD=$( ([ -n "$CODE_FILES" ] || [ "$HAS_PACKAGE" = "yes" ]) && echo "yes" || echo "no")
   HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes")
   ```

   **You MUST run all bash commands above using the Bash tool before proceeding.**

</step>

<step name="question">

**Open the conversation:**

**If IS_UPDATE=true (update mode):**
- Read existing `.planning/PROJECT.md`
- Present a brief summary of the current project context
- Ask inline (freeform, NOT AskUserQuestion): "What do you want to update?"
- Follow the same questioning principles below, but focused on what changed

**If IS_UPDATE=false (first run):**

Ask inline (freeform, NOT AskUserQuestion):

- **Greenfield** (no existing code): "What do you want to build?"
- **Brownfield** (code detected in Step 1): "Tell me about this project — if you were explaining it to someone who's never seen it, what does it do and who uses it?"

For brownfield, explicitly note: "Not the next feature — the product as a whole."

Wait for their response. This gives you the context needed to ask intelligent follow-up questions.

**Derive business context:**

After the initial response, infer business context before asking more questions. Present inferred audience/problem/differentiation for the user to react to:

"It sounds like this is for [audience] dealing with [problem], and your approach is different because [differentiation]. Sound right?"

This leverages what they've already said and gives them something concrete to react to.

**Follow the thread:**

Based on what they said, ask follow-up questions that dig into their response. Use AskUserQuestion with options that probe what they mentioned — interpretations, clarifications, concrete examples.

Track coverage against the 6-item context checklist from `questioning.md`. Probe fuzziest areas first — spend questioning budget where clarity is lowest.

Use grounding questions from `questioning.md` instead of template-shaped questions. Don't ask "Who is your target audience?" — ask "Who would be your first 10 users?"

When the conversation pauses and sections are still fuzzy, use success-backward: "Imagine this is wildly successful in a year. What does that look like?"

Consult `questioning.md` for techniques — challenge vagueness, derive before asking, use grounding questions over template-shaped questions.

**Decision gate:**

When you could write a clear PROJECT.md, use AskUserQuestion:

- header: "Ready?"
- question (first run): "I think I understand what you're after. Ready to create PROJECT.md?"
- question (update mode): "Ready to update PROJECT.md with these changes?"
- options:
  - "Create PROJECT.md" / "Update PROJECT.md" — Let's move forward
  - "Keep exploring" — I want to share more / ask me more

If "Keep exploring" — ask what they want to add, or identify gaps and probe naturally.

Loop until create/update selected.

</step>

<step name="project">

Synthesize all context into `.planning/PROJECT.md` using the template from `templates/project.md`.

**For greenfield projects:**

Initialize all sections from questioning:
- **What This Is** — product identity from questioning
- **Core Value** — the ONE thing from questioning
- **Who It's For** — target audience from questioning
- **Core Problem** — pain or desire from questioning
- **How It's Different** — differentiators from questioning
- **Key User Flows** — core interactions from questioning
- **Out of Scope** — boundaries from questioning
- **Constraints** — hard limits from questioning
- **Technical Context** — minimal for greenfield (stack choices if discussed)
- **Validated** — `(None yet — ship to validate)`
- **Key Decisions** — any decisions made during questioning

**For brownfield projects (codebase map exists):**

Same as greenfield, plus:

1. Read `.planning/codebase/ARCHITECTURE.md` and `STACK.md`
2. Infer Validated requirements from existing code — what the codebase already does
3. Populate Technical Context from codebase map (stack, integrations, known debt)

```markdown
## Validated
- ✓ [Existing capability 1] — existing
- ✓ [Existing capability 2] — existing
```

**Key Decisions:**

Initialize with any decisions made during questioning:

```markdown
## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| [Choice from questioning] | [Why] | — Pending |
```

**Last updated footer:**

```markdown
---
*Last updated: [date] after initialization*
```

Do not compress. Capture everything gathered.

</step>

<step name="config">

Create or update `.planning/config.json` with subsystems and code_review using `templates/config.json` structure.

**Subsystems:** Derive 5-10 initial subsystems from the project context gathered during questioning. These are short, lowercase identifiers for the major functional areas of the project.

Examples by project type:
- E-commerce: `["auth", "products", "cart", "checkout", "payments", "orders", "ui", "api", "database"]`
- SaaS: `["auth", "dashboard", "analytics", "billing", "notifications", "ui", "api", "database"]`
- Mobile app: `["auth", "onboarding", "feed", "messaging", "profile", "media", "api", "storage"]`

These values are used throughout the system for consistent categorization of summaries, debug docs, and adhoc work.

**Update mode (config.json already exists):** Re-derive subsystems from updated context. Preserve any existing `code_review` values — do not overwrite configured reviewers with nulls.

</step>

<step name="commit">

**First run:**
```bash
git add .planning/PROJECT.md .planning/config.json
git commit -m "$(cat <<'EOF'
docs: initialize [project-name]

[One-liner from PROJECT.md]

Creates PROJECT.md with business context and constraints.
EOF
)"
```

**Update mode:**
```bash
git add .planning/PROJECT.md .planning/config.json
git commit -m "$(cat <<'EOF'
docs: update [project-name] project context

[Brief description of what changed]
EOF
)"
```

</step>

<step name="done">

Present completion with next steps (see ~/.claude/mindsystem/references/continuation-format.md):

**First run:**
```
Project initialized:

- Project: .planning/PROJECT.md
- Config: .planning/config.json
[If .planning/codebase/ exists:] - Codebase: .planning/codebase/ (7 documents)
```

**Update mode:**
```
Project updated:

- Project: .planning/PROJECT.md
- Config: .planning/config.json
```

**Routing (both modes):**

```
---

## ▶ Next Up

`/ms:new-milestone` — Discover what to build first, create requirements and roadmap

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:config` — Configure code reviewers, gitignore, and other preferences
[If brownfield detected and no codebase map:] - `/ms:map-codebase` — Analyze existing codebase for technical context

---
```

</step>

<step name="update_last_command">
Update `.planning/STATE.md` Last Command field (if STATE.md exists):
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:new-project | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line
- Note: STATE.md may not exist yet if this is the first command
</step>

</process>

<output>

- `.planning/PROJECT.md`
- `.planning/config.json`

</output>

<success_criteria>

- [ ] Deep questioning completed with business context extracted (or update conversation completed)
- [ ] PROJECT.md captures product identity (What/Value/Audience/Problem/Differentiation/Flows)
- [ ] PROJECT.md captures boundaries (Out of Scope, Constraints, Technical Context)
- [ ] Validated requirements initialized (empty for greenfield, inferred for brownfield)
- [ ] Key Decisions table initialized
- [ ] config.json has subsystems and code_review settings (existing code_review preserved in update mode)
- [ ] All committed to git

</success_criteria>
