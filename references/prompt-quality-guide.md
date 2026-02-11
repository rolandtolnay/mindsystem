# Prompt Quality Guide

Philosophy and constraints for writing effective LLM prompts. Applies universally — commands, agents, system prompts, templates, any context where humans write instructions for LLMs to follow.

---

## How LLMs Process Instructions

### Finite Instruction-Following Capacity

Frontier LLMs follow ~150-200 instructions with reasonable consistency. System prompts and injected context consume a portion of that budget before your prompt even begins. Every instruction competes for the remaining capacity.

Adding one instruction dilutes all others. A low-value instruction actively degrades high-value ones. This means **each instruction must earn its place** — not by being correct or reasonable, but by measurably changing the LLM's behavior in the runtime context where the prompt executes.

Not all content costs equally against this budget:

- **Reference data** (commands, schemas, examples): Low cost. Factual context the LLM can't discover on its own.
- **Structural markers** (headers, XML containers, step labels): Low cost. They organize without competing for instruction slots.
- **Behavioral instructions** ("do X", "do NOT X"): Standard cost. One slot each.
- **Meta-commentary** ("this is important because..."): Standard cost with zero behavioral return.

### Positional Attention Bias

LLMs bias toward instructions at the **peripheries** of the prompt — the beginning and the end. Instructions buried in the middle receive the least attention.

- **Beginning:** Objective, critical constraints, essential reference data
- **Middle:** Elaboration and process details (keep lean — this is the attention trough)
- **End:** Success criteria, closing reinforcement of what matters most

Restating a critical instruction at the end of a prompt is not redundancy — it's **peripheral reinforcement**. The items the LLM is most likely to skip should appear first in end-of-prompt criteria.

### Context Is a Shared, Depletable Resource

Every token in the prompt competes with the LLM's reasoning and output for the same context window. Output quality degrades predictably as context fills:

| Context usage | Quality |
|---|---|
| 0-30% | Peak |
| 30-50% | Good |
| 50-70% | Degrading — starts cutting corners |
| 70%+ | Poor |

A verbose prompt that fills 15% of context before the LLM begins working is already handicapping output quality. Shorter, more focused prompts leave more room for the LLM's actual work.

**Implication:** When two approaches produce equivalent results, choose the one consuming less context. This applies to prompt design, reference loading, and how much supporting material gets injected.

### Default Behaviors Shift With Context

LLMs have strong defaults, but those defaults become unreliable as context grows. An LLM in a 500-token conversation reliably uses its tools. The same LLM in a 50,000-token context with a large system prompt may forget specific tools exist.

This makes the value test more nuanced than "does the LLM know this?" The real question is: **"Does the LLM reliably do this given everything else competing for its attention?"**

- A tool reminder is waste in a minimal prompt but critical in a large, complex context
- A formatting instruction is unnecessary for short outputs but essential when the LLM generates long, structured responses
- A constraint the LLM follows by default may need explicit reinforcement when surrounded by many other instructions

**Test instructions against the actual runtime context**, not against the LLM's theoretical capabilities.

---

## Core Philosophy

### The Value of a Prompt Is Its Behavioral Overrides

Everything in a prompt that doesn't change the LLM's behavior is noise. The question for every instruction: *"If I remove this, does the output get worse in the context where this prompt runs?"*

- If removing it changes nothing → it wastes budget and dilutes everything else
- If removing it causes failures → it earns its place regardless of whether it seems redundant

This test must be empirical, not theoretical. "The LLM should know this" is irrelevant if it doesn't reliably act on it. Conversely, instructions that seem obviously unnecessary may be load-bearing in practice. Trust observed behavior over assumptions.

### Specificity Over Abstraction

Specific instructions outperform vague ones. "Return a JSON object with fields `name` (string) and `age` (integer)" beats "return structured data." Concrete examples anchor abstract rules and reduce the space of valid interpretations.

When a prompt includes rules, show what compliance looks like. When it includes constraints, show what violation looks like. The more concrete the instruction, the less room for the LLM to drift.

### Patterns and Anti-Patterns Work Together

Showing the right way ("do this") and the wrong way ("not this") are complementary techniques. Anti-patterns aren't wasted negation — they're **contrastive anchoring**. Seeing the wrong pattern makes the right pattern clearer and easier to detect.

The waste to avoid is negating **unlikely behaviors** — telling the LLM not to do something it wasn't going to do. This activates the concept without benefit. But negating **observed failure modes** (things the LLM actually does wrong) is high-value, especially when paired with the correct alternative.

### Progressive Disclosure

Load information only when needed. Not every reference, example, or constraint needs to be present from the start.

- **Eager loading:** Content injected into the prompt before the LLM begins. In practice, this means `@file` references or inline content that gets expanded at prompt assembly time. The LLM sees it immediately. Use for content needed on every execution path.
- **Lazy loading:** Content the LLM fetches during execution when a condition is met. In practice, this means a read instruction inside the prompt: "If type is `tdd`, read `tdd-reference.md`." The content only enters context when the LLM decides it's needed.

Default to lazy. Promote to eager only when the content is essential regardless of execution path. Every token loaded upfront that goes unused is pure context waste.

### Imperative Voice

"Create the file" not "the file should be created." Imperative sentences are shorter, less ambiguous, and map directly to actions. Passive voice adds tokens without adding information.

### No Filler, No Sycophancy

Words that carry zero information content — "Let me", "Simply", "Basically", "I'd be happy to", "Great question!" — waste both prompt tokens and output tokens. Direct instructions and factual statements only.

---

## Evaluating Instructions

### The Reliability Test

For each instruction in a prompt, ask:

1. **Does removing this degrade output in the actual runtime context?** Not in theory — in practice, with the full system prompt and injected context present. If no, remove.
2. **Is this positioned for attention?** High-skip-risk items belong at the beginning or end, not buried in the middle.
3. **If this is a negation, does the LLM actually exhibit the unwanted behavior?** If not, the negation activates the concept without benefit. Remove.
4. **Is this restated elsewhere?** Duplication at the same position is waste. Duplication across positions (process step + success criterion) is peripheral reinforcement and may be intentional.
5. **Could this be shorter without losing meaning?** Fewer tokens = less budget consumed.

### Success Criteria

Success criteria at the end of a prompt serve as peripheral reinforcement — a final pass of attention over what matters most.

- Order by **skip risk** (highest first) — the things the LLM is most likely to forget or shortcut
- Omit items for steps the LLM never skips (obvious first steps, routine actions)
- Keep to 5-7 items — each additional item dilutes all others
- Use concrete, verifiable language, not vague aspirations

### Common Waste

| Pattern | Example | Problem |
|---|---|---|
| Meta-commentary | "Thoroughness is more important than speed" | The concrete instructions below already enforce this |
| Architecture rationale | "This design survives context resets" | Explains *why*, not *what to do* |
| Negations of unlikely behavior | "Do NOT delete the database" | LLM wasn't going to; negation activates the concept |
| Low-risk success criteria | "File was read successfully" | LLM never skips this; reinforce what it *does* skip |
| Filler and sycophancy | "Simply", "I'd love to help" | Zero information content |
| Verbose restatement | "IMPORTANT: You must always ensure that..." | Same instruction at 3x the token cost |

### Common Value

| Pattern | Example | Why it earns its place |
|---|---|---|
| Reference data | `uv run script.py get $ARGUMENTS` | LLM cannot discover this on its own |
| Behavioral overrides | "Read files yourself, don't rely on summaries" | Counteracts a real observed tendency |
| Tool reminders | "Use AskUserQuestion to clarify" | Specific tools get lost in large contexts |
| Separation constraints | "Do NOT combine steps 3 and 4" | Prevents a verified failure mode |
| Confidence gates | "Do NOT proceed until 95% confident" | Prevents premature phase transitions |
| Contrastive examples | Right pattern paired with wrong pattern | Anchors rules through contrast |
| Output format specifications | Exact structure with example | LLM needs the format, not "be concise" |
