# Workflow: Break Issue into Sub-Issues

<required_reading>
Read `references/graphql-queries.md` for API queries and mutations.
</required_reading>

<process>

## Step 1: Load Configuration

Read `.linear.json` from project root. Verify `LINEAR_API_KEY` exists.

## Step 2: Fetch Parent Issue

Query the issue to understand what needs breaking down:

```graphql
query Issue($id: String!) {
  issue(id: $id) {
    id
    identifier
    title
    description
    estimate
    state {
      name
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

Check if already has children - warn user if so.

## Step 3: Analyze and Propose Breakdown

Based on the issue title and description:

1. Identify logical sub-tasks (aim for 2-5 sub-issues)
2. Each sub-issue should be:
   - Independently deliverable
   - Clear scope
   - Roughly similar size

If description mentions codebase elements, optionally use Task tool with `subagent_type: "Explore"` to understand technical breakdown better.

## Step 4: Present Breakdown

Show proposed sub-issues:

```
Breaking down: ABC-123 - [parent title]

Proposed sub-issues:
1. [Title 1] - [brief scope]
2. [Title 2] - [brief scope]
3. [Title 3] - [brief scope]

Create these sub-issues?
```

Use AskUserQuestion:
1. **Create all** - Looks good
2. **Modify list** - I want to change/add/remove some
3. **Cancel** - Don't create

If "Modify list", gather changes and re-present.

## Step 5: Create Sub-Issues

For each approved sub-issue, create with `parentId` set to parent's UUID:

```graphql
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      identifier
      title
    }
  }
}
```

Input for each:
```json
{
  "teamId": "<from config>",
  "projectId": "<from config>",
  "parentId": "<parent issue UUID>",
  "title": "<sub-issue title>",
  "description": "<brief description>"
}
```

## Step 6: Report Results

```
Created sub-issues for ABC-123:
- ABC-124: [title]
- ABC-125: [title]
- ABC-126: [title]
```

If any failed, report which ones succeeded and which failed with reasons.

</process>

<success_criteria>
- Parent issue fetched successfully
- User approved breakdown
- Sub-issues created with correct parentId
- All created issues reported with identifiers
</success_criteria>
