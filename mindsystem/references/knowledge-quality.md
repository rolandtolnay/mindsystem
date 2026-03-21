<knowledge_quality>

Shared quality gate for knowledge extraction. Referenced by ms-consolidator and ms-compounder agents.

<filtering_principle>

**The single test:** "Would an LLM implement this incorrectly without this entry?"

If yes — the entry earns its place. If an LLM with access to the codebase would get it right anyway, the entry is noise.

What passes the test:
- Conventions that differ from LLM defaults or framework norms
- Failed experiments and why they failed (prevents re-discovery)
- Non-obvious bugs, gotchas, or workarounds
- Decisions where the alternative was reasonable (the "because" matters)
- Cross-cutting patterns not visible from a single file

</filtering_principle>

<fails_the_test>

These categories consistently fail the filtering test. Drop them during extraction.

| Category | Why It Fails | Example |
|----------|-------------|---------|
| Design tokens (colors, spacing, typography) | Readable from code/config files | "Primary: #6366F1, spacing-md: 16px" |
| Component API descriptions | Readable from component source | "SubscriptionCard accepts `plan`, `onSelect` props" |
| Schema/model field listings | Readable from schema files | "User has fields: id, email, name, createdAt" |
| Version pins without rationale | Readable from package.json/lockfile | "Using React 18.2.0" |
| Decisions without alternatives | No "because" = no reusable knowledge | "Using Tailwind for styling" (vs. what?) |
| Implementation descriptions | Restates what the code does | "Login endpoint hashes password and returns JWT" |

</fails_the_test>

<passes_the_test>

Concrete examples that earn their place — each would cause incorrect implementation without the entry.

1. **FieldMask casing (gRPC):** FieldMask paths must use camelCase in JSON, not snake_case — proto3 JSON mapping silently drops snake_case paths. LLMs default to snake_case matching proto definitions.

2. **keepAlive auto-dispose (Flutter):** Riverpod providers with `keepAlive()` in `autoDispose` family providers — calling `keepAlive()` inside `ref.onDispose` creates a retain cycle. Dispose callback never fires, provider leaks. Place `keepAlive()` in the provider body before any async gap.

3. **HiveField index stability:** HiveField indices are permanent storage keys — changing an index silently corrupts existing user data. New fields must use the next unused index, never reuse or reorder.

4. **do/while pagination (API):** Firestore `startAfter` cursor pagination requires do/while, not while — a while loop with an empty-page exit condition misses the last partial page when `limit` equals page size exactly.

5. **Payment timeout (Stripe):** Stripe webhook delivery retries for up to 72 hours. Payment confirmation UI must show "processing" state, not assume success/failure within a session.

6. **Interceptor ordering (Dio):** Dio interceptors run in addition order for requests but reverse order for responses/errors. Auth token injection must be added first to run last on error (so retry logic sees the refreshed token).

</passes_the_test>

<decision_quality_test>

Not every decision is knowledge. Apply this secondary filter:

**"Could a reasonable agent have chosen differently?"**

- **Pass:** "jose over jsonwebtoken — better TypeScript types and actively maintained" → Yes, jsonwebtoken is the more common choice. The rationale prevents revisiting.
- **Pass:** "httpOnly cookies over localStorage for JWT — XSS prevention" → Yes, localStorage is the LLM default. Without this entry, an LLM would likely use localStorage.
- **Fail:** "Using TypeScript for type safety" → No reasonable agent would choose plain JS for a new project. This is a default, not a decision.
- **Fail:** "Using ESLint for linting" → No alternative was seriously considered. Not knowledge.

</decision_quality_test>

<cross_subsystem_dedup>

Before writing an entry, check whether it already exists in another subsystem's knowledge file.

- If the entry belongs primarily to another subsystem, add a cross-reference: `(see {subsystem})` instead of duplicating.
- If the entry spans multiple subsystems equally, place it in the most upstream subsystem and cross-reference from others.
- If an existing duplicate is found during extraction, remove it from the less-relevant file and cross-reference.

</cross_subsystem_dedup>

<existing_content_review>

On every write to a knowledge file, review the touched file's existing entries:

- **Still relevant?** Remove entries for features/patterns that no longer exist.
- **Code-derivable now?** Remove entries that were non-obvious when written but are now self-evident from the codebase (e.g., a pattern that was novel is now standard in the project).
- **Superseded?** Update or remove entries contradicted by new decisions.
- **Duplicated?** Check against other knowledge files — deduplicate using cross-references.

This is opportunistic maintenance during normal writes, not a full audit.

</existing_content_review>

</knowledge_quality>
