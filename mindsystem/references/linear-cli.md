<linear_cli>
CLI prefix: provided via `task_tracker.cli` in config.json

## Operations

| Command        | Usage                                   |
|----------------|-----------------------------------------|
| get            | `{cli} get <ID> [-c for comments]`      |
| comment        | `{cli} comment <ID> "<body>"`           |
| done           | `{cli} done <ID>`                       |
| attach-commit  | `{cli} attach-commit <ID> [sha]`        |

Ticket ID pattern: `[A-Z]{2,4}-\d+` (e.g., MIN-123, PROJ-42)

## Ticket Detection

When `$ARGUMENTS` matches the ticket ID pattern:

```bash
TICKET_ID=$(echo "$ARGUMENTS" | grep -oE '[A-Z]{2,4}-[0-9]+' | head -1)
TICKET_JSON=$($TRACKER_CLI get "$TICKET_ID" 2>/dev/null)
```

Parse JSON response — extract `title` and `description` fields. Use ticket title as work description; append ticket description as additional context.

If fetch fails: treat full `$ARGUMENTS` as free-text description. No error — proceed normally.

## Planner Context

When spawning the plan writer with ticket context, include in the prompt:
- Ticket ID, title, and description
- Instruct planner to use title format: `# Adhoc: {Ticket Title} [{TICKET-ID}]`
- Instruct planner to include ticket description in the Context section

## Executor Instructions

When spawning the executor with a ticket ID, instruct it to append `[TICKET-ID]` to commit messages (e.g., `feat(adhoc-auth): description [MIN-140]`).

## Finalization

Run after knowledge consolidation. Each is a separate CLI call — verify exit code 0. If any fails, log a warning but continue.

**Comment on ticket:** Extract solution summary from SUMMARY.md (key decisions, files modified). Post via:
```bash
$TRACKER_CLI comment "$TICKET_ID" "$COMMENT_BODY"
```

**Attach commit:**
```bash
$TRACKER_CLI attach-commit "$TICKET_ID"
```

**Mark done:**
```bash
$TRACKER_CLI done "$TICKET_ID"
```

## Commit Message Suffix

Append ` [TICKET-ID]` to the consolidation commit message when ticket-driven.

## Report Additions

When ticket was finalized, append to completion report:
```
**Ticket:** [TICKET-ID]
- Comment posted: [yes/failed]
- Commit attached: [yes/failed]
- State → Done: [yes/failed]
```
</linear_cli>
