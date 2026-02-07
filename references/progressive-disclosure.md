# Progressive Disclosure: Eager vs Lazy Loading

How context loading works in Mindsystem and when to use each mechanism.

## Core Principle

Context is consumed at read time, not at file-exist time. A file on disk costs nothing. A file loaded into context costs tokens. The only question that matters: **does this text enter Claude's context window during this invocation?**

## Loading Mechanisms

### Eager Loading (`@-references`)

`@-references` in `<execution_context>` load before any logic executes. Content enters context regardless of which code path is taken.

```markdown
<execution_context>
@~/.claude/mindsystem/workflows/execute-phase.md
@~/.claude/mindsystem/references/checkpoints.md    <!-- always loaded -->
</execution_context>
```

**Use for:** Content needed on every invocation — routing tables, shared definitions, decision criteria.

### Lazy Loading (conditional `Read`)

`Read` inside a conditional branch fires only when that branch is taken. Content enters context only when needed.

```markdown
If milestone complete:
  Use the Read tool to load ~/.claude/mindsystem/references/milestone-complete-routing.md
  Follow its template instructions.

If gap closure needed:
  Use the Read tool to load ~/.claude/mindsystem/references/gap-closure-routing.md
  Follow its template instructions.
```

**Use for:** Branch-specific content — output templates, specialized instructions, per-route formatting.

### Key Distinction

Extracting content into a separate file but `@-referencing` it at the top of a command saves zero context. The file is smaller, but every byte still enters the context window. **Only conditional `Read` achieves actual context savings.**

## The Pattern: Conditional Branch Extraction

When a command or workflow has branching paths where only one branch executes per invocation, apply this pattern:

1. **Keep decision criteria inline.** The routing table (if/else logic) stays in the command. It's small and must be evaluated before any loading.
2. **Extract branch content into reference files.** Output templates, formatting blocks, and specialized instructions move to separate files.
3. **Load via conditional `Read`.** Each branch calls `Read` for its template file. Only the winning branch's content enters context.
4. **Group by semantic purpose, not source command.** If two commands share the same branch template (e.g., "milestone complete" routing), use ONE reference file for both. Context savings AND deduplication.

### When to Apply

- Command/workflow has 3+ branches where only one fires per invocation
- Branch content exceeds ~20 lines (below this, extraction overhead isn't worth it)
- Branch content is output-oriented (templates, formatting) rather than logic-oriented
- Same branch template appears across multiple commands (cross-command reuse)

### When NOT to Apply

- Branch content is small (<20 lines) with no cross-command reuse
- Content is logic-heavy and needs surrounding context to execute correctly
- The branch content is already loaded eagerly for other reasons

## Case Study: Routing Block Extraction

The routing commands (`progress.md`, `execute-phase.md`, `audit-milestone`) demonstrate this pattern.

**Problem:** Each command contains 5-6 route branches. A routing decision produces exactly ONE winner. The other branches are dead weight consuming context.

**Analysis:** Claude needs two things per route — decision criteria (which route?) and output template (what to show). Decision criteria must stay inline. Only the output template can be extracted.

**Cross-command reuse discovered:**
- "Milestone complete" routing — appears in `execute-phase` and `progress`
- "Gap closure" routing — appears in `execute-phase` and `progress`
- "Next phase" routing — appears in `execute-phase`, `verify-work`, and `progress`

**Result:** Shared reference files grouped by semantic route, loaded conditionally. Each command keeps a lean routing table (~20 lines) with conditional `Read` calls per branch.

**Extraction threshold applied:**
- Routes A/B in `progress.md` (~17-40 lines, single-command use) — left inline or borderline
- Routes D/E/F (~30+ lines, cross-command reuse) — extracted to shared reference files
- `audit-milestone` routes (~110 lines total) — extracted due to sheer size
