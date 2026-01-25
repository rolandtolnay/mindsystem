"""Main CLI entry point for ms-linear."""

import json
from typing import Optional

import typer

from ms_linear import __version__
from ms_linear.client import LinearClient
from ms_linear.config import load_config
from ms_linear.errors import MsLinearError
from ms_linear.output import format_error, format_success, output_json

app = typer.Typer(
    name="ms-linear",
    help="Mindsystem Linear CLI - create, update, and manage Linear issues",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"ms-linear {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Mindsystem Linear CLI - create, update, and manage Linear issues."""
    pass


@app.command()
def create(
    title: str = typer.Argument(..., help="Issue title"),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Issue description (markdown)",
    ),
    priority: Optional[int] = typer.Option(
        None,
        "--priority",
        "-p",
        help="Priority: 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low",
    ),
    estimate: Optional[int] = typer.Option(
        None,
        "--estimate",
        "-e",
        help="Estimate (team-specific scale)",
    ),
    parent: Optional[str] = typer.Option(
        None,
        "--parent",
        help="Parent issue ID for sub-issues",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Project name (resolved to ID) - overrides config default",
    ),
    no_project: bool = typer.Option(
        False,
        "--no-project",
        help="Don't assign to any project (ignores config default)",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Create a new issue.

    Examples:
        ms-linear create "Fix login bug"
        ms-linear create "Add OAuth" -d "Support Google and GitHub OAuth"
        ms-linear create "Auth subtask" --parent ABC-123
        ms-linear create "Mobile bug" --project "Mobile App"
        ms-linear create "Backlog item" --no-project
    """
    command = "create"

    try:
        config = load_config()
        client = LinearClient()

        # Resolve project name to ID if provided
        project_id = None
        if project:
            project_info = client.find_project_by_name(project, config.team_id)
            project_id = project_info["id"]

        issue = client.create_issue(
            config=config,
            title=title,
            description=description,
            priority=priority,
            estimate=estimate,
            parent_id=parent,
            project_id=project_id,
            no_project=no_project,
        )

        metadata = {
            "teamId": config.team_id,
        }
        if project_id:
            metadata["projectId"] = project_id
        elif config.project_id and not no_project:
            metadata["projectId"] = config.project_id

        response = format_success(
            command=command,
            result={
                "identifier": issue.get("identifier"),
                "title": issue.get("title"),
                "url": issue.get("url"),
                "state": issue.get("state", {}).get("name"),
            },
            metadata=metadata,
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def update(
    issue_id: str = typer.Argument(..., help="Issue ID (e.g., ABC-123)"),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="New title",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="New description",
    ),
    priority: Optional[int] = typer.Option(
        None,
        "--priority",
        "-p",
        help="New priority: 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Update an existing issue.

    Examples:
        ms-linear update ABC-123 -t "New title"
        ms-linear update ABC-123 -d "Updated description"
        ms-linear update ABC-123 -p 2
    """
    command = "update"

    try:
        client = LinearClient()

        issue = client.update_issue(
            issue_id=issue_id,
            title=title,
            description=description,
            priority=priority,
        )

        response = format_success(
            command=command,
            result={
                "identifier": issue.get("identifier"),
                "title": issue.get("title"),
                "url": issue.get("url"),
                "state": issue.get("state", {}).get("name"),
            },
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def done(
    issue_id: str = typer.Argument(..., help="Issue ID (e.g., ABC-123)"),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Mark an issue as completed.

    Examples:
        ms-linear done ABC-123
    """
    command = "done"

    try:
        client = LinearClient()
        issue = client.mark_done(issue_id)

        response = format_success(
            command=command,
            result={
                "identifier": issue.get("identifier"),
                "title": issue.get("title"),
                "url": issue.get("url"),
                "state": issue.get("state", {}).get("name"),
            },
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def state(
    issue_id: str = typer.Argument(..., help="Issue ID (e.g., ABC-123)"),
    state_name: str = typer.Argument(..., help="Target state name"),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Change an issue's state.

    Examples:
        ms-linear state ABC-123 "In Progress"
        ms-linear state ABC-123 "Done"
        ms-linear state ABC-123 "Backlog"
    """
    command = "state"

    try:
        client = LinearClient()
        issue = client.change_state(issue_id, state_name)

        response = format_success(
            command=command,
            result={
                "identifier": issue.get("identifier"),
                "title": issue.get("title"),
                "url": issue.get("url"),
                "state": issue.get("state", {}).get("name"),
            },
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command("break")
def break_issue(
    issue_id: str = typer.Argument(..., help="Parent issue ID (e.g., ABC-123)"),
    issues: str = typer.Option(
        ...,
        "--issues",
        "-i",
        help='JSON array of sub-issues: [{"title": "...", "description": "...", "priority": N, "estimate": N}]',
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Project name for sub-issues (default: inherit from parent)",
    ),
    no_project: bool = typer.Option(
        False,
        "--no-project",
        help="Don't assign sub-issues to any project",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Break down an issue into sub-issues.

    The --issues parameter must be a JSON array of objects with at minimum a "title" field.
    Optional fields: description, priority, estimate.

    By default, sub-issues inherit the parent's project. Use --project to override
    or --no-project to create without project assignment.

    Examples:
        ms-linear break ABC-123 --issues '[{"title": "Design"}, {"title": "Implement"}, {"title": "Test"}]'
        ms-linear break ABC-123 --issues '[{"title": "Task"}]' --project "Backend"
    """
    command = "break"

    try:
        config = load_config()
        client = LinearClient()

        # Parse JSON issues
        try:
            issues_data = json.loads(issues)
        except json.JSONDecodeError as e:
            from ms_linear.errors import ErrorCode, MsLinearError

            raise MsLinearError(
                code=ErrorCode.INVALID_INPUT,
                message=f"Invalid JSON for --issues: {e}",
                suggestions=["Ensure --issues is valid JSON array"],
            )

        if not isinstance(issues_data, list):
            from ms_linear.errors import ErrorCode, MsLinearError

            raise MsLinearError(
                code=ErrorCode.INVALID_INPUT,
                message="--issues must be a JSON array",
                suggestions=['Use format: [{"title": "..."}, {"title": "..."}]'],
            )

        # Resolve project name to ID if provided
        project_id = None
        if project:
            project_info = client.find_project_by_name(project, config.team_id)
            project_id = project_info["id"]

        created = client.create_sub_issues(
            config, issue_id, issues_data, project_id=project_id, no_project=no_project
        )

        response = format_success(
            command=command,
            result={
                "parent": issue_id,
                "created": [
                    {
                        "identifier": i.get("identifier"),
                        "title": i.get("title"),
                        "url": i.get("url"),
                    }
                    for i in created
                ],
            },
            metadata={
                "count": len(created),
                "teamId": config.team_id,
            },
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def get(
    issue_id: str = typer.Argument(..., help="Issue ID (e.g., ABC-123)"),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Fetch issue details.

    Examples:
        ms-linear get ABC-123
    """
    command = "get"

    try:
        client = LinearClient()
        issue = client.get_issue(issue_id)

        # Format children if present
        children = issue.get("children", {}).get("nodes", [])
        children_data = [
            {
                "identifier": c.get("identifier"),
                "title": c.get("title"),
                "state": c.get("state", {}).get("name"),
            }
            for c in children
        ]

        result = {
            "identifier": issue.get("identifier"),
            "title": issue.get("title"),
            "description": issue.get("description"),
            "priority": issue.get("priority"),
            "estimate": issue.get("estimate"),
            "url": issue.get("url"),
            "state": {
                "id": issue.get("state", {}).get("id"),
                "name": issue.get("state", {}).get("name"),
                "type": issue.get("state", {}).get("type"),
            },
            "team": {
                "id": issue.get("team", {}).get("id"),
                "key": issue.get("team", {}).get("key"),
                "name": issue.get("team", {}).get("name"),
            },
        }

        # Add parent if exists
        parent = issue.get("parent")
        if parent:
            result["parent"] = {
                "identifier": parent.get("identifier"),
                "title": parent.get("title"),
            }

        # Add children if any
        if children_data:
            result["children"] = children_data

        # Add project if exists
        project = issue.get("project")
        if project:
            result["project"] = {
                "id": project.get("id"),
                "name": project.get("name"),
            }

        response = format_success(command=command, result=result)
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def states(
    team_id: Optional[str] = typer.Option(
        None,
        "--team",
        "-t",
        help="Filter by team ID (optional)",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """List workflow states.

    Without --team, returns all states across all teams.
    With --team, returns states for that specific team.

    Examples:
        ms-linear states
        ms-linear states --team abc123-team-uuid
    """
    command = "states"

    try:
        client = LinearClient()
        states_list = client.get_workflow_states(team_id)

        # Group by team for cleaner output
        teams: dict[str, dict] = {}
        for state in states_list:
            team = state.get("team", {})
            team_key = team.get("key", "unknown")
            if team_key not in teams:
                teams[team_key] = {
                    "id": team.get("id"),
                    "key": team_key,
                    "name": team.get("name"),
                    "states": [],
                }
            teams[team_key]["states"].append(
                {
                    "id": state.get("id"),
                    "name": state.get("name"),
                    "type": state.get("type"),
                    "position": state.get("position"),
                }
            )

        # Sort states by position within each team
        for team_data in teams.values():
            team_data["states"].sort(key=lambda s: s.get("position", 0))

        response = format_success(
            command=command,
            result={"teams": list(teams.values())},
            metadata={"totalStates": len(states_list)},
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def projects(
    team_id: Optional[str] = typer.Option(
        None,
        "--team",
        "-t",
        help="Filter by team ID (optional)",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-P",
        help="Pretty-print JSON output",
    ),
) -> None:
    """List projects.

    Without --team, returns all projects across all teams.
    With --team, returns projects for that specific team.

    Examples:
        ms-linear projects
        ms-linear projects --team abc123-team-uuid
    """
    command = "projects"

    try:
        client = LinearClient()
        projects_list = client.get_projects(team_id)

        # Group by team for cleaner output
        teams: dict[str, dict] = {}
        for project in projects_list:
            team = project.get("team", {})
            team_key = team.get("key", "unknown")
            if team_key not in teams:
                teams[team_key] = {
                    "id": team.get("id"),
                    "key": team_key,
                    "name": team.get("name"),
                    "projects": [],
                }
            teams[team_key]["projects"].append(
                {
                    "id": project.get("id"),
                    "name": project.get("name"),
                    "state": project.get("state"),
                }
            )

        # Sort projects by name within each team
        for team_data in teams.values():
            team_data["projects"].sort(key=lambda p: p.get("name", "").lower())

        response = format_success(
            command=command,
            result={"teams": list(teams.values())},
            metadata={"totalProjects": len(projects_list)},
        )
        typer.echo(output_json(response, pretty=json_pretty))

    except MsLinearError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
