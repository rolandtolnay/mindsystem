---
name: ms:debug
description: Systematic debugging with persistent state across context resets
argument-hint: [issue description]
allowed-tools:
  - Read
  - Bash
  - Task
  - AskUserQuestion
---

<objective>
Gather symptoms from user, spawn ms-debugger agent, handle returns and checkpoints.
</objective>

<context>
User's issue: $ARGUMENTS

Check for active sessions:
```bash
ls .planning/debug/*.md 2>/dev/null | grep -v resolved | head -5
```
</context>

<process>

## 1. Check Active Sessions

If active sessions exist AND no $ARGUMENTS:
- Read each debug file's frontmatter (status, hypothesis from Current Focus, next_action)
- Display as numbered list: `{N}. {slug} — status: {status}, focus: {hypothesis}`
- User picks number to resume OR describes new issue

If $ARGUMENTS provided OR user describes new issue:
- Continue to symptom gathering

## 2. Gather Symptoms

Extract what you can from $ARGUMENTS first. Only use AskUserQuestion for missing categories:

1. **Expected behavior** - What should happen?
2. **Actual behavior** - What happens instead?
3. **Error messages** - Any errors?
4. **Timeline** - When did this start? Ever worked?
5. **Reproduction** - How to trigger it?

If the user's description covers most categories, proceed directly.

## 3. Spawn ms-debugger Agent

Fill prompt template and spawn:

```markdown
<objective>
Investigate issue: {slug}

**Summary:** {trigger}
</objective>

<symptoms>
expected: {expected}
actual: {actual}
errors: {errors}
reproduction: {reproduction}
timeline: {timeline}
</symptoms>

<mode>
symptoms_prefilled: true
goal: find_and_fix
</mode>

<debug_file>
Create: .planning/debug/{slug}.md
</debug_file>
```

```
Task(
  prompt=filled_prompt,
  subagent_type="ms-debugger",
  description="Debug {slug}"
)
```

## 4. Handle Agent Return

**If `## DEBUG COMPLETE`:**
- Display root cause, fix applied, and verification summary
- Done — the agent already committed the fix

**If `## ROOT CAUSE FOUND`** (from `find_root_cause_only` mode):
- Display root cause and evidence summary
- Offer options:
  - "Fix now" — spawn ms-debugger with `goal: find_and_fix` and the debug file
  - "Plan fix" — suggest /ms:plan-phase --gaps
  - "Done" — leave the diagnosis

**If `## CHECKPOINT REACHED`:**
- Present checkpoint details to user
- Get user response
- Spawn continuation agent (see step 5)

**If `## INVESTIGATION INCONCLUSIVE`:**
- Show what was checked and eliminated
- Offer options:
  - "Continue investigating" — spawn new agent with additional context
  - "Add more context" — gather more symptoms, spawn again
  - "Done" — stop investigation

## 5. Spawn Continuation Agent (After Checkpoint)

When user responds to checkpoint, spawn fresh agent:

```markdown
<objective>
Continue debugging {slug}. Evidence is in the debug file.
</objective>

<prior_state>
Debug file: @.planning/debug/{slug}.md
</prior_state>

<checkpoint_response>
**Type:** {checkpoint_type}
**Response:** {user_response}
</checkpoint_response>

<mode>
goal: find_and_fix
</mode>
```

```
Task(
  prompt=continuation_prompt,
  subagent_type="ms-debugger",
  description="Continue debug {slug}"
)
```

## 6. Update Last Command

```bash
ms-tools set-last-command "ms:debug $ARGUMENTS"
```

</process>

<success_criteria>
- [ ] All 4 return types handled (DEBUG COMPLETE, ROOT CAUSE FOUND, CHECKPOINT, INCONCLUSIVE)
- [ ] Symptoms extracted from $ARGUMENTS first — only ask for gaps
- [ ] Continuation agent spawned after checkpoint response
- [ ] Last command updated after completion
</success_criteria>
