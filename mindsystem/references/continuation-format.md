# Continuation Format

Standard format for presenting next steps after completing a command or workflow.

## Core Structure

```
---

## ▶ Next Up

`{command to copy-paste}` — {one-line description}

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `{alternative option 1}` — description
- `{alternative option 2}` — description

---
```

When there's meaningful additional context (like a phase identifier), add it as a header line:

```
**Phase {N}: {Name}** — {Goal}

`/ms:plan-phase {N}`
```

## Format Rules

1. **Command is the anchor** — backtick command + description on one line, no separate bold label restating the command name
2. **Phase identifiers are additive context** — `**Phase 2: Auth**` carries info the command doesn't; bold labels like `**Plan gap closure**` just restate `/ms:plan-phase --gaps` and should be omitted
3. **Pull context from source** — ROADMAP.md for phases, PLAN.md `<objective>` for plans
4. **Command in inline code** — backticks, easy to copy-paste, renders as clickable link
5. **`/clear` explanation** — always include, keeps it concise but explains why
6. **"Also available" not "Other options"** — sounds more app-like
7. **Visual separators** — `---` above and below to make it stand out

## Variants

### Execute Next Phase

```
---

## ▶ Next Up

**Phase 2: Authentication** — JWT login with refresh tokens

`/ms:execute-phase 2`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- Review plans before executing
- `/ms:discuss-phase 2` — gather context and validate assumptions

---
```

### Execute Final Phase in Milestone

Add note that this is the last phase and what comes after:

```
---

## ▶ Next Up

**Phase 3: Core Features** — User dashboard, settings, and data export
<sub>Final phase in milestone</sub>

`/ms:execute-phase 3`

<sub>`/clear` first → fresh context window</sub>

---

**After this completes:**
- Milestone complete
- Next: `/ms:complete-milestone` — archive milestone

---
```

### Plan a Phase

```
---

## ▶ Next Up

**Phase 2: Authentication** — JWT login flow with refresh tokens

`/ms:plan-phase 2`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:discuss-phase 2` — gather context first
- `/ms:research-phase 2` — investigate unknowns
- Review roadmap

---
```

### Phase Complete, Ready for Next

Show completion status before next action:

```
---

## ✓ Phase 2 Complete

3/3 plans executed

## ▶ Next Up

**Phase 3: Core Features** — User dashboard, settings, and data export

`/ms:plan-phase 3`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:discuss-phase 3` — gather context first
- `/ms:research-phase 3` — investigate unknowns
- Review what Phase 2 built

---
```

### Multiple Equal Options

When there's no clear primary action:

```
---

## ▶ Next Up

**Phase 3: Core Features** — User dashboard, settings, and data export

**To plan directly:** `/ms:plan-phase 3`

**To discuss context first:** `/ms:discuss-phase 3`

**To research unknowns:** `/ms:research-phase 3`

<sub>`/clear` first → fresh context window</sub>

---
```

### Milestone Complete

```
---

## 🎉 Milestone Complete

All 4 phases shipped

## ▶ Next Up

`/ms:new-milestone` — discover what to build next

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- Review accomplishments before moving on

---
```

## Pulling Context

### For phases (from ROADMAP.md):

```markdown
### Phase 2: Authentication
**Goal**: JWT login flow with refresh tokens
```

Extract: `**Phase 2: Authentication** — JWT login flow with refresh tokens`

### For plans (from ROADMAP.md):

```markdown
Plans:
- [ ] 02-03: Add refresh token rotation
```

Or from PLAN.md `<objective>`:

```xml
<objective>
Add refresh token rotation with sliding expiry window.

Purpose: Extend session lifetime without compromising security.
</objective>
```

Extract: `**02-03: Refresh Token Rotation** — Add /api/auth/refresh with sliding expiry`

## Anti-Patterns

### Don't: Command-only (no context)

```
## To Continue

Run `/clear`, then paste:
/ms:execute-phase 2
```

User has no idea what Phase 2 is about.

### Don't: Missing /clear explanation

```
`/ms:plan-phase 3`

Run /clear first.
```

Doesn't explain why. User might skip it.

### Don't: "Other options" language

```
Other options:
- Review roadmap
```

Sounds like an afterthought. Use "Also available:" instead.

### Don't: Fenced code blocks for commands

```
```
/ms:plan-phase 3
```
```

Fenced blocks inside templates create nesting ambiguity. Use inline backticks instead.
