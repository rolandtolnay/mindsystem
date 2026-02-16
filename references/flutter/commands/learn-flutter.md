---
description: Learn from recent Flutter/Dart code changes and update the remote coding principles gist. Use after completing Flutter implementation work.
argument-hint: [focus_instructions] [number] [commit_sha]
allowed-tools: Bash, Read, Grep, Glob, Write
---

<objective>
Extract Flutter/Dart coding principles from code changes and append them to the remote GitHub Gist.
</objective>

<context>
Arguments: $ARGUMENTS

Git status (run `git status --porcelain` and `git diff --stat`):
```
$( git status --porcelain 2>/dev/null | head -20 )
$( git diff --stat 2>/dev/null | tail -5 )
```
</context>

<embedded_knowledge>
<gist_details>
- Gist ID: `edf9ea7d5adf218f45accb3411f0627c`
- File name: `flutter-code-quality-guidelines.md`
- Always use `gh api` for gist operations — never WebFetch (it summarizes instead of returning raw content)
</gist_details>

<categories>
Match principles to these categories (use existing section names exactly):
- Widget Structure
- State & Providers
- Sealed Classes
- Domain & Business Logic
- Collections
- Forms & Input
- Hooks
- Model & Data
- Widget API
- Animation
- Theme & Styling
- Extensions
- Project Structure
- Localization
- Anti-Patterns (for negative patterns to flag)
</categories>

<format_rules>
Follow LLM-optimized documentation format:

1. **Terseness over explanation**
   - Single-line rules; no paragraphs
   - No "why" explanations
   - Remove noise words: no `IMPORTANT:`, `YOU MUST`, `Please ensure`

2. **Concrete syntax inline**
   - Show code pattern directly: `Early return: if (items.isEmpty) return const SizedBox.shrink();`
   - Arrow notation for transformations: `.toList()..sort()` → `.sorted()`
   - Backticks for identifiers: `useState`, `AsyncValue.guard()`

3. **Flat hierarchy**
   - Rules as bullet points under category headers
   - No nested subcategories
</format_rules>

<example_principles>
```markdown
## State & Providers
- Loading flags from provider state: `final isLoading = actionProvider.isLoading` not `useState<bool>(false)`

## Collections
- `.sorted((a, b) => ...)` not `.toList()..sort()`

## Anti-Patterns (flag these)
- `_handleAction(ref, controller, user, state)` with 4+ params (move inside build)
```
</example_principles>
</embedded_knowledge>

<process>
<step name="preflight_checks">
## 1. Pre-flight Checks

1. Verify GitHub CLI is authenticated:
   ```bash
   gh auth status
   ```
   If not authenticated, stop with: "GitHub CLI not authenticated. Run `gh auth login` first."

2. Verify git repository exists:
   ```bash
   git rev-parse --git-dir
   ```
   If not a repo, stop with: "Not a git repository."
</step>

<step name="parse_arguments">
## 2. Parse Arguments

Analyze `$ARGUMENTS` to identify:
- **Commit SHA**: 7+ character hex string, verify with `git rev-parse --verify <sha>^{commit}` (if fails, treat as focus text)
- **Explicit count**: Standalone number (1-10)
- **Focus instructions**: Remaining text describes areas to emphasize

Examples:
- `learn-flutter` → uncommitted changes, auto count
- `learn-flutter 5` → uncommitted changes, exactly 5 principles
- `learn-flutter state management` → focus on state management
- `learn-flutter a1b2c3d` → analyze specific commit
- `learn-flutter 3 error handling` → 3 principles about error handling
</step>

<step name="fetch_current_gist">
## 3. Fetch Current Gist

Fetch the gist content using `gh api`:

```bash
gh api /gists/edf9ea7d5adf218f45accb3411f0627c \
  --jq '.files["flutter-code-quality-guidelines.md"].content'
```

Parse the content to:
1. Identify existing categories and their rules
2. Build a list of existing principles for duplicate detection
3. Understand the current structure

Duplicate detection: normalize candidates by trimming whitespace and comparing core content (ignore minor formatting differences).
</step>

<step name="analyze_changes">
## 4. Analyze Code Changes

**If commit SHA provided:**
```bash
git show -m --format="%s%n%n%b" <commit_sha>
```

**Otherwise (uncommitted changes):**
```bash
git diff --cached  # staged changes
git diff           # unstaged changes
```

Focus on:
- Refactoring patterns
- Style improvements
- Architectural decisions
- Areas mentioned in focus instructions
</step>

<step name="determine_count">
## 5. Determine Principle Count

**If explicit count provided:** Use that number (max 10).

**Otherwise, calculate based on:**
- Size of diff: small (1-3), medium (3-5), large (5-8)
- Diversity of patterns
- Focus instruction scope (narrow → fewer; broad → more)

Never exceed 10 principles per invocation.
</step>

<step name="extract_principles">
## 6. Extract Principles

Compare before/after in each hunk. Identify:
- Refactoring transformations (old pattern → new pattern)
- New API usage or library patterns introduced
- Structural improvements (file organization, naming, decomposition)

Prioritize:
1. Areas mentioned in focus instructions
2. Reusable patterns, not implementation-specific details
3. Patterns not already in the gist (skip duplicates)

Consider: structure, naming, error handling, state management, API design, collections, widgets.
</step>

<step name="format_principles">
## 7. Format Principles

Format each principle following the embedded format rules:

```markdown
- Terse rule with `inline code` example
- Transformation: `bad pattern` → `good pattern`
- Concrete syntax showing what to do
```

No emphasis markers. No explanations. One line per rule.

Match to the closest existing category from the gist.
</step>

<step name="update_gist">
## 8. Update Gist

1. Write the complete updated gist content to a temp file (e.g., `/tmp/flutter-gist-update.md`)
2. Build a JSON payload with `jq` and pipe to `gh api` via `--input -`:

```bash
jq -n --rawfile content /tmp/flutter-gist-update.md \
  '{"files":{"flutter-code-quality-guidelines.md":{"content":$content}}}' | \
  gh api -X PATCH /gists/edf9ea7d5adf218f45accb3411f0627c --input -
```

**Do NOT use** `-f "files[...][content]=@/path"` — the `@` file reference does not expand with `gh api -f` and uploads the literal string `@/path` instead.

Insert new principles under their matching category sections.
If a principle doesn't fit existing categories, add to the closest match.
3. Clean up: `rm /tmp/flutter-gist-update.md`
</step>

<step name="verify_update">
## 9. Verify Update

1. Re-fetch the gist content via `gh api`:
   ```bash
   gh api /gists/edf9ea7d5adf218f45accb3411f0627c \
     --jq '.files["flutter-code-quality-guidelines.md"].content'
   ```
2. Grep the output for a distinctive keyword from each new principle to confirm presence
3. Report what was added:
   - Number of principles added
   - Which categories were updated
   - Any principles skipped as duplicates
</step>
</process>

<success_criteria>
- [ ] Format follows LLM-optimized rules (terse, inline code, no emphasis markers)
- [ ] No duplicate principles added
- [ ] Gist updated via `jq --rawfile` piped to `gh api --input -` (not `-f files[...]=@path`)
- [ ] Update verified by re-fetching via `gh api --jq` and grepping for new content
- [ ] Gist fetched and updated via `gh api` (not WebFetch)
</success_criteria>
