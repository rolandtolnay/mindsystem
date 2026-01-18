---
name: release
description: Auto-version based on commits, update changelog, and release
arguments: "[major|minor|patch|X.Y.Z]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

<objective>
Analyze changes since last release, determine version bump (or use explicit version), update CHANGELOG.md, and create release commits.

**SemVer rules applied:**
- `major` — Breaking changes (BREAKING CHANGE in commit, or explicit)
- `minor` — New features (`feat:` commits)
- `patch` — Bug fixes, docs, refactors, chores

Run with no arguments to auto-detect, or specify `major`, `minor`, `patch`, or explicit version.
</objective>

<process>

<step name="get_current_version">
Read current version from package.json:

```bash
CURRENT=$(grep '"version"' package.json | sed 's/.*: "\(.*\)".*/\1/')
echo "Current version: $CURRENT"
```

Parse into components for incrementing.
</step>

<step name="review_changes">
Show uncommitted changes:

```bash
git status
git diff --stat
git diff --stat --cached
```

Review and understand what needs to be committed.
</step>

<step name="commit_changes">
Stage and commit changes with conventional commit format.

**Commit types (determines version bump):**
- `feat(scope): description` — New feature → triggers MINOR
- `fix(scope): description` — Bug fix → triggers PATCH
- `docs(scope): description` — Documentation → triggers PATCH
- `refactor(scope): description` — Code cleanup → triggers PATCH
- `chore(scope): description` — Config/dependencies → triggers PATCH
- `BREAKING CHANGE:` in body — Breaking change → triggers MAJOR

**Rules:**
- Group related changes into logical commits
- Use descriptive scope (e.g., `gsd`, `agent`, `command`)
- Stage files individually, never `git add .`
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` in commit body

Create all necessary commits before proceeding.
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
Calculate new version based on current + bump type:

```
Current: X.Y.Z
- MAJOR bump → (X+1).0.0
- MINOR bump → X.(Y+1).0
- PATCH bump → X.Y.(Z+1)
```

Announce the new version before proceeding.
</step>

<step name="generate_changelog">
Read commits since last version and generate changelog entries.

**Changelog format (Keep a Changelog):**

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features (from `feat:` commits)

### Changed
- Changes to existing functionality (from `refactor:`, behavior changes)

### Fixed
- Bug fixes (from `fix:` commits)

### Removed
- Removed features (if any)
```

**Rules:**
- Group by type (Added, Changed, Fixed, Removed)
- One bullet per logical change
- Write from user perspective, not implementation details
- Include scope context where helpful
- Skip empty sections
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
Create the version commit (GSD convention: version number only):

```bash
git add package.json
git commit -m "$VERSION"
```
</step>

<step name="show_summary">
Display release summary:

```bash
echo "=== Release $VERSION complete ==="
echo ""
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo "$CURRENT")..HEAD
echo ""
echo "To push: git push origin HEAD"
echo "To tag: git tag v$VERSION && git push origin v$VERSION"
echo "To publish: npm publish"
```
</step>

</process>

<examples>
**Auto-detect version bump:**
```
/release
```
Analyzes commits, determines bump type, updates changelog.

**Force minor bump:**
```
/release minor
```

**Force specific version:**
```
/release 2.1.0
```
</examples>
