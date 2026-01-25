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
Provide a conversational interface to Linear for issue management. Route to the appropriate CLI command based on user intent.

Apply Pareto principle: ask max 4 high-impact questions. Skip questions with obvious answers from context.
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
| `break <ID>` | Break into sub-issues | Go to break flow |
| `update <ID> <text>` | Update issue | Execute `update` with parsed fields |
| `<ID> <description>` | Create sub-issue | Go to create flow with parent |
| `<description>` | Create issue | Go to create flow |
| (empty) | No input | Ask what they want to do |

Issue ID pattern: 2-4 uppercase letters followed by hyphen and numbers (e.g., `ABC-123`, `PROJ-42`).
</step>

<step name="direct_commands">
**For direct commands (done, state, get, states, projects):**

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
**For create/sub-issue:**

1. **Parse input for hints:**
   - Title from first sentence or quoted text
   - Priority hints: "urgent", "high priority", "low priority", "blocker"
   - Estimate hints: "XS", "S", "M", "L", "XL", "small", "medium", "large"
   - Parent ID if pattern `<ID> <description>`
   - Project hints: "in [Project]", "for [Project]", "(project: [Name])", "[Project] project"

2. **Ask clarifying questions (max 4, single AskUserQuestion call):**

   Skip questions with obvious answers. Examples:
   - Title clearly stated → don't ask for title
   - Priority mentioned → don't ask for priority
   - Simple task → skip estimate question
   - Project mentioned → don't ask for project

   Use AskUserQuestion with questions like:
   - Priority (if not obvious from context)
   - Estimate (if not mentioned)
   - Project (if multiple projects exist and none specified)
   - Description details (if ambiguous)

   For project selection, first run `projects` command to get available options.

3. **Show preview and confirm:**

   ```
   ## Create Issue

   **Title:** [parsed title]
   **Project:** [project name or "Team backlog"]
   **Priority:** [priority name]
   **Estimate:** [estimate if set]
   **Parent:** [parent ID if sub-issue]

   Create this issue?
   ```

   Use AskUserQuestion: "Create this issue?" with options:
   - "Yes, create it"
   - "Edit first"
   - "Cancel"

4. **Execute CLI:**

   ```bash
   ~/.claude/mindsystem/scripts/ms-linear-wrapper.sh create "[title]" \
     -d "[description]" -p [priority] -e [estimate] [--parent ID] \
     [--project "Name"] [--no-project] --json-pretty
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

1. **Fetch parent issue:**

   ```bash
   ~/.claude/mindsystem/scripts/ms-linear-wrapper.sh get [ID] --json-pretty
   ```

2. **Analyze and propose sub-issues:**

   Based on title and description, propose 2-5 sub-issues:
   - Each with clear title
   - Inherit parent's priority unless specified
   - Suggest estimates if pattern is clear

   ```
   ## Break Down: [identifier] — [title]

   Proposed sub-issues:
   1. [Title 1] (M)
   2. [Title 2] (S)
   3. [Title 3] (M)
   ```

3. **Confirm with user:**

   Use AskUserQuestion: "Create these sub-issues?" with options:
   - "Yes, create all"
   - "Let me edit the list"
   - "Cancel"

4. **Build JSON and execute:**

   ```bash
   ~/.claude/mindsystem/scripts/ms-linear-wrapper.sh break [ID] \
     --issues '[{"title":"...","estimate":3},{"title":"...","estimate":2}]' --json-pretty
   ```

5. **Format result:**

   ```
   Created 3 sub-issues under [parent-identifier]:
   - **[ID-1]** — [title 1]
   - **[ID-2]** — [title 2]
   - **[ID-3]** — [title 3]
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
- [ ] Direct commands execute immediately
- [ ] Create flow asks max 4 questions
- [ ] User confirms before creating/updating
- [ ] CLI output parsed and formatted for readability
- [ ] Errors handled with helpful suggestions
</success_criteria>
