---
description: Extract coding principles from code changes and append them to docs/CODE_QUALITY.md
argument-hint: [focus_instructions] [number] [commit_sha]
allowed-tools: Bash, Read, Edit, Glob, Grep, AskUserQuestion
---

# learn

Use ultrathink and extract coding principles from code changes and append them to `docs/CODE_QUALITY.md`.

## Usage

```
learn [focus_instructions] [number] [commit_sha]
```

All arguments in `$ARGUMENTS` are optional and can appear in any order:
- **Focus instructions**: Natural language describing what areas to focus on (e.g., "form validation patterns", "error handling improvements")
- **Number**: Explicit count of principles to extract (e.g., `5`)
- **Commit SHA**: A git commit hash to analyze instead of uncommitted changes (e.g., `a1b2c3d`)

### Examples
- `learn` - Auto-extract principles from uncommitted changes
- `learn 5` - Extract exactly 5 principles from uncommitted changes
- `learn focus on state management patterns` - Extract principles focused on state management
- `learn a1b2c3d` - Extract principles from a specific commit
- `learn 3 error handling in the payment flow` - Extract 3 principles about error handling
- `learn abc123 widget decomposition` - Extract principles about widget decomposition from commit abc123

## Contract

- **Inputs:** Optional focus instructions, number, or commit SHA from `$ARGUMENTS`
- **Outputs:** Adds new principles (as new bullet lines) to `docs/CODE_QUALITY.md`
- **Side Effects:** Modifies `docs/CODE_QUALITY.md` by inserting new bullet lines only (no edits or deletions)
- **Stop Conditions:** No git changes found; `docs/CODE_QUALITY.md` doesn't exist
- **Definition of Done:** New principles appended, no duplicates, file verified

## Safety

- This command appends to `docs/CODE_QUALITY.md` (non-destructive)
- Never edits or deletes existing text; only adds new bullet lines under existing `### ...` headings, or adds new sections at the end if needed
- If duplicate principles are detected, skip them rather than append
- Duplicate detection: normalize candidate and existing bullets by trimming and collapsing whitespace; compare both with and without the `IMPORTANT:` / `YOU MUST` prefix, and treat exact matches as duplicates
- All changes are in version control and can be reverted with git

## Instructions

### 1. Parse Arguments

Analyze `$ARGUMENTS` to identify:
- **Commit SHA**: Look for a 7+ character hex string, and verify it's a commit with `git rev-parse --verify <sha>^{commit}` (if verification fails, treat it as focus text)
- **Explicit count**: Look for standalone numbers (e.g., `5`, `10`)
- **Focus instructions**: Remaining text describes areas to emphasize

### 2. Analyze Code Changes

**If commit SHA is provided:**
- Run `git show -m --format="%s%n%n%b" <commit_sha>` to understand intent and see the patch (use `-m` so merge commits still show changes)

**Otherwise (uncommitted changes):**
- Run `git diff --cached` to see staged changes
- Run `git diff` to see unstaged changes

Focus on: refactoring patterns, style improvements, architectural decisions, and areas mentioned in focus instructions.

### 3. Determine Optimal Number of Principles

**If explicit count provided:** Use that number.

**Otherwise, calculate based on:**
- Size of diff (more changes = more potential principles)
- Diversity of patterns (multiple categories = more principles)
- User's focus instructions (narrow focus = fewer, deeper principles; broad focus = more principles)
- Avoid redundancy with existing `docs/CODE_QUALITY.md` guidelines

**Guidelines:**
- Small focused change: 1-3 principles
- Medium refactoring: 3-5 principles
- Large architectural change: 5-8 principles
- Never exceed 10 principles per invocation

### 4. Extract Principles

- Look for patterns in how code was improved
- Identify what was changed from "bad" to "good" patterns
- Prioritize areas mentioned in user's focus instructions
- Focus on reusable principles, not specific implementations
- Consider: structure, naming, error handling, state management, API design

### 5. Apply Emphasis Markers

Add emphasis markers based on rule importance:

**Use `IMPORTANT:` when the rule:**
- Prevents subtle bugs that are hard to debug
- Enforces architectural boundaries (e.g., "business logic in entities, not UI")
- Has significant impact on code maintainability
- Is easy to forget but important to follow

**Use `YOU MUST` when the rule:**
- Prevents security issues or data corruption
- Is a non-negotiable standard (e.g., "sanitize input", "use immutable collections")
- Violating it causes immediate, obvious problems
- Is a hard requirement, not a preference

**Examples:**
```markdown
- IMPORTANT: Encapsulate business rules in entity computed properties
- YOU MUST sanitize text input on capture: `controller.text.trim()`
- Use semantic spacing constants for hierarchy (no marker - preference)
```

### 6. Categorize Principles

Group into categories like:
- Widget Structure
- State Management
- Error Handling
- API Design
- Testing Patterns
- Performance
- Code Organization
- Form Validation
- Data Modeling

Match existing categories in `docs/CODE_QUALITY.md` when possible.

### 7. Format Principles

```markdown
### Category Name
- [EMPHASIS] Brief action-oriented rule with inline example: `specificMethod()` or `Pattern.usage()`
- Another principle with concrete pattern from the codebase
- Focus on WHAT to do, include HOW inline
```

### 8. Append to `docs/CODE_QUALITY.md`

- Add principles under existing category sections when they match (by inserting new bullet lines into the appropriate `### ...` section)
- Create new category sections only when necessary (append new `### ...` sections at the end)
- Maintain consistent formatting with existing guidelines
- Ensure no duplication with existing principles
- Keep descriptions concise and LLM-optimized

### 9. Verify Changes

- Read back `docs/CODE_QUALITY.md` to confirm changes were applied correctly
- Run `git diff -- docs/CODE_QUALITY.md` and confirm the diff contains only additions (no removed/modified lines beyond diff headers)
- Verify no duplication with existing principles occurred
- Confirm markdown syntax is valid (no broken formatting)
- Summarize which sections were updated or created (e.g., "added 2 bullets under ### Error Handling")
- If verification fails, report the issue and do not claim success

## Example Output

```markdown
### State Management
- IMPORTANT: Initialize providers with defensive null checks: `if (account == null) return emptyState;`
- Use `copyWithPrevious` for paginated data updates
- Invalidate dependent providers after mutations

### Error Handling
- Wrap API calls with `AsyncValue.guard()` for consistent error handling
- YOU MUST log errors with context: `logger.e('PaymentApi.charge failed', error, stackTrace)`

### Input Handling
- YOU MUST sanitize text input on capture: `notifier.updateField(value: controller.text.trim())`
```

## Notes

- Principles should be universally applicable, not specific to one feature
- Focus on patterns that prevent bugs or improve maintainability
- Keep each principle to one line with inline code example
- Group related principles under clear category headings
- Aim for actionable rules that can be followed in future development
- Use AskUserQuestion if focus instructions are ambiguous or unclear
