<purpose>
Generate HTML/CSS mockup variants for visual direction exploration. Spawns parallel ms-mockup-designer agents, presents results, handles user selection, and extracts CSS specs into a `<mockup_direction>` block for ms-designer.

Called by design-phase command (step 4b) when user opts into mockup generation.
</purpose>

<required_reading>
@~/.claude/mindsystem/references/design-directions.md
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

Present directions as text output first, then collect the choice separately. Do NOT put direction details inside AskUserQuestion — text output has no truncation limits and renders full markdown.

**Output format** (as regular text, before the question):

```
Here are 3 design directions for the {screen}:

**A: {name}** — {philosophy}
{2-3 concrete layout/component choices as flowing text, ~1-2 lines}
→ Optimized for: {what this direction prioritizes — one phrase}

**B: {name}** — {philosophy}
{2-3 concrete layout/component choices as flowing text, ~1-2 lines}
→ Optimized for: {what this direction prioritizes — one phrase}

**C: {name}** — {philosophy}
{2-3 concrete layout/component choices as flowing text, ~1-2 lines}
→ Optimized for: {what this direction prioritizes — one phrase}
```

**Then** use AskUserQuestion with short options only — no direction details repeated:

> "Generate mockups for all 3 directions?"
> 1. **Generate mockups** — Spawn 3 parallel agents, one per direction
> 2. **Tweak directions first** — Adjust before generating
> 3. **Describe different directions** — Replace with your own ideas

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
# Assumes single match. If empty, phase directory is missing — stop and report.
mkdir -p "${PHASE_DIR}/mockups"
```

Spawn 3 ms-mockup-designer agents IN PARALLEL, each receiving:
- `<product_context>` — from PROJECT.md "What This Is" section
- `<phase_context>` — from ROADMAP.md phase entry
- `<design_direction>` — one of the 3 directions from `derive_directions` (name, philosophy, concrete choices)
- `<platform>` — `mobile` or `web` from `determine_platform`
- `<feature_grounding>` — screen/feature identified in `identify_primary_screen`
- `<existing_aesthetic>` — from project UI skill (`SKILL.md` with design tokens) if exists, else scan codebase theme/style files for colors and fonts. If greenfield, state "No existing aesthetic."
- `<mockup_template>` — HTML scaffold from `read_template`
- Output path: `.planning/phases/{phase}-{slug}/mockups/variant-a.html` (b, c for others)

```
Task(prompt=assembled_context, subagent_type="ms-mockup-designer", description="Mockup variant A")
Task(prompt=assembled_context, subagent_type="ms-mockup-designer", description="Mockup variant B")
Task(prompt=assembled_context, subagent_type="ms-mockup-designer", description="Mockup variant C")
```
</step>

<step name="present_mockups">
After all 3 agents return, run the comparison script to create the comparison page. Do NOT generate comparison HTML manually — use the script:

```bash
ms-compare-mockups "${PHASE_DIR}/mockups"
```

Read the `open_mockups` config setting:

```bash
OPEN_MOCKUPS=$(ms-tools config-get open_mockups --default "auto")
```

Branch on the value:

- **`"auto"` (default):** Run `open "${PHASE_DIR}/mockups/comparison.html"`. Display summary with "comparison page opened in browser."
- **`"ask"`:** Display summary with "comparison page ready." Ask "Open mockup comparison in browser?" (Yes/No). If Yes, run `open`.
- **`"off"`:** Display summary with explicit comparison page path. No open.

**Summary template** (adapt first line per branch above):

```markdown
3 mockup variants generated — {status line from branch}.

Individual variants for reference:
- **A: {Direction A name}** — `.planning/phases/{phase}-{slug}/mockups/variant-a.html`
- **B: {Direction B name}** — `.planning/phases/{phase}-{slug}/mockups/variant-b.html`
- **C: {Direction C name}** — `.planning/phases/{phase}-{slug}/mockups/variant-c.html`
```

**After displaying summary**, use AskUserQuestion:
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
Read the chosen HTML file. Extract from the inline CSS and assemble into a `<mockup_direction>` block with this exact structure:

```xml
<mockup_direction>
Direction: [chosen direction name]
Philosophy: [direction one-sentence philosophy]

Color palette:
[Extracted hex values — background, text, accent, secondary from `background`, `color`, CSS custom properties, repeated accent values]

Layout structure:
[Container arrangement from CSS — sidebar/topnav/stacked, grid/list]

Typography:
[`font-size`, `font-weight`, `line-height` from headings and body]

Spacing:
[`padding`, `gap`, `margin` values used consistently]

User preferences:
[Any specific feedback from mockup selection — "I liked X but want Y changed"]
</mockup_direction>
```

Return this block to the design-phase orchestrator.
</step>

</process>
