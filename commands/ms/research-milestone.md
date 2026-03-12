---
name: ms:research-milestone
description: Research domain ecosystem before creating roadmap
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - AskUserQuestion
---

<objective>
Research milestone domain before creating roadmap. Spawns 2-5 adaptive agents based on milestone scope.

**Orchestrator role:** Analyze milestone context, determine research dimensions, spawn parallel agents returning text, synthesize into MILESTONE-RESEARCH.md.

**Why this exists:** Sits between `/ms:new-milestone` and `/ms:create-roadmap`. Produces a single file the roadmapper consumes to create better phase breakdowns. Research conclusions flow through ROADMAP.md so all downstream phase commands implicitly benefit.
</objective>

<execution_context>
@~/.claude/mindsystem/templates/milestone-research.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/MILESTONE-CONTEXT.md (if exists)
@.planning/config.json (if exists)
</context>

<process>

## 1. Validate Prerequisites

```bash
[ -f .planning/PROJECT.md ] || { echo "ERROR: No PROJECT.md. Run /ms:new-project first."; exit 1; }
[ -f .planning/MILESTONE-CONTEXT.md ] || { echo "ERROR: No MILESTONE-CONTEXT.md. Run /ms:new-milestone first."; exit 1; }
[ -f .planning/MILESTONE-RESEARCH.md ] && echo "RESEARCH_EXISTS" || echo "NO_RESEARCH"
```

## 2. Handle Existing Research

**If RESEARCH_EXISTS:** Use AskUserQuestion:
- header: "Existing research"
- question: "MILESTONE-RESEARCH.md already exists. What would you like to do?"
- options:
  - "View existing" — Show current research
  - "Replace" — Research from scratch (will overwrite)
  - "Cancel" — Keep existing

If "View existing": Read and display, then exit.
If "Cancel": Exit.
If "Replace": Continue.

## 3. Analyze Milestone Scope

Read MILESTONE-CONTEXT.md and PROJECT.md. Extract:
- **Features** — what the milestone aims to build
- **Open Questions** — unknowns flagged during discovery
- **Vision** — the "why" behind the milestone
- **Priorities** — must-have vs nice-to-have
- **Scope boundaries** — what's excluded

Check if this is a brownfield project:
```bash
[ -d .planning/codebase ] && echo "BROWNFIELD" || echo "GREENFIELD"
```

## 4. Determine Research Dimensions

Select which agents to spawn based on milestone context:

| Dimension | Agent | Spawn when |
|-----------|-------|------------|
| Ecosystem/Stack | ms-researcher | Unfamiliar tech, first milestone, or Open Questions mention stack |
| Product Landscape | ms-product-researcher | User-facing features where competitor analysis adds value |
| Codebase Feasibility | ms-codebase-researcher | Brownfield project with existing codebase |
| Architecture/Dependencies | ms-researcher | 3+ features with dependencies, or system design in Open Questions |
| Pitfalls/Risk | ms-researcher | Unfamiliar domain, external services, complex integrations |

Default: lean toward spawning more agents.

Present proposed agents to user:

```
Research dimensions for milestone: [Name]

Spawning [N] agents:
1. [Dimension] — [one-line reason]
2. [Dimension] — [one-line reason]
...

Proceed? (yes / adjust)
```

Use AskUserQuestion:
- header: "Research scope"
- question: "These agents will research your milestone. Adjust?"
- options:
  - "Proceed" — Spawn agents as proposed
  - "Add dimension" — I want more coverage
  - "Remove dimension" — Skip some of these
  - "Cancel" — Skip research entirely

## 5. Spawn Agents in Parallel

Spawn all selected agents in a single message. Each agent receives milestone and project context and returns structured text (no file writes).

**Announce:** "Spawning [N] research agents... may take 2-3 minutes."

### Ecosystem/Stack Agent (ms-researcher)

```
Task(
  prompt="
<research_type>
Milestone Research — Ecosystem/Stack dimension.
</research_type>

<milestone_context>
[MILESTONE-CONTEXT.md content]
</milestone_context>

<project_context>
[PROJECT.md summary — core value, constraints, tech stack if known]
</project_context>

<focus>
Research the technology stack for this milestone scope. Recommend specific libraries with versions and rationale. Flag what NOT to use and why. If the project has an established stack, focus on NEW libraries needed for the milestone features.
</focus>

<output>
Return findings as structured text. Do NOT write to filesystem.
Format:
## ECOSYSTEM/STACK FINDINGS
### Recommended Stack (technology, version, purpose, rationale)
### Alternatives Rejected (what, why not, use instead)
### Version Constraints & Compatibility
### Confidence (HIGH/MEDIUM/LOW per recommendation with sources)
</output>
",
  subagent_type="ms-researcher",
  description="Stack research"
)
```

### Product Landscape Agent (ms-product-researcher)

```
Task(
  prompt="
<milestone_context>
[MILESTONE-CONTEXT.md content]
</milestone_context>

<project_context>
[PROJECT.md summary]
</project_context>

<focus>
Research the product landscape for this milestone's features. What do users expect (table stakes)? What differentiates? What should be deliberately excluded?
</focus>

Return findings as structured text:
## PRODUCT LANDSCAPE FINDINGS
### Table Stakes (feature, why users expect it)
### Differentiators (feature, competitive advantage)
### Anti-Features (feature, why excluded)
### Confidence (HIGH/MEDIUM/LOW with sources)
",
  subagent_type="ms-product-researcher",
  description="Product research"
)
```

### Codebase Feasibility Agent (ms-codebase-researcher)

```
Task(
  prompt="
<objective>
Analyze codebase feasibility for milestone features.
</objective>

<milestone_context>
[MILESTONE-CONTEXT.md content]
</milestone_context>

<project_context>
[PROJECT.md summary]
</project_context>

<focus>
Assess how the existing codebase supports the milestone's planned features. Identify which components need modification vs creation. Surface feasibility constraints and integration points.
</focus>
",
  subagent_type="ms-codebase-researcher",
  description="Codebase feasibility"
)
```

### Architecture/Dependencies Agent (ms-researcher)

```
Task(
  prompt="
<research_type>
Milestone Research — Architecture/Dependencies dimension.
</research_type>

<milestone_context>
[MILESTONE-CONTEXT.md content]
</milestone_context>

<project_context>
[PROJECT.md summary]
</project_context>

<focus>
Research architecture patterns and component dependencies for this milestone. Determine build order based on dependencies. Identify integration points between components.
</focus>

<output>
Return findings as structured text. Do NOT write to filesystem.
Format:
## ARCHITECTURE FINDINGS
### Components (name, responsibility)
### Build Order (sequence with rationale)
### Integration Points (how components connect)
### Confidence (HIGH/MEDIUM/LOW with sources)
</output>
",
  subagent_type="ms-researcher",
  description="Architecture research"
)
```

### Pitfalls/Risk Agent (ms-researcher)

```
Task(
  prompt="
<research_type>
Milestone Research — Pitfalls/Risk dimension.
</research_type>

<milestone_context>
[MILESTONE-CONTEXT.md content]
</milestone_context>

<project_context>
[PROJECT.md summary]
</project_context>

<focus>
Research common pitfalls and risks for this milestone's domain and features. For each pitfall: severity, prevention strategy, and which components/phases it affects.
</focus>

<output>
Return findings as structured text. Do NOT write to filesystem.
Format:
## PITFALLS/RISK FINDINGS
### Pitfalls (pitfall, severity, prevention, affects)
### Feasibility Assessment (feasible YES/CONDITIONALLY/NO, constraints)
### Open Questions (needing resolution)
### Confidence (HIGH/MEDIUM/LOW with sources)
</output>
",
  subagent_type="ms-researcher",
  description="Pitfalls research"
)
```

## 6. Synthesize into MILESTONE-RESEARCH.md

After all agents return, synthesize findings into `.planning/MILESTONE-RESEARCH.md` using template.

Map agent returns to template sections:
- Ecosystem/Stack → Technology Decisions
- Product Landscape → Product Landscape
- Codebase Feasibility → Feasibility Assessment + Architecture & Dependencies
- Architecture → Architecture & Dependencies
- Pitfalls/Risk → Pitfalls & Risks + Feasibility Assessment

Write Executive Summary (2-3 paragraphs) synthesizing all findings.

Merge overlapping findings. Resolve conflicts by preferring higher-confidence sources.

## 7. Update state and commit:

```bash
ms-tools set-last-command "ms:research-milestone"
git add .planning/MILESTONE-RESEARCH.md .planning/STATE.md
git commit -m "$(cat <<'EOF'
docs: complete milestone research

Key findings:
- Stack: [one-liner]
- Architecture: [one-liner]
- Critical pitfall: [one-liner]
EOF
)"
```

Present summary:

```
Research complete:

File: .planning/MILESTONE-RESEARCH.md

Key findings:
- Stack: [one-liner]
- Architecture: [one-liner]
- Critical pitfall: [one-liner]
- Feasibility: [YES/CONDITIONALLY/NO]

---
## ▶ Next Up
`/ms:create-roadmap` — define requirements and create roadmap
<sub>`/clear` first → fresh context window</sub>
---
```

</process>

<success_criteria>
- [ ] PROJECT.md and MILESTONE-CONTEXT.md validated
- [ ] Research dimensions determined and approved by user
- [ ] 2-5 agents spawned in parallel (adaptive selection)
- [ ] All agent results received and synthesized
- [ ] MILESTONE-RESEARCH.md created using template
- [ ] Research committed to git
- [ ] User routed to /ms:create-roadmap
</success_criteria>
