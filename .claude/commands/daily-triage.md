---
description: Fetch all unsolved Linear tickets, score them by leverage, and recommend 1-3 tickets for today's session
---

<objective>
Daily triage routine that surfaces the highest-leverage work for a 30-60 minute Claude Code session. Fetches all unsolved tickets from Linear, understands the project's architecture, scores each ticket by impact and effort, and recommends 1-3 tickets that maximize value delivered today.

This command applies the Pareto principle: find the 20% of tickets that deliver 80% of the impact.
</objective>

<process>

<step name="load_domain_context">
You need to understand this project's architecture before you can score impact accurately.

Run these in parallel:

1. **CLAUDE.md** — Read the project's `CLAUDE.md`. Contains development conventions, architecture notes, and system overview.
2. **Check for PROJECT.md** — Run `test -f .planning/PROJECT.md && echo EXISTS || echo MISSING` via Bash. Do NOT attempt to read the file yet.
3. **Load skills** — Invoke both skills using the Skill tool (no args needed):
   - `linear` — loads the CLI reference for fetching tickets
   - `ms-meta` — loads Mindsystem architecture knowledge for accurate impact scoring

Then, if step 2 reported PROJECT.md EXISTS, read `.planning/PROJECT.md`. It provides business context, system structure, and current project state. Skip silently if MISSING.

The goal is to understand: what are the core workflows, what is upstream vs downstream, and where do changes have the highest blast radius. This directly determines impact scoring in the next steps.
</step>

<step name="fetch_all_unsolved_tickets">
Run all three queries in parallel using Bash:
- `uv run ~/.claude/skills/linear/scripts/linear.py list --state backlog --limit 50`
- `uv run ~/.claude/skills/linear/scripts/linear.py list --state started --limit 50`
- `uv run ~/.claude/skills/linear/scripts/linear.py list --state todo --limit 50`

Combine all results into a single list. These are all unsolved tickets.

**Important:** The list response only includes title, priority, and estimate. This is often not enough to accurately score a ticket. Before scoring, fetch full details (with comments) for any ticket that could plausibly be high-leverage:

```
get <ID> --comments
```

Always fetch details when:
- The title is vague or could mean different things (e.g., "Improve X" — improve how?)
- You can't tell from the title how many files or parts of the system are affected
- The ticket might have a known root cause or approach documented in comments
- The estimate seems off relative to the title (e.g., a seemingly simple fix with a large estimate — why?)
- The ticket has comments (comment count > 0) — comments often contain critical context like root cause analysis, design decisions, or scope clarifications

Err on the side of fetching more details rather than fewer. A wrong score from insufficient context is worse than spending an extra minute reading ticket details. Fetch tickets in parallel where possible.
</step>

<step name="filter_ready_now">
Eliminate tickets that are NOT actionable today:

- **Blocked** — explicitly depends on another unfinished ticket (check relations like "blocked by"). Note: parent/sub-issue relationships are NOT blocking — parents are abstractions and sub-issues are the actual work. Sub-issues are always actionable regardless of parent state.
- **Research-only** — no code deliverable, just reading/learning (defer to spare time)
- **Needs design decisions** — requires architectural choices that haven't been made yet
Mark eliminated tickets with the reason. This typically cuts the list by 30-50%.

**Do NOT filter by size.** Large tickets (L, XL) survive filtering — effort scoring and session composition handle them. Filtering by size before scoring guarantees the highest-impact work never gets evaluated.
</step>

<step name="score_remaining_tickets">
Score each remaining ticket on two axes:

**Impact Score (1-3):**

| Score | Criteria |
|---|---|
| 3 | **Upstream/core path.** Affects root context (PROJECT.md, templates), executor, plan-phase, or any workflow that runs on every session. Correctness fix or quality ceiling lift. Changes here compound across all future usage. |
| 2 | **Frequently-used path.** Affects a command used regularly (design-phase, verify-work, progress). Removes real user friction or fixes degraded output. |
| 1 | **Peripheral path.** Affects a rarely-used command, a nice-to-have, or cosmetic improvement. Low blast radius. |

**Effort Score (1-3) — calibrated for Claude Code development:**

| Score | Criteria |
|---|---|
| 1 (low) | 1-2 files changed, clear approach, no ambiguity. Estimated 15-30 min with Claude Code. Examples: remove a dead config property, fix a file reference, update a template section. |
| 2 (medium) | 3-5 files changed, known approach but requires coordination across files. Estimated 30-60 min. Examples: restructure a template + update discovery flow, fix skill discovery in a workflow. |
| 3 (high) | 6+ files, OR requires investigation/diagnosis, OR requires architectural decisions before coding. Likely exceeds 60 min. Examples: new command, multi-file refactor, cross-cutting workflow change. |

**Key effort signals to look for:**
- Adding/removing entire commands or workflows = effort 3
- Changing a template + updating references to it = effort 2
- Single-file fix with clear root cause = effort 1
- "Research" or "evaluate" in the title = effort 3 (investigation needed)

**Score effort on remaining work, not original scope.** Effort 3 includes "requires investigation/diagnosis" and "requires architectural decisions" as OR conditions. When comments already contain root cause analysis, approach decisions, or investigation results, those conditions no longer apply. Re-evaluate effort based on what's left to implement:
- If investigation is done and 3-5 files remain with a known approach → effort 2, not "effort 3 minus 1"
- If approach is decided and only 1-2 files need changes → effort 1
- Comments that contain analysis but no clear conclusion don't reduce effort — the decision still needs to be made

**Leverage = Impact / Effort**
</step>

<step name="compose_session">
Rank all scored tickets by leverage (highest first).

Compose a session by selecting the best option:

1. **Strategic ticket** — Impact 3 at any effort level. When the most upstream/core work is available, recommend it regardless of leverage score. These tickets compound across all future usage — deferring them repeatedly is worse than spending a longer session. For effort-3 strategic tickets, identify the actionable scope for today (what's the meaningful slice that ships progress).
2. **High-leverage ticket** — Leverage >= 1.5, effort 2-3.
3. **Two quick wins** — Each leverage >= 2.0, effort 1 each.
4. **One quick win + scoping** a future high-impact ticket (read its details, identify approach, leave notes).

Evaluate options in order. If option 1 qualifies, prefer it over lower-numbered options unless a quick win has dramatically higher leverage (3.0+).

**Selection tiebreakers** (when leverage scores are equal):
1. Correctness fixes beat quality improvements beat friction reduction
2. Upstream (pipeline position) beats downstream
3. Smaller effort wins (ship something today)
</step>

<step name="present_recommendations">
Present the recommendations conversationally, like an assistant briefing you on what to tackle today. Keep it concise and actionable.

Format:

---

## Daily Triage — [date]

### Recommended ([estimated total time])

For each recommended ticket (1-2):

**[ID] — [Title]**
- Impact: [1-3] — [one-line reason]
- Effort: [1-3] — [one-line reason]
- Leverage: [score]
- Quick plan: [2-3 sentences on what you'd actually do]

### Also worth considering

List 3 alternative tickets the user could realistically pick instead. For each:

**[ID] — [Title]** (leverage [score])
[1-2 sentences: what the work involves and why you'd pick this over the top recommendations — e.g., "If you're in the mood for a quick win..." or "If you'd rather tackle something upstream that compounds..."]

---

End with: "Ready to start? Pick a ticket and I'll fetch its full details."
</step>

</process>

<success_criteria>
- All unsolved tickets fetched from Linear (backlog + started + todo)
- Project architecture understood before scoring
- Ambiguous tickets inspected in detail (with comments) before scoring
- Blocked/premature tickets filtered out (internally, not shown to user)
- Every remaining ticket scored on impact (1-3) and effort (1-3)
- Effort scores reflect Claude Code development speed, not traditional estimates
- 1-2 top tickets recommended with quick plans
- 3 alternatives presented with arguments for why you'd pick them instead
- Output is concise and conversational — no backlog dumps or filter breakdowns
</success_criteria>
