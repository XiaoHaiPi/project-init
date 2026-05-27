---
name: project-init
description: Initialize project-level Codex collaboration constraints for engineering or research projects. Use when the user asks to initialize this project, 对这个项目进行初始化, 建立项目约束, 初始化 AGENTS.md, create SOUL.md, build project memory, 建立记忆系统, initialize a research topic workspace, or set up code/memory/style workflow constraints for a repository or project directory.
---

# ProjectInit

## Workflow

Use this skill to initialize a project by project type:

- `engineering`: software engineering and code projects. This is the current implemented template.
- `research`: research topic or model-development projects. This initializes research memory, reference, writing, outputs, data, and project-code directories.

When the user does not specify a project type, default to `engineering` unless the repository is clearly a research workspace.

Engineering initialization creates:

- `AGENTS.md` for project operation rules, code-constraint placeholder, and memory rules.
- `SOUL.md` for style-constraint placeholder.
- `memory/` with `current`, `ongoing`, and `history` layers.

Language policy:

- Write generated constraint files in English: `AGENTS.md`, `SOUL.md`, and generated merge files.
- Write generated memory documents in Chinese: everything under `memory/`.

Run the bundled script from the target project root:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root . --project-type engineering
```

If the user provides an initial active task, pass it explicitly:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root . --project-type engineering --active-task "任务名称" --task-folder "short-task-name" --requirement "用户需求"
```

For research projects:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root . --project-type research
```

Research initialization creates:

- `AGENTS.md` with research project structure and session-start rules.
- `SOUL.md` with research rigor, truthfulness, carefulness, and integrity rules.
- `memory/` with `experiments/`, `experiments_4user/`, `report_assets/`, `architectures/`, `datasets/`, `mission/`, `templates/`, `model_iter.md`, `ideas.md`, `ideas_4user.html`, `index_4user.html`, and `lesson.md`.
- `memory/templates/` with reusable `mission_plan.md`, `experiment.md`, `architecture.md`, and `dataset.md` templates.
- `<project-root-name>/` as the code directory, with the same name as the root folder.
- `reference/` with `papers/`, `notes/`, `trans/`, `code/`, and `index.md`.
- Empty `writing/`, `outputs/logs/`, `outputs/models/`, `outputs/zips/`, and `data/`.

Research project records use Markdown as the source and HTML as a user-facing generated view:

- `memory/experiments/<config-name>.md` remains the evidence source for experiments.
- `memory/experiments_4user/<config-name>.html` and `memory/experiments_4user/index.html` are generated browser reports derived from experiment Markdown and referenced logs.
- `memory/ideas.md` remains the source for ideas.
- `memory/ideas_4user.html` is a generated self-contained browser view derived from `memory/ideas.md`.
- `memory/index_4user.html` is the generated user-facing memory entry page.
- Generated HTML must include source path and generation time, and must not be treated as the source for metrics, evidence, model status, or ideas.
- All Markdown and generated HTML table column names must use readable natural casing. Do not convert metric or field names to all-uppercase unless the name is an established acronym or code token. Use `mIoU`, `mAcc`, `aAcc`, `mFscore`, `Precision`, and `Recall`, not `MIOU`, `MACC`, `AACC`, `MFSCORE`, `PRECISION`, or `RECALL`.
- When adding or updating an experiment Markdown record, regenerate the matching HTML report with `python memory/build_user_reports.py --experiments <config-name-or-md-path>`.
- When adding or updating `memory/ideas.md`, regenerate `memory/ideas_4user.html` with `python memory/build_user_reports.py --ideas`.
- Compare model results against best checkpoint metrics unless the user explicitly asks for final-metric comparison.
- `memory/model_iter.md` must use only `未验证` or `已验证` for `Status`, and keep `Baseline` as a compact encoder+decoder+module description.

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
│   └── <task-folder>/
│       ├── requirement.md
│       ├── plan.md
│       ├── sprint.md
│       ├── task.md
│       ├── subtasks.md
│       └── summary.md
├── ongoing/
│   ├── index.md
│   └── <task-folder>/
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

- `current` is the active task set. It can contain multiple independent task folders under `current/<task-folder>/`.
- `ongoing` is the hold-task archive layer and the complete set of unfinished task archives.
- `history` is the complete set of done task archives.
- `active` means a task folder under `current/<task-folder>/`.
- `hold` means a task folder under `ongoing/<task-folder>/`.
- `done` means a task folder under `history/<task-folder>/`.
- An active task can be copied from `ongoing/<task-folder>/` into `current/<task-folder>/`, then moved back to `ongoing/<task-folder>/` when paused.
- A task must not exist in both `ongoing` and `history`.
- `index.md` files are short navigation files, not detailed logs.
- Each task follows `Requirement -> Plan -> Sprint -> Task -> SubTask`.
- `Task` is executed in the main conversation.
- `SubTask` items are executed in subagents when subagent delegation is available. If not available, execute them sequentially in the main conversation and state that limitation.

## Task Update Rules

When a user starts a new task:

1. Read the active task folders in `memory/current/`.
2. If an active task is unfinished, sync its current folder into `memory/ongoing/<task-folder>/`.
3. If an active task is paused, remove it from `memory/current/` after syncing it back to `memory/ongoing/<task-folder>/`.
4. If an active task is finished, move or sync its folder into `memory/history/<task-folder>/` and remove the same folder from `memory/current/` and `ongoing`.
5. Create `memory/ongoing/<new-task>/`.
6. Write the new task into both `memory/current/<new-task>/` and `memory/ongoing/<new-task>/`.
7. Update `memory/ongoing/index.md` and `memory/history/index.md`.

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
