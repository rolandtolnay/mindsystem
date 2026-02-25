---
name: ms-meta
description: Instant Mindsystem expert. Use when working on Mindsystem, asking how it works, or describing/discussing improvements to commands, agents, workflows, or the framework itself.
---

<objective>
Provides instant expertise about the Mindsystem framework for meta-discussions, diagnostics, and planning Mindsystem changes. Use when working on Mindsystem itself, diagnosing Mindsystem issues, or asking how Mindsystem works.
</objective>

<behavior>
**This is a domain knowledge skill, not a Q&A assistant.**

When invoked:
1. **Absorb** the essential knowledge below as context
2. **Continue** with your original task, informed by this Mindsystem expertise
3. **Do NOT** treat the invocation arguments as a question to answer

The arguments passed to this skill describe WHY you need Mindsystem knowledge. Use that context to apply the knowledge appropriately, but return to your primary task.

**Example:** If invoked during a CLI tool design task with "need to understand subagent patterns", absorb the subagent knowledge, then continue designing the CLI tool — don't write an essay about subagent patterns.
</behavior>

<essential_knowledge>

<what_mindsystem_is>
Mindsystem is a meta-prompting and context engineering system for Claude Code that solves **context rot** — the quality degradation that happens as Claude fills its context window.

**Core insight:** Claude's quality degrades predictably:
- 0-30% context: Peak quality
- 30-50%: Good quality
- 50-70%: Degrading ("I'll be more concise now" = cutting corners)
- 70%+: Poor quality

**The 50% rule:** Plans should complete within ~50% context usage. Stop BEFORE quality degrades, not at context limit.

**Solution:** Budget-aware consolidation. The orchestrator proposes plan boundaries using weight heuristics (target 25-45%) with user collaboration. The plan-writer validates structurally (file conflicts, circular deps) but follows proposed grouping. Each plan executes in a fresh subagent with 200k tokens purely for implementation. Plans use pure markdown — no XML containers, no YAML frontmatter — to maximize the ratio of actionable content to structural overhead.
</what_mindsystem_is>

<philosophy>

**North Star: Quality x Speed.** Mindsystem's purpose is producing output that matches the user's vision completely in the shortest time possible. The ideal: user articulates their vision, Mindsystem extracts all missing context through questions, then generates perfect output on the first try. Every workflow step exists on a spectrum between two poles:
- **Quality gates** — Steps that meaningfully improve output (code review catches real bugs, verification catches real mismatches). Worth their latency cost.
- **Engineering noise** — Steps that add overhead without meaningfully influencing output (overly complicated prompts, redundant checks, ceremony that wastes tokens). Must be eliminated.

The critical judgment when evaluating any Mindsystem feature: **does this step's quality improvement justify its time cost?** If a step doesn't measurably increase the chance of correct output, it's noise — remove it regardless of how reasonable it sounds in theory. Conversely, if removing a step causes regressions, it's a quality gate — keep it even if it adds latency.

**Modularity over bundling.** Commands stay small, explicit, and composable. Avoid mega-flows. Users pick the depth they need (quick fix vs. new feature vs. UI-heavy system). Each command has a clear purpose — no consulting documentation to understand which to use. When in doubt, keep commands separate rather than unifying into one large command.

**Main context for collaboration.** Planning, discussion, and back-and-forth happen with the user in the main conversation. Subagents are for autonomous execution, not for hiding key decisions or reasoning. This preserves:
- Conversational iteration during planning
- User ability to question, redirect, and contribute
- Visibility into Claude's thinking

Reserve subagents for autonomous execution work, not collaborative thinking.

**Script + prompt hybrid.** Deterministic chores live in scripts (`scripts/`); language models do what they're good at: interpreting intent, making trade-offs, and writing code. Examples: STATE.md updates via `ms-tools update-state`, execution order validation via `ms-tools validate-execution-order`, patch generation via `ms-tools generate-phase-patch`. Prompts handle reasoning and decisions; scripts handle mechanical operations.

**User as collaborator.** Trust that users can contribute meaningfully. Maintain:
- **Control** — User decides when to proceed, what to skip
- **Granularity** — Separate commands for research, requirements, planning, execution
- **Transparency** — No hidden delegation or background orchestration

**Minimal ceremony.** No process overhead that doesn't improve output — sprint ceremonies, RACI matrices, stakeholder management, time estimates. This applies regardless of team size. User is the visionary. Claude is the builder.

**Plans ARE prompts.** PLAN.md is not a document that gets transformed — it IS the executable prompt. Plans optimize for a single intelligent reader executing in one context: ~90% actionable content (Context, Changes, Verification, Must-Haves), ~10% structure. Orchestration metadata (wave grouping, dependencies) lives separately in EXECUTION-ORDER.md, not in individual plans.

**Claude automates everything.** If it has CLI/API, Claude does it. Human interaction points exist only for verification (human confirms visual/UX), decisions (human chooses direction), and unavoidable manual steps (no API exists). These are handled dynamically at runtime, not pre-planned into execution.

**Goal-backward planning.** Don't ask "what should we build?" — ask "what must be TRUE for the goal to be achieved?" This produces verifiable requirements, not vague task lists.

**Dream extraction, not requirements gathering.** Discovery phases (new-milestone, discuss-phase, new-project) act as an experienced product owner and business analyst working with a visionary leader. The user often needs guidance articulating ideas, thinking through the right questions, confronting constraints, and grounding abstractions into what's buildable. The system amplifies everything in the user's head through collaborative dialogue — not forms or checklists. Make the user excited to talk about their ideas, then transform that dialogue into structured requirements and specification.

**Artifact discipline.** Every artifact earns its place; every line earns its place within it. No redundant information across artifacts — if data exists in one canonical source, don't duplicate it elsewhere. Relevance is measured by consumption: who reads this, when, and what decision does it inform? Posterity is valid only when non-deducible from other existing sources. Planning artifacts (ROADMAP.md, REQUIREMENTS.md) are milestone-scoped and recreated fresh each milestone — history lives in purpose-built archives and MILESTONES.md, not in cumulative documents that grow unboundedly.
</philosophy>

<context_engineering>
**The primary constraint is context quality.** LLM output quality correlates directly with input quality. Every unnecessary token — verbose instructions, inline scripts, redundant explanations, orchestration metadata mixed with execution content — accelerates degradation. The goal: complete work before quality drops.

**Decision principle: minimize context at equal output.** When two approaches produce equivalent results, choose the one consuming less context. This applies to everything: prompt design, workflow steps, feature scope, and whether a feature should be extended or simplified.

**Instruction-following budget (~150-250).** Reasoning models follow ~150-250 behavioral instructions before sharp threshold decay; standard frontier models show linear decay from much earlier; smaller models show exponential decay (IFScale, July 2025). At 500 instructions, even the best models hit ~68% compliance. Instructions have negative dependencies — simultaneous compliance is harder than individual probabilities predict. Reference data (when task-relevant) and structural markers cause less interference because they're retrieved, not obeyed. Motivational fluff ("this is important", "thoroughness matters") adds context load without behavioral change. Corrective rationale ("never use ellipses — TTS can't pronounce them") earns its place by encoding causal chains that enable generalization. When designing commands, workflows, or agents, every behavioral instruction must earn its place by measurably changing output in the runtime context.

**Positional attention bias.** LLMs bias toward instructions at the beginning and end of prompts. The middle is the attention trough — instructions buried there are most likely skipped. Place objectives and critical constraints at the beginning, success criteria and key reinforcement at the end, elaboration and process details in the middle (kept lean). This is why Mindsystem commands use `<objective>` first and `<success_criteria>` last. Restating a critical instruction at the end isn't redundancy — it's peripheral reinforcement.

### Latency-Quality Spectrum

| Tactic | Context saved | Latency cost | Use when |
|--------|--------------|--------------|----------|
| Subagent delegation | High (fresh 200k) | High (spinup + re-reads) | Task would fill >30% of parent context |
| Script extraction | Medium (prompt shrinks) | Low (script execution) | Logic is deterministic and reusable |
| CLI tool wrapping | High (API logic externalized) | Medium (tool development) | Repeated API interactions across sessions |
| Progressive disclosure | Medium (defer loading) | None | Always — default approach |
| Eager vs lazy loading | Variable | None | @-ref for essential files; read instructions for conditional |
| Orchestration separation | Medium (per-plan savings) | None | Always — orchestration metadata centralized in EXECUTION-ORDER.md |
</context_engineering>

<architecture>

### Context Split

Mindsystem deliberately separates where work happens:

| Main context (with user) | Fresh subagent contexts (autonomous) |
|--------------------------|--------------------------------------|
| `/ms:new-project` | ms-executor |
| `/ms:config` | ms-verifier |
| `/ms:create-roadmap` | ms-researcher |
| `/ms:plan-phase` | ms-debugger |
| `/ms:discuss-phase` | ms-codebase-mapper |
| `/ms:design-phase` | ms-code-simplifier |
| `/ms:verify-work` | |

Collaboration benefits from user visibility and iteration. Execution benefits from fresh context (200k tokens, peak quality). Planning stays editable; execution produces artifacts.

### Component Model

```
Command → Workflow → Agent → Artifact
```

- **Command** (`commands/ms/*.md`) — User interface. Thin wrapper that delegates to workflow. Answers: "Should I use this?"
- **Workflow** (`mindsystem/workflows/*.md`) — Detailed procedure with steps. Answers: "What happens?"
- **Agent** (`agents/ms-*.md`) — Subagent definition for autonomous work. Spawned via Task tool.
- **Template** (`mindsystem/templates/*.md`) — Output structure with placeholders. Answers: "What does output look like?"
- **Reference** (`mindsystem/references/*.md`) — Deep concept explanation. Answers: "Why this design?"
- **Script** (`ms-tools`) — Unified Python CLI for deterministic automation. No judgment logic.
- **Skill** (`skills/*/SKILL.md`) — Domain expertise loaded on demand.

### Repository Structure

```
mindsystem/
├── agents/               # Subagent definitions (→ ~/.claude/agents/)
├── commands/ms/          # Slash commands (→ ~/.claude/commands/ms/)
├── mindsystem/           # Core system (→ ~/.claude/mindsystem/)
│   ├── workflows/           # Step-by-step procedures
│   ├── templates/           # Output structures
│   └── references/          # Deep-dive concept docs
├── skills/               # Domain expertise skills
├── scripts/              # Shell scripts (→ ~/.claude/mindsystem/scripts/)
└── CLAUDE.md             # Contributor guidelines (enforcement rules)
```

**Installation:** `npx mindsystem-cc` copies to `~/.claude/` (global) or `.claude/` (local).

### Core Workflow — Milestone Lifecycle

1. `/ms:new-milestone` → Discover what to build, update PROJECT.md
1b. `/ms:config` → (optional) Configure code reviewers, gitignore, git remote
2. `/ms:create-roadmap` → REQUIREMENTS.md + ROADMAP.md + STATE.md

**Per phase (repeat for each):**

3. `/ms:discuss-phase N` (optional) → Gather context before planning
4. `/ms:design-phase N` (optional) → DESIGN.md for UI-heavy phases
5. `/ms:research-phase N` (optional) → Research implementation approach
6. `/ms:plan-phase N` → PLAN.md files + EXECUTION-ORDER.md
7. `/ms:execute-phase N` → Subagents execute plans, create SUMMARY.md
8. `/ms:verify-work N` (optional) → UAT verification with mock generation and inline fixing

**After all phases:**

9. `/ms:audit-milestone` → Verify milestone completion against original intent
10. `/ms:complete-milestone` → Archive milestone, prepare for next milestone

### Artifact Flow

| Artifact | Produced by | Consumed by |
|----------|------------|-------------|
| PROJECT.md | new-project, new-milestone | create-roadmap, plan-phase, execute-phase, design-phase, config |
| MILESTONES.md | complete-milestone | progress, new-milestone |
| REQUIREMENTS.md | ms-roadmapper (create-roadmap) | plan-phase, audit-milestone, ms-verifier |
| ROADMAP.md | ms-roadmapper (create-roadmap) | progress, plan-phase, execute-phase, audit-milestone |
| STATE.md | ms-roadmapper (init), ms-tools update-state | progress, plan-phase, execute-phase, verify-work |
| CONTEXT.md | discuss-phase | plan-phase, ms-plan-writer, ms-designer |
| DESIGN.md | ms-designer (design-phase) | plan-phase, ms-executor |
| PLAN.md | ms-plan-writer (plan-phase) | ms-executor, ms-verifier, verify-work |
| EXECUTION-ORDER.md | ms-plan-writer (plan-phase) | execute-phase, ms-tools validate-execution-order |
| SUMMARY.md | ms-executor (execute-phase) | progress, verify-work, audit-milestone, dependent plans |
| VERIFICATION.md | ms-verifier (execute-phase) | progress, plan-phase (gap closure), audit-milestone |
| UAT.md | verify-work | progress, audit-milestone |
| MILESTONE-AUDIT.md | audit-milestone | complete-milestone |
| knowledge/*.md | ms-consolidator (execute-phase), ms-compounder (compound) | future phase planning |
</architecture>

<change_propagation>

| When you change... | Also update... |
|--------------------|----------------|
| Workflow steps | Corresponding command's `<process>` section |
| Agent expected output | Workflow that spawns it |
| Template structure | All agents/workflows that reference it |
| config.json options | execute-phase workflow + help.md + config command |
| Plan format or structure | plan-format.md reference + plan-phase workflow + ms-plan-writer agent |
| EXECUTION-ORDER.md format | execute-phase workflow + ms-plan-writer agent |
| Plan inline metadata | verifier + executor + plan-checker |
| STATE.md format | state template + ms-tools update-state |
| SUMMARY.md format | execute-plan workflow (inline summary instructions) |
| Command name | help.md command list |
| New command | help.md + (workflow if non-trivial) |
| New agent | Workflow that spawns it |
</change_propagation>

<where_things_belong>

| Question | Location |
|----------|----------|
| User invokes directly? | Command (`commands/ms/`) |
| Detailed procedure? | Workflow (`mindsystem/workflows/`) |
| Autonomous execution? | Agent (`agents/`) |
| Deterministic/mechanical? | Script (`scripts/`) |
| Output structure? | Template (`mindsystem/templates/`) |
| Deep concept explanation? | Reference (`mindsystem/references/`) |
| Domain expertise? | Skill (`skills/`) |
| Enforcement rules? | `CLAUDE.md` |
| Design philosophy? | This skill (ms-meta) |
</where_things_belong>

<anti_patterns>
**Mindsystem-specific bans** (generic bans like enterprise patterns, temporal language, vague tasks are enforced by CLAUDE.md):

- **Mega-flows** that bundle unrelated commands into one
- **Hidden delegation** — subagents making key decisions without user visibility
- **Judgment logic in scripts** — scripts do mechanical operations, prompts do reasoning
- **Reflexive SUMMARY chaining** — independent plans don't need prior SUMMARY references
- **Horizontal splitting** — split plans by vertical feature slices, not by layer (model/API/UI)
- **Context inflation** — @-references to files not needed for current path, plan-writer overriding orchestrator's grouping for budget reasons
- **Manual gates for automatable work** — if Claude can verify it, don't ask the user
- **Orchestration in plans** — wave numbers, dependencies, and file ownership metadata belong in EXECUTION-ORDER.md, not in individual plan files
- **XML/YAML in plans** — plans use pure markdown; XML containers and YAML frontmatter are overhead that doesn't improve code output
</anti_patterns>

<deep_dive_paths>
Read source files directly for detailed knowledge:

| Topic | Read |
|-------|------|
| Project initialization | `commands/ms/new-project.md` |
| Project configuration | `commands/ms/config.md` |
| Milestone discovery | `commands/ms/new-milestone.md` |
| Roadmap creation | `commands/ms/create-roadmap.md` |
| Phase discussion | `mindsystem/workflows/discuss-phase.md` |
| Design specification | `commands/ms/design-phase.md` |
| Phase research | `commands/ms/research-phase.md` |
| Phase planning | `mindsystem/workflows/plan-phase.md` |
| Plan format & anatomy | `mindsystem/references/plan-format.md` |
| Plan conventions | `.claude/skills/ms-meta/references/conventions.md` |
| Execution orchestration | `mindsystem/workflows/execute-phase.md` |
| Plan execution (in subagent) | `mindsystem/workflows/execute-plan.md` |
| Verification protocol | `agents/ms-verifier.md` |
| Milestone audit | `commands/ms/audit-milestone.md` |
| Milestone completion | `mindsystem/workflows/complete-milestone.md` |
| Code review (simplifier) | `agents/ms-code-simplifier.md` |
| Code review (structural) | `agents/ms-code-reviewer.md` |
| Health checks & config healing | `commands/ms/doctor.md` |
| All agents | `ls agents/` |
| All commands | `ls commands/ms/` |
| All workflows | `ls mindsystem/workflows/` |
| Contributor rules | `CLAUDE.md` |
</deep_dive_paths>

</essential_knowledge>

<success_criteria>
After loading this skill:
- Continue with the original task, informed by Mindsystem expertise
- Apply Mindsystem principles naturally (modularity, main context collaboration, user as collaborator)
- Reference specific file paths when designing changes
- Use the change propagation table when modifying existing files
- Use where_things_belong to decide file locations for new features

**Do NOT:** Write a response "about" Mindsystem principles. Apply them to the work at hand.
</success_criteria>
