<browser_verification>

# Browser Verification Reference

Lazily loaded by execute-phase when `ms-tools browser-check` returns READY (exit 0).

## Auth Flow

Handle browser authentication before spawning the verifier agent.

**Step 1: Check for existing auth state**

```bash
AUTH_STATE=".agent-browser-state.json"
[ -f "$AUTH_STATE" ] && echo "HAS_STATE" || echo "NO_STATE"
```

**Step 2: Detect dev server URL**

Probe common ports to find the running dev server:

```bash
for PORT in 5173 3000 8080 4200 3001; do
  curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" 2>/dev/null | grep -q "200\|301\|302" && echo "http://localhost:$PORT" && break
done
```

Store the result as `{dev_url}`.

**Step 3: Validate or establish auth**

If `HAS_STATE`:
1. Open app headless at `{dev_url}`
2. Check current URL — if redirected to a login/auth path, auth has expired
3. If still on app pages: auth valid, proceed to Derive User Journeys

If `NO_STATE` or auth expired:
1. Close headless browser
2. Open `{dev_url}` in **headed** mode (visible browser)
3. Use AskUserQuestion:
   - header: "Browser authentication"
   - question: "Please log in to the app in the browser window. Select 'Done' when you've logged in."
   - options: ["Done — I'm logged in", "Skip browser verification"]
4. If user logged in: save browser state to `.agent-browser-state.json`, close headed browser, ensure gitignored:
   ```bash
   grep -q "\.agent-browser-state\.json" .gitignore 2>/dev/null || echo '.agent-browser-state.json' >> .gitignore
   ```
5. If user skips: proceed to code_review, skip browser verification

## Derive User Journeys

Transform SUMMARY.md accomplishments into user journeys for the browser verifier.

**Step 1: Read summaries**

Read all `*-SUMMARY.md` files from the phase directory.

**Step 2: Extract per-summary**

For each SUMMARY, extract:
- **Accomplishments** section
- **mock_hints** frontmatter (if present) — specifically `external_data` entries
- **key-files** frontmatter (if present) — for route inference

**Step 3: Derive user journeys**

For each user-observable accomplishment, derive a journey:
- `name`: verb-first — what the user is trying to accomplish (e.g., "Create a new project via the Add button")
- `start`: page reachable via sidebar/nav (NOT a deep URL)
- `steps`: ordered actions — click, fill, submit, verify state change
- `success`: what should be true after completing the journey
- `needs_backend_data`: true/false (from mock_hints `external_data` entries)

**Derivation rules:**
- New pages/routes: journey starts from parent page, navigates via UI
- Forms: MUST include fill AND submit
- Toggles/filters: MUST include activate AND deactivate
- CRUD: one journey per built operation
- Modals: open, interact, confirm — not just "modal opens"

**Step 4: Filter**

Include: UI renders, navigation, forms, data display, visual states, user interactions — each as a complete journey.
Exclude: refactors, type changes, API internals, test files, build config, non-visual changes.

**Step 5: Group and format**

Group journeys by starting area for efficient navigation. Format as a numbered list:

```
1. **{name}**
   Start: {start page/area}
   Steps:
   - {action 1}
   - {action 2}
   Success: {what should be true after}
   Needs backend data: {yes/no}

2. **{name}**
   ...
```

## Spawn

Spawn the browser verifier agent after auth is established and journeys are derived.

The orchestrator must pass `{screenshots_dir}` as a fully resolved path (e.g., `.planning/phases/04-comments/screenshots` or `.planning/adhoc/fix-auth/screenshots`). The browser verifier does not resolve paths — it uses whatever directory is provided.

```
Task(
  prompt="Run browser verification.

Dev URL: {dev_url}
Auth state: .agent-browser-state.json
Screenshots directory: {screenshots_dir}

## User Journeys

{derived_journeys}

## Backend Context

{summary of which journeys need real backend data — from mock_hints external_data entries.
Journeys needing backend data may show empty states or errors — mark as ENVIRONMENT_BLOCKED, not ISSUE.}

Complete each user journey end-to-end. Save all screenshots to {screenshots_dir}/.
Fix trivial issues inline. Return structured report.",
  subagent_type="ms-browser-verifier"
)
```

## Post-Verifier Handling

Route based on the report's **Status** field:

**`environment_blocked`:**
Surface the blocker description and screenshot evidence to the user. Use AskUserQuestion:
- header: "Browser verification blocked"
- question: "The browser verifier hit an environment issue: {blocker description}. How to proceed?"
- options: ["Re-run after fixing environment", "Skip browser verification"]

**`has_fixes`:**
Report: "Browser verification: {N} fixes applied, {M} issues found"
Include the Fixes Applied section in the consolidator prompt (step `consolidate_knowledge`) so browser-discovered patterns are captured in knowledge files.

**`has_issues`:**
Report: "Browser verification: {N} issues found (see screenshots in {screenshots_dir}/)"
Note issues for verify-work — these are candidates for manual UAT.

**`all_passed`:**
Report: "Browser verification: all {N} journeys passed"

</browser_verification>
