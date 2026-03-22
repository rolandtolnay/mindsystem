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

**Orchestrator role:** Parse phase, validate against roadmap, check existing design, gather context chain (CONTEXT.md → design skill → codebase extraction), adaptive Q&A if gaps, spawn designer agent, enable conversational refinement.

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

Resolve phase directory:
```bash
ms-tools find-phase "$ARGUMENTS"
```

Check for existing design:
```bash
ls ${PHASE_DIR}/*DESIGN.md 2>/dev/null
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
# PHASE_DIR already resolved from find-phase in <context>
ls "${PHASE_DIR}"/*-DESIGN.md 2>/dev/null
```

**If exists:** Use AskUserQuestion to offer:
1. **Update design** — Spawn designer with existing design as context
2. **View existing** — Display current DESIGN.md
3. **Skip** — Proceed to research/planning without changes

Wait for response and act accordingly.

**If doesn't exist:** Continue to gather context.

## 3. Load Design Skills

```bash
DESIGN_SKILLS=$(ms-tools config-get skills.design --default "[]")
```

**If skills configured:** Invoke each via the Skill tool.

After loading, check if the skill content contains project-specific design tokens (hex colors in palette context, spacing scales with values, font family names). If it does, these are the authoritative aesthetic — skip step 4c. If it contains only design methodology or you're uncertain, proceed to codebase extraction in step 4c.

**If no skills configured:**

```
Tip: Configuring design skills in /ms:config can improve design and mockup quality. Run /ms:config to set them up.
```

Non-blocking. Proceed to codebase extraction in step 4c.

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
cat ${PHASE_DIR}/*-CONTEXT.md 2>/dev/null
```

If exists, extract:
- How This Should Work (vision)
- What Must Be Nailed (essentials)
- Specific Ideas (references to products)

**4b2. Optional context — prior knowledge:**

Match subsystem(s) to this phase by comparing ROADMAP phase description against subsystem names in config.json. Load matching knowledge files:

```bash
ms-tools config-get subsystems
cat .planning/knowledge/{matched_subsystem}.md 2>/dev/null
```

If knowledge files exist, extract:
- Architecture patterns (tech constraints the design must respect)
- Prior design patterns (visual consistency)
- Key decisions (constraints)
- Pitfalls (design must avoid known traps)

Pass the extracted knowledge to ms-designer in the design prompt (see step 6 `<prior_knowledge>` block).

**4c. Optional context - codebase aesthetic extraction:**

If authoritative aesthetic already gathered from skill in step 3 → skip this step.

Otherwise, spawn an Explore agent to extract the project's visual identity:

```
Task(
  prompt="Read `.planning/PROJECT.md` (Technical Context section) for tech stack. If PROJECT.md doesn't exist, read root dependency files (`pubspec.yaml`, `package.json`, etc.) to identify the framework.

Extract exact values for:
- **Color palette:** background, text, accent, error — hex values with semantic roles
- **Typography scale:** font families, size/weight combos
- **Spacing system:** recurring padding/margin/gap values
- **Reusable UI components:** names + visual characteristics (border-radius, shadows)
- **Layout conventions:** navigation pattern, content layout

Format findings as:

Color palette:
| Role | Value | Context |
|------|-------|---------|
| [role] | #hex | [where used] |

Typography:
| Element | Family | Size/Weight | Usage |
|---------|--------|-------------|-------|
| [element] | [family] | [size/weight] | [where used] |

Spacing scale:
[base unit and scale values]

Component inventory:
- [ComponentName] — [visual characteristics]

Layout conventions:
- [pattern description]

Extract EXACT values (hex codes, pixel values, font names). Don't summarize or approximate. Return 'not found' for sections with no data. Look in theme files, style constants, design token files, and framework-specific configuration — you know where these live for the detected framework.",
  subagent_type="Explore",
  description="Extract codebase aesthetic"
)
```

If the agent returns mostly empty results → greenfield. If substantive findings → use them for the `<existing_aesthetic>` block in step 6.

## 5. Adaptive Q&A (If Gaps Exist)

Assess context coverage:
- Can platform be inferred? (from codebase or PROJECT.md)
- Can visual style be inferred? (from existing aesthetic)
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

Read `~/.claude/mindsystem/workflows/mockup-generation.md` and follow the mockup-generation workflow. Generate 3 HTML mockup variants, present comparison to user, and handle selection.

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

No explicit vision provided. Derive design direction from phase requirements and product context above.
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
[Always present. Populated from skill content OR Explore agent findings OR greenfield.]

Color palette:
| Role | Value | Context |
|------|-------|---------|
| bg-primary | #hex | Main background |
| text-primary | #hex | Body text |
| accent | #hex | Interactive elements |
| ... | | |

Typography:
| Element | Family | Size/Weight | Usage |
|---------|--------|-------------|-------|
| heading | [family] | [size/weight] | Page titles |
| body | [family] | [size/weight] | General content |
| ... | | | |

Spacing scale:
[base unit and scale values, e.g. 4/8/12/16/24/32px]

Component inventory:
- [ComponentName] — [visual characteristics]

Layout conventions:
- [Navigation pattern, content layout, responsive breakpoints]

Platform: [Flutter / React / etc.]

[If greenfield: "No existing aesthetic. Design fresh with platform conventions."]
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

**Update state and commit:**

```bash
ms-tools set-last-command "ms:design-phase $ARGUMENTS"
git add ${PHASE_DIR}/*-DESIGN.md .planning/STATE.md
git commit -m "docs: create design for phase ${PHASE}"
```

Display summary from agent response:
- Platform designed for
- Aesthetic source used
- Screens designed
- Key design decisions

Also offer:
- **Refine design** — Discuss changes conversationally
- **View full design** — Display DESIGN.md

Read `~/.claude/mindsystem/references/prework-status.md` and present what's done vs still needed for this phase.

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

</process>

<success_criteria>
- [ ] Aesthetic context gathered: skills checked for design tokens, codebase extraction run if needed
- [ ] Adaptive Q&A completed if context gaps existed
- [ ] Mockup generation offered for significant UI; direction passed to ms-designer if generated
- [ ] ms-designer spawned with quality-forcing patterns
- [ ] DESIGN.md created with Design Direction, Design Tokens, and Screens sections and committed
- [ ] User informed of refinement options and next steps
- [ ] STATE.md Last Command updated with timestamp
</success_criteria>
