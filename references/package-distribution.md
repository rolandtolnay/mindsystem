# Prompt Package Distribution: Analysis & Improvement Plan

## Executive Summary

After deep analysis of [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) and comparing it with flutter-llm-toolkit's current installer, a surprising finding: **flutter-llm-toolkit already has the more sophisticated distribution model**. The ui-ux-pro-max uses a copy-only approach with no symlinks, no manifest tracking, and no conflict detection. However, it excels in **multi-tool support** (15 AI coding assistants) and **template-based generation** for platform-specific files.

The ideal model combines the best of both: flutter-llm-toolkit's symlink + manifest architecture with ui-ux-pro-max's multi-tool platform awareness. **Symlink-first is the default** — clone once, link everywhere, `git pull` auto-updates. Copy mode exists as a fallback for npx users. This pattern applies across prompt package projects (Mindsystem, LLM Toolkit, flutter-llm-toolkit).

---

## Part 1: How Each System Works

### ui-ux-pro-max (uipro-cli)

| Aspect | Detail |
|--------|--------|
| **Distribution** | npm package (`uipro-cli`), invoked via `npx uipro-cli@latest init` |
| **Installation** | Copies files into current project directory |
| **Symlinks** | None — every project gets independent copies |
| **Scope** | Project-only (installs into `./<tool-dir>/`) |
| **Multi-tool** | 15 AI tools via `--ai <type>` flag and platform JSON configs |
| **Updates** | `uipro update` re-copies latest files (overwrites) |
| **Manifest** | None — no tracking of installed files |
| **Conflict detection** | None — `--force` overwrites everything |
| **Uninstall** | Manual `rm -rf` |

**Architecture**: Template generation system. Each AI tool has a JSON config specifying folder structure, frontmatter, and content sections. A base `skill-content.md` template is rendered with platform-specific variables.

```
src/ui-ux-pro-max/templates/platforms/
├── claude.json    → .claude/skills/ui-ux-pro-max/SKILL.md
├── cursor.json    → .cursor/skills/ui-ux-pro-max/SKILL.md
├── codex.json     → .codex/skills/ui-ux-pro-max/SKILL.md
├── windsurf.json  → .windsurf/skills/ui-ux-pro-max/SKILL.md
└── ... (15 total)
```

### flutter-llm-toolkit (current)

| Aspect | Detail |
|--------|--------|
| **Distribution** | npm package (`flutter-llm-toolkit`), invoked via `npx flutter-llm-toolkit` |
| **Installation** | Copy (default) or symlink (`--link`) |
| **Symlinks** | File-level for agents/commands/references, directory-level for skills |
| **Scope** | Global (`--global` → `~/.claude/`) or local (`--local` → `./.claude/`) |
| **Multi-tool** | Claude Code only |
| **Updates** | Copy: re-run npx. Symlink: `git pull` auto-updates |
| **Manifest** | SHA256 checksums in `.manifest.json` |
| **Conflict detection** | Detects local modifications, prompts user |
| **Uninstall** | Orphan detection removes stale files |

**Architecture**: Direct file installation with manifest tracking. 9-phase pipeline: detect target → read manifest → migrate legacy → collect files → compare → resolve conflicts → install → remove orphans → write manifest.

---

## Part 2: Validating the Core Insight

> "Users clone the repo anywhere, use a CLI to create symlinks, git pull auto-updates everywhere."

### Does ui-ux-pro-max do this?

**No.** It copies files. Every project is independent. Updates require re-running `uipro update` in each project. There is no single-source-of-truth symlink model. The repo isn't even intended to be cloned by end users — it's distributed purely via npm.

### Does flutter-llm-toolkit do this?

**Yes, with `--link` mode.** When installed with `npx flutter-llm-toolkit --global --link`:
- Skills get directory-level symlinks: `~/.claude/skills/flutter-senior-review` → `/path/to/repo/skills/flutter-senior-review`
- Commands/agents/references get file-level symlinks
- Running `git pull` in the repo automatically updates all symlinked files
- The manifest tracks what was installed for clean upgrades

**However, the current flow has friction points** (detailed in Part 3).

---

## Part 3: Current Limitations & Improvement Opportunities

### 3.1 The npx Indirection Problem

**Current flow:**
```bash
# User must first clone the repo (undocumented for symlink use)
git clone https://github.com/rolandtolnay/flutter-llm-toolkit.git ~/my-toolkits/flutter-llm-toolkit

# Then run npx, which downloads a SEPARATE copy from npm
npx flutter-llm-toolkit --global --link
```

**Problem:** `npx` downloads the package from npm into a temp cache. The symlinks created point to the **npm cache copy**, not the user's cloned repo. The user would need to run `node install.js --global --link` from within their cloned repo for symlinks to point to the right place.

**Fix:** The installer should detect when it's running from a git clone vs npm cache and adjust behavior accordingly. Or better: provide a clone-and-install workflow.

### 3.2 No "Clone Once, Install Everywhere" Workflow

There's no documented flow for the symlink-based multi-project workflow:

```bash
# Ideal flow (doesn't exist yet):
git clone <repo> ~/toolkits/flutter-llm-toolkit
cd ~/toolkits/flutter-llm-toolkit
./install --scope global          # symlinks into ~/.claude/
./install --scope project ~/my-app  # symlinks into ~/my-app/.claude/
./install --scope project ~/other   # symlinks into ~/other/.claude/

# Later:
cd ~/toolkits/flutter-llm-toolkit && git pull  # updates everywhere
```

### 3.3 No Multi-Tool Support

Currently only installs into `.claude/` directories. With Codex, Cursor, Windsurf, and other AI tools becoming prevalent, the installer should support multiple targets.

### 3.4 npx vs Local CLI Confusion

The `npx` flow works well for copy-mode distribution (fire and forget). But for symlink mode, users need to clone the repo first, making `npx` the wrong entry point. These are two fundamentally different workflows that should be separated.

### 3.5 No Self-Contained CLI Script

The current `install.js` requires Node.js but has no dependencies beyond built-in modules. It could be made even more accessible as a standalone script with a shebang, runnable directly after cloning.

### 3.6 Symlink Fragility with AI Editing Tools

**Observed:** Claude Code's Edit tool reads through symlinks but writes a new regular file at the symlink path, silently replacing the symlink with an independent copy. The source file in the repo may or may not retain the changes.

**Impact:** After an AI tool edits a symlinked skill, command, or agent file, the installation silently diverges from the repo. Future `git pull` updates no longer reach the replaced file. The user has no indication this happened.

**Detection pattern:** `ls -la <path>` — a regular file (`-rw-r--r--`) where a symlink (`lrwxr-xr-x`) was expected.

**Recovery pattern:** Verify the source file in the repo has the intended content, then `rm <path> && ln -s <source> <path>` to restore the symlink.

**Mitigation:** The `doctor` command should detect broken symlinks on every run. This is the strongest argument for promoting doctor/diagnostics to Phase 2 (see Part 6).

---

## Part 4: Recommended Architecture

### Two Distribution Modes, Two Entry Points

#### Default: Symlink Install (from cloned repo)
The recommended workflow. Clone once, symlink everywhere, `git pull` updates all installations:
```bash
# One-time setup
git clone <repo> ~/toolkits/flutter-llm-toolkit
cd ~/toolkits/flutter-llm-toolkit

# Install globally (symlinks into ~/.claude/)
./install.js link --tool claude --scope global

# Install into specific project (symlinks into project/.claude/)
./install.js link --tool claude --scope project ~/path/to/my-app

# Install for Codex too
./install.js link --tool codex --scope global

# Update everything at once
git pull  # All symlinks auto-update
```

#### Fallback: Copy Install (via npx)
For users who want to try the toolkit without cloning:
```bash
npx flutter-llm-toolkit install --tool claude --scope global
npx flutter-llm-toolkit install --tool codex --scope project
```
- Copies files into target directory
- No repo clone needed
- Updates via re-running `npx flutter-llm-toolkit install`
- Manifest tracks installed files for clean upgrades

### Unified CLI Interface

```
flutter-llm-toolkit <command> [options]

Commands:
  install     Copy files into target (npx-friendly)
  link        Create symlinks to this repo (requires clone)
  unlink      Remove symlinks created by this repo
  status      Show what's installed, where, and freshness
  doctor      Diagnose installation issues (broken symlinks, diverged copies)

Options:
  --tool <name>     Target tool: claude, codex, cursor, windsurf, all (default: claude)
  --scope <scope>   global (~/) or project (./) (default: global)
  --project <path>  Explicit project path (alternative to --scope project + cd)
  --force           Overwrite without prompting
```

### Multi-Tool Platform Config

Borrowing from ui-ux-pro-max's platform config approach:

```
platforms/
├── claude.json      # { root: ".claude", skills: "skills/", commands: "commands/" }
├── codex.json       # { root: ".codex", instructions: "instructions/" }
├── cursor.json      # { root: ".cursor", rules: "rules/" }
└── windsurf.json    # { root: ".windsurf", rules: "rules/" }
```

Each config maps the toolkit's content types to the tool's expected directory structure:

```json
{
  "platform": "codex",
  "displayName": "Codex CLI",
  "structure": {
    "root": ".codex",
    "contentMap": {
      "skills": { "target": "instructions", "format": "single-file" },
      "references": { "target": "instructions", "format": "concatenated" },
      "commands": null
    }
  }
}
```

The `contentMap` tells the installer how to transform flutter-llm-toolkit content for each tool. Some tools want individual files (Claude Code skills/), others want a single concatenated instruction file (Codex AGENTS.md).

### Symlink Architecture for Multi-Project

```
~/toolkits/flutter-llm-toolkit/          # Cloned repo (single source of truth)
├── skills/flutter-senior-review/
├── commands/capture-lesson.md
├── agents/ms-flutter-reviewer.md
└── references/code_quality.md

~/.claude/                                # Global Claude Code (symlinked)
├── skills/flutter-senior-review → ~/toolkits/flutter-llm-toolkit/skills/flutter-senior-review
├── commands/capture-lesson.md → ~/toolkits/flutter-llm-toolkit/commands/capture-lesson.md
└── flutter-llm-toolkit/.manifest.json

~/projects/app-a/.claude/                 # Project A (symlinked)
├── skills/flutter-senior-review → ~/toolkits/flutter-llm-toolkit/skills/flutter-senior-review
└── flutter-llm-toolkit/.manifest.json

~/projects/app-b/.codex/                  # Project B, different tool (symlinked)
├── instructions/flutter-toolkit.md       # Generated/concatenated from skills + references
└── flutter-llm-toolkit/.manifest.json

~/.codex/                                 # Global Codex (symlinked)
└── instructions/flutter-toolkit.md → ~/toolkits/flutter-llm-toolkit/.generated/codex/instructions.md
```

### Installation Registry

Track all installations from a single manifest in the repo:

```json
// ~/toolkits/flutter-llm-toolkit/.installations.json
{
  "installations": [
    {
      "id": "global-claude",
      "tool": "claude",
      "scope": "global",
      "target": "/Users/roland/.claude",
      "mode": "link",
      "installedAt": "2026-02-25T10:00:00Z"
    },
    {
      "id": "app-a-claude",
      "tool": "claude",
      "scope": "project",
      "target": "/Users/roland/projects/app-a/.claude",
      "mode": "link",
      "installedAt": "2026-02-25T10:05:00Z"
    }
  ]
}
```

This enables:
- `status` command showing all installations
- `unlink --all` to clean up everything
- Detecting broken symlinks after repo moves

---

## Part 5: What to Borrow from ui-ux-pro-max

### Worth Adopting

1. **Platform JSON configs** — Clean separation of "what to install" from "where to install it." Each AI tool gets a JSON file describing its directory conventions.

2. **Template rendering for cross-tool content** — Some tools need different file formats. A template system can render the same skill content into Claude's SKILL.md format, Codex's AGENTS.md format, or Cursor's .cursorrules format.

3. **`--ai` / `--tool` flag with auto-detection** — Detect which AI tools are configured in a project by checking for `.claude/`, `.cursor/`, `.codex/` directories.

4. **Offline-first with network fallback** — Bundled assets work without network; GitHub releases provide the latest version if available.

5. **`--ai all` flag** — Install for every detected AI tool in one command.

### Not Worth Adopting

1. **Copy-only distribution** — Their approach means every project has independent copies that must be updated individually. The symlink model is strictly better for power users.

2. **No manifest/tracking** — They have no way to detect conflicts, orphans, or local modifications. The manifest system in flutter-llm-toolkit is a clear advantage.

3. **No uninstall** — Manual `rm -rf` is not a great UX.

4. **Template duplication** — They maintain copies of assets in both `src/` and `cli/assets/`, requiring manual sync. A symlink-from-source approach eliminates this.

---

## Part 6: Implementation Priority

### Phase 1: Multi-Tool Platform Configs (High Impact, Low Effort)
- Add `platforms/` directory with JSON configs for claude, codex, cursor, windsurf
- Modify `install.js` to accept `--tool` flag
- Map content types to each tool's expected structure

### Phase 2: Doctor & Symlink Integrity (High Impact, Low Effort)
- `doctor` command to detect symlinks replaced by regular files (see 3.6)
- Verify every symlinked path is still a symlink, offer `--fix` to restore broken ones
- Detect repo moves and suggest re-linking
- Version freshness checks (compare local HEAD with remote)

### Phase 3: Explicit Clone-and-Link Workflow (High Impact, Medium Effort)
- Document the "clone repo → run install.js link" workflow
- Add `link` and `unlink` subcommands
- Add `.installations.json` registry in repo root
- Add `status` command

### Phase 4: Cross-Tool Content Rendering (Medium Impact, Medium Effort)
- Template system to render skills/references into tool-specific formats
- Concatenation for tools that want single instruction files (Codex)
- Frontmatter adaptation per tool

---

## Appendix: Key Files Reference

| File | Repository | Purpose |
|------|-----------|---------|
| `cli/src/commands/init.ts` | ui-ux-pro-max | Main installation logic with template rendering |
| `cli/src/utils/template.ts` | ui-ux-pro-max | Template engine for multi-platform file generation |
| `cli/assets/templates/platforms/*.json` | ui-ux-pro-max | Platform-specific configs (15 AI tools) |
| `install.js` | flutter-llm-toolkit | 9-phase installer with manifest tracking |
| `package.json` | flutter-llm-toolkit | npm package config with bin entry |
