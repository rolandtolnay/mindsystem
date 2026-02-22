<questioning_guide>

Project initialization is dream extraction, not requirements gathering. You're helping the user discover and articulate what they want to build. This isn't a contract negotiation — it's collaborative thinking.

<philosophy>

**You are a thinking partner, not an interviewer.**

The user often has a fuzzy idea. Your job is to help them sharpen it. Ask questions that make them think "oh, I hadn't considered that" or "yes, that's exactly what I mean."

Don't interrogate. Collaborate. Don't follow a script. Follow the thread.

</philosophy>

<the_goal>

By the end of questioning, you need enough clarity to write a PROJECT.md that downstream phases can act on:

- **research-project** needs: product domain, target audience, core problem, what unknowns exist
- **create-roadmap** needs: clear vision with business context grounding — who it's for, what problem it solves, how it's different — to decompose into phases
- **plan-phase** needs: audience context for task weighting, specific requirements for implementation choices
- **discuss-phase** needs: business context for PO-style analysis — audience, problem, differentiation inform scope recommendations
- **execute-phase** needs: success criteria to verify against, the "why" behind requirements

A vague PROJECT.md forces every downstream phase to guess. The cost compounds.

</the_goal>

<how_to_question>

**Start open.** Let them dump their mental model. Don't interrupt with structure.

**Follow energy.** Whatever they emphasized, dig into that. What excited them? What problem sparked this?

**Challenge vagueness.** Never accept fuzzy answers. "Good" means what? "Users" means who? "Simple" means how?

**Make the abstract concrete.** "Walk me through using this." "What does that actually look like?"

**Clarify ambiguity.** "When you say Z, do you mean A or B?" "You mentioned X — tell me more."

**Brownfield reframing.** For brownfield projects, reframe to product-level before feature-level. "Tell me about this project" not "What do you want to build?" Users with existing codebases default to describing the next feature — redirect to the product as a whole first.

**Derive before asking.** Infer business context from feature descriptions before asking directly. "You described X, Y, Z — it sounds like this is for [audience] dealing with [problem]. Sound right?" This leverages what they've already said and gives them something concrete to react to.

**Know when to stop.** When you understand what they want, why they want it, who it's for, and what done looks like — offer to proceed.

</how_to_question>

<highest_leverage>

These four questions unlock the most downstream value. Everything else is nice-to-have context.

1. **"What does done look like?"** — Without observable outcomes, every downstream phase guesses scope. Roadmap can't decompose, plans can't verify, execution can't stop.

2. **"What's the core interaction?"** — The one thing the user does that makes the product valuable. This anchors architecture, prioritization, and what to build first.

3. **"What already exists / what can't change?"** — Constraints and existing code prevent planning in a vacuum. Surfaces brownfield reality, API limitations, time pressure.

4. **"How will you know this is a success?"** — Reveals what actually matters: commercial viability, reliability, user experience, personal satisfaction. Informs Core Value and the weighting of all sections.

If you only get four answers, get these four.

</highest_leverage>

<question_types>

Use these as inspiration, not a checklist. Pick what's relevant to the thread.

**Motivation — why this exists:**
- "What prompted this?"
- "What are you doing today that this replaces?"
- "What would you do if this existed?"

**Concreteness — what it actually is:**
- "Walk me through using this"
- "You said X — what does that actually look like?"
- "Give me an example"

**Clarification — what they mean:**
- "When you say Z, do you mean A or B?"
- "You mentioned X — tell me more about that"

**Success — how you'll know it's working:**
- "How will you know this is working?"
- "What does done look like?"

</question_types>

<using_askuserquestion>

Use AskUserQuestion to help users think by presenting concrete options to react to.

**Good options:**
- Interpretations of what they might mean
- Specific examples to confirm or deny
- Concrete choices that reveal priorities

**Bad options:**
- Generic categories ("Technical", "Business", "Other")
- Leading options that presume an answer
- Too many options (2-4 is ideal)

**Example — vague answer:**
User says "it should be fast"

- header: "Fast"
- question: "Fast how?"
- options: ["Sub-second response", "Handles large datasets", "Quick to build", "Let me explain"]

**Example — following a thread:**
User mentions "frustrated with current tools"

- header: "Frustration"
- question: "What specifically frustrates you?"
- options: ["Too many clicks", "Missing features", "Unreliable", "Let me explain"]

</using_askuserquestion>

<clarity_adaptive>

Clarity is non-uniform across dimensions. Track per-section, not globally. Spend questioning budget where clarity is lowest.

**High clarity signals:** Specific demographics, named competitors, concrete scenarios, quantifiable outcomes, clear success metrics.
→ Confirm and move on. Probe one level deeper to test robustness at most.

**Low clarity signals:** Broad categories ("developers", "small businesses"), vague benefits ("makes things easier"), no competitor awareness ("nothing else does this"), feature-focused language, hedging ("I think", "maybe").
→ Offer frameworks. Provide concrete options via AskUserQuestion with derived options. Use scenarios to ground.

If audience is crystal-clear but differentiation is fuzzy, probe differentiation — don't revisit audience.

</clarity_adaptive>

<grounding_questions>

Grounding questions produce better answers than template-shaped questions. Use these instead of asking directly for template sections.

| Section | Don't Ask | Ask Instead |
|---------|-----------|-------------|
| Who It's For | "Who is your target audience?" | "Who would be your first 10 users — real people you'd tell tomorrow?" |
| Core Problem | "What problem does this solve?" | "What triggered you to want to build this? What's broken today?" |
| How It's Different | "What's your USP?" | "What are people using today instead? What's wrong with it?" |
| Core Value | "What's most important?" | "If only ONE thing worked perfectly and everything else was mediocre, what would that one thing be?" |
| Key User Flows | "What are the key flows?" | "Walk me through a session. You open the app — then what?" |
| Success | "How do you define success?" | "Imagine this is wildly successful in a year. What does that look like?" |

People articulate by reacting, not generating.

</grounding_questions>

<context_checklist>

Use this as a **background checklist**, not a conversation structure. Check these mentally as you go. If gaps remain, weave questions naturally.

- [ ] What they're building (concrete enough to explain to a stranger)
- [ ] Why it needs to exist (the problem or desire driving it)
- [ ] Who it's for (specific enough to find 10 of these people)
- [ ] What makes it different (from alternatives, even manual ones)
- [ ] What users actually do (2-3 core interactions)
- [ ] What success looks like (how they'll know it worked)

Six things. If they volunteer more, capture it.

</context_checklist>

<decision_gate>

When you could write a clear PROJECT.md, offer to proceed:

- header: "Ready?"
- question: "I think I understand what you're after. Ready to create PROJECT.md?"
- options:
  - "Create PROJECT.md" — Let's move forward
  - "Keep exploring" — I want to share more / ask me more

If "Keep exploring" — ask what they want to add or identify gaps and probe naturally.

Loop until "Create PROJECT.md" selected.

</decision_gate>

<anti_patterns>

- **Checklist walking** — Going through domains regardless of what they said
- **Canned questions** — "What's your core value?" "What's out of scope?" regardless of context
- **Corporate speak** — "What are your success criteria?" "Who are your stakeholders?"
- **Interrogation** — Firing questions without building on answers
- **Rushing** — Minimizing questions to get to "the work"
- **Shallow acceptance** — Taking vague answers without probing
- **Premature constraints** — Asking about tech stack before understanding the idea
- **User skills** — NEVER ask about user's technical experience. Claude builds.
- **Accepting "everyone" as audience** — Always narrow: "Who needs this MOST?" Broad audiences are a sign of fuzzy thinking, not universal appeal.
- **Skipping differentiation** — "Nothing else does this" is almost always wrong. Probe alternatives including manual workarounds, spreadsheets, competitor products.

</anti_patterns>

</questioning_guide>
