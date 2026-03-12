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
3. If still on app pages: auth valid, proceed to Spawn

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

## Spawn

Spawn the browser verifier agent after auth is established:

```
Task(
  prompt="Run browser verification for phase {phase_number}.

Phase directory: {phase_dir}
Phase goal: {phase_goal}
VERIFICATION.md: {verification_path}
Dev URL: {dev_url}
Auth state: .agent-browser-state.json
Screenshots directory: {phase_dir}/screenshots

Read VERIFICATION.md for observable truths. Test browser-testable ones.
Save all screenshots to {phase_dir}/screenshots/.
Fix issues inline. Return structured report.",
  subagent_type="ms-browser-verifier"
)
```

**After verifier returns:**

If fixes were made, include the report summary in the consolidator prompt (step `consolidate_knowledge`) so browser-discovered patterns are captured in knowledge files.

</browser_verification>
