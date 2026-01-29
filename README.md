<div align="center">

# MINDSYSTEM

**A spec-driven development system for Claude Code that stays reliable over long sessions.**

*Based on [GSD](https://github.com/glittercowboy/get-shit-done) by TÂCHES (philosophy + early foundations, for now).*

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

[Why](#why-engineers-use-this) · [Install](#installation) · [Mental model](#mental-model) · [Playbooks](#playbooks) · [Why this works](#why-this-works) · [Config](#configuration) · [Commands](#command-index-one-liners) · [Troubleshooting](#troubleshooting)

</div>

---

## Why Engineers Use This

> *"I'm a solo developer. I don't write code — Claude Code does. Other spec-driven development tools exist; BMAD, Speckit... But they all seem to make things way more complicated than they need to be. I'm not a 50-person software company. I don't want to play enterprise theater. I'm just a creative person trying to build great things that work."*
>
> — **TÂCHES**, creator of the original [GSD](https://github.com/glittercowboy/get-shit-done)

Mindsystem is built for **Claude Code power users with an engineering mindset**: you want speed, but you also want **repeatability, reviewability, and quality gates**.

### The pitch (factual)

- **Stable quality over long sessions**: plan with you in the main chat; execute in fresh subagents (peak context quality).
- **Externalized project truth**: `.planning/` becomes the persistent source of “what we’re building” and “what we proved works”.
- **Diff-first control**: changes are checkpointed into commits *and* reviewable `.patch` files.
- **Hybrid deterministic + LLM judgment**: scripts do mechanics; models do trade-offs and code.

### Engineering-grade additions (everything after `v2.0.0`)

See `CHANGELOG.md` for the full story — these are the additions that matter for production apps.

- **Batched UAT with inline fixing**: `/ms:verify-work` presents tests in batches, then fixes failures immediately (inline or via fixer subagents) and drives re-test loops while context is fresh.
- **Mock-assisted validation**: `/ms:verify-work` can generate mock states for hard-to-reproduce scenarios (error/empty/role-based/etc.) without committing mock code.
- **Patch artifacts for review**: phase execution and UAT fixes generate `.patch` files you can diff/apply/discard (`{phase}-changes.patch`, `{phase}-uat-fixes.patch`, adhoc patches).
- **UI quality tooling**: `/ms:design-phase` produces UI/UX specs; `/ms:review-design` audits already-implemented UI and upgrades design quality systematically.
- **Script/API-backed research CLI**: `ms-lookup` provides fast, reliable research through APIs (Context7 docs, Perplexity deep research), with caching and JSON output (e.g. `ms-lookup docs react "useEffect cleanup"`).
- **Streamlined milestone management**: milestone completion consolidates decisions into `vX.Y-DECISIONS.md` and archives details so `.planning/` stays lean and future-referenceable.
- **Configurable code review gates**: reviewers run after phase execution and milestone audit, and produce separate commits; milestone-level structural reviews can be report-only so you decide what to fix and when.

---

## Mental Model

```
Main chat (you + Claude)          Fresh subagents (peak quality)
────────────────────────         ────────────────────────────────
1) Decide scope & intent   ───▶   4) Execute plans (commits)
2) (Optional) design spec         5) Post-exec code review (commit)
3) Plan small, verifiable work    6) Verify phase goals + generate .patch

Manual validation loop (still with you)
───────────────────────────────────────
7) /ms:verify-work  →  fix inline/subagent  →  re-test  →  uat-fixes .patch

Ship
────
8) /ms:audit-milestone  →  milestone review (report-only optional)  →  /ms:complete-milestone (decisions archived)
```

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

<details>
<summary><strong>Non-interactive install (Docker, CI, scripts)</strong></summary>

```bash
npx mindsystem-cc --global   # Install to ~/.claude/
npx mindsystem-cc --local    # Install to ./.claude/
```

</details>

<details>
<summary><strong>Staying updated</strong></summary>

Inside Claude Code:

```
/ms:whats-new
/ms:update
```

Or via npm:

```bash
npx mindsystem-cc@latest
```

</details>

<details>
<summary><strong>Development installation</strong></summary>

Clone the repository and run the installer locally:

```bash
git clone https://github.com/rolandtolnay/mindsystem.git
cd mindsystem
node bin/install.js --local
```

Installs to `./.claude/` for testing modifications before contributing.

</details>

---

## Playbooks

Replace `<N>` with the phase number you’re working on.

### New project (greenfield)

**When:** starting from scratch (new repo or blank slate).

**Run:**
```
/ms:new-project
/ms:research-project        # optional (recommended when domain is new)
/ms:define-requirements
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
```

**Key artifacts:**
- `.planning/PROJECT.md` (vision + constraints)
- `.planning/REQUIREMENTS.md` (checkable scope)
- `.planning/ROADMAP.md` + `.planning/STATE.md` (plan + project memory)

**Notes:**
- If phase 1 is UI-heavy, insert `/ms:design-phase 1` before `/ms:plan-phase 1`.

### Existing project (brownfield adoption)

**When:** you want Mindsystem to respect an existing codebase (structure, conventions, tests).

**Run:**
```
/ms:map-codebase
/ms:new-project
/ms:research-project        # optional (use for new domain areas)
/ms:define-requirements
/ms:create-roadmap
/ms:plan-phase 1
/ms:execute-phase 1
```

**Key artifacts:**
- `.planning/codebase/*` (captured conventions + structure)
- `.planning/PROJECT.md` / `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md`

### Add feature (existing product)

**When:** you already have `.planning/` and want to add a new feature with traceability.

**Run (typical):**
```
/ms:add-phase "Feature: <short name>"
/ms:discuss-phase <N>       # optional (lock intent before planning)
/ms:design-phase <N>        # optional (UI-heavy)
/ms:plan-phase <N>
/ms:execute-phase <N>
```

**Key artifacts:**
- `.planning/ROADMAP.md` updated with the new phase
- `.planning/phases/<N>-*/<N>-01-PLAN.md` + `*-SUMMARY.md`

**Notes:**
- Use `/ms:insert-phase <after> "..."` instead of `/ms:add-phase` when the work must happen *before* the next planned phase.

### Work on feature (plan → execute → verify-work loop)

**When:** you want engineering-grade confidence (implementation + review + manual UAT).

**Run:**
```
/ms:plan-phase <N>
/ms:execute-phase <N>
/ms:verify-work <N>
```

**Key artifacts:**
- `.planning/phases/<N>-*/<N>-changes.patch` (phase implementation diff)
- `.planning/phases/<N>-*/<N>-VERIFICATION.md` (phase goal verification report)
- `.planning/phases/<N>-*/<N>-UAT.md` + `<N>-uat-fixes.patch` (manual test log + fixes diff)

**Notes:**
- `/ms:verify-work` fixes issues in-session (inline or via subagent), commits fixes as `fix(<N>-uat): ...`, and asks you to re-test.
- For existing UI that “works but feels off”, add `/ms:review-design <scope>` to audit and improve design quality.

### Fix bug

**When:** something is broken and you want a structured investigation that survives `/clear`.

**Run:**
```
/ms:debug "Describe symptoms and what you observed"
```

**Then route the fix:**
- Small and urgent (1–2 tasks): `/ms:do-work "Fix <bug>"`
- Must happen before the next phase: `/ms:insert-phase <after> "Hotfix: <bug>"` → `/ms:plan-phase <N>` → `/ms:execute-phase <N>`
- Belongs in the current phase after verification gaps: `/ms:plan-phase <N> --gaps` → `/ms:execute-phase <N>`

### Scope change (what to use when)

**When:** you discover new work mid-stream.

**Use:**
- `/ms:add-phase "..."` — add non-urgent scope *after* current phases.
- `/ms:insert-phase <after> "..."` — insert urgent work *before* the next phase without rewriting the roadmap.
- `/ms:add-todo "..."` — capture a deferred task with context into `.planning/todos/`.
- `/ms:do-work "..."` — execute a small discovered fix now with lightweight artifacts and review.

### Milestone ship (finish feature = milestone completion)

**When:** you believe a version is shippable and want to lock it down cleanly.

**Run:**
```
/ms:audit-milestone 1.0.0
/ms:complete-milestone 1.0.0
/ms:new-milestone "v1.1"
```

**Key artifacts:**
- `.planning/milestones/v1.0-DECISIONS.md` (consolidated decisions; future reference)
- `.planning/milestones/v1.0-ROADMAP.md` / `v1.0-REQUIREMENTS.md` (archived detail; keeps active docs lean)

**Notes:**
- Milestone review can be **report-only** (e.g. Flutter structural review), so you keep control: create a dedicated quality phase or accept tech debt explicitly.

---

## Why This Works

- **Context rot is addressed structurally**: the “truth” lives in `.planning/` files (scope, decisions, plans, verification), not in a scrolling chat transcript.
- **Execution stays high-quality**: plans are intentionally small and run in fresh subagent contexts, so implementation doesn’t inherit long-chat drift.
- **Verification is first-class**: phase verification plus `/ms:verify-work` gives you a human-in-the-loop UAT loop with inline fixes (including mock-assisted states).
- **Review is engineer-friendly**: changes are checkpointed into commits and reviewable `.patch` files, and milestone review can be report-only when you want full control.
- **Milestones stay readable over time**: decisions are consolidated and archived so active planning docs don’t grow without bound.

---

## Configuration

Mindsystem stores project configuration in `.planning/config.json`.

### Code review

After `/ms:execute-phase` (and optionally `/ms:audit-milestone`), Mindsystem runs a reviewer that produces a **separate commit (guaranteed)** for easy inspection.

```json
{
  "code_review": {
    "adhoc": null,
    "phase": null,
    "milestone": null
  }
}
```

Values:

- `null`: use the default for that level (stack-aware when available).
- `"ms-code-simplifier"`: generic reviewer that improves clarity and maintainability.
- `"ms-flutter-simplifier"`: Flutter/Dart-specific simplifier with strong widget/Riverpod conventions.
- `"ms-flutter-reviewer"`: Flutter structural analysis (report-only; does not modify code).
- `"skip"`: disable review for that level.

Flutter expertise (built-in):

- **`ms-flutter-simplifier`**: applies pragmatic refactors while preserving behavior.
- **`ms-flutter-reviewer`**: milestone-level structural audit that produces an actionable report (engineer keeps control over fixes).
- **`flutter-senior-review` skill**: domain principles that raise review quality beyond generic “lint advice”.

---

## Command Index (One-Liners)

Canonical command API docs live in `/ms:help` (same content as `commands/ms/help.md`).

- `/ms:help` — show the full, authoritative command reference.
- `/ms:progress` — show where you are and what to run next.
- `/ms:new-project` — initialize `.planning/` and capture intent through questions.
- `/ms:map-codebase` — document an existing repo’s stack, structure, conventions, and tests for better plans.
- `/ms:research-project` — do domain research and save reusable findings into `.planning/research/`.
- `/ms:define-requirements` — turn intent into checkable v1/v2/out-of-scope requirements.
- `/ms:create-roadmap` — convert requirements into phases and persistent state.
- `/ms:discuss-phase <number>` — lock intent and constraints for a phase before planning.
- `/ms:design-phase <number>` — generate a UI/UX spec for UI-heavy work (flows, components, verification criteria).
- `/ms:review-design [scope]` — audit and improve design quality of existing UI/code.
- `/ms:research-phase <number>` — do deep research for niche/unknown phase domains.
- `/ms:list-phase-assumptions <number>` — show what Mindsystem assumes before planning/execution so you can correct it.
- `/ms:plan-phase [number] [--gaps]` — create small, verifiable PLAN.md files for the phase (or close verifier gaps).
- `/ms:check-phase <number>` — sanity-check phase plans before spending execution cycles.
- `/ms:execute-phase <phase-number>` — execute all unexecuted plans in the phase in fresh subagents (with review + verification).
- `/ms:verify-work [number]` — run manual UAT in batches (with mock support) and fix failures in-session.
- `/ms:debug [issue description]` — run a structured debugging workflow that persists across `/clear`.
- `/ms:do-work <description>` — execute a small discovered fix now with lightweight artifacts and review.
- `/ms:add-phase <description>` — append a new phase to the roadmap.
- `/ms:insert-phase <after> <description>` — insert urgent work between phases without rewriting the roadmap.
- `/ms:remove-phase <number>` — delete a future phase and renumber subsequent phases.
- `/ms:audit-milestone [version]` — audit milestone completion and surface gaps/tech debt.
- `/ms:complete-milestone <version>` — archive the milestone, consolidate decisions, and prepare for the next version.
- `/ms:new-milestone [name]` — start the next milestone with fresh scope and phases.
- `/ms:plan-milestone-gaps` — turn audit gaps into a concrete set of fix phases.
- `/ms:add-todo [description]` — capture a deferred task with context into `.planning/todos/`.
- `/ms:check-todos [area]` — list pending todos and route one into work/planning.
- `/ms:whats-new` — show what changed since your installed version.
- `/ms:update` — update Mindsystem and show the changelog.

---

## Troubleshooting

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

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Claude Code is powerful. Mindsystem makes it reliable.**

</div>
