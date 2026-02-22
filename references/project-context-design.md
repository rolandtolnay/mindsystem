# PROJECT.md Context Design

First-principles analysis of what PROJECT.md should contain, why each section earns its place, and how to populate it through collaborative dream extraction.

---

## Purpose

PROJECT.md is the document that answers: **"If you're working on this product and need to make a decision, what do you need to know?"**

Every section passes this test: "Does knowing this change what I would build or how I would build it?"

---

## Template Structure

Three conceptual layers, flat headers, ordered by consumption frequency.

### Layer 1 — Product Identity

Consumed by every creative/strategic workflow (design-phase, discuss-phase, new-milestone).

| Section | Content | Why It's Irreducible |
|---------|---------|---------------------|
| **What This Is** | 2-3 sentence product identity in plain language | Anchors all downstream context |
| **Core Value** | Single sentence: the ONE thing that cannot fail | Lossy compression function — resolves tradeoffs without parsing paragraphs. Used by 4+ consumers as standalone heuristic |
| **Who It's For** | Target audience — who they are, their context, their workflow today. 2-4 sentences | Grounds UX complexity, priority weighting, and scope decisions |
| **Core Problem** | Why this exists — what pain or desire drives it. 1-2 sentences | Anchors "is this feature worth building?" across all workflows |
| **How It's Different** | Differentiators + competitive context if relevant. 2-3 bullets | Prevents building generic solutions. Competitive landscape folds in here — no standalone section |
| **Key User Flows** | The 2-3 core interactions users perform. One line each | Bridges abstract identity → concrete architecture. Persists the "core interaction" insight that questioning extracts but currently discards |

### Layer 2 — Product Boundaries

Consumed by scoping/planning workflows (define-requirements, plan-phase).

| Section | Content | Why It's Irreducible |
|---------|---------|---------------------|
| **Out of Scope** | Excluded items with reasoning | Prevents re-proposing deferred ideas across milestones |
| **Constraints** | Hard limits with rationale | Bounds solution space for all downstream consumers |
| **Technical Context** | Stack, integrations, prior work, known debt | Informs implementation decisions. Renamed from "Context" — no longer overloaded with business context |

### Layer 3 — Product Memory

Consumed by evolution workflows (transition, complete-milestone).

| Section | Content | Why It's Irreducible |
|---------|---------|---------------------|
| **Validated** | Shipped and confirmed requirements: `✓ [Requirement] — [version/phase]` | Cumulative record of what exists. Prevents re-learning across milestones |
| **Key Decisions** | Table: Decision / Rationale / Outcome (✓ Good, ⚠️ Revisit, — Pending) | Prevents re-debating settled questions |

Plus: **Last Updated** footer with timestamp and trigger.

---

## Design Decisions and Rationale

### Active Requirements Removed

Active requirements are hypotheses for the *current milestone* — created by create-roadmap, consumed by plan-phase, replaced every milestone. Milestone-scoped data belongs in milestone-scoped artifacts (REQUIREMENTS.md). No "Current Focus" replacement needed — STATE.md serves that purpose.

### Core Value Stays Separate from Business Context

Core Value is consumed as a **standalone single-sentence heuristic** by design-phase, define-requirements, complete-milestone, and transition. It works because it's lossy compression — one sentence that resolves tradeoffs without parsing paragraphs. The business context sections (Who It's For, Core Problem, How It's Different) provide the reasoning behind Core Value. They're complementary, not redundant.

### Competitive Landscape Folds Into "How It's Different"

Competitive landscape is inherently dynamic — it shifts faster than PROJECT.md evolves. Persisting a dedicated section creates stale data that misleads rather than informs. A sentence or two about what else exists is part of explaining differentiation. Runtime research (discuss-phase PO analysis) produces better competitive analysis than static snapshots.

### "Context" Renamed to "Technical Context"

Previous "Context" conflated business context (who uses this) with technical context (what tech exists). With explicit business context sections in Layer 1, this section becomes purely technical: stack, integrations, prior work, known debt.

### Key User Flows Earns Standalone Status

The "core interaction" question ("What's the one thing users do that makes this valuable?") is one of the three highest-leverage questions in dream extraction. Currently asked during project initialization but never persisted — the insight gets discarded. Key User Flows bridges abstract identity ("fitness tracker") and concrete architecture ("log workout → view history → track progress").

---

## Downstream Consumer Impact

The system was already designed to consume business context fields that didn't exist in the template. `new-milestone` step 4 explicitly references "problem/audience/USP" — fields that the original template never provided.

| Consumer | Reads From PROJECT.md | Benefits From New Sections |
|----------|----------------------|---------------------------|
| **design-phase** | What This Is, Core Value, Constraints | Who It's For (UX density), How It's Different (visual differentiation), Core Problem (which flows to emphasize) |
| **new-milestone** | All sections, references "problem/audience/USP" | All Layer 1 sections — already designed for them |
| **plan-phase** | @-references broadly | Moderate — Who It's For for task weighting |
| **create-roadmap** | Core Value, Constraints, existing reqs | Core Problem + Who It's For for scope validation |
| **discuss-phase** | Not currently (Session 3 adds this) | All Layer 1 sections for PO-style analysis |
| **transition / complete-milestone** | Full evolution review | "Has our understanding of audience/problem/differentiation evolved?" checks |

---

## Dream Extraction: Questioning Principles

> **Runtime reference:** `~/.claude/mindsystem/references/questioning.md`. This section documents design rationale for the questioning approach — not for `@-reference` at runtime.

PROJECT.md is populated through collaborative brainstorming during `/ms:new-project`. The questioning flow follows the **dream extraction** philosophy — the system is a thinking partner, not an interviewer.

### Core Truths

**People articulate by reacting, not generating.** When someone is fuzzy on their audience, asking "Who is your target audience?" forces generation from scratch. Offering concrete options to react to is easier: "Is this more for indie developers who want speed, or enterprise teams who need compliance?" AskUserQuestion with thoughtful, derived options unlocks fuzzy thinking.

**Clarity is non-uniform across dimensions.** A user might give crystal-clear audience understanding but completely fuzzy differentiation. The system needs per-section clarity tracking, not a global assessment. Spend questioning budget where clarity is lowest.

**Feature-first thinking is the default mode.** Most users think "I want to build X that does Y." This isn't wrong — features contain implicit business context. Derive audience, problem, and differentiation from feature descriptions before asking directly: "You described X, Y, Z — what problem do they all solve?"

**The "first 10 users" question beats the "target market" question.** Concrete grounding questions produce better answers than template-shaped questions:

| Section | Don't Ask | Ask Instead |
|---------|-----------|-------------|
| Who It's For | "Who is your target audience?" | "Who would be your first 10 users — real people you'd tell tomorrow?" |
| Core Problem | "What problem does this solve?" | "What triggered you to want to build this? What's broken today?" |
| How It's Different | "What's your USP?" | "What are people using today instead? What's wrong with it?" |
| Core Value | "What's most important?" | "If only ONE thing worked perfectly and everything else was mediocre, what would that one thing be?" |
| Key User Flows | "What are the key flows?" | "Walk me through a session. You open the app — then what?" |
| Success | "How do you define success?" | "Imagine this is wildly successful in a year. What does that look like?" |

**Success definition shapes everything.** "How will you know this worked?" reveals what actually matters — commercial viability, reliability, user experience, personal satisfaction. The answer directly informs Core Value and the weighting of all other sections.

**Challenging vague answers is a gift.** Users with fuzzy thinking often want to be challenged — they came to a brainstorming partner precisely because they need help sharpening ideas. "You said 'everyone' — but who needs this most?" is the kind of input that makes the product better before a line of code is written.

**Brownfield users know more than they can articulate.** They have deep implicit knowledge but haven't externalized it. "If someone at a dinner party asked what this app does, what would you say?" triggers natural explanation mode and prevents feature-level framing.

### Clarity Detection

**High clarity signals:** Specific demographics, named competitors, concrete scenarios, quantifiable outcomes, clear success metrics.
→ Confirm and move on. Probe one level deeper to test robustness at most.

**Low clarity signals:** Broad categories ("developers", "small businesses"), vague benefits ("makes things easier"), no competitor awareness ("nothing else does this"), feature-focused language, hedging ("I think", "maybe").
→ Offer frameworks. Provide concrete options via AskUserQuestion. Use scenarios to ground.

### The Flow Shape

```
1. OPEN
   Greenfield: "What do you want to build?"
   Brownfield: "Tell me about this project — what does it do, who uses it?"

2. LISTEN
   Let them dump their mental model. Follow energy. Don't interrupt with structure.

3. DERIVE
   Infer business context from what they said:
   "It sounds like this is for [audience] who struggle with [problem],
    and your approach is different because [differentiation]. Sound right?"

4. ASSESS
   Internally check: which template sections are clear? Which are fuzzy?

5. PROBE FUZZIEST
   Use grounding questions or AskUserQuestion with derived options
   for the lowest-clarity section. One area at a time.

6. REPEAT 4-5
   Until all sections have adequate clarity.

7. SUCCESS CHECK
   "How will you know this worked?" — if not yet covered.

8. SYNTHESIZE
   Present the complete picture for confirmation.

9. CREATE
   Write PROJECT.md.
```

Steps 4-6 are adaptive. A user with high clarity skips from step 3 to step 8. A user with fuzzy thinking cycles through 4-6 multiple times. The system adapts to the user.

### AskUserQuestion as a Sharpening Tool

When a user is stuck, options should be plausible interpretations derived from what they've said — not generic categories.

**Good** (derived from context):
```
"You mentioned workout tracking. Who specifically?"
→ "Gym regulars who follow structured programs"
→ "Casual exercisers who want to stay consistent"
→ "Athletes training for competition"
→ "Let me describe"
```

**Bad** (generic):
```
"Who is your audience?"
→ "Professionals"
→ "Consumers"
→ "Both"
```

Options should feel like the system already understands and is offering its best interpretations.

### Success-Backward Questioning

When the conversation pauses and sections are still fuzzy, flip direction: "Imagine this product is wildly successful in a year. What does that look like?"

This unlocks everything:
- "10,000 monthly active users" → audience scale expectations
- "My friends stop using spreadsheets" → audience + problem + competition
- "I never lose a workout log again" → Core Value (reliability)
- "People recommend it to each other" → differentiation (word-of-mouth quality)

Work backward from the success vision to fill remaining gaps.

---

## Evolution Strategy

After each phase transition (via transition workflow):
- Has "What This Is" drifted from reality?
- Core Value still the right priority?
- Has understanding of audience, problem, or differentiation evolved?
- New key flows emerged?
- Requirements to validate or invalidate?
- Key decisions to log?

After each milestone (via complete-milestone workflow):
- Full review of all sections
- Core Value audit against shipped reality
- Out of Scope audit — still valid boundaries?
- Technical Context updated with current state
