---
name: ms:design-phase
description: Create visual/UX design specifications before planning
argument-hint: "[phase]"
allowed-tools:
  - Read
  - Bash
  - Task
  - AskUserQuestion
  - Skill
---

<objective>
Create design specifications for a phase. Spawns ms-designer agent with phase context.

**Orchestrator role:** Parse phase, validate against roadmap, check existing design, gather context chain (CONTEXT.md → project UI skill → codebase), adaptive Q&A if gaps, spawn designer agent, enable conversational refinement.

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
# ms-tools is on PATH — invoke directly, not as a script path
ms-tools find-phase "$ARGUMENTS"
```

**If not found (dir is null):** Error and exit with message: "Phase not found in ROADMAP.md"

**If found:** Extract phase number, name, description from the returned JSON and ROADMAP.md.

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

## 3. Discover Relevant Skills

Before gathering context, check for skills that provide design-relevant conventions.

**3a. Scan available skills:**

Scan skills in your system-reminder for matches. Look for skills related to:
- The platform or framework (Flutter, React, web, etc.)
- UI conventions, design systems, or component patterns
- The specific domain of this phase (from the ROADMAP.md phase description extracted in step 1)

**3b. Confirm with user:**

Present via AskUserQuestion with `multiSelect: true`:
- Each matching skill is one option (label: skill name, description: what it provides)
- Always include a "None — skip skill loading" option
- User selects which to load, skips, or types a skill name in the free-text field

**3c. Load selected skills:**

Invoke each confirmed skill via the Skill tool. Extract aesthetic patterns (colors, components, spacing, typography) from loaded content for the `<existing_aesthetic>` block in step 6.

## 4. Gather Context Chain

Load context in order of priority:

**4a. Mandatory context:**

```bash
# Load PROJECT.md for product context
cat .planning/PROJECT.md 2>/dev/null

# Load ROADMAP.md for phase requirements
grep -A30 "Phase ${PHASE}:" .planning/ROADMAP.md 2>/dev/null
```

Extract from PROJECT.md:
- What This Is (product type)
- Core Value (design must serve this)
- Who It's For (target audience and their context)
- Core Problem (what the design must address)
- How It's Different (competitive context, differentiators)
- Key User Flows (primary interactions that drive hierarchy)
- Constraints (platform, technical limits)

Extract from ROADMAP.md:
- Phase goal
- Success criteria
- Requirements mapped

**4b. Optional context - CONTEXT.md (from discuss-phase):**

```bash
cat .planning/phases/${PHASE}-*/${PHASE}-CONTEXT.md 2>/dev/null
```

If exists, extract:
- How This Should Work (vision)
- What Must Be Nailed (essentials)
- Specific Ideas (references to products)

**4b2. Optional context — prior knowledge:**

Match subsystem(s) to this phase by comparing ROADMAP phase description against subsystem names in config.json. Load matching knowledge files:

```bash
jq -r '.subsystems[]' .planning/config.json 2>/dev/null
cat .planning/knowledge/{matched_subsystem}.md 2>/dev/null
```

If knowledge files exist, extract:
- Architecture patterns (tech constraints the design must respect)
- Prior design patterns (visual consistency)
- Key decisions (constraints)
- Pitfalls (design must avoid known traps)

Pass the extracted knowledge to ms-designer in the design prompt (see step 6 `<prior_knowledge>` block).

**4c. Optional context - codebase analysis:**

```bash
# Platform detection
if [ -f "pubspec.yaml" ]; then
  echo "Platform: Flutter (pubspec.yaml found)"
  # Search Flutter project structure
  find lib -name "*.dart" 2>/dev/null | head -20
  grep -r "colors\|theme\|spacing" lib/ --include="*.dart" 2>/dev/null | head -10
elif [ -f "package.json" ]; then
  echo "Platform: Web (package.json found)"
  grep -E "react|vue|angular|svelte" package.json 2>/dev/null | head -5
  # Search web project structure
  find src -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" 2>/dev/null | head -20
  grep -r "colors\|theme\|spacing" src/ --include="*.ts" --include="*.tsx" 2>/dev/null | head -10
fi
```

Document discovered patterns for the designer.

## 5. Adaptive Q&A (If Gaps Exist)

Assess context coverage:
- Can platform be inferred? (from codebase or PROJECT.md)
- Can visual style be inferred? (from project UI skill or codebase)
- Can design priorities be inferred? (from CONTEXT.md or phase requirements)

**If everything can be inferred:** Skip to step 6.

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

## 5b. Mockup Generation (Optional)

After gathering context and closing gaps, assess whether this phase has significant new UI (new screens, novel flows, complex layouts — not minor tweaks to existing patterns).

**If significant new UI detected:**

Use AskUserQuestion:
> "This phase involves [brief UI description]. Generate visual mockups to explore directions first?"
> 1. **Yes, generate mockups** — Spawn 3 HTML mockup variants before DESIGN.md
> 2. **No, go straight to design spec** — Proceed directly to ms-designer

**If user selects "Yes":**

Read `~/.claude/mindsystem/workflows/mockup-generation.md` and follow the mockup-generation workflow.

1. Determine platform from context chain (or ask user)
2. Identify primary screen for the phase
3. Derive 3 design directions from feature context
4. Present directions to user for approval/tweaking
5. Read platform template (mobile or web)
6. Spawn 3 x ms-mockup-designer agents in parallel
7. Run comparison script (`compare_mockups.py`), open in browser, and present to user
8. Handle selection (single pick, combine, tweak, more variants, or skip)
9. Extract CSS specs from chosen variant into `<mockup_direction>` block

Pass gathered context (PROJECT.md, ROADMAP.md phase entry, existing aesthetic) to the workflow. The workflow returns either a `<mockup_direction>` block for step 6, or nothing if user skips.

**If user selects "No":** Proceed directly to step 6.

## 6. Spawn ms-designer Agent

Assemble the design prompt from gathered context:

```markdown
<design_context>
Product: [From PROJECT.md - What This Is]
Platform: [Inferred from codebase or PROJECT.md constraints]
Phase: [N]: [Phase name from ROADMAP.md]

Target audience:
[From PROJECT.md - Who It's For section]

Core problem:
[From PROJECT.md - Core Problem section]

Competitive differentiators:
[From PROJECT.md - How It's Different section]

Core value this design must serve:
[From PROJECT.md - Core Value section]

Primary user flows:
[From PROJECT.md - Key User Flows section]

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

<prior_knowledge>
[If knowledge files exist:]

Architecture constraints:
[From knowledge Architecture sections]

Prior design patterns:
[From knowledge Design sections]

Pitfalls to avoid:
[From knowledge Pitfalls sections]

[If no knowledge files exist:]

No prior knowledge files. First phase or no prior execution.
</prior_knowledge>

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
[If mockups were generated in step 5b, include the extracted specs:]

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

<quality_constraints>
Specify exact values for every design token — colors as hex, spacing in px/dp, typography with weight+size+line-height. No "appropriate", "suitable", or "as needed". Every decision must be explicit and implementable without interpretation.

Differentiate from platform defaults: if a color, radius, or spacing matches the default system value, choose a deliberate alternative that serves the product's identity.

Assume the user will say "This looks like generic AI output." Generate something that proves them wrong. Could you show this design to a professional UI designer and claim it as skilled work? If not, it's not done.
</quality_constraints>

<output_specification>
Generate: DESIGN.md following template structure

Location: .planning/phases/{phase}-{slug}/{phase}-DESIGN.md

Required sections:
1. Design Direction (1-2 sentences: feel, inspiration)
2. Design Tokens (compact table: token, value, note)
3. Screens (per screen: wireframe with inline annotations, States table, Behavior notes, Hints)

Verification criteria are not a section — plan writer derives from specs.
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

## 7. Handle Agent Return

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

## 8. Conversational Refinement

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

Read `~/.claude/mindsystem/templates/design-iteration.md` and use the iteration template:

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

## 9. Update Last Command

```bash
ms-tools set-last-command "ms:design-phase $ARGUMENTS"
```

</process>

<success_criteria>
- [ ] Available skills scanned, surfaced via AskUserQuestion, and loaded via Skill tool
- [ ] Codebase analyzed for existing patterns (step 4c)
- [ ] Adaptive Q&A completed if context gaps existed
- [ ] Mockup generation offered if phase has significant new UI
- [ ] Mockup direction extracted and passed to ms-designer (if generated)
- [ ] ms-designer spawned with quality-forcing patterns
- [ ] DESIGN.md created with Design Direction, Design Tokens, and Screens sections and committed
- [ ] User informed of refinement options and next steps
- [ ] STATE.md Last Command updated with timestamp
</success_criteria>
