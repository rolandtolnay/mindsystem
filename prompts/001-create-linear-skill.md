<objective>
Create a Claude Code skill for interacting with Linear's API programmatically.

The skill should allow users to describe what they want to implement in natural language, and Claude will:
1. Lightly flesh out the description using Pareto-principle questioning (max 4 high-impact questions)
2. Optionally explore relevant codebase files for technical context
3. Create an appropriate Linear issue with optimal settings
4. Support sub-issues, state transitions, and updates

This prompt guides you through creating this skill using the `create-agent-skill` skill to follow Claude Code best practices.
</objective>

<context>
**Skill distribution model**: The skill will be copied to each project where Linear integration is needed. Each copy has its own `.linear.json` config file specifying the target Linear project.

**Authentication**: Personal API key via `LINEAR_API_KEY` environment variable.

**Target capabilities**:
- Create issues from natural language descriptions
- Create sub-issues (reference parent by identifier like ABC-123)
- Break existing issues into sub-issues
- Update existing issues
- Transition issues between workflow states (fetch states from Linear)
- T-shirt size estimates support

**UX principles**:
- Lightweight, not cumbersome - Pareto principle throughout
- Single AskUserQuestion call with max 4 high-impact questions
- Always confirm before creating (show what will be created)
- Simple confirmation after creation (no browser opening)
- Code exploration should be quick and targeted
</context>

<process>

<step name="fetch_linear_documentation">
## Step 1: Fetch Linear API Documentation

Use the Context7 MCP to get current Linear API documentation. You need to understand:

1. **Authentication**: How to authenticate with personal API keys
2. **Issue creation**: GraphQL mutation for creating issues
3. **Issue updates**: GraphQL mutation for updating issues
4. **Sub-issues**: How parent-child relationships work
5. **Workflow states**: How to fetch and transition between states
6. **Estimates**: How t-shirt sizing/estimates work in the API
7. **Projects**: How to scope operations to a specific project

Use `mcp__plugin_context7_context7__resolve-library-id` to find Linear's API documentation, then `mcp__plugin_context7_context7__query-docs` to fetch relevant sections.

Focus on the GraphQL API - Linear uses GraphQL exclusively.
</step>

<step name="invoke_skill_creator">
## Step 2: Invoke the Skill Creator

Use the `create-agent-skill` skill to create the Linear skill following Claude Code best practices.

Invoke the Skill tool with:
```
skill: "create-agent-skill"
```

When the skill creator asks for requirements, provide these specifications:

**Skill name**: `linear` (invoked as `/linear`)

**Skill purpose**: Interact with Linear API to create, update, and manage issues from natural language descriptions.

**Core behaviors**:

1. **Configuration loading**:
   - Read `.linear.json` from project root
   - Config contains: `projectId`, `teamId`, and optionally default `priority`, `labels`
   - Error gracefully if config missing with setup instructions

2. **Issue creation flow**:
   - Accept natural language description of what to build/fix
   - Use Task tool with `subagent_type: "Explore"` for quick, targeted codebase exploration (find relevant files, understand context)
   - Use AskUserQuestion ONCE with max 4 questions to capture highest-impact clarifications (Pareto principle - identify questions that add most value)
   - Flesh out the description slightly based on context
   - Show confirmation of what will be created (title, description preview, project, priority, estimate if provided)
   - On approval, create via Linear GraphQL API
   - Return simple confirmation with issue identifier

3. **Sub-issue support**:
   - Accept parent issue identifier (e.g., ABC-123) as argument
   - Support command like `/linear ABC-123 "Add validation to the form"`
   - Support breaking down: `/linear break ABC-123` - analyzes issue and suggests sub-issues

4. **Issue updates**:
   - `/linear update ABC-123 "new description or changes"`
   - `/linear done ABC-123` - transitions to completed state
   - `/linear state ABC-123 "In Progress"` - explicit state transition
   - Fetch available workflow states from Linear, don't hardcode

5. **Estimate support**:
   - Recognize t-shirt sizes (XS, S, M, L, XL) in natural language
   - Map to Linear's estimate system

**API interaction**:
- Use Bash tool with `curl` for GraphQL requests
- LINEAR_API_KEY from environment
- GraphQL endpoint: https://api.linear.app/graphql
- Include proper error handling for API failures

**Question selection heuristic** (for the Pareto questions):
- Prioritize questions that disambiguate scope (what's in vs out)
- Ask about acceptance criteria only if not obvious
- Ask about priority/urgency if not stated
- Ask about related issues/dependencies if the feature seems connected
- Skip questions whose answers are obvious from context
- Never ask more than 4 questions total

**Config file format** (`.linear.json`):
```json
{
  "projectId": "uuid-of-linear-project",
  "teamId": "uuid-of-linear-team",
  "defaultPriority": 2,
  "defaultLabels": []
}
```
</step>

<step name="create_readme">
## Step 3: Create Setup README

After the skill is created, create a README.md file alongside the skill that explains:

1. **Prerequisites**:
   - Linear account with API access
   - Personal API key from Linear settings

2. **Installation**:
   - Copy skill to project's `.claude/commands/` directory
   - Create `.linear.json` in project root

3. **Getting your Linear IDs**:
   - How to find projectId (from Linear URL or API)
   - How to find teamId

4. **Environment setup**:
   - Setting LINEAR_API_KEY environment variable
   - Recommend adding to shell profile or using direnv

5. **Usage examples**:
   - Creating a simple issue
   - Creating with parent (sub-issue)
   - Breaking down an issue
   - Updating an issue
   - Marking done
   - Changing state

Save this as a README.md in the same directory as the skill.
</step>

</process>

<success_criteria>
- Linear API documentation fetched and understood via Context7
- Skill created using `create-agent-skill` following Claude Code best practices
- Skill supports: create, update, state transitions, sub-issues, estimates
- Skill uses lightweight Pareto-principle questioning (max 4 questions, single AskUserQuestion)
- Skill uses Explore agent for quick codebase context
- Skill confirms before creating issues
- Config-based project targeting via `.linear.json`
- README with complete setup instructions created
- Skill is ready to copy to any project and configure
</success_criteria>

<verification>
Before completing, verify:
- [ ] The skill file is syntactically valid (proper YAML frontmatter, valid markdown)
- [ ] GraphQL queries/mutations in the skill match Linear's actual API
- [ ] The README covers all setup steps a new user would need
- [ ] The skill gracefully handles missing config or API key
</verification>
