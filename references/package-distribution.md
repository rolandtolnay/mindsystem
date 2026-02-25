# Prompt Package Distribution

How to distribute prompt packages (skills, agents, commands, references) to users via GitHub. This is the authoritative implementation guide — give it to an agent building a new toolkit installer and it should have everything needed to implement autonomously.

## Core Principle

Clone once, symlink everywhere, `git pull` auto-updates all installations.

```bash
git clone <repo> ~/toolkits/my-toolkit
cd my-flutter-project && ~/toolkits/my-toolkit/install.js          # project scope
~/toolkits/my-toolkit/install.js --global                          # global scope
cd ~/toolkits/my-toolkit && git pull                                # updates everywhere
```

Symlink mode is the default. Copy mode (`--copy`) exists as a fallback for users who want to commit toolkit files into their project's git for team sharing.

---

## Repository Structure

```
my-toolkit/
├── install.js              # Standalone installer (Node.js, zero dependencies)
├── package.json            # npm metadata + test scripts
├── scripts/
│   └── test-install-regressions.sh
├── agents/                 # Subagent definitions (individual .md files)
│   └── my-agent.md
├── commands/               # Slash commands (individual .md files)
│   └── my-command.md
├── skills/                 # Skills (each is a directory)
│   ├── skill-a/
│   │   ├── SKILL.md
│   │   └── references/
│   └── skill-b/
│       └── SKILL.md
└── references/             # Reference docs (files and subdirectories)
    ├── guide.md
    └── patterns/
        └── common.md
```

Content directories (`agents/`, `commands/`, `skills/`, `references/`) map 1:1 to the target's `.claude/` structure. The installer recursively collects all files from these four directories.

---

## Installation Modes

### Link Mode (default)

Creates symlinks from the target `.claude/` back to the cloned repo.

- **Agents, commands, references**: Individual file-level symlinks (absolute paths).
- **Skills**: Directory-level symlinks per skill folder. This is critical because skills are multi-file directories (SKILL.md + supporting files) and directory symlinks keep them atomic.

```
~/.claude/
├── agents/my-agent.md → ~/toolkits/my-toolkit/agents/my-agent.md
├── commands/my-command.md → ~/toolkits/my-toolkit/commands/my-command.md
├── skills/skill-a → ~/toolkits/my-toolkit/skills/skill-a           # directory symlink
└── .my-toolkit.manifest.json
```

### Copy Mode (`--copy`)

Copies files into the target directory. Useful when:
- Users want to commit toolkit files into their project's git
- Windows without admin privileges (symlinks require elevated permissions)

Copy mode must handle a critical edge case: if the target already has directory symlinks for skills (from a previous link-mode install), writing files "into" that symlink would write into the source repo. The installer must detect and remove toolkit-owned skill symlinks before copying.

---

## Manifest System

The manifest is the single source of truth for what was installed and where. Stored as a dotfile directly in the target directory: `<target>/.<toolkit-name>.manifest.json`.

```json
{
  "version": "1.0.0",
  "installedAt": "2026-02-25T10:00:00.000Z",
  "mode": "link",
  "files": {
    "agents/my-agent.md": "a1b2c3d4e5f67890",
    "commands/my-command.md": "f0e1d2c3b4a59876",
    "skills/skill-a/SKILL.md": "1234567890abcdef",
    "skills/skill-a/references/guide.md": "fedcba0987654321"
  }
}
```

- **`version`**: Manifest schema version for future migrations.
- **`mode`**: The mode used for this installation (`link` or `copy`). Critical for detecting mode switches.
- **`files`**: Map of relative path → SHA-256 checksum (first 16 hex chars). In link mode, checksums come from the source file. In copy mode, checksums come from the installed copy.

### What the Manifest Enables

| Capability | How |
|---|---|
| **Orphan detection** | Files in old manifest but not in new file list → removed on next install |
| **Conflict detection** | Compare on-disk checksum vs manifest checksum to detect local edits |
| **Mode switch safety** | Detect copy→link transitions that would silently overwrite local edits |
| **Clean uninstall** | Delete every file listed in manifest, then the manifest itself |
| **Idempotent installs** | Skip files where on-disk matches source (no unnecessary writes) |

---

## Installation Pipeline

The installer runs a 9-phase pipeline. Each phase is a pure function operating on the results of prior phases.

### Phase 1: Determine Target

Resolve the target directory from CLI flags:
- Default: `<cwd>/.claude/`
- `--global`: `~/.claude/`

Derive the manifest path: `<target>/.<toolkit-name>.manifest.json`

Safety check: refuse to install into the toolkit repo itself (when cwd === script dir and not `--global`).

### Phase 2: Read Old Manifest

Load the existing manifest if present. If corrupted JSON, warn and treat as fresh install.

### Phase 3: Migrate from Legacy Installs

If no manifest exists, scan the target for symlinks pointing into this toolkit repo. Build a synthetic manifest from discovered symlinks so that orphan/conflict logic works correctly on the first manifest-aware install.

This is essential for upgrading from any pre-manifest installer (e.g., a shell script). The migration scans `agents/`, `commands/`, `skills/`, `references/` in the target directory. For each symlink whose resolved target falls within the toolkit repo's real path, record it in the synthetic manifest.

Important: Symlinks can be relative or absolute. Resolution must handle both by resolving relative to the link's parent directory, then calling `realpathSync` for comparison against the repo's real path.

### Phase 4: Build New File List

Recursively collect all files from the four content directories in the repo. Each entry is `{ rel, abs }` where `rel` is the forward-slash-normalized relative path (e.g., `skills/skill-a/SKILL.md`) and `abs` is the absolute filesystem path.

Skip patterns: `.DS_Store`, `__pycache__`, `.git`.

### Phase 5: Compare Manifests

Produce two lists by diffing old manifest against new file list:

**Orphans**: Files in old manifest but not in new file list, and still present on disk. These will be removed.

**Conflicts**: Files where the on-disk content differs from both the manifest checksum (user edited it) AND the source checksum (source also changed). If on-disk matches source, there's no conflict — the user's edit happens to match the update.

Conflict detection applies in two scenarios:
1. **Copy mode reinstall**: Standard three-way comparison (manifest vs disk vs source).
2. **Copy → link mode switch**: This is the dangerous transition. The user may have edited copied files. Switching to link mode would silently replace those edits with symlinks to the repo. Detect conflicts for individual files AND for entire skill directories (since skills switch from copied file trees to directory symlinks).

### Phase 6: Resolve Conflicts

If conflicts exist, prompt the user per-file: `[O]verwrite / [K]eep / [A]ll overwrite / [N]one keep`.

Behavior modifiers:
- `--force`: Overwrite all conflicts without prompting.
- Non-interactive terminal: Overwrite all (with warning), EXCEPT during copy→link transitions where non-interactive mode throws an error. This prevents CI scripts from silently destroying local edits during the most dangerous mode switch.

### Phase 7: Install Files

For each file in the new list (skipping kept files):

**Link mode:**
- Skills: Create one directory symlink per skill folder. If the symlink already points to the correct target, skip. If a real directory exists (from copy mode), remove it first (only allowed during copy→link switch or with `--force`).
- Other files: Create individual file symlinks. Remove existing symlink or file first if present.

**Copy mode:**
- Remove existing toolkit skill symlinks first (prevents writing into the repo).
- Copy each file. Skip if content is identical to existing file.
- Set executable permissions on `.sh` and `.py` files.

### Phase 8: Remove Orphans

Delete orphaned files. Additionally scan for stale skill directory symlinks (pointing into the toolkit repo but whose target no longer exists on disk — meaning the skill was removed from the repo).

Clean up empty parent directories (deepest first). Never remove top-level category directories (`agents/`, `commands/`, `skills/`, `references/`) since other tools or manual files may live there.

### Phase 9: Write New Manifest

Record every installed file with its current checksum. For kept files, record the on-disk checksum (not the source). This ensures the next install correctly detects whether the user's kept version has been further modified.

---

## Uninstall

The `--uninstall` flag removes all toolkit files from the target scope.

Implementation: Read the manifest, treat every entry as an orphan, delete them all, remove skill directory symlinks pointing into the toolkit repo, clean up empty directories, delete the manifest file.

```bash
cd my-project && ~/toolkits/my-toolkit/install.js --uninstall          # project scope
~/toolkits/my-toolkit/install.js --uninstall --global                  # global scope
```

If no manifest exists, print "Nothing to uninstall" and exit cleanly.

---

## Symlink Ownership Detection

A recurring problem: determining whether a symlink "belongs to" this toolkit. A naive check (`target.startsWith(SCRIPT_DIR)`) fails for relative symlinks and for symlinks created when the repo was at a different path.

The robust approach:

1. Read the symlink target with `readlinkSync`.
2. If relative, resolve to absolute using `path.resolve(path.dirname(linkPath), target)`.
3. Resolve to real path with `realpathSync` (follows further symlinks, canonicalizes).
4. Check if the resolved real path falls within `realpathSync(SCRIPT_DIR)` using `path.relative`.

```javascript
function symlinkPointsIntoScriptDir(linkPath) {
  const linkTarget = fs.readlinkSync(linkPath);
  const absolute = path.resolve(path.dirname(linkPath), linkTarget);
  const real = fs.realpathSync(absolute);  // may throw if dangling
  const relative = path.relative(SCRIPT_DIR_REAL, real);
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
}
```

---

## Edge Cases (Regression-Tested)

These are hard-won lessons. Each has a corresponding regression test.

### 1. Copy → Link: Modified Files Must Not Be Silently Overwritten

**Scenario**: User installs with `--copy`, edits a file, then re-runs the installer (which defaults to link mode). The modified copy would be silently replaced by a symlink.

**Solution**: Detect copy→link transitions via `oldManifest.mode === 'copy'` and `currentMode === 'link'`. Run conflict detection for all files. In non-interactive mode, throw an error instead of silently overwriting. The user must either run interactively (to choose overwrite/keep per file), or use `--force`.

### 2. Copy → Link: Skill Directories Need Whole-Directory Conflict Check

**Scenario**: In copy→link transitions, skills switch from individual copied files to a single directory symlink. If any file within the skill directory was modified, the entire directory replacement must be flagged as a conflict.

**Solution**: Compare every file in the installed skill directory against the source. Also check for extra files the user may have added. If any difference exists, flag `skills/<name>` as a conflict (not individual files).

### 3. Relative Symlinks from Previous Installers

**Scenario**: A previous version of the installer (or a shell script) created relative symlinks. The ownership check using `startsWith(SCRIPT_DIR)` fails on relative paths.

**Solution**: Always resolve symlinks to absolute+real paths before checking ownership (see Symlink Ownership Detection above).

### 4. Copy Mode Must Remove Pre-Existing Skill Symlinks

**Scenario**: User previously installed with link mode (skill directory symlinks), then re-runs with `--copy`. Writing files into a directory symlink writes into the source repo, not the target.

**Solution**: Before the copy loop, scan `<target>/skills/` for symlinks pointing into the toolkit repo and remove them. The copy loop then creates real directories via `mkdirSync`.

### 5. AI Tools Replace Symlinks with Regular Files

**Scenario**: Claude Code's Edit tool reads through symlinks but writes a new regular file at the symlink path. The symlink silently becomes an independent copy. Future `git pull` updates no longer reach it.

**Detection**: `ls -la <path>` shows a regular file where a symlink was expected.

**Recovery**: Re-running the installer fixes it (the existing file is removed and replaced with a fresh symlink).

---

## CLI Interface

```
Usage: install.js [options]

Options:
  -g, --global     Install to ~/.claude/ (default: current project ./.claude/)
      --copy       Copy files instead of symlinking
  -f, --force      Overwrite modified files without prompting
      --uninstall  Remove all toolkit files from the target scope
  -h, --help       Show this help message
```

The installer is a standalone Node.js script with zero dependencies (only `fs`, `path`, `os`, `readline`, `crypto`). It uses a shebang (`#!/usr/bin/env node`) so it's directly executable after cloning.

`package.json` should declare the installer as a `bin` entry so `npx` works as a fallback distribution method, though the primary flow is clone-and-run.

---

## Regression Tests

Ship a bash test script (`scripts/test-install-regressions.sh`) that exercises the critical edge cases. Each test creates a temporary directory, runs installs with specific flag combinations, and asserts the expected filesystem state.

Tests to include:

1. **Copy → link blocks non-interactive modified files**: Install `--copy`, modify a file, re-run without flags. Assert exit code is non-zero, error message mentions "Local modifications", file is NOT replaced with symlink, content is preserved.

2. **Copy → link force overwrites modified files**: Same setup, but re-run with `--force`. Assert file IS now a symlink, local edit content is gone.

3. **Copy mode converts relative skill symlinks**: Pre-create a relative symlink for a skill directory, run `--copy`. Assert the symlink is replaced with a real directory containing copied files.

Add the test script to `package.json`:
```json
{
  "scripts": {
    "test:install-regressions": "scripts/test-install-regressions.sh"
  }
}
```

---

## Multi-CLI Tool Support (Future)

Currently installs into `.claude/` only. This section documents the architecture for supporting Codex, Cursor, Windsurf, and other AI coding tools.

### Platform Configuration

Each AI tool has different directory conventions. Define platform configs that map toolkit content types to the tool's expected structure:

```json
{
  "platform": "codex",
  "root": ".codex",
  "contentMap": {
    "skills": { "target": "instructions", "format": "single-file" },
    "references": { "target": "instructions", "format": "concatenated" },
    "commands": null,
    "agents": null
  }
}
```

- `root`: The tool's configuration directory (`.claude/`, `.codex/`, `.cursor/`).
- `contentMap`: How each content type maps to the tool's structure. `null` means the content type isn't supported by this tool.
- `format`: `"individual"` (one file per source file, like Claude Code), `"single-file"` (one file per content type), or `"concatenated"` (all content types merged into one file).

### CLI Extension

Add a `--tool` flag:
```
--tool <name>    Target tool: claude (default), codex, cursor, windsurf, all
```

`--tool all` installs for every detected tool (check for existence of `.claude/`, `.codex/`, etc. in the target).

### Content Transformation

Some tools need different file formats:
- **Claude Code**: Individual files in subdirectories (skills/, commands/, etc.)
- **Codex CLI**: Single AGENTS.md instruction file
- **Cursor**: .cursorrules or .cursor/rules/ files

The installer should support a content transformation step that renders the same source content into tool-specific formats. For tools that want concatenated files, the installer generates them into a `.generated/<tool>/` directory in the repo and symlinks to those generated files.

### Manifest Per Tool

Each tool installation gets its own manifest dotfile: `<target>/.<toolkit-name>.manifest.json`. This allows independent install/uninstall per tool.
