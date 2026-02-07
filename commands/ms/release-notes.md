---
name: ms:release-notes
description: Show full Mindsystem release notes with update status
allowed-tools: [Read, Bash, WebFetch]
---

<objective>
Display all Mindsystem release notes from 2.0.0 onward in clean bullet format, with update status at the end.

Use when: you want to see what Mindsystem has shipped across versions, or check if an update is available.
</objective>

<process>

<step name="get_installed_version">
Read installed version from VERSION file:

```bash
cat ~/.claude/mindsystem/VERSION 2>/dev/null
```

**If VERSION file missing:**
```
Installed version: Unknown

Your installation doesn't include version tracking.

Reinstall with: `npx mindsystem-cc`
```

STOP here if no VERSION file.
</step>

<step name="fetch_changelog">
Fetch latest CHANGELOG.md from GitHub:

Use WebFetch tool with:
- URL: `https://raw.githubusercontent.com/rolandtolnay/mindsystem/main/CHANGELOG.md`
- Prompt: "Return the full raw markdown content of this changelog file. Do not summarize or modify."

**If fetch fails:**
Fall back to local changelog:
```bash
cat ~/.claude/mindsystem/CHANGELOG.md 2>/dev/null
```

Note to user: "Showing local changelog (couldn't reach GitHub)."
</step>

<step name="parse_and_display">
From the changelog content:

1. **Extract latest version** — First `## [X.Y.Z]` entry after `## [Unreleased]`
2. **Parse all version entries from 2.0.0 onward** — Skip the collapsed `## [1.x]` section
3. **Convert to clean bullet format** — Transform Keep-a-Changelog sections into flat bullets:

**Format each version as:**
```
Version X.Y.Z:
  - Added feature description
  - Added another feature
  - Changed behavior description
  - Removed old thing
  - Fixed bug description
```

**Conversion rules:**
- Combine all `### Added`, `### Changed`, `### Removed`, `### Fixed` items under a single version header
- Prefix each item with its category: "Added", "Changed", "Removed", "Fixed"
- Strip bold markers from item text
- One bullet per changelog line item
- Blank line between versions
- Skip `### Migration` sections

Output all versions from newest to oldest, stopping before `## [1.x]`.
</step>

<step name="update_status">
After all release notes, add a single status line:

**Compare installed version with latest version from changelog.**

- **If behind:** `Update available: vINSTALLED -> vLATEST. Run 'npx mindsystem-cc@latest' to update.`
- **If current:** `You are using the latest version (vINSTALLED).`
- **If ahead:** `You are ahead of the latest release (vINSTALLED > vLATEST) — development version.`
</step>

</process>

<success_criteria>
- [ ] Installed version read from VERSION file
- [ ] Remote changelog fetched (or graceful fallback to local)
- [ ] All versions from 2.0.0 onward displayed in clean bullet format
- [ ] Update status shown as single line at end
</success_criteria>
