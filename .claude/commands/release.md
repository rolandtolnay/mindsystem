---
name: release
description: Commit changes and bump version for release
arguments: version
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

<objective>
Commit staged/unstaged changes with proper conventional commit messages, then bump package.json version and create a version commit.

Use when ready to release a new version of the fork.
</objective>

<process>

<step name="validate_version">
Version from $ARGUMENTS (required). Must be valid semver.

```bash
VERSION="$ARGUMENTS"
if [ -z "$VERSION" ]; then
  echo "Error: Version required. Usage: /release 2.0.0"
  exit 1
fi

# Basic semver validation
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$'; then
  echo "Error: Invalid semver format. Use X.Y.Z (e.g., 2.0.0)"
  exit 1
fi

echo "Target version: $VERSION"
```
</step>

<step name="review_changes">
Show what will be committed:

```bash
git status
git diff --stat
git diff --stat --cached
```

Review the changes. Group them logically for commit messages.
</step>

<step name="commit_changes">
Stage and commit changes with conventional commit format.

**Commit message conventions:**
- `feat(scope): description` — New feature
- `fix(scope): description` — Bug fix
- `docs(scope): description` — Documentation
- `refactor(scope): description` — Code cleanup
- `chore(scope): description` — Config/dependencies

**Rules:**
- Group related changes into logical commits
- Use descriptive scope (e.g., `gsd`, `agent`, `command`)
- Stage files individually, never `git add .`
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` in commit body

Example for adding a new agent and command:
```bash
git add agents/gsd-plan-checker.md
git commit -m "$(cat <<'EOF'
feat(agent): add plan-checker for pre-execution verification

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git add commands/gsd/check-phase.md
git commit -m "$(cat <<'EOF'
feat(command): add check-phase slash command

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```
</step>

<step name="bump_version">
Update package.json with new version:

```bash
# Read current version
CURRENT=$(grep '"version"' package.json | sed 's/.*: "\(.*\)".*/\1/')
echo "Current version: $CURRENT"
echo "New version: $VERSION"

# Update package.json
sed -i '' "s/\"version\": \"$CURRENT\"/\"version\": \"$VERSION\"/" package.json

# Verify
grep '"version"' package.json
```
</step>

<step name="version_commit">
Create the version commit (follows GSD convention of version-only commits):

```bash
git add package.json
git commit -m "$VERSION"
```
</step>

<step name="verify">
Show final state:

```bash
echo "=== Release $VERSION complete ==="
git log --oneline -5
echo ""
echo "To publish: npm publish"
echo "To push: git push origin HEAD"
```
</step>

</process>

<examples>
**Release version 2.0.0:**
```
/release 2.0.0
```

**Release patch version:**
```
/release 2.0.1
```
</examples>
