<plan_format>

Plans are executable prompts for a single intelligent reader. ~90% actionable content, ~10% structure. Pure markdown — no XML containers, no YAML frontmatter.

A plan is Claude-executable when Claude can read the PLAN.md and start implementing without asking clarifying questions. If Claude has to guess, interpret, or make assumptions — the plan is too vague.

## Plan Anatomy

Every plan follows this structure:

```markdown
# Plan NN: Descriptive Title

**Subsystem:** auth | **Type:** tdd

## Context
Why this work exists. Approach chosen and why.

## Changes

### 1. Change title
**Files:** `src/path/to/file.ts`

Implementation details with inline code blocks where needed.

### 2. Another change
**Files:** `src/path/to/other.ts`, `src/path/to/related.ts`

Details referencing existing utilities: "Use `comparePassword` in `src/lib/crypto.ts`".

## Verification
- `npm test -- --grep auth` passes
- `curl -X POST localhost:3000/api/auth/login` returns 200 with Set-Cookie

## Must-Haves
- [ ] Valid credentials return 200 with Set-Cookie header
- [ ] Invalid credentials return 401
- [ ] Passwords compared with bcrypt, never plaintext
```

### Section Reference

| Section | Purpose | Required |
|---------|---------|----------|
| `# Plan NN: Title` | H1 with plan number and descriptive title | Yes |
| `**Subsystem:** X \| **Type:** Y \| **Skills:** Z` | Inline metadata (replaces YAML frontmatter) | Yes (type defaults to `execute`, skills optional) |
| `## Context` | Why this work exists, why this approach | Yes |
| `## Changes` | Numbered subsections with files and implementation details | Yes |
| `## Verification` | Bash commands and observable checks | Yes |
| `## Must-Haves` | Markdown checklist of user-observable truths | Yes |

---

## Context Section Guidance

The `## Context` section bridges the gap between plan-writer and executor. The executor starts with zero context beyond the plan — approach rationale compensates for this boundary.

**Include:**
- Problem being solved
- Approach chosen and WHY (constraints, trade-offs, rejected alternatives)
- Key dependencies or prior work referenced
- Technical context the executor needs to make correct decisions

**Exclude:**
- Rehash of the roadmap or project vision
- Generic background information
- Anything not specific to this plan's implementation decisions

**Example:**

```markdown
## Context
User authentication requires JWT tokens for the API layer. Using jose library
(not jsonwebtoken) because jsonwebtoken uses CommonJS which causes issues with
Next.js Edge runtime. Refresh token rotation prevents token theft — a single-use
refresh token invalidates on use and issues a new pair.

Prior plan 01 created the User model with `passwordHash` field in Prisma schema.
```

---

## Changes Section Guidance

Each `### N. Title` subsection is a coherent unit of work — a file group, a logical change, or a feature slice.

**Structure each subsection with:**
- `**Files:**` line listing exact paths
- Implementation details in prose with inline code blocks for critical snippets
- References to existing utilities with file paths: "Use `hashPassword` in `src/lib/crypto.ts`"
- Tables for configuration, mappings, or data structures
- Line number references when modifying existing files: "After the import block (~line 15)"

**Sizing:** Each subsection represents 15-60 minutes of Claude work. If a subsection takes multiple sessions, split it. If it's trivial, combine with a related subsection.

**Example:**

```markdown
### 2. Add password comparison utility
**Files:** `src/lib/crypto.ts`

Export `comparePassword(plain: string, hash: string): Promise<boolean>` using
bcrypt.compare. Import `bcrypt` from the existing dependency in package.json.

Follow the pattern of `hashPassword` already in this file (~line 8).
```

---

## Inline Metadata Specification

The metadata line sits directly below the H1 title:

```markdown
# Plan 03: Create login endpoint with JWT

**Subsystem:** auth | **Type:** tdd
```

### Subsystem

Matches vocabulary from the project's `config.json`. Used by the executor when generating SUMMARY.md after plan completion.

### Type

| Value | Behavior |
|-------|----------|
| `execute` | Default. Standard plan execution. Can be omitted. |
| `tdd` | Triggers lazy-load of `tdd-execution.md` reference during execution. Plan uses RED/GREEN/REFACTOR structure. |

When `**Type:**` is omitted, the plan defaults to `execute`.

### Skills

| Value | Behavior |
|-------|----------|
| *(omitted)* | No skills loaded. Skill discovery happens during `/ms:plan-phase` — absence means none were relevant. |
| `skill-a, skill-b` | Executor invokes listed skills via Skill tool before implementing. |

Skills are confirmed by the user during `/ms:plan-phase` and encoded into plans. Comma-separated list of skill names matching entries in the system-reminder.

---

## Must-Haves Specification

The `## Must-Haves` section is a markdown checklist consumed by ms-verifier. Each item is a user-observable truth — not an implementation detail.

**Good (observable truths):**
- `- [ ] Valid credentials return 200 with Set-Cookie header`
- `- [ ] Passwords are hashed, never stored plaintext`
- `- [ ] Unauthenticated requests to /api/protected return 401`

**Bad (implementation details):**
- `- [ ] bcrypt library installed`
- `- [ ] JWT_SECRET in .env file`
- `- [ ] Auth middleware created`

The verifier derives artifacts and key_links from the `## Changes` section. Must-haves focus on what the user can observe or verify.

---

## EXECUTION-ORDER.md Specification

Execution order lives in a single `EXECUTION-ORDER.md` file alongside the plans. Individual plans carry no wave numbers or dependency declarations.

**Format:**

```markdown
# Execution Order

## Wave 1 (parallel)
- 03-01-PLAN.md — Database schema and Prisma client
- 03-02-PLAN.md — Environment configuration

## Wave 2 (parallel)
- 03-03-PLAN.md — Auth endpoints (depends on schema from 01)
- 03-04-PLAN.md — User profile CRUD (depends on schema from 01)

## Wave 3
- 03-05-PLAN.md — Protected route middleware (depends on auth from 03)
```

**Rules:**
- Generated by plan-writer alongside plans
- Read by execute-phase orchestrator for wave grouping
- Plans within a wave execute in parallel
- Single source of truth for execution structure
- Human-readable, easy to override by editing directly

---

## Cross-Reference Table

| Question | Answer |
|----------|--------|
| How does the verifier find must-haves? | Reads `## Must-Haves` section |
| How does the executor know the subsystem? | Reads inline metadata (`**Subsystem:**`) |
| How does the plan-checker validate plans? | Reads EXECUTION-ORDER.md + plan structure |
| What triggers TDD lazy-loading? | `**Type:** tdd` in inline metadata |
| How does the executor know why an approach was chosen? | Reads `## Context` section |
| How does the executor find existing utilities? | Reads `**Files:**` lines and inline references in `## Changes` |
| What triggers skill loading in executor? | `**Skills:**` in inline metadata. No skills loaded if omitted. |

---

## What Plans Do NOT Contain

- **No YAML frontmatter** — metadata is inline markdown
- **No XML containers** — pure markdown throughout
- **No wave numbers or dependency declarations** — centralized in EXECUTION-ORDER.md
- **No file ownership lists** — centralized in EXECUTION-ORDER.md
- **No `<output>` or `<execution_context>` sections** — executor handles these inline
- **No summary template references** — executor loads templates as needed

---

## Examples

### Simple Plan: CRUD Endpoint

```markdown
# Plan 01: Create user profile CRUD endpoints

**Subsystem:** api

## Context
The API needs basic user profile management. Using Next.js route handlers with
Prisma ORM. The User model already exists in the schema (created during project
init).

## Changes

### 1. Create GET /api/users/[id] endpoint
**Files:** `src/app/api/users/[id]/route.ts`

Route handler accepting `id` param. Query User by ID with Prisma. Return 200
with user JSON (exclude passwordHash). Return 404 if not found.

### 2. Create PATCH /api/users/[id] endpoint
**Files:** `src/app/api/users/[id]/route.ts`

Accept JSON body with optional `name` and `email` fields. Validate email format
with regex. Update User with Prisma. Return 200 with updated user. Return 404
if not found, 400 if validation fails.

## Verification
- `curl localhost:3000/api/users/1` returns 200 with user JSON
- `curl -X PATCH localhost:3000/api/users/1 -d '{"name":"New"}' -H 'Content-Type: application/json'` returns 200
- `curl localhost:3000/api/users/999` returns 404

## Must-Haves
- [ ] GET /api/users/:id returns user profile without password hash
- [ ] PATCH /api/users/:id updates name and email
- [ ] Invalid user ID returns 404
- [ ] Invalid email format returns 400
```

### Complex Plan: Auth with Approach Rationale

```markdown
# Plan 03: Create login endpoint with JWT

**Subsystem:** auth | **Type:** execute

## Context
User authentication for the API layer. Using jose library instead of
jsonwebtoken — jsonwebtoken uses CommonJS which causes issues with Next.js Edge
runtime. Tokens use httpOnly cookies (not Authorization headers) to prevent XSS
token theft.

Refresh token rotation: each refresh token is single-use. On refresh, the old
token is invalidated and a new access/refresh pair is issued. This limits the
window of a stolen refresh token.

Prior plan 01 created the User model with `passwordHash` field in Prisma schema.

## Changes

### 1. Create POST /api/auth/login endpoint
**Files:** `src/app/api/auth/login/route.ts`

POST endpoint accepting `{email, password}`. Query User by email with Prisma.
Compare password using `comparePassword` in `src/lib/crypto.ts` (created in
plan 02). On match, create access JWT (15-min expiry) and refresh JWT (7-day
expiry) with jose. Set both as httpOnly cookies. Return 200 with user profile.
On mismatch, return 401 with generic "Invalid credentials" message.

### 2. Create POST /api/auth/refresh endpoint
**Files:** `src/app/api/auth/refresh/route.ts`

Read refresh token from cookie. Verify with jose. Look up token in
RefreshToken table — if not found or already used, return 401. Mark current
token as used. Issue new access + refresh pair. Set cookies. Return 200.

### 3. Add RefreshToken model to schema
**Files:** `prisma/schema.prisma`

Add RefreshToken model with fields: `id`, `token` (unique), `userId` (relation
to User), `used` (boolean, default false), `expiresAt` (DateTime), `createdAt`.
Run `npx prisma db push` after schema change.

## Verification
- `curl -X POST localhost:3000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"test@test.com","password":"test123"}'` returns 200 with Set-Cookie headers
- Login with wrong password returns 401
- Refresh endpoint with valid cookie returns new tokens
- Refresh endpoint with used token returns 401

## Must-Haves
- [ ] Valid credentials return 200 with httpOnly cookie containing JWT
- [ ] Invalid credentials return 401 with generic error message
- [ ] Refresh token rotation invalidates used tokens
- [ ] Passwords compared with bcrypt, never plaintext
```

### TDD Plan: Pure Markdown RED/GREEN/REFACTOR

```markdown
# Plan 04: Email validation utility

**Subsystem:** validation | **Type:** tdd

## Context
Multiple endpoints need email validation (registration, profile update, invite).
Centralizing in a utility prevents inconsistent validation rules. Using TDD
because the function has clear inputs/outputs and edge cases that benefit from
test-first design.

## Changes

### 1. RED — Write failing tests
**Files:** `src/lib/__tests__/validate-email.test.ts`

Test cases:
- Valid: `user@example.com`, `name+tag@domain.co.uk` → returns true
- Invalid: `@domain.com`, `user@`, `user@.com`, empty string, `null` → returns false
- Edge: very long local part (>64 chars), very long domain (>255 chars) → returns false

Import `validateEmail` from `src/lib/validate-email.ts` (does not exist yet).
Run tests — all must fail with import/function error.

### 2. GREEN — Implement minimal validation
**Files:** `src/lib/validate-email.ts`

Export `validateEmail(email: string): boolean`. Use regex matching RFC 5322
simplified pattern. Handle null/undefined input by returning false. No
optimization — just make tests pass.

### 3. REFACTOR — Extract regex constant
**Files:** `src/lib/validate-email.ts`

Extract regex to `EMAIL_REGEX` constant at module level. Add JSDoc with
examples. Run tests — all must still pass. Only commit if changes improve
readability.

## Verification
- `npm test -- --grep "validate-email"` passes all cases
- Import works from other modules without errors

## Must-Haves
- [ ] Valid email addresses return true
- [ ] Invalid email addresses return false
- [ ] Edge cases (length limits, null input) handled correctly
```

---

## Specificity Guidelines

### Too Vague

```markdown
### 1. Add authentication
**Files:** ???

Implement auth.
```

Claude: "How? What type? What library? Where?"

### Just Right

```markdown
### 1. Create login endpoint with JWT
**Files:** `src/app/api/auth/login/route.ts`

POST endpoint accepting {email, password}. Query User by email, compare
password with bcrypt. On match, create JWT with jose library, set as httpOnly
cookie (15-min expiry). Return 200. On mismatch, return 401. Use jose instead
of jsonwebtoken (CommonJS issues with Edge).
```

Claude can implement this immediately.

### Too Detailed

Writing the actual code in the plan. Trust Claude to implement from clear instructions — specify WHAT and WHY, not the exact lines of code.

---

## Anti-Patterns

### Vague Actions

- "Set up the infrastructure"
- "Handle edge cases"
- "Make it production-ready"
- "Add proper error handling"

These require Claude to decide WHAT to do. Specify it.

### Unverifiable Completion

- "It works correctly"
- "User experience is good"
- "Code is clean"
- "Tests pass" (which tests? do they exist?)

These require subjective judgment. Make it objective.

### Missing Context

- "Use the standard approach"
- "Follow best practices"
- "Like the other endpoints"

Claude has no memory of your standards across contexts. Be explicit.

### Implementation-Detail Must-Haves

- "bcrypt library installed"
- "Middleware file created"
- "ENV variable added"

Must-haves are user-observable truths. The verifier checks outcomes, not internals.

</plan_format>
