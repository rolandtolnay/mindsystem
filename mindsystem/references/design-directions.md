<design_directions>

Reference for deriving context-adaptive design directions. Read by the design-phase orchestrator before spawning mockup agents.

<philosophy>

Design directions emerge from context, not from fixed categories.

Bad approach: Always generate "minimal", "dense", and "bold" variants.
Good approach: Analyze the feature, its tensions, and generate 3 directions that explore the most valuable design axes for THIS specific feature.

A collection view for a recipe app has different tensions than a collection view for a project management tool. "Minimal vs. dense" might be irrelevant when the real tension is "browsable vs. searchable" or "visual-first vs. metadata-first."

Each direction represents a meaningfully different design philosophy — not a color/font swap.
</philosophy>

<derivation_process>

Three-step process for the orchestrator:

**Step 1: Identify the primary tension**

What is the core design trade-off for this feature? Examples:
- Information density vs. scannability
- Guided flow vs. power-user flexibility
- Visual richness vs. speed/simplicity
- Discovery vs. task completion
- Content-first vs. navigation-first

**Step 2: Pick the most valuable exploration axes**

From the primary tension and feature context, identify 3 axes worth exploring. These become the directions. An axis is a spectrum with a clear "more of X vs. more of Y" dimension.

Examples of axes:
- Density: spacious ↔ compact
- Navigation: linear ↔ non-linear
- Hierarchy: flat ↔ layered
- Interaction: direct manipulation ↔ command-driven
- Content: visual-heavy ↔ text-heavy
- Organization: chronological ↔ categorical

**Step 3: Generate 3 directions**

Place each direction at a distinct, defensible point along the axes. Each direction gets:
- A short name (2-3 words)
- A one-sentence philosophy
- 2-3 concrete layout/component choices that make it different

Directions must differ in STRUCTURE, not decoration. A user should be able to tell them apart from a wireframe alone.
</derivation_process>

<feature_type_examples>

**Collection views** (lists, grids, galleries)
- Possible axes: list ↔ grid ↔ carousel, metadata-rich ↔ visual-only, flat ↔ grouped
- Example directions: "Card Grid" (visual browsing), "Dense Table" (scannable metadata), "Grouped Timeline" (chronological with sections)

**Navigation patterns** (sidebars, tabs, menus)
- Possible axes: persistent ↔ contextual, flat ↔ hierarchical, visible ↔ collapsed
- Example directions: "Sidebar + Breadcrumbs" (always-visible hierarchy), "Contextual Tabs" (content-driven navigation), "Command Palette" (search-first, keyboard-native)

**Dashboards** (overviews, summaries, analytics)
- Possible axes: dense ↔ focused, data-driven ↔ action-driven, overview ↔ drill-down
- Example directions: "KPI Wall" (dense metrics, minimal chrome), "Action Center" (task-oriented, metrics secondary), "Story View" (guided narrative through data)

**Forms** (input, configuration, settings)
- Possible axes: single-page ↔ multi-step, minimal ↔ contextual, standard ↔ conversational
- Example directions: "Single Page" (everything visible, scroll to complete), "Progressive Wizard" (step-by-step with validation), "Inline Edit" (settings as editable display)

**Detail screens** (profiles, items, articles)
- Possible axes: linear ↔ tabbed, content-first ↔ action-first, minimal ↔ comprehensive
- Example directions: "Linear Scroll" (long-form, everything in order), "Tabbed Sections" (organized by category, quick jump), "Split View" (summary left, details right)
</feature_type_examples>

<what_makes_variants_different>

**Good differentiation** (structural, visible in wireframe):
- Different layout patterns (sidebar vs. top-nav vs. no-nav)
- Different component choices (cards vs. table rows vs. list items)
- Different information hierarchy (what's prominent vs. tucked away)
- Different interaction models (tabs vs. scroll vs. expand/collapse)
- Different density levels (spacious overview vs. dense working view)

**Bad differentiation** (cosmetic, invisible in wireframe):
- Different color palettes with same layout
- Different border-radius values
- Different font choices with same hierarchy
- Different shadow depths
- Different icon styles

Rule: If you can only tell variants apart by squinting at colors, they are not different enough.
</what_makes_variants_different>

<existing_aesthetic_constraint>

When the project has an existing visual aesthetic (implement-ui skill, established codebase patterns):

**ALL variants use the same colors, fonts, and component shapes.** Directions differ ONLY in:
- Layout and spatial organization
- Component selection and arrangement
- Information density and hierarchy
- Navigation patterns
- Content emphasis and ordering

This constraint is non-negotiable. Mockup directions explore layout alternatives, not brand alternatives. An existing product stays visually cohesive across all variants.

When the project is greenfield (no existing aesthetic):
- Each variant MAY propose a different color palette
- Each variant MAY propose different typography
- Structural differences remain the primary differentiator
</existing_aesthetic_constraint>

</design_directions>
