---
name: project-init
description: Initialize project-level Codex collaboration constraints. Use when the user asks to initialize this project, 对这个项目进行初始化, 建立项目约束, 初始化 AGENTS.md, create SOUL.md, build project memory, 建立记忆系统, or set up code/memory/style workflow constraints for a repository or project directory.
---

# ProjectInit

## Workflow

Use this skill to initialize a project with:

- `AGENTS.md` for project operation rules, code-constraint placeholder, and memory rules.
- `SOUL.md` for style-constraint placeholder.
- `memory/` with `current`, `ongoing`, and `history` layers.

Language policy:

- Write generated constraint files in English: `AGENTS.md`, `SOUL.md`, and generated merge files.
- Write generated memory documents in Chinese: everything under `memory/`.

Run the bundled script from the target project root:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root .
```

If the user provides an initial active task, pass it explicitly:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root . --active-task "任务名称" --task-folder "short-task-name" --requirement "用户需求"
```

Use the script output to report which files were created and which files need manual merge.

Use `--task-folder` for the directory name when the active task name is Chinese or long. Keep it short, lowercase, and readable, such as `project-constraints` or `memory-init`.

## File Policy

Do not overwrite existing project instructions by default.

If `AGENTS.md` or `SOUL.md` already exists, the script writes generated content to:

- `AGENTS.project-init.generated.md`
- `SOUL.project-init.generated.md`

After that, inspect the existing file and generated file, then merge only the missing project-initialization rules when the user asks for integration.

## Memory Model

The initialized memory structure is:

```text
memory/
├── INDEX.md
├── current/
│   ├── requirement.md
│   ├── plan.md
│   ├── sprint.md
│   ├── task.md
│   ├── subtasks.md
│   └── summary.md
├── ongoing/
│   ├── index.md
│   └── <short-task-name>/
│       ├── requirement.md
│       ├── plan.md
│       ├── sprint.md
│       ├── task.md
│       ├── subtasks.md
│       └── summary.md
└── history/
    ├── index.md
    └── <short-task-name>/
        ├── requirement.md
        ├── plan.md
        ├── sprint.md
        ├── task.md
        ├── subtasks.md
        └── summary.md
```

Semantics:

- `current` is the active task folder set. Each active task lives in its own folder under `current/<task-folder>/`.
- `ongoing` is the complete set of unfinished task archives.
- `history` is the complete set of finished task archives.
- Every active task must exist in both `current/<task-folder>/` and `ongoing/<task-folder>/`.
- A task must not exist in both `ongoing` and `history`.
- `index.md` files are short navigation files, not detailed logs.
- Each task follows `Requirement -> Plan -> Sprint -> Task -> SubTask`.
- `Task` is executed in the main conversation.
- `SubTask` items are executed in subagents when subagent delegation is available. If not available, execute them sequentially in the main conversation and state that limitation.

## Task Update Rules

When a user starts a new task:

1. Read the active task folders in `memory/current/`.
2. If an active task is unfinished, sync its current folder into `memory/ongoing/<task-folder>/`.
3. If an active task is finished, move or sync its folder into `memory/history/<task-folder>/` and remove the same folder from `memory/current/` and `ongoing`.
4. Create `memory/ongoing/<new-task>/`.
5. Write the new task into both `memory/current/<new-task>/` and `memory/ongoing/<new-task>/`.
6. Update `memory/ongoing/index.md` and `memory/history/index.md`.

When a user provides a requirement:

1. Check whether the requirement is clear enough to implement.
2. If key information is missing, ask for the missing information instead of planning or coding.
3. After the requirement is confirmed, write the plan.
4. Continue through Sprint, Task, and SubTask.
5. For complex or heavy tasks, split the main task into ordered SubTask items and review each completed SubTask.

When a task is completed:

1. Move its task folder from `memory/ongoing/` to `memory/history/`.
2. Remove the same task folder from `memory/current/`.
3. Remove the task from `memory/ongoing/index.md`.
4. Add or update the task entry in `memory/history/index.md`.

Keep each current task folder short. Record only the active requirement, plan, sprint, main task, subtasks, and compact progress summary.
