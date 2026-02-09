# Design Template

Template for `.planning/phases/XX-name/{phase}-DESIGN.md` - captures visual/UX design specifications for a phase.

**Purpose:** Translate user vision into concrete, implementable design specifications. This is design context, not technical implementation. Technical details come from research and planning.

---

## File Template

```markdown
# Phase [X]: [Name] - Design Specification

**Designed:** [date]
**Platform:** [web / mobile / both]
**Aesthetic source:** [project UI skill / codebase analysis / fresh design]

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

**Dimensions:** [width x height or responsive]
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

**Touch targets:** Minimum 44x44px for interactive elements

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
- Touch targets: 48x48dp minimum
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

---

*Phase: XX-name*
*Design created: [date]*
```

<good_examples>
```markdown
# Phase 3: User Dashboard - Design Specification

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

**Dimensions:** 1440x900 primary, responsive to 1024px
**Edge padding:** 24px
**Component gaps:** 16px
**Sidebar width:** 240px (collapsible to 64px on tablet)

**Components used:**
- Sidebar: NavSidebar, Logo, UserAvatar
- Header: PageHeader, DateRangePicker, ExportButton
- KPIs: MetricCard (x4)
- Charts: AreaChart, FunnelChart, BarChart

**Responsive behavior:**
- Desktop (1024px+): Full sidebar, 4 KPI cards in row, 2-column secondary charts
- Tablet (768-1024px): Collapsed sidebar (icons only), 2 KPI cards per row
- Mobile (<768px): Bottom nav replaces sidebar, stacked layout

---

## Component Specifications

### MetricCard

**Purpose:** Display single KPI with trend indicator

**Visual:**
- Background: `#1a1f2e` (dark navy)
- Border: 1px `#2a3142`, 8px radius
- Shadow: none (flat design)
- Size: min 180px width, 120px height

**States:**
| State | Visual Change | Trigger |
|-------|--------------|---------|
| Default | Base appearance | Initial |
| Hover | Border brightens to `#3a4152` | Mouse over |
| Loading | Content replaced with skeleton | Data fetching |

**Content:**
- Label: 12px, 500 weight, `#8b95a8`
- Value: 32px, 600 weight, `#ffffff`
- Trend: 14px, `#22c55e` (up) or `#ef4444` (down)
- Spacing: 16px padding all sides

---

## Design System Decisions

| Category | Decision | Values | Rationale |
|----------|----------|--------|-----------|
| **Colors** | Primary | `#0a0f1a` | Deep navy instead of pure black - warmer, more sophisticated |
| | Secondary | `#1a1f2e` | Card backgrounds - slight contrast from primary |
| | Text | `#ffffff` | Primary text |
| | Text Secondary | `#8b95a8` | Labels, captions |
| | Accent | `#F59E0B` | Amber - warm, energetic, stands out from cool tones |
| **Typography** | All | Inter | Clean, professional, excellent number rendering |
| | H1 | 32px/600 | Page titles |
| | H2 | 24px/600 | Section headers |
| | Body | 14px/400 | General content |
| | Caption | 12px/500 | Labels, metadata |
| **Spacing** | Base unit | 4px | 4/8/12/16/24/32/48 scale |
| | Edge padding | 24px | Breathing room at edges |
| | Component gap | 16px | Related items |
| | Section gap | 32px | Distinct sections |

---

## Verification Criteria

### Visual Verification
- [ ] Background is deep navy `#0a0f1a`, not generic black
- [ ] Accent color is amber `#F59E0B`, visible in buttons and highlights
- [ ] Cards have consistent 16px internal padding
- [ ] Typography uses Inter font family

### Functional Verification
- [ ] Dashboard: All 4 KPI cards display with correct values
- [ ] Dashboard: Main chart shows trend data with interactive tooltips
- [ ] Dashboard: Date picker filters all displayed data

### Platform Verification
- [ ] Responsive: Sidebar collapses to icons at 1024px
- [ ] Responsive: Layout stacks vertically below 768px
- [ ] Touch: All interactive elements meet 44px minimum

---

*Phase: 03-user-dashboard*
*Design created: 2026-01-19*
```
</good_examples>

<guidelines>
**This template captures DESIGN, not technical implementation.**

The design phase produces:
- How it should look (visual identity, layouts)
- How it should behave (states, transitions)
- How it should feel (UX flows, interactions)
- What proves it's correct (verification criteria)

The design phase does NOT produce:
- Library choices (that's research)
- Task breakdown (that's planning)
- Code architecture (that's execution)

**Content should read like:**
- A design specification a developer can implement
- "The card has 16px padding, 8px border radius, and a subtle shadow"
- "On hover, the border brightens from #2a3142 to #3a4152"
- ASCII wireframes showing exact layout structure

**Content should NOT read like:**
- A technical architecture document
- A list of npm packages to install
- Code snippets or implementation details
- Vague descriptions ("make it look nice")

**Quality markers:**
- Specific color values (hex codes), not "blue" or "primary"
- Exact spacing values (16px), not "some padding"
- All component states defined (default, hover, active, disabled)
- ASCII wireframes with labeled regions
- Verification criteria that are observable and testable

**After creation:**
- File lives in phase directory: `.planning/phases/XX-name/{phase}-DESIGN.md`
- Research phase adds technical details (which libraries enable this design)
- Planning phase creates tasks that reference design specs
- Execute phase implements to match design exactly
</guidelines>
