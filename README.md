<div align="center">

# MINDSYSTEM

**A light-weight and powerful meta-prompting, context engineering and spec-driven development system for Claude Code by TÂCHES.**

**Solves context rot — the quality degradation that happens as Claude fills its context window.**

[![npm version](https://img.shields.io/npm/v/mindsystem-cc?style=for-the-badge&logo=npm&logoColor=white&color=CB3837)](https://www.npmjs.com/package/mindsystem-cc)
[![npm downloads](https://img.shields.io/npm/dm/mindsystem-cc?style=for-the-badge&logo=npm&logoColor=white&color=CB3837)](https://www.npmjs.com/package/mindsystem-cc)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/rolandtolnay/mindsystem?style=for-the-badge&logo=github&color=181717)](https://github.com/rolandtolnay/mindsystem)

<br>

```bash
npx mindsystem-cc
```

**Works on Mac, Windows, and Linux.**

<br>

![Mindsystem Install](assets/terminal.svg)

<br>

*"If you know clearly what you want, this WILL build it for you. No bs."*

*"I've done SpecKit, OpenSpec and Taskmaster — this has produced the best results for me."*

*"By far the most powerful addition to my Claude Code. Nothing over-engineered. Literally just gets shit done."*

<br>

**Trusted by engineers at Amazon, Google, Shopify, and Webflow.**

[Why I Built This](#why-i-built-this) · [How It Works](#how-it-works) · [Commands](#commands) · [Why It Works](#why-it-works)

</div>

---

## Why I Built This

I'm a solo developer. I don't write code — Claude Code does.

Other spec-driven development tools exist; BMAD, Speckit... But they all seem to make things way more complicated than they need to be (sprint ceremonies, story points, stakeholder syncs, retrospectives, Jira workflows) or lack real big picture understanding of what you're building. I'm not a 50-person software company. I don't want to play enterprise theater. I'm just a creative person trying to build great things that work.

So I built Mindsystem. The complexity is in the system, not in your workflow. Behind the scenes: context engineering, XML prompt formatting, subagent orchestration, state management. What you see: a few commands that just work.

The system gives Claude everything it needs to do the work *and* verify it. I trust the workflow. It just does a good job.

That's what this is. No enterprise roleplay bullshit. Just an incredibly effective system for building cool stuff consistently using Claude Code.

— **TÂCHES**

---

Vibecoding has a bad reputation. You describe what you want, AI generates code, and you get inconsistent garbage that falls apart at scale.

Mindsystem fixes that. It's the context engineering layer that makes Claude Code reliable. Describe your idea, let the system extract everything it needs to know, and let Claude Code get to work.

---

## Who This Is For

People who want to describe what they want and have it built correctly — without pretending they're running a 50-person engineering org.

---

## Getting Started

```bash
npx mindsystem-cc
```

That's it. Verify with `/ms:help` inside your Claude Code interface.

### Start Here

- If you already have `.planning/` in this repo: run `/ms:progress`.
- If you’re starting in an existing codebase (brownfield): run `/ms:map-codebase`, then `/ms:new-project`.
- Otherwise: run `/ms:new-project`.

### Staying Updated

Mindsystem evolves fast. Check for updates periodically:

```
/ms:whats-new       # See what changed since your version
/ms:update          # Update and show changelog
```

Or update directly via npm:

```bash
npx mindsystem-cc@latest
```

<details>
<summary><strong>Non-interactive Install (Docker, CI, Scripts)</strong></summary>

```bash
npx mindsystem-cc --global   # Install to ~/.claude/
npx mindsystem-cc --local    # Install to ./.claude/
```

Use `--global` (`-g`) or `--local` (`-l`) to skip the interactive prompt.

</details>

<details>
<summary><strong>Development Installation</strong></summary>

Clone the repository and run the installer locally:

```bash
git clone https://github.com/rolandtolnay/mindsystem.git
cd gsd
node bin/install.js --local
```

Installs to `./.claude/` for testing modifications before contributing.

</details>

### Recommended: Skip Permissions Mode

Mindsystem is designed for frictionless automation. Run Claude Code with:

```bash
claude --dangerously-skip-permissions
```

> [!TIP]
> This is how Mindsystem is intended to be used — stopping to approve `date` and `git commit` 50 times defeats the purpose.

<details>
<summary><strong>Alternative: Granular Permissions</strong></summary>

If you prefer not to use that flag, add this to your project's `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(date:*)",
      "Bash(echo:*)",
      "Bash(cat:*)",
      "Bash(ls:*)",
      "Bash(mkdir:*)",
      "Bash(wc:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(sort:*)",
      "Bash(grep:*)",
      "Bash(tr:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git status:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(git tag:*)"
    ]
  }
}
```

</details>

---

## How It Works

### 1. Start with an idea

```
/ms:new-project
```

The system asks questions. Keeps asking until it has everything — your goals, constraints, tech preferences, edge cases. You go back and forth until the idea is fully captured. Creates **PROJECT.md**.

### 1.5. Research the domain (optional)

```
/ms:research-project
```

Spawns parallel agents to investigate the domain — what's the standard stack, what features users expect, common architectural patterns, and pitfalls to avoid. Creates `.planning/research/` with ecosystem knowledge.

> Recommended for best results. Skip only if you need speed over thoroughness.

### 2. Define requirements

```
/ms:define-requirements
```

Scope what's v1, what's v2, and what's out of scope. Creates **REQUIREMENTS.md** with checkable requirements and traceability. Works with or without prior research.

### 3. Create roadmap

```
/ms:create-roadmap
```

Produces:
- **ROADMAP.md** — Phases from start to finish, mapped to requirements
- **STATE.md** — Living memory that persists across sessions

### 4. Plan and execute phases

```
/ms:plan-phase 1      # System creates atomic task plans
/ms:execute-phase 1   # Parallel agents execute all plans (includes verification)
```

Each phase breaks into 2-3 task plans. Each plan runs in a fresh subagent context — 200k tokens purely for implementation, zero degradation. Plans without dependencies run in parallel.

Checkpoints and resumption are handled automatically — if interrupted, run `/ms:execute-phase 1` again and it picks up where it left off.

If a phase verifies with gaps, close them with:

```
/ms:plan-phase 1 --gaps
/ms:execute-phase 1
```

### 5. Ship and iterate

```
/ms:audit-milestone 1.0.0        # (recommended) verify milestone before archiving
/ms:complete-milestone 1.0.0     # Archive v1, prep for v2
/ms:add-phase "Add admin dashboard"
/ms:insert-phase 2 "Fix critical auth bug"
```

Ship your MVP in a day. Add features. Insert hotfixes. The system stays modular — you're never stuck.

---

## Existing Projects (Brownfield)

Already have code? Start here instead.

### 1. Map the codebase

```
/ms:map-codebase
```

Spawns parallel agents to analyze your code. Creates `.planning/codebase/` with 7 documents:

| Document | Purpose |
|----------|---------|
| `STACK.md` | Languages, frameworks, dependencies |
| `ARCHITECTURE.md` | Patterns, layers, data flow |
| `STRUCTURE.md` | Directory layout, where things live |
| `CONVENTIONS.md` | Code style, naming patterns |
| `TESTING.md` | Test framework, patterns |
| `INTEGRATIONS.md` | External services, APIs |
| `CONCERNS.md` | Tech debt, known issues, fragile areas |

### 2. Initialize project

```
/ms:new-project
```

Same as greenfield, but the system knows your codebase. Questions focus on what you're adding/changing, not starting from scratch.

### 3. Continue as normal

From here, it's the same flow:
- `/ms:research-project` (optional) → `/ms:define-requirements` → `/ms:create-roadmap` → `/ms:plan-phase` → `/ms:execute-phase <phase>`

The codebase docs load automatically during planning. Claude knows your patterns, conventions, and where to put things.

---

## Why It Works

### Context Engineering

Claude Code is incredibly powerful *if* you give it the context it needs. Most people don't.

Mindsystem handles it for you:

| File | What it does |
|------|--------------|
| `PROJECT.md` | Project vision, always loaded |
| `research/` | Ecosystem knowledge (stack, features, architecture, pitfalls) |
| `REQUIREMENTS.md` | Scoped v1/v2 requirements with phase traceability |
| `ROADMAP.md` | Where you're going, what's done |
| `STATE.md` | Decisions, blockers, position — memory across sessions |
| `PLAN.md` | Atomic task with XML structure, verification steps |
| `SUMMARY.md` | What happened, what changed, committed to history |
| `todos/` | Captured ideas and tasks for later work |
| `adhoc/` | Small work executed mid-session with audit trail |

Size limits based on where Claude's quality degrades. Stay under, get consistent excellence.

### XML Prompt Formatting

Every plan is structured XML optimized for Claude:

```xml
<task type="auto">
  <name>Create login endpoint</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>
    Use jose for JWT (not jsonwebtoken - CommonJS issues).
    Validate credentials against users table.
    Return httpOnly cookie on success.
  </action>
  <verify>curl -X POST localhost:3000/api/auth/login returns 200 + Set-Cookie</verify>
  <done>Valid credentials return cookie, invalid return 401</done>
</task>
```

Precise instructions. No guessing. Verification built in.

### Subagent Execution

As Claude fills its context window, quality degrades. You've seen it: *"Due to context limits, I'll be more concise now."* That "concision" is code for cutting corners.

Mindsystem prevents this. Each plan is maximum 3 tasks. Each plan runs in a fresh subagent — 200k tokens purely for implementation, zero accumulated garbage.

| Task | Context | Quality |
|------|---------|---------|
| Task 1 | Fresh | ✅ Full |
| Task 2 | Fresh | ✅ Full |
| Task 3 | Fresh | ✅ Full |

No degradation. Walk away, come back to completed work.

### Atomic Git Commits

Each task gets its own commit immediately after completion:

```bash
abc123f docs(08-02): complete user registration plan
def456g feat(08-02): add email confirmation flow
hij789k feat(08-02): implement password hashing
lmn012o feat(08-02): create registration endpoint
```

> [!NOTE]
> **Benefits:** Git bisect finds exact failing task. Each task independently revertable. Clear history for Claude in future sessions. Better observability in AI-automated workflow.

Every commit is surgical, traceable, and meaningful.

### Modular by Design

- Add phases to current milestone
- Insert urgent work between phases
- Complete milestones and start fresh
- Adjust plans without rebuilding everything

You're never locked in. The system adapts.

---

## Commands

For full details and up-to-date usage, run `/ms:help` inside Claude Code (or read `commands/ms/help.md`).

### Setup

| Command | What it does |
|---------|--------------|
| `/ms:new-project` | Extract your idea through questions, create PROJECT.md |
| `/ms:research-project` | Research domain ecosystem (stacks, features, pitfalls) |
| `/ms:define-requirements` | Scope v1/v2/out-of-scope with checkable requirements |
| `/ms:create-roadmap` | Create roadmap with phases mapped to requirements |
| `/ms:map-codebase` | Map existing codebase for brownfield projects |

### Execution

| Command | What it does |
|---------|--------------|
| `/ms:plan-phase [N] [--gaps]` | Generate task plans for a phase (or close verification gaps) |
| `/ms:execute-phase <N>` | Execute all plans in phase (parallel, handles checkpoints) |
| `/ms:progress` | Where am I? What's next? |

### Verification

| Command | What it does |
|---------|--------------|
| `/ms:check-phase <N>` | Verify phase plans before execution (optional) |
| `/ms:verify-work [N]` | User acceptance test of phase or plan ¹ |
| `/ms:audit-milestone [version]` | Audit milestone completion before archiving |

### Milestones

| Command | What it does |
|---------|--------------|
| `/ms:complete-milestone <version>` | Ship it, prep next version |
| `/ms:discuss-milestone` | Gather context for next milestone |
| `/ms:new-milestone [name]` | Create new milestone with phases |
| `/ms:plan-milestone-gaps` | Create phases to close gaps from audit |

### Phase Management

| Command | What it does |
|---------|--------------|
| `/ms:add-phase <desc>` | Append phase to roadmap |
| `/ms:insert-phase <after> <desc>` | Insert urgent work between phases |
| `/ms:remove-phase <N>` | Remove future phase, renumber subsequent |
| `/ms:discuss-phase <N>` | Gather context before planning |
| `/ms:research-phase <N>` | Deep research for unfamiliar domains |
| `/ms:list-phase-assumptions <N>` | See what Claude assumes before correcting |

### Session

| Command | What it does |
|---------|--------------|
| `/ms:pause-work` | Create handoff file when stopping mid-phase |
| `/ms:resume-work` | Restore from last session |

### Utilities

| Command | What it does |
|---------|--------------|
| `/ms:add-todo [desc]` | Capture idea or task for later |
| `/ms:check-todos [area]` | List pending todos, select one to work on |
| `/ms:do-work <desc>` | Execute small discovered work (max 2 tasks) |
| `/ms:debug [desc]` | Systematic debugging with persistent state |
| `/ms:review-design [scope]` | Audit and improve design of implemented features |
| `/ms:simplify-flutter [scope]` | Simplify Flutter/Dart code for clarity and maintainability |
| `/ms:help` | Show all commands and usage guide |
| `/ms:update` | Update Mindsystem with changelog display |
| `/ms:whats-new` | See what changed since installed version |

<sup>¹ Contributed by reddit user OracleGreyBeard</sup>

---

## Troubleshooting

**Commands not found after install?**
- Restart Claude Code to reload slash commands
- Verify files exist in `~/.claude/commands/ms/` (global) or `./.claude/commands/ms/` (local)

**Commands not working as expected?**
- Run `/ms:help` to verify installation
- Re-run `npx mindsystem-cc` to reinstall

**Updating to the latest version?**
```bash
npx mindsystem-cc@latest
```

**Using Docker or containerized environments?**

If file reads fail with tilde paths (`~/.claude/...`), set `CLAUDE_CONFIG_DIR` before installing:
```bash
CLAUDE_CONFIG_DIR=/home/youruser/.claude npx mindsystem-cc --global
```
This ensures absolute paths are used instead of `~` which may not expand correctly in containers.

---

## Star History

<a href="https://star-history.com/#rolandtolnay/gsd&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=rolandtolnay/gsd&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=rolandtolnay/gsd&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=rolandtolnay/gsd&type=Date" />
 </picture>
</a>

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Claude Code is powerful. Mindsystem makes it reliable.**

</div>
