# LLM-Optimized Documentation Format

Principles for structuring documentation files that are effective for LLM consumption and code review automation.

## Core Principles

### Terseness Over Explanation

- Single-line rules; no paragraphs
- Sacrifice grammar for brevity: `"Label optional fields"` not `"You should always label optional fields explicitly"`
- No "why" explanations—rules are self-evident or trust is assumed
- Remove noise words: no `IMPORTANT:`, `YOU MUST`, `Please ensure`

### Concrete Syntax Inline

- Show code pattern directly in rule: `Early return: if (items.isEmpty) return const SizedBox.shrink();`
- Arrow notation for transformations: `.toList()..sort()` → `.sorted()`
- Backticks for identifiers: `useState`, `AsyncValue.guard()`

### Flat Hierarchy

- Maximum two levels: `Category → Rules`
- No nested subcategories
- Categories as H2/H3 headers, rules as bullet points
- Consolidate overlapping categories

### Dedicated Anti-Patterns Section

- Explicit "flag these" framing
- Mirror rules in negative form
- Quick pattern matching for violations
- Include concrete bad patterns: `_handleAction(ref, controller, user, state)` with 4+ params

### Output Format Specification

- Define exact output structure
- Include concrete example block
- Specify format: `file:line - issue → fix`
- Group by file, terse findings
- Include pass indicator: `✓ pass`

## File Structure

```text
---
description: One-line purpose statement
argument-hint: <file-or-pattern>
---

# Title

Review these files for compliance: $ARGUMENTS

Read files, check against rules below. Output concise but comprehensive—sacrifice grammar for brevity. High signal-to-noise.

## Rules

### Category Name

- Rule with `inline code` example
- Transformation: `bad pattern` → `good pattern`
- Concrete syntax: `if (x) return const Widget();`

### Another Category

- More rules...

## Anti-Patterns (flag these)

- Bad pattern description (use X instead)
- `concrete.bad.code()` (explanation)

## Output Format

Group by file. Use `file:line` format. Terse findings.

\`\`\`text
## path/to/file.ext

path/to/file.ext:42 - issue description → fix
path/to/file.ext:67 - another issue

## path/to/another.ext

✓ pass
\`\`\`

State issue + location. Skip explanation unless fix non-obvious. No preamble.
```

## Rule Writing Patterns

### Good Rules

```markdown
- Extract nested widgets into private builders: `_buildHeader()`, `_buildContent()`
- Immutable methods: `.sorted((a, b) => ...)` not `.toList()..sort()`
- Icon-only buttons need `aria-label`
```

### Bad Rules (avoid)

```markdown
- IMPORTANT: You must always ensure that nested widgets are properly extracted
- It is recommended to use immutable collection methods when possible
- Please make sure to add aria-label attributes to buttons that only have icons
```

## Transformation Checklist

When converting verbose documentation:

1. Delete introductory paragraphs and rationale
2. Compress sentences to single-line rules
3. Add concrete code inline with backticks
4. Use arrow `→` for before/after patterns
5. Consolidate overlapping sections
6. Extract violations to anti-patterns section
7. Add output format with example
8. Remove all filler: "basically", "should", "please", "important"
