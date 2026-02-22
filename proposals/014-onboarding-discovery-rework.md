# Proposal: Onboarding & Discovery Rework

**Date:** 2026-02-22
**Scope:** Restructure project initialization, config setup, and discuss-phase to create a clear, non-overlapping command chain with rich business context flowing through all downstream workflows.

---

## Vision

The current onboarding flow has overlapping concerns between `new-project` and `new-milestone`, buries mechanical config alongside dream extraction, and lacks the business context (target audience, USP, core problem) needed for effective product decisions downstream. The discuss-phase operates at ~20-25% context with generic questions when it could be a grounded PO-style collaborator.

**Target flow after rework:**

```
/ms:new-project     → Dream extraction. Business context, audience, USP, core problem.
                      Idempotent — callable anytime for updates or pivots.
                      Focuses on the WHOLE project's scope.

/ms:setup           → Mechanical config. Code reviewers, gitignore, token budget.
                      Idempotent — callable anytime to reconfigure.

/ms:new-milestone   → Discover what to build for this release cycle.
                      Works identically for first and subsequent milestones.

/ms:create-roadmap  → Requirements + phase planning. Stays separate from new-milestone.
```

The discuss-phase then consumes rich PROJECT.md business context to perform PO-style analysis before every decision question, grounding phase discussions in target audience, industry patterns, and product strategy.

---

## Session Breakdown

### Session 1: PROJECT.md Business Context (MIN-49)

**Goal:** Redesign PROJECT.md template to capture business context that grounds all downstream product decisions. Update new-project's questioning flow to populate these new sections.

**Relevant tickets:**
- **MIN-49** (High, est. 3) — "Improve PROJECT.md to capture business context for product decisions"
  - Comment: sample context file at `references/samples/context-with-first-principles.md`
  - Comment: design constraints — human-readable, maximally useful for downstream consumers, balanced structure/readability

**What to do:**

1. **Audit current PROJECT.md template** (`mindsystem/templates/project.md`)
   - Current sections: What This Is, Core Value, Requirements (3 tiers), Context, Constraints, Key Decisions
   - Evaluate which sections earn their place vs. which are noise
   - The Requirements section is a design decision point — where do Active requirements live after the rework? (flagged for first-principles analysis during implementation)

2. **Design new business context sections** — apply first-principles thinking to determine what fields maximize downstream decision quality:
   - Target audience (who uses this, their context, their workflow)
   - Core problem being solved (why this exists)
   - USP / differentiator (what makes this different)
   - Key user flows (the 2-3 things users actually do)
   - Competitive landscape (brief — who else solves this, how they differ)
   - Consider: should "Core Value" be merged into/replaced by these sections?

3. **Update questioning flow in new-project** (`commands/ms/new-project.md`)
   - Rework Step 3 (Question) to elicit business context naturally — not as a checklist
   - For brownfield projects: the questioning should recognize the codebase exists and focus on "tell me about the project, not the next feature"
   - Use the `questioning.md` reference techniques but oriented toward business discovery

4. **Update template file** and any downstream references

**Key design constraint:** The sample file `references/samples/context-with-first-principles.md` shows what a CONTEXT.md with deep first-principles analysis looks like. PROJECT.md should enable that level of grounded analysis in discuss-phase without being that verbose itself — it's the source data, not the analysis output.

**Dependencies:** None — this is the foundation.

**Change propagation:**
- Template: `mindsystem/templates/project.md`
- Command: `commands/ms/new-project.md` (Step 3 + Step 4)
- Downstream consumers to verify (read-only, no changes needed yet): discuss-phase, design-phase, plan-phase, new-milestone

---

### Session 2: Extract ms:setup + Make new-project Idempotent (MIN-56, MIN-67, MIN-68)

**Goal:** Extract mechanical config from new-project into standalone ms:setup command. Make new-project callable anytime with targeted update mode. Ensure the command chain routes correctly for all project states.

**Relevant tickets:**
- **MIN-56** (Normal, parent) — "Create ms:setup command"
  - Comment (2026-02-14): "Decision: split doctor out into its own command (MIN-120, DONE). ms:setup stays focused on first-time setup and config wizard."
  - Sub-issues: MIN-69 (version migration — defer), MIN-65 (patch reapply — defer)
- **MIN-67** (Normal, est. 3) — "Config wizard — interactive config.json walkthrough"
  - Acceptance: shared workflow file that both ms:setup and new-project reference
- **MIN-68** (Normal, est. 2) — "Project detection and routing"
  - Fresh → config wizard → suggest new-project. Existing → show health status, offer actions.
- **MIN-102** (parent, Todo) — "Streamline project setup and milestone creation commands"

**What to do:**

1. **Create ms:setup command** (`commands/ms/setup.md`)
   - Config wizard walking through all config.json options
   - Currently config.json has: `subsystems[]`, `code_review { adhoc, phase, milestone }`
   - Extend with: `.gitignore` setup for `.planning/` artifacts (patch files, mockups), token budget config (if applicable)
   - Idempotent — shows current values, lets user modify selectively
   - Create shared workflow (`mindsystem/workflows/config-wizard.md`) that both setup and new-project can reference

2. **Extract config from new-project**
   - Current Step 5 (Config) in new-project creates config.json with subsystems and code_review
   - Replace with: delegate to config-wizard workflow OR suggest running ms:setup
   - Decision point: does new-project auto-run the config wizard inline, or just suggest ms:setup as next step?

3. **Make new-project idempotent (targeted update mode)**
   - Remove the "abort if PROJECT.md exists" check in Step 1
   - When PROJECT.md exists: show current sections, let user pick which to update
   - Smart diffing — only re-question sections that changed
   - Detect whether this is a minor update or a major pivot based on what the user wants to change

4. **Project detection and routing (MIN-68)**
   - ms:setup detects: fresh project (no .planning/) → config wizard → suggest new-project
   - new-project detects: no config → suggest ms:setup first
   - new-milestone detects: no PROJECT.md → suggest new-project first
   - Each command guides the user to the right next step

5. **Update new-milestone routing**
   - Ensure new-milestone works as the "always next step" after new-project for greenfield projects
   - Currently new-project suggests research-project OR create-roadmap → update to suggest new-milestone
   - Small change to Step 7 (Done) in new-project

**Dependencies:** Session 1 should be done first (new template exists). However, the setup extraction is mechanically independent and could be started in parallel.

**Change propagation:**
- New command: `commands/ms/setup.md`
- New workflow: `mindsystem/workflows/config-wizard.md`
- Modified command: `commands/ms/new-project.md` (Steps 1, 5, 7)
- Modified command: `commands/ms/new-milestone.md` (add PROJECT.md check)
- help.md: add ms:setup to command list
- README.md: update onboarding flow description (or defer to MIN-70)

---

### Session 3: Enrich Discuss-Phase (MIN-126)

**Goal:** Transform discuss-phase from a shallow vision-gathering protocol into a grounded PO-style collaborator that loads comprehensive artifacts, performs industry-aware analysis before questions, and integrates phase-assumptions surfacing.

**Relevant tickets:**
- **MIN-126** (High, est. 5) — "Enrich discuss-phase with deep artifact loading and phase-assumptions integration"
  - Comment (2026-02-19): PO-style analysis before every AskUserQuestion — industry best practices, target audience fit, UX/UI tradeoffs, recommendation
  - Comment (2026-02-19): preserve parallel-work compatibility — discuss-phase should be milestone-context-dependent, not sibling-phase-dependent
  - Dependency: MIN-49 (business context in PROJECT.md) makes PO analysis grounded in actual product domain

**What to do:**

1. **Expand artifact loading** — target ~40-50% context consumption (up from ~20-25%)
   - Currently loads: STATE.md, ROADMAP.md, knowledge files for matched subsystems
   - Add: PROJECT.md (with new business context), MILESTONE-CONTEXT.md, REQUIREMENTS.md (if exists)
   - Do NOT load sibling phase artifacts (preserves parallel-work pattern)
   - Context budget: ~40-50%, leaving room for user responses and analysis

2. **PO-style analysis before every decision question**
   - Before each AskUserQuestion, perform quick analysis covering:
     - Industry best practices (what do comparable apps typically do?)
     - Target audience fit (given the users, which option serves them better?)
     - UX/UI tradeoffs (pros and cons of each approach)
     - Recommendation (brief take on what data suggests)
   - This analysis requires PROJECT.md business context (target audience, core problem, industry) — which is why Session 1 must come first
   - Show analysis BEFORE the question, so user reads context then decides informed

3. **Integrate list-phase-assumptions**
   - Surface Claude's assumptions about the phase approach as part of the discussion flow
   - Currently exists as standalone `commands/ms/list-phase-assumptions.md`
   - After integration, remove the standalone command
   - Present assumptions early in the flow (after artifact loading, before deep questioning)

4. **Improve final "all captured?" gate**
   - Current gate: generic "Ready to create CONTEXT.md?" with no context about completeness
   - New gate: present summary of what was discussed vs what loaded artifacts suggest should be covered
   - User can make an informed decision about whether discussion was thorough enough

5. **Update CONTEXT.md output** — consider whether CONTEXT.md template needs new sections to capture:
   - Business context applied (how the PO analysis influenced decisions)
   - Assumptions validated/corrected during discussion

**Design constraint (from MIN-126 comment):** discuss-phase should be **milestone-context-dependent, not sibling-phase-dependent.** All business context, requirements, and product direction needed for effective discussion should live at the milestone level (PROJECT.md, REQUIREMENTS.md, ROADMAP.md) or be derivable from the phase description. This keeps phases independently preparable and preserves parallel work.

**Dependencies:** Session 1 (PROJECT.md business context) must be complete. Session 2 is independent.

**Change propagation:**
- Modified workflow: `mindsystem/workflows/discuss-phase.md` (major rework)
- Modified command: `commands/ms/discuss-phase.md` (update process steps, add artifact loading)
- Removed command: `commands/ms/list-phase-assumptions.md`
- help.md: remove list-phase-assumptions from command list
- ms-meta skill: update discuss-phase description in essential knowledge

---

## Dependency Graph

```
Session 1 (MIN-49: PROJECT.md business context)
    ├── Session 2 (MIN-56/67/68: setup + idempotency)
    │       └── Soft dependency — config extraction is mechanically independent,
    │           but new-project's final routing depends on Session 1's template
    └── Session 3 (MIN-126: discuss-phase enrichment)
            └── Hard dependency — PO analysis needs business context fields
```

**Recommended order:** Session 1 → Session 2 → Session 3

Sessions 2 and 3 could run in parallel if Session 1 is complete, but Session 2 is recommended first because it finalizes the command chain that discuss-phase operates within.

---

## Deferred Work (Separate Sessions)

| Ticket | Title | Why Deferred |
|--------|-------|--------------|
| MIN-130 | Tighten discuss-phase recommendation to default 'likely' | Natural follow-up after MIN-126 ships. Depends on enriched discuss-phase being available. |
| MIN-71 | Rework research-project into milestone-aware research command | Explicitly out of scope per user direction. Separate session. |
| MIN-110 | Evaluate research-phase modes: simplification opportunities | Research ticket, separate from onboarding rework. |
| MIN-70 | Rewrite README as product landing page | Should happen after commands stabilize. Depends on all 3 sessions being done. |
| MIN-9 | Audit PROJECT.md, STATE.md, and ROADMAP.md lifecycle | Research ticket. Partially addressed by Session 1's template audit. |
| MIN-58 | Add ms:update command | Depends on MIN-56 (setup) being done. Thin wrapper — small follow-up. |
| MIN-69 | Version migration — detect and apply breaking changes | Sub-issue of MIN-56, deferred for future setup enhancements. |
| MIN-65 | Support re-applying local patches after updates | Sub-issue of MIN-56, deferred. |

---

## Open Design Decisions

These should be resolved with first-principles thinking at the start of each session:

1. **Where do Active requirements live?** PROJECT.md currently has Requirements (Validated/Active/Out of Scope). With business context added, does this section still belong in PROJECT.md, or does it migrate to REQUIREMENTS.md (created by create-roadmap)? The answer affects what new-project populates vs. what new-milestone/create-roadmap handles.

2. **Git init and brownfield detection:** Currently in new-project Step 1. Should these move to ms:setup (mechanical), stay in new-project (contextual — informs questioning), or be shared? Brownfield detection specifically informs the questioning approach.

3. **Config delegation model:** Does new-project auto-run the config wizard inline when config.json doesn't exist, or does it suggest ms:setup as a next step and skip config entirely? The former is smoother for first-time users; the latter is cleaner separation.

4. **CONTEXT.md template evolution:** With PO analysis integrated into discuss-phase, should CONTEXT.md capture the analysis reasoning (for auditability) or just the final decisions? Adding analysis reasoning increases downstream context load.

5. **Subsystem derivation:** Currently new-project derives 5-10 subsystems for config.json. With config moving to setup, who derives subsystems — setup (from PROJECT.md) or new-project (during questioning)?

---

## Ticket Summary

### Directly addressed in this work:

| Ticket | Session | Current State |
|--------|---------|---------------|
| **MIN-49** | 1 | Todo (High, est. 3) |
| **MIN-56** | 2 | Backlog (Normal, est. 0 — parent) |
| **MIN-67** | 2 | Backlog (Normal, est. 3) |
| **MIN-68** | 2 | Backlog (Normal, est. 2) |
| **MIN-102** | 1+2 | Todo (Normal — parent of 56, 67, 68, 71, 120) |
| **MIN-126** | 3 | Todo (High, est. 5) |

### Partially addressed / informed:

| Ticket | How |
|--------|-----|
| **MIN-57** (Done) | Previous consolidation work. Context informs current rework. |
| **MIN-9** | Session 1's template audit partially covers PROJECT.md lifecycle questions. |

---

## How to Pick Up Each Session

### Starting Session 1
```
Load ms-meta skill. Read MIN-49 (with comments) and this proposal's Session 1 section.
Read current files: mindsystem/templates/project.md, commands/ms/new-project.md,
references/samples/context-with-first-principles.md.
Apply first-principles thinking to the open design decisions (#1, #2, #5).
Design the new template, update the command, test with a brownfield and greenfield scenario.
```

### Starting Session 2
```
Load ms-meta skill. Read MIN-56, MIN-67, MIN-68 (with comments) and this proposal's
Session 2 section. Read current files: commands/ms/new-project.md (post-Session 1),
commands/ms/new-milestone.md, commands/ms/doctor.md (for pattern reference).
Apply first-principles thinking to open design decisions (#3, #5).
Create setup command + config wizard workflow, update new-project for idempotency.
```

### Starting Session 3
```
Load ms-meta skill. Read MIN-126 (with comments) and this proposal's Session 3 section.
Read current files: commands/ms/discuss-phase.md, mindsystem/workflows/discuss-phase.md,
commands/ms/list-phase-assumptions.md, mindsystem/references/prework-status.md.
Read .planning/PROJECT.md from a test project to see the new business context fields.
Apply first-principles thinking to open design decision #4.
Rework discuss-phase workflow, update command, remove list-phase-assumptions.
```
