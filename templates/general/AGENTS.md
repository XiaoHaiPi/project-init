# Project Agent Instructions

## Reading Order

1. Read `AGENTS.md` first.
2. If `SOUL.md` exists, read it next.
3. Read `memory/INDEX.md` to understand project state.
4. Read `memory/mission/INDEX.md` and relevant task folders under `memory/mission/active/`.
5. Read only the additional memory files needed for the current task.

## General Project Rules

- Treat this workspace as a general-purpose project, not specifically a software engineering repository or a research workspace.
- Keep project notes, decisions, and task context under `memory/`.
- Keep user-facing generated deliverables under `outputs/`.
- Do not create additional state systems unless the user explicitly asks for a different structure.

## Work Rules

- Clarify ambiguous requirements before changing files.
- State meaningful assumptions before acting on them.
- Keep changes scoped to the user's request.
- Verify the result before reporting completion. If verification is not possible, say what was not verified.
- Do not hide failed commands, missing files, or incomplete work.

## Mission Workflow

Use this workflow for every task:

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

- `requirements.md`: records the user requirement, constraints, and acceptance criteria.
- `plan.md`: records the complete plan for the requirement.
- `task.md`: records task steps as TODO items.
- `subtask.md`: optional; create it only when the task is complex enough to need smaller units.
- `work`: the execution stage; do not create a separate `work.md`.
- `summary.md`: updated at task end with what was done, expected result, and actual result.

Task state belongs under `memory/mission/`:

- `active/<task-name>/`: task currently being worked on.
- `ongoing/<task-name>/`: task not completed but temporarily paused.
- `history/<task-name>/`: done task archive.

Every task starts in `active`. Multiple active tasks may exist at the same time. A task may update only its own folder and its own mission index entry; it must not change another task's state unless the user explicitly asks about that task.

When a task completes, update `summary.md`, then move only that task folder to `memory/mission/history/<task-name>/`. When a task is paused before completion, update `summary.md`, then move only that task folder to `memory/mission/ongoing/<task-name>/`.

## File Policy

- Do not overwrite existing project instructions by default.
- Before deleting files, ask the user for explicit permission.
- Preserve user-created structure unless the user asks to reorganize it.

## Memory Rules

`memory/` is the project memory area.

- `memory/INDEX.md`: navigation and current state.
- `memory/mission/`: task state and task workflow records.
- `memory/notes.md`: compact notes that are still useful for future sessions.
- `memory/decisions.md`: decisions, rationale, and date.

Keep memory concise. Prefer updating existing entries over creating many small files.
