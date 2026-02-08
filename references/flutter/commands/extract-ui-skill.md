---
description: Extract UI patterns from current Flutter project into a reusable implement-ui skill
allowed-tools: Task(Explore), AskUserQuestion, Glob, Grep, Read, Write, Bash, Skill(taches-cc-resources:create-agent-skills)
---

<objective>
Extract UI patterns, widgets, screen structures, and styling conventions from the current Flutter + Riverpod project into a comprehensive `implement-ui` skill. The skill enables consistent UI implementation by documenting discovered patterns, widget references, spacing constants, and screen structures.

Output: `.claude/skills/implement-ui/` with SKILL.md and dynamic reference files based on findings.
</objective>

<command_workflow>

# Phase 1: Pre-flight Checks

<output_quality_constraints>
<critical>
Optimize for high-signal, reusable output.
Avoid dumping large code blocks or full file contents into JSON.
</critical>

Global constraints:
- Prefer repo-relative file paths (e.g. `lib/common/widgets/...`), never absolute paths.
- Keep any code snippets short (≤ 20 lines). If longer, include only the key portion and mention what was omitted.
- Return valid JSON only from Explore agents (no commentary before/after the JSON).
- Prefer references over raw code: include file path + symbol/widget name + brief usage guidance.
</output_quality_constraints>

<existing_skill_check>
<critical>
Before any exploration, check if an implement-ui skill already exists.
</critical>

Use Glob to check for existing skill:
```
Glob(pattern: ".claude/skills/implement-ui/SKILL.md")
```

If skill exists, use AskUserQuestion:
```
Question: "An implement-ui skill already exists. How would you like to proceed?"
Header: "Existing Skill"
Options:
1. "Overwrite" - Replace existing skill with new extraction
2. "Review first" - Show me the existing skill before deciding
3. "Cancel" - Keep existing skill, abort extraction
```

If "Review first" selected, use Read to show existing SKILL.md, then ask again whether to overwrite or cancel.

If user selects "Cancel", stop immediately and do not create or write any files.
</existing_skill_check>

<setup_directories>
<critical>
Create the output directory before any Write calls (Phase 3 writes `analysis.json`).
</critical>

Use Bash to ensure output structure exists:
```bash
mkdir -p .claude/skills/implement-ui/references
```
</setup_directories>

<existing_docs_check>
If available, use existing documentation as authoritative baseline:

1. Use Glob for `docs/code_quality.md` and Read it if present

During synthesis, prefer documented guidance from `docs/code_quality.md` where applicable and use extraction primarily to:
- fill gaps,
- add concrete references/examples,
- and update any stale references.
</existing_docs_check>

<project_validation>
Verify this is a Flutter project with expected structure:

1. Use Glob to check for `pubspec.yaml`
2. Use Glob to check for `lib/common/widgets/` directory
3. Use Glob to check for screen files: `lib/**/*_screen.dart` (fallback: any `lib/**/screen*.dart` if naming differs)

If `lib/common/widgets/` doesn't exist, use AskUserQuestion:
```
Question: "No common widgets directory found at lib/common/widgets/. Where are shared widgets located?"
Header: "Widget Path"
Options:
1. "lib/widgets/" - Flat widget directory
2. "lib/shared/widgets/" - Shared module
3. "lib/core/widgets/" - Core module
4. "Other" - Let me specify the path
```

Store the widget path for agent prompts.
When launching Explore agents, substitute this widget path in SEARCH LOCATIONS and recommendations.
</project_validation>

---

# Phase 2: Parallel Exploration

<parallel_analysis>
<critical>
Launch 4 Explore agents IN A SINGLE MESSAGE for true parallel execution.
Each agent analyzes one UI domain and returns structured findings.
Do NOT launch agents sequentially - send ONE message with FOUR Task tool calls.
</critical>

<agent_1 name="Widget Catalog Analyzer">
```
Task(
  description: "Analyze widget organization and catalog",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for UI widget patterns. Be very thorough.

SEARCH LOCATIONS:
- Primary: lib/common/widgets/**/*.dart
- Secondary: lib/*/widgets/**/*.dart (feature-specific widgets)
- Also check: lib/shared/, lib/core/ for alternative organizations

FOCUS AREAS:
1. Widget Organization: Directory structure, naming conventions, atomic design usage
2. Frequently Used: Identify widgets imported in 5+ files
3. Layout Widgets: Scaffolds, containers, section boxes, card wrappers
4. Data Display: Labels, text widgets, value displays, status indicators
5. Input Widgets: Text fields, pickers, selectors, form components
6. Feedback Widgets: Loading states, error displays, empty states, toasts
7. Navigation: Buttons, list tiles, bottom sheets, modals

OUTPUT RULES:
- Output MUST be valid JSON (and JSON only).
- Keep lists concise: top 15 \"frequently_used\" and ≤ 20 items per category.
- For examples, use \"code_snippet_lines\" as an array of ≤ 20 lines (no triple-backticks).

OUTPUT FORMAT (JSON):
{
  \"organization\": {
    \"base_path\": \"lib/common/widgets/\",
    \"structure\": \"atomic|type-based|flat|mixed\",
    \"directories\": [{\"name\": \"...\", \"purpose\": \"...\", \"widget_count\": N}]
  },
  \"widgets\": {
    \"frequently_used\": [{
      \"name\": \"WidgetName\",
      \"purpose\": \"one-line description\",
      \"location\": \"relative/path.dart\",
      \"usage_count\": N
    }],
    \"by_category\": {
      \"layout\": [{\"name\": \"...\", \"purpose\": \"...\", \"location\": \"...\"}],
      \"data_display\": [...],
      \"input\": [...],
      \"feedback\": [...],
      \"navigation\": [...]
    }
  },
  \"patterns\": [{
    \"name\": \"pattern name\",
    \"description\": \"what it provides\",
    \"example_widget\": \"WidgetName\",
    \"code_snippet_lines\": [\"line 1\", \"line 2\"]
  }],
  \"external_packages\": [\"package:shadcn_ui\", ...],
  \"recommendations\": \"summary of what to document\"
}"
)
```
</agent_1>

<agent_2 name="Screen Pattern Analyzer">
```
Task(
  description: "Analyze screen structure patterns",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for screen implementation patterns. Be very thorough.

SEARCH LOCATIONS:
- Files ending in *_screen.dart across lib/
- Look for HookConsumerWidget, ConsumerWidget, StatelessWidget patterns
- Check for @RoutePage() annotations

FOCUS AREAS:
1. Base Structure: Common screen wrapper (Scaffold types, app bars)
2. Detail Screens: Single entity display with async data
3. Form Screens: Create/edit with validation and submission
4. List Screens: Paginated data, infinite scroll, grouping
5. Settings Screens: Navigation lists, preference toggles
6. Wizard/Flow Screens: Multi-step processes, state machines
7. State Handling: How loading, error, empty states are managed
8. Pull-to-refresh: RefreshIndicator patterns

OUTPUT RULES:
- Output MUST be valid JSON (and JSON only).
- Keep \"patterns\" to the most representative 8–12 examples.
- Use \"code_snippet_lines\" as an array of ≤ 20 lines (no triple-backticks).

OUTPUT FORMAT (JSON):
{
  \"base_structure\": {
    \"screen_widget\": \"HookConsumerWidget|ConsumerWidget|other\",
    \"scaffold_widget\": \"AppScaffold|Scaffold|other\",
    \"common_imports\": [\"package:...\"],
    \"code_template_lines\": [\"line 1\", \"line 2\"]
  },
  \"patterns\": [{
    \"type\": \"detail|form|list|settings|wizard\",
    \"name\": \"descriptive name\",
    \"reference_file\": \"lib/path/to/example.dart\",
    \"structure\": [\"1. First element\", \"2. Second element\"],
    \"key_widgets\": [\"Widget1\", \"Widget2\"],
    \"code_snippet_lines\": [\"line 1\", \"line 2\"],
    \"async_handling\": \"description of .when() or similar\"
  }],
  \"state_patterns\": {
    \"loading\": \"how loading is displayed\",
    \"error\": \"error handling approach\",
    \"empty\": \"empty state handling\"
  },
  \"recommendations\": \"patterns worth documenting\"
}"
)
```
</agent_2>

<agent_3 name="Spacing and Theme Analyzer">
```
Task(
  description: "Analyze spacing constants and theme patterns",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for spacing, theming, and styling patterns. Be very thorough.

SEARCH LOCATIONS:
- lib/common/theme/**/*.dart
- lib/common/extensions/**/*.dart
- Search for: const k.*Spacing, const k.*Padding, kSide, kCorner
- Look for: context.color, context.typography, Theme.of

FOCUS AREAS:
1. Spacing Constants: All k-prefixed spacing values and their purposes
2. Color Access: How colors are accessed (extensions, Theme.of, direct)
3. Typography: Text style access patterns
4. Animation: Duration constants, common curves
5. Corner Radii: Border radius constants
6. Scroll Physics: Default physics for scrollable content

OUTPUT RULES:
- Output MUST be valid JSON (and JSON only).
- Verify actual code locations; avoid assumptions.
- Keep lists concise and complete: include all spacing constants, but avoid duplicates/aliases.

OUTPUT FORMAT (JSON):
{
  \"spacing_constants\": [{
    \"name\": \"kBoxSpacing\",
    \"value\": \"8.0\",
    \"purpose\": \"Between components in same section\",
    \"file\": \"lib/common/extensions/build_context_ext.dart\"
  }],
  \"theme_access\": {
    \"colors\": \"context.color.primary or Theme.of(context)...\",
    \"typography\": \"context.typography.heading or TextTheme...\",
    \"example_code_lines\": [\"line 1\", \"line 2\"]
  },
  \"animation_constants\": [{
    \"name\": \"kDefaultDuration\",
    \"value\": \"Duration(...)\",
    \"purpose\": \"...\"
  }],
  \"scroll_physics\": {
    \"constant_name\": \"kBouncingPhysics or similar\",
    \"usage\": \"where it's used\"
  },
  \"recommendations\": \"what to include in constants reference\"
}"
)
```
</agent_3>

<agent_4 name="Advanced Pattern Analyzer">
```
Task(
  description: "Analyze advanced UI patterns",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for advanced and specialized UI patterns. Be very thorough.

SEARCH LOCATIONS:
- All *_screen.dart files for complex implementations
- Look for: useState, useEffect, custom hooks
- Search for: sealed class, PageTransitionSwitcher, AnimatedSwitcher
- Check for: ref.watch, ref.listen, ref.read patterns

FOCUS AREAS:
1. Multi-step Wizards: Sequential flows with state management
2. Form Validation: Validation approach (ShadForm, flutter_form_builder, manual)
3. Focus Management: FocusNode patterns in forms
4. Conditional UI: Role-based visibility, feature flags
5. Animations: Page transitions, implicit animations
6. Custom Hooks: Project-specific hooks (useInit, useAsyncEffect, etc.)
7. Provider Integration: How providers connect to UI
8. Error Handling: ref.listenOnError, toast patterns

OUTPUT RULES:
- Output MUST be valid JSON (and JSON only).
- Keep \"advanced_patterns\" to the most reusable 8–12 patterns.
- Use \"code_snippet_lines\" as an array of ≤ 20 lines (no triple-backticks).

OUTPUT FORMAT (JSON):
{
  \"advanced_patterns\": [{
    \"name\": \"pattern name\",
    \"type\": \"wizard|form|animation|state|hook\",
    \"description\": \"what it accomplishes\",
    \"reference_file\": \"lib/path/to/example.dart\",
    \"key_components\": [\"Component1\", \"Component2\"],
    \"code_snippet_lines\": [\"line 1\", \"line 2\"],
    \"when_to_use\": \"guidance on when to apply\"
  }],
  \"custom_hooks\": [{
    \"name\": \"useInit\",
    \"purpose\": \"Execute callback once on mount\",
    \"signature\": \"void useInit(VoidCallback callback)\",
    \"file\": \"lib/common/util/use_init_hook.dart\"
  }],
  \"provider_patterns\": [{
    \"pattern\": \"ref.listenOnError\",
    \"purpose\": \"Centralized error handling\",
    \"code_snippet_lines\": [\"line 1\", \"line 2\"]
  }],
  \"recommendations\": \"advanced patterns worth documenting\"
}"
)
```
</agent_4>

Wait for all 4 agents to complete before proceeding to Phase 3.
</parallel_analysis>

---

# Phase 3: Synthesize and Review

<synthesis>
After all agents complete:

1. **Parse Agent Outputs**: Extract JSON from each agent's response
2. **Merge Findings**: Combine into unified analysis structure
3. **Identify Gaps**: Note any missing or incomplete areas
4. **Detect Inconsistencies**: Flag conflicting patterns

During merge:
- Normalize all file paths to be repo-relative (no absolute paths).
- Prefer patterns consistent with `docs/code_quality.md` where relevant; flag disagreements explicitly.

Use Write to save combined analysis:
```
Write(
  file_path: ".claude/skills/implement-ui/analysis.json",
  content: [merged JSON analysis]
)
```
</synthesis>

<present_findings>
Present findings to user in this format:

---

## Widget Catalog

**Organization:** [structure type] in `[base_path]`

**Frequently Used Widgets:**
- `WidgetName` - Purpose (N+ usages)
- [continue for top 10]

**Categories Found:**
- Layout: N widgets
- Data Display: N widgets
- Input: N widgets
- Feedback: N widgets
- Navigation: N widgets

---

## Screen Patterns

**Base Structure:** [screen widget type] with [scaffold widget]

**Patterns Detected:**
| Type | Reference | Key Widgets |
|------|-----------|-------------|
| Detail | `lib/path/file.dart` | Widget1, Widget2 |
| Form | `lib/path/file.dart` | Widget1, Widget2 |
[continue for each pattern found]

**State Handling:**
- Loading: [approach]
- Error: [approach]
- Empty: [approach]

---

## Spacing & Theme

**Spacing Constants:**
| Constant | Value | Purpose |
|----------|-------|---------|
| `kName` | 8.0 | Description |
[continue for all found]

**Theme Access:**
- Colors: [pattern]
- Typography: [pattern]

---

## Advanced Patterns

**Documented:**
- [Pattern 1]: [brief description]
- [Pattern 2]: [brief description]

**Custom Hooks:**
- `hookName()` - Purpose

---

</present_findings>

<user_review>
Use AskUserQuestion to confirm findings:

```
Question: "Review the findings above. Are there any areas that need deeper investigation or corrections?"
Header: "Findings Review"
Options:
1. "Looks good - proceed to generation" - Continue with current findings
2. "Investigate specific areas" - Explore certain patterns further
3. "Add missing patterns" - I'll describe patterns you missed
4. "Exclude some findings" - Remove irrelevant patterns
```

If "Investigate specific areas" or "Add missing patterns" selected, use follow-up AskUserQuestion to gather specifics, then launch additional Explore agents as needed.

If "Exclude some findings" selected, ask which categories or specific patterns to exclude.

Iterate until user selects "Looks good - proceed to generation".
</user_review>

---

# Phase 4: Generate Skill Output

<determine_reference_files>
Based on findings, determine which reference files to create:

**Always create:**
- `SKILL.md` - Main skill definition

**Create if substantial content found:**
- `references/widgets.md` - If 10+ widgets documented
- `references/screen-patterns.md` - If 3+ screen patterns found
- `references/constants.md` - If 5+ spacing/theme constants found
- `references/advanced-patterns.md` - If 3+ advanced patterns found

For sparse projects (fewer findings), consolidate into fewer files or all-in-one SKILL.md.
</determine_reference_files>

<generate_skill_md>
<critical>
Before generating SKILL.md, attempt to invoke the `taches-cc-resources:create-agent-skills` skill using the Skill tool.
Pass the extracted patterns and analysis as context.

If the skill tool is unavailable or errors, proceed with the structure below (do not block generation).
</critical>

Generate SKILL.md following this structure:

<critical>
Replace all bracketed placeholders (e.g. `[app-name]`, `[widget_path]`, `[list main constants]`, `[error_widget]`) with actual values from the analysis and/or existing guides. Do not leave placeholders in the final output.
</critical>

```markdown
---
name: implement-ui
description: Expert guidance for implementing UI screens and components in this [app-name] app. Use when building screens, creating widgets, or following UI patterns. Provides widget references, spacing constants, screen patterns, and best practices.
---

<objective>
Implement high-quality, consistent UI screens and components that follow established patterns in this codebase. This skill provides comprehensive guidance on widget organization, spacing constants, screen patterns, and implementation best practices.

Load this skill when implementing any UI-related task to ensure pattern compliance and widget reuse.
</objective>

<essential_principles>

**1. Research Before Building**
Always check existing screens in the same feature folder for established patterns. Search `[widget_path]` before creating new components.

**2. Reuse Over Recreation**
Never create widgets that already exist in `[widget_path]`. Check `<widget_quick_reference>` below and reference files before building anything.

**3. Follow Spacing Constants**
Always use spacing constants ([list main constants]) instead of hardcoded values. Never use magic numbers for spacing.

**4. Handle All States**
Every async data display must handle loading, error, and empty states. Use [error_widget] for errors and always implement pull-to-refresh on detail screens.

**5. Match Existing Patterns**
Match the structure of similar existing screens ([pattern types found]). Don't innovate on patterns unless explicitly required.

</essential_principles>

<widget_quick_reference>

**Most Used Widgets (check these first):**

| Widget | Purpose | Location |
|--------|---------|----------|
[Top 10 frequently used widgets from analysis]

**Full widget reference:** `references/widgets.md`

</widget_quick_reference>

<spacing_quick_reference>

[Table of spacing constants from analysis]

**Full constants reference:** `references/constants.md`

</spacing_quick_reference>

<screen_pattern_quick_reference>

**Screen Type → Reference File Pattern**

| Screen Type | Key Widgets | Reference Pattern |
|-------------|-------------|-------------------|
[Each pattern type found with key widgets and reference file]

**Full patterns with code:** `references/screen-patterns.md`

</screen_pattern_quick_reference>

<common_mistakes>

**Avoid These:**

1. **Creating duplicate widgets** - Always search `[widget_path]` first
2. **Hardcoded spacing** - Use [constant names]
3. [Additional mistakes based on patterns found]

</common_mistakes>

<implementation_checklists>

[Generate checklist for each screen pattern type found]

</implementation_checklists>

<reference_index>

**Widget Organization:**
```
[Directory tree from widget analysis]
```

**Detailed References:**
[List reference files created]

</reference_index>

<success_criteria>

UI implementation is complete when:

- [ ] Widget reuse checked - no duplicate widgets created
- [ ] Spacing constants used - no hardcoded values
- [ ] Screen pattern matches established patterns
- [ ] All async states handled (loading, error, data, empty)
- [ ] Pull-to-refresh implemented where appropriate
- [ ] Error retry implemented where appropriate
- [ ] Code formatted and passes analysis

</success_criteria>
```

Use Write to save: `.claude/skills/implement-ui/SKILL.md`
</generate_skill_md>

<generate_reference_files>
For each reference file determined necessary:

**widgets.md:**
```markdown
<overview>
Complete widget reference for [app-name]. Widgets are organized by category in `[widget_path]`. Always check this reference before creating new components.
</overview>

<frequently_used>
[Table of most-used widgets]
</frequently_used>

[Additional categories based on analysis]

<widget_organization>
[Directory structure]
</widget_organization>
```

**screen-patterns.md:**
```markdown
<overview>
Screen implementation patterns with code examples.
</overview>

[For each pattern type found:]

<pattern name="[Pattern Name]">
<reference>[file path]</reference>

<structure>
[Numbered list of elements]
</structure>

<key_widgets>
[List of widgets used]
</key_widgets>

<code_example>
```dart
[Code from analysis]
```
</code_example>
</pattern>
```

**constants.md:**
```markdown
<spacing_constants>
[Table with name, value, purpose]
</spacing_constants>

<theme_access>
[Color and typography access patterns]
</theme_access>

<animation_constants>
[If found]
</animation_constants>
```

**advanced-patterns.md:** (if needed)
```markdown
[For each advanced pattern:]

<pattern name="[Name]">
<when_to_use>[guidance]</when_to_use>

<implementation>
```dart
[Code example]
```
</implementation>

<key_components>
[List]
</key_components>
</pattern>
```

Use Write to save each reference file to `.claude/skills/implement-ui/references/`.
</generate_reference_files>

---

# Phase 5: Validation

<syntax_validation>
Perform basic validation of generated content:

1. **Check YAML frontmatter**: Use Read to verify SKILL.md starts with valid `---` block
2. **Check file references**: Use Glob to verify all referenced files in SKILL.md exist
3. **Check code snippets**: Use Grep to verify referenced screen files exist at stated paths

Report any validation issues to user.
</syntax_validation>

<final_review>
Use AskUserQuestion for final review:

```
Question: "The implement-ui skill has been generated. Would you like to review it before finalizing?"
Header: "Final Review"
Options:
1. "Show me SKILL.md" - Display the main skill file
2. "List generated files" - Show what was created
3. "Done - finalize skill" - Complete the extraction
```

If "Show me SKILL.md" selected, use Read to display the file, then ask if any edits are needed.

Iterate until user selects "Done - finalize skill".
</final_review>

---

# Phase 6: Completion Report

<final_report>
Present completion summary:

```
Skill extraction complete!

Generated files:
.claude/skills/implement-ui/
  SKILL.md                      - Main skill definition
  references/
    widgets.md                  - [N] widgets documented
    screen-patterns.md          - [N] patterns documented
    constants.md                - [N] constants documented
    [additional files if created]

Summary:
- Widgets: [N] cataloged across [N] categories
- Screen Patterns: [list types found]
- Spacing Constants: [N] documented
- Advanced Patterns: [N] documented

Usage:
Load this skill when implementing UI by asking Claude to use the implement-ui skill,
or reference specific patterns by reading the reference files directly.
```
</final_report>

</command_workflow>

<fallback_behavior>
If `taches-cc-resources:create-agent-skills` skill is unavailable:
- Proceed with the SKILL.md structure defined in Phase 4
- Use XML tags for structure (<objective>, <patterns>, etc.)
- Follow the pattern of existing implement-ui skills in the codebase
- Ensure YAML frontmatter has `name` and `description` fields
</fallback_behavior>

<success_criteria>
- Pre-flight checks completed (existing skill, project validation)
- 4 Explore agents launched in parallel
- All findings presented and confirmed with user
- Reference files generated dynamically based on content found
- Basic syntax validation passed
- User confirmed final output
- Completion report presented
</success_criteria>
