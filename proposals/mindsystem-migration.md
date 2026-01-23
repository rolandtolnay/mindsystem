# Mindsystem Migration Proposal

> Rebrand GSD fork to Mindsystem with `ms:` command prefix

## Executive Summary

**What:** Rename this GSD fork to "Mindsystem" — a complete rebrand including command prefix (`gsd:` → `ms:`), directory structure (`get-shit-done/` → `mindsystem/`), NPM package (`mindsystem-cc`), and GitHub repository.

**Why:** The fork has diverged significantly from upstream GSD. Different philosophies (collaborative vs no-code, Claude Code specific vs multi-CLI) warrant independent identity. The rebrand establishes Mindsystem as its own product while crediting GSD origins.

**Impact:** ~150-200 files affected. Breaking change for existing users. Version bump to 3.0.0. Clean break with no backwards compatibility aliases.

---

## Goals

**Primary:** Complete rebrand from GSD to Mindsystem with consistent naming throughout the codebase.

**Secondary:**
- Establish independent brand identity
- Align with Mindsystem Solutions company branding
- Clean, memorable command prefix (`ms:`)
- Credit GSD origins appropriately

## Non-Goals

- **Backwards compatibility:** No `gsd:` aliases — clean break
- **Feature changes:** This is purely a rename, no functional changes
- **Historical revision:** Changelog entries and proposals preserve original names
- **Upstream merge:** This divergence is permanent

---

## Architecture Overview

### Naming Convention Changes

```
BEFORE                          AFTER
──────────────────────────────────────────────────────
/gsd:command                    /ms:command
gsd-executor (agent)            ms-executor
gsd-meta (skill)                ms-meta
get-shit-done/ (directory)      mindsystem/
get-shit-done-cc (npm)          mindsystem-cc
rolandtolnay/gsd (repo)         rolandtolnay/mindsystem
```

### Directory Structure Changes

```
BEFORE                          AFTER
──────────────────────────────────────────────────────
commands/gsd/                   commands/ms/
├── progress.md                 ├── progress.md
├── execute-phase.md            ├── execute-phase.md
└── ... (33 files)              └── ... (33 files)

agents/                         agents/
├── gsd-executor.md             ├── ms-executor.md
├── gsd-researcher.md           ├── ms-researcher.md
└── ... (13 files)              └── ... (13 files)

get-shit-done/                  mindsystem/
├── workflows/                  ├── workflows/
├── templates/                  ├── templates/
└── references/                 └── references/

.claude/skills/gsd-meta/        .claude/skills/ms-meta/

scripts/gsd-lookup/             scripts/ms-lookup/
```

---

## Detailed Design

### Phase 1: Directory Moves

| From | To | Files |
|------|-----|-------|
| `commands/gsd/` | `commands/ms/` | 33 command files |
| `agents/gsd-*.md` | `agents/ms-*.md` | 13 agent files |
| `get-shit-done/` | `mindsystem/` | 3 subdirs, ~70 files |
| `.claude/skills/gsd-meta/` | `.claude/skills/ms-meta/` | 8 files |
| `scripts/gsd-lookup/` | `scripts/ms-lookup/` | 4 files |
| `scripts/gsd-lookup-wrapper.sh` | `scripts/ms-lookup-wrapper.sh` | 1 file |

### Phase 2: YAML Frontmatter Updates

**Commands (33 files):**
```yaml
# BEFORE
name: gsd:progress

# AFTER
name: ms:progress
```

**Agents (13 files):**
```yaml
# BEFORE
name: gsd-executor

# AFTER
name: ms-executor
```

**Skill (1 file):**
```yaml
# BEFORE
name: gsd-meta

# AFTER
name: ms-meta
```

### Phase 3: Package & Installation Updates

**package.json:**
```json
{
  "name": "mindsystem-cc",
  "bin": {
    "mindsystem-cc": "bin/install.js"
  },
  "repository": {
    "url": "git+https://github.com/rolandtolnay/mindsystem.git"
  }
}
```

**bin/install.js changes:**
- Update banner text
- Update path references (`commands/gsd` → `commands/ms`)
- Update `get-shit-done` → `mindsystem` directory references
- Update final message (`/gsd:help` → `/ms:help`)

### Phase 4: Logo/Visual Update

**assets/terminal.svg:**

Current ASCII art:
```
   ██████╗ ███████╗██████╗
  ██╔════╝ ██╔════╝██╔══██╗
  ██║  ███╗███████╗██║  ██║
  ██║   ██║╚════██║██║  ██║
  ╚██████╔╝███████║██████╔╝
   ╚═════╝ ╚══════╝╚═════╝
```

New design direction:
- Replace "GSD" ASCII art with "MINDSYSTEM" or stylized "MS" logo
- Update color scheme if desired (current: cyan `#7dcfff`)
- Update title: "Mindsystem" with version
- Update subtitle: "AI-Powered Development"
- Remove TÂCHES attribution (move to README acknowledgments)
- Update install output: `commands/ms`, `mindsystem`
- Update help reference: `/ms:help`

### Phase 5: Documentation Updates

**README.md:**
- Replace "GET SHIT DONE" branding with "Mindsystem - AI-Powered Development"
- Update all command examples (`/gsd:` → `/ms:`)
- Update installation command (`npx mindsystem-cc`)
- Update badge URLs to new repo
- Add acknowledgments section crediting GSD

**CLAUDE.md:**
- Update `gsd-meta` skill reference → `ms-meta`
- Update any command examples

**Standalone docs:**
- Rename `GSD Command Reference.md` → `Mindsystem Command Reference.md`
- Rename `GSD-PATTERNS-EXTRACTED.md` → `Mindsystem-Patterns-Extracted.md`
- Update content within these files

### Phase 6: Content Updates (Search/Replace)

**Pattern replacements across all active files:**

| Pattern | Replacement | Scope |
|---------|-------------|-------|
| `/gsd:` | `/ms:` | All non-historical files |
| `gsd-executor` | `ms-executor` | All non-historical files |
| `gsd-researcher` | `ms-researcher` | All non-historical files |
| (all 13 agents) | (ms-* equivalent) | All non-historical files |
| `gsd-meta` | `ms-meta` | All non-historical files |
| `@~/.claude/get-shit-done/` | `@~/.claude/mindsystem/` | All @-references |
| `get-shit-done-cc` | `mindsystem-cc` | Package references |

**Excluded from replacement (historical preservation):**
- `CHANGELOG.md` entries before 3.0.0
- All files in `proposals/`
- All files in `prompts/`
- All files in `migrations/`

### Phase 7: Version Bump

**CHANGELOG.md addition:**
```markdown
## [3.0.0] - YYYY-MM-DD

### Changed
- **BREAKING:** Rebranded from GSD to Mindsystem
- Command prefix changed from `gsd:` to `ms:`
- NPM package renamed to `mindsystem-cc`
- All agents renamed from `gsd-*` to `ms-*`
- Directory structure: `get-shit-done/` → `mindsystem/`

### Migration
Users must reinstall: `npx mindsystem-cc`
All muscle memory commands change from `/gsd:*` to `/ms:*`
```

---

## File Change Inventory

### Directories to Move/Rename

| Directory | Action |
|-----------|--------|
| `commands/gsd/` | Move to `commands/ms/` |
| `agents/` | Rename 13 files (gsd-* → ms-*) |
| `get-shit-done/` | Move to `mindsystem/` |
| `.claude/skills/gsd-meta/` | Move to `.claude/skills/ms-meta/` |
| `scripts/gsd-lookup/` | Move to `scripts/ms-lookup/` |

### Files Requiring Frontmatter Updates

**Commands (33 files):**
- add-phase.md, add-todo.md, audit-milestone.md, check-phase.md, check-todos.md
- complete-milestone.md, create-roadmap.md, debug.md, define-requirements.md
- design-phase.md, discuss-milestone.md, discuss-phase.md, do-work.md
- execute-phase.md, help.md, insert-phase.md, list-phase-assumptions.md
- map-codebase.md, new-milestone.md, new-project.md, pause-work.md
- plan-milestone-gaps.md, plan-phase.md, progress.md, remove-phase.md
- research-phase.md, research-project.md, resume-work.md, review-design.md
- simplify-flutter.md, update.md, verify-work.md, whats-new.md

**Agents (13 files):**
- ms-codebase-mapper.md, ms-debugger.md, ms-designer.md, ms-executor.md
- ms-integration-checker.md, ms-milestone-auditor.md, ms-mock-generator.md
- ms-plan-checker.md, ms-research-synthesizer.md, ms-researcher.md
- ms-roadmapper.md, ms-verifier.md, ms-verify-fixer.md

**Skill (1 file):**
- .claude/skills/ms-meta/SKILL.md

### Files Requiring Content Updates

**Core documentation:**
- README.md
- CLAUDE.md
- Mindsystem Command Reference.md (renamed)
- Mindsystem-Patterns-Extracted.md (renamed)

**Installation:**
- bin/install.js
- package.json

**Visual:**
- assets/terminal.svg

**Workflows (~20 files with command references):**
- mindsystem/workflows/execute-phase.md
- mindsystem/workflows/plan-phase.md
- mindsystem/workflows/do-work.md
- mindsystem/workflows/verify-work.md
- (and others)

**Templates (~10 files with references):**
- mindsystem/templates/phase-prompt.md
- mindsystem/templates/state.md
- mindsystem/templates/UAT.md
- (and others)

**References (~5 files):**
- mindsystem/references/plan-format.md
- (and others)

**Skill files:**
- .claude/skills/ms-meta/references/*.md
- .claude/skills/ms-meta/workflows/*.md

### Files NOT Modified (Historical)

- CHANGELOG.md (entries before 3.0.0)
- proposals/*.md
- prompts/*.md
- migrations/*.md

---

## Resolved Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Command prefix | `ms:` | Short (2 chars), matches brand, easy to type |
| Agent prefix | `ms-` | Consistent with command convention |
| Directory name | `mindsystem/` | Full brand name for clarity |
| NPM package | `mindsystem-cc` | `-cc` suffix indicates Claude Code focus |
| Version | 3.0.0 | Major bump signals breaking change |
| Backwards compat | None | Clean break reduces maintenance burden |
| Historical docs | Preserve | Accurate record of development history |
| Attribution | README section | Standard open-source practice |
| Logo style | New ASCII art | Visual refresh for new identity |

---

## Implementation Plan

### Execution Order

```
Phase 1: Directory moves (git mv)
    ↓
Phase 2: Frontmatter updates (sed/script)
    ↓
Phase 3: Package/install updates (manual)
    ↓
Phase 4: Logo update (manual SVG edit)
    ↓
Phase 5: Documentation updates (manual)
    ↓
Phase 6: Content search/replace (script)
    ↓
Phase 7: Version bump + changelog
    ↓
Phase 8: Testing
    ↓
Phase 9: GitHub repo rename
    ↓
Phase 10: NPM publish
```

### Recommended Approach

1. **Create migration script** for bulk operations:
   - Directory moves
   - File renames
   - Frontmatter updates
   - Search/replace patterns

2. **Manual review** for:
   - README branding
   - Logo SVG design
   - CHANGELOG entry

3. **Test locally** before GitHub rename:
   - Run `node bin/install.js`
   - Verify all commands resolve
   - Verify agent spawning works

---

## Success Criteria

- [ ] All 33 commands accessible via `/ms:*`
- [ ] All 13 agents spawn correctly with `ms-*` names
- [ ] `ms-meta` skill invocable
- [ ] `npx mindsystem-cc` installs successfully
- [ ] No references to `gsd:`, `gsd-*`, or `get-shit-done` in active code paths
- [ ] Historical documents preserved with original names
- [ ] README displays new branding with GSD acknowledgment
- [ ] Terminal logo shows "MINDSYSTEM" branding
- [ ] Version shows 3.0.0

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missed reference | Medium | Low | Grep verification before release |
| NPM name taken | Low | High | Check availability before starting |
| Broken @-references | Medium | Medium | Test all command flows |
| User confusion | Medium | Low | Clear changelog, migration notes |

---

## Acknowledgments Section (for README)

```markdown
## Acknowledgments

Mindsystem originated as a fork of [GSD (Get Shit Done)](https://github.com/taches/gsd)
by TÂCHES. While the projects have diverged significantly in philosophy and implementation,
we acknowledge GSD's foundational contribution to AI-assisted development workflows.
```

---

## Appendix: ASCII Art Options for Logo

**Option A: Full "MINDSYSTEM" (wide)**
```
███╗   ███╗██╗███╗   ██╗██████╗ ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
████╗ ████║██║████╗  ██║██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
██╔████╔██║██║██╔██╗ ██║██║  ██║███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
██║╚██╔╝██║██║██║╚██╗██║██║  ██║╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
██║ ╚═╝ ██║██║██║ ╚████║██████╔╝███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
```

**Option B: Compact "MS" logo**
```
███╗   ███╗███████╗
████╗ ████║██╔════╝
██╔████╔██║███████╗
██║╚██╔╝██║╚════██║
██║ ╚═╝ ██║███████║
╚═╝     ╚═╝╚══════╝
```

**Option C: Stylized with tagline**
```
  ╔═╗╔═╗  mindsystem
  ║║║║║║  AI-Powered Development
  ╚╩╝╚╩╝
```

Recommendation: Option B (compact "MS") fits the existing SVG dimensions and maintains visual weight similar to original "GSD" logo.
