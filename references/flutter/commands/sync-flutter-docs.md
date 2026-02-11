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

# Discover and download root files (exclude code_quality.md — fetched from gist instead)
curl -sf "$REPO_API" | jq -r '.[] | select(.type=="file" and (.name | endswith(".md")) and (.name | test("^code_quality") | not)) | .name' | while IFS= read -r f; do
  [ -z "$f" ] && continue
  curl -sf "$RAW_BASE/$f" -o "docs/$f"
done

# Discover and download pattern files
curl -sf "$REPO_API/patterns" | jq -r '.[] | select(.type=="file" and (.name | endswith(".md"))) | .name' | while IFS= read -r f; do
  [ -z "$f" ] && continue
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

Check whether each discovered skill already exists in the **user scope** (`~/.claude/skills/`) and matches the remote version. Run this script, replacing `<discovered_skill_names>` with the actual skill names:

```bash
set -e

SKILLS_API="https://api.github.com/repos/rolandtolnay/mindsystem/contents/skills"
SKILLS_RAW="https://raw.githubusercontent.com/rolandtolnay/mindsystem/main/skills"
USER_SKILLS="$HOME/.claude/skills"
REMOTE_TMP=$(mktemp -d)
RESULTS=$(mktemp)
trap "rm -rf $REMOTE_TMP $RESULTS" EXIT

for skill in <discovered_skill_names>; do
  CONTENTS=$(curl -sf "$SKILLS_API/$skill")
  mkdir -p "$REMOTE_TMP/$skill"

  # Download root files
  for f in $(echo "$CONTENTS" | jq -r '.[] | select(.type=="file") | .name'); do
    curl -sf "$SKILLS_RAW/$skill/$f" -o "$REMOTE_TMP/$skill/$f"
  done

  # Download subdirectory files
  for subdir in $(echo "$CONTENTS" | jq -r '.[] | select(.type=="dir") | .name'); do
    mkdir -p "$REMOTE_TMP/$skill/$subdir"
    for f in $(curl -sf "$SKILLS_API/$skill/$subdir" | jq -r '.[] | select(.type=="file") | .name'); do
      curl -sf "$SKILLS_RAW/$skill/$subdir/$f" -o "$REMOTE_TMP/$skill/$subdir/$f"
    done
  done

  # Compare with user scope
  if [ -d "$USER_SKILLS/$skill" ] && diff -rq "$REMOTE_TMP/$skill" "$USER_SKILLS/$skill" >/dev/null 2>&1; then
    echo "user_match:$skill" >> "$RESULTS"
  elif [ -d ".claude/skills/$skill" ]; then
    echo "project_exists:$skill" >> "$RESULTS"
  else
    echo "new:$skill" >> "$RESULTS"
  fi
done

cat "$RESULTS"
```

Interpret the results:

- **All skills are `user_match`:** Print "Skipped skill installation — all Flutter skills already available in user scope (`~/.claude/skills/`)." and **stop here**. Do NOT use AskUserQuestion.
- **Some skills are `user_match`, some are not:** Note which skills were skipped (available in user scope), then offer to install only the remaining skills using AskUserQuestion. Adapt the question based on whether any remaining skills already exist in project scope (`project_exists`):
  - None in project scope: "Install Flutter skills to `.claude/skills/`? {remaining_names}. (Skipped {skipped_names} — already in user scope)" Options: "Yes, install" / "No, skip"
  - Some in project scope: "Install Flutter skills to `.claude/skills/`? These will be overwritten: {project_existing_names}. (Skipped {skipped_names} — already in user scope)" Options: "Yes, install and overwrite" / "No, skip"
- **No skills are `user_match`:** Offer all skills using AskUserQuestion, checking project scope for overwrite warnings:
  - No existing project skills: "Install Flutter-specific Claude Code skills to `.claude/skills/`?" with skill names listed. Options: "Yes, install all" / "No, skip"
  - Some exist in project scope: "Install Flutter-specific Claude Code skills to `.claude/skills/`? These already exist and will be overwritten: {existing_names}" Options: "Yes, install and overwrite" / "No, skip"

If user declines, stop here.
</step>

<step name="install_skills">
If the user accepted, run this script via Bash and present the output. Replace `<skills_to_install>` with only the skill names that need installation (i.e. the ones that were NOT `user_match` from the previous step):

```bash
set -e

SKILLS_API="https://api.github.com/repos/rolandtolnay/mindsystem/contents/skills"
SKILLS_RAW="https://raw.githubusercontent.com/rolandtolnay/mindsystem/main/skills"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required. Install with: brew install jq"; exit 1; }

NEW=0; UPDATED=0; UNCHANGED=0
COUNTS=$(mktemp)
echo "0 0 0" > "$COUNTS"

dl() {
  local url="$1" dest="$2"
  local old_hash=""
  [ -f "$dest" ] && old_hash=$(md5 -q "$dest" 2>/dev/null || md5sum "$dest" | cut -d' ' -f1)
  curl -sf "$url" -o "$dest"
  local new_hash=$(md5 -q "$dest" 2>/dev/null || md5sum "$dest" | cut -d' ' -f1)
  read n u uc < "$COUNTS"
  if [ -z "$old_hash" ]; then
    echo "  + $dest (new)"
    n=$((n + 1))
  elif [ "$old_hash" != "$new_hash" ]; then
    echo "  ~ $dest (updated)"
    u=$((u + 1))
  else
    echo "  = $dest (unchanged)"
    uc=$((uc + 1))
  fi
  echo "$n $u $uc" > "$COUNTS"
}

# Only install skills not already covered by user scope
FLUTTER_SKILLS="<skills_to_install>"

if [ -z "$FLUTTER_SKILLS" ]; then
  echo "No skills to install."
  rm -f "$COUNTS"
  exit 0
fi

for skill in $FLUTTER_SKILLS; do
  [ -z "$skill" ] && continue
  CONTENTS=$(curl -sf "$SKILLS_API/$skill")
  mkdir -p ".claude/skills/$skill"

  # Download root files
  for f in $(echo "$CONTENTS" | jq -r '.[] | select(.type=="file") | .name'); do
    dl "$SKILLS_RAW/$skill/$f" ".claude/skills/$skill/$f"
  done

  # Download subdirectories (one level deep)
  for subdir in $(echo "$CONTENTS" | jq -r '.[] | select(.type=="dir") | .name'); do
    mkdir -p ".claude/skills/$skill/$subdir"
    for f in $(curl -sf "$SKILLS_API/$skill/$subdir" | jq -r '.[] | select(.type=="file") | .name'); do
      dl "$SKILLS_RAW/$skill/$subdir/$f" ".claude/skills/$skill/$subdir/$f"
    done
  done
done

read NEW UPDATED UNCHANGED < "$COUNTS"
rm -f "$COUNTS"

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
- Skills in user scope (`~/.claude/skills/`) that match remote are skipped implicitly with a note — no AskUserQuestion for these
- User offered skill installation via AskUserQuestion only for skills NOT already matching in user scope
- If accepted, only non-user-scope skills installed to `.claude/skills/` with diff report
</success_criteria>
