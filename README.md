<div align="center">

# MINDSYSTEM

**A meta-prompting and context engineering system for Claude Code.**

Every piece of work makes the next one better. Mindsystem structures your Claude Code sessions into plannable, executable, verifiable phases — and compounds what it learns into persistent knowledge files that survive `/clear`. The result: context rot stops being the bottleneck, and quality stays consistent from phase 1 to phase 20.

```bash
npx mindsystem-cc
```

[![npm version](https://img.shields.io/npm/v/mindsystem-cc?style=flat-square&logo=npm&logoColor=white&color=CB3837)](https://www.npmjs.com/package/mindsystem-cc)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

<br>

![Mindsystem Install](assets/terminal.svg)

<br>

[How It Works](#how-it-works) · [Walkthrough](#end-to-end-walkthrough) · [Features](#features) · [Quick Start](#quick-start) · [Config](#configuration) · [Commands](#command-reference) · [Troubleshooting](#troubleshooting)

</div>

---

## How It Works

```
  new-milestone          Define what to build next
       │
  create-roadmap         Derive requirements, map to phases
       │
       ▼
  ┌─────────────────┐
  │  Per Phase:      │
  │                  │
  │  discuss-phase ──┤  (optional) Lock intent, validate assumptions
  │  design-phase  ──┤  (optional) Generate mockups, pick direction
  │  research-phase ─┤  (optional) External docs, codebase patterns, community practices
  │                  │
  │  plan-phase ─────┤  Break into context-budgeted plans
  │  execute-phase ──┤  Fresh subagents run each plan autonomously
  │  verify-work ────┤  Manual acceptance tests, inline fixes
  │                  │
  │  ← repeat ───────┘
  │
  audit-milestone        Check requirements coverage, surface tech debt
       │
  complete-milestone     Archive, evolve PROJECT.md, clean slate
```

Each phase gets its own preparation depth. A database migration might skip straight to planning. A user-facing feature might warrant discussion, design mockups, and research first. You pick the depth; the system adapts.

Execution happens in fresh subagent contexts — each plan gets up to 200k tokens of headroom at peak quality, regardless of how much planning you did in the main conversation.

---

## End-to-End Walkthrough

### 1. New Milestone

```
/ms:new-milestone
```

Claude reads your project history — tech debt, deferred requirements, validated decisions — and surfaces strategic directions. You articulate the vision. The output is a `MILESTONE-CONTEXT.md` that grounds everything downstream.

This is dream extraction: Claude acts as product owner, helping you think through what to build next by asking the right questions rather than prescribing answers.

### 2. Create Roadmap

```
/ms:create-roadmap
```

Claude derives requirements from your milestone context, assigns each a `REQ-ID`, and maps them to phases with success criteria. You approve scope and phase grouping.

Requirements define what must be TRUE when you ship, not what to build. This goal-backward framing means verification can check outcomes, not task completion.

**Creates:** `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, phase directories.

### 3. Discuss Phase (optional, recommended)

```
/ms:discuss-phase 1
```

The most impactful human moment in the pipeline. Claude loads milestone context, feature knowledge files, and competitor research — then surfaces its assumptions with confidence levels. You validate intent, make tradeoff decisions, correct misunderstandings.

Everything downstream flows from decisions made here. The assumption-based briefing catches misalignment before a single line of code is written.

**Creates:** `CONTEXT.md` with vision, essentials, and reasoning-backed decisions.

### 4. Design Phase (optional)

```
/ms:design-phase 1
```

Claude generates parallel HTML/CSS mockup variants and a side-by-side comparison page that opens in your browser. You pick a direction, iterate with feedback.

The output is a `DESIGN.md` with exact design tokens — hex colors, px spacing, font weights — not descriptions of what things should look like. Implementable, not interpretive.

### 5. Research Phase (optional)

```
/ms:research-phase 1
```

Three parallel agents investigate simultaneously: one queries external documentation through Perplexity and Context7, one analyzes your codebase for existing patterns, one surveys community best practices. Claude synthesizes findings into `RESEARCH.md` with confidence levels and source attribution.

You resolve library conflicts if any arise. Otherwise, this phase runs with minimal input.

### 6. Plan Phase

```
/ms:plan-phase 1
```

Claude breaks the phase into tasks, groups them into plans targeting 25-45% of the context budget. Plans are pure markdown — no YAML frontmatter, no XML containers. The plan IS the executable prompt, with ~90% actionable content and ~10% structure.

Independent plans are grouped into waves for parallel execution. A risk score (0-100) flags complex plans for optional verification before you commit to running them.

You approve the plan structure and can adjust granularity.

**Creates:** `PLAN.md` files, `EXECUTION-ORDER.md`.

### 7. Execute Phase

```
/ms:execute-phase 1
```

Fully autonomous. Each plan runs in a fresh subagent with the full context window available. Goal-backward verification checks that the phase achieved its intended outcome — not that tasks were marked complete.

Configurable code review produces separate commits for review changes. Patch files are generated for manual inspection.

After execution, knowledge consolidation updates subsystem-scoped knowledge files. Future phases that touch the same subsystems start with accumulated context about decisions made, patterns established, and pitfalls encountered.

**Creates:** `SUMMARY.md`, `VERIFICATION.md`, `.patch` files, knowledge file updates.

### 8. Verify Work

```
/ms:verify-work 1
```

The quality gate. You run manual acceptance tests presented in batches of 4. Claude fixes issues inline or via subagent, then asks you to re-test until passing.

For hard-to-test scenarios — error states, loading screens, role-based views — mock generation creates temporary inline states without shipping test infrastructure.

Fixes compound into knowledge files through automatic consolidation. This is where edge cases, UI tweaks, and small bugs get caught before moving on.

**Creates:** `UAT.md`, `uat-fixes.patch`, knowledge file updates.

### 9. Repeat

Run steps 3-8 for each phase. Pick the preparation depth each phase needs.

### 10. Audit Milestone

```
/ms:audit-milestone
```

Claude checks requirements coverage against `REQ-IDs`, spawns an integration checker for cross-phase wiring, aggregates untested UAT assumptions, and consolidates tech debt into `TECH-DEBT.md` with severity tiers and `TD-IDs`.

Optional code review with quality-phase decisions for high-impact findings — you decide what gets fixed vs. accepted as debt.

### 11. Complete Milestone

```
/ms:complete-milestone
```

Full `PROJECT.md` evolution: validates core value proposition, moves shipped requirements to validated, triages deferred items. Archives the milestone to `.planning/milestones/{name}/` with the roadmap, requirements, and phase summaries.

Updates `MILESTONES.md` with stats and accomplishments. Clean slate for the next `/ms:new-milestone`.

---

## Features

### Knowledge Compounding

The core differentiator. Subsystem-scoped knowledge files are enriched after every phase. Execute-phase consolidates implementation decisions. Verify-work compounds fixes and edge cases. `/ms:compound` catches out-of-pipeline work — direct Claude sessions, manual edits, merged branches.

The effect accumulates: phase 1 starts from scratch; phase 10 starts with a knowledge base that captures what works, what failed, and why.

### Context Budget Management

Plans target 25-45% of the context window. Execution runs in fresh subagents — no inherited drift from long planning conversations. The 50% rule ensures plans complete before quality degrades.

Orchestration metadata (wave grouping, dependencies) lives in `EXECUTION-ORDER.md`, separate from plans. Plans carry only what the executor needs: context, changes, verification, must-haves.

### Built-in Code Review

Configurable per tier — adhoc, phase, or milestone. Runs after execution and produces separate commits for inspection. Ships with structural analysis (`ms-code-reviewer`) and clarity-focused simplification (`ms-code-simplifier`), but you can point any tier at your own custom reviewer agent via `.planning/config.json`.

### Structured Debugging

`/ms:debug` creates investigation state that persists across `/clear`. Scientific method: gather evidence, form hypotheses, test. Resume any debug session by running `/ms:debug` with no arguments. Archives resolved issues to `.planning/debug/resolved/`.

### Adhoc Execution

Work that's too coherent for a todo but too small for formal phase planning. `/ms:adhoc` reads existing knowledge files, generates a standard-format plan, executes, reviews, and consolidates learnings — all in one context. Accepts Linear ticket IDs, todo file paths, or plain descriptions.

### Design Mockups

`/ms:design-phase` generates parallel HTML/CSS variant mockups with a side-by-side comparison page. Design tokens in the output are exact values (hex, px, font-weight), not descriptions. `/ms:review-design` audits existing screens using screenshots for retroactive design improvement.

### Project Health

`/ms:doctor` runs 10 health checks: subsystem vocabulary, directory structure, milestone naming, knowledge files, CLI wrappers, API keys, version freshness. Fixes are applied in dependency order with atomic commits. Safe to run repeatedly.

### Smart Routing

`/ms:progress` reads project state and tells you what to run next. Visual progress bar, recent work summary, pending todos, active debug sessions. Reconstructs `STATE.md` from artifacts if it's missing. Also detects available updates.

### Deferred Requirements

Requirements you want but haven't shipped track in `PROJECT.md` with origin milestone and deferral reason. `complete-milestone` triages them before archiving; `create-roadmap` consumes them as candidates for new milestones. Nothing falls through the cracks.

### Task Capture

`/ms:add-todo` with Linear-inspired metadata: priority (1-4), estimate (XS-XL), inferred subsystem. Todos live as flat files in `.planning/todos/`. Address them later via `/ms:adhoc`, which reads the problem description, executes the work, and moves the todo to `done/`.

### Codebase Mapping

`/ms:map-codebase` spawns 4 parallel agents producing 7 structured documents: stack, architecture, conventions, testing, integrations, directory structure, and concerns. Use on brownfield projects so Mindsystem respects your existing patterns.

---

## Quick Start

### New project

```
/ms:new-project
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
/ms:verify-work 1
```

You'll get `.planning/` with your project vision, requirements, roadmap, and the first phase implemented with commits, patch files, and knowledge files.

### Existing project

```
/ms:new-project
/ms:map-codebase
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
```

Codebase mapping produces 7 documents covering your stack, conventions, and architecture. All downstream planning and execution respects what's already there.

**Returning after a break?** Run `/ms:progress` — it shows where you left off and what to do next.

---

## Configuration

Mindsystem stores project config in `.planning/config.json`. Run `/ms:config` to set up code reviewers, mockup preferences, gitignore patterns, and git remote.

### Code review tiers

```json
{
  "code_review": {
    "adhoc": null,
    "phase": null,
    "milestone": null
  }
}
```

| Value | Behavior |
| ----- | -------- |
| `null` | No reviewer (default) |
| `"ms-code-reviewer"` | Structural analysis — architectural and design issues |
| `"ms-code-simplifier"` | Clarity-focused — improves readability and maintainability |
| `"skip"` | Disable review for that tier |

---

## Command Reference

Full docs live in `/ms:help`.

| Command | What it does |
| ------- | ------------ |
| `/ms:help` | Show the full command reference |
| `/ms:progress` | Show where you are and what to run next |
| `/ms:new-project` | Initialize `.planning/` and capture project intent |
| `/ms:config` | Configure code reviewers, mockups, gitignore, git remote |
| `/ms:map-codebase` | Document existing repo's stack, structure, and conventions |
| `/ms:research-project` | Domain research saved to `.planning/research/` |
| `/ms:create-roadmap` | Define requirements and create phases mapped to them |
| `/ms:new-milestone [name]` | Discover what to build next, start new milestone |
| `/ms:discuss-phase <number>` | Product-informed collaborative thinking before planning |
| `/ms:design-phase <number>` | Generate UI/UX spec and optional HTML mockups |
| `/ms:review-design [scope]` | Audit and improve existing UI quality |
| `/ms:research-phase <number>` | Deep research for niche phase domains |
| `/ms:plan-phase [number]` | Create context-budgeted plans with optional risk scoring |
| `/ms:execute-phase <number>` | Run all unexecuted plans in fresh subagents |
| `/ms:verify-work [number]` | Batched manual UAT with inline fixes |
| `/ms:debug [description]` | Structured debugging that survives `/clear` |
| `/ms:adhoc <description>` | Knowledge-aware execution for discovered work |
| `/ms:compound [input]` | Compound out-of-pipeline changes into knowledge files |
| `/ms:add-phase <description>` | Append a new phase to the roadmap |
| `/ms:insert-phase <after> <description>` | Insert urgent work between phases |
| `/ms:remove-phase <number>` | Delete a future phase and renumber |
| `/ms:add-todo [description]` | Capture a task with priority, estimate, subsystem |
| `/ms:audit-milestone [name]` | Audit completion and surface gaps |
| `/ms:complete-milestone [name]` | Archive milestone and prepare for next |
| `/ms:doctor` | Health check and fix project configuration |
| `/ms:update` | Check for and install latest version |
| `/ms:release-notes` | Show full release notes with update status |

---

## Updating

Inside Claude Code:

```
/ms:update
```

Check what changed:

```
/ms:release-notes
```

From your terminal:

```bash
npx mindsystem-cc@latest
```

---

## Troubleshooting

**Commands not found after install?**

- Restart Claude Code to reload slash commands.
- Check that files exist in `~/.claude/commands/ms/` (global) or `./.claude/commands/ms/` (local).

**Commands not working as expected?**

- Run `/ms:help` to verify installation.
- Re-run `npx mindsystem-cc` to reinstall.

**Outdated project structure after a major update?**

- Run `/ms:doctor` to detect and fix stale artifacts, missing config fields, and directory structure changes between versions.

**Updating to the latest version?**

```bash
npx mindsystem-cc@latest
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
