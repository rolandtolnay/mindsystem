---
name: linear
description: Interact with Linear API to create, update, and manage issues from natural language descriptions. Use when working with Linear issues, creating tickets, updating issue states, or breaking down work into sub-issues.
---

<essential_principles>

**Lightweight, Not Cumbersome**

Apply Pareto principle throughout. Ask max 4 high-impact questions in a single AskUserQuestion call. Skip questions whose answers are obvious from context.

**Always Confirm Before Creating**

Show exactly what will be created (title, description preview, project, priority, estimate) before making API calls. Never create issues without explicit user approval.

**Config-Driven Project Targeting**

Read `.linear.json` from project root for teamId, projectId, and defaults. Error gracefully with setup instructions if missing.

**API Key from Environment**

Use `LINEAR_API_KEY` environment variable. Never hardcode or ask for credentials.

</essential_principles>

<quick_start>

**Create an issue:**
```
/linear Add user authentication with JWT tokens
```

**Create a sub-issue:**
```
/linear ABC-123 Add password validation to auth form
```

**Update an issue:**
```
/linear update ABC-123 Change scope to include OAuth
```

**Mark done:**
```
/linear done ABC-123
```

**Change state:**
```
/linear state ABC-123 "In Progress"
```

**Break down an issue:**
```
/linear break ABC-123
```

</quick_start>

<intake>
Parse the command to determine intent:

| Pattern | Intent | Workflow |
|---------|--------|----------|
| `update <ID> <text>` | Update issue | workflows/update-issue.md |
| `done <ID>` | Mark complete | workflows/update-issue.md |
| `state <ID> <state>` | Change state | workflows/update-issue.md |
| `break <ID>` | Break into sub-issues | workflows/break-issue.md |
| `<ID> <description>` | Create sub-issue | workflows/create-issue.md (with parentId) |
| `<description>` | Create issue | workflows/create-issue.md |

If no arguments provided, ask what they want to do.
</intake>

<config_format>
`.linear.json` in project root:

```json
{
  "teamId": "uuid-of-linear-team",
  "projectId": "uuid-of-linear-project",
  "defaultPriority": 3,
  "defaultLabels": []
}
```

**Finding your IDs:**
- teamId: Linear URL shows team key (e.g., `ABC`), use API to get UUID
- projectId: From project URL or API query
</config_format>

<api_reference>
**Endpoint:** `https://api.linear.app/graphql`

**Authentication:** `Authorization: <API_KEY>` (no Bearer prefix)

**Priority values:** 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low

**Estimate:** Integer value (team-specific scale: fibonacci, t-shirt, etc.)

**T-shirt to estimate mapping** (suggest to user, they confirm):
- XS → 1
- S → 2
- M → 3
- L → 5
- XL → 8
</api_reference>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| create-issue.md | Create new issues or sub-issues |
| update-issue.md | Update, change state, mark done |
| break-issue.md | Analyze and break down issues |
</workflows_index>

<success_criteria>
- Config loaded from `.linear.json`
- API key available in environment
- User approved issue details before creation
- API call succeeded with issue identifier returned
- Simple confirmation shown (identifier + title)
</success_criteria>
