---
name: ms:update
description: Check for updates and install latest Mindsystem version
allowed-tools: [Bash, AskUserQuestion]
---

<objective>
Check installed Mindsystem version against npm registry and offer to update if behind. Detects local vs global install mode automatically.

Run when the user wants to update Mindsystem or check if a newer version is available.
</objective>

<process>

<step name="detect_version_and_mode">
Detect installed version and install mode:

```bash
# Check local first (takes precedence)
cat ./.claude/mindsystem/VERSION 2>/dev/null
```

```bash
# If not found, check global (respect CLAUDE_CONFIG_DIR)
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/mindsystem/VERSION" 2>/dev/null
```

- If local VERSION exists → `mode = "local"`
- Else if global VERSION exists → `mode = "global"`
- If neither found:

```
Mindsystem not installed. Run `npx mindsystem-cc` to install.
```

STOP.

Store the installed version (strip whitespace).
</step>

<step name="fetch_latest_version">
Fetch latest version from npm:

```bash
npm view mindsystem-cc version
```

If the command fails (network error, timeout), report the error and STOP.
</step>

<step name="compare_versions">
Compare installed version against latest:

- If installed == latest → "You are using the latest version (v{installed})." STOP.
- If installed > latest → "Development version (v{installed} > v{latest})." STOP.
- If installed < latest → proceed to next step.

Use semantic version comparison (split on `.`, compare major/minor/patch numerically).
</step>

<step name="ask_user">
Use AskUserQuestion:

- header: "Update"
- question: "Update available: v{installed} → v{latest}. Update now?"
- options:
  - "Update" — install latest version
  - "Skip" — leave current version

If "Skip" → STOP.
</step>

<step name="run_install">
Build the install command based on mode:

- Global: `npx mindsystem-cc@latest --force --global`
- Local: `npx mindsystem-cc@latest --force --local`

Also pass `--config-dir "$CLAUDE_CONFIG_DIR"` if `CLAUDE_CONFIG_DIR` is set.

Run the command. If exit code != 0, show the error output and STOP.
</step>

<step name="post_update_guidance">
Show success message:

```
Updated to v{latest}.

Restart Claude Code for changes to take effect, then run `/ms:doctor` to check for breaking changes.
```
</step>

</process>

<success_criteria>
- [ ] Post-update message includes restart and /ms:doctor instructions
- [ ] Passes correct --force and mode flags to installer
- [ ] Skips update when already on latest or development version
- [ ] Reports "not installed" when no VERSION file exists
- [ ] Handles npm fetch failures gracefully
</success_criteria>
