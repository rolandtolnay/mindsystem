# GSD Design Phase Proposal

> A comprehensive proposal for integrating UI/UX design into the GSD workflow system.

**Status:** Draft for Review
**Date:** 2026-01-19
**Collaborators:** User + Claude (Brainstorm Session)

---

## 1. Executive Summary

### Problem Statement

GSD executes plans through subagents that write code directly from requirements. There is no design step, so UI features often look functional but not beautiful — they lack intentional visual hierarchy, proper spacing, and platform-appropriate aesthetics. The code works, but the visual output doesn't respect UI/UX best practices.

Current workarounds (using `/gsd:discuss-phase` to describe envisioned designs) help somewhat but don't provide the structured, quality-forcing approach needed for professional-grade interfaces.

### Proposed Solution

Introduce a **design phase** that sits between `discuss-phase` and `research-phase`:

```
discuss-phase → design-phase → research-phase → plan-phase → execute-phase
     ↓              ↓              ↓              ↓              ↓
 CONTEXT.md     DESIGN.md     RESEARCH.md     PLAN.md      SUMMARY.md
 (vision)       (UI/UX)       (technical)     (tasks)      (results)
```

The design phase:
- Translates user vision (CONTEXT.md) into concrete visual/UX specifications
- Produces ASCII wireframes and prose specifications
- Applies quality-forcing patterns to prevent generic AI output
- Informs research-phase (what libraries/capabilities are needed)
- Guides plan-phase (task structure follows design decisions)
- Directs execute-phase (implementation matches design specs)

### Key Benefits

1. **Intentional Design** — UI decisions are explicit, not emergent from code
2. **Quality Forcing** — Commercial benchmark anchoring prevents generic output
3. **Harmonization** — New designs integrate with existing project aesthetics
4. **Platform Awareness** — Design considers iOS, Android, and web conventions
5. **Verifiable** — Design specs include observable criteria for implementation validation

---

## 2. Research Findings

### GSD Architecture Analysis

#### Command Flow (30 commands total)

GSD uses a phase-based workflow with clear handoffs:

| Stage | Command | Output | Purpose |
|-------|---------|--------|---------|
| Vision | `/gsd:discuss-phase` | CONTEXT.md | Capture user's vision, essentials, scope |
| Research | `/gsd:research-phase` | RESEARCH.md | Investigate implementation approach |
| Planning | `/gsd:plan-phase` | PLAN.md files | Break phase into executable tasks |
| Execution | `/gsd:execute-phase` | SUMMARY.md files | Build code with atomic commits |
| Verification | `/gsd:verify-work` | UAT.md | Validate features work correctly |

**Key insight:** Each phase produces artifacts that downstream phases consume. Design fits naturally as a new artifact type.

#### Agent Architecture (10 agents)

GSD agents follow consistent patterns:

- **Fresh context** — Each agent gets 200k tokens, preserving orchestrator context
- **File-first output** — Agents write to `.planning/`, return brief confirmations
- **Goal-backward methodology** — Start from desired outcome, derive requirements
- **Structured returns** — YAML frontmatter + markdown sections

**Relevant patterns for design agent:**
- Tools: `Read, Write, Bash, Grep, Glob` (no WebSearch — design derives from project context, not web inspiration)
- Output: Write DESIGN.md directly, return confirmation
- Methodology: Goal-backward (what should users experience → what enables that)

#### File Structure

```
.planning/
├── PROJECT.md           # Living project context
├── ROADMAP.md           # Phase structure
├── STATE.md             # Session memory
├── phases/
│   └── XX-name/
│       ├── {phase}-CONTEXT.md    # User vision (discuss-phase)
│       ├── {phase}-DESIGN.md     # UI/UX specs (NEW)
│       ├── {phase}-RESEARCH.md   # Technical research
│       ├── {phase}-01-PLAN.md    # Executable plan
│       └── {phase}-01-SUMMARY.md # Execution results
```

### AI-Driven Design Patterns (from ai-driven-ui-design-system.md)

#### Quality-Forcing Patterns (All 5 to be included)

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Commercial Benchmark** | "Design must look like commercial $50-200 [product type]" | Anchors to real market standards |
| **Pre-emptive Criticism** | "Assume user will say 'This looks generic'" | Forces counteraction of predictable failures |
| **Accountability Check** | "Could you show this to a skilled designer?" | Creates psychological ownership |
| **Mandatory Self-Review** | Check for generic colors, arbitrary spacing, default inputs | Catches obvious issues before return |
| **Explicit Anti-Patterns** | List what NOT to do (blue accents, arbitrary spacing) | Makes failures recognizable |

#### Three-Tier Architecture

```
ORCHESTRATOR (/gsd:design-phase command)
├── Gathers context (CONTEXT.md, implement-ui, codebase)
├── Routes to design agent
└── Presents results for refinement

DESIGN AGENT (gsd-designer)
├── Fresh context per invocation
├── Pure design generation
└── Returns structured DESIGN.md

IMPLEMENTATION (gsd-executor in later phase)
├── Reads DESIGN.md specifications
├── Implements components to spec
└── Validates against design criteria
```

#### Common Anti-Patterns to Prevent

| Anti-Pattern | Why It's Bad | What to Do Instead |
|--------------|--------------|-------------------|
| Generic dark gray | Reads as "default dark mode" | Choose distinctive darks (warm brown, deep blue) |
| Blue accent everywhere | Overused, reads as generic | Match accent to product personality |
| Same-sized controls | Visual monotony | Vary sizes by importance |
| Arbitrary spacing | Looks unintentional | Use consistent spacing scale (4/8/12/16/24/32) |
| System fonts only | Reads as prototype | Use distinctive fonts OR careful spacing |

### Platform-Specific Considerations

#### Web (React + Tailwind)

- Responsive breakpoints required
- Touch targets: 44×44px minimum
- No viewport units on initial render
- Focus states for keyboard navigation

#### Mobile (Flutter/Dart)

- iOS: Follow Human Interface Guidelines
- Android: Follow Material Design 3
- Safe area insets respected
- Platform-appropriate navigation patterns

### Existing Aesthetic Handling (Tiered Approach)

```
1. implement-ui skill exists?
   └── YES → Load as authoritative source of existing patterns
       ↓
2. Analyze codebase
   └── Fill gaps, discover implicit patterns not in skill
       ↓
3. Propose design
   └── Novel solutions that harmonize with discovered aesthetic
```

**Key principle:** Optimize for fresh design with harmonization, not pattern replication. Design phase is for UI-heavy phases with novel requirements.

---

## 3. Proposed Architecture

### Workflow Position

Design phase sits between vision gathering and technical research:

```
discuss-phase → design-phase → research-phase → plan-phase → execute-phase
                     │
                     ▼
              DESIGN.md informs:
              ├── research-phase → "We need animation library for this interaction"
              ├── plan-phase → "Task 3: Implement Card component per design spec"
              └── execute-phase → "Follow DESIGN.md for component styling"
```

**Why this position:**
- After discuss-phase: User vision is crystallized
- Before research-phase: Design decisions inform technical choices
- Technical constraints don't artificially limit design vision

### Context Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    /gsd:design-phase N                          │
│                     (Orchestrator)                              │
│                                                                 │
│  1. Load context chain                                          │
│  2. Assess if Q&A needed (adaptive)                             │
│  3. Ask targeted questions (if gaps)                            │
│  4. Spawn gsd-designer with full context                        │
└─────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐   ┌───────────────────┐   ┌───────────────────────┐
│ PROJECT.md  │   │ ROADMAP.md        │   │ CONTEXT.md            │
│ (ALWAYS)    │   │ (phase reqs)      │   │ (if exists)           │
│             │   │                   │   │                       │
│ - Audience  │   │ - Success criteria│   │ - User vision         │
│ - Problems  │   │ - Phase goal      │   │ - Essentials          │
│ - Core value│   │ - Requirements    │   │ - Specific ideas      │
└─────────────┘   └───────────────────┘   └───────────────────────┘
    │                         │                         │
    └─────────────────────────┼─────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    ▼                         ▼                         ▼
┌─────────────┐   ┌───────────────────┐   ┌───────────────────────┐
│implement-ui │   │ Codebase Analysis │   │ Adaptive Q&A          │
│skill        │   │ (existing styles) │   │ (if gaps identified)  │
│(if exists)  │   │                   │   │                       │
└─────────────┘   └───────────────────┘   └───────────────────────┘
    │                         │                         │
    └─────────────────────────┼─────────────────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │     gsd-designer        │
                 │  (Fresh 200k context)   │
                 │                         │
                 │  + Quality-forcing      │
                 │    patterns             │
                 │  + Platform awareness   │
                 │  + ASCII layouts        │
                 └─────────────────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      DESIGN.md          │
                 │                         │
                 │  - Visual layouts       │
                 │  - Component specs      │
                 │  - UX flows             │
                 │  - Design decisions     │
                 │  - Verification criteria│
                 └─────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────────┐
│ research-phase│   │   plan-phase    │   │   execute-phase     │
│ (informed by  │   │  (tasks follow  │   │  (implementation    │
│  design needs)│   │   design spec)  │   │   matches design)   │
└───────────────┘   └─────────────────┘   └─────────────────────┘
```

### Optional Command Chain

The first three commands in the phase workflow are **optional**:

```
[discuss-phase] → [design-phase] → [research-phase] → plan-phase → execute-phase
   optional          optional          optional         mandatory    mandatory
```

Design-phase must handle all scenarios:
- **discuss-phase was run** → CONTEXT.md exists, may have design context
- **discuss-phase skipped** → No CONTEXT.md, infer from PROJECT.md + phase requirements
- **Partial context** → Some info exists, adaptive Q&A fills gaps

### When to Invoke Design Phase

Design phase is **explicitly invoked** by the user, not auto-triggered. It's appropriate for:

- UI-heavy phases with significant new interface work
- Novel flows/components not deducible from existing patterns
- Features requiring careful UX consideration
- Cross-platform work needing coordinated design

**Not needed for:**
- Backend-only phases
- Minor UI tweaks using existing patterns
- Phases where established patterns suffice

### Adaptive Q&A Logic

The orchestrator intelligently assesses whether questions are needed:

**Step 1: Load mandatory context**
- PROJECT.md — target audience, problems solved, core value (ALWAYS)
- ROADMAP.md — phase goal, success criteria, requirements (ALWAYS)

**Step 2: Load optional context**
- CONTEXT.md — user's vision (if discuss-phase was run)
- implement-ui skill — authoritative patterns (if exists)
- Codebase analysis — existing styles/components

**Step 3: Assess coverage**
- Can platform be inferred? (from project type, existing code)
- Can visual style be inferred? (from codebase, audience)
- Can design priorities be inferred? (from phase requirements)

**Step 4: Ask only for genuine gaps**
- If everything can be inferred → proceed directly to designer
- If gaps exist → ask targeted questions for those gaps only

**Most valuable question (if not in CONTEXT.md):**
> "Are there apps or sites whose design you'd like this to feel like?"

Reference products are hard to infer and extremely valuable for design direction.

---

## 4. Design Agent Specification

### Agent Definition

```yaml
---
name: gsd-designer
description: Creates visual/UX design specifications for phases. Spawned by /gsd:design-phase orchestrator.
tools: Read, Write, Bash, Grep, Glob
color: magenta
---
```

### Role Definition

```xml
<role>
You are a GSD designer. You create visual/UX design specifications that guide implementation.

You are spawned by:
- `/gsd:design-phase` orchestrator (phase-specific design before research)

Your job: Transform user vision into concrete, implementable design specifications that prevent generic AI output and ensure professional-grade interfaces.

**Core responsibilities:**
- Analyze existing project aesthetic (implement-ui skill, codebase patterns)
- Apply quality-forcing patterns (commercial benchmark, pre-emptive criticism, self-review)
- Create ASCII wireframes with precise spacing and component placement
- Specify component behaviors, states, and platform-specific requirements
- Document UX flows with clear user journey steps
- Provide verification criteria that prove design was implemented correctly
</role>
```

### Upstream Input

```xml
<upstream_input>
## Mandatory Context (ALWAYS loaded)

**PROJECT.md** — Product context that shapes design direction

| Section | How You Use It |
|---------|----------------|
| `## What This Is` | Product type informs design conventions |
| `## Core Value` | The ONE thing design must serve |
| `## Context` | Target audience shapes UX priorities |
| `## Constraints` | Technical limits, platform requirements |

**ROADMAP.md** — Phase-specific requirements

| Section | How You Use It |
|---------|----------------|
| Phase Goal | What the design must enable |
| Success Criteria | Observable behaviors to support |
| Requirements mapped | Specific features to design for |

## Optional Context (loaded if exists)

**CONTEXT.md** (from discuss-phase) — User's vision for the phase

| Section | How You Use It |
|---------|----------------|
| `## How This Should Work` | Core design vision — capture this feeling |
| `## What Must Be Nailed` | Non-negotiables — design MUST support these |
| `## Specific Ideas` | References to existing products — learn from these |

**implement-ui skill** (if exists) — Authoritative existing patterns

| Element | How You Use It |
|---------|----------------|
| Color palette | Use exact values, don't deviate |
| Component library | Reference existing components by name |
| Spacing system | Follow established scale |
| Typography | Match existing hierarchy |

**Codebase analysis** — Implicit patterns not in skill

| Discovery | How You Use It |
|-----------|----------------|
| Existing components | Design new components to harmonize |
| Layout patterns | Follow established structure conventions |
| Interaction patterns | Match existing behaviors |

## Context Priority

When sources conflict, follow this priority:
1. implement-ui skill (authoritative project patterns)
2. CONTEXT.md user decisions (explicit user choices)
3. Codebase analysis (implicit established patterns)
4. PROJECT.md guidance (product-level direction)
5. Platform conventions (iOS HIG, Material, web standards)
</upstream_input>
```

### Quality-Forcing Integration

```xml
<quality_forcing>
## Commercial Benchmark

Before generating any design:
> "This design must look like a commercial $50-200 [product type] — intentional decisions, not defaults."

For web apps: "Well-funded SaaS product with Series A+ design budget"
For mobile apps: "Top 100 App Store app in this category"

## Pre-emptive Criticism

Assume the user will say: "This looks like generic AI output."
Generate something that proves them wrong.

What makes it generic (avoid these):
- Generic dark gray with blue accents
- Default spacing with no intentional rhythm
- Controls that look like styled HTML inputs
- Typography using only system fonts

## Accountability Check

Before returning, ask yourself:
> "Could I show this design to a professional UI designer and claim it as skilled work?"

If not, it's not done. Refine.

## Mandatory Self-Review

REQUIRED: Review your own work before returning.

| Question | If "No" → Action |
|----------|------------------|
| Does the color palette have character? | Choose distinctive colors |
| Does spacing feel intentional? | Apply consistent spacing scale |
| Do controls look refined? | Add proper states, sizing, polish |
| Is there clear visual hierarchy? | Adjust size/weight/contrast |
| Would this pass professional review? | Keep refining |

This is not optional. The first pass is never the best.

## Explicit Anti-Patterns

Quality failures — if you see these, the design is NOT done:

❌ Generic dark gray with blue accents (unless specifically requested)
❌ Default spacing with no intentional rhythm
❌ Controls that look like styled HTML inputs
❌ Typography using only system fonts without spacing compensation
❌ Elements that appear positioned without thought
❌ Same-sized everything (no visual hierarchy)
❌ Centered everything (lazy layout solution)
</quality_forcing>
```

### Execution Flow

```xml
<execution_flow>
## Step 1: Load Context Chain

1. Read CONTEXT.md from discuss-phase
   - Extract vision, essentials, specific ideas

2. Check for implement-ui skill
   ```bash
   ls .claude/skills/*implement-ui* 2>/dev/null
   ```
   - If exists: Load and parse for authoritative patterns

3. Analyze codebase for existing patterns
   ```bash
   # Find existing component files
   find src -name "*.tsx" -o -name "*.dart" | head -20
   # Check for design tokens/themes
   grep -r "colors\|theme\|spacing" src/ --include="*.ts" --include="*.dart" | head -10
   ```
   - Document discovered patterns

## Step 2: Establish Design Foundation

Based on context chain, determine:
- Platform(s): web, mobile, or both
- Aesthetic source: implement-ui / codebase / fresh
- Color direction: warm, cool, monochromatic, vibrant
- Density: tight, comfortable, spacious

Document in Visual Identity section.

## Step 3: Design Screens/Layouts

For each screen in the phase:
1. Create ASCII wireframe with component placement
2. Specify spacing (edge padding, component gaps)
3. List components used
4. Note responsive behavior

Apply quality-forcing patterns — check for generic output.

## Step 4: Specify Components

For each new or modified component:
1. Visual description (what it looks like)
2. States (default, hover, active, disabled, loading)
3. Size constraints (min/max)
4. Platform-specific notes

## Step 5: Document UX Flows

For each user journey:
1. Entry point (what triggers the flow)
2. Steps (numbered sequence)
3. Decision points (branches)
4. Completion (success state)
5. Error handling (failure states)

## Step 6: Capture Design Decisions

Create decision table:
| Category | Decision | Rationale |
|----------|----------|-----------|
| Colors | [specific values] | [why] |
| Typography | [specific values] | [why] |
| Spacing | [specific scale] | [why] |

## Step 7: Write Verification Criteria

Observable behaviors that prove correct implementation:
- [ ] User can see [element] in [location]
- [ ] Tapping [element] produces [response]
- [ ] [Accessibility requirement] is met

## Step 8: Self-Review and Refine

Run through quality-forcing checklist.
If any answer is "generic/arbitrary/default" → refine before returning.

## Step 9: Write DESIGN.md

Write to: `.planning/phases/{phase}-{slug}/{phase}-DESIGN.md`

Return brief confirmation to orchestrator.
</execution_flow>
```

### Structured Returns

```xml
<structured_returns>
## Design Complete

When design finishes successfully:

```markdown
## DESIGN COMPLETE

**Phase:** [X]: [Name]
**Platform:** [web / mobile / both]
**Aesthetic:** [source: implement-ui / codebase / fresh]

### Summary

[2-3 sentences on design approach and key decisions]

### Screens Designed

| Screen | Components | Notes |
|--------|------------|-------|
| [name] | [count] | [key feature] |

### Files Created

- `.planning/phases/{phase}-{slug}/{phase}-DESIGN.md`

### Ready for Refinement

Design is ready for user review. Conversational refinement available before proceeding to research-phase.
```

## Design Needs Clarification

When design requires user input:

```markdown
## DESIGN NEEDS CLARIFICATION

**Phase:** [X]: [Name]
**Question:** [specific design decision needed]

### Context

[Why this decision matters]

### Options

1. **[Option A]:** [description]
   - Pros: [benefits]
   - Cons: [tradeoffs]

2. **[Option B]:** [description]
   - Pros: [benefits]
   - Cons: [tradeoffs]

### Awaiting

User decision to continue design.
```
</structured_returns>
```

---

## 5. Design Output Format

### DESIGN.md Template

```markdown
# Phase [X]: [Name] - Design Specification

**Designed:** [date]
**Platform:** [web / mobile / both]
**Aesthetic source:** [implement-ui skill / codebase analysis / fresh design]

## Visual Identity

[2-3 sentences describing the design philosophy and feelings evoked. What's the vibe? What should users feel when they see this interface?]

**Design direction:**
- Overall feel: [e.g., "Professional yet approachable"]
- Key differentiator: [e.g., "Generous whitespace, subtle animations"]
- Inspiration: [e.g., "Linear's clean density, Notion's approachability"]

---

## Screen Layouts

### [Screen 1 Name]

```
+--------------------------------------------------+
|  [Header Area]                                   |
|  Logo        Nav Items              User Avatar  |
+--------------------------------------------------+
|                                                  |
|  [Main Content Area]                             |
|                                                  |
|  +---------------------+  +-------------------+  |
|  |                     |  |                   |  |
|  |  Primary Card       |  |  Secondary Card   |  |
|  |                     |  |                   |  |
|  +---------------------+  +-------------------+  |
|                                                  |
|  +---------------------------------------------+ |
|  |  Full-width Section                         | |
|  +---------------------------------------------+ |
|                                                  |
+--------------------------------------------------+
|  [Footer]                                        |
+--------------------------------------------------+
```

**Dimensions:** [width × height or responsive]
**Edge padding:** [value]px
**Component gaps:** [value]px
**Components used:**
- Header: [component names]
- Cards: [component names]
- Footer: [component names]

**Responsive behavior:**
- Desktop (1024px+): [layout description]
- Tablet (768-1024px): [layout changes]
- Mobile (<768px): [layout changes]

### [Screen 2 Name]

[Repeat structure for each screen]

---

## Component Specifications

### [Component Name]

**Purpose:** [what this component does]

**Visual:**
- Background: [color/gradient]
- Border: [style, color, radius]
- Shadow: [depth level]
- Size: [min/max dimensions]

**States:**
| State | Visual Change | Trigger |
|-------|--------------|---------|
| Default | [base appearance] | Initial |
| Hover | [change description] | Mouse over (web) |
| Active | [change description] | Click/tap |
| Disabled | [change description] | Interaction blocked |
| Loading | [change description] | Async operation |

**Content:**
- Typography: [font, size, weight, color]
- Icons: [if any, which ones, sizing]
- Spacing: [internal padding]

**Platform notes:**
- Web: [specific considerations]
- iOS: [specific considerations]
- Android: [specific considerations]

### [Next Component]

[Repeat for each component]

---

## UX Flows

### [Flow Name]

**Entry point:** [what triggers this flow]
**Goal:** [what user is trying to accomplish]

**Steps:**
1. User sees [initial screen/state]
2. User [action] on [element]
3. App responds with [feedback/transition]
4. User sees [next screen/state]
5. [Continue as needed]

**Decision points:**
- At step [N]: If [condition], go to step [X]; else continue
- [Additional branches]

**Success state:**
- User sees: [what appears]
- System state: [what changed]

**Error handling:**
- If [error condition]: Show [error message/state]
- Recovery: [how user recovers]

### [Next Flow]

[Repeat for each flow]

---

## Design System Decisions

| Category | Decision | Values | Rationale |
|----------|----------|--------|-----------|
| **Colors** | Primary | `#[hex]` | [why this color] |
| | Secondary | `#[hex]` | [why this color] |
| | Background | `#[hex]` | [why this color] |
| | Text | `#[hex]` | [why this color] |
| | Accent | `#[hex]` | [why this color] |
| | Error | `#[hex]` | [standard red variant] |
| | Success | `#[hex]` | [standard green variant] |
| **Typography** | Headings | [font family] | [why chosen] |
| | Body | [font family] | [why chosen] |
| | H1 | [size/weight] | [hierarchy purpose] |
| | H2 | [size/weight] | [hierarchy purpose] |
| | Body | [size/weight] | [hierarchy purpose] |
| | Caption | [size/weight] | [hierarchy purpose] |
| **Spacing** | Base unit | [4px / 8px] | [scaling approach] |
| | Edge padding | [value]px | [breathing room] |
| | Component gap | [value]px | [relationship] |
| | Section gap | [value]px | [separation] |
| **Borders** | Radius | [value]px | [style approach] |
| | Width | [value]px | [visibility] |
| **Shadows** | Elevation 1 | [values] | [subtle depth] |
| | Elevation 2 | [values] | [prominent depth] |

---

## Platform-Specific Notes

### Web (React + Tailwind)

**Responsive breakpoints:**
- Mobile: `< 640px`
- Tablet: `640px - 1024px`
- Desktop: `> 1024px`

**Touch targets:** Minimum 44×44px for interactive elements

**Keyboard navigation:**
- [Which elements should be focusable]
- [Focus order/flow]

**Accessibility:**
- Color contrast: WCAG AA (4.5:1 body text, 3:1 large text)
- Screen reader: [aria labels needed]

### Mobile (Flutter)

**iOS considerations:**
- Follow HIG for [specific patterns]
- Safe area insets: Respect notch/home indicator
- Navigation: [pattern - stack, tabs, drawer]

**Android considerations:**
- Follow Material Design 3 for [specific patterns]
- System bars: [edge-to-edge consideration]
- Back gesture: [handling]

**Shared:**
- Touch targets: 48×48dp minimum
- Text sizes: 16sp minimum for body text

---

## Verification Criteria

Observable behaviors that prove this design was implemented correctly:

### Visual Verification
- [ ] Color palette matches specification exactly
- [ ] Typography hierarchy is clearly visible
- [ ] Spacing follows specified scale consistently
- [ ] Components match specified states and transitions

### Functional Verification
- [ ] [Screen 1]: User can [primary action]
- [ ] [Screen 2]: User can [primary action]
- [ ] [Flow 1]: User can complete [goal]
- [ ] Error states display correctly when [condition]

### Platform Verification
- [ ] Web: Responsive layout works at all breakpoints
- [ ] Web: Keyboard navigation functional
- [ ] Mobile: Touch targets meet minimum size
- [ ] Mobile: Safe areas respected

### Accessibility Verification
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader can navigate all interactive elements
- [ ] Focus states are visible
```

---

## 6. Iteration Workflow

### Initial Generation

1. User runs `/gsd:design-phase N`
2. Orchestrator gathers context (CONTEXT.md, implement-ui, codebase)
3. Spawns gsd-designer with quality-forcing patterns
4. Agent produces initial DESIGN.md
5. Agent returns brief confirmation

### Conversational Refinement

After initial generation, the conversation continues in main context:

```
User: The card layout feels too cramped. Can we increase spacing?

Claude: [Reads DESIGN.md, understands context]
        I'll update the component gaps from 12px to 16px and adjust
        the card internal padding. Let me revise the layouts...
        [Edits DESIGN.md directly]

User: The blue accent doesn't feel right for this app. What about
      something warmer?

Claude: Given the existing warm tones in your app, I'd suggest:
        - Option A: Amber (#F59E0B) - energetic, approachable
        - Option B: Coral (#F97316) - friendly, distinctive
        Which direction?

User: Let's go with amber.

Claude: [Updates DESIGN.md color decisions]
        Updated. The amber accent now flows through buttons, links,
        and highlights. Want to review the full design before
        proceeding to research?
```

### Refinement Principles

- **Direct edits** — Claude edits DESIGN.md directly, doesn't regenerate
- **Preserve decisions** — Changes are incremental, not wholesale replacement
- **User controls pace** — User decides when design is "done"
- **No subagent for refinement** — Conversational, same context

### Transition to Research

When user is satisfied:

```
User: Design looks good. Let's proceed.

Claude: Design finalized. Ready for `/gsd:research-phase N` to investigate
        implementation approach. Key areas to research based on design:
        - Animation library for card transitions
        - Form validation patterns
        - Mobile navigation component
```

---

## 7. Integration Plan

### New Command: `/gsd:design-phase`

**File:** `commands/gsd/design-phase.md`

```yaml
---
name: gsd:design-phase
description: Create visual/UX design specifications before planning
argument-hint: "[phase]"
allowed-tools:
  - Read
  - Bash
  - Task
---

<objective>
Create design specifications for a phase. Spawns gsd-designer agent with phase context.

**Orchestrator role:** Parse phase, validate against roadmap, check existing design, gather context chain (CONTEXT.md → implement-ui → codebase), spawn designer agent, enable conversational refinement.

**Why subagent:** Design requires focused attention with quality-forcing patterns. Fresh 200k context for design generation. Main context reserved for user refinement conversation.
</objective>

<context>
Phase number: $ARGUMENTS (required)

Check for existing design:
```bash
ls .planning/phases/${PHASE}-*/*DESIGN.md 2>/dev/null
```
</context>

<process>
[Process steps as defined in agent specification]
</process>

<success_criteria>
- [ ] Phase validated against roadmap
- [ ] Context chain loaded (CONTEXT.md, implement-ui, codebase)
- [ ] gsd-designer spawned with quality-forcing patterns
- [ ] DESIGN.md created with all sections
- [ ] User informed of refinement options
</success_criteria>
```

### Orchestrator Prompt Construction Template

The orchestrator assembles context into a structured prompt before spawning gsd-designer. This template ensures consistent, high-quality input to the design agent:

```xml
<design_context>
  Product: [From PROJECT.md - What This Is]
  Platform: [Inferred from codebase or PROJECT.md constraints]
  Phase: [N]: [Phase name from ROADMAP.md]

  Target audience:
  [From PROJECT.md - Context section]

  Core value this design must serve:
  [From PROJECT.md - Core Value section]

  Technical constraints:
  [From PROJECT.md - Constraints section]
</design_context>

<phase_requirements>
  Goal: [From ROADMAP.md phase entry]

  Success criteria:
  [From ROADMAP.md - what this phase must achieve]

  Requirements mapped:
  [From ROADMAP.md - specific features/behaviors]
</phase_requirements>

<user_vision>
  [If CONTEXT.md exists, include:]

  How this should work:
  [From CONTEXT.md - How This Should Work section]

  What must be nailed:
  [From CONTEXT.md - What Must Be Nailed section]

  Reference products:
  [From CONTEXT.md - Specific Ideas section, or from Q&A]

  [If CONTEXT.md doesn't exist:]

  Vision inferred from phase requirements and PROJECT.md context.
  Reference products: [From Q&A if asked, or "None specified"]
</user_vision>

<existing_aesthetic>
  [If implement-ui skill exists:]

  Authoritative patterns from implement-ui skill:
  - Color palette: [exact values]
  - Typography: [font families, sizes]
  - Spacing system: [scale values]
  - Component library: [named components]

  [If no skill, from codebase analysis:]

  Discovered patterns from codebase:
  - Colors found: [hex values from theme/styles]
  - Components found: [existing component names]
  - Layout patterns: [grid systems, spacing used]

  [If greenfield:]

  No existing aesthetic. Design fresh with platform conventions.
</existing_aesthetic>

<quality_expectation>
  Commercial benchmark: Design must look like [benchmark from table below]
  - intentional decisions, not defaults.

  | Platform | Benchmark |
  |----------|-----------|
  | Web SaaS | Well-funded SaaS with Series A+ design budget |
  | Mobile app | Top 100 App Store app in this category |
  | Desktop app | Commercial $200+ professional software |

  Pre-emptive criticism: Assume the user will say "This looks like generic
  AI output." Generate something that proves them wrong.

  Accountability check: Could you show this design to a professional UI
  designer and claim it as skilled work? If not, it's not done.
</quality_expectation>

<output_specification>
  Generate: DESIGN.md following template structure

  Location: .planning/phases/{phase}-{slug}/{phase}-DESIGN.md

  Required sections:
  1. Visual Identity (philosophy, direction, inspiration)
  2. Screen Layouts (ASCII wireframes with dimensions)
  3. Component Specifications (visual, states, content)
  4. UX Flows (entry, steps, decisions, completion, errors)
  5. Design System Decisions (colors, typography, spacing with rationale)
  6. Platform-Specific Notes (responsive, touch targets, accessibility)
  7. Verification Criteria (observable behaviors proving correct implementation)
</output_specification>

<validation_requirements>
  Before returning, verify:
  - [ ] All screens have ASCII layouts with spacing specified
  - [ ] All new components have state definitions
  - [ ] Color palette has character (not generic dark gray + blue)
  - [ ] Spacing values follow consistent scale
  - [ ] Typography hierarchy is explicit
  - [ ] Verification criteria are observable and testable

  Self-review checklist (MANDATORY):
  - [ ] Does the color palette have character or is it generic?
  - [ ] Does spacing feel intentional or arbitrary?
  - [ ] Do controls look refined or like default inputs?
  - [ ] Would a professional designer claim this as their work?

  If any answer is "generic/arbitrary/default/no," refine before returning.
</validation_requirements>
```

**Prompt Assembly Process:**

1. Load PROJECT.md → Extract product context, audience, constraints
2. Load ROADMAP.md → Extract phase goal, success criteria, requirements
3. Check CONTEXT.md → If exists, extract vision sections
4. Check implement-ui skill → If exists, load authoritative patterns
5. Analyze codebase → Fill gaps not covered by skill
6. Run adaptive Q&A → If genuine gaps remain (especially reference products)
7. Assemble prompt → Populate template sections
8. Spawn gsd-designer → Pass assembled prompt as task description

### New Agent: `gsd-designer`

**File:** `agents/gsd-designer.md`

[Full agent definition as specified in Section 4]

### Modified Workflows

#### `research-phase` Workflow Update

Add DESIGN.md to context loading:

```markdown
## Context Loading

Load design context if exists:
```bash
cat .planning/phases/${PHASE}-*/${PHASE}-DESIGN.md 2>/dev/null
```

If DESIGN.md exists, research should address:
- Libraries needed for specified interactions
- Technical feasibility of design requirements
- Platform-specific implementation approaches
```

#### `plan-phase` Workflow Update

Add DESIGN.md to plan context:

```markdown
## Plan Context

When DESIGN.md exists:
- Tasks reference specific screens/components from design
- Verification criteria include design verification items
- must_haves include design-specified observable behaviors
```

### File Structure Changes

New file location:
```
.planning/phases/XX-name/{phase}-DESIGN.md
```

Follows existing pattern for phase artifacts.

---

## 8. Open Questions

### Questions for Future Consideration

1. **Design templates/presets**
   - Should GSD ship with aesthetic templates (SaaS dashboard, mobile app, etc.)?
   - How would users select/customize these?

2. **Design versioning**
   - If design changes significantly after research, how to handle?
   - Should there be DESIGN-v2.md or just overwrite?

3. **Cross-phase design consistency**
   - How to ensure Phase 3 design matches Phase 2?
   - Should there be a project-level design system document?

4. **Design for non-UI phases**
   - API design? Data model design? Architecture diagrams?
   - Or keep design-phase purely for UI/UX?

5. **Screenshot input**
   - Claude can receive images — could users provide screenshots of inspiration?
   - Context window cost vs value tradeoff?

### Decisions Made in This Session

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Workflow position | After discuss, before research | Design informs technical research |
| Trigger mechanism | Explicit user invocation | User knows when design is needed |
| Quality patterns | All 5 included | Comprehensive quality forcing |
| Existing aesthetic | Tiered (skill → codebase → fresh) | Balances authority with discovery |
| Output format | ASCII + prose | Text-based, no external tools |
| Iteration style | Conversational refinement | Matches discuss-phase pattern |
| Mandatory context | PROJECT.md always loaded | Target audience/problems shape design |
| Optional upstream | discuss/design/research all optional | Only plan + execute are mandatory |
| Pre-design Q&A | Adaptive (smart assessment) | Only ask if genuine gaps exist |
| Reference products | Ask if not in CONTEXT.md | Hard to infer, high value for direction |

---

## 9. Recommended Next Steps

### Phase 1: Core Implementation

1. **Create gsd-designer agent** (`agents/gsd-designer.md`)
   - Full agent definition with quality-forcing patterns
   - Tool specification
   - Execution flow
   - Structured returns

2. **Create design-phase command** (`commands/gsd/design-phase.md`)
   - Orchestrator logic
   - Context chain loading
   - Agent spawning
   - Refinement support

3. **Create DESIGN.md template** (`get-shit-done/templates/design.md`)
   - Full template structure
   - Section guidelines
   - Example content

### Phase 2: Integration

4. **Update research-phase**
   - Load DESIGN.md in context
   - Research based on design requirements

5. **Update plan-phase**
   - Reference DESIGN.md in task creation
   - Include design verification in must_haves

6. **Update execute-phase**
   - Executor reads DESIGN.md for implementation guidance

### Phase 3: Testing & Refinement

7. **Test with real project**
   - Run design-phase on UI-heavy phase
   - Iterate on quality-forcing patterns
   - Refine output format based on usage

8. **Document in help**
   - Add to `/gsd:help` command reference
   - Document when to use design-phase

### Quick Win: Prototype First

Before full implementation, create minimal version:
- gsd-designer agent (core only)
- design-phase command (basic orchestration)
- Test on single phase

Validate approach before building full integration.

---

## Appendix: Example DESIGN.md

### Phase 3: User Dashboard - Design Specification

**Designed:** 2026-01-19
**Platform:** Web (React + Tailwind)
**Aesthetic source:** Codebase analysis + fresh design

## Visual Identity

Professional analytics dashboard with approachable data visualization. Clean density inspired by Linear, with generous whitespace that doesn't sacrifice information. Dark mode primary (analysts work long hours), with a distinctive deep navy (`#0a0f1a`) instead of generic black. Amber accent (`#F59E0B`) for energy and warmth.

**Design direction:**
- Overall feel: "Powerful yet approachable"
- Key differentiator: "Data-dense without feeling cluttered"
- Inspiration: Linear's information hierarchy, Stripe's professional polish

---

## Screen Layouts

### Dashboard Overview

```
+------------------------------------------------------------------+
|  [Sidebar]  |  [Header: Page Title    Date Picker    [Export]]   |
|             |--------------------------------------------------------|
|  [Logo]     |                                                    |
|             |  [KPI Card 1]  [KPI Card 2]  [KPI Card 3]  [KPI 4] |
|  Dashboard  |                                                    |
|  Campaigns  |--------------------------------------------------------|
|  Reports    |                                                    |
|  Settings   |  +--------------------------------------------+    |
|             |  |                                            |    |
|  [Avatar]   |  |           Main Chart Area                  |    |
|             |  |           (Trend over time)                |    |
|             |  |                                            |    |
|             |  +--------------------------------------------+    |
|             |                                                    |
|             |  +---------------------+  +---------------------+  |
|             |  | Secondary Chart 1   |  | Secondary Chart 2   |  |
|             |  | (Funnel)            |  | (Top Campaigns)     |  |
|             |  +---------------------+  +---------------------+  |
+------------------------------------------------------------------+
```

**Dimensions:** 1440×900 primary, responsive to 1024px
**Edge padding:** 24px
**Component gaps:** 16px
**Sidebar width:** 240px (collapsible to 64px on tablet)

---

*[Full example would continue with all sections...]*

---

**End of Proposal**
