# Workflow: Create Issue

<required_reading>
Read `references/graphql-queries.md` for API mutations.
</required_reading>

<process>

## Step 1: Load Configuration

Read `.linear.json` from project root. If missing, show setup instructions and stop:

```
Missing .linear.json configuration.

Create .linear.json in project root:
{
  "teamId": "your-team-uuid",
  "projectId": "your-project-uuid"
}

Get IDs from Linear:
- Team: Settings → Team → Copy team ID
- Project: Project settings → Copy project ID
```

Verify `LINEAR_API_KEY` environment variable exists.

## Step 2: Parse Input

Extract from arguments:
- **Parent ID** (optional): Issue identifier like `ABC-123` at start
- **Description**: Natural language description of what to build/fix
- **Estimate hints**: Look for t-shirt sizes (XS, S, M, L, XL) or point values

## Step 3: Quick Codebase Context (Optional)

If the description references code, files, or features:

Use Task tool with `subagent_type: "Explore"` to find relevant files:
- Search for mentioned components, functions, or features
- Limit to 2-3 most relevant files
- Extract brief context (what exists, where changes might go)

Keep exploration quick and targeted. Skip if description is self-contained.

## Step 4: Clarifying Questions (Pareto Principle)

Use **single AskUserQuestion call** with max 4 questions. Only ask questions that:
- Disambiguate scope (what's in vs out)
- Clarify acceptance criteria (if not obvious)
- Determine priority/urgency (if not stated)
- Identify dependencies (if feature seems connected)

**Skip questions if:**
- Answer is obvious from description
- Answer can be reasonably inferred
- Question is low-impact

Example questions:
- "Should this include [related thing] or stay focused on [core thing]?"
- "What's the priority? (Urgent / High / Normal / Low)"
- "Any specific acceptance criteria beyond [inferred criteria]?"
- "Does this block or depend on other work?"

If description is clear and complete, skip questions entirely.

## Step 5: Compose Issue

Based on input and any clarifications:

**Title:** Action-oriented, concise (e.g., "Add JWT authentication to login endpoint")

**Description:** Markdown format with:
- Brief context (1-2 sentences)
- What needs to be done (bullet points)
- Acceptance criteria (if discussed)
- Technical notes (from codebase exploration, if any)

**Priority:** Map from input or default from config

**Estimate:** If t-shirt size mentioned:
- XS → 1, S → 2, M → 3, L → 5, XL → 8

**Parent ID:** If creating sub-issue, include parentId

## Step 6: Confirm Before Creating

Show user exactly what will be created:

```
Creating issue:

Title: [title]
Project: [project name if known, else projectId]
Priority: [priority name]
Estimate: [estimate if set]
Parent: [parent identifier if sub-issue]

Description:
[full description preview]

Proceed?
```

Use AskUserQuestion with options:
1. **Create issue** - Looks good, create it
2. **Edit first** - I want to change something
3. **Cancel** - Don't create

If "Edit first", ask what to change and loop back.

## Step 7: Create via API

Build GraphQL mutation:

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
    "teamId": "<from config>",
    "projectId": "<from config>",
    "title": "<composed title>",
    "description": "<composed description>",
    "priority": <priority int>,
    "estimate": <estimate int if set>,
    "parentId": "<parent UUID if sub-issue>"
  }
}
```

Execute with curl (see `references/graphql-queries.md`).

## Step 8: Handle Response

**On success:**
```
Created: ABC-123 - [title]
```

**On error:**
- Parse error message from response
- Show actionable error (e.g., "Invalid projectId - check .linear.json")
- Suggest fix

</process>

<success_criteria>
- Config loaded successfully
- User confirmed issue details
- API call returned success
- Issue identifier displayed
</success_criteria>
