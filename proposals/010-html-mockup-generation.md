# HTML Mockup Generation in Design-Phase

> Extending design-phase with optional HTML/CSS mockup generation for visual direction exploration before DESIGN.md creation.
> Generated: 2026-02-07

## Executive Summary

Design-phase produces DESIGN.md — a structured specification with ASCII wireframes, color palettes, spacing values, and component specs. The specification is precise and machine-readable, but the user never sees a *visual* representation of the design before committing to it. By the time plan-phase converts DESIGN.md into implementation tasks, the user is trusting text descriptions and ASCII art to represent their product's visual identity.

This proposal adds an **optional mockup generation step** between context gathering and DESIGN.md creation. Three parallel subagents generate self-contained HTML/CSS files representing three distinct design directions. The user opens them in their browser, picks a direction (or combines elements), and that choice feeds into ms-designer as concrete visual context. DESIGN.md is then grounded in user-validated visual decisions rather than the agent's interpretation of text descriptions alone.

**Why HTML over AI image generation:** Image generators (Gemini, DALL-E) produce visuals that Claude cannot parse back into specs — the user becomes the bottleneck translating visual preferences into structured data. With HTML/CSS, the entire pipeline stays machine-readable: the CSS *is* the spec. Colors, spacing, typography, and layout are extractable directly from the chosen variant's source code. No external API key required. No Python dependency. No cost per generation.

**Architecture:** One new agent (`ms-mockup-designer`) with platform as a parameter (mobile/web). Three instances spawned in parallel during design-phase, each generating a variant grounded in the feature, the problem it solves, and the target audience. User reviews in browser, picks direction, orchestrator extracts CSS specs and passes them to ms-designer. DESIGN.md becomes the final, authoritative output — mockups are brainstorming artifacts.

---

## Background: How Design-Phase Works Today

### Current Flow

```
/ms:design-phase {phase}
  ├── Validate phase against ROADMAP.md
  ├── Check for existing DESIGN.md
  ├── Gather context chain:
  │     PROJECT.md → ROADMAP.md → CONTEXT.md → implement-ui skill → codebase
  ├── Adaptive Q&A if gaps exist
  ├── Spawn ms-designer subagent (fresh 200k context)
  │     └── 12-step process with quality-forcing patterns
  │         → Produces DESIGN.md with 7 sections
  ├── Commit DESIGN.md
  └── Offer refinement (direct edit / conversation / major redesign)
```

### Current Strengths

- **Context assembly is thorough** — 5-source priority chain ensures ms-designer has full picture
- **Quality-forcing patterns work** — commercial benchmark, pre-emptive criticism, accountability check, mathematical validation
- **DESIGN.md is precise** — hex codes, pixel values, font weights, not vague descriptions
- **Downstream consumption is clean** — research-phase, plan-phase, execute-plan all reference DESIGN.md directly

### Current Gap

The user never *sees* the design before committing to it. They review a markdown file with ASCII wireframes and color tables. For phases with established patterns (minor UI tweaks, extensions of existing screens), this is sufficient. For phases introducing **novel screens, new visual directions, or significant new UI**, the user is making high-stakes visual decisions based on text descriptions.

The iteration loop exists (design-iteration.md template with KEEP/FIX/ADD) but it's reactive — the user must imagine the design from text, realize they don't like it, articulate what's wrong, and iterate. Visual mockups allow proactive exploration before any specification is written.

---

## Proposed Architecture

### Modified Design-Phase Flow

```
/ms:design-phase {phase}
  │
  ├── Steps 1-3: Validate, check existing, gather context (UNCHANGED)
  │
  ├── Step 4: Adaptive Q&A (MODIFIED — one new question)
  │     │
  │     └── If phase involves significant new UI:
  │         "This phase has significant new UI work. Generate visual
  │          mockups to explore design directions before creating
  │          the design spec?"
  │         ├── Yes → Step 4b (mockup generation)
  │         └── No  → Step 5 (spawn ms-designer directly — today's flow)
  │
  ├── Step 4b: Mockup Generation (NEW)
  │     ├── Determine platform (mobile/web) from context chain
  │     ├── Derive 3 design directions grounded in:
  │     │     - The feature being built
  │     │     - The problem it solves
  │     │     - The target audience
  │     ├── Spawn 3 × ms-mockup-designer agents IN PARALLEL
  │     │     ├── Agent A: "minimal/clean" direction
  │     │     ├── Agent B: "information-dense" direction
  │     │     └── Agent C: "bold/expressive" direction
  │     ├── Each agent writes a self-contained HTML file:
  │     │     .planning/phases/{phase}-{slug}/mockups/variant-a.html
  │     │     .planning/phases/{phase}-{slug}/mockups/variant-b.html
  │     │     .planning/phases/{phase}-{slug}/mockups/variant-c.html
  │     ├── Present to user with AskUserQuestion:
  │     │     "Open these files in your browser and pick a direction:"
  │     │     - Variant A (Minimal/Clean)
  │     │     - Variant B (Information-Dense)
  │     │     - Variant C (Bold/Expressive)
  │     │     — Native free text handles: combine elements, regenerate, refine
  │     ├── If user picks one variant → read that HTML, extract CSS specs
  │     ├── If user describes combination → generate variant D from description
  │     │     + relevant CSS from mentioned variants, then extract
  │     └── Extracted specs become <mockup_direction> context block
  │
  ├── Step 5: Spawn ms-designer (MODIFIED)
  │     ├── Same context as today PLUS:
  │     └── NEW: <mockup_direction> block containing:
  │           - Color palette (extracted hex values from CSS)
  │           - Layout structure (sidebar? tabs? cards? single column?)
  │           - Typography choices (font families, size scale)
  │           - Spacing values (padding, gaps, margins from CSS)
  │           - Component patterns (what HTML structures were used)
  │           - User's stated preferences (from their choice/description)
  │
  ├── Steps 6-8: Handle return, refinement, state update (UNCHANGED)
  │
  └── DESIGN.md is now grounded in user-validated visual choices
```

### Key Design Decisions

**Mockups are brainstorming, not specification.** DESIGN.md remains the authoritative output of design-phase. Mockups help the user explore and choose a visual direction. They are consumed only by the design-phase orchestrator (to extract specs for ms-designer) and are not referenced by plan-phase, execute-phase, or any downstream workflow.

**One agent, platform as parameter.** Mobile and web mockups share ~80% of their knowledge (color theory, typography, spacing, component design, CSS generation). The 20% that differs (device frame vs. full-width container, navigation patterns, touch targets, platform conventions) is handled through a `<platform_conventions>` section in the agent prompt. Two separate agents would duplicate quality-forcing patterns and become a maintenance burden.

**User decides case-by-case.** The mockup step is never automatic. The orchestrator asks whether to generate mockups based on the phase's UI complexity. Phases with minor UI tweaks or backend-only work skip directly to ms-designer. The user always controls whether to invest the extra step.

**Three directions grounded in context.** The directions (minimal/dense/bold) are not arbitrary aesthetic choices — they represent different answers to "how should this feature serve this audience?" A finance dashboard for analysts gets different minimal/dense/bold interpretations than a fitness app for millennials.

**Self-contained HTML files.** Each mockup is a single `.html` file with inline CSS. No external dependencies, no build step, no server. User double-clicks and sees the mockup in their default browser. The CSS is machine-readable — the orchestrator extracts specs by reading the file.

**AskUserQuestion handles combination naturally.** The tool's native free text option ("Other") lets users describe combinations ("colors from A, layout from C") or request regeneration with specific guidance. No special combine workflow needed.

---

## New Artifact: ms-mockup-designer Agent

### Agent Identity

```yaml
# agents/ms-mockup-designer.md
name: ms-mockup-designer
description: Generates self-contained HTML/CSS mockups for design direction exploration
spawned_by: design-phase command
tools: [Read, Write, Bash]
```

### What It Receives

| Context Block | Source | Content |
|---------------|--------|---------|
| `<product_context>` | PROJECT.md | Product type, core value, target audience, constraints |
| `<phase_context>` | ROADMAP.md | Phase goal, success criteria, features to design |
| `<user_vision>` | CONTEXT.md (if exists) | How this should work, what must be nailed, reference products |
| `<existing_aesthetic>` | implement-ui skill or codebase | Established colors, components, spacing — used as CONSTRAINTS on all variants |
| `<design_direction>` | Orchestrator | Which of the three directions this agent generates (minimal/dense/bold) |
| `<platform>` | Inferred from context | mobile or web — determines container, conventions, chrome |
| `<feature_grounding>` | Orchestrator | The feature, the problem it solves, the audience — so directions are contextual |

### What It Produces

A single self-contained `.html` file written to `.planning/phases/{phase}-{slug}/mockups/variant-{x}.html`.

Requirements:
- All CSS inline (no external stylesheets)
- No JavaScript required (static mockup)
- No external fonts or CDN links (use system font stacks or embed via base64 if critical)
- Opens directly in any browser by double-clicking
- For mobile: wrapped in device frame with platform chrome
- For web: responsive layout at primary breakpoint
- Focuses on the **primary screen** — the one that defines the visual direction
- If multiple screens are essential, use a simple tab-like navigation within the HTML

### Platform-Specific Conventions

**Mobile mockups:**
- Device frame: iPhone 15 proportions (393 × 852px) with rounded corners and notch
- Status bar with time/signal/battery indicators
- Bottom navigation bar or tab bar (iOS pattern)
- Safe area insets respected (top: 59px, bottom: 34px)
- Touch targets minimum 44 × 44pt
- System font stack: `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto`
- Single column layout with vertical scroll
- Platform chrome elements (navigation header, back button)

**Web mockups:**
- Full-width layout with max-width container (1280px)
- Sidebar or top navigation (context-dependent)
- Hover state indicators on interactive elements (subtle color shifts)
- Multi-column grid where appropriate
- System font stack: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- Show at a representative breakpoint (typically 1280px or 1440px)

### Quality Expectations

**Design quality bar for mockups is lower than DESIGN.md** — these are brainstorming artifacts, not production specs. However:

- Colors must be harmonious (not random)
- Typography must have clear hierarchy (not uniform sizing)
- Spacing must feel intentional (not arbitrary)
- The mockup must communicate the *direction* clearly enough for the user to compare three options and have a preference
- Each variant must be **meaningfully different** — a user should look at all three and think "these represent genuinely different approaches"

**When existing aesthetic exists (implement-ui skill or codebase patterns):**
- All three variants MUST use the established color palette as a constraint
- Variants differ in layout, density, component emphasis, and visual weight — not in the color system
- This prevents generating a variant the user loves visually but that contradicts the project's established identity

### Direction Derivation

The three directions are not fixed labels. They are derived from context:

**Base directions** (adapted per context):

| Direction | General | Finance App | Fitness App | Dev Tool |
|-----------|---------|-------------|-------------|----------|
| Minimal | Whitespace, typography-driven, fewer elements | Clean tables, key metrics prominent, calm palette | Focused progress view, hero stat, motivational space | Single-pane, monospace, essential info only |
| Dense | Compact, more visible data, functional-first | Dashboard with charts, filters, multi-panel | Stats grid, activity log, detailed breakdowns | Multi-panel, file tree, terminal + editor |
| Bold | Strong colors, prominent CTAs, visual hierarchy | Gradient headers, large metric cards, action-oriented | Vibrant colors, animated feel, gamification hints | Accent-heavy, command palette prominent, dark mode |

The orchestrator derives specific direction descriptions from: what the feature does, what problem it solves, and who it's for. These descriptions are passed to each agent as `<design_direction>`.

---

## New Artifacts: Templates

### mockup-mobile.md

`mindsystem/templates/mockup-mobile.md`

Contains:
- HTML scaffold with device frame CSS (iPhone 15 proportions)
- Status bar template (time, signal, battery — CSS-only)
- Safe area handling
- Bottom navigation bar template
- System font stack declaration
- Viewport meta tag for correct rendering
- Instructions for the agent: "Fill in the content area with your design. Do not modify the device frame."

The agent receives this scaffold so it focuses on *design decisions within the frame* rather than reinventing device chrome each time.

### mockup-web.md

`mindsystem/templates/mockup-web.md`

Contains:
- HTML scaffold with max-width container
- CSS reset (minimal — box-sizing, margins)
- Grid system utilities (simple flexbox/grid helpers)
- System font stack declaration
- Instructions for the agent: "Build your layout using these utilities or write custom CSS."

### design-directions.md

`mindsystem/references/design-directions.md`

Contains:
- How to derive three directions from feature/problem/audience
- Direction examples per product category
- What makes variants "meaningfully different" (not just color swaps)
- Constraints when existing aesthetic exists

---

## Spec Extraction: How CSS Becomes Context

After the user picks a variant, the design-phase orchestrator reads the chosen HTML file and extracts design specs. This is a deterministic operation — CSS values are explicit.

**What gets extracted:**

| Property | CSS Source | Example |
|----------|-----------|---------|
| Primary color | `--color-primary` or most-used accent | `#2563EB` |
| Background color | `body` or main container background | `#0F172A` |
| Text color | `body` color property | `#E2E8F0` |
| Secondary/accent colors | Other CSS custom properties or repeated values | `#10B981`, `#F59E0B` |
| Font family | `body` or heading font-family | `Inter, system-ui` |
| Heading sizes | `h1`, `h2`, `h3` font-size values | `32px`, `24px`, `18px` |
| Body text size | `body` or `p` font-size | `16px` |
| Base spacing | Most common padding/gap value | `16px` |
| Border radius | Most common border-radius | `12px` |
| Layout pattern | Container structure (sidebar, single-column, grid) | "Sidebar + main content" |
| Component patterns | Major structural elements (cards, nav, headers) | "Card-based with top nav" |

**Extraction method:** The orchestrator reads the HTML file content, then assembles a `<mockup_direction>` block for ms-designer:

```xml
<mockup_direction>
The user reviewed three visual mockups and chose Variant B (Information-Dense).

Extracted design specs from chosen mockup:
- Primary color: #2563EB (blue)
- Background: #0F172A (dark navy)
- Text: #E2E8F0 (light gray)
- Accent: #10B981 (green for success indicators)
- Font: Inter, system-ui
- Heading scale: 32/24/18px
- Body text: 16px
- Base spacing unit: 16px (gaps), 24px (section padding)
- Border radius: 12px (cards), 8px (buttons)
- Layout: Sidebar navigation + scrollable main content area
- Key patterns: Metric cards in 3-column grid, data table below, filter bar at top

User's comment: "I like this dense layout but want the sidebar narrower"

Use these as the foundation for DESIGN.md. The user has already validated this
visual direction — preserve these choices. Elaborate and refine, don't replace.
</mockup_direction>
```

This is passed to ms-designer alongside all existing context blocks. ms-designer treats it as high-priority input (similar to how implement-ui skill is authoritative for existing projects).

---

## Modification to design-phase.md Command

### Changes Required

**Step 4 (Adaptive Q&A):** Add one conditional question after gap assessment:

```
If phase involves new screens or significant new UI:
  AskUserQuestion: "This phase involves [N new screens / significant UI work].
    Generate visual mockups to explore design directions first?"
    1. Yes, generate mockups — Explore 3 visual directions before designing
    2. No, go straight to design spec — Use text-based design process (current flow)
```

**New Step 4b (Mockup Generation):** Full mockup generation flow as described above.

**Step 5 (Spawn ms-designer):** Add conditional `<mockup_direction>` block to the assembled prompt when mockups were generated.

**allowed-tools:** No changes needed — design-phase already has `Task` (for spawning agents) and `AskUserQuestion`.

### What Stays The Same

- Steps 1-3 (validation, existing design check, context gathering)
- ms-designer agent itself (receives one additional optional context block)
- DESIGN.md template and all 7 sections
- Design iteration workflow for refinement after DESIGN.md
- Steps 6-8 (handle return, refinement, state update)
- Downstream consumption (research-phase, plan-phase, execute-phase)

---

## Feasibility Concerns and Mitigations

### 1. HTML Design Quality Variance

**Concern:** Claude generates functional HTML/CSS, but the quality of *design decisions* (color harmony, typography pairing, visual rhythm) can be inconsistent across invocations.

**Mitigation:** The agent prompt includes strong design principles (quality-forcing patterns adapted from ms-designer). Templates provide scaffolding so the agent focuses on design decisions, not boilerplate. The three-variant approach means the user has options — if one variant is weak, the other two likely show clearer direction.

### 2. Complex Phases With Many Screens

**Concern:** A phase with 5 screens can't be meaningfully represented in a single HTML file per variant.

**Mitigation:** Mockups focus on the **primary screen** — the one that defines the visual direction. This is typically the most novel or complex screen in the phase. Color palette, typography, spacing, and component style transfer from the primary screen to secondary screens when ms-designer creates the full DESIGN.md. If essential, the mockup can include tab-like navigation between 2-3 screens, but simplicity is preferred.

### 3. Prolonged Design Phase

**Concern:** Adding a step extends the design-phase duration and adds friction.

**Mitigation:**
- **Parallel generation** — three agents run simultaneously, so wall-clock time is ~1 agent's time, not 3x
- **User controls opt-in** — the question is asked, not forced. Minor UI phases skip directly to ms-designer
- **Mockup quality bar is lower** — agents don't run mathematical validation, accessibility audits, or the full 12-step process. They produce a *visual direction*, not a spec
- **Quick decision** — user opens 3 HTML files, picks one, done. The combine/regenerate path only triggers if they explicitly request it via free text

### 4. Existing Aesthetic Constraint

**Concern:** When implement-ui skill or codebase patterns exist, generating "different" variants that must use the same color palette may produce variants that look too similar.

**Mitigation:** When an established aesthetic exists, variants differ in **layout, density, component emphasis, and visual weight** — not color. This is actually the more useful differentiation for established projects, where the visual identity is settled but the *layout approach* for a new feature is not.

### 5. The "Combine" Path Complexity

**Concern:** User saying "colors from A, layout from C" requires generating a new variant.

**Mitigation:** The orchestrator spawns one more ms-mockup-designer with a `<combine>` directive that includes the user's description plus the CSS from the referenced variants. This is a single additional agent call, not a complex workflow. AskUserQuestion's native free text handles the user input naturally.

### 6. File Size and Git

**Concern:** HTML mockup files in git.

**Mitigation:** Self-contained HTML files with inline CSS are typically 5-15KB — smaller than most PLAN.md files. No images, no base64 fonts (system font stacks used), no JavaScript. The `.planning/phases/{phase}/mockups/` directory contains at most 3-4 files per phase. Acceptable for git.

---

## What NOT to Build

**No image generation.** The Gemini/DALL-E path was explored and rejected. AI-generated images can't be parsed back into specs. Claude can't extract colors, spacing, or layout from a PNG. The user becomes the bottleneck translating visual preferences into structured data. HTML/CSS keeps the pipeline machine-readable end-to-end.

**No separate mobile and web agents.** The overlap is ~80% (color theory, typography, spacing, component design, CSS generation). Platform-specific conventions (device frame, navigation patterns, touch targets) are handled through a parameter section in the single agent's prompt.

**No config.json changes.** The mockup step is case-by-case — the user decides during each design-phase invocation via AskUserQuestion. There's no "always generate mockups" toggle because the decision depends on phase complexity, which varies.

**No downstream mockup consumption.** Mockups are consumed only by the design-phase orchestrator to extract specs for ms-designer. Plan-phase, execute-phase, and verify-phase never reference mockup files. DESIGN.md remains the single source of truth for all downstream workflows.

**No interactive mockups.** No JavaScript, no animations, no hover-state simulations. Mockups are static visual representations. The DESIGN.md component specifications section handles interaction states (hover, active, disabled, loading) as structured text — this is more precise than CSS `:hover` rules for specification purposes.

---

## Artifacts Summary

| Artifact | Type | Action | Purpose |
|----------|------|--------|---------|
| `agents/ms-mockup-designer.md` | Agent | **Create** | Generates self-contained HTML/CSS mockups |
| `commands/ms/design-phase.md` | Command | **Modify** | Add mockup generation step (4b) between Q&A and ms-designer |
| `mindsystem/templates/mockup-mobile.md` | Template | **Create** | Device frame HTML scaffold + mobile conventions |
| `mindsystem/templates/mockup-web.md` | Template | **Create** | Full-width HTML scaffold + web conventions |
| `mindsystem/references/design-directions.md` | Reference | **Create** | Direction derivation from feature/problem/audience |
| `agents/ms-designer.md` | Agent | **Minor modify** | Document optional `<mockup_direction>` context block |

### Effort Estimate

- `ms-mockup-designer.md` — Medium (new agent with platform handling, quality patterns, template consumption)
- `design-phase.md` — Small (add conditional step 4b, modify step 5 prompt assembly)
- Templates — Small (HTML scaffolds are mostly boilerplate with clear instructions)
- `design-directions.md` — Small (reference doc with direction derivation logic)
- `ms-designer.md` — Trivial (document one new optional input block)

### Dependencies

No dependencies on other proposals or features. This is a self-contained extension to design-phase.

---

## Open Questions

1. **Primary screen selection.** When a phase has multiple screens, should the orchestrator pick the primary screen for mockups (based on novelty/complexity), or should the user choose which screen to mockup? Orchestrator picking reduces friction; user picking ensures the right screen is explored.

2. **Mockup persistence.** Should mockups be committed to git and persist, or treated as ephemeral artifacts that get cleaned up after DESIGN.md is created? Committing provides history; cleaning up reduces clutter.

3. **Direction customization.** The three base directions (minimal/dense/bold) are adapted per context. Should users be able to override these with custom directions? ("Generate one that feels like Linear, one like Notion, one like Figma") This adds flexibility but also friction in the Q&A step.

4. **Iteration depth.** If the user doesn't like any of the three variants, should the orchestrator offer to generate three more with different directions, or should it fall back to the text-only path? Generating more risks an endless loop; falling back loses the visual exploration benefit.
