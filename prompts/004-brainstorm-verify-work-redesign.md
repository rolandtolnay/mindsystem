<objective>
Conduct a collaborative brainstorming session to scope and produce a full implementation spec for redesigning `/gsd:verify-work`. The goal is a proposal detailed enough to execute directly in a fresh context.

You are working with the GSD framework maintainer to redesign the verify-work command. The current implementation has friction points around context switching (verify → log → plan gaps → execute gaps → verify again) and inability to test UI states requiring mocks (premium user, error states, empty states).

The desired end state: run verify-work and by session end, have everything verified, issues fixed, and tests passing — all in one flow.
</objective>

<execution_context>
**Invoke gsd-meta skill first** — load GSD domain knowledge before proceeding.

Key GSD files to reference during exploration:
@commands/gsd/verify-work.md
@get-shit-done/workflows/verify-work.md
@get-shit-done/workflows/diagnose-issues.md
@get-shit-done/templates/UAT.md
@agents/gsd-debugger.md
@agents/gsd-executor.md
</execution_context>

<context>
**User's draft proposal** (problem + initial ideas):
@proposals/verify-work-redesign-draft.md

**Fixed decisions** (do not revisit):
- Test source: Keep SUMMARY.md (test what was actually built)
- Fix timing: Fix immediately while mocks are active (don't batch failures to end)
- Framework: Design framework-agnostic patterns (not Flutter-specific)
- Session state: Keep persistence (UAT.md survives /clear for interruptions)
- Debug approach: Build on existing /gsd:debug and gsd-debugger agent
- Proposal format: Full spec (workflow, templates, subagent configs — ready to implement)

**Decisions to explore** (use AskUserQuestion to converge):
1. Mock lifecycle: temporary file + git revert vs conditional compilation vs other
2. Agent architecture: multi-agent (mock generator, fixer, cleanup) vs single unified verify-fix agent
3. Investigation approach: main context lightweight investigation vs always spawn debugger subagent
4. Batch granularity: how many tests per batch, how to group by mock requirements
</context>

<ideal_flow_sketch>
The user described this target experience (refine during session):

1. Run /gsd:verify-work
2. See list of criteria to verify
3. Claude determines which tests need mocks and groups them logically
4. User chooses: Claude implements mocks or user does manually
5. Claude implements mocks (if chosen)
6. Present first batch using AskUserQuestion
7. User tests on device, reports any issues
8. For each issue:
   a. Claude investigates (reuse gsd-debugger patterns)
   b. Claude proposes fix
   c. User confirms fix before applying
   d. Apply fix
   e. User re-tests same item
   f. Confirm fix worked
9. Move to next batch (repeat 6-8)
10. After all batches: revert mocks, commit fixes, final summary
</ideal_flow_sketch>

<process>

<step name="load_domain_knowledge">
Invoke gsd-meta skill to absorb GSD framework knowledge. This gives you context about:
- Plans as prompts philosophy
- Subagent patterns and when to use them
- Context budget management (50% rule)
- Wave execution and parallel agents
- Checkpoint types and deviation rules
</step>

<step name="explore_existing_patterns">
Read and understand current implementation:
1. Current verify-work command and workflow — what works, what doesn't
2. diagnose-issues workflow — how parallel debugging currently works
3. UAT.md template — state management, section rules, lifecycle
4. gsd-debugger agent — investigation patterns to reuse
5. gsd-executor agent — deviation rules, checkpoint patterns

Note patterns to preserve and patterns to change.
</step>

<step name="surface_tradeoffs">
For each undecided design question, present tradeoffs using AskUserQuestion.

**Mock lifecycle options:**
- Temporary file + git revert: Simple, but requires careful revert
- Conditional compilation: Clean, but adds build complexity
- Environment variable flags: Runtime toggles, no code changes needed
- Separate mock branch: Isolation, but merge complexity

**Agent architecture options:**
- Multi-agent (generator, fixer, cleanup): Matches GSD patterns, fresh context per role
- Single verify-fix agent per batch: Less orchestration, but context accumulates
- Hybrid: Main context orchestrates, subagent only for complex fixes

**Investigation options:**
- Main context lightweight: Quick for simple issues, preserves flow
- Always subagent: Fresh context, matches gsd-debugger pattern, more overhead
- Threshold-based: Try main context first, escalate to subagent if inconclusive

Present each with concrete implications for context budget, user experience, and implementation complexity.
</step>

<step name="validate_against_codebase">
For each design decision, check:
- Does it align with existing GSD patterns?
- What changes to existing files are required?
- What new files need to be created?
- How does it interact with related commands (plan-phase --gaps, execute-phase)?

Reference specific file paths when validating.
</step>

<step name="converge_on_architecture">
After exploring tradeoffs, synthesize the chosen approach into a clear architecture diagram (text-based). Show:
- Main context responsibilities
- Subagent responsibilities (if any)
- State persistence points (UAT.md updates)
- User interaction points
- Mock lifecycle stages
</step>

<step name="draft_proposal">
Write the full spec to `proposals/verify-work-redesign.md` with these sections:

```markdown
# Verify-Work Redesign Proposal

## Problem Statement
[Summarize friction points with current implementation]

## Goals
[What success looks like]

## Non-Goals
[What's explicitly out of scope]

## Architecture Overview
[Text diagram of flow, agents, state]

## Detailed Design

### Mock System
[Lifecycle, implementation pattern, revert mechanism]

### Test Batching
[How tests are grouped, batch size, mock requirements]

### Investigation & Fix Flow
[Per-issue flow: investigate → propose → confirm → apply → retest]

### State Management
[UAT.md structure changes, persistence guarantees]

### Subagent Specifications
[For each agent: purpose, inputs, outputs, prompt template]

## File Changes Required
[List of files to create/modify with brief description]

### Commands
- commands/gsd/verify-work.md — [changes]

### Workflows
- get-shit-done/workflows/verify-work.md — [changes]
- get-shit-done/workflows/mock-generation.md — [new]

### Templates
- get-shit-done/templates/UAT.md — [changes]

### Agents
- agents/gsd-verify-fixer.md — [new, if needed]

## Migration Notes
[How this affects existing UAT files, backwards compatibility]

## Open Questions
[Any remaining decisions to make during implementation]
```

</step>

<step name="review_with_user">
Present the draft proposal summary. Ask:
- Does this capture the intended design?
- Any sections that need more detail?
- Ready to finalize?

Make refinements based on feedback until user approves.
</step>

</process>

<anti_patterns>
- Don't make decisions without exploring tradeoffs with user
- Don't design Flutter-specific patterns (must be framework-agnostic)
- Don't skip validating against existing GSD files
- Don't propose changes that conflict with GSD philosophy (plans as prompts, context budget)
- Don't add enterprise patterns (story points, sprints, stakeholder matrices)
- Don't use vague tasks in the spec — everything must be concrete and executable
</anti_patterns>

<success_criteria>
- [ ] gsd-meta skill invoked at start
- [ ] Existing verify-work, diagnose-issues, UAT template, gsd-debugger read and understood
- [ ] All 4 design decisions explored with AskUserQuestion
- [ ] Architecture validated against GSD codebase patterns
- [ ] Full spec written to proposals/verify-work-redesign.md
- [ ] Spec includes: problem, goals, architecture, detailed design, file changes, migration notes
- [ ] User approves final proposal
- [ ] Proposal is detailed enough to execute directly in fresh context
</success_criteria>

<output>
Save final proposal to: `proposals/verify-work-redesign.md`

This file should be self-contained — a fresh Claude context should be able to read it and implement the changes without needing additional context from this brainstorming session.
</output>
