---
description: Optimize Markdown skill and reference documentation for LLM consumption. Use on SKILL.md content, reference files, or entire documentation folders.
argument-hint: "<file-or-folder-path>"
allowed-tools: [Read, Write, Edit, Glob, Grep, AskUserQuestion]
---

<objective>
Apply LLM-optimized documentation principles to existing Markdown files. Works on a single `.md` file or an entire folder (skill directory, reference folder, etc.).

Transforms verbose, human-oriented documentation into terse, high-signal reference files that LLMs parse efficiently — without losing accuracy or completeness.
</objective>

<context>
Target: $ARGUMENTS (required — path to a `.md` file or folder containing `.md` files)
</context>

<principles>
Core transformations (apply all of these):

- Compress sentences to single-line rules with inline code
- Add concrete code inline with backticks: `if (items.isEmpty) return const SizedBox.shrink();`
- Use arrow `→` for before/after: `.toList()..sort()` → `.sorted()`
- Maximum two levels: Category (H2) → Rules (bullets)
- Consolidate overlapping sections
- Extract violations to Anti-Patterns section
- Remove all filler: "basically", "should", "please", "important", "make sure to"
- Remove `IMPORTANT:`, `YOU MUST`, `Please ensure` prefixes
- Remove introductory paragraphs and rationale
- Remove `---` horizontal rules between sections
- No "why" explanations — rules are self-evident
- Delete duplicate summary/recap sections that restate rules already covered
</principles>

<preservation_rules>
<critical>
Preserve actionable reference data even when it appears redundant with surrounding code examples.

Never remove:
- **Checklists** — verification tools, not explanations. Compress items but keep every item.
- **Decision frameworks** — "when to use X vs Y", "key principles" sections. These are the mental model for choosing between options. Compress to terse bullets but don't delete.
- **Generated/output examples** — showing what a tool produces. Without the output shape, the code that references it becomes opaque.
- **Alternative syntax** — distinct API surfaces (e.g., `tr()` vs `.tr()`) are separate patterns, not restatements.
- **Default values and parameter behavior** — omitting defaults changes the meaning of "optional."
- **Code blocks** — these ARE the documentation in pattern files. Keep complete and copy-pasteable. Only trim prose wrapping them.
- **Tables** — structured reference data (parameters, types, mappings). Compress columns but keep all rows.

Test: if removing a line would force the reader to reverse-engineer the answer from code examples, keep it.
</critical>
</preservation_rules>

<context_efficiency>
Git is the safety net. Write files directly — user reviews via `git diff` and reverts with `git checkout` if needed.

- No draft files, no intermediate copies
- No full-content previews in conversation — write and summarize
- Process files sequentially: read one → transform → write → next
- Confirm once before batch, not per file
</context_efficiency>

<process>

## 1. Determine Scope

Read $ARGUMENTS path:

**Single file:** Process that one file.

**Folder:** Use Glob to find all `.md` files in the folder (including subdirectories):
```
Glob(pattern: "$ARGUMENTS/**/*.md")
```

If folder contains 5+ files, use AskUserQuestion:
```
Question: "Found N markdown files. Process all of them or select specific ones?"
Header: "Scope"
Options:
1. "All files" - Process every .md file in the folder
2. "Let me pick" - I'll specify which files to process
3. "Preview first" - Show me the file list
```

## 2. Assess and Confirm

Read each file. For each, classify by type and identify specific changes.

**File type determines transformation strategy:**

| Type | Signal | Strategy |
|------|--------|----------|
| Rules/guidelines | Mostly prose bullets, few code blocks | Aggressive compression — sentences → terse rules |
| Pattern/reference | Code-heavy with prose wrappers | Keep code, trim prose around it |
| Setup/config | Step-by-step with code blocks | Keep code and commands, trim explanatory text |
| API reference | Tables, parameters, signatures | Keep tables and signatures, trim descriptions |

Present a per-file change plan showing what will be removed, kept, and rewritten:

```
## [filename] (N lines, Type)

**Remove:**
- [Section/content being deleted and why]

**Compress:**
- [Section] — rewrite from prose to terse bullets

**Keep as-is:**
- [Code blocks, tables, checklists that stay unchanged]
```

Then confirm before any writes. Use AskUserQuestion:
```
Question: "Review the change plan above. Proceed? You can review all changes via git diff afterward."
Header: "Confirm"
Options:
1. "Proceed" - Optimize all files
2. "Skip some" - Let me exclude specific files
3. "Questions first" - I want to ask about specific sections
4. "Cancel" - Don't make changes
```

## 3. Transform and Write

Process each file sequentially. For each file:

**Read → Transform → Write → Report one-liner.** Do not hold multiple files in memory.

Apply transformations in this order:

**Pass 1 — Delete**
- Introductory paragraphs ("This document describes...", "Use these rules when...")
- "Why" explanations and rationale paragraphs
- Duplicate summary/recap sections that restate rules already covered
- `---` horizontal rules between sections
- Filler words and noise prefixes

**Pass 2 — Compress**
- Multi-sentence rules → single-line rules with inline code
- Verbose headers → terse headers (`## 1) Breaking up a large build() method` → `## Breaking Up build()`)
- Numbered prose lists → bullet points
- "When to use" paragraphs → single-line bullets
- Checkbox checklists `- [ ]` → plain bullets `-` (keep every item)

**Pass 3 — Restructure**
- Flatten deep nesting (max 2 levels: H2 → bullets)
- Consolidate overlapping sections
- Move violations/bad patterns to Anti-Patterns section (create if missing, only when file has rule-like content)
- Ensure code blocks use language-specific fencing (```dart, ```yaml, etc.)

**Pass 4 — Verify completeness** (before writing)
- Every checklist item still present (compressed, not deleted)
- Every decision framework still present (terse, not deleted)
- Every code block still present and complete
- Every table still present with all rows
- Default values and parameter behavior preserved
- Alternative syntax variants preserved

After writing each file, output a single summary line:
```
✓ file.md — 120 → 85 lines (29% reduction)
```

## 4. Final Report

After all files are written:

```
Optimized N file(s):

| File | Before | After | Reduction |
|------|--------|-------|-----------|
| file.md | X lines | Y lines | Z% |

Review changes: `git diff`
Revert all: `git checkout -- <path>`
```

</process>

<success_criteria>
- Preservation rules verified — no checklists, code blocks, tables, or decision frameworks removed
- User confirmed before any writes
- Files written directly (no drafts)
- Final report with line counts and git commands
- No placeholder text or broken markdown in output
</success_criteria>
