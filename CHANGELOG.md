# Changelog

All notable changes to Mindsystem will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [3.22.0] - 2026-02-24

### Added
- **Configurable mockup open behavior** in design-phase. New `open_mockups` config setting (`auto`/`ask`/`off`) controls whether comparison pages auto-open in browser during design work.
- **Research API key health check** in doctor. New CHECK 9 detects missing Context7 and Perplexity API keys with actionable setup guidance. Uses WARN status since missing keys degrade research quality but don't break functionality.
- **UNCERTAIN verification signal** in verify-work pipeline. Verification items that can't be confirmed programmatically now surface as UNCERTAIN instead of being silently passed, with automatic verify-work recommendation when functional confirmation is needed.

### Changed
- **UAT management moved to ms-tools.** Deterministic `uat-init`, `uat-update`, and `uat-status` commands replace LLM-driven Read/Edit cycles for UAT.md bookkeeping, improving reliability. Fix commits now amend-on-retry and UAT.md + STATE.md fold into a single completion commit.
- **Last Command tracking uses ms-tools.** `set-last-command` replaces manual text-manipulation across 22 commands/workflows, with real timestamps instead of hallucinated placeholders.
- **Flutter-specific components removed.** Flutter agents, skills, and references now live in the standalone `flutter-llm-toolkit` package. Agent mappings replaced with generic defaults.

### Fixed
- **Plan checker** uses budget-aware scope estimation matching scope-estimation.md instead of rigid change-count thresholds. Fixed ROADMAP phase extraction.
- **Product researcher** receives actual current date, applying year strings selectively — for trend queries but not product-specific searches where it narrows results.
- **Prompt ergonomics** improved across commands: skill selection uses multiSelect, ms-tools code blocks include PATH hints, plan-phase uses explicit AskUserQuestion gate.
- **Doctor scan** exits 0 on successful scan regardless of check results (exit 2 retained for infrastructure failures).

## [3.21.0] - 2026-02-23

### Added
- **Product-aware discuss phase:** The discuss phase now loads milestone artifacts, surfaces Claude's assumptions, and offers optional competitor/UX/industry research — grounding questions in real project context rather than generic templates. Discuss is now the default pre-work recommendation for all non-mechanical phases, with required assumption enumeration to catch misalignment early.
- **Unified `ms-tools.py` CLI with PATH wrappers:** Consolidated 10 standalone bash scripts into a single Python CLI with comprehensive test suite. Thin `ms-tools` and `ms-lookup` wrappers auto-installed to PATH replace long-form invocations across commands and workflows, saving ~1,600 chars of prompt overhead per session.
- **Name-based milestones:** Milestones use slugified names (e.g., "mvp", "push-notifications") instead of version numbers, eliminating conflicts with app semver and git tags. Includes auto-detection from PROJECT.md, doctor check, and migration tooling.
- **`/ms:config` command:** Configure code reviewers, gitignore patterns, and git remote. Supports updating existing PROJECT.md without starting over.
- **User actions in execution summaries:** Execute-phase surfaces manual steps (migrations, installs, env vars) after plan execution.

### Changed
- Upgraded mockup-designer and researcher agents from Sonnet to Opus; research-synthesizer from Haiku to Sonnet.
- Doctor command extracted fix steps into a dedicated workflow, keeping the command as a thin orchestrator.
- Simplified language and UX polish across config, new-project, release, and design-phase commands.

### Removed
- `/ms:list-phase-assumptions` command (absorbed into discuss-phase).

## [3.20.0] - 2026-02-22

### Added
- Smart pre-work routing for `add-phase` and `insert-phase` — both commands now analyze phase descriptions and suggest the right next step (discuss, design, research, or plan) instead of always defaulting to plan-phase
- Skill discovery in `plan-phase` — automatically finds relevant project skills after task breakdown, confirms with user, and encodes them in plan metadata so the executor loads exact skills without guessing

### Changed
- `PROJECT.md` template restructured with business context: Product Identity (core value, audience, differentiator, key flows), Product Boundaries (constraints, scope), and Product Memory (validated decisions) — gives Claude grounding for product decisions during milestones and design phases
- Onboarding questioning flow updated with grounding questions and clarity-adaptive tracking, especially for brownfield projects where users tend to describe features instead of the overall project

### Fixed
- `doctor-scan` no longer crashes on phases with comma-separated lists or decimal numbering (e.g., `8.3`)

## [3.19.0] - 2026-02-19

### Added
- Doctor command now performs 6 comprehensive health checks — subsystem integrity, milestone directories, phase archival, knowledge files, phase summaries, and plan cleanup — with fixes applied in dependency order

### Changed
- Plan grouping recalibrated to produce right-sized plans — effort-weighted sizing replaces uniform task count ceiling, reducing redundant executor agents while staying within context budget
- Release notes command delegates to Haiku subagent, filters by installed version, and displays oldest-first for better reading order
- Design phase presents directions as structured text with philosophy and concrete choices, then collects selection separately
- Execute phase verifies phase goal achievement before code review, catching goal misses earlier

### Fixed
- Doctor command: fixed stale step references and enforced AskUserQuestion for interactive paths

## [3.18.1] - 2026-02-18

### Changed
- Design template simplified to wireframe-centric format — less context spent on structural overhead, same output quality
- Plan-writer uses budget-weighted task grouping — right-sized plans reduce redundant executor agents while staying within context budget
- Review-design command refocused on practical screen-level improvements
- Planning context scanning simplified with streamlined design skill discovery

## [3.18.0] - 2026-02-17

### Added
- Reusable shell scripts for milestone completion: stats gathering (`gather-milestone-stats.sh`) and phase archival (`archive-milestone-phases.sh`)

### Changed
- `complete-milestone` defers phase directory archival until after consolidation, preserving artifact access during stats and summary-reading steps
- Pre-work routing reordered to match priority logic (Discuss → Design → Research)

### Fixed
- `ms-lookup` surfaces real API errors instead of generic failures; agent templates reference functional tool names instead of MCP service names
- Removed vestigial reorganize step from `complete-milestone` that operated on an already-archived ROADMAP
- Reduced context waste across multiple commands (`complete-milestone`, `extract-pattern`) by trimming prompt fluff and reordering success criteria

### Removed
- Orphaned `cleanup-phase-artifacts.sh` (superseded by `archive-milestone-phases.sh`)

## [3.17.1] - 2026-02-15

### Changed

- Reorder pre-work recommendations to Discuss → Design → Research, matching the intended execution flow where vision clarity precedes visual specification precedes technical investigation

### Fixed

- Remove redundant command labels from Next Up routing format for cleaner output

## [3.17.0] - 2026-02-15

### Added
- Tech debt collection from UAT: unfixed issues discovered during milestone audit now flow automatically into TECH-DEBT.md with severity mapping (blocker→Critical, major→High, minor→Medium, cosmetic→Low)

### Changed
- Milestone archives use versioned folders (`milestones/v[X.Y]/`) instead of flat files, with research files preserved alongside the roadmap
- TECH-DEBT.md replaces PHASE-FINDINGS.md as the single source of truth for quality issues, using 4-tier severity sections; plan-phase auto-loads it for quality/cleanup phases

## [3.16.2] - 2026-02-15

### Fixed
- Plan file references in EXECUTION-ORDER.md now use phase-prefixed names (e.g., `16-01-PLAN.md`) matching actual filenames, preventing validation failures during execution

## [3.16.1] - 2026-02-15

### Changed
- Extract skill loading into dedicated step in design-phase workflow, ensuring design context is loaded before adaptive Q&A begins
- Add Skill tool access to Flutter code quality and simplifier agents
- Add allowed-tools specification to discuss-phase command

### Fixed
- Plan-writer and plan-checker agents were silently downgraded from Opus to Sonnet due to explicit model overrides in workflow and reference docs

## [3.16.0] - 2026-02-15

### Added
- **Executor skill loading** — Executor scans available skills and loads relevant ones before implementation, automatically applying domain-specific best practices
- **Python context scanner for plan-phase** — Deterministic artifact scanning (frontmatter parsing, relevance scoring, directory existence checks) moved from LLM context into `scan-planning-context.py`, saving tokens especially in early projects with few artifacts

### Changed
- **Explicit model pinning on agents** — 9 agents that previously inherited defaults now declare their model (opus/sonnet) explicitly
- **Plan-checker prompt reduced ~39%** — Removed duplicated verification steps, redundant examples, and trimmed success criteria from 13 to 6 high-skip-risk items
- **Verifier prompt reduced ~35%** — Now tech-agnostic (removed React coupling), cleaner truth derivation with contrastive examples, success criteria trimmed from 13 to 7
- **Check-phase command audited** — Renamed tags to follow conventions, removed redundant steps, added success criteria section

## [3.15.0] - 2026-02-14

### Added
- **`ms:doctor` command** — Project health check that diagnoses configuration drift (subsystem vocabulary, missing setup) and fixes issues interactively
- **Phase-level knowledge consolidation** — Consolidator runs after each phase, producing per-subsystem knowledge files that preserve decisions, design rationale, and implementation insights across the project lifecycle
- **Parallel specialized agents for research phases** — Research work split across multiple focused sub-agents with orchestrator synthesis for deeper, faster results

### Changed
- All consuming phases (discuss, design, research, plan, verify, new-milestone) load per-subsystem knowledge files for compounding context
- Milestone completion simplified to cleanup-only (knowledge is already consolidated per-phase)
- `discuss-phase` prompt streamlined to reduce context waste
- `roadmapper` prompt trimmed to reduce interference with agent output
- Subsystem scanning and phase artifact cleanup extracted to reusable scripts

## [3.14.0] - 2026-02-12

### Changed
- **verify-work context footprint reduced by 36%** — UAT template stripped to pure reference data (403→129 lines), removing behavioral sections that duplicated workflow instructions; template double-load eliminated

### Fixed
- **design-phase skill loading and script invocation** — Replaced vague "check your available skills" with explicit scan-invoke-fallback instructions; replaced "generate comparison page" with "run the comparison script" and added anti-pattern guard against generating HTML manually

## [3.13.1] - 2026-02-12

### Changed
- **Inline mock generation for verify-work** — Replaced mock-generator subagent (~90s per mock) with direct inline method edits in the main context; eliminated test-overrides scaffolding (feature flags, injection points) in favor of temporary hardcoded return values
- **Batch-only mock subagent** — ms-mock-generator now reserved for 5+ mocks; removed generate-mocks workflow and updated mock-patterns reference for inline editing techniques

## [3.13.0] - 2026-02-11

Planning pipeline rework. Plans are now pure markdown prompts optimized for a single intelligent reader — no YAML frontmatter, no XML containers. Orchestration metadata (wave grouping, dependencies) separated from execution content into EXECUTION-ORDER.md. Executor workflow cut from 1,209 to 338 lines. Every token the executor loads now serves code output, not process ceremony. Net effect: executors start with more context headroom, plans read as direct instructions, and the system aligns with Claude Code's native plan conventions and prompting best practices.

### Changed
- **Pure markdown plans** — Plans use `## Context`, `## Changes`, `## Verification`, `## Must-Haves` sections; ~90% actionable content, ~10% structure
- **Executor workflow rewrite** — Execute-plan workflow reduced from 1,209 to 338 lines; conditional sections lazy-loaded instead of eagerly injected
- **EXECUTION-ORDER.md for wave orchestration** — Wave grouping and dependencies moved out of plan frontmatter into a dedicated orchestration file
- **Downstream format alignment** — Updated consolidator, check-phase, execute-phase, verify-phase, adhoc, verification-report, and roadmap templates for markdown plan terminology

### Fixed
- **Verification gaps** — Closed remaining stale frontmatter and must_haves references across verify-phase, plan-phase, and templates

## [3.12.0] - 2026-02-10

### Added
- **Mockup comparison page** — Design-phase auto-generates a side-by-side comparison page from mockup variants [MIN-81]

### Changed
- **Simplified configuration** — Removed depth, parallelization, and safety config flags; config.json reduced to subsystems + code_review only [MIN-77]
- **System context UI skill discovery** — Design-phase and review-design use system context for skill lookup instead of file-based globbing
- **Consolidated ms-meta references** — Merged discrete reference docs into conventions.md; removed separate architecture, concepts, and execution-model files
- **Plan-phase task summary** — Task breakdown displays a scannable numbered list instead of verbose XML output [MIN-80]

## [3.11.0] - 2026-02-09

### Added
- **Mock identification in verify-work** — Two-tier classification for test mocks: `mock_hints` frontmatter (populated during execution with `transient_states` and `external_data`) with keyword heuristics fallback [MIN-79]

### Changed
- **Dynamic UI skill discovery** — Design-phase and review-design commands discover project UI skills by reading SKILL.md frontmatter instead of hardcoded filename globs [MIN-75]
- **Removed checkpoint system** — Consolidated execution model into pure autonomous+orchestrator pattern; decisions move to planning phase via AskUserQuestion
- **Context engineering documentation** — Distinguished eager loading (@-references) vs lazy loading (read instructions), added context efficiency strategies and philosophy section

### Fixed
- **Stale checkpoint references** — Removed dangling references to removed checkpoint system across skill workflows and guidelines
- **`learn-flutter` gist operations** — Replaced WebFetch with `gh api` for reliable raw content retrieval; fixed gist update to use `jq --rawfile`

## [3.10.1] - 2026-02-08

### Added
- **Flutter command references** — `heal-docs` and `extract-pattern` reference documentation for Flutter skills
- **Flutter key principles** — Senior review principles and key coding guidelines in Flutter references

### Changed
- **Consolidated requirements into roadmap** — `/ms:define-requirements` merged into `/ms:create-roadmap` command
- **Consolidated milestone workflow** — `/ms:new-milestone` refined for collaborative discovery scope
- **Flutter reference reorganization** — Skills consolidated into main directory, pattern docs condensed, file naming normalized to hyphens

### Fixed
- **Execute-phase wave spawn** — Explicitly specifies `subagent_type="ms-executor"` preventing incorrect agent dispatch

## [3.10.0] - 2026-02-08

### Added
- **`/ms:release-notes` command** — Renamed from `/ms:whats-new` and `/ms:update` for clarity
- **`mockup-designer` agent** — Dedicated agent for HTML mockup generation extracted from design-phase
- **Design direction workflow** — Extracted mockup generation to dedicated workflow for design-phase
- **Subsystem metadata tagging** — `subsystem_hint` field on debug, adhoc, and phase artifacts for cross-cutting traceability
- **CE knowledge compounding** — Enhanced todo frontmatter and pattern surfacing for Compound Engineering integration
- **Curated learning extraction** — `/ms:complete-milestone` now extracts learnings during milestone completion
- **Plan risk assessment** — `/ms:plan-phase` adds risk assessment and verification step before plan approval
- **Context compliance verification** — Decision sections with compliance checks in context workflow
- **Discuss/design recommendations in roadmap** — Roadmap routing now suggests discuss/design phases
- **Last command tracking** — All `ms` commands track the last executed command in STATE.md
- **Phase number normalization** — All phase commands normalize phase numbers consistently
- **Progressive disclosure reference** — Context loading strategies guide for @-reference patterns

### Changed
- **New milestone discovery flow** — Refactored for collaborative goal exploration instead of prescriptive questioning
- **Audit milestone redesign** — Standalone `TECH-DEBT.md` as single source of truth for tech debt tracking
- **`/ms:do-work` renamed to `/ms:adhoc`** — Clearer naming for small adhoc work
- **Plan-phase lazy loading** — Branch-specific references loaded on-demand instead of eagerly
- **Verify-work lazy loading** — Branch-specific references loaded on-demand
- **Routing blocks extracted to reference files** — On-demand reference files for routing logic
- **Plan-phase delegation** — Plan-writing extracted to `ms-plan-writer` subagent for better context management

### Fixed
- **Audit milestone** — Added missing commit step and fixed filename typo
- **Research-phase** — Added missing git commit step for RESEARCH.md artifact

### Removed
- **`ms-milestone-auditor` agent** — Dead agent deleted with references cleaned up
- **`/ms:do-work` command name** — Renamed to `/ms:adhoc`

## [3.6.0] - 2026-01-29

### Added
- **`flutter-code-simplification` skill** — Reusable Flutter code simplification principles extracted into standalone SKILL.md for both `ms-flutter-code-quality` and `ms-flutter-simplifier` agents
- **`ms-flutter-code-quality` agent** — Three-pass code quality analysis (patterns, widgets, structure) with embedded guidelines and remote gist reference for fresh rules
- **`flutter-code-quality` skill** — Code quality skill covering anti-patterns, widget organization, folder structure conventions
- **Manifest-based file tracking** — Installer now tracks files with SHA-256 checksums in `.manifest.json` for automatic orphan cleanup when commands/agents are deleted
- **Interactive conflict resolution** — `--force` flag to skip prompts for locally modified files during installation

### Changed
- **`ms-flutter-code-quality` agent behavior** — Shifted from conservative reviewer to autonomous refactorer: applies guidelines unless verification fails, with "Preserve Behavior" as first non-negotiable principle
- **Simplified code quality output** — Removed "needs review" category; agent now makes binary decisions (fix when confident, leave unchanged when uncertain)
- **Release process** — npm publish step removed (requires manual authentication)

## [3.5.0] - 2026-01-28

### Added
- **Adhoc code review configuration** — New `code_review.adhoc` field in config.json for `/ms:adhoc` with cascade fallback (adhoc → phase → default)
- **`ms-flutter-reviewer` structural analysis** — New analyze-only reviewer for Flutter projects that reports findings without modifying code. At milestone level, offers binary choice: create quality phase or accept as tech debt

### Changed
- **Milestone code review default** — `/ms:audit-milestone` now defaults to `ms-flutter-reviewer` instead of `ms-code-simplifier`
- **Stack detection sets all code review fields** — `/ms:map-codebase` and `/ms:research-project` now configure all three levels (adhoc, phase, milestone) based on detected framework

## [3.4.0] - 2026-01-27

### Added
- **`flutter-senior-review` skill** — Senior engineering principles for Flutter/Dart code reviews. 12 principles organized into State & Types, Structure, Dependencies, and Pragmatism categories. Includes 3 core lenses (State Modeling, Responsibility Boundaries, Abstraction Timing) and individual principle files with detection signals, smell examples, and senior solutions.

### Changed
- **Restructured `ms-flutter-simplifier` agent** — Now principle-driven with focus on structural improvements rather than checklist-based review. Added Configuration section documenting simplifier options in `config.json`.

## [3.3.0] - 2026-01-26

### Added
- **Decision consolidation on milestone completion** — New `ms-consolidator` agent extracts decisions from phase artifacts (PLAN.md, CONTEXT.md, RESEARCH.md, DESIGN.md) into `v{X.Y}-DECISIONS.md` during `/ms:complete-milestone`. Decisions grouped by category (Technical Stack, Architecture, Data Model, API Design, UI/UX, Security, Performance)
- **Auto-simplification after phase execution** — Code simplifier agent runs automatically after `/ms:execute-phase` and `/ms:adhoc`, reviewing changes for clarity and maintainability. Stack-aware: uses `ms-flutter-simplifier` for Flutter projects (configurable in `config.json`)
- **Patch generation for adhoc** — `/ms:adhoc` now generates patches for complex discoveries, enabling execution in fresh context

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
- **`/gsd:adhoc` command** — Bridges gap between `/gsd:add-todo` (capture for later) and `/gsd:insert-phase` (full planning). Executes small adhoc work (max 2 tasks) with proper audit trail in `.planning/adhoc/` while keeping overhead proportional to work size
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

[Unreleased]: https://github.com/rolandtolnay/mindsystem/compare/v3.22.0...HEAD
[3.22.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.21.0...v3.22.0
[3.21.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.20.0...v3.21.0
[3.20.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.19.0...v3.20.0
[3.19.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.18.1...v3.19.0
[3.18.1]: https://github.com/rolandtolnay/mindsystem/compare/v3.18.0...v3.18.1
[3.18.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.17.1...v3.18.0
[3.17.1]: https://github.com/rolandtolnay/mindsystem/compare/v3.17.0...v3.17.1
[3.17.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.16.2...v3.17.0
[3.16.2]: https://github.com/rolandtolnay/mindsystem/compare/v3.16.1...v3.16.2
[3.16.1]: https://github.com/rolandtolnay/mindsystem/compare/v3.16.0...v3.16.1
[3.16.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.15.0...v3.16.0
[3.15.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.14.0...v3.15.0
[3.14.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.13.1...v3.14.0
[3.13.1]: https://github.com/rolandtolnay/mindsystem/compare/v3.13.0...v3.13.1
[3.13.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.12.0...v3.13.0
[3.12.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.11.0...v3.12.0
[3.11.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.10.1...v3.11.0
[3.10.1]: https://github.com/rolandtolnay/mindsystem/compare/v3.10.0...v3.10.1
[3.10.0]: https://github.com/rolandtolnay/mindsystem/compare/v3.6.0...v3.10.0
[3.6.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.6.0
[3.5.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.5.0
[3.4.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.4.0
[3.3.0]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.3.0
[3.2.3]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.2.3
[3.2.2]: https://github.com/rolandtolnay/mindsystem/releases/tag/v3.2.2
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
