---
name: ms:design-phase
description: Create visual/UX design specifications before planning
argument-hint: "[phase]"
allowed-tools:
  - Read
  - Bash
  - Task
  - AskUserQuestion
---

<objective>
Create design specifications for a phase. Spawns ms-designer agent with phase context.

**Orchestrator role:** Parse phase, validate against roadmap, check existing design, gather context chain (CONTEXT.md → project UI skill → codebase), adaptive Q&A if gaps, spawn designer agent, enable conversational refinement.

**Why subagent:** Design requires focused attention with quality-forcing patterns. Fresh 200k context for design generation. Main context reserved for user refinement conversation.

**When to use:**
- UI-heavy phases with significant new interface work
- Novel flows/components not deducible from existing patterns
- Features requiring careful UX consideration
- Cross-platform work needing coordinated design

**Not needed for:**
- Backend-only phases
- Minor UI tweaks using existing patterns
- Phases where established patterns suffice
</objective>

<context>
Phase number: $ARGUMENTS (required)

Check for existing design:
```bash
ls .planning/phases/${PHASE}-*/*DESIGN.md 2>/dev/null
```
</context>

<process>

## 1. Parse and Validate Phase

```bash
# Extract and normalize phase number from arguments
PHASE_ARG="$ARGUMENTS"
PHASE=$(printf "%02d" "$PHASE_ARG" 2>/dev/null || echo "$PHASE_ARG")

# Validate phase exists in roadmap
grep -A5 "Phase ${PHASE}:" .planning/ROADMAP.md 2>/dev/null
```

**If not found:** Error and exit with message: "Phase ${PHASE} not found in ROADMAP.md"

**If found:** Extract phase number, name, description. Store for later use.

## 2. Check Existing Design

```bash
# Check for existing DESIGN.md
PHASE_DIR=$(ls -d .planning/phases/${PHASE}-* 2>/dev/null | head -1)
ls "${PHASE_DIR}"/*-DESIGN.md 2>/dev/null
```

**If exists:** Use AskUserQuestion to offer:
1. **Update design** — Spawn designer with existing design as context
2. **View existing** — Display current DESIGN.md
3. **Skip** — Proceed to research/planning without changes

Wait for response and act accordingly.

**If doesn't exist:** Continue to gather context.

## 3. Gather Context Chain

Load context in order of priority:

**3a. Mandatory context:**

```bash
# Load PROJECT.md for product context
cat .planning/PROJECT.md 2>/dev/null

# Load ROADMAP.md for phase requirements
grep -A30 "Phase ${PHASE}:" .planning/ROADMAP.md 2>/dev/null
```

Extract from PROJECT.md:
- What This Is (product type)
- Core Value (design must serve this)
- Context (target audience)
- Constraints (platform, technical limits)

Extract from ROADMAP.md:
- Phase goal
- Success criteria
- Requirements mapped

**3b. Optional context - CONTEXT.md (from discuss-phase):**

```bash
cat .planning/phases/${PHASE}-*/${PHASE}-CONTEXT.md 2>/dev/null
```

If exists, extract:
- How This Should Work (vision)
- What Must Be Nailed (essentials)
- Specific Ideas (references to products)

**3c. Optional context — project UI skill:**

Discover project-level skills:
```bash
ls .claude/skills/*/SKILL.md 2>/dev/null
```

If skills found, read the YAML frontmatter (name + description) of each SKILL.md. Identify any skill whose description indicates it provides UI implementation patterns (screens, widgets, components, theming, spacing, visual patterns).

If a UI skill is found, read its full content. Extract aesthetic patterns (colors, components, spacing, typography) for the `<existing_aesthetic>` block passed to ms-designer.

**3d. Optional context - codebase analysis:**

```bash
# Platform detection
if [ -f "package.json" ]; then
  echo "Platform: Web (package.json found)"
  grep -E "react|vue|angular|svelte" package.json 2>/dev/null | head -5
fi

if [ -f "pubspec.yaml" ]; then
  echo "Platform: Flutter (pubspec.yaml found)"
fi

# Find existing component/theme files
find src -name "*.tsx" -o -name "*.dart" 2>/dev/null | head -20
grep -r "colors\|theme\|spacing" src/ --include="*.ts" --include="*.dart" 2>/dev/null | head -10
```

Document discovered patterns for the designer.

## 4. Adaptive Q&A (If Gaps Exist)

Assess context coverage:
- Can platform be inferred? (from codebase or PROJECT.md)
- Can visual style be inferred? (from project UI skill or codebase)
- Can design priorities be inferred? (from CONTEXT.md or phase requirements)

**If everything can be inferred:** Skip to step 5.

**If gaps exist:** Use AskUserQuestion with targeted questions.

Most valuable question (if reference products not in CONTEXT.md):
> "Are there apps or sites whose design you'd like this to feel like?"

Other potential questions (only if genuine gaps):
- Visual direction (if no existing aesthetic)
- Density preference (if not inferrable)
- Platform priority (if multi-platform)

**Decision gate after Q&A:**
Use AskUserQuestion to confirm:
1. **Create DESIGN.md** — Proceed to spawn designer
2. **Ask more questions** — Continue gathering context
3. **Add context** — Let user provide additional information

## 4b. Mockup Generation (Optional)

After gathering context and closing gaps, assess whether this phase has significant new UI (new screens, novel flows, complex layouts — not minor tweaks to existing patterns).

**If significant new UI detected:**

Use AskUserQuestion:
> "This phase involves [brief UI description]. Generate visual mockups to explore directions first?"
> 1. **Yes, generate mockups** — Spawn 3 HTML mockup variants before DESIGN.md
> 2. **No, go straight to design spec** — Proceed directly to ms-designer

**If user selects "Yes":**

Follow mockup-generation workflow:
@~/.claude/mindsystem/workflows/mockup-generation.md

1. Determine platform from context chain (or ask user)
2. Identify primary screen for the phase
3. Derive 3 design directions from feature context
4. Present directions to user for approval/tweaking
5. Read platform template (mobile or web)
6. Spawn 3 x ms-mockup-designer agents in parallel
7. Generate comparison page, open in browser, and present to user
8. Handle selection (single pick, combine, tweak, more variants, or skip)
9. Extract CSS specs from chosen variant into `<mockup_direction>` block

Pass gathered context (PROJECT.md, ROADMAP.md phase entry, existing aesthetic) to the workflow. The workflow returns either a `<mockup_direction>` block for step 5, or nothing if user skips.

**If user selects "No":** Proceed directly to step 5.

## 5. Spawn ms-designer Agent

Assemble the design prompt from gathered context:

```markdown
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
[If CONTEXT.md exists:]

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
[If project UI skill exists:]

Authoritative patterns from project UI skill:
- Color palette: [exact values]
- Typography: [font families, sizes]
- Spacing system: [scale values]
- Component library: [named components]

[If no UI skill, from codebase analysis:]

Discovered patterns from codebase:
- Colors found: [hex values from theme/styles]
- Components found: [existing component names]
- Layout patterns: [grid systems, spacing used]

[If greenfield:]

No existing aesthetic. Design fresh with platform conventions.
</existing_aesthetic>

<mockup_direction>
[If mockups were generated in step 4b, include the extracted specs:]

Direction: [chosen direction name]
Philosophy: [direction one-sentence philosophy]

Color palette:
[Extracted hex values — background, text, accent, secondary, etc.]

Layout structure:
[How content is arranged — sidebar/topnav/stacked, grid/list, etc.]

Typography:
[Font sizes, weights, line-heights extracted from mockup CSS]

Spacing:
[Padding, gaps, margins extracted from mockup CSS]

User preferences:
[Any specific feedback from mockup selection — "I liked X but want Y changed"]

[If mockups were NOT generated, omit this entire block.]
</mockup_direction>

<quality_expectation>
Commercial benchmark: This design must look like a [benchmark] with intentional decisions, not defaults.

Pre-emptive criticism: Assume the user will say "This looks like generic AI output." Generate something that proves them wrong.

Accountability check: Could you show this design to a professional UI designer and claim it as skilled work? If not, it's not done.
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
```

Spawn the agent:

```
Task(
  prompt=assembled_design_prompt,
  subagent_type="ms-designer",
  description="Design Phase {phase}"
)
```

## 6. Handle Agent Return

**`## DESIGN COMPLETE`:**

Commit the design file:

```bash
git add .planning/phases/${PHASE}-*/*-DESIGN.md
git commit -m "docs: create design for phase ${PHASE}"
```

Display summary from agent response:
- Platform designed for
- Aesthetic source used
- Screens designed
- Key design decisions

Then present pre-work status: Read `~/.claude/mindsystem/references/prework-status.md` and show what's done vs still needed for this phase.

Also offer:
- **Refine design** — Discuss changes conversationally
- **View full design** — Display DESIGN.md

**`## DESIGN NEEDS CLARIFICATION`:**

Present the question to user. Get response. Spawn continuation with the clarification.

## 7. Conversational Refinement

After initial generation, if user wants to refine:

- Read DESIGN.md directly
- Discuss changes conversationally
- Edit DESIGN.md directly (no subagent needed for small changes)
- For major redesign, spawn ms-designer again with structured feedback

**Refinement principles:**
- Direct edits — Edit DESIGN.md directly, don't regenerate
- Preserve decisions — Changes are incremental, not wholesale replacement
- User controls pace — User decides when design is "done"

**For major redesigns (multiple aspects changing):**

Use the iteration template from `~/.claude/mindsystem/templates/design-iteration.md`:

1. Capture feedback using the structured format:
   - What worked well (KEEP)
   - What needs improvement (FIX)
   - New requirements (ADD)
   - Primary focus for this iteration

2. Spawn ms-designer with iteration context:
   - Include `<previous_design>` with relevant sections
   - Include `<feedback_on_previous>` with structured feedback
   - Include `<specific_focus>` identifying the ONE thing
   - Include `<constraints>` noting what must NOT change

3. After iteration completes:
   - Verify "what worked well" was preserved
   - Verify "what needs improvement" was addressed
   - Update design version in DESIGN.md frontmatter

## 8. Update Last Command

Update `.planning/STATE.md` Last Command field:
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:design-phase $ARGUMENTS | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line

</process>

<success_criteria>
- [ ] Phase validated against roadmap
- [ ] Existing design checked and handled appropriately
- [ ] Context chain loaded (PROJECT.md, ROADMAP.md, CONTEXT.md if exists)
- [ ] Project UI skill discovered and loaded if exists
- [ ] Codebase analyzed for existing patterns
- [ ] Adaptive Q&A completed if gaps existed
- [ ] Mockup generation offered if phase has significant new UI
- [ ] Mockup direction extracted and passed to ms-designer (if generated)
- [ ] ms-designer spawned with quality-forcing patterns
- [ ] DESIGN.md created with all 7 sections
- [ ] DESIGN.md committed
- [ ] User informed of refinement options and next steps
</success_criteria>
