<original_task>
Review and improve multiple slash commands, mental framework commands, and the create-slash-command skill by applying prompt quality guide principles. The goal is to eliminate meta-commentary, reduce instruction budget waste, fix ambiguous output formats, reorder success criteria by skip risk, and ensure the create-slash-command skill teaches prompt quality principles so generated commands are also effective.
</original_task>

<work_completed>

## 1. work-ticket command (`~/.claude/commands/work-ticket.md`)

**Added `design_solution` step** between `clarify_requirements` and `plan`:
- Presents: current situation, problem, 2-3 proposed solutions with trade-offs
- Uses AskUserQuestion to get user direction before planning
- Ensures user guides the final solution rather than the LLM prescribing one
- Initial version was too prescriptive (included first-principles reasoning instructions); revised per user feedback to surface information without dictating how the user should think

**Removed meta-commentary:**
- "Do not proceed to planning until the codebase is deeply understood" (line 44, step ordering already enforces this)
- "do not rely solely on agent summaries" (redundant when paired with positive instruction "read the key files yourself")
- "Tickets are written by humans for humans and almost always underspecify" (rationale, not behavioral)
- "All context is now gathered" (meta-commentary in plan step)

**Fixed success criteria:**
- Reordered by skip risk: "Solution direction confirmed by user" moved to first position
- Removed duplicate: "Codebase explored in depth" (already enforced in step body)
- Final count: 5 items (down from 6)

## 2. first-principles command (`~/.claude/commands/consider/first-principles.md`)

**Fixed ambiguous output format:**
- `[challenged: true/false/partially]` replaced with `**holds** / **breaks** / **partially holds**: [why]`
- Old format was genuinely ambiguous — "challenged: true" could mean "the assumption was challenged" (it's wrong) or "the assumption is true" (it survived)
- Added `[why]` after each verdict to force inline reasoning

**Removed meta-commentary:**
- "Strip away assumptions, conventions, and analogies to identify fundamental truths, then rebuild understanding from scratch" — philosophy description; process steps already implement this

## 3. analyze-problem command (`~/.claude/commands/analyze-problem.md`)

**Major rewrite — 319 lines to 124 lines:**
- Kept all 12 framework definitions unchanged (reference data, low interference)
- Collapsed `<available_research>` from 48 lines (categorized with examples) to 10 lines (name + one-liner each)
- Eliminated `<research_decision_logic>` (24 lines, 12 behavioral instructions for a ~20% path) — replaced with 2 sentences in process step 3
- Replaced 3 conditional output templates (66 lines) with 1 flat template (7 lines) where research is a single line
- Eliminated `<post_research_checkpoint>` (11 lines) — LLM handles this naturally
- Eliminated `<research_subagents>` section — redundant with available_research list
- Simplified process from 8 steps to 4
- Simplified objective from 15 lines (with deduction logic) to 2 lines
- Success criteria: 13 items down to 5, reordered by skip risk

## 4. daily-triage command (`.claude/commands/daily-triage.md` in mindsystem repo)

**Removed meta-commentary:**
- "This command applies the Pareto principle: find the 20% of tickets that deliver 80% of the impact" (scoring system already implements this)
- "You need to understand this project's architecture before you can score impact accurately" (instructions say what to read)
- "The goal is to understand: what are the core workflows..." (restates what impact scoring table encodes)
- "A wrong score from insufficient context is worse than spending an extra minute reading ticket details" (rationale for behavioral override already stated)

**Fixed confusing wording:**
- "prefer it over lower-numbered options" (nonsensical — option 1 IS the lowest) changed to "Prefer the first qualifying option"

**Trimmed success criteria:** 9 items to 6, reordered by skip risk:
1. Ambiguous tickets inspected in detail before scoring (highest skip risk)
2. Effort scores reflect Claude Code speed
3. 3 alternatives presented
4. Output concise — no backlog dumps
5. Score effort on remaining work (peripheral reinforcement)
6. 1-2 top tickets recommended (lowest skip risk)

## 5. pareto command (`~/.claude/commands/consider/pareto.md`)

**Light touch — already lean:**
- Removed "cutting through noise to focus on what actually matters" (meta-commentary restating Pareto)
- Loosened rigid 20/80 ratio: "~20% of factors account for ~80% of impact" changed to "a small minority of factors account for the majority of impact"
- Success criteria: 5 to 4 items. Removed "Reduces decision fatigue" (meta-commentary). Moved "Specific, actionable recommendations" to first (highest skip risk)

## 6. opportunity-cost command (`~/.claude/commands/consider/opportunity-cost.md`)

- Removed aphorism: "Every yes is a no to something else. What's the true cost of this choice?"
- Simplified output format: replaced rigid resource-by-resource parallel lists (Time/Money/Energy each with own alternative) with flexible fields
- Added AI-assisted coding context to step 2: "For coding decisions with AI-assisted development, implementation time is often trivial — focus on complexity introduced, cognitive load, and whether the approach is proportionate to the problem."
- Success criteria: 5 to 3 items, reordered. Removed "Reveals when affordable things are actually expensive" and "Enables genuine comparison" (meta-commentary/vague)

## 7. create-slash-command skill (`~/.claude/skills/create-slash-command/SKILL.md`)

**Major restructure — 631 lines to 197 lines (user applied changes via linter/manual edit):**

Structural changes:
- Moved `<generation_protocol>` from line 553 (attention trough) to line 37 (prime attention)
- Removed sections that duplicate reference files: `<arguments_intelligence>` (75 lines), `<common_patterns>` (116 lines), `<best_practices>` (48 lines), `<structure_example>`, `<intelligence_rules>`, `<file_structure>`, `<reference_guides>`, `<arguments>`
- Added lazy-loading instructions in generation_protocol: read references/arguments.md, patterns.md, tool-restrictions.md when relevant

Content quality changes:
- Added step 5 "Write effective prompt content" to generation_protocol with:
  - Contrastive example showing bad (with "This ensures...") vs good objective
  - Guidance on imperative voice, skip-risk ordering, instruction budget
  - "Every instruction must change the LLM's behavior" principle
- Trimmed success criteria from 13 sub-items across 5 categories to 6 items ordered by skip risk
- First criterion: "Generated objectives contain no filler" (highest skip risk)

**Reference file updates (`references/patterns.md`):**
- Removed all "This helps..." / "This ensures..." / "This provides..." filler from example command objectives throughout the file
- All example objectives now follow the lean pattern established in the skill

`references/arguments.md` and `references/tool-restrictions.md` — not yet updated (see work remaining).

</work_completed>

<attempted_approaches>

No failed approaches. All changes were iterative refinements:

1. First version of `design_solution` step was too prescriptive — included first-principles reasoning instructions and "do not anchor on the ticket's approach" meta-commentary. User correctly identified this was dictating how they should think rather than surfacing information. Revised to: present situation + problem + proposed solutions, then AskUserQuestion.

2. For analyze-problem, considered keeping research decision logic as a condensed section. Decided instead to collapse it into 2 sentences within process step 3, since the full decision tree was 12 behavioral instructions for a 20% execution path.

</attempted_approaches>

<critical_context>

## Prompt Quality Guide Principles (applied throughout)

These principles from the user's global CLAUDE.md drove all changes:
- **Instruction budget**: ~150-200 behavioral instructions before compliance degrades. Each instruction competes with all others.
- **Skip risk ordering**: Success criteria ordered by what the LLM is most likely to skip (highest first)
- **5-7 cap**: Success criteria beyond 7 items dilute all others
- **Meta-commentary is waste**: Explaining *why* an instruction exists burns a slot without changing behavior
- **Positional attention**: Important content at beginning/end. Middle is the attention trough.
- **Progressive disclosure**: Lazy-load content only when needed. Eager-load only essential content.
- **Negations of unlikely behaviors**: Activates the concept without benefit. Only negate observed failure modes.
- **Contrastive examples**: Good + bad paired together anchor rules more effectively than rules alone.

## Key Design Decisions

- **analyze-problem research handling**: Collapsed from 60% of prompt to ~15%. Research is still available but no longer dominates the prompt for the 80% of cases where it's not needed.
- **work-ticket design_solution step**: Surfaces information (situation, problem, options) without prescribing mental frameworks. User chooses their own reasoning approach.
- **create-slash-command**: The skill generates prompts, so its content quality directly determines quality of every command created with it. Adding prompt quality guidance to the generation protocol is the highest-leverage change.
- **opportunity-cost coding context**: Added one sentence to step 2 that conditionally reframes "resources" for AI-assisted coding decisions (complexity/cognitive load instead of time). Non-coding uses unaffected.

## File Locations

All modified commands are in the user's personal config (`~/.claude/commands/`) EXCEPT:
- `daily-triage.md` is in the mindsystem repo (`.claude/commands/daily-triage.md`)
- This matters because mindsystem repo changes go through git; personal config changes do not

## The user's workflow

The user is a solo developer using Claude Code extensively. Mental framework commands (`/consider:*`) and `/analyze-problem` are used frequently for architectural decisions. `/work-ticket` is the primary development workflow. `/daily-triage` starts each session. The create-slash-command skill is used to create new commands — its output quality compounds across all future commands.

</critical_context>

<current_state>

## Deliverable Status

| File | Status | Notes |
|------|--------|-------|
| `~/.claude/commands/work-ticket.md` | Complete | User applied additional edits via linter |
| `~/.claude/commands/consider/first-principles.md` | Complete | User applied additional edits via linter |
| `~/.claude/commands/analyze-problem.md` | Complete | Major rewrite (319 → 124 lines) |
| `.claude/commands/daily-triage.md` (mindsystem) | Complete | User applied additional edits via linter |
| `~/.claude/commands/consider/pareto.md` | Complete | User applied additional edits via linter |
| `~/.claude/commands/consider/opportunity-cost.md` | Complete | User applied additional edits via linter |
| `~/.claude/skills/create-slash-command/SKILL.md` | Complete | User applied restructure (631 → 197 lines) |
| `~/.claude/skills/create-slash-command/references/patterns.md` | Complete | Filler removed from examples |
| `~/.claude/skills/create-slash-command/references/arguments.md` | Not started | Needs filler review |
| `~/.claude/skills/create-slash-command/references/tool-restrictions.md` | Not started | Needs filler review + possible trim |

## Git State

- `daily-triage.md` is the only changed file in the mindsystem repo (shown as modified in git status)
- All other files are in `~/.claude/` (user personal config, not version controlled)

## Open Questions

- Should the remaining reference files (arguments.md, tool-restrictions.md) be trimmed aggressively or just have filler removed?
- Should the plan file (`~/.claude/plans/ethereal-orbiting-wren.md`) be deleted?

</current_state>
