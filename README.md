<div align="center">

# MINDSYSTEM

**A lightweight, opinionated spec-driven development system for Claude Code.**

*Based on [GSD](https://github.com/glittercowboy/get-shit-done) by TÂCHES.*

**Solves context rot — the quality degradation that happens as Claude fills its context window.**

[![npm version](https://img.shields.io/npm/v/mindsystem-cc?style=flat-square&logo=npm&logoColor=white&color=CB3837)](https://www.npmjs.com/package/mindsystem-cc)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

<br>

```bash
npx mindsystem-cc
```

**Works on macOS, Windows, and Linux.**

<br>

![Mindsystem Install](assets/terminal.svg)

<br>

[Why](#why-this-exists) · [Install](#installation) · [Quickstart](#quickstart) · [Workflows](#common-workflows) · [Commands](#command-index) · [Troubleshooting](#troubleshooting--advanced)

</div>

---

## Why This Exists

> *"I'm a solo developer. I don't write code — Claude Code does. Other spec-driven development tools exist; BMAD, Speckit... But they all seem to make things way more complicated than they need to be. I'm not a 50-person software company. I don't want to play enterprise theater. I'm just a creative person trying to build great things that work."*
>
> — **TÂCHES**, creator of the original [GSD](https://github.com/glittercowboy/get-shit-done)

Mindsystem is a fork of GSD that shares the same “keep it simple” philosophy, but is tuned for a specific audience: **Claude Code power users who prefer to design in plain English**.

You already understand architecture, trade-offs, and quality. Mindsystem focuses on turning your intent into stable outputs over long sessions: it externalizes project memory into files and pushes execution into fresh contexts so quality stays high.

## Philosophy

### Opinionated, modular commands
Mindsystem avoids mega-flows. Commands stay small, explicit, and composable — you pick the depth you need for this task (quick fix vs. new feature vs. UI-heavy system).

### Collaboration stays in the main chat
Planning and back-and-forth happen with you. Subagents are for autonomous execution, not for hiding key decisions or reasoning.

### Scripts for mechanics, prompts for judgment
Deterministic chores live in scripts; language models do what they’re good at: interpreting intent, making trade-offs, and writing code you can review.

## What's New (Fork Highlights)

- **Quality-control pipeline**: execution produces reviewable artifacts and verification steps.
- **Design phase**: `/ms:design-phase` generates a UI/UX spec (flows, components, wireframes) before implementation.
- **Research tooling**: `scripts/ms-lookup/` can be used standalone or inside workflows.
- **Enhanced verification**: better UAT batching and debugging support when gaps are found.
- **Automatic code review**: after phase execution (and optionally at milestone completion), a code review agent reviews code for clarity and maintainability. Stack-aware (Flutter gets specialized guidance) with generic fallback. Produces separate commit for easy review. See [Configuration](#configuration).
- **Skills distribution**: bundled skills (like `flutter-senior-review`) are installed to `~/.claude/skills/` and provide domain-specific expertise for code reviews and audits.

---

## Installation

```bash
npx mindsystem-cc
```

This installs Mindsystem slash commands into `~/.claude/` (global) or `./.claude/` (local).

After install, restart Claude Code (so it reloads slash commands) and verify with:

```
/ms:help
```

### Non-interactive install (Docker, CI, scripts)

```bash
npx mindsystem-cc --global   # Install to ~/.claude/
npx mindsystem-cc --local    # Install to ./.claude/
```

Use `--global` (`-g`) or `--local` (`-l`) to skip the interactive prompt.

### Staying updated

Inside Claude Code:

```
/ms:whats-new
/ms:update
```

Or via npm:

```bash
npx mindsystem-cc@latest
```

### Development installation

Clone the repository and run the installer locally:

```bash
git clone https://github.com/rolandtolnay/mindsystem.git
cd mindsystem
node bin/install.js --local
```

Installs to `./.claude/` for testing modifications before contributing.

---

## Quickstart

### New project (greenfield MVP)

```
/ms:new-project
/ms:research-project
/ms:define-requirements
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
```

At a high level: `/ms:new-project` captures intent and creates the project workspace, `/ms:research-project` pulls in ecosystem knowledge and common pitfalls, `/ms:define-requirements` turns “what you want” into checkable scope, and `/ms:create-roadmap` converts that scope into phases plus persistent project memory. `/ms:plan-phase` then breaks a phase into small, verifiable tasks, and `/ms:execute-phase` runs those tasks in fresh subagent contexts with verification and reviewable artifacts. The payoff is less context rot, fewer forgotten decisions, and more repeatable output than “just keep chatting until it works”.

`/ms:research-project` is part of the default flow. Skip it only when you already know the domain and stack choices.

### Existing project (brownfield)

```
/ms:map-codebase
/ms:new-project
/ms:research-project
/ms:define-requirements
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
```

`/ms:map-codebase` is the “adoption” step: it teaches Mindsystem your repo’s conventions, structure, and testing patterns so plans land in the right places.

---

## Common Workflows

Replace `<N>` with the phase you’re working on (usually `1` when you’re starting).

### 1) Ship an MVP (fast, structured)

```
/ms:new-project
/ms:define-requirements
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
```

Use when you already know the shape of the product and want momentum with guardrails (planning + verification).

### 2) Add a feature to an existing codebase

```
/ms:map-codebase
/ms:new-project
/ms:discuss-phase <N>
/ms:plan-phase <N>
/ms:execute-phase <N>
```

Use `/ms:discuss-phase` when you have strong opinions about UX/behavior and want them captured before planning.

### 3) Fix a bug / hotfix with traceability

```
/ms:debug "Describe the bug and what you observed"
/ms:insert-phase <after> "Hotfix: <short description>"
/ms:plan-phase <N>
/ms:execute-phase <N>
```

If execution verifies with gaps:

```
/ms:plan-phase <N> --gaps
/ms:execute-phase <N>
```

### 4) Complex UI/UX feature (design first)

```
/ms:discuss-phase <N>
/ms:design-phase <N>
/ms:plan-phase <N>
/ms:execute-phase <N>
/ms:verify-work <N>
```

Use when the UI is the product (new interaction patterns, multiple screens, hard edge cases). Design is optional; this is the “pay the thinking cost up front” path.

`/ms:verify-work` guides you through manual UI verification (UAT). When issues are found, it can spin up subagents to investigate and fix them, then re-present the checks until you’re satisfied.

### 5) Milestone-driven iteration in an existing product

```
/ms:audit-milestone 1.0.0
/ms:complete-milestone 1.0.0
/ms:new-milestone "v1.1"
/ms:add-phase "Next feature"
```

Use when you’re shipping continuously: audit what’s “actually done”, archive cleanly, then start the next milestone with explicit phases.

---

## Appendix: How Mindsystem Works (High-Level)

### Context rot → external memory
Long Claude Code sessions degrade. Mindsystem pushes project “truth” into files that persist across sessions (vision, requirements, roadmap, state, plans), so you’re not relying on chat history as the only source of reality.

### Fresh contexts for execution
Planning and discussion happen with you; execution happens in fresh subagent contexts, so implementation doesn’t inherit the accumulated noise of a long conversation.

### Small plans + verification loops
Mindsystem keeps plans intentionally small and explicit, with concrete “verify” criteria. When verification finds gaps, you can generate targeted follow-up work (e.g. `/ms:plan-phase <N> --gaps`). For UI-heavy work, `/ms:verify-work` guides manual UAT and can use subagents to investigate and fix issues as they’re found.

If you want the authoritative, up-to-date guide, run `/ms:help` inside Claude Code (or read `commands/ms/help.md`).

---

## Command Index

Commands are grouped by workflow domain (start → plan → execute → ship → maintain).

| Command | What it does |
|--------:|--------------|
| `/ms:help` | Show the full command reference and usage guide. |
| `/ms:progress` | Show where you are and what’s next. |
| `/ms:new-project` | Initialize `.planning/` and capture project intent. |
| `/ms:map-codebase` | Analyze an existing repo and capture conventions + structure. |
| `/ms:research-project` | Research the overall domain ecosystem (optional). |
| `/ms:define-requirements` | Scope v1/v2/out-of-scope requirements with checkboxes. |
| `/ms:create-roadmap` | Create roadmap phases and persistent state tracking. |
|  |  |
| `/ms:discuss-phase <N>` | Gather context before planning a phase. |
| `/ms:list-phase-assumptions <N>` | Show what Claude assumes before planning/execution. |
| `/ms:research-phase <N>` | Deep research for unfamiliar or niche phase domains. |
| `/ms:design-phase <N>` | Produce a UI/UX design spec for a phase. |
| `/ms:plan-phase [N] [--gaps]` | Generate task plans for a phase (or close gaps). |
| `/ms:check-phase <N>` | Verify phase plans before execution (optional). |
|  |  |
| `/ms:execute-phase <N>` | Execute all plans in a phase (parallel, checkpointed). |
| `/ms:verify-work [N]` | User acceptance test of a phase or a plan. |
| `/ms:debug [desc]` | Run a systematic debugging workflow with persistent state. |
| `/ms:review-design [scope]` | Audit and improve design quality of implemented features. |
| `/ms:do-work <desc>` | Execute small discovered work (kept intentionally small). |
|  |  |
| `/ms:add-phase <desc>` | Append a phase to the roadmap. |
| `/ms:insert-phase <after> <desc>` | Insert urgent work between phases (renumbers). |
| `/ms:remove-phase <N>` | Remove a future phase and renumber subsequent phases. |
|  |  |
| `/ms:discuss-milestone` | Gather context for the next milestone. |
| `/ms:new-milestone [name]` | Create a new milestone with phases. |
| `/ms:audit-milestone [version]` | Audit milestone completion before archiving. |
| `/ms:complete-milestone <version>` | Archive the milestone and prep the next version. |
| `/ms:plan-milestone-gaps` | Create phases to close gaps from a milestone audit. |
|  |  |
| `/ms:add-todo [desc]` | Capture an idea/task for later. |
| `/ms:check-todos [area]` | List pending todos and pick one to work on. |
| `/ms:whats-new` | See what changed since your installed version. |
| `/ms:update` | Update Mindsystem and show the changelog. |

---

## Configuration

Mindsystem stores project configuration in `.planning/config.json`. This file is created when you initialize a project and can be edited to customize behavior.

### Code Review

After phase execution (and optionally at milestone completion), Mindsystem runs a code review agent to review changes for clarity and maintainability. Configure this in `config.json`:

```json
{
  "code_review": {
    "phase": null,
    "milestone": null
  }
}
```

**Configuration levels:**

| Level | When it runs | Config key |
|-------|--------------|------------|
| Phase | After `/ms:execute-phase` completes | `code_review.phase` |
| Milestone | After `/ms:audit-milestone` completes | `code_review.milestone` |

**Available values for each level:**

| Value | Behavior |
|-------|----------|
| `null` (default) | Uses `ms-code-simplifier` — generic reviewer for any language |
| `"ms-flutter-simplifier"` | Flutter/Dart-specific reviewer with Riverpod and widget patterns |
| `"ms-flutter-reviewer"` | Flutter/Dart structural analysis (reports only, does not modify code). When used at milestone level, offers binary choice: create quality phase or accept as tech debt. |
| `"skip"` | Skip code review at this level |
| `"my-custom-agent"` | Use any custom agent you've defined |

**Example: Flutter project with phase review only**
```json
{
  "code_review": {
    "phase": "ms-flutter-simplifier",
    "milestone": "skip"
  }
}
```

**Example: Skip all code review**
```json
{
  "code_review": {
    "phase": "skip",
    "milestone": "skip"
  }
}
```

Code review runs automatically and creates a separate commit for easy review. Changes are purely cosmetic (clarity, consistency) — functionality is preserved.

---

## Troubleshooting & Advanced

**Commands not found after install?**
- Restart Claude Code to reload slash commands.
- Verify files exist in `~/.claude/commands/ms/` (global) or `./.claude/commands/ms/` (local).

**Commands not working as expected?**
- Run `/ms:help` to verify installation.
- Re-run `npx mindsystem-cc` to reinstall.

**Updating to the latest version?**
```bash
npx mindsystem-cc@latest
```

<details>
<summary><strong>Claude Code permissions (optional)</strong></summary>

If you use Claude Code’s permissions allowlist, you can add a small set of shell commands Mindsystem commonly needs. Example:

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

**Using Docker or containerized environments?**

If file reads fail with tilde paths (`~/.claude/...`), set `CLAUDE_CONFIG_DIR` before installing:
```bash
CLAUDE_CONFIG_DIR=/home/youruser/.claude npx mindsystem-cc --global
```
This ensures absolute paths are used instead of `~` which may not expand correctly in containers.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Claude Code is powerful. Mindsystem makes it reliable.**

</div>
