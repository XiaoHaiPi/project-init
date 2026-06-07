# Memory

This folder stores compact project context for future sessions.

## Files

- `mission/`: task folders organized by `active`, `ongoing`, and `history` states.
- `notes.md`: useful project notes, constraints, links, and context.
- `decisions.md`: decisions and their rationale.

## Mission Flow

Every task follows:

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

Each task starts under `mission/active/<task-name>/`. Completed tasks move to `mission/history/<task-name>/`; paused unfinished tasks move to `mission/ongoing/<task-name>/`. A task updates only its own folder and index entry.

## Current State

No active project state has been recorded yet.
