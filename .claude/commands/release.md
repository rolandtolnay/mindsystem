---
name: release
description: Auto-version based on commits, update changelog, tag, push, and publish to npm
argument-hint: "[major|minor|patch|X.Y.Z]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Analyze changes since last release, determine version bump (or use explicit version), update CHANGELOG.md, create release commits, tag the version, push to remote, and publish to npm.

**SemVer rules applied:**
- `major` — Breaking changes (BREAKING CHANGE in commit, or explicit)
- `minor` — New features (`feat:` commits)
- `patch` — Bug fixes, docs, refactors, chores

Run with no arguments to auto-detect, or specify `major`, `minor`, `patch`, or explicit version.
</objective>

<context>
$ARGUMENTS
</context>

<process>

<step name="get_current_version">
Read current version from package.json:

```bash
CURRENT=$(grep '"version"' package.json | sed 's/.*: "\(.*\)".*/\1/')
echo "Current version: $CURRENT"
```
</step>

<step name="review_changes">
Show uncommitted changes:

```bash
git status
git diff --stat
git diff --stat --cached
```
</step>

<step name="commit_changes">
Stage and commit changes with conventional commit format.

**Commit types:**
- `feat(scope): description` — New feature
- `fix(scope): description` — Bug fix
- `docs(scope): description` — Documentation
- `refactor(scope): description` — Code cleanup
- `chore(scope): description` — Config/dependencies
- `BREAKING CHANGE:` in body — Breaking change

**Rules:**
- Group related changes into logical commits
- Use descriptive scope (e.g., `mindsystem`, `agent`, `command`)
- Stage files individually, never `git add .`
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` in commit body
</step>

<step name="analyze_commits">
After committing, analyze commits since last version tag to determine bump:

```bash
# Find commits since last version
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~10")..HEAD
```

**Determine version bump:**
1. If any commit contains `BREAKING CHANGE:` → MAJOR
2. If any commit starts with `feat` → MINOR
3. Otherwise → PATCH

If $ARGUMENTS provided:
- `major`, `minor`, `patch` → use that bump type
- `X.Y.Z` → use that exact version
</step>

<step name="calculate_new_version">
Calculate and store new version based on current + bump type:

```
MAJOR bump → (X+1).0.0
MINOR bump → X.(Y+1).0
PATCH bump → X.Y.(Z+1)
```

Store result as `VERSION` variable for all subsequent steps. Announce the new version before proceeding.
</step>

<step name="gather_ticket_context">
Extract ticket references (e.g., `[MIN-123]`, `MIN-123`) from commit messages and bodies since last tag.

```bash
git log --format="%s%n%b" $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~10")..HEAD
```

For each unique ticket ID found, fetch it via the Linear skill CLI:

```bash
uv run ~/.claude/skills/linear/scripts/linear.py get <ID>
```

Use each ticket's title and description (especially Problem/Solution sections) to understand the user-facing intent behind each change.

Skip this step if no ticket references are found.
</step>

<step name="generate_changelog">
Read commits since last version and generate changelog entries, using ticket context from the previous step.

**Relevance filter — include only core Mindsystem changes:**

| Include | Omit |
|---------|------|
| New/changed commands, workflows, agents | Prompt quality guide updates (reference material) |
| Template or reference changes that alter system behavior | Flutter-specific skill changes |
| Script changes | Documentation-only changes to CLAUDE.md or ms-meta |
| New features, bug fixes, refactors to core system | Standalone utility scripts |

When uncertain, include. The user can remove during confirmation.

**Changelog format (Keep a Changelog):**

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
### Changed
### Fixed
### Removed
```

**Writing rules:**
- Group by type (Added, Changed, Fixed, Removed). Skip empty sections.
- One bullet per logical change. Consolidate iterative commits on the same feature into one entry reflecting the **final state**.
- Write from user perspective: what changed and why it benefits them. Use ticket Problem/Solution context when available.
- Never include ticket identifiers (e.g., `[MIN-86]`) in changelog lines
</step>

<step name="confirm_changelog">
Present the changelog as regular text output first, then collect the decision separately. Do NOT put changelog content inside AskUserQuestion — text output has no truncation limits and renders full markdown.

**Output format** (as regular text, before the question):

```
Here's the proposed changelog for v{VERSION}:

{full changelog section}

---

**Omitted from changelog:**
- `abc1234 docs(ms-meta): update prompt quality principles` — reference material, no behavioral change
- `def5678 docs(flutter-skill): add animation patterns` — Flutter-specific, not core system
```

**Then** use AskUserQuestion with short options only — no changelog content repeated:

> "Approve this changelog for v{VERSION}?"
> 1. **Approve** — Insert into CHANGELOG.md and proceed
> 2. **Edit** — Provide corrections first

Do NOT write to CHANGELOG.md until the user approves.
</step>

<step name="update_changelog">
Read CHANGELOG.md and insert new version section after `## [Unreleased]`.

Update the comparison links at the bottom:
- Change `[Unreleased]` link to compare from new version
- Add new version link

Example link format:
```markdown
[Unreleased]: https://github.com/owner/repo/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/owner/repo/releases/tag/vX.Y.Z
```
</step>

<step name="commit_changelog">
Commit the changelog update:

```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for v$VERSION"
```
</step>

<step name="bump_package_version">
Update package.json with new version:

```bash
sed -i '' "s/\"version\": \"$CURRENT\"/\"version\": \"$VERSION\"/" package.json
grep '"version"' package.json
```
</step>

<step name="version_commit">
Create the version commit (Mindsystem convention: version number only):

```bash
git add package.json
git commit -m "$VERSION"
```
</step>

<step name="create_tag">
Create annotated git tag for the release:

```bash
git tag -a "v$VERSION" -m "Release v$VERSION"
```
</step>

<step name="push_to_remote">
Push commits and tag to remote:

```bash
git push origin HEAD
git push origin "v$VERSION"
```
</step>

<step name="show_summary">
Show the commit log via git, then output the rest as text (avoid echoing npm commands in bash — triggers security hooks):

```bash
git log --oneline $(git describe --tags --abbrev=0~1 2>/dev/null || echo "HEAD~5")..HEAD
```

Then output as text:

```
Release v{VERSION} complete. Tag: v{VERSION}

To publish: `npm publish`
```
</step>

</process>

<success_criteria>
- [ ] Ticket context fetched for commits referencing Linear tickets and used to inform changelog entries
- [ ] Relevance filter applied — peripheral changes (prompt guides, Flutter skills, docs-only) omitted from changelog
- [ ] Omitted commits listed with reasons in the confirmation message
- [ ] Changelog entries written from user perspective (benefit, not implementation detail)
- [ ] No ticket identifiers in changelog lines
- [ ] CHANGELOG.md not written until user approves
</success_criteria>
