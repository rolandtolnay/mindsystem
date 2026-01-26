# Changelog

All notable changes to Mindsystem will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [3.3.0] - 2026-01-26

### Added
- **Decision consolidation on milestone completion** — New `ms-consolidator` agent extracts decisions from phase artifacts (PLAN.md, CONTEXT.md, RESEARCH.md, DESIGN.md) into `v{X.Y}-DECISIONS.md` during `/ms:complete-milestone`. Decisions grouped by category (Technical Stack, Architecture, Data Model, API Design, UI/UX, Security, Performance)
- **Auto-simplification after phase execution** — Code simplifier agent runs automatically after `/ms:execute-phase` and `/ms:do-work`, reviewing changes for clarity and maintainability. Stack-aware: uses `ms-flutter-simplifier` for Flutter projects (configurable in `config.json`)
- **Patch generation for do-work** — `/ms:do-work` now generates patches for complex discoveries, enabling execution in fresh context

### Changed
- **`/ms:new-milestone` consolidates discuss-milestone** — Discovery mode now opt-in via decision gate ("I know what to build" / "Help me figure it out" / "Show previous decisions first"). Loads previous milestone's DECISIONS.md and AUDIT.md on-demand only when user chooses discovery
- **Rebranded GSD to Mindsystem** — Internal references updated throughout codebase
- **Streamlined ms-executor** — 30% reduction in agent prompt size

### Removed
- `/ms:discuss-milestone` command — functionality merged into `/ms:new-milestone`
- `milestone-context.md` template — replaced by on-demand DECISIONS.md loading
- `/ms:linear` command and Python CLI — moved to separate skill

### Fixed
- **Previous milestone context loading** — Removed placeholder @-references that wouldn't resolve; now uses explicit on-demand loading after user choice

## [3.2.3] - 2026-01-25

### Changed
- **Removed mode/gates distinction** — Single default behavior (YOLO-style auto-approve) for all workflows. Removes `mode` field and `gates` section from config.json, simplifying configuration. Existing configs with these fields are silently ignored.

### Fixed
- **`/ms:whats-new` URLs** — Updated GitHub repository URLs from gsd to mindsystem

## [3.2.2] - 2026-01-25

### Fixed
- **`/ms:linear` config lookup** — Wrapper script now preserves original working directory so `.linear.json` is found in the user's project root instead of the script location

## [3.2.1] - 2026-01-25

### Changed
- **`/ms:linear` streamlined** — Issue creation now prioritizes speed: infer priority/estimate from description, ask up to 4 high-impact questions in one batch, create immediately without preview confirmation
- Break flow simplified — user provides sub-issues explicitly, no AI-generated proposals
- Codebase exploration only happens when explicitly requested

## [3.2.0] - 2026-01-25

### Added
- **`ms-linear` CLI tool** — Python CLI wrapping Linear GraphQL API with commands: `create`, `update`, `done`, `state`, `break`, `get`, `states`, `projects`
- **`/ms:linear` slash command** — Conversational interface for Linear issue management
- **Flexible project assignment** — `--project` flag to specify project by name, `--no-project` to skip project assignment
- Sub-issues inherit parent's project by default

### Removed
- `.claude/skills/linear/` skill — replaced by CLI + slash command architecture

## [3.1.0] - 2026-01-25

### Removed
- `/ms:pause-work` and `/ms:resume-work` commands — redundant with `/ms:progress` which now handles session resumption
- Session Continuity section from STATE.md template
- Handoff file infrastructure (`.continue-here` files)

### Changed
- `/ms:progress` now reconstructs STATE.md from artifacts when missing
- Simplified state tracking without resume file management

## [3.0.0] - 2026-01-23

### Changed
- **BREAKING:** Rebranded from GSD to Mindsystem
- Command prefix changed from `gsd:` to `ms:`
- NPM package renamed to `mindsystem-cc`
- All agents renamed from `gsd-*` to `ms-*`
- Directory structure: `get-shit-done/` → `mindsystem/`
- Skill renamed from `gsd-meta` to `ms-meta`
- Python CLI renamed from `gsd-lookup` to `ms-lookup`

### Migration
Users must reinstall: `npx mindsystem-cc`
All commands change from `/gsd:*` to `/ms:*`

## [2.14.0] - 2026-01-23

### Added
- **verify-work redesign** — Mock support for isolated testing and inline fixing for quick corrections without full plan overhead

### Fixed
- **verify-work** — Improved retry tracking and stash handling for cleaner verification cycles
- **design-phase command** — Now commits DESIGN.md after creation (was missing commit step)

## [2.13.1] - 2026-01-22

### Fixed
- **simplify-flutter command** — Now uses `fvm flutter` commands for analyze and test steps, ensuring correct Flutter version when fvm is configured

## [2.13.0] - 2026-01-22

### Added
- **`/gsd:review-design` command** — Retroactive design audits for already-implemented features. Reviews existing code against design quality criteria, creates DESIGN.md if missing, presents improvements with trade-offs, and applies approved changes. Use for features built before GSD or periodic design quality checks.

## [2.12.0] - 2026-01-22

### Added
- **`/gsd:simplify-flutter` command** — Code simplification specialist for Flutter/Dart projects. Analyzes code for clarity improvements while preserving functionality. Includes embedded Flutter-specific guidance for widgets, Riverpod, collections, and code organization. Runs `flutter analyze` and `flutter test` to verify no regressions.

## [2.11.0] - 2026-01-22

### Added
- **gsd-lookup CLI** — New research tooling for library documentation (Context7) and deep research (Perplexity) at `scripts/gsd-lookup/`
- Switched to `sonar-reasoning-pro` model for faster, higher-quality deep research

### Fixed
- Updated hardcoded 2025 year references to 2026 in research prompts to prevent stale search results

### Changed
- Reset vanilla branch to upstream base for cleaner fork management

## [2.10.2] - 2026-01-21

### Fixed
- Context7 MCP tool references in `gsd-researcher` agent — corrected tool prefix from `mcp__context7__*` to `mcp__plugin_context7_context7__*`, fixed tool name from `get-library-docs` to `query-docs`, and updated parameter names

## [2.10.1] - 2026-01-20

### Changed
- Optimized sub-agent model selection for cost reduction: `gsd-codebase-mapper`, `gsd-plan-checker`, `gsd-verifier` now use Sonnet; `gsd-research-synthesizer` uses Haiku. Agents requiring judgment (debugger, designer, executor, etc.) inherit Opus.

## [2.10.0] - 2026-01-20

### Added
- **`/gsd:do-work` command** — Bridges gap between `/gsd:add-todo` (capture for later) and `/gsd:insert-phase` (full planning). Executes small adhoc work (max 2 tasks) with proper audit trail in `.planning/adhoc/` while keeping overhead proportional to work size
- GSD patterns reference document

### Changed
- Updated CLAUDE.md contributor guidelines

## [2.9.0] - 2026-01-20

### Added
- **Design phase** (`/gsd:design-phase`) — New phase between discuss and research for UI/UX specifications. Creates DESIGN.md with ASCII wireframes, component specs, UX flows, and verification criteria
- **gsd-designer agent** — Dedicated agent for design work with quality-forcing patterns (commercial benchmark, pre-emptive criticism, accountability check, mandatory self-review)
- **DESIGN.md template** — 7-section specification format: Visual Identity, Screen Layouts, Component Specifications, UX Flows, Design System Decisions, Platform-Specific Notes, Verification Criteria
- **Mathematical validation** — Blocking validation before design completion: bounds containment, platform-specific touch targets (Web 32×32px, iOS 44×44pt, Android 48×48dp), spacing minimums, WCAG AA contrast
- **Design iteration template** — Structured feedback format for major redesigns: what worked (keep), what needs improvement (fix), new requirements (add), primary focus
- **verify-changes command** — Goal-backward verification that code changes achieve requirements
- **gsd-meta skill** — Expert guidance for understanding and modifying GSD itself, with reference docs for architecture, concepts, execution model, and workflows for diagnose/plan-change

### Changed
- Research phase now loads DESIGN.md and uses design specifications to guide technical research
- Plan phase references design specifications when creating tasks
- Execute phase includes smart routing to suggest design-phase for UI-heavy work
- Progress command shows DESIGN.md status alongside other phase artifacts
- gsd-executor honors DESIGN.md specifications during implementation

## [2.8.1] - 2026-01-19

### Added
- GSD Command Reference document with installation guide, quick start flows for greenfield/brownfield projects, and complete command documentation organized by category
- Updated help command to reference the new command reference document
- Improved README structure with clearer organization

## [2.8.0] - 2026-01-19

### Removed
- `/gsd:execute-plan` command — use `/gsd:execute-phase` instead (handles all use cases including single plans)

### Changed
- Progress, help, README, and resume-project now route to `/gsd:execute-phase`
- Plan-phase workflow removes execute-plan as an option
- gsd-executor agent description updated

## [2.7.0] - 2026-01-19

### Added
- Batched UAT testing — `/gsd:verify-work` now presents tests in groups of 4 using AskUserQuestion instead of one-at-a-time plain text, optimized for the common case where most tests pass
- Distinct test result types: `pass`, `issue`, `blocked` (re-tested on next run), `skipped` (assumption logged)
- Assumptions tracking — skipped tests logged to UAT.md Assumptions section, aggregated by `/gsd:audit-milestone`, surfaced during `/gsd:new-milestone` discovery
- "Address untested assumptions" option in `/gsd:discuss-milestone` for planning test infrastructure work

### Changed
- UAT file writes batched after each group of 4 tests instead of per-test, reducing file I/O
- Resume behavior distinguishes blocked tests (re-present) from skipped tests (assumption stands)

## [2.6.0] - 2026-01-18

### Changed
- Phase patch generation externalized to shell script — execute-phase now calls `scripts/generate-phase-patch.sh` instead of inline bash, improving maintainability and making the patch generation logic reusable

## [2.5.1] - 2026-01-18

### Added
- Smart routing for "Next Up" suggestion — after phase execution, suggests discuss/research/plan based on roadmap analysis (user-facing keywords, complexity signals, Research: Likely flag)

## [2.5.0] - 2026-01-18

### Added
- Phase patch file generation — after phase verification, a `{phase}-{name}-changes.patch` file is created with all implementation changes (excluding `.planning/` docs), left uncommitted for manual review

## [2.4.0] - 2026-01-18

### Added
- Auto-diagnosis in `/gsd:verify-work` — when UAT finds issues, parallel debug agents now investigate root causes automatically
- STATE.md blockers — diagnosed issues are tracked as phase blockers
- Migration documentation (MIGRATE-VERIFY-WORK-DIAGNOSIS.md, MIGRATE-PROJECT-CLEANUP.md, MIGRATE-SESSION-MANAGEMENT.md)
- UX guidance in CLAUDE.md — prefer simple markdown formatting over decorative banners

### Changed
- `/gsd:verify-work` now spawns `gsd-debugger` agents to diagnose each gap before presenting `/gsd:plan-phase --gaps`
- UAT.md gap format now includes `root_cause`, `artifacts`, `missing`, and `debug_session` fields
- Updated help.md and README.md with all 30 commands and corrected GitHub URLs (rolandtolnay/gsd)

## [2.3.0] - 2026-01-18

### Added
- Phase number continuation — new milestones continue phase numbering from existing phases
- Thread-following questioning in `/gsd:discuss-milestone` — dig deeper before switching topics
- Probe-for-edges questions — MVP vs complete, simplest version, constraints
- Starting phase number in MILESTONE-CONTEXT.md output
- Automatic git tagging and push in `/release` command

### Changed
- `/gsd:create-roadmap` calculates and passes `$START_PHASE` to gsd-roadmapper agent
- `/gsd:new-milestone` shows next phase number in routing message
- All 4 research prompts in `/gsd:research-project` have stronger subsequent milestone guidance

## [2.2.0] - 2026-01-18

### Added
- New `gsd-roadmapper` agent for roadmap creation with goal-backward success criteria
- Roadmap approval gate — user reviews roadmap before commit
- "What shipped" presentation in `/gsd:new-milestone` — shows previous accomplishments before asking what's next
- Migration guide (MIGRATE-PROJECT-WORKFLOW.md)

### Changed
- `/gsd:create-roadmap` now spawns roadmapper agent instead of using workflow file

### Removed
- `workflows/create-roadmap.md` — logic moved to gsd-roadmapper agent

## [2.1.0] - 2026-01-18

### Added
- New `gsd-research-synthesizer` agent for atomic commits and unified summaries in project research
- CONTEXT.md integration in `gsd-researcher` — researchers now respect locked decisions from discuss-phase
- Migration guides (HYBRID-SETUP.md, MIGRATE-RESEARCH-FEATURES.md)
- Project-level Claude settings (.claude/settings.json)

### Changed
- `/gsd:research-project` now spawns synthesizer agent instead of orchestrator synthesis

## [2.0.0] - 2026-01-18

### Added
- Fork initialization with project-scoped `/release` command
- `/gsd:check-phase` command for on-demand plan verification
- `gsd-plan-checker` agent for goal-backward plan verification

### Changed
- Consolidated GSD-STYLE.md into CLAUDE.md


## [1.x] - Upstream (pre-fork)

Versions `1.0.0` through `1.5.17` were authored in the upstream `get-shit-done` project before the `2.0.0` fork.
The detailed per-release entries have been collapsed here to keep this changelog readable.

### Highlights
- Introduced the phase-based workflow and templates (`PROJECT.md`, `STATE.md`) and core `/gsd:*` commands
- Added issue triage and TDD guidance, plus iterative workflow refinements
- Expanded the agent library and tooling (e.g. researcher/debugger/codebase mapping, `/gsd:update`)

[Unreleased]: https://github.com/rolandtolnay/mindsystem/compare/v3.3.0...HEAD
[3.3.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.3.0
[3.2.1]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.2.1
[3.2.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.2.0
[3.1.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.1.0
[3.0.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.0.0
[2.14.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.14.0
[2.13.1]: https://github.com/rolandtolnay/gsd/releases/tag/v2.13.1
[2.13.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.13.0
[2.12.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.12.0
[2.11.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.11.0
[2.10.2]: https://github.com/rolandtolnay/gsd/releases/tag/v2.10.2
[2.10.1]: https://github.com/rolandtolnay/gsd/releases/tag/v2.10.1
[2.10.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.10.0
[2.9.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.9.0
[2.8.1]: https://github.com/rolandtolnay/gsd/releases/tag/v2.8.1
[2.8.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.8.0
[2.7.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.7.0
[2.6.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.6.0
[2.5.1]: https://github.com/rolandtolnay/gsd/releases/tag/v2.5.1
[2.5.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.5.0
[2.4.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.4.0
[2.3.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.3.0
[2.2.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.2.0
[2.1.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.1.0
[2.0.0]: https://github.com/rolandtolnay/gsd/releases/tag/v2.0.0
[1.x]: https://github.com/glittercowboy/get-shit-done/releases
