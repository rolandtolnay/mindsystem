---
name: ms:research-project
description: Research domain ecosystem before creating roadmap
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - AskUserQuestion
---

<objective>
Research domain ecosystem. Spawns 4 parallel ms-researcher agents for comprehensive coverage.

**Orchestrator role:** Analyze project, generate research questions, spawn 4 parallel agents, synthesize SUMMARY.md.

**Why subagents:** Research burns context fast. Fresh 200k context per domain. Main context stays lean.
</objective>

<context>
@.planning/PROJECT.md
@.planning/config.json (if exists)
</context>

<process>

## 1. Validate Prerequisites

```bash
[ -f .planning/PROJECT.md ] || { echo "ERROR: No PROJECT.md. Run /ms:new-project first."; exit 1; }
[ -f .planning/ROADMAP.md ] && echo "WARNING: ROADMAP.md exists. Research is typically done before roadmap."
[ -d .planning/research ] && echo "RESEARCH_EXISTS" || echo "NO_RESEARCH"
```

## 2. Handle Existing Research

**If RESEARCH_EXISTS:** Use AskUserQuestion (View existing / Replace / Cancel)

## 3. Analyze Project

Read PROJECT.md, extract domain/stack/core value/constraints. Present for approval:
```
Domain analysis:
- Type: [domain]
- Stack: [stated or TBD]
- Core: [core value]
Does this look right? (yes / adjust)
```

## 4. Generate Research Questions

| Dimension | Question |
|-----------|----------|
| Stack | "What's the standard 2026 stack for [domain]?" |
| Features | "What features do [domain] products have?" |
| Architecture | "How are [domain] systems structured?" |
| Pitfalls | "What do [domain] projects get wrong?" |

Present for approval.

## 5. Spawn Research Agents

```bash
mkdir -p .planning/research
```

**Determine milestone context:**
- If no "Validated" requirements in REQUIREMENTS.md → Greenfield (v1.0)
- If "Validated" requirements exist → Subsequent milestone (v1.1+)

Spawn all 4 in parallel with rich context:

```
Task(prompt="
<research_type>
Project Research — Stack dimension for [domain].
</research_type>

<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
Research the standard stack for building [domain] from scratch. Full ecosystem investigation.

**Subsequent (v1.1+):**
Research what's needed to add [target features] to an existing [domain] app.

IMPORTANT for subsequent milestones:
- DON'T re-research the existing system (validated requirements already work)
- DON'T question established stack choices (they're proven)
- DO research new libraries/patterns needed for [target features] specifically
- DO investigate how [target features] integrate with the existing architecture
- DO surface any compatibility concerns with current stack
</milestone_context>

<question>
[stack question from step 4]
</question>

<project_context>
[PROJECT.md summary]
</project_context>

<downstream_consumer>
Your STACK.md feeds into /ms:create-roadmap. Be prescriptive:
- Specific libraries with versions
- Clear rationale for each choice
- What NOT to use and why
</downstream_consumer>

<quality_gate>
- [ ] Versions are current (not Claude's training data)
- [ ] Rationale explains WHY, not just WHAT
- [ ] Confidence levels assigned
</quality_gate>

<output>
Write to: .planning/research/STACK.md
Use template: ~/.claude/mindsystem/templates/research-project/STACK.md
</output>
", subagent_type="ms-researcher", description="Stack research")

Task(prompt="
<research_type>
Project Research — Features dimension for [domain].
</research_type>

<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
What features do [domain] products have? What's table stakes vs differentiating?

**Subsequent (v1.1+):**
How do [target features] typically work? What's expected behavior?

IMPORTANT for subsequent milestones:
- Focus ONLY on [target features] - the new capabilities being added
- DON'T list features the system already has (see Validated requirements)
- DO research user expectations for [target features] specifically
- DO identify table stakes vs differentiators within [target features] scope
</milestone_context>

<question>
[features question from step 4]
</question>

<project_context>
[PROJECT.md summary]
</project_context>

<downstream_consumer>
Your FEATURES.md feeds into /ms:create-roadmap. Categorize clearly:
- Table stakes (must have or users leave)
- Differentiators (competitive advantage)
- Anti-features (things to deliberately NOT build)
</downstream_consumer>

<quality_gate>
- [ ] Categories are clear
- [ ] Complexity noted for each
- [ ] Dependencies between features identified
</quality_gate>

<output>
Write to: .planning/research/FEATURES.md
Use template: ~/.claude/mindsystem/templates/research-project/FEATURES.md
</output>
", subagent_type="ms-researcher", description="Features research")

Task(prompt="
<research_type>
Project Research — Architecture dimension for [domain].
</research_type>

<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
How are [domain] systems typically structured? What are major components?

**Subsequent (v1.1+):**
How do [target features] integrate with existing [domain] architecture?

IMPORTANT for subsequent milestones:
- The existing architecture is KNOWN (from previous milestones)
- Research how [target features] should connect to existing components
- Identify which existing components need modification vs new components needed
- Surface any architectural concerns (scaling, coupling, migration)
</milestone_context>

<question>
[architecture question from step 4]
</question>

<project_context>
[PROJECT.md summary]
</project_context>

<downstream_consumer>
Your ARCHITECTURE.md informs phase structure in roadmap. Include:
- Component boundaries (what talks to what)
- Data flow (how information moves)
- Suggested build order (dependencies between components)
</downstream_consumer>

<quality_gate>
- [ ] Components clearly defined
- [ ] Boundaries explicit
- [ ] Build order implications noted
</quality_gate>

<output>
Write to: .planning/research/ARCHITECTURE.md
Use template: ~/.claude/mindsystem/templates/research-project/ARCHITECTURE.md
</output>
", subagent_type="ms-researcher", description="Architecture research")

Task(prompt="
<research_type>
Project Research — Pitfalls dimension for [domain].
</research_type>

<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
What do [domain] projects commonly get wrong? Critical mistakes?

**Subsequent (v1.1+):**
What are common mistakes when adding [target features] to [domain]?

IMPORTANT for subsequent milestones:
- Focus on integration pitfalls, not greenfield mistakes
- Research upgrade/migration pitfalls (existing users, data migration)
- Identify feature interaction bugs (new features breaking existing ones)
- Surface performance concerns when [target features] are added to existing load
</milestone_context>

<question>
[pitfalls question from step 4]
</question>

<project_context>
[PROJECT.md summary]
</project_context>

<downstream_consumer>
Your PITFALLS.md prevents mistakes in roadmap/planning. For each pitfall:
- Warning signs (how to detect early)
- Prevention strategy (how to avoid)
- Which phase should address it
</downstream_consumer>

<quality_gate>
- [ ] Pitfalls are specific, not generic
- [ ] Prevention is actionable
- [ ] Phase mapping included
</quality_gate>

<output>
Write to: .planning/research/PITFALLS.md
Use template: ~/.claude/mindsystem/templates/research-project/PITFALLS.md
</output>
", subagent_type="ms-researcher", description="Pitfalls research")
```

**Announce:** "Spawning 4 research agents... may take 2-3 minutes."

## 6. Wait for Completion and Synthesize

After all 4 agents return:

```bash
# Verify all research files exist
ls .planning/research/STACK.md .planning/research/FEATURES.md \
   .planning/research/ARCHITECTURE.md .planning/research/PITFALLS.md
```

**If any missing:** Report which agent failed, offer to retry.

**If all present:** Spawn synthesizer:

```
Task(
  prompt="
Synthesize research outputs into SUMMARY.md.

Read all 4 files in .planning/research/:
- STACK.md
- FEATURES.md
- ARCHITECTURE.md
- PITFALLS.md

Create SUMMARY.md with:
- Executive summary (2-3 paragraphs)
- Key findings from each file
- Roadmap implications (suggested phase structure)
- Confidence assessment
- Gaps to address

After creating SUMMARY.md, update config.json code_review fields with agent names:
1. Read recommended stack from STACK.md
2. Map to code review agent names:
   - Flutter/Dart:
     - adhoc: \"ms-flutter-code-quality\"
     - phase: \"ms-flutter-code-quality\"
     - milestone: \"ms-flutter-reviewer\"
   - All others:
     - adhoc: \"ms-code-simplifier\"
     - phase: \"ms-code-simplifier\"
     - milestone: (leave as null)
3. Update .planning/config.json (create from template if needed)

Then commit ALL research files together:
git add .planning/research/
git add .planning/config.json
git commit -m 'docs: complete [domain] project research'
",
  subagent_type="ms-research-synthesizer",
  description="Synthesize research"
)
```

## 7. Present Results

```
Research complete:

Files: SUMMARY.md, STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md

Key findings:
- Stack: [one-liner]
- Architecture: [one-liner]
- Critical pitfall: [one-liner]

---
## ▶ Next Up
`/ms:create-roadmap` — define requirements and create roadmap
<sub>`/clear` first → fresh context window</sub>
---
```

## 8. Update Last Command

Update `.planning/STATE.md` Last Command field:
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:research-project | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line

</process>

<success_criteria>
- [ ] PROJECT.md validated
- [ ] Domain identified and approved
- [ ] 4 ms-researcher agents spawned in parallel
- [ ] All 4 research files created (STACK, FEATURES, ARCHITECTURE, PITFALLS)
- [ ] ms-research-synthesizer spawned to create SUMMARY.md
- [ ] All research files committed atomically by synthesizer
</success_criteria>
