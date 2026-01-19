# AI-Driven UI Design System: Principles and Patterns for High-Fidelity Design Generation

This guide documents how to use AI agents to generate professional-grade UI mockups and visual design systems. The patterns here are derived from the Plugin Freedom System—a production-tested approach for creating audio plugin interfaces through AI-driven design workflows.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [System Architecture](#system-architecture)
3. [Quality-Forcing Patterns](#quality-forcing-patterns)
4. [Prompt Construction](#prompt-construction)
5. [Visual Systems as Reusable Templates](#visual-systems-as-reusable-templates)
6. [Requirement Flow: From Vision to Specification](#requirement-flow-from-vision-to-specification)
7. [Validation and Quality Gates](#validation-and-quality-gates)
8. [Design Principles for Prompts](#design-principles-for-prompts)
9. [The 8-Section Aesthetic Template](#the-8-section-aesthetic-template)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
11. [Summary](#summary)
12. [Appendix A: Complete Example](#appendix-a-complete-example)
13. [Appendix B: Copy-Paste Templates](#appendix-b-copy-paste-templates)

---

## Core Philosophy

### The Fundamental Insight

AI-generated designs suffer from a predictable failure mode: **generic defaults**. Without explicit quality constraints, AI produces:
- Generic dark backgrounds
- Blue accent colors (the "safe" default)
- Arbitrary spacing with no intentional rhythm
- Controls that look like styled HTML inputs, not professional interfaces

The solution is **quality-forcing patterns**—explicit language in prompts that:
1. Sets a concrete commercial benchmark
2. Pre-empts criticism before it happens
3. Forces self-review before output
4. Provides specific anti-patterns to avoid

### The Commercial Benchmark Principle

The most effective quality trigger is anchoring to real-world commercial standards:

> **"The design must look like a $50-200 commercial product."**

This single sentence activates several quality behaviors:
- Intentional decisions replace defaults
- Professional polish becomes expected
- User trust becomes a design requirement
- "Good enough" is explicitly rejected

---

## System Architecture

### Three-Tier Orchestration Model

Effective AI-driven design uses separation of concerns:

```
┌─────────────────────────────────────────────────┐
│         ORCHESTRATOR (Skill/Workflow)           │
│  - Gathers requirements through adaptive Q&A    │
│  - Manages state across iterations              │
│  - Routes to specialized agents                 │
│  - Presents decision menus to user              │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│          DESIGN AGENT (Subagent)                │
│  - Fresh context per invocation                 │
│  - Pure design generation                       │
│  - No user interaction                          │
│  - Returns structured specification             │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│       IMPLEMENTATION AGENT (Subagent)           │
│  - Converts specifications to code              │
│  - Generates production assets                  │
│  - Creates integration documentation            │
└─────────────────────────────────────────────────┘
```

### Why Fresh Context Per Iteration?

Each design iteration runs in a **fresh agent context**:
- Prevents context bloat from accumulated changes
- Enables clean A/B comparison between versions
- Allows version history without state pollution
- Each version is complete and self-contained

### State Management

The orchestrator maintains persistent state:
```yaml
current_version: 3
design_finalized: false
requirements_complete: true
aesthetic_selected: "vintage-hardware-001"
user_feedback_history:
  - v1: "Too generic, needs more character"
  - v2: "Colors better, spacing feels cramped"
```

---

## Quality-Forcing Patterns

### Pattern 1: The Commercial Benchmark

**Implementation:**
```
Quality expectation: "Design must look like commercial $50-200 [product type]
- intentional decisions, not defaults"
```

**Why it works:** Anchors quality to real market standards, not abstract "good design."

### Pattern 2: Pre-emptive Criticism

**Implementation:**
```
Pre-emptive criticism: Assume the user will say "This looks like generic AI output."
Generate something that proves them wrong.
```

**Why it works:** Forces the AI to anticipate criticism and actively counteract it.

### Pattern 3: Accountability Check

**Implementation:**
```
Accountability check: Could you show this design to prove you're a skilled
[domain] designer? If not, it's not done.
```

**Why it works:** Creates psychological ownership of quality outcomes.

### Pattern 4: Mandatory Self-Review

**Implementation:**
```
REQUIRED: After generating output, review your own work for quality before returning.

Check:
- Does the color palette have character or is it generic?
- Does spacing feel intentional or arbitrary?
- Do controls look refined or like default inputs?

If any answer is "generic/arbitrary/default," refine before returning.
This is not optional. The first pass is never the best.
```

**Why it works:** Forces iteration before output, catching obvious quality issues.

### Pattern 5: Explicit Anti-Pattern Lists

**Implementation:**
```
Quality failures (these indicate the design is NOT done):
❌ Generic dark gray with blue accents (unless specifically requested)
❌ Default spacing with no intentional rhythm
❌ Controls that look like styled HTML inputs
❌ Typography using only system fonts without spacing compensation
❌ Elements that appear positioned without thought
```

**Why it works:** Gives specific examples of what NOT to do, making failures recognizable.

---

## Prompt Construction

### The Complete Invocation Template

When invoking a design agent, structure the prompt with these components:

```xml
<context>
  Product: [Name]
  Type: [Mobile App / Desktop App / Web App / Plugin]
  Version: [N] (for iteration tracking)

  Domain context:
  [Brief description of the product and its users]

  Existing constraints:
  [Technical platform, brand guidelines, accessibility requirements]
</context>

<requirements>
  Layout preference: [Grid / Stacked / Sidebar / Tab-based / Custom]

  Components:
  - [Component 1]: [type, purpose, priority]
  - [Component 2]: [type, purpose, priority]
  - [Component N]: [type, purpose, priority]

  Visual style: [Modern / Vintage / Minimal / Skeuomorphic / Custom description]

  Color direction: [Warm / Cool / Monochromatic / Vibrant / Specific palette]

  Dimensions: [Width × Height] or [Responsive breakpoints]
</requirements>

<quality_expectation>
  Design must look like commercial $50-200 [product type] - intentional decisions, not defaults.

  Pre-emptive criticism: Assume the user will say "This looks like generic AI output."
  Generate something that proves them wrong.
</quality_expectation>

<additional_context>
  [Creative brief, brand values, user research, competitive analysis]

  [Aesthetic template content, if using predefined visual system]

  [User feedback from previous iteration, if v2+]
</additional_context>

<output_specification>
  Generate:
  1. [Specification format - YAML, JSON, Figma-compatible, etc.]
  2. [Preview format - HTML, image, wireframe, etc.]

  File locations:
  - Specification: ./designs/v[N]-spec.[format]
  - Preview: ./designs/v[N]-preview.[format]
</output_specification>

<validation_requirements>
  Before returning, verify:
  - [ ] All components fit within specified dimensions
  - [ ] Minimum spacing requirements met (15px edges, 10px between elements)
  - [ ] Color contrast meets accessibility standards
  - [ ] Typography hierarchy is clear
  - [ ] Interactive elements are appropriately sized for the platform
</validation_requirements>
```

### Prompt Component Breakdown

| Component | Purpose | When to Include |
|-----------|---------|-----------------|
| Context | Grounds the AI in the product domain | Always |
| Requirements | Specifies what to design | Always |
| Quality Expectation | Forces professional standards | Always |
| Additional Context | Provides design direction | When available |
| Output Specification | Ensures consistent deliverables | Always |
| Validation Requirements | Prevents obvious errors | Always |

---

## Visual Systems as Reusable Templates

### The Aesthetic Template Concept

Rather than defining designs with rigid pixel specifications, capture visual systems as **interpretable prose**:

**Why Prose Over Specs?**
- **Flexibility:** Same aesthetic works for 3-component or 30-component screens
- **Human-readable:** Designers can understand and approve the system
- **Machine-parseable:** AI extracts values and principles programmatically
- **Conceptual:** Captures "vibe" and intent, not just measurements

### Aesthetic Capture Process

1. **Design a reference implementation** (one complete screen/mockup)
2. **Extract patterns** (colors, typography, spacing, controls, textures)
3. **Document as prose** in structured sections
4. **Store for reuse** across projects

### Application Process

1. **Load aesthetic** from template library
2. **Analyze target** (component count, types, purpose)
3. **Select layout** appropriate for complexity
4. **Apply visual system** to chosen layout
5. **Generate specification** with aesthetic applied

---

## Requirement Flow: From Vision to Specification

### Tier-Based Gap Analysis

Organize requirements into priority tiers:

**Tier 1 (Critical):**
- Overall vibe/mood
- Layout approach
- Color philosophy
- Primary interaction patterns

**Tier 2 (Visual Core):**
- Specific color palette
- Typography choices
- Spacing density
- Component styling

**Tier 3 (Context):**
- Best suited use cases
- Special features
- Inspirations and references
- Technical constraints

### Adaptive Questioning Algorithm

```
1. Parse what user already provided
2. Check coverage against tier priority (1 → 2 → 3)
3. Identify top N gaps (typically 4)
4. Generate targeted questions
5. NEVER ask about concepts already stated
6. Merge answers into cumulative context
7. Present decision gate: "Finalize / Continue / Add context"
8. Loop or proceed based on user choice
```

### Decision Gate Pattern

After each questioning round, present:
```
I have enough context to generate your design. Ready to proceed?

1. Proceed - Generate design with current context
2. Ask more questions - I have more details to clarify
3. Add context - I want to provide additional information
```

This prevents both over-questioning and premature generation.

---

## Validation and Quality Gates

### Mathematical Validation

Before generating visual output, validate specifications:

**Bounds Containment:**
```
x + width <= container_width
y + height <= container_height
```

**Overlap Detection:**
```
For each pair of elements A and B:
  NOT (A.right < B.left OR A.left > B.right OR
       A.bottom < B.top OR A.top > B.bottom)
```

**Minimum Sizes (Platform-Dependent):**
- Touch targets: 44×44pt minimum (iOS), 48×48dp (Android)
- Desktop controls: 24×24px minimum
- Text inputs: 32px minimum height

**Spacing Rules:**
- Edge padding: 15-20px minimum
- Component spacing: 8-16px minimum
- Group spacing: 24-32px for visual separation

### Platform-Specific Validation

**For Web/WebView:**
- No viewport units (`100vh`, `100vw`) that fail on initial render
- Required `html, body { height: 100%; }` for percentage-based layouts
- Native feel: `user-select: none`, `overflow: hidden`, disable context menu

**For Mobile:**
- Safe area insets respected
- Touch targets meet minimum size
- Text sizes meet accessibility minimums (16px body text)

**For Desktop:**
- Window chrome accommodated
- Resizable constraints defined
- High-DPI assets specified

### Quality Gate Sequence

```
Step 1: Specification Validation
├─ Pass → Continue to Step 2
└─ Fail → Return error, DO NOT generate visuals

Step 2: Generate Visual Output

Step 3: Self-Review (Mandatory)
├─ "Is the color palette distinctive?" → If no, refine
├─ "Does spacing feel intentional?" → If no, refine
├─ "Do components look refined?" → If no, refine
└─ All yes → Return success

Step 4: Technical Validation
├─ Platform constraints met → Return output
└─ Constraints violated → Return error with specifics
```

---

## Design Principles for Prompts

### Contrast and Hierarchy

**Embed in prompts:**
```
Visual hierarchy requirements:
- Primary actions: Highest contrast, largest touch targets
- Secondary actions: Medium contrast, standard sizing
- Tertiary/informational: Lower contrast, smaller sizing

Color contrast: WCAG AA minimum (4.5:1 for normal text, 3:1 for large text)
```

### Spacing Philosophy

**Embed in prompts:**
```
Spacing should communicate relationships:
- Tight spacing (4-8px): Strongly related elements (label to input)
- Medium spacing (12-16px): Elements in same group
- Wide spacing (24-32px): Different groups or sections

Every spacing value should appear intentional. Random variation reads as careless.
```

### Typography Hierarchy

**Embed in prompts:**
```
Typography establishes information hierarchy:
- H1: [Size] - Page/screen titles only
- H2: [Size] - Section headers
- Body: [Size] - Primary content
- Caption: [Size] - Supporting information

Font weight variations:
- Bold: Headlines, labels, emphasis
- Medium: Subheads, important body text
- Regular: Body text, descriptions
```

### Control Styling Philosophy

**Embed in prompts:**
```
Controls should feel crafted, not generated:
- Buttons: Clear affordance, consistent states (default, hover, active, disabled)
- Inputs: Visible boundaries, clear focus states
- Sliders/Knobs: Physical metaphor if skeuomorphic, clean geometry if flat
- Toggles: Clear on/off states, smooth transitions

Every control should look like someone spent hours perfecting it.
```

---

## The 8-Section Aesthetic Template

When capturing visual systems as reusable templates, include these sections:

### 1. Visual Identity
2-3 sentences describing the core design philosophy and feelings evoked.
```
Example: "Professional 19-inch rack unit with industrial precision.
Dark metal surfaces, LED metering, and yellow-gold accents create
the feel of high-end studio hardware. Functional first,
aesthetic second—every element serves a purpose."
```

### 2. Color System
Background, accent, text, and control colors with philosophy.
```
Example:
- Background: Pure dark rack metal (#1a1a1a)
- Accent: Bright yellow-gold (#ffc864) for labels and indicators
- Text: High-contrast white (#ffffff) for readability
- LEDs: Traffic light system (green, yellow, red)
- Philosophy: High contrast for readability in any environment
```

### 3. Typography
Font families, sizes, weights, spacing, and philosophy.
```
Example:
- Primary: Monospace for technical precision
- Headers: Bold, wide letter-spacing (0.1em)
- Labels: Uppercase, 10-12px, gold color
- Values: Regular weight, 14-16px, white
- Philosophy: Industrial precision, not decorative
```

### 4. Controls
Detailed styling for interactive elements.
```
Example:
- Knobs: Conic gradient simulating machined metal, gold pointer indicator
- Sliders: Vertical faders with LED fill, color changes at threshold
- Buttons: Recessed metal with power LED indicator
- Metering: Segmented LED bars with traffic light coloring
```

### 5. Spacing & Layout Philosophy
Density, control spacing, padding, layout flexibility.
```
Example:
- Density: Tight rack-style (8-12px gaps)
- Sections: Grouped by function, subtle separators
- Edge padding: 15px minimum, more on larger displays
- Grid: 8px base unit for all measurements
```

### 6. Surface & Details
Textures, depth, dimensionality, shadows, borders, decorative elements.
```
Example:
- Texture: Brushed metal via repeating linear gradient
- Depth: Deep inset shadows for professional feel
- Borders: 1px dark borders for element definition
- Embellishments: Mounting holes, ventilation slots, panel screws
- Hover states: None (hardware doesn't hover)
```

### 7. Technical Implementation
CSS patterns, layout techniques, performance notes, interaction feel.
```
Example:
- Use CSS custom properties for all colors
- Gradients for metal textures (performant)
- Avoid box-shadow stacking (performance)
- Use CSS Grid for control layout
- Immediate response (no transition delays)
- Knob drag: Linear, precise feel
```

### 8. Usage Guidelines
Product types, design contexts, parameter count adaptation, customization.
```
Example:
- Best for: Mixing/mastering tools, technical processors, professional utilities
- NOT suited for: Creative effects, experimental designs, playful contexts
- 1-4 params: Single horizontal row
- 5-8 params: 2×4 or 3×3 grid
- 9+ params: Grouped sections with dividers
- Scale window, not control density
```

---

## Anti-Patterns to Avoid

### In Prompts

❌ **Vague quality requests:**
```
"Make it look good"
"Professional design"
"Beautiful interface"
```

✅ **Specific quality anchors:**
```
"Design must look like commercial $50-200 product"
"Would a professional designer claim this as their work?"
```

❌ **Open-ended scope:**
```
"Design a dashboard"
"Create an app interface"
```

✅ **Constrained scope:**
```
"Design a dashboard with: user stats widget, activity feed, quick actions panel"
"Create login screen with: email input, password input, submit button, forgot password link"
```

❌ **Missing validation criteria:**
```
"Generate the design"
```

✅ **Explicit validation:**
```
"Before returning, verify: all elements fit, spacing is consistent, contrast meets AA"
```

### In Generated Designs

| Anti-Pattern | Why It's Bad | What to Do Instead |
|--------------|--------------|---------------------|
| Generic dark gray | Reads as "default dark mode" | Choose distinctive dark (warm brown, deep blue) |
| Blue accent on everything | Overused, reads as generic | Match accent to product personality |
| Same-sized controls | Creates visual monotony | Vary sizes by importance |
| Arbitrary spacing | Looks unintentional | Use consistent spacing scale (4/8/12/16/24/32) |
| System fonts only | Reads as prototype | Either use distinctive fonts OR careful spacing |
| Centered everything | Lazy layout solution | Use intentional alignment (left, grid, asymmetric) |

---

## Summary

### Core Components

1. **Quality-Forcing Language**
   - Commercial benchmark anchoring
   - Pre-emptive criticism pattern
   - Accountability checks
   - Mandatory self-review

2. **Structured Requirements**
   - Tier-based gap analysis
   - Adaptive questioning
   - Decision gates

3. **Validation Gates**
   - Mathematical constraints
   - Platform requirements
   - Quality self-review

4. **Reusable Visual Systems**
   - Prose-based aesthetic templates
   - 8-section capture format
   - Flexible application to different layouts

5. **Iteration Management**
   - Fresh context per version
   - Complete version history
   - User feedback integration

### Implementation Checklist

- [ ] Define commercial quality benchmark for your domain
- [ ] Create prompt template with quality-forcing patterns
- [ ] Implement validation rules for your platform
- [ ] Design aesthetic template format for reuse
- [ ] Build orchestration layer for requirement gathering
- [ ] Test with diverse complexity levels (simple → complex)
- [ ] Refine based on quality failures observed

---

## Appendix A: Complete Example

### Desktop SaaS Dashboard

```xml
<context>
  Product: MetricFlow
  Type: Web Application (Desktop-first SaaS)
  Version: 1

  Domain context:
  MetricFlow is a B2B analytics platform for marketing teams. Users track
  campaign performance, visualize conversion funnels, and generate reports
  for stakeholders. The app handles complex data but should feel approachable.

  Existing constraints:
  - Desktop-first (1440px primary, responsive down to 1024px)
  - Dark mode primary (analysts work long hours)
  - Must support data-dense views without overwhelming
  - Accessibility: WCAG AA compliance required
</context>

<requirements>
  Screen: Campaign Analytics Dashboard

  Layout preference: Sidebar navigation + main content area with card grid

  Components:
  - Sidebar: Logo, nav items (Dashboard, Campaigns, Reports, Settings), user avatar (always visible)
  - Header bar: Page title, date range picker, export button, notifications (high priority)
  - KPI cards row: 4 metrics with sparklines (Impressions, Clicks, Conversions, Revenue) (high)
  - Main chart: Line/area chart showing trend over selected period (high)
  - Secondary grid: 2×2 grid of smaller visualizations (funnel, top campaigns table, geo map, device breakdown) (medium)
  - Quick actions: Floating action menu (create report, share, schedule) (low)

  Visual style: Modern professional with subtle depth - Linear/Stripe aesthetic

  Color direction:
  - Dark mode: Deep navy background (#0a0f1a), not pure black
  - Accent: Vibrant but not garish (electric blue or teal)
  - Data visualization: Consistent, accessible color scale for charts
  - Success/warning/error states clearly distinguished

  Dimensions: 1440×900 (primary), responsive to 1024px minimum
</requirements>

<quality_expectation>
  Design must look like a well-funded SaaS product with Series A+ design budget
  - the kind of dashboard featured in design showcases on Dribbble or Mobbin.

  Pre-emptive criticism: Assume a VP of Marketing will compare this to
  Amplitude, Mixpanel, or HubSpot. It should feel like it belongs in that tier.

  Accountability check: Could you present this to a SaaS design lead at
  Stripe or Linear and have them nod approvingly? If not, it's not done.
</quality_expectation>

<additional_context>
  Brand values: Trustworthy, powerful, approachable, data-driven

  Competitive reference:
  - Linear (clean dark mode, excellent information hierarchy)
  - Stripe Dashboard (professional density without clutter)
  - Amplitude (data visualization excellence)
  - Notion (approachable despite complexity)

  User research insight: "I need to prep for my Monday stakeholder meeting
  in 5 minutes. Show me what matters without making me dig."

  Technical notes:
  - Charts will use a visualization library (D3/Recharts)
  - Real-time data updates expected
  - Export functionality is critical (PDF, CSV, scheduled emails)
</additional_context>

<output_specification>
  Generate:
  1. Design specification (YAML format with component hierarchy)
  2. Preview mockup (HTML with realistic sample data)

  File locations:
  - Specification: ./designs/v1-analytics-dashboard-spec.yaml
  - Preview: ./designs/v1-analytics-dashboard-preview.html
</output_specification>

<validation_requirements>
  Before returning, verify:
  - [ ] Sidebar is fixed, content scrolls independently
  - [ ] All interactive elements minimum 32×32px (desktop standard)
  - [ ] Text sizes: body 14px+, labels 12px+ (never smaller)
  - [ ] Contrast meets WCAG AA on dark background
  - [ ] KPI cards scannable in <2 seconds
  - [ ] Chart has clear legend, axis labels, hover states defined
  - [ ] Responsive behavior defined for 1024px breakpoint
  - [ ] Loading/skeleton states considered

  Self-review checklist:
  - [ ] Does this look like a shipping SaaS product, not a template?
  - [ ] Is the dark mode sophisticated (deep navy) not lazy (pure black)?
  - [ ] Does the information hierarchy guide the eye correctly?
  - [ ] Are data visualizations professional, not default chart library output?
  - [ ] Would a marketing VP trust this with their data?
  - [ ] Does density feel intentional (enough info) not cluttered (too much)?
</validation_requirements>
```

---

## Appendix B: Copy-Paste Templates

### Template 1: Universal Design Prompt

Copy and fill in all `[BRACKETED]` sections:

```xml
<context>
  Product: [Product name]
  Type: [Mobile App / Desktop App / Web App / Plugin / Other]
  Version: [N - start with 1]

  Domain context:
  [2-3 sentences: What is this product? Who uses it? What problem does it solve?]

  Existing constraints:
  [List: Platform requirements, brand guidelines, accessibility needs, technical limits]
</context>

<requirements>
  Screen/View: [What specific screen are you designing?]

  Layout preference: [Grid / Card-based / Sidebar / Stacked / Tab-based / Custom]

  Components:
  - [Component 1]: [type] - [purpose] - [priority: high/medium/low]
  - [Component 2]: [type] - [purpose] - [priority]
  - [Component 3]: [type] - [purpose] - [priority]
  - [Add more as needed]

  Visual style: [Modern / Vintage / Minimal / Skeuomorphic / Custom description]

  Color direction: [Warm / Cool / Monochromatic / Vibrant / Dark mode / Light mode]
  [Optional: specific colors or palette reference]

  Dimensions: [Width × Height] or [Responsive breakpoints]
</requirements>

<quality_expectation>
  Design must look like [QUALITY BENCHMARK - see table below] - intentional
  decisions, not defaults.

  Pre-emptive criticism: Assume the user will say "This looks like generic
  AI output." Generate something that proves them wrong.

  Accountability check: Could you show this to [AUTHORITY FIGURE] and claim
  it as professional work? If not, it's not done.
</quality_expectation>

<additional_context>
  Brand values: [3-5 adjectives describing the brand personality]

  Competitive reference:
  - [Competitor 1]: [what to borrow from them]
  - [Competitor 2]: [what to borrow from them]
  - [Competitor 3]: [what to borrow from them]

  User insight: [1 sentence quote or insight from user research]

  Technical notes: [Any implementation constraints or considerations]
</additional_context>

<output_specification>
  Generate:
  1. Design specification ([YAML / JSON / other format])
  2. Preview mockup ([HTML / image / wireframe])

  File locations:
  - Specification: ./designs/v[N]-[screen-name]-spec.[format]
  - Preview: ./designs/v[N]-[screen-name]-preview.[format]
</output_specification>

<validation_requirements>
  Before returning, verify:
  - [ ] All elements fit within specified dimensions
  - [ ] Minimum spacing: [15-20]px edges, [8-16]px between elements
  - [ ] Interactive elements meet platform minimums ([44pt iOS / 48dp Android / 32px desktop])
  - [ ] Color contrast meets WCAG AA (4.5:1 body text, 3:1 large text)
  - [ ] Typography hierarchy is clear (H1 > H2 > Body > Caption)
  - [ ] [Add domain-specific checks]

  Self-review checklist (REQUIRED):
  - [ ] Does the color palette have character or is it generic?
  - [ ] Does spacing feel intentional or arbitrary?
  - [ ] Do controls look refined or like default inputs?
  - [ ] Would a professional designer claim this as their work?

  If any answer is "generic/arbitrary/default/no," refine before returning.
</validation_requirements>
```

**Quality Benchmark Reference:**

| Domain | Fill in [QUALITY BENCHMARK] with: |
|--------|----------------------------------|
| Mobile App | "a top 100 App Store app in this category" |
| Desktop App | "commercial $200+ professional software" |
| Web SaaS | "a well-funded SaaS product with Series A+ design" |
| Audio Plugin | "a commercial $50-200 audio plugin" |
| Creative Tool | "Adobe/Figma-quality professional creative software" |
| E-commerce | "a top Shopify Plus store or Amazon-tier experience" |
| Fintech | "a Stripe/Plaid-tier financial product" |

---

### Template 2: Iteration Feedback Prompt

Use this when refining a design (v2, v3, etc.):

```xml
<context>
  Product: [Same as v1]
  Version: [N] (incrementing from previous)
  Previous version: v[N-1]
</context>

<feedback_on_previous>
  What worked well:
  - [Keep this aspect]
  - [Keep this aspect]

  What needs improvement:
  - [Specific issue 1]: [What's wrong and how to fix]
  - [Specific issue 2]: [What's wrong and how to fix]
  - [Specific issue 3]: [What's wrong and how to fix]

  New requirements (if any):
  - [New component or feature to add]
</feedback_on_previous>

<quality_expectation>
  [Same commercial benchmark as v1]

  Specific focus for this iteration:
  [The main thing that must improve in this version]
</quality_expectation>

<output_specification>
  Generate v[N] files:
  - Specification: ./designs/v[N]-[screen-name]-spec.[format]
  - Preview: ./designs/v[N]-[screen-name]-preview.[format]

  Note: Keep v[N-1] files for comparison.
</output_specification>

<validation_requirements>
  Before returning, verify:
  - [ ] All feedback items from previous version addressed
  - [ ] Nothing that "worked well" was accidentally changed
  - [ ] New requirements (if any) are implemented
  - [ ] All original validation requirements still pass

  Self-review: Is this version clearly better than v[N-1]?
  If not, keep refining.
</validation_requirements>
```

---

### Template 3: Blank Aesthetic Template (8 Sections)

Use this to capture a visual system from an existing design for reuse:

```markdown
# [Aesthetic Name]

## 1. Visual Identity
[2-3 sentences: Core design philosophy and feelings evoked. What's the vibe?
What should users feel when they see this design?]

## 2. Color System
- **Background:** [Primary background color with hex] - [why this color]
- **Surface:** [Secondary/card background with hex] - [why this color]
- **Accent primary:** [Main accent with hex] - [when to use]
- **Accent secondary:** [Secondary accent with hex] - [when to use]
- **Text primary:** [Main text color with hex]
- **Text secondary:** [Muted text color with hex]
- **Success/Error/Warning:** [State colors with hex]
- **Philosophy:** [1-2 sentences on color strategy]

## 3. Typography
- **Primary font:** [Font family] - [why chosen]
- **Headings:** [Size, weight, letter-spacing]
- **Body:** [Size, weight, line-height]
- **Labels:** [Size, weight, case (uppercase?)]
- **Captions:** [Size, weight, color]
- **Philosophy:** [1-2 sentences on typography approach]

## 4. Controls
- **Buttons:** [Shape, size, states, shadow]
- **Inputs:** [Border style, focus state, placeholder style]
- **Toggles/Switches:** [Style, on/off colors]
- **Sliders/Knobs:** [Style, track, thumb, value display]
- **Dropdowns:** [Style, arrow, open state]
- **Philosophy:** [1-2 sentences on control aesthetic]

## 5. Spacing & Layout Philosophy
- **Base unit:** [4px / 8px grid]
- **Density:** [Tight / Comfortable / Spacious]
- **Edge padding:** [Minimum padding from edges]
- **Component gaps:** [Standard gap between elements]
- **Section gaps:** [Gap between major sections]
- **Layout approach:** [How components should be arranged]

## 6. Surface & Details
- **Depth:** [Flat / Subtle shadows / Pronounced depth]
- **Borders:** [None / Subtle / Defined]
- **Border radius:** [Sharp / Slight / Rounded / Pill]
- **Texture:** [None / Subtle pattern / Pronounced texture]
- **Shadows:** [None / Light / Medium / Heavy - with CSS values]
- **Decorative elements:** [Any special visual features]
- **Hover/Active states:** [What changes on interaction]

## 7. Technical Implementation
- **CSS approach:** [Custom properties / specific techniques]
- **Animation:** [Transition durations, easing functions]
- **Responsive strategy:** [How design adapts]
- **Performance notes:** [What to avoid for performance]
- **Interaction feel:** [Snappy / smooth / immediate]

## 8. Usage Guidelines
- **Ideal use cases:** [Product types this aesthetic fits]
- **NOT suited for:** [What this aesthetic should NOT be used for]
- **1-3 components:** [Layout approach]
- **4-8 components:** [Layout approach]
- **9+ components:** [Layout approach]
- **Customization points:** [What can be adjusted]
- **Non-negotiables:** [What must stay consistent]
```

---

*This document captures principles and patterns for AI-driven UI design. Apply and adapt these patterns to your specific domain, platform, and quality requirements.*
