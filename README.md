# project-init

Codex skill for initializing project-level collaboration constraints and memory files.

It supports three initialization types:

- `engineering`: software engineering and code projects.
- `research`: research, model-development, experiment, paper, and reference workspaces.
- `general`: lightweight memory for projects that are not specifically engineering or research.

## Outputs

All project types create:

- `AGENTS.md`
- `SOUL.md`
- `memory/mission/INDEX.md`
- `memory/mission/active/index.md`
- `memory/mission/ongoing/index.md`
- `memory/mission/history/index.md`

If those files already exist, the initializer creates merge candidates instead:

- `AGENTS.project-init.generated.md`
- `SOUL.project-init.generated.md`

### engineering

Creates:

```text
memory/
├── INDEX.md
└── mission/
    ├── INDEX.md
    ├── active/
    │   └── index.md
    ├── ongoing/
    │   └── index.md
    └── history/
        └── index.md
```

With `--active-task`, it also creates:

```text
memory/
└── mission/active/<task-folder>/
    ├── requirements.md
    ├── plan.md
    ├── task.md
    ├── summary.md
    └── subtask.md   # only with --with-subtask
```

### research

Creates:

```text
memory/
├── INDEX.md
├── build_user_reports.py
├── model_iter.md
├── ideas.md
├── ideas_4user.html
├── index_4user.html
├── lesson.md
├── architectures/
├── datasets/
├── experiments/
├── experiments_4user/
├── mission/
│   ├── INDEX.md
│   ├── active/
│   ├── ongoing/
│   └── history/
├── report_assets/
└── templates/
reference/
├── index.md
├── papers/
├── notes/
├── trans/
└── code/
writing/
outputs/
├── logs/
├── models/
└── zips/
data/
<project-root-name>/
```

### general

Creates:

```text
memory/
├── INDEX.md
├── mission/
│   ├── INDEX.md
│   ├── active/
│   │   └── index.md
│   ├── ongoing/
│   │   └── index.md
│   └── history/
│       └── index.md
├── notes.md
└── decisions.md
outputs/
```

## Usage

Engineering project:

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py --root . --project-type engineering
```

Engineering project with an initial task:

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py \
  --root . \
  --project-type engineering \
  --active-task "Initialize project constraints" \
  --task-folder project-constraints \
  --requirement "Create AGENTS.md, SOUL.md, and layered memory files."
```

Create optional `subtask.md` for a complex initial task:

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py \
  --root . \
  --project-type research \
  --active-task "Design ablation plan" \
  --task-folder ablation-plan \
  --requirement "Plan the ablation experiments." \
  --with-subtask
```

Research project:

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py --root . --project-type research
```

General project:

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py --root . --project-type general
```

Windows PowerShell example:

```powershell
python "$env:USERPROFILE\.codex\skills\project-init\scripts\init_project_constraints.py" --root . --project-type engineering
```

## Template Structure

Generated content lives in Markdown and asset templates:

```text
templates/
├── common/
├── engineering/
├── research/
└── general/
```

The Python code handles CLI parsing, template rendering, file conflict policy, and project-type dispatch.
