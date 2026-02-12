# Skill Description Guide

Reference for writing YAML `description` fields that Claude Code reliably discovers and invokes.

## How Matching Works

Claude sees skills as a flat list of `- name: description` in a system-reminder. It matches user intent against this single string. The `name` carries semantic weight — don't repeat what the name already conveys.

## Description Template

```
[What it does — distinct verb]. Use [when/after] [concrete trigger conditions].
[Optional: specific user phrases or artifacts].
[Optional: Do NOT use when... (only if overlapping skills exist)].
```

**Target length:** 25-35 words. Under 20 is too sparse for matching. Over 50 wastes context budget loaded into every session.

## Principles

### Lead with a distinct verb, not a category label

```
BAD:  "Flutter/Dart code simplification principles."
GOOD: "Reduce complexity in Flutter/Dart code."
```

The verb ("Reduce", "Organize", "Review", "Create") is the primary differentiator when multiple skills share a domain.

### Use user vocabulary, not expert vocabulary

```
BAD:  "clarity and maintainability"
GOOD: "too nested, hard to read, or has duplication"
```

Users say "clean up this file" not "apply code quality guidelines." Match their words.

### Add trigger conditions with "Use when"

```
BAD:  "Guide for creating MCP servers"
GOOD: "Create MCP servers... Use when building custom integrations, APIs, or data sources via MCP"
```

Every description needs a "Use when" clause. Without it, Claude must infer when to invoke — lowering confidence below the invocation threshold.

### Disambiguate overlapping skills

When multiple skills share a domain, each needs naturally exclusive trigger vocabulary:

| Skill | Distinct Verb | Distinct Trigger |
|-------|--------------|-----------------|
| flutter-senior-review | "Review...for issues" | "reviewing PRs, auditing design" |
| flutter-code-quality | "Organize...to follow conventions" | "after implementation, restructure folders" |
| flutter-code-simplification | "Reduce complexity" | "too nested, hard to read, duplication" |

Anti-triggers ("Do NOT use for X") are a fallback — distinct vocabulary is better and costs fewer tokens.

### Don't start with "Expert guidance for"

Generic openers waste tokens and add no matching signal. Lead with the action.

```
BAD:  "Expert guidance for creating, building, and using Claude Code hooks."
GOOD: "Create and configure Claude Code hooks for event-driven automation."
```

### Anchor to concrete artifacts when possible

```
BAD:  "Use when working with skills"
GOOD: "Use when authoring new SKILL.md files"
```

File names, tool names, and format extensions (`.pptx`, `SKILL.md`, `agents/`) are strong matching signals.

## Gold Standard Examples

**Trigger-first with user phrases:**
```yaml
description: >
  Use when the user wants to customize keyboard shortcuts, rebind keys,
  add chord bindings, or modify ~/.claude/keybindings.json. Examples:
  "rebind ctrl+s", "add a chord shortcut", "change the submit key".
```

**Intent-mapping with quoted patterns:**
```yaml
description: >
  Helps users discover and install agent skills when they ask questions
  like "how do I do X", "find a skill for X", "is there a skill that
  can...", or express interest in extending capabilities.
```

**File-format with boundaries:**
```yaml
description: >
  Use this skill any time a .pptx file is involved in any way — as input,
  output, or both. Trigger whenever the user mentions "deck," "slides,"
  "presentation," or references a .pptx filename. If a .pptx file needs
  to be opened, created, or touched, use this skill.
```

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| "Expert guidance for creating, building, and using..." | Generic opener, wastes tokens |
| "principles" / "guidelines" / "best practices" | Category labels, not trigger signals |
| "reviewing, refactoring, or cleaning up" on 3 skills | Identical triggers = ambiguity = no invocation |
| Description under 15 words | Not enough surface for semantic matching |
| Repeating the skill name in the description | Name already carries that signal for free |
