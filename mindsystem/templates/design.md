# Design Template

Template for `.planning/phases/XX-name/{phase}-DESIGN.md` - captures visual/UX design specifications for a phase.

**Purpose:** Translate user vision into concrete, implementable design specifications. All values appear exactly once, inline where consumed.

---

## File Template

```markdown
# Phase [X]: [Name] - Design Specification

**Designed:** [date]
**Platform:** [web / mobile / both]
**Aesthetic source:** [project UI skill / codebase analysis / fresh design]

## Design Direction

[1-2 sentences: feel, inspiration, what sets this apart. Not generic — specific enough to guide decisions.]

## Design Tokens

| Token | Value | Note |
|-------|-------|------|
| bg-primary | `#[hex]` | [brief context] |
| bg-surface | `#[hex]` | [brief context] |
| text-primary | `#[hex]` | |
| text-secondary | `#[hex]` | |
| accent | `#[hex]` | [brief context] |
| error | `#[hex]` | |
| success | `#[hex]` | |
| font-heading | [family] | |
| font-body | [family] | |
| h1 | [size/weight] | |
| h2 | [size/weight] | |
| body | [size/weight] | |
| caption | [size/weight] | |
| spacing-base | [value]px | [scale: 4/8/12/16/24/32] |
| radius | [value]px | |
| shadow-1 | [values] | [subtle depth] |
| shadow-2 | [values] | [prominent depth] |

## Screens

### [Screen Name]

` ` `
+--------------------------------------------------+
|  ← bg-primary                                    |
|  [Header]  h1 "Title"                            |
|            text-secondary caption                 |
+--------------------------------------------------+
|                         ↕ 24px                    |
|  +---------------------+  +-------------------+  |
|  | Card  ← bg-surface  |  | Card              |  |
|  | ↔ 16px padding      |  |                   |  |
|  | body text-primary    |  | body              |  |
|  | radius: 8px          |  | radius: 8px       |  |
|  +---------------------+  +-------------------+  |
|         ↕ 16px gap                                |
+--------------------------------------------------+
` ` `

**States**

| Element | State | Change | Trigger |
|---------|-------|--------|---------|
| Card | hover | border → accent | mouse over |
| Card | loading | skeleton pulse | data fetch |
| Button | disabled | opacity 0.5 | form invalid |

**Behavior**
- [Non-obvious interaction only — skip obvious actions like "tap button submits form"]
- [Animations, transitions, or conditional logic worth noting]

**Hints**
- [Framework-specific reuse: "Extend existing CardWidget", "Use Tailwind group-hover"]
- [Gotchas: "Safe area inset on iOS", "Focus trap in modal"]
- [Responsive: "Stack cards vertically below 768px"]

### [Screen 2 Name]

[Repeat: wireframe + states + behavior + hints per screen]

---

Validation: passed

*Phase: XX-name*
*Design created: [date]*
```

<good_examples>
```markdown
# Phase 3: User Dashboard - Design Specification

**Designed:** 2026-01-19
**Platform:** Web (React + Tailwind)
**Aesthetic source:** Codebase analysis + fresh design

## Design Direction

Professional analytics dashboard with approachable data visualization. Dark mode primary — deep navy instead of generic black, amber accent for energy. Inspired by Linear's information hierarchy and Stripe's professional polish.

## Design Tokens

| Token | Value | Note |
|-------|-------|------|
| bg-primary | `#0a0f1a` | Deep navy, not generic black |
| bg-surface | `#1a1f2e` | Card backgrounds |
| text-primary | `#ffffff` | |
| text-secondary | `#8b95a8` | Labels, captions |
| accent | `#F59E0B` | Amber — warm, stands out from cool tones |
| error | `#ef4444` | |
| success | `#22c55e` | |
| font-all | Inter | Clean, excellent number rendering |
| h1 | 32px/600 | Page titles |
| h2 | 24px/600 | Section headers |
| body | 14px/400 | General content |
| caption | 12px/500 | Labels, metadata |
| spacing-base | 4px | Scale: 4/8/12/16/24/32 |
| edge-padding | 24px | Breathing room at edges |
| component-gap | 16px | Related items |
| section-gap | 32px | Distinct sections |
| radius | 8px | |

## Screens

### Dashboard Overview

```
+------------------------------------------------------------------+
|  [Sidebar 240px]  |  ← bg-primary                                |
|  ← bg-surface     |  [Header] h1 "Dashboard"  [DatePicker] [Export]
|                    |                                              |
|  Logo              |  ↕ 24px edge-padding                        |
|  ─────────         |                                              |
|  Dashboard  ←active|  [KPI] [KPI] [KPI] [KPI]  ← 16px gap       |
|  Campaigns         |  ↕ 16px                    min-w:180 h:120  |
|  Reports           |                                              |
|  Settings          |  +--------------------------------------------+
|                    |  | Main Chart ← bg-surface  radius:8px      |
|  ─────────         |  | h2 "Trend"   ↔ 16px padding              |
|  [Avatar]          |  | AreaChart                                 |
|                    |  +--------------------------------------------+
|                    |  ↕ 16px                                      |
|                    |  +-------------------+  +-------------------+|
|                    |  | FunnelChart       |  | BarChart          ||
|                    |  | ← bg-surface      |  | ← bg-surface     ||
|                    |  +-------------------+  +-------------------+|
+------------------------------------------------------------------+
```

**States**

| Element | State | Change | Trigger |
|---------|-------|--------|---------|
| KPI Card | hover | border brightens `#2a3142` → `#3a4152` | mouse over |
| KPI Card | loading | content → skeleton pulse | data fetch |
| Nav item | active | text-primary + left accent bar | current route |
| Sidebar | collapsed | 240px → 64px (icons only) | tablet ≤1024px |

**Behavior**
- Date picker filters all displayed data (KPIs + charts) simultaneously
- Chart tooltips appear on hover with exact values and % change
- Bottom nav replaces sidebar below 768px

**Hints**
- Sidebar collapse: CSS transition 200ms, persist preference in localStorage
- KPI cards: Use CSS Grid `repeat(auto-fit, minmax(180px, 1fr))` for responsive wrapping
- Charts: Lazy-load chart library, show skeleton during load
- Touch targets: All nav items and buttons ≥ 44px

---

Validation: passed

*Phase: 03-user-dashboard*
*Design created: 2026-01-19*
```
</good_examples>

<annotation_conventions>
**Arrows and inline refs in wireframes:**
- `←` points to a property of the region (e.g., `← bg-surface` means this area uses bg-surface token)
- `↕` vertical spacing between elements (e.g., `↕ 16px`)
- `↔` horizontal padding/spacing (e.g., `↔ 16px padding`)
- Token names reference the Design Tokens table (e.g., `bg-primary`, `accent`, `h1`)
- Dimensions inline where relevant (e.g., `min-w:180 h:120`, `240px`)
- Component names in `[brackets]`
</annotation_conventions>

<guidelines>
**This template captures DESIGN, not technical implementation.**

The design phase produces:
- How it should look (wireframe layouts with inline specs)
- How it should behave (states, non-obvious interactions)
- How it should feel (design direction)
- Implementation hints (framework-specific reuse, gotchas)

The design phase does NOT produce:
- Library choices (that's research)
- Task breakdown (that's planning)
- Code architecture (that's execution)
- Verification criteria (plan writer derives from specs)

**Content should read like:**
- A design specification a developer can implement
- ASCII wireframes with inline token refs, spacing, and dimensions
- States tables with concrete triggers and changes
- Behavior notes for non-obvious interactions only

**Content should NOT read like:**
- A technical architecture document
- A list of npm packages to install
- Code snippets or implementation details
- Vague descriptions ("make it look nice")
- Narration of obvious interactions ("user taps button, form submits")

**Quality markers:**
- Specific values in tokens (hex, px, font/weight), not "blue" or "primary"
- All values appear exactly once — in tokens table or inline wireframe annotation
- All component states defined (default, hover, active, disabled, loading)
- ASCII wireframes with inline annotations (token refs, spacing, dimensions)
- Non-obvious behaviors documented, obvious ones omitted

**After creation:**
- File lives in phase directory: `.planning/phases/XX-name/{phase}-DESIGN.md`
- Research phase adds technical details (which libraries enable this design)
- Planning phase creates tasks that reference design specs
- Plan writer derives verification criteria from specs
- Execute phase implements to match design exactly
</guidelines>
