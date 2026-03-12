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
3. If still on app pages: auth valid, proceed to Derive Browser Checklist

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

## Derive Browser Checklist

Transform SUMMARY.md accomplishments into a structured checklist for the browser verifier.

**Step 1: Read summaries**

Read all `*-SUMMARY.md` files from the phase directory.

**Step 2: Extract per-summary**

For each SUMMARY, extract:
- **Accomplishments** section
- **mock_hints** frontmatter (if present) — specifically `external_data` entries
- **key-files** frontmatter (if present) — for route inference

**Step 3: Derive checklist items**

For each user-observable accomplishment, derive:
- `name`: brief description of what to verify
- `route`: URL path (infer from key-files paths, routing config, or component names)
- `expected`: what should be visible on screen (be specific — "table with columns X, Y, Z", not "data displays")
- `interaction`: optional action + expected result (e.g., "click Add button → modal opens with form fields A, B, C")
- `needs_backend_data`: true/false (from mock_hints `external_data` entries)

**Step 4: Filter**

Include: UI renders, navigation, forms, data display, visual states, user interactions.
Exclude: refactors, type changes, API internals, test files, build config, non-visual changes.

**Step 5: Group and format**

Group items by route for efficient navigation. Format as a numbered list:

```
1. **{name}**
   Route: {route}
   Expected: {expected}
   Interaction: {interaction or "none"}
   Needs backend data: {yes/no}

2. **{name}**
   ...
```

## Spawn

Spawn the browser verifier agent after auth is established and checklist is derived:

```
Task(
  prompt="Run browser verification for phase {phase_number}.

Phase directory: {phase_dir}
Dev URL: {dev_url}
Auth state: .agent-browser-state.json
Screenshots directory: {phase_dir}/screenshots

## Browser Checklist

{derived_checklist}

## Backend Context

{summary of which items need real backend data — from mock_hints external_data entries.
Items needing backend data may show empty states or errors — mark as ENVIRONMENT_BLOCKED, not ISSUE.}

Verify each checklist item. Save all screenshots to {phase_dir}/screenshots/.
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
Report: "Browser verification: {N} issues found (see screenshots in {phase_dir}/screenshots/)"
Note issues for verify-work — these are candidates for manual UAT.

**`all_passed`:**
Report: "Browser verification: all {N} items passed"

</browser_verification>
