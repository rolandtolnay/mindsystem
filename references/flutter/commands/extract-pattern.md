---
description: Extract reusable Flutter/Dart patterns from the current project into LLM-optimized documentation
argument-hint: "<pattern-area-description>"
allowed-tools: [Task, AskUserQuestion, Glob, Grep, Read, Write, Bash]
---

<objective>
Extract implementation patterns from a specific project area (e.g., error handling, authentication, navigation, pagination) into a standalone LLM-optimized pattern file.

Output: a `.md` file in `docs/patterns/` (or user-specified location) that follows LLM documentation principles — terse rules, inline code, flat hierarchy, anti-patterns section, no prose filler.

The output is designed to be portable across Flutter projects as a reference for refactoring existing code or implementing new features correctly.
</objective>

<execution_context>
@docs/patterns/ (existing pattern files — match their format)
</execution_context>

<context>
Pattern area: $ARGUMENTS (required — describes what to extract)
</context>

<output_format_spec>
The generated pattern file follows these LLM-optimized documentation principles:

- Single-line rules with inline code: `Early return: if (items.isEmpty) return const SizedBox.shrink();`
- Arrow notation for transformations: `.toList()..sort()` → `.sorted()`
- Maximum two levels: `Category (H2) → Rules (bullets)`
- Code blocks ARE the documentation — keep them, trim prose around them
- Dedicated Anti-Patterns section with concrete bad patterns
- No "why" explanations, no filler words, no `IMPORTANT:` prefixes
- Checklists use plain bullets, not checkboxes

**Structure template:**
```markdown
# Pattern Name

One-line description of what this pattern covers.

## Section Name

- Terse rule with `inline code`
- Another rule: `concrete example`

```dart
// Code block serving as template — keep complete and copy-pasteable
```

- Bullet summarizing key points from code above (only if non-obvious)

## Another Section

...

## Checklist

- Verification item
- Another verification item

## Anti-Patterns (flag these)

- Bad pattern description (`concrete.bad.code()`)
- Another bad pattern → fix
```
</output_format_spec>

<context_efficiency>
Write the pattern file directly — user reviews in their editor or via `git diff`, not by reading full content in conversation.

- No "present draft in conversation" step — write the file, then ask for feedback
- User's editor provides better review (syntax highlighting, scrolling) than CLI output
- Iterate via targeted edits, not full rewrites
- Git is the safety net for reverting
</context_efficiency>

<process>

## 1. Parse and Clarify Pattern Area

Read $ARGUMENTS. If the description is vague or could mean multiple things, use AskUserQuestion immediately:

```
Question: "What specific aspect of [area] should this pattern cover?"
Header: "Pattern Scope"
Options: [2-4 concrete interpretations based on $ARGUMENTS]
```

Ask additional clarifying questions as needed:
- What files or directories contain the relevant implementation?
- Are there specific conventions or libraries involved (e.g., Riverpod, Dio, auto_route)?
- Should this pattern document an existing implementation or a target architecture?
- Are there parts of the current implementation that should NOT be documented (known tech debt)?

Do not proceed until you have a clear, unambiguous understanding of what to extract.

## 2. Check Existing Patterns

```bash
ls docs/patterns/ 2>/dev/null
```

If a pattern file for this area already exists, use AskUserQuestion:
```
Question: "A pattern file for [area] already exists. How should we proceed?"
Header: "Existing Pattern"
Options:
1. "Replace" - Extract fresh and overwrite
2. "Review first" - Show existing file before deciding
3. "Cancel" - Keep existing, abort
```

## 3. Parallel Codebase Exploration

<critical>
Launch all N agents in a SINGLE message with N parallel Task tool calls. Do NOT launch sequentially.

Determine 3-5 exploration angles based on the pattern area. Each agent explores one angle.
</critical>

Example angles (adapt to the specific pattern area):
- **Architecture angle**: How is this area structured? What classes, interfaces, base types exist?
- **Implementation angle**: What does the actual implementation look like? Key code paths, algorithms, state management.
- **Usage angle**: How is this consumed by screens/widgets? What's the API surface from the caller's perspective?
- **Integration angle**: How does this connect to other systems? Dependencies, providers, shared state.
- **Edge cases angle**: Error handling, loading states, empty states, retry logic, platform differences.

For each agent, use `subagent_type: "Explore"` with thoroughness "very thorough":

```
Task(
  description: "[Angle] for [pattern area]",
  subagent_type: "Explore",
  prompt: "Thoroughly explore this Flutter codebase for [specific angle].

SEARCH STRATEGY:
- Start with: [specific directories/files based on user input]
- Also check: [related directories]
- Search for: [specific class names, patterns, imports]

CAPTURE:
1. File paths of all relevant implementations
2. Key code blocks (complete, copy-pasteable — not fragments)
3. Naming conventions and structural patterns
4. How this connects to the rest of the codebase

Return findings as structured text with file paths and code blocks."
)
```

Wait for all agents to complete.

## 4. Analyze and Resolve Contradictions

Review all agent findings. Look for:

- **Contradicting patterns**: Different files doing the same thing differently
- **Unclear conventions**: Patterns that might be intentional vs accidental
- **Incomplete coverage**: Areas the agents didn't find enough about
- **Tech debt vs convention**: Older code that doesn't match newer patterns

For EACH contradiction or ambiguity found, use AskUserQuestion:

```
Question: "I found two different approaches to [thing]. Which represents the intended pattern?"
Header: "Resolve Pattern"
Options:
1. "[Approach A from file X]" - Description
2. "[Approach B from file Y]" - Description
3. "Both are valid" - Document both with when-to-use guidance
4. "Neither" - Let me explain the intended approach
```

Thoroughness is more important than speed. Ask as many questions as needed to achieve complete clarity.

## 5. Write Pattern File

Default output path: `docs/patterns/[slug].md`. If this directory doesn't exist in the project, ask the user where to save.

Synthesize agent findings into the LLM-optimized format and write the file directly:

1. **Title and one-line description**
2. **Group by functional area** — each area becomes an H2 section
3. **Rules as terse bullets** with inline code
4. **Code blocks for templates** — complete, copy-pasteable implementations
5. **Minimal prose between code blocks** — only when the code isn't self-evident
6. **Tables for structured reference data** (parameters, types, mappings)
7. **Checklist section** — verification items for implementers
8. **Anti-Patterns section** — concrete bad patterns with fixes

Quality checks before writing:
- Every rule has inline code or a code block
- No sentences starting with "You should", "It is recommended", "Make sure to"
- No `---` horizontal rules between sections
- No explanatory paragraphs — compress to single-line rules
- Code blocks include enough context to be copy-pasteable
- All code blocks use ```dart fencing
- No placeholder text remains

After writing, report the file path, line count, and section list. Then use AskUserQuestion:

```
Question: "Pattern file written. Open it in your editor to review. What's next?"
Header: "Review"
Options:
1. "Looks good" - Done
2. "Missing patterns" - I'll describe what to add
3. "Needs corrections" - I'll describe what's wrong
4. "Too verbose" - Compress further
```

If changes needed, apply targeted edits to the file (not full rewrites).

</process>

<collaboration_principles>
Thoroughness over speed. This command extracts reusable documentation that will be referenced across multiple projects. Getting it right matters more than getting it fast.

**When to ask the user (non-exhaustive):**
- Pattern area description is ambiguous or could mean multiple things
- Found contradicting implementations across files
- Unsure whether something is intentional convention vs tech debt
- Multiple valid approaches exist and it's unclear which to document
- Agent exploration found gaps — unclear where to look next
- Draft includes patterns you're not confident about

**How to ask:**
- Always use AskUserQuestion with concrete options
- Include file paths and code snippets in option descriptions when relevant
- Never ask yes/no questions — provide actionable choices
- Group related uncertainties into a single question when possible
</collaboration_principles>

<success_criteria>
- Pattern area fully understood through clarifying questions
- 3-5 explore agents launched in parallel (SINGLE message)
- All contradictions and ambiguities resolved with user
- Output file follows LLM-optimized format (terse rules, inline code, anti-patterns)
- Code blocks are complete and copy-pasteable
- File written directly (no draft-in-conversation step)
- User reviewed in editor and approved
</success_criteria>
