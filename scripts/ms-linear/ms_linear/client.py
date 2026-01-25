"""Linear GraphQL API client."""

from typing import Any

import httpx

from ms_linear.config import LINEAR_API_URL, LinearConfig, get_api_key
from ms_linear.errors import ErrorCode, MsLinearError

# GraphQL Queries
QUERY_ISSUE = """
query Issue($id: String!) {
  issue(id: $id) {
    id
    identifier
    title
    description
    priority
    estimate
    url
    state {
      id
      name
      type
    }
    parent {
      identifier
      title
    }
    children {
      nodes {
        identifier
        title
        state {
          name
        }
      }
    }
    project {
      id
      name
    }
    team {
      id
      key
      name
    }
  }
}
"""

QUERY_WORKFLOW_STATES = """
query {
  workflowStates {
    nodes {
      id
      name
      type
      position
      team {
        id
        key
        name
      }
    }
  }
}
"""

QUERY_TEAM_STATES = """
query TeamWorkflowStates($teamId: String!) {
  team(id: $teamId) {
    id
    name
    key
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
"""

QUERY_PROJECTS = """
query {
  projects {
    nodes {
      id
      name
      state
      team {
        id
        key
        name
      }
    }
  }
}
"""

QUERY_TEAM_PROJECTS = """
query TeamProjects($teamId: String!) {
  team(id: $teamId) {
    id
    name
    key
    projects {
      nodes {
        id
        name
        state
      }
    }
  }
}
"""

# GraphQL Mutations
MUTATION_CREATE_ISSUE = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state {
        name
      }
    }
  }
}
"""

MUTATION_UPDATE_ISSUE = """
mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state {
        id
        name
      }
    }
  }
}
"""


class LinearClient:
    """Client for Linear GraphQL API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_api_key()
        self.client = httpx.Client(timeout=30.0)

    def _request(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GraphQL request to Linear."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
        }

        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = self.client.post(LINEAR_API_URL, headers=headers, json=payload)
        except httpx.NetworkError as e:
            raise MsLinearError(
                code=ErrorCode.NETWORK_ERROR,
                message=f"Network error: {e}",
                suggestions=["Check your internet connection"],
            )

        if response.status_code == 429:
            raise MsLinearError(
                code=ErrorCode.RATE_LIMITED,
                message="Rate limited by Linear API",
                suggestions=["Wait a moment and retry"],
            )

        if response.status_code != 200:
            raise MsLinearError(
                code=ErrorCode.API_ERROR,
                message=f"API error: HTTP {response.status_code}",
                suggestions=["Check your API key is valid"],
            )

        try:
            data = response.json()
        except ValueError:
            raise MsLinearError(
                code=ErrorCode.INVALID_RESPONSE,
                message="Invalid JSON response from Linear",
            )

        if "errors" in data:
            error_msg = data["errors"][0].get("message", "Unknown error")
            if "Authentication" in error_msg:
                raise MsLinearError(
                    code=ErrorCode.MISSING_API_KEY,
                    message="Authentication failed",
                    suggestions=[
                        "Check LINEAR_API_KEY is valid",
                        "Get a new key from Linear Settings > API",
                    ],
                )
            if "not found" in error_msg.lower():
                raise MsLinearError(
                    code=ErrorCode.ISSUE_NOT_FOUND,
                    message=error_msg,
                    suggestions=["Check the issue identifier is correct"],
                )
            raise MsLinearError(
                code=ErrorCode.API_ERROR,
                message=error_msg,
            )

        return data.get("data", {})

    def get_issue(self, issue_id: str) -> dict[str, Any]:
        """Fetch issue details by ID or identifier."""
        data = self._request(QUERY_ISSUE, {"id": issue_id})
        issue = data.get("issue")
        if not issue:
            raise MsLinearError(
                code=ErrorCode.ISSUE_NOT_FOUND,
                message=f"Issue {issue_id} not found",
                suggestions=["Check the issue identifier is correct"],
            )
        return issue

    def get_workflow_states(self, team_id: str | None = None) -> list[dict[str, Any]]:
        """Get workflow states, optionally filtered by team."""
        if team_id:
            data = self._request(QUERY_TEAM_STATES, {"teamId": team_id})
            team = data.get("team", {})
            states = team.get("states", {}).get("nodes", [])
            # Add team info to each state
            team_info = {"id": team.get("id"), "key": team.get("key"), "name": team.get("name")}
            return [{"team": team_info, **state} for state in states]
        else:
            data = self._request(QUERY_WORKFLOW_STATES)
            return data.get("workflowStates", {}).get("nodes", [])

    def get_projects(self, team_id: str | None = None) -> list[dict[str, Any]]:
        """Get projects, optionally filtered by team."""
        if team_id:
            data = self._request(QUERY_TEAM_PROJECTS, {"teamId": team_id})
            team = data.get("team", {})
            projects = team.get("projects", {}).get("nodes", [])
            # Add team info to each project
            team_info = {"id": team.get("id"), "key": team.get("key"), "name": team.get("name")}
            return [{"team": team_info, **project} for project in projects]
        else:
            data = self._request(QUERY_PROJECTS)
            return data.get("projects", {}).get("nodes", [])

    def find_project_by_name(self, project_name: str, team_id: str | None = None) -> dict[str, Any]:
        """Find a project by name, optionally within a specific team."""
        projects = self.get_projects(team_id)
        project_name_lower = project_name.lower()

        # Exact match first
        for project in projects:
            if project["name"].lower() == project_name_lower:
                return project

        # Partial match
        for project in projects:
            if project_name_lower in project["name"].lower():
                return project

        available = ", ".join(sorted(set(p["name"] for p in projects)))
        raise MsLinearError(
            code=ErrorCode.PROJECT_NOT_FOUND,
            message=f"Project '{project_name}' not found",
            suggestions=[f"Available projects: {available}"],
        )

    def create_issue(
        self,
        config: LinearConfig,
        title: str,
        description: str | None = None,
        priority: int | None = None,
        estimate: int | None = None,
        parent_id: str | None = None,
        state_id: str | None = None,
        label_ids: list[str] | None = None,
        project_id: str | None = None,
        no_project: bool = False,
    ) -> dict[str, Any]:
        """Create a new issue.

        Args:
            config: Linear configuration
            title: Issue title
            description: Issue description (markdown)
            priority: Priority (0-4)
            estimate: Estimate value
            parent_id: Parent issue ID for sub-issues
            state_id: Initial state ID
            label_ids: Label IDs to apply
            project_id: Explicit project ID (overrides config default)
            no_project: If True, don't assign to any project (ignores config default)
        """
        input_data: dict[str, Any] = {
            "teamId": config.team_id,
            "title": title,
        }

        if description:
            input_data["description"] = description

        # Project logic: explicit > config default, unless no_project
        if not no_project:
            if project_id:
                input_data["projectId"] = project_id
            elif config.project_id:
                input_data["projectId"] = config.project_id

        if priority is not None:
            input_data["priority"] = priority
        else:
            input_data["priority"] = config.default_priority
        if estimate is not None:
            input_data["estimate"] = estimate
        if parent_id:
            input_data["parentId"] = parent_id
        if state_id:
            input_data["stateId"] = state_id
        if label_ids:
            input_data["labelIds"] = label_ids
        elif config.default_labels:
            input_data["labelIds"] = config.default_labels

        data = self._request(MUTATION_CREATE_ISSUE, {"input": input_data})
        result = data.get("issueCreate", {})

        if not result.get("success"):
            raise MsLinearError(
                code=ErrorCode.API_ERROR,
                message="Failed to create issue",
            )

        return result.get("issue", {})

    def update_issue(
        self,
        issue_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: int | None = None,
        state_id: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing issue."""
        input_data: dict[str, Any] = {}

        if title is not None:
            input_data["title"] = title
        if description is not None:
            input_data["description"] = description
        if priority is not None:
            input_data["priority"] = priority
        if state_id is not None:
            input_data["stateId"] = state_id

        if not input_data:
            raise MsLinearError(
                code=ErrorCode.INVALID_INPUT,
                message="No fields to update",
                suggestions=["Provide at least one field to update"],
            )

        data = self._request(MUTATION_UPDATE_ISSUE, {"id": issue_id, "input": input_data})
        result = data.get("issueUpdate", {})

        if not result.get("success"):
            raise MsLinearError(
                code=ErrorCode.API_ERROR,
                message="Failed to update issue",
            )

        return result.get("issue", {})

    def find_state_by_name(self, team_id: str, state_name: str) -> dict[str, Any]:
        """Find a workflow state by name within a team."""
        states = self.get_workflow_states(team_id)
        state_name_lower = state_name.lower()

        # Exact match first
        for state in states:
            if state["name"].lower() == state_name_lower:
                return state

        # Partial match
        for state in states:
            if state_name_lower in state["name"].lower():
                return state

        # Type-based match (e.g., "done" matches completed type)
        type_mapping = {
            "done": "completed",
            "complete": "completed",
            "finished": "completed",
            "todo": "unstarted",
            "backlog": "backlog",
            "in progress": "started",
            "started": "started",
            "cancelled": "canceled",
            "canceled": "canceled",
        }
        if state_name_lower in type_mapping:
            target_type = type_mapping[state_name_lower]
            for state in states:
                if state.get("type") == target_type:
                    return state

        available = ", ".join(sorted(set(s["name"] for s in states)))
        raise MsLinearError(
            code=ErrorCode.STATE_NOT_FOUND,
            message=f"State '{state_name}' not found",
            suggestions=[f"Available states: {available}"],
        )

    def mark_done(self, issue_id: str) -> dict[str, Any]:
        """Mark an issue as completed."""
        # First get the issue to find its team
        issue = self.get_issue(issue_id)
        team_id = issue.get("team", {}).get("id")

        if not team_id:
            raise MsLinearError(
                code=ErrorCode.API_ERROR,
                message="Could not determine team for issue",
            )

        # Find the completed state
        done_state = self.find_state_by_name(team_id, "done")
        return self.update_issue(issue_id, state_id=done_state["id"])

    def change_state(self, issue_id: str, state_name: str) -> dict[str, Any]:
        """Change an issue's state by name."""
        # First get the issue to find its team
        issue = self.get_issue(issue_id)
        team_id = issue.get("team", {}).get("id")

        if not team_id:
            raise MsLinearError(
                code=ErrorCode.API_ERROR,
                message="Could not determine team for issue",
            )

        # Find the target state
        target_state = self.find_state_by_name(team_id, state_name)
        return self.update_issue(issue_id, state_id=target_state["id"])

    def create_sub_issues(
        self,
        config: LinearConfig,
        parent_id: str,
        issues: list[dict[str, Any]],
        project_id: str | None = None,
        no_project: bool = False,
    ) -> list[dict[str, Any]]:
        """Create multiple sub-issues under a parent."""
        # Get parent issue to extract its UUID and project
        parent = self.get_issue(parent_id)
        parent_uuid = parent.get("id")

        # Inherit parent's project if not explicitly specified
        if not no_project and not project_id:
            parent_project = parent.get("project")
            if parent_project:
                project_id = parent_project.get("id")

        created = []
        for issue_data in issues:
            issue = self.create_issue(
                config=config,
                title=issue_data.get("title", ""),
                description=issue_data.get("description"),
                priority=issue_data.get("priority"),
                estimate=issue_data.get("estimate"),
                parent_id=parent_uuid,
                project_id=project_id,
                no_project=no_project,
            )
            created.append(issue)

        return created
