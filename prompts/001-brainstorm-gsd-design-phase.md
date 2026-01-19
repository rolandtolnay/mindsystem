<objective>
Conduct a COLLABORATIVE brainstorming session to design a UI/UX design phase for the GSD (Get Shit Done) workflow system.

The GSD system currently produces functional code but lacks a design step, resulting in UI output that doesn't follow UI/UX best practices and isn't visually engaging. Your goal is to investigate the existing GSD architecture, research design-in-prompts techniques, and work WITH THE USER to determine how to integrate a design phase that produces beautiful, professional-grade interfaces.

This is an INTERACTIVE RESEARCH session. Do NOT write the final proposal until you have achieved complete clarity and confidence through collaboration with the user. Use AskUserQuestion liberally throughout.
</objective>

<collaboration_approach>
## Critical: This is a Collaborative Session

**Do NOT rush to produce output.** This brainstorming session succeeds through dialogue, not one-shot generation.

### Use AskUserQuestion Tool Extensively

Use AskUserQuestion at these key moments:

1. **After each research phase** - Share what you learned and ask for the user's reaction before proceeding
2. **At every major decision point** - Present options with trade-offs and let the user choose direction
3. **When you have assumptions** - Surface them explicitly and verify before building on them
4. **When trade-offs exist** - Don't decide unilaterally; present options and get user input
5. **Before finalizing any section** - Confirm the approach aligns with user's vision

### Question Patterns to Use

**After research:**
```
"I've analyzed [X]. Here's what I found: [summary].
Does this match your understanding? Any corrections or additions?"
```

**At decision points:**
```
"There are [N] approaches to [decision]:
- Option A: [description] - pros/cons
- Option B: [description] - pros/cons
Which direction resonates with you?"
```

**Surfacing assumptions:**
```
"I'm assuming [assumption]. Is this correct, or should I adjust?"
```

**Before proceeding:**
```
"Based on our discussion, I'm thinking [approach].
Ready to move on, or should we explore further?"
```

### Confidence Gate

**Do NOT write the final proposal until:**
- You have discussed findings from ALL research phases with the user
- Major architectural decisions have been made collaboratively
- The user has confirmed the overall direction
- You have 95%+ confidence you understand what to build

When in doubt, ASK. Thoroughness beats speed.
</collaboration_approach>

<context>
## The Problem
GSD executes plans through subagents that write code directly from requirements. There is no design step, so UI features often look "ugly" - functional but not beautiful or engaging. The code works, but the visual output doesn't respect UI/UX best practices.

## Current Workarounds Attempted
- Using `/gsd:discuss-phase` to describe envisioned designs - helps somewhat but not ideal
- No systematic approach to design before implementation

## Technology Stacks
- **Web projects**: React/Next.js + Tailwind CSS
- **Mobile projects**: Flutter/Dart
- Different UI/UX principles apply to each platform

## Key Reference Document
Read and deeply study: @ai-driven-ui-design-system.md

This document contains proven patterns for AI-driven design including:
- Quality-forcing patterns (commercial benchmark, pre-emptive criticism, mandatory self-review)
- Three-tier architecture (Orchestrator → Design Agent → Implementation Agent)
- 12-section aesthetic template for visual systems
- Platform-specific validation rules
- Anti-patterns to avoid

## Project Context
- Some projects have an "implement-ui" skill documenting existing widgets/patterns
- Novel features require novel designs that harmonize with existing app aesthetics
- Need to support both web and mobile with different design agents
</context>

<research_requirements>
## Phase 1: Understand GSD Architecture

1. **Read and analyze GSD's core workflow files:**
   - All commands in `commands/gsd/*.md`
   - All workflows in `get-shit-done/workflows/*.md`
   - Agent definitions in `agents/*.md`
   - Templates in `get-shit-done/templates/*.md`

2. **Map the current execution flow:**
   - How does `/gsd:plan-phase` create PLAN.md files?
   - How does `/gsd:execute-phase` invoke executor agents?
   - What context gets passed to executors?
   - Where would design naturally fit?

3. **Identify integration points:**
   - Could design happen during `/gsd:plan-phase`?
   - Should it be a separate `/gsd:design-phase` command?
   - Should design be part of the executor's workflow?
   - How would design artifacts flow to implementation?

## Phase 2: Research Design-in-Prompts Techniques

1. **Study the AI-driven design document thoroughly:**
   - Extract all quality-forcing patterns
   - Understand the three-tier orchestration model
   - Note the 12-section aesthetic template structure
   - Catalog platform-specific considerations

2. **Research additional techniques:**
   - How do other systems handle LLM-driven design?
   - What prompting techniques produce better visual output?
   - How can ASCII art effectively represent layouts?
   - What level of specification detail helps implementation?

3. **Investigate screenshot/image input feasibility:**
   - Can Claude Code agents receive image input?
   - What's the context window cost of screenshot analysis?
   - How would this affect other workflow steps?
   - Is this practical or should we use text descriptions only?

## Phase 3: Design Agent Architecture

1. **Determine agent structure:**
   - Should there be separate mobile and web design agents?
   - What tools does a design agent need?
   - Should design run in fresh context (like executors)?
   - How to handle design iteration/refinement?

2. **Define design output format:**
   - ASCII layout representation
   - Detailed design specifications (spacing, colors, typography, states)
   - Platform-specific requirements (touch targets, safe areas, etc.)
   - How executor agents will consume this output

3. **Consider existing project context:**
   - How to reference existing "implement-ui" skills
   - How to ensure novel designs harmonize with existing aesthetics
   - How to capture project-level design systems

## Phase 4: Workflow Integration

1. **Placement decision:**
   - Evaluate: Before planning vs during planning vs before execution
   - Consider context window implications
   - Consider user workflow (when do they want to review designs?)

2. **Iteration workflow:**
   - How does user review and provide feedback on designs?
   - How to handle design refinement before implementation?
   - Should there be a "design checkpoint" gate?

3. **Artifact management:**
   - Where do design files live? (`.planning/designs/`?)
   - How do PLAN.md files reference design specs?
   - How do executors load design context?
</research_requirements>

<output_specification>
## Deliverable: Design Proposal Document

Create: `./proposals/gsd-design-phase-proposal.md`

Structure the proposal with these sections:

### 1. Executive Summary
- Problem statement
- Proposed solution (1-2 paragraphs)
- Key benefits

### 2. Research Findings
- GSD architecture analysis
- Design-in-prompts techniques catalog
- Screenshot input feasibility assessment
- Platform-specific considerations (web vs mobile)

### 3. Proposed Architecture
- Where design fits in GSD workflow
- Agent structure (with rationale for choices)
- Output format specification
- Context flow diagram (ASCII)

### 4. Design Agent Specification
- Agent type: skill, subagent, or command
- Required tools
- Prompt structure (with quality-forcing patterns)
- Platform variants (web agent vs mobile agent)

### 5. Design Output Format
- ASCII layout template
- Design specification schema
- Example output for a sample feature
- How executors consume this

### 6. Iteration Workflow
- User review process
- Feedback integration
- Refinement loop
- When to proceed to implementation

### 7. Integration Plan
- New/modified commands
- New/modified workflows
- New agents needed
- File structure changes

### 8. Open Questions
- Decisions that need user input
- Trade-offs to consider
- Areas needing further research

### 9. Recommended Next Steps
- Prioritized implementation order
- Quick wins vs larger changes
- What to prototype first
</output_specification>

<research_approach>
## How to Conduct This Research (With Collaboration Checkpoints)

### Phase 1: GSD Architecture Analysis
1. Use Glob to find all relevant files
2. Read commands, workflows, agents, templates systematically
3. Build understanding of how context flows through the system

**→ CHECKPOINT: Use AskUserQuestion**
- Share your understanding of GSD's architecture
- Ask: "Does this match how you use GSD? Any workflows I'm missing?"
- Clarify any misunderstandings before proceeding

### Phase 2: Design Document Deep Dive
1. Read @ai-driven-ui-design-system.md thoroughly
2. Extract patterns that apply to GSD integration
3. Note what would need adaptation

**→ CHECKPOINT: Use AskUserQuestion**
- Share key patterns you identified
- Ask: "Which of these patterns resonate most? Any you'd deprioritize?"
- Discuss how strictly to follow the three-tier model

### Phase 3: Explore Integration Options
1. Identify possible integration points (before planning, during planning, before execution)
2. Consider context window implications
3. Map out trade-offs for each approach

**→ CHECKPOINT: Use AskUserQuestion**
- Present integration options with trade-offs
- Ask: "Where do you imagine design fitting in your workflow?"
- Get user preference before designing architecture

### Phase 4: Design Agent Architecture
1. Based on user's chosen integration point, design agent structure
2. Define output format and how executors consume it
3. Plan iteration/feedback workflow

**→ CHECKPOINT: Use AskUserQuestion**
- Present proposed agent architecture
- Ask: "Does this structure make sense? Anything to adjust?"
- Confirm output format meets user's needs

### Phase 5: Finalize and Write Proposal
**Only proceed to this phase when:**
- All previous checkpoints passed
- User has confirmed direction at each decision point
- You have 95%+ confidence in the approach

Then synthesize everything into the proposal document.
</research_approach>

<quality_requirements>
## What Makes This Proposal Successful

- **Grounded in GSD reality**: Proposals must work with GSD's actual architecture, not hypothetical systems
- **Actionable recommendations**: Each section should lead to clear next steps
- **Trade-offs explicit**: Don't hide complexity - acknowledge where decisions are hard
- **Platform-aware**: Web (React/Tailwind) and Mobile (Flutter) need different treatment
- **Context-conscious**: Remember Claude's context window limitations
- **Iteration-friendly**: The design workflow should support refinement, not just one-shot generation
- **Quality-forcing**: Incorporate patterns from the design document that prevent generic output
</quality_requirements>

<success_criteria>
## Collaboration Success Criteria

Before writing the final proposal, verify:

- [ ] **Phase 1 checkpoint passed** - User confirmed understanding of GSD architecture
- [ ] **Phase 2 checkpoint passed** - User selected which design patterns to prioritize
- [ ] **Phase 3 checkpoint passed** - User chose integration point (where design fits)
- [ ] **Phase 4 checkpoint passed** - User approved agent architecture and output format
- [ ] **All major decisions made collaboratively** - No unilateral architectural choices
- [ ] **95%+ confidence achieved** - You know exactly what to build

## Proposal Completeness Criteria

The final proposal must include:

- [ ] GSD architecture analysis (commands, workflows, agents)
- [ ] AI-driven design document patterns extracted and applied
- [ ] Clear recommendation on where design fits in workflow (user-validated)
- [ ] Design agent specification that is concrete and implementable
- [ ] Output format defined with examples
- [ ] Iteration workflow addressing user feedback loop
- [ ] Screenshot input feasibility assessed with recommendation
- [ ] Web vs mobile differences addressed
- [ ] Integration plan that is actionable
- [ ] Any remaining open questions for future consideration
</success_criteria>
