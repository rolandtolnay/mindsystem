---
title: Consistent Error Handling
category: pragmatism
impact: MEDIUM
impactDescription: Improves UX and debugging
tags: error-handling, try-catch, error-boundaries, consistency
---

## Consistent Error Handling

Adopt one error handling strategy and apply it everywhere. Ad-hoc try/catch leads to inconsistent UX and swallowed errors.

**Detection signals:**
- Errors appear differently across screens (toasts vs dialogs vs inline vs nothing)
- try/catch blocks scattered in component/handler code with different recovery strategies
- Inconsistent error messaging (raw exceptions shown to users in some places)
- No standard retry mechanism
- Some code paths silently swallow errors with empty catch blocks

**Why it matters:**
- Users get a consistent experience when things go wrong
- Developers follow one pattern — no decision fatigue per error site
- Error states are explicit and testable, not hidden in catch blocks
- Debugging is faster: errors flow through a known path

**Senior pattern:** Establish a single error handling strategy for the project: errors flow through a known path (Result types, error boundaries, middleware, or global handlers) and surface to users through one consistent mechanism. Individual call sites don't decide how to present errors — they report them, and the strategy handles presentation. Empty catch blocks are banned; if an error is truly ignorable, document why.

**Detection questions:**
- Do errors appear differently across different screens or endpoints?
- Are try/catch blocks scattered with different recovery strategies?
- Are there empty catch blocks that silently swallow errors?
- Is there a standard, documented error handling strategy for the project?
