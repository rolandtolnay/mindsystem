<graphql_reference>

<authentication>
Linear uses personal API keys in the Authorization header (no Bearer prefix):

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  --data '{"query": "..."}' \
  https://api.linear.app/graphql
```
</authentication>

<mutations>

<create_issue>
```graphql
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
    }
  }
}
```

Variables:
```json
{
  "input": {
    "teamId": "uuid",
    "title": "Issue title",
    "description": "Markdown description",
    "projectId": "uuid (optional)",
    "priority": 3,
    "estimate": 3,
    "parentId": "uuid (for sub-issues)",
    "stateId": "uuid (optional)",
    "labelIds": ["uuid1", "uuid2"]
  }
}
```

**Priority values:** 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low
**Estimate:** Integer, meaning depends on team settings (fibonacci, linear, t-shirt)
</create_issue>

<update_issue>
```graphql
mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue {
      id
      identifier
      title
      state {
        id
        name
      }
    }
  }
}
```

The `id` parameter accepts either:
- Full UUID: `550e8400-e29b-41d4-a716-446655440000`
- Issue identifier: `ABC-123`

Variables:
```json
{
  "id": "ABC-123",
  "input": {
    "title": "New title (optional)",
    "description": "New description (optional)",
    "stateId": "uuid (optional)",
    "priority": 2
  }
}
```
</update_issue>

</mutations>

<queries>

<get_issue>
```graphql
query Issue($id: String!) {
  issue(id: $id) {
    id
    identifier
    title
    description
    priority
    estimate
    state {
      id
      name
      type
    }
    parent {
      identifier
    }
    children {
      nodes {
        identifier
        title
      }
    }
  }
}
```
</get_issue>

<get_team_states>
```graphql
query TeamWorkflowStates($teamId: String!) {
  team(id: $teamId) {
    id
    name
    states {
      nodes {
        id
        name
        type
        position
      }
    }
  }
}
```

State types:
- `backlog` - Backlog/Triage
- `unstarted` - Todo
- `started` - In Progress
- `completed` - Done
- `canceled` - Canceled
</get_team_states>

<get_all_workflow_states>
```graphql
query {
  workflowStates {
    nodes {
      id
      name
      type
      team {
        id
        key
      }
    }
  }
}
```

Use this to find state IDs when you don't know the team ID yet.
</get_all_workflow_states>

</queries>

<curl_examples>

<create_issue_curl>
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  --data '{
    "query": "mutation IssueCreate($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { id identifier title url } } }",
    "variables": {
      "input": {
        "teamId": "team-uuid",
        "title": "Issue title",
        "description": "Description here",
        "projectId": "project-uuid",
        "priority": 3
      }
    }
  }' \
  https://api.linear.app/graphql
```
</create_issue_curl>

<update_issue_curl>
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  --data '{
    "query": "mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) { issueUpdate(id: $id, input: $input) { success issue { identifier state { name } } } }",
    "variables": {
      "id": "ABC-123",
      "input": {
        "stateId": "state-uuid"
      }
    }
  }' \
  https://api.linear.app/graphql
```
</update_issue_curl>

<fetch_issue_curl>
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  --data '{
    "query": "query Issue($id: String!) { issue(id: $id) { id identifier title description state { name } } }",
    "variables": {
      "id": "ABC-123"
    }
  }' \
  https://api.linear.app/graphql
```
</fetch_issue_curl>

<fetch_team_states_curl>
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  --data '{
    "query": "query TeamWorkflowStates($teamId: String!) { team(id: $teamId) { states { nodes { id name type } } } }",
    "variables": {
      "teamId": "team-uuid"
    }
  }' \
  https://api.linear.app/graphql
```
</fetch_team_states_curl>

</curl_examples>

<error_handling>
Common errors and solutions:

**Invalid API key:**
```json
{"errors":[{"message":"Authentication required"}]}
```
→ Check LINEAR_API_KEY environment variable

**Invalid team/project ID:**
```json
{"errors":[{"message":"Entity not found"}]}
```
→ Verify UUIDs in .linear.json

**Invalid state ID:**
```json
{"errors":[{"message":"WorkflowState not found"}]}
```
→ Fetch available states and use valid ID

**Rate limiting:**
```json
{"errors":[{"message":"Rate limit exceeded"}]}
```
→ Wait and retry, Linear has generous limits for normal use
</error_handling>

</graphql_reference>
