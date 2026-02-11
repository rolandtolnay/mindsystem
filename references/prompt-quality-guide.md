# Prompt Quality Guide

Universal reference for evaluating and improving prompts, commands, agents, and LLM-facing documentation. Applies to any system where humans write instructions that LLMs execute.

---

## LLM Cognitive Model

Effective prompting requires understanding how LLMs actually process instructions — not how humans read documents.

### The Instruction Budget

Frontier LLMs follow ~150-200 instructions with reasonable consistency. System prompts (Claude Code, API wrappers, etc.) consume ~50 of those. Every instruction in your prompt competes for the remaining budget.

**Each instruction must earn its place.** A low-value instruction actively degrades a high-value one by diluting attention across more items.

Not all content costs equally:

| Content type | Budget cost | Notes |
|---|---|---|
| Reference data (bash commands, API formats, code examples) | Low | Factual context, not behavioral directives |
| Structural markers (`<step>`, `## Headers`) | Low | Organize without competing for instruction slots |
| Affirmative instructions ("do X") | Standard | One instruction slot each |
| Negation instructions ("do NOT X") | Standard | Often wasted on behaviors the LLM wasn't going to exhibit |
| Meta-commentary ("this is important because...") | Standard cost, zero behavioral return | Pure waste |

### Positional Attention Bias

LLMs bias toward instructions at the **peripheries** — the very beginning and the very end. The middle receives the least attention.

Structure prompts accordingly:

- **Beginning:** Objective, critical context, reference data (commands, API formats, schemas)
- **Middle:** Behavioral overrides that need elaboration (keep lean)
- **End:** Success criteria focused on high-skip-risk items; closing reinforcement of what matters most

Success criteria at the end are not duplication — they are **peripheral reinforcement**. Place the items the LLM is most likely to skip first in the list.

### Context Quality Degradation

LLM output quality degrades predictably as context fills:

| Context usage | Quality level |
|---|---|
| 0-30% | Peak quality |
| 30-50% | Good quality |
| 50-70% | Degrading — LLM starts cutting corners |
| 70%+ | Poor quality |

**The 50% rule:** Work should complete within ~50% context usage. Stop before quality degrades, not at the context limit. Every token that doesn't improve output is waste.

**Implication for prompts:** Shorter, more focused prompts leave more context for the LLM's actual work — reasoning, code generation, analysis. A verbose 2000-line prompt that fills 15% of context before the LLM writes a single line is already handicapping output quality.

### Default Behaviors vs. Overrides

LLMs have strong default behaviors. The value of a prompt is the set of **behavioral overrides** it induces. Everything else is noise.

**The behavioral override test:** For every instruction, ask: *"Does the LLM already do this without being told?"*

- If yes → remove it (wastes budget)
- If no → keep it (this is the prompt's actual value)

---

## Prompt Architecture

### Section Ordering (for commands and workflow prompts)

1. **Objective** — What, why, when (always present, always first)
2. **Context** — Reference data, file contents, dynamic inputs
3. **Process** — Steps to follow, behavioral overrides
4. **Success criteria** — Measurable completion checklist (always last)

This maps to how LLMs process: understand the goal → absorb context → execute steps → self-verify against criteria.

### Semantic Containers

Use containers that communicate **purpose**, not structure.

**Good:** `<objective>`, `<verification>`, `<action>`, `<context>`

**Bad:** `<section>`, `<item>`, `<content>`, `<subsection>`

Use markdown headers for hierarchy within containers. Containers mark semantic boundaries; headers organize content within those boundaries.

### Progressive Disclosure

Load information only when needed. Two mechanisms:

- **Eager loading** (`@file` references, inline content): For files that are always essential. Content injected upfront into prompt context.
- **Lazy loading** (read instructions during execution): For conditionally needed files. "If type is `tdd`, read `tdd-reference.md`."

Default to lazy. Promote to eager only when the content is needed on every execution path.

### Separation of Concerns

Prompts serve one reader doing one job. Mixing audiences creates waste.

| Keep separate | Because |
|---|---|
| Orchestration vs. execution | Executors don't need wave grouping or dependency info |
| Instructions vs. rationale | LLMs need "what to do", not "why the design works" |
| Process vs. output format | Process governs behavior; output format governs artifacts |
| Reference data vs. behavioral rules | Different budget costs, different update frequencies |

---

## Content Principles

### Terseness Over Explanation

- Single-line rules; no paragraphs where a line suffices
- Sacrifice grammar for brevity: `"Label optional fields"` not `"You should always label optional fields explicitly"`
- No "why" explanations — rules are self-evident or trust is assumed
- Remove noise words: no `IMPORTANT:`, `YOU MUST`, `Please ensure`

### Concrete Syntax Inline

Show the pattern directly in the rule:

**Good:** `Early return: if (items.isEmpty) return const SizedBox.shrink();`

**Bad:** "When a collection is empty, you should return an empty widget early to avoid unnecessary rendering."

- Arrow notation for transformations: `.toList()..sort()` → `.sorted()`
- Backticks for all identifiers: `useState`, `AsyncValue.guard()`

### Flat Hierarchy

- Maximum two levels: `Category → Rules`
- No nested subcategories
- Categories as H2/H3 headers, rules as bullet points
- Consolidate overlapping categories

Deep nesting wastes structural tokens and makes rules harder for LLMs to index against input.

### Affirmative Over Negation

Affirmative instructions ("do X") are more reliable than negations ("do NOT X"). Negations require the LLM to:

1. Understand the unwanted behavior
2. Activate the concept
3. Suppress it

This is cognitively expensive and failure-prone. Use negations only when the LLM **actually exhibits** the unwanted behavior (verified through testing).

### Imperative Voice

**Do:** "Execute tasks", "Create file", "Return JSON"

**Don't:** "Tasks should be executed", "The file should be created"

Imperative sentences are shorter, less ambiguous, and map directly to actions.

---

## Document Formats

Different prompt artifacts serve different purposes and optimize for different readers.

### Commands (User-Facing Entry Points)

Thin wrappers that delegate to workflows. Contain:

- Objective (what/why/when)
- Context injection (dynamic inputs, file references)
- High-level process overview
- Success criteria

Commands answer: *"Should I use this?"*

### Workflows (Detailed Procedures)

Step-by-step execution logic. Where behavioral overrides and process details live.

Commands and workflows must stay in sync — same steps at different detail levels.

### Reference Documents (LLM-Optimized Knowledge)

Structured for fast pattern matching during code review or analysis:

```
# Title

Review instruction with $ARGUMENTS

## Rules

### Category Name
- Rule with `inline code` example
- Transformation: `bad` → `good`

## Anti-Patterns (flag these)
- Bad pattern (use X instead)
- `concrete.bad.code()` (explanation)

## Output Format
file:line - issue → fix
```

Key properties:
- No introductory paragraphs or rationale
- Concrete code inline with every rule
- Dedicated anti-patterns section (mirror rules in negative form)
- Explicit output format with example

### Plans (Executable Prompts)

Pure markdown — no XML containers, no YAML frontmatter. ~90% actionable content, ~10% structure. Plans ARE the prompt, not a document that gets transformed.

**Specificity test:** Can the executor start implementing without clarifying questions? If not, the plan is too vague.

---

## Waste Patterns

Instructions that consume budget without changing behavior:

| Pattern | Example | Why it wastes budget |
|---|---|---|
| Tool-usage instructions | "use the Skill tool", "call Read" | LLM knows its own tools |
| Meta-commentary | "Thoroughness is more important than speed" | Concrete instructions below already enforce this |
| Architecture rationale | "These steps survive the context reset" | Explains *why*, not *what to do* |
| Negations of unlikely behavior | "Do NOT run the CLI directly" | LLM wasn't going to; negation activates the concept |
| Low-risk success criteria | "Ticket details fetched and understood" | LLM never skips step 1 — reinforce what it *does* skip |
| Filler phrases | "Let me", "Simply", "Basically", "I'd be happy to" | Zero information content |
| Sycophancy prompts | "Great question!", "Excellent choice!" | Wastes output tokens, degrades professional tone |
| Verbose rule statements | "IMPORTANT: You must always ensure that..." | Same rule, 3x the tokens |

### Patterns That Earn Their Place

| Pattern | Example | Why it's needed |
|---|---|---|
| Reference data | `uv run script.py get $ARGUMENTS` | LLM cannot discover this on its own |
| Behavioral overrides | "Read files yourself, don't rely on agent summaries" | Counteracts a real default tendency |
| Separation constraints | "Do NOT combine steps 3 and 4" | Prevents a verified failure mode |
| Confidence gates | "Do NOT proceed until 95% confident" | Prevents premature transitions |
| Gap-hunting checklists | Bullet list of ambiguity types to look for | Provides structure LLM wouldn't generate |
| Concrete code examples | `bad pattern` → `good pattern` | Anchors abstract rules to specific syntax |
| Output format specifications | `file:line - issue → fix` | LLM needs exact format, not just "be concise" |

---

## Quality Evaluation

### Per-Instruction Scoring

For each instruction in a prompt:

1. **Does this change behavior?** If the LLM would do the same thing without this instruction, remove it.
2. **Is this positioned correctly?** High-risk items at beginning or end, not buried in the middle.
3. **Affirmative or negating?** If negating, does the LLM actually exhibit the unwanted behavior? If not, remove.
4. **Is this a duplicate?** Success criteria may intentionally duplicate process steps (peripheral reinforcement). Two instructions in the same position saying the same thing is waste.
5. **Could this be shorter?** Fewer tokens = cheaper against the budget.

### Success Criteria Design

Success criteria serve as **end-of-prompt reinforcement**, not a cross-reference checklist.

- Order by **skip risk** (highest first) — items the LLM is most likely to forget
- Omit items for steps the LLM never skips (early steps, obvious actions)
- Maximum 5-7 items — each one dilutes the others
- Concrete, verifiable language: `"commit message includes [TICKET-ID]"` not `"code is clean"`

### The Quality x Speed Tradeoff

Every prompt feature exists on a spectrum:

- **Quality gates** — Steps that measurably improve output (verification catches real mismatches, checklists catch real omissions). Worth their token cost.
- **Engineering noise** — Steps that add overhead without measurably influencing output (redundant checks, verbose explanations, ceremony). Must be eliminated.

**Decision principle:** Does this step's quality improvement justify its context cost? If not, it's noise — remove it regardless of how reasonable it sounds in theory.

---

## Revision Process

When trimming an existing prompt:

1. **Count behavioral overrides** — things the LLM wouldn't do without this prompt
2. **Count everything else**
3. **Remove "everything else"** unless it's reference data or structural markers
4. **Check positioning** — anything in the middle that should be at the peripheries?
5. **Tighten success criteria** to high-skip-risk items only
6. **Compress verbose rules** to single-line with inline code examples
7. **Extract anti-patterns** to a dedicated section (enables fast pattern matching)
8. **Verify specificity** — can the LLM execute without clarifying questions?

### Transformation Checklist (Verbose → LLM-Optimized)

1. Delete introductory paragraphs and rationale
2. Compress sentences to single-line rules
3. Add concrete code inline with backticks
4. Use arrow `→` for before/after patterns
5. Consolidate overlapping sections
6. Extract violations to anti-patterns section
7. Add output format with concrete example
8. Remove all filler: "basically", "should", "please", "important"
