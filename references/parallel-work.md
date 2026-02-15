# Parallel Work Guide

Running multiple Mindsystem sessions on the same project simultaneously. Covers what's safe, what conflicts, and the optimal pattern.

## How isolation works

Each phase writes artifacts to its own directory (`.planning/phases/01-name/`, `02-name/`). Commands share STATE.md and ROADMAP.md as readers, but only `execute-phase` modifies them structurally. No file locks exist — git commits act as coordination checkpoints.

## The one pattern that matters

**Execute phase N in one session, prepare phase N+1 in another.**

Execution is the longest operation (multiple subagent waves). While it runs autonomously, start discussing, researching, or designing the next phase in a separate session. Different phase directories, zero file conflicts.

```
Session A                          Session B
─────────────────────────────────  ─────────────────────────────
execute-phase 1  ───────────────→  discuss-phase 2
         │                              │
    verify-work 1                  research-phase 2
                                        │
                                   plan-phase 2
                                        │
                                   execute-phase 2 ──→ discuss-phase 3
```

## The one rule that matters

**Never run two execute-phase commands at the same time** — regardless of phase number. Both modify STATE.md progress counters, ROADMAP.md completion status, and implementation files. Race conditions cause lost work.

## Safe combinations

| Session A | Session B | Safe? |
|---|---|---|
| `execute-phase N` | `discuss-phase N+1` | Yes |
| `execute-phase N` | `design-phase N+1` | Yes |
| `execute-phase N` | `research-phase N+1` | Yes |
| `execute-phase N` | `plan-phase N+1` | Yes |
| `plan-phase N` | `discuss-phase N+1` | Yes |
| `verify-work N` | `discuss-phase N+1` | Yes |
| `discuss-phase N` | `research-phase N` | Yes (but misses cross-context) |
| `design-phase N` | `research-phase N` | Yes (but misses cross-context) |
| Any command | `progress`, `check-todos`, `add-todo` | Yes (read-only) |

## Unsafe combinations

| Combination | Risk |
|---|---|
| Two `execute-phase` (any phases) | STATE.md and ROADMAP.md race conditions, file collisions |
| `execute-phase` + `adhoc` | Both modify implementation files and STATE.md |
| `execute-phase` + `complete-milestone` | Milestone rewrites STATE.md and ROADMAP.md |
| `create-roadmap` + any phase command | Roadmap creation overwrites ROADMAP.md |

## Interactive vs autonomous windows

Some commands have two phases — interactive (needs user attention) then autonomous (subagent takes over). The parallel window opens at the autonomous handoff:

- **plan-phase:** Interactive task identification (steps 1-8), then `ms-plan-writer` subagent generates plans autonomously
- **design-phase:** Context gathering and Q&A, then `ms-designer` subagent generates DESIGN.md autonomously
- **research-phase:** Brief setup, then 3 parallel researcher subagents run autonomously
- **execute-phase:** Brief setup, then wave-based executor subagents run autonomously

Once a command goes autonomous, start the next piece of work in another session.

## Sequential dependencies (per phase)

These must complete in order — each step's output feeds the next:

```
discuss-phase N ─┐
                 ├──→ plan-phase N ──→ execute-phase N ──→ verify-work N
design-phase N  ─┤
                 │
research-phase N ┘
```

The pre-planning commands (discuss, design, research) are optional and independent of each other, but all must finish before `plan-phase` to get full benefit.

## Bootstrap chain (one-time, strictly sequential)

```
new-project → research-project (optional) → create-roadmap → phase work
```
