# project-init

Codex skill，用于给一个项目初始化协作约束和分层任务记忆。它会生成项目级 `AGENTS.md`、`SOUL.md`，以及 `memory/` 目录，用来记录当前任务、未完成任务和已完成任务。

## 能做什么

- 创建项目级协作规则文件：`AGENTS.md`
- 创建项目风格约束文件：`SOUL.md`
- 创建任务记忆目录：`memory/current/`、`memory/ongoing/`、`memory/history/`
- 支持带初始任务初始化，把需求同步写入 `current` 和 `ongoing/<task-folder>/`
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
python ~/.codex/skills/project-init/scripts/init_project_constraints.py --root .
```

Windows PowerShell 可使用：

```powershell
python "$env:USERPROFILE\.codex\skills\project-init\scripts\init_project_constraints.py" --root .
```

带初始任务：

```bash
python ~/.codex/skills/project-init/scripts/init_project_constraints.py \
  --root . \
  --active-task "Initialize project constraints" \
  --task-folder project-constraints \
  --requirement "Create AGENTS.md, SOUL.md, and layered memory files."
```

## 生成结构

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
│   └── <task-folder>/
└── history/
    └── index.md
```

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
