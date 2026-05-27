# project-init

Codex skill，用于给工程项目或研究项目初始化协作约束和记忆结构。它会生成项目级 `AGENTS.md`、`SOUL.md`，以及对应的 `memory/`、`reference/`、`outputs/` 等目录。

## 能做什么

- 创建项目级协作规则文件：`AGENTS.md`
- 创建项目风格约束文件：`SOUL.md`
- 创建工程任务记忆目录：`memory/current/<task-folder>/`、`memory/ongoing/<task-folder>/`、`memory/history/<task-folder>/`
- 创建研究项目记忆目录：`memory/experiments/`、`memory/architectures/`、`memory/datasets/`、`memory/mission/`、`memory/templates/`
- 创建研究浏览报告入口：`memory/experiments_4user/`、`memory/ideas_4user.html`、`memory/index_4user.html`
- 支持带初始任务初始化，把需求同步写入 `current/<task-folder>/` 和 `ongoing/<task-folder>/`
- 遇到已有 `AGENTS.md` 或 `SOUL.md` 时，不覆盖原文件，而是生成待合并文件

## 安装

Windows PowerShell:

```powershell
git clone https://github.com/XiaoHaiPi/project-init.git "$env:USERPROFILE\.codex\skills\project-init"
```

macOS 或 Linux:

```bash
git clone https://github.com/XiaoHaiPi/project-init.git ~/.codex/skills/project-init
```

## 使用

在目标项目根目录运行：

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py --root . --project-type engineering
```

Windows PowerShell 可使用：

```powershell
python "$env:USERPROFILE\.codex\skills\project-init\scripts\init_project_constraints.py" --root . --project-type engineering
```

带初始任务：

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py \
  --root . \
  --project-type engineering \
  --active-task "Initialize project constraints" \
  --task-folder project-constraints \
  --requirement "Create AGENTS.md, SOUL.md, and layered memory files."
```

研究项目：

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py --root . --project-type research
```

## 生成结构

工程项目默认生成：

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
    └── <task-folder>/
        ├── requirement.md
        ├── plan.md
        ├── sprint.md
        ├── task.md
        ├── subtasks.md
        └── summary.md
```

研究项目生成：

```text
memory/
├── INDEX.md
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
├── report_assets/
└── templates/
```

研究记录规则跟随生成的 `AGENTS.md`：实验和想法以 Markdown 为来源，HTML 只作为浏览视图；更新实验记录后运行 `python memory/build_user_reports.py --experiments <config-name-or-md-path>`，更新想法后运行 `python memory/build_user_reports.py --ideas`。

## 文件策略

脚本默认不覆盖已有项目说明文件：

- 已存在 `AGENTS.md` 时，生成 `AGENTS.project-init.generated.md`
- 已存在 `SOUL.md` 时，生成 `SOUL.project-init.generated.md`

生成后需要人工检查原文件和待合并文件，再决定是否整合。

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── init_project_constraints.py
└── README.md
```
