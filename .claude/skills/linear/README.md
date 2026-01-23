# Linear Skill

Create, update, and manage Linear issues from natural language descriptions.

## Prerequisites

- Linear account with API access
- Personal API key from Linear settings

## Installation

1. Copy the `linear/` skill directory to your project's `.claude/skills/` directory (or user-level `~/.claude/skills/`)

2. Create `.linear.json` in your project root (see Configuration below)

3. Set up your API key (see Environment Setup below)

The skill automatically registers as `/linear` - no separate slash command file needed.

## Configuration

Create `.linear.json` in your project root:

```json
{
  "teamId": "your-team-uuid",
  "projectId": "your-project-uuid",
  "defaultPriority": 3,
  "defaultLabels": []
}
```

### Finding Your Linear IDs

**Team ID:**
1. Go to Linear → Settings → Team Settings
2. Look for "Team ID" or use the API:
   ```bash
   curl -H "Authorization: $LINEAR_API_KEY" \
     -H "Content-Type: application/json" \
     --data '{"query": "{ teams { nodes { id name key } } }"}' \
     https://api.linear.app/graphql
   ```

**Project ID:**
1. Open your project in Linear
2. Go to Project Settings → copy the project ID, or use the API:
   ```bash
   curl -H "Authorization: $LINEAR_API_KEY" \
     -H "Content-Type: application/json" \
     --data '{"query": "{ projects { nodes { id name } } }"}' \
     https://api.linear.app/graphql
   ```

## Environment Setup

Get your personal API key from Linear:
1. Linear → Settings → Account → API → Personal API keys
2. Create a new key with appropriate permissions

Set the environment variable:

**Option 1: Shell profile (~/.zshrc or ~/.bashrc)**
```bash
export LINEAR_API_KEY="lin_api_xxxxxxxxxxxxx"
```

**Option 2: direnv (.envrc in project root)**
```bash
export LINEAR_API_KEY="lin_api_xxxxxxxxxxxxx"
```
Remember to run `direnv allow` after creating .envrc

**Option 3: Per-session**
```bash
export LINEAR_API_KEY="lin_api_xxxxxxxxxxxxx"
```

## Usage

### Create an Issue

Describe what you want to build:
```
/linear Add user authentication with JWT tokens
```

Claude will:
1. Optionally explore relevant codebase files
2. Ask clarifying questions (max 4, only if needed)
3. Show you exactly what will be created
4. Create the issue on confirmation

### Create a Sub-Issue

Reference the parent issue ID:
```
/linear ABC-123 Add password validation to the auth form
```

### Update an Issue

Change description or title:
```
/linear update ABC-123 Expand scope to include OAuth providers
```

### Mark as Done

```
/linear done ABC-123
```

### Change State

```
/linear state ABC-123 "In Progress"
/linear state ABC-123 "In Review"
```

State names are matched against your team's workflow states.

### Break Down an Issue

Analyze an issue and create sub-issues:
```
/linear break ABC-123
```

Claude will analyze the issue and propose a breakdown into sub-issues.

## Priority Values

- **Urgent** (1): Critical, needs immediate attention
- **High** (2): Important, should be done soon
- **Normal** (3): Standard priority (default)
- **Low** (4): Nice to have, do when time permits

## Estimates (T-Shirt Sizes)

Mention size in your description:
- "This is a small task" → 2 points
- "Probably medium sized" → 3 points
- "Large effort" → 5 points

Mapping: XS=1, S=2, M=3, L=5, XL=8

## Troubleshooting

**"Missing .linear.json configuration"**
Create the config file in your project root with teamId and projectId.

**"Authentication required" error**
Check that LINEAR_API_KEY is set in your environment.

**"Entity not found" error**
Verify the UUIDs in .linear.json are correct. Use the API queries above to find valid IDs.

**State not found**
The state name must match your team's workflow states exactly. Run `/linear state ABC-123 "?"` to see available states.
