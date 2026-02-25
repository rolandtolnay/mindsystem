---
title: Single Source of Truth
category: state
impact: HIGH
impactDescription: Prevents stale data bugs
tags: state-management, derived-state, duplication, synchronization
---

## Single Source of Truth

One owner per piece of state. Derive everything else via selectors, computed properties, or transformations — never duplicate.

**Detection signals:**
- Same data stored in both global state and local component state
- Effect hooks syncing local state from global state
- Two sources of truth that could disagree
- Derived data being cached in state instead of computed on access
- Manual synchronization logic between stores or contexts

**Why it matters:**
- No "which value is authoritative?" confusion
- State updates propagate automatically through derivations
- Easier debugging: one place to inspect each piece of state
- Eliminates stale data bugs caused by desynchronized copies

**Senior pattern:** Identify the single authoritative owner for each piece of state. All other consumers read from that owner or derive values from it. Local component state is reserved for truly ephemeral UI concerns (focus, hover, animation progress) that no other component needs. If two components need the same state, lift it to a shared owner rather than syncing copies.

**Detection questions:**
- Is the same data stored in both a global store and local component state?
- Are there effect hooks whose sole purpose is syncing one state source to another?
- Could two sources of truth disagree? What happens when they do?
- Is derived data being cached in state instead of computed from the source?
