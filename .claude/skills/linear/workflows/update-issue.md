# Workflow: Update Issue

<required_reading>
Read `references/graphql-queries.md` for API mutations and queries.
</required_reading>

<process>

## Step 1: Load Configuration

Read `.linear.json` from project root. Verify `LINEAR_API_KEY` exists.

## Step 2: Parse Command

Determine operation from arguments:

| Command | Operation |
|---------|-----------|
| `update ABC-123 <text>` | Update description/title |
| `done ABC-123` | Transition to completed state |
| `state ABC-123 "In Progress"` | Transition to named state |

Extract:
- **Issue identifier**: e.g., `ABC-123`
- **Operation**: update, done, or state
- **Payload**: New text or target state name

## Step 3: Fetch Current Issue (if needed)

For `done` or `state` operations, fetch workflow states for the team:

```graphql
query TeamWorkflowStates($teamId: String!) {
  team(id: $teamId) {
    states {
      nodes {
        id
        name
        type
      }
    }
  }
}
```

For `done`: Find state with `type: "completed"`
For `state`: Match by name (case-insensitive)

## Step 4: Build Update

**For `update`:**
- Parse new text to determine if it's a title change, description change, or both
- If text is short (< 10 words) and doesn't include markdown, treat as title
- Otherwise, append to or replace description

**For `done`:**
- Set `stateId` to completed state UUID

**For `state`:**
- Match state name to available states
- If no match, show available states and ask user to pick

## Step 5: Execute Update

```graphql
mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue {
      id
      identifier
      title
      state {
        name
      }
    }
  }
}
```

The `id` can be the issue identifier (e.g., `ABC-123`) - Linear accepts both UUID and identifier.

## Step 6: Confirm Result

**On success:**
```
Updated ABC-123: [brief summary of change]
```

Examples:
- "Updated ABC-123: State → Done"
- "Updated ABC-123: Title changed"
- "Updated ABC-123: State → In Progress"

**On error:**
- Parse error and show actionable message
- Common errors: Invalid identifier, state not found, permission denied

</process>

<success_criteria>
- Issue identifier parsed correctly
- For state changes, valid state ID resolved
- API call succeeded
- Confirmation shown with change summary
</success_criteria>
