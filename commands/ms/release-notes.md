---
name: ms:release-notes
description: Show full Mindsystem release notes with update status
allowed-tools: [Read, Bash, Task]
---

<objective>
Display Mindsystem release notes from 2.0.0 through installed version in clean bullet format, oldest first, with update status at the end.

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

<step name="fetch_and_display">
Spawn a Haiku general-purpose subagent with `model: "haiku"` to fetch, parse, and display the changelog.

The subagent prompt must include the installed version and instruct it to:

1. **Fetch changelog** — Run `curl -sfL https://raw.githubusercontent.com/rolandtolnay/mindsystem/main/CHANGELOG.md`. If curl fails, fall back to reading `~/.claude/mindsystem/CHANGELOG.md`.

2. **Parse versions** — Extract all `## [X.Y.Z]` entries from 2.0.0 onward (skip `## [Unreleased]` and `## [1.x]`).

3. **Filter by installed version** — Only include versions where X.Y.Z is less than or equal to the installed version (semver comparison). Also extract the latest version from the changelog for the status line.

4. **Convert to clean bullet format:**
   ```
   Version X.Y.Z:
     - Added feature description
     - Changed behavior description
     - Removed old thing
     - Fixed bug description
   ```
   - Combine all `### Added`, `### Changed`, `### Removed`, `### Fixed` items under a single version header
   - Prefix each item with its category: "Added", "Changed", "Removed", "Fixed"
   - Strip bold markers from item text
   - One bullet per changelog line item
   - Blank line between versions
   - Skip `### Migration` sections

5. **Output oldest first, newest last** — Display versions starting from 2.0.0 up to the installed version.

6. **End with update status line:**
   - If installed < latest: `Update available: vINSTALLED -> vLATEST. Run 'npx mindsystem-cc@latest' to update.`
   - If installed == latest: `You are using the latest version (vINSTALLED).`
   - If installed > latest: `You are ahead of the latest release (vINSTALLED > vLATEST) — development version.`

Output the subagent's response directly to the user.
</step>

</process>

<success_criteria>
- [ ] Delegated to Haiku subagent (no main-agent token waste)
- [ ] Only versions ≤ installed version displayed
- [ ] Versions displayed oldest first, newest last
- [ ] Clean bullet format with category prefixes
- [ ] Update status shown as single line at end
</success_criteria>
