<purpose>
Generate HTML/CSS mockup variants for visual direction exploration. Spawns parallel ms-mockup-designer agents, presents results, handles user selection, and extracts CSS specs into a `<mockup_direction>` block for ms-designer.

Called by design-phase command (step 4b) when user opts into mockup generation.
</purpose>

<required_reading>
@~/.claude/mindsystem/references/design-directions.md
@~/.claude/mindsystem/templates/mockup-mobile.md (if mobile)
@~/.claude/mindsystem/templates/mockup-web.md (if web)
</required_reading>

<process>

<step name="determine_platform">
Infer platform from context chain:
- `pubspec.yaml` exists → mobile
- `package.json` with React/Vue/Angular/Svelte → web
- PROJECT.md constraints → check for platform mentions

If ambiguous, use AskUserQuestion:
> "Which platform should the mockups target?"
> 1. **Mobile** — iPhone device frame
> 2. **Web** — Desktop viewport
</step>

<step name="identify_primary_screen">
Determine which screen to mock up from phase requirements.

Single primary screen/feature → use it directly.

Multiple screens or ambiguous → use AskUserQuestion to confirm which screen to mock up. The primary screen is the one that defines the visual direction — typically the most novel or complex screen in the phase.
</step>

<step name="derive_directions">
Read `~/.claude/mindsystem/references/design-directions.md`. Follow the 3-step derivation process:

1. **Identify primary design tension** for this feature
2. **Pick most valuable exploration axes** from feature context
3. **Generate 3 directions** — each with name, one-sentence philosophy, and 2-3 concrete layout/component choices

Present all 3 directions to user via AskUserQuestion:
> "Here are 3 design directions for [screen]. Generate mockups for all 3?"
>
> **A: {Direction A name}** — {one-sentence philosophy}
> **B: {Direction B name}** — {one-sentence philosophy}
> **C: {Direction C name}** — {one-sentence philosophy}
>
> 1. **Generate mockups** — Spawn 3 parallel agents, one per direction
> 2. **Tweak directions first** — Adjust before generating
> 3. **Let me describe different directions** — Replace with your own

If user picks option 2 or 3, incorporate their input, re-derive or adjust directions, and present again.
</step>

<step name="read_template">
Read the mockup template for the selected platform:

```bash
cat ~/.claude/mindsystem/templates/mockup-{platform}.md
```

Extract the HTML scaffold from the `<template>` block.
</step>

<step name="spawn_agents">
```bash
PHASE_DIR=$(ls -d .planning/phases/${PHASE}-* 2>/dev/null | head -1)
mkdir -p "${PHASE_DIR}/mockups"
```

Spawn 3 ms-mockup-designer agents IN PARALLEL, each receiving:
- `<product_context>` — From PROJECT.md
- `<phase_context>` — From ROADMAP.md phase entry
- `<design_direction>` — One of the 3 derived directions (name, philosophy, concrete choices)
- `<platform>` — `mobile` or `web`
- `<feature_grounding>` — The screen/feature being mocked
- `<existing_aesthetic>` — Colors/fonts from implement-ui or codebase (if exists)
- `<mockup_template>` — The HTML scaffold from the template file
- Output path: `.planning/phases/{phase}-{slug}/mockups/variant-a.html` (b, c for others)

```
Task(prompt=assembled_context, subagent_type="ms-mockup-designer", description="Mockup variant A")
Task(prompt=assembled_context, subagent_type="ms-mockup-designer", description="Mockup variant B")
Task(prompt=assembled_context, subagent_type="ms-mockup-designer", description="Mockup variant C")
```
</step>

<step name="present_mockups">
After all 3 agents return, display file paths:

```markdown
3 mockup variants generated:

- **A: {Direction A name}** — `.planning/phases/{phase}-{slug}/mockups/variant-a.html`
- **B: {Direction B name}** — `.planning/phases/{phase}-{slug}/mockups/variant-b.html`
- **C: {Direction C name}** — `.planning/phases/{phase}-{slug}/mockups/variant-c.html`

Open these in your browser to compare.
```

Use AskUserQuestion:
> "Which direction works best?"
> 1. **A: {name}** — Use this direction
> 2. **B: {name}** — Use this direction
> 3. **C: {name}** — Use this direction
> 4. **Combine elements** — Mix two directions
> (free text also accepted for: tweak requests, "more variants", or "skip mockups")
</step>

<step name="handle_selection">
Handle user response:

**Single choice (A/B/C):** Read the chosen HTML file. Proceed to `extract_specs`.

**Combine:** Spawn one more ms-mockup-designer with a combined direction (elements from both chosen variants). Output to `variant-combined.html`. Present for confirmation, then proceed to `extract_specs`.

**Tweak:** Spawn one more ms-mockup-designer with the chosen variant plus tweak instructions. Output to `variant-{letter}-tweaked.html`. Present for confirmation, then proceed to `extract_specs`.

**More variants:** Loop back to `derive_directions`. Derive 3 new directions (avoid repeating previous ones).

**Skip:** Return no `<mockup_direction>` block. Design-phase proceeds to ms-designer without mockup context.
</step>

<step name="extract_specs">
Read the chosen HTML file. Extract from the inline CSS:
- Direction name and description (from the derived direction that was selected)
- Color palette — `background`, `color`, CSS custom properties, repeated accent values
- Layout structure — container arrangement (sidebar/topnav/stacked, grid/list)
- Typography — `font-size`, `font-weight`, `line-height` from headings and body
- Spacing — `padding`, `gap`, `margin` values used consistently
- User preferences (any specific feedback from selection)

Assemble into a `<mockup_direction>` block for ms-designer. See the `<mockup_direction>` template in `design-phase.md` step 5 for the expected format.

Return this block to the design-phase orchestrator.
</step>

</process>
