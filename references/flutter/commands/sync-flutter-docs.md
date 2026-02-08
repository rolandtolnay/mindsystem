---
description: Sync Flutter reference docs and code quality guidelines from mindsystem into this project
allowed-tools: [Bash]
---

<objective>
Fetch the latest Flutter reference files from the mindsystem GitHub repo and the code quality gist, then write them to `docs/` in the current project. Running this command again overwrites all files with the latest versions.

This command is portable: copy it into any Flutter project's `.claude/commands/` to use.
</objective>

<process>
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
</process>

<success_criteria>
- All discovered files written to `docs/` and `docs/patterns/`
- Gist written to `docs/code-quality.md`
- No hardcoded file lists — new files added to the repo are picked up automatically
- Diff report printed showing new/updated/unchanged counts
</success_criteria>
