---
name: project-init
description: Initialize project-level Codex collaboration constraints and memory for engineering, research, or general projects, including the mission workflow requirements-plan-task-subtask(optional)-work-summary. Use when the user asks to initialize this project, 对这个项目进行初始化, 建立项目约束, 初始化 AGENTS.md, create SOUL.md, build project memory, 建立记忆系统, initialize a research workspace, or set up code/memory/style workflow constraints for a repository or project directory.
---

# ProjectInit

## Purpose

Initialize a project with project-level instruction files, style constraints, and a memory structure. The skill supports three project types:

- `engineering`: software engineering and code projects.
- `research`: research topic, model-development, experiment, paper, and reference workspaces.
- `general`: a lightweight project workspace for projects that are not clearly engineering or research.

When the user does not specify a project type, use `engineering` unless the workspace is clearly a research workspace or the user asks for a general/non-code project setup.

## Execution Flow

1. Identify the target project root.
2. Choose `--project-type engineering`, `--project-type research`, or `--project-type general`.
3. Run the bundled initializer from the target project root:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root . --project-type engineering
```

4. Use the script output to report which files were created, already existed, or were generated for merge.
5. If `AGENTS.md` or `SOUL.md` already exists, inspect the existing file and the generated merge file only when the user asks to integrate them.

For any project type with an initial active task, pass it explicitly:

```bash
python <skill-dir>/scripts/init_project_constraints.py --root . --project-type engineering --active-task "任务名称" --task-folder "short-task-name" --requirement "用户需求"
```

Use `--task-folder` when the task name is Chinese or long. Keep it short, lowercase, and readable, such as `project-constraints` or `memory-init`.

Use `--with-subtask` only when the initial task is already complex enough to need `subtask.md`.

## Mission Workflow

All project types use the same task workflow:

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

The initializer creates `memory/mission/` with three state directories:

- `active/`: tasks currently being worked on. Multiple active tasks may exist at the same time.
- `ongoing/`: tasks that are not complete but temporarily paused.
- `history/`: done task archives.

Every task starts under `memory/mission/active/<task-folder>/`. A task may update only its own folder and its own mission index entry; it must not change another task's state unless the user explicitly asks about that task.

Each task folder contains:

- `requirements.md`: user requirement, constraints, and acceptance criteria.
- `plan.md`: complete plan for the requirement.
- `task.md`: TODO steps for execution.
- `summary.md`: task-end summary of what was done, expected result, and actual result.

Create `subtask.md` only when the task is complex enough to need smaller subtask units. `work` is the execution stage and does not get a separate document.

When the task completes, update `summary.md` and move that task folder to `memory/mission/history/<task-folder>/`. When the task is paused before completion, update `summary.md` and move that task folder to `memory/mission/ongoing/<task-folder>/`.

## Project Types

### engineering

Creates:

- `AGENTS.md`
- `SOUL.md`
- `memory/INDEX.md`
- `memory/mission/INDEX.md`
- `memory/mission/active/index.md`
- `memory/mission/ongoing/index.md`
- `memory/mission/history/index.md`

When `--active-task` is provided, also creates:

- `memory/mission/active/<task-folder>/requirements.md`
- `memory/mission/active/<task-folder>/plan.md`
- `memory/mission/active/<task-folder>/task.md`
- `memory/mission/active/<task-folder>/summary.md`
- `memory/mission/active/<task-folder>/subtask.md` when `--with-subtask` is used

### research

Creates:

- `AGENTS.md`
- `SOUL.md`
- `memory/` for the mission workflow, model iteration, experiments, ideas, browser reports, templates, datasets, architectures, and lessons.
- `<project-root-name>/` as the code directory.
- `reference/` with papers, notes, translations, code repositories, and an index.
- Empty `writing/`, `outputs/logs/`, `outputs/models/`, `outputs/zips/`, and `data/`.

Research model iterations also use `memory/mission/{active,ongoing,history}/<task-folder>/` with the same task documents.

Research records use Markdown as the source and generated HTML as user-facing browser views:

- `memory/experiments/<config-name>.md` is the experiment evidence source.
- `memory/experiments_4user/<config-name>.html` is generated from experiment Markdown and referenced logs.
- `memory/ideas.md` is the idea source.
- `memory/ideas_4user.html` is generated from `memory/ideas.md`.
- `memory/index_4user.html` is the memory browser entry page.

When updating research records:

- Regenerate experiment HTML with `python memory/build_user_reports.py --experiments <config-name-or-md-path>`.
- Regenerate idea HTML with `python memory/build_user_reports.py --ideas`.
- Treat generated HTML as derived browsing artifacts, not as the source for metrics, evidence, model status, or ideas.
- Compare model results against best checkpoint metrics unless the user explicitly asks for final-metric comparison.
- Keep Markdown and generated HTML table column names in readable natural casing. Use `mIoU`, `mAcc`, `aAcc`, `mFscore`, `Precision`, and `Recall`, not all-uppercase variants unless the name is an established acronym or code token.
- `memory/model_iter.md` must use only `未验证` or `已验证` for `Status`.

### general

Creates:

- `AGENTS.md`
- `SOUL.md`
- `memory/INDEX.md`
- `memory/mission/INDEX.md`
- `memory/mission/active/index.md`
- `memory/mission/ongoing/index.md`
- `memory/mission/history/index.md`
- `memory/notes.md`
- `memory/decisions.md`
- `outputs/`

Use this project type when the project needs lightweight shared memory but not the engineering task workflow or the research experiment/reference structure.

## File Policy

Do not overwrite existing project instructions by default.

If `AGENTS.md` or `SOUL.md` already exists, the initializer writes generated content to:

- `AGENTS.project-init.generated.md`
- `SOUL.project-init.generated.md`

Other existing files are left unchanged and reported as `exists`.

## Template Layout

The skill uses Markdown and asset templates instead of embedding project constraints in Python.

```text
project-init/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── init_project_constraints.py
│   └── project_init/
│       ├── cli.py
│       ├── core.py
│       └── profiles/
│           ├── engineering.py
│           ├── research.py
│           └── general.py
└── templates/
    ├── common/
    ├── engineering/
    ├── research/
    └── general/
```

Modify shared mission workflow rules in `templates/common/`. Modify project-type-specific rules in `templates/<project-type>/`. Change Python only when updating CLI behavior, rendering behavior, conflict handling, shared mission copying, or project-type dispatch.

## Language Policy

- Generated constraint files are English: `AGENTS.md`, `SOUL.md`, and generated merge files.
- Generated memory documents under `memory/` may be Chinese when the template is Chinese.
- Preserve code identifiers, paths, metric names, and established API names as written.
