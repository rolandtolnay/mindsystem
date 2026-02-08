---
description: Sync Flutter reference docs and optionally install Flutter-specific Claude Code skills from mindsystem
allowed-tools: [Bash, AskUserQuestion]
---

<objective>
Fetch the latest Flutter reference files from the mindsystem GitHub repo and the code quality gist, then write them to `docs/` in the current project. Optionally install Flutter-specific Claude Code skills to `.claude/skills/`.

Running this command again overwrites all files with the latest versions.

This command is portable: copy it into any Flutter project's `.claude/commands/` to use.
</objective>

<process>

<step name="sync_docs">
Run this script via Bash and present the output to the user:

```bash
set -e

REPO_API="https://api.github.com/repos/rolandtolnay/mindsystem/contents/references/flutter"
RAW_BASE="https://raw.githubusercontent.com/rolandtolnay/mindsystem/main/references/flutter"
GIST_URL="https://gist.githubusercontent.com/rolandtolnay/edf9ea7d5adf218f45accb3411f0627c/raw/flutter-code-quality-guidelines.md"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required. Install with: brew install jq"; exit 1; }

mkdir -p docs/patterns

# Record checksums of existing files
CHECKSUMS=$(mktemp)
for f in docs/*.md docs/patterns/*.md; do
  [ -f "$f" ] && echo "$(md5 -q "$f" 2>/dev/null || md5sum "$f" | cut -d' ' -f1) $f" >> "$CHECKSUMS"
done

# Discover files via GitHub API
ROOT_FILES=$(curl -sf "$REPO_API" | jq -r '.[] | select(.type=="file" and (.name | endswith(".md")) and .name != "code_quality.md") | .name')
PATTERN_FILES=$(curl -sf "$REPO_API/patterns" | jq -r '.[] | select(.type=="file" and (.name | endswith(".md"))) | .name')

# Download root files
for f in $ROOT_FILES; do
  curl -sf "$RAW_BASE/$f" -o "docs/$f"
done

# Download pattern files
for f in $PATTERN_FILES; do
  curl -sf "$RAW_BASE/patterns/$f" -o "docs/patterns/$f"
done

# Download gist
curl -sf "$GIST_URL" -o "docs/code-quality.md"

# Diff report
NEW=0; UPDATED=0; UNCHANGED=0
for f in docs/*.md docs/patterns/*.md; do
  [ -f "$f" ] || continue
  NEW_HASH=$(md5 -q "$f" 2>/dev/null || md5sum "$f" | cut -d' ' -f1)
  OLD_HASH=$(grep -F " $f" "$CHECKSUMS" | head -1 | cut -d' ' -f1)
  if [ -z "$OLD_HASH" ]; then
    echo "  + $f (new)"
    NEW=$((NEW + 1))
  elif [ "$OLD_HASH" != "$NEW_HASH" ]; then
    echo "  ~ $f (updated)"
    UPDATED=$((UPDATED + 1))
  else
    echo "  = $f (unchanged)"
    UNCHANGED=$((UNCHANGED + 1))
  fi
done

rm -f "$CHECKSUMS"
echo ""
echo "Sync complete: $NEW new, $UPDATED updated, $UNCHANGED unchanged"
```
</step>

<step name="offer_skills">
Discover available Flutter skills by running:

```bash
curl -sf "https://api.github.com/repos/rolandtolnay/mindsystem/contents/skills" | jq -r '.[] | select(.type=="dir" and (.name | startswith("flutter-"))) | .name'
```

If no skills found, stop here.

Check which of the discovered skills already exist locally:

```bash
for skill in <discovered_skill_names>; do
  [ -d ".claude/skills/$skill" ] && echo "$skill"
done
```

Use AskUserQuestion to ask the user. Adapt the question based on whether collisions exist:

- **No existing skills:** "Install Flutter-specific Claude Code skills to `.claude/skills/`?" with the discovered skill names listed. Options: "Yes, install all" / "No, skip"
- **Some skills already exist:** "Install Flutter-specific Claude Code skills to `.claude/skills/`? These already exist and will be overwritten: {existing_names}" with both new and existing skill names listed. Options: "Yes, install and overwrite" / "No, skip"

If user declines, stop here.
</step>

<step name="install_skills">
If the user accepted, run this script via Bash and present the output:

```bash
set -e

SKILLS_API="https://api.github.com/repos/rolandtolnay/mindsystem/contents/skills"
SKILLS_RAW="https://raw.githubusercontent.com/rolandtolnay/mindsystem/main/skills"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required. Install with: brew install jq"; exit 1; }

NEW=0; UPDATED=0; UNCHANGED=0

download_file() {
  local url="$1" dest="$2"
  local old_hash=""
  [ -f "$dest" ] && old_hash=$(md5 -q "$dest" 2>/dev/null || md5sum "$dest" | cut -d' ' -f1)
  curl -sf "$url" -o "$dest"
  local new_hash=$(md5 -q "$dest" 2>/dev/null || md5sum "$dest" | cut -d' ' -f1)
  if [ -z "$old_hash" ]; then
    echo "  + $dest (new)"
    NEW=$((NEW + 1))
  elif [ "$old_hash" != "$new_hash" ]; then
    echo "  ~ $dest (updated)"
    UPDATED=$((UPDATED + 1))
  else
    echo "  = $dest (unchanged)"
    UNCHANGED=$((UNCHANGED + 1))
  fi
}

# Discover Flutter skills
FLUTTER_SKILLS=$(curl -sf "$SKILLS_API" | jq -r '.[] | select(.type=="dir" and (.name | startswith("flutter-"))) | .name')

if [ -z "$FLUTTER_SKILLS" ]; then
  echo "No Flutter skills found."
  exit 0
fi

for skill in $FLUTTER_SKILLS; do
  CONTENTS=$(curl -sf "$SKILLS_API/$skill")
  mkdir -p ".claude/skills/$skill"

  # Download root files
  for f in $(echo "$CONTENTS" | jq -r '.[] | select(.type=="file") | .name'); do
    download_file "$SKILLS_RAW/$skill/$f" ".claude/skills/$skill/$f"
  done

  # Download subdirectories (one level deep)
  for subdir in $(echo "$CONTENTS" | jq -r '.[] | select(.type=="dir") | .name'); do
    mkdir -p ".claude/skills/$skill/$subdir"
    for f in $(curl -sf "$SKILLS_API/$skill/$subdir" | jq -r '.[] | select(.type=="file") | .name'); do
      download_file "$SKILLS_RAW/$skill/$subdir/$f" ".claude/skills/$skill/$subdir/$f"
    done
  done
done

echo ""
echo "Skills installed: $NEW new, $UPDATED updated, $UNCHANGED unchanged"
```
</step>

</process>

<success_criteria>
- All discovered doc files written to `docs/` and `docs/patterns/`
- Gist written to `docs/code-quality.md`
- No hardcoded file lists — new files added to the repo are picked up automatically
- Doc diff report printed showing new/updated/unchanged counts
- User offered skill installation via AskUserQuestion after doc sync
- If accepted, all `flutter-*` skills from `skills/` installed to `.claude/skills/` with diff report
</success_criteria>
