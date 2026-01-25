---
name: ms:linear
description: Interact with Linear API to create, update, and manage issues
argument-hint: "[action or description]"
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
---

<objective>
Conversational interface to Linear for fast issue management. Primary use case: user describes work → ask high-impact questions → create ticket immediately.

**Speed over polish.** Get tickets into Linear quickly. Don't over-engineer descriptions or explore solutions.

**No codebase exploration unless explicitly requested.** Work from user's description only. Do NOT launch agents, explore files, or analyze code unless the user explicitly asks for it.
</objective>

<execution_context>
@~/.claude/mindsystem/scripts/ms-linear-wrapper.sh
</execution_context>

<cli_reference>
**CLI location:** `~/.claude/mindsystem/scripts/ms-linear-wrapper.sh`

**Commands:**
| Command | Usage | Purpose |
|---------|-------|---------|
| `create` | `create "<title>" [-d desc] [-p priority] [-e estimate] [--parent ID] [--project name] [--no-project]` | Create issue |
| `update` | `update <ID> [-t title] [-d desc] [-p priority]` | Update fields |
| `done` | `done <ID>` | Mark completed |
| `state` | `state <ID> "<name>"` | Change state |
| `break` | `break <ID> --issues '[{...}]' [--project name] [--no-project]` | Create sub-issues |
| `get` | `get <ID>` | Fetch details |
| `states` | `states` | List workflow states |
| `projects` | `projects` | List available projects |

**Priority values:** 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low

**T-shirt to estimate mapping:**
- XS → 1, S → 2, M → 3, L → 5, XL → 8

**Project handling:**
- `--project "Name"` — Assign to project by name (overrides config default)
- `--no-project` — Don't assign to any project
- If neither specified, uses `projectId` from `.linear.json` if present
</cli_reference>

<config_format>
`.linear.json` in project root:

```json
{
  "teamId": "uuid-of-linear-team",
  "projectId": "uuid-of-linear-project (optional)",
  "defaultPriority": 3,
  "defaultLabels": []
}
```

- `teamId` — Required. Your Linear team UUID.
- `projectId` — Optional. Default project for new issues. Can be overridden with `--project` or `--no-project`.
</config_format>

<process>

<step name="parse_intent">
**Parse the command to determine intent:**

| Pattern | Intent | Action |
|---------|--------|--------|
| `done <ID>` | Mark complete | Execute `done` directly |
| `state <ID> "<name>"` | Change state | Execute `state` directly |
| `get <ID>` | Fetch details | Execute `get` directly |
| `states` | List states | Execute `states` directly |
| `projects` | List projects | Execute `projects` directly |
| `update <ID> <text>` | Update issue | Execute `update` with parsed fields |
| `break <ID>` + user provides sub-issues | Break into sub-issues | Execute `break` with user's list |
| `<ID> <description>` | Create sub-issue | Go to create flow with parent |
| `<description>` | Create issue | Go to create flow |
| (empty) | No input | Ask what they want to do |

Issue ID pattern: 2-4 uppercase letters followed by hyphen and numbers (e.g., `ABC-123`, `PROJ-42`).
</step>

<step name="direct_commands">
**For direct commands (done, state, get, states, projects, update):**

Execute CLI and format output.

```bash
~/.claude/mindsystem/scripts/ms-linear-wrapper.sh [command] [args] --json-pretty
```

Parse JSON response and present result:
- Success: Show identifier, title, new state, and URL
- For `projects`: List projects grouped by team
- Error: Show error message and suggestions
</step>

<step name="create_flow">
**For create/sub-issue — FAST PATH:**

1. **Parse input for hints:**
   - Title from first sentence or quoted text
   - Priority hints: "urgent", "high priority", "low priority", "blocker"
   - Estimate hints: "XS", "S", "M", "L", "XL", "small", "medium", "large"
   - Parent ID if pattern `<ID> <description>`
   - Project hints: "in [Project]", "for [Project]", "(project: [Name])", "[Project] project"

2. **Infer priority and estimate** from the description:
   - Bug fixes, blockers → High/Urgent
   - Small tweaks, copy changes → Low priority, XS/S estimate
   - New features → Normal priority, M estimate
   - Large features, refactors → Normal priority, L/XL estimate

3. **Ask UP TO 4 questions in ONE AskUserQuestion call:**

   Combine these into a single batch:

   **Confirmation question:** Show inferred priority/estimate, ask to confirm or adjust

   **High-impact domain questions (pick 1-3 most relevant):**
   - Scope clarification: "Should this [specific behavior] or [alternative]?"
   - Edge cases: "What should happen when [edge case]?"
   - Acceptance criteria: "What's the minimum for this to be done?"
   - Context: "Is this related to [existing feature/area]?"

   Skip questions with obvious answers from description. If description is very clear, may only need confirmation.

   If project not specified and multiple projects exist, include project selection.

4. **Create immediately after answers:**

   ```bash
   ~/.claude/mindsystem/scripts/ms-linear-wrapper.sh create "[title]" \
     -d "[description with user's answers incorporated]" -p [priority] -e [estimate] \
     [--parent ID] [--project "Name"] [--no-project] --json-pretty
   ```

5. **Format result:**

   ```
   Created: **[identifier]** — [title]
   Project: [project name]
   [url]
   ```
</step>

<step name="break_flow">
**For breaking down issues:**

User provides the sub-issues in conversation. Do NOT propose or generate sub-issues.

1. **Get sub-issue list from user** (they specify titles/estimates in their message)

2. **Build JSON and execute:**

   ```bash
   ~/.claude/mindsystem/scripts/ms-linear-wrapper.sh break [ID] \
     --issues '[{"title":"...","estimate":3},{"title":"...","estimate":2}]' --json-pretty
   ```

3. **Format result:**

   ```
   Created N sub-issues under [parent-identifier]:
   - **[ID-1]** — [title 1]
   - **[ID-2]** — [title 2]
   ```
</step>

<step name="error_handling">
**Handle errors gracefully:**

- **MISSING_API_KEY:** Explain how to set LINEAR_API_KEY
- **MISSING_CONFIG:** Explain how to create .linear.json
- **ISSUE_NOT_FOUND:** Suggest checking the identifier
- **STATE_NOT_FOUND:** List available states from `states` command
- **PROJECT_NOT_FOUND:** List available projects from `projects` command

Always parse JSON error response and present human-friendly message with suggestions.
</step>

</process>

<success_criteria>
- [ ] Intent correctly parsed from input
- [ ] Direct commands execute immediately without questions
- [ ] Create flow asks max 4 questions in ONE AskUserQuestion call
- [ ] No codebase exploration unless user explicitly requests it
- [ ] Issue created immediately after user answers questions
- [ ] CLI output parsed and formatted for readability
- [ ] Errors handled with helpful suggestions
</success_criteria>
