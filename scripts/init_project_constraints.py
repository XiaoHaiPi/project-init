#!/usr/bin/env python3
"""Initialize project constraints and layered memory files."""

from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WriteResult:
    path: Path
    action: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower().strip()).strip("-")
    if slug:
        return slug[:40]
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"task-{digest}"


def write_if_missing(path: Path, content: str, *, collision_path: Path | None = None) -> WriteResult:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if collision_path is None:
            return WriteResult(path, "exists")
        collision_path.write_text(content, encoding="utf-8", newline="\n")
        return WriteResult(collision_path, f"generated-for-merge:{path.name}")
    path.write_text(content, encoding="utf-8", newline="\n")
    return WriteResult(path, "created")


def agents_content() -> str:
    return """# Project Agent Instructions

## Reading Order

1. Read `AGENTS.md` first.
2. If `SOUL.md` exists, read it next.
3. To recover the active project state, read `memory/INDEX.md` and `memory/current/`.
4. To find unfinished tasks, read `memory/ongoing/index.md`.
5. To find completed tasks, read `memory/history/index.md`.

## Coding Constraints

These rules reduce common LLM coding mistakes. Merge them with project-specific instructions as needed.

Tradeoff: these rules bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

Do not assume. Do not hide confusion. Surface tradeoffs.

Before implementing:

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them instead of choosing silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop, name what is confusing, and ask.

### 2. Simplicity First

Write the minimum code that solves the problem. Do not add speculative work.

- Do not add features beyond what was requested.
- Do not create abstractions for single-use code.
- Do not add flexibility or configurability that was not requested.
- Do not add error handling for impossible scenarios.
- If 200 lines can be 50 lines, rewrite it.

Ask whether a senior engineer would call the implementation overcomplicated. If yes, simplify.

### 3. Surgical Changes

Touch only what is required. Clean up only issues caused by the current change.

When editing existing code:

- Do not improve adjacent code, comments, or formatting.
- Do not refactor code that is not part of the request.
- Match existing style, even if another style would be preferable.
- If unrelated dead code is found, mention it instead of deleting it.

When the current change creates unused code:

- Remove imports, variables, and functions made unused by the current change.
- Do not remove pre-existing dead code unless asked.

Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

Define success criteria and verify before reporting completion.

Transform tasks into verifiable goals:

- Add validation -> write tests for invalid inputs, then make them pass.
- Fix the bug -> write a test that reproduces the bug, then make it pass.
- Refactor X -> ensure tests pass before and after.

For multi-step tasks, state a brief plan:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria support independent iteration. Weak criteria such as make it work require clarification first.

These rules are working when diffs contain fewer unrelated changes, fewer rewrites are caused by overcomplication, and clarifying questions happen before implementation mistakes.

## Engineering Constraints

When starting a completely new project, choose the architecture before writing code.

Before implementation:

- Analyze the user's requirements.
- Compare reasonable architecture and technology-stack options.
- Explain the main advantages and disadvantages of each option.
- Present the options to the user and wait for confirmation.
- Start coding only after the user confirms the architecture and technology stack.

During implementation:

- Split the project into a readable and maintainable engineering structure.
- Avoid putting multiple unrelated features into a single large code file.
- Keep files focused, clean, and easy to read.
- Avoid bloated modules and speculative structure.
- For new projects, use PascalCase variable names unless the language, framework, or project convention conflicts with it.
- If PascalCase variable names conflict with a language, framework, or existing project convention, state the conflict and ask before proceeding.
- Write functions to be reusable where it meaningfully reduces duplication.
- Do not make functions overly specific to a single incidental call site when a clear reusable shape is available.

After implementing a feature:

- Review the work independently before reporting completion.
- Check code correctness, including obvious edge cases and integration points.
- Check functional completeness against the user's request.
- Estimate implementation coverage: identify which requested parts are fully implemented, partially implemented, or not implemented.
- Fix issues found during self-review before handing the result back, unless the fix requires user clarification.

## Development Workflow Constraints

Use this workflow for non-trivial work:

```text
Requirement -> Plan -> Sprint -> Task -> SubTask
```

Definitions:

- `Requirement`: the user's requirement and acceptance criteria.
- `Plan`: the overall solution and technical route.
- `Sprint`: staged delivery batches.
- `Task`: the main task executed in the main conversation.
- `SubTask`: smaller units split from a complex or heavy main task.

Requirement rules:

- When the user provides a requirement, check whether it is clear enough to implement.
- If required information is missing, ask for the missing information before planning or coding.
- Do not start implementation from an ambiguous requirement.
- After the requirement is confirmed, write the plan and then continue the workflow.

Task and SubTask execution:

- Execute the main `Task` in the main conversation.
- When the main task is complex or heavy, split it into ordered `SubTask` items.
- Run `SubTask` work in subagents when the environment allows subagent delegation.
- If subagents are unavailable, execute the `SubTask` items sequentially in the main conversation and state that limitation.
- Complete `SubTask` items according to the planned order.
- Review each completed `SubTask` before integrating it into the main task.
- After all `SubTask` items are complete, review the full task for code correctness, functional completeness, and implementation coverage.

## Memory Constraints

`memory/current/` is the active task folder set. Each active task lives in its own folder under `memory/current/<task-folder>/`.

`memory/ongoing/` is the complete set of unfinished tasks. Every active task must exist in both `memory/current/<task-folder>/` and `memory/ongoing/<task-folder>/`.

`memory/history/` is the archive of completed tasks. A task must not exist in both `ongoing` and `history`.

Each task folder in `memory/current/` stores:

- `requirement.md`: current requirement and acceptance criteria.
- `plan.md`: current task plan.
- `sprint.md`: staged delivery batches.
- `task.md`: main task handled in the main conversation.
- `subtasks.md`: split subtask list and execution status.
- `summary.md`: compact progress summary for the current task.

`memory/ongoing/index.md` and `memory/history/index.md` are navigation indexes only. Each task entry should describe the task in one or two sentences, without long paragraphs.

Each task folder contains:

- `requirement.md`
- `plan.md`
- `sprint.md`
- `task.md`
- `subtasks.md`
- `summary.md`

## Task Switching Flow

When the user starts a new task, process the active task folders in `memory/current/` first:

1. If an active task is unfinished, sync its current folder into `memory/ongoing/<task-folder>/`.
2. If an active task is completed, place it in `memory/history/<task-folder>/` and remove the same folder from `memory/current/` and `ongoing`.
3. Create `memory/ongoing/<new-task>/`.
4. Write the new task into both `memory/current/<new-task>/` and `memory/ongoing/<new-task>/`.
5. Sync the same requirement, plan, sprint, task, subtasks, and summary files into `memory/ongoing/<new-task>/`.
6. Update `memory/ongoing/index.md` and `memory/history/index.md`.

When a task is completed:

1. Move the task folder from `memory/ongoing/` to `memory/history/`.
2. Remove the same task folder from `memory/current/`.
3. Remove the task from `memory/ongoing/index.md`.
4. Add or update the task entry in `memory/history/index.md`.

## State File Constraints

Do not create a second project memory or task-state system. Project memory belongs only in `memory/`.
"""


def soul_content() -> str:
    return """# Project Style Constraints

## Work Style

- Work seriously and with care.
- Keep reasoning clear and plans explicit.
- Complete tasks in an orderly way.
- Prefer structured progress over improvised action.

## Integrity

- Do not deceive the user.
- Do not hide uncertainty, failed tests, missing verification, or known problems.
- State what has been verified and what has not.
- Review your own work before reporting completion.
"""


def memory_index_content() -> str:
    return """# Memory

项目记忆按任务状态和开发流程分层。

- `current/`：当前进行中的任务文件夹集合，每个任务一个文件夹，里面只保留很短的需求、计划、Sprint、主任务、子任务和进展摘要。
- `ongoing/`：未完成任务总集，每个任务一个文件夹。
- `history/`：已完成任务档案，每个任务一个文件夹。

读取当前状态时先看 `current/`。查找未完成任务看 `ongoing/index.md`。查找已完成任务看 `history/index.md`。

每个任务按 `Requirement -> Plan -> Sprint -> Task -> SubTask` 组织：

- `requirement.md`：用户需求和验收标准。
- `plan.md`：总体方案和技术路线。
- `sprint.md`：阶段性推进批次。
- `task.md`：主任务，主对话中执行。
- `subtasks.md`：拆分的子任务，通常交给 subagent 执行。
- `summary.md`：核心进展摘要。
"""


def current_requirement_content(active_task: str | None, requirement: str | None) -> str:
    if active_task:
        resolved_requirement = requirement or "待补充。"
        return f"""# Requirement

- 当前任务：{active_task}
- 用户需求：{resolved_requirement}
- 验收标准：待确认。
- 澄清问题：暂无。
"""
    return """# Requirement

当前没有活动任务。
"""


def current_plan_content(active_task: str | None) -> str:
    if active_task:
        return f"""# Plan

- 当前任务：{active_task}
- 总体方案：待补充。
- 技术路线：待补充。
"""
    return """# Plan

当前没有活动任务。
"""


def current_sprint_content(active_task: str | None) -> str:
    if active_task:
        return f"""# Sprint

- 当前任务：{active_task}
- 阶段性推进批次：待补充。
"""
    return """# Sprint

当前没有活动任务。
"""


def current_task_content(active_task: str | None) -> str:
    if active_task:
        return f"""# Task

- 主任务：{active_task}
- 执行位置：主对话。
- 状态：待开始。
"""
    return """# Task

当前没有活动任务。
"""


def current_subtasks_content(active_task: str | None) -> str:
    if active_task:
        return f"""# SubTask

- 当前任务：{active_task}
- 子任务：暂无。
- 执行位置：subagent 可用时交给 subagent；不可用时由主对话按顺序执行。
- Review：每个子任务完成后需要 review，再进入整合。
"""
    return """# SubTask

当前没有活动任务。
"""


def current_summary_content(active_task: str | None) -> str:
    if active_task:
        return f"""# Summary

- 当前任务：{active_task}
- 进展：刚创建任务记忆，尚未开始执行。
"""
    return """# Summary

当前没有活动任务。
"""


def ongoing_index_content(
    active_task: str | None,
    task_folder: str | None,
    requirement: str | None,
) -> str:
    lines = [
        "# Ongoing Tasks",
        "",
        "这里索引所有尚未完成的任务。每条索引用一到两句话说明任务内容。",
        "",
    ]
    if active_task and task_folder:
        lines.extend(
            [
                f"## {task_folder}",
                "",
                f"{active_task}。{requirement or '需求待补充。'}",
                "",
            ]
        )
    else:
        lines.append("当前没有未完成任务。")
        lines.append("")
    return "\n".join(lines)


def history_index_content() -> str:
    return """# History Tasks

这里索引已经完成并归档的任务。每条索引用一到两句话说明任务内容。

当前没有已完成任务。
"""


def initialize(
    root: Path,
    active_task: str | None,
    task_folder_arg: str | None,
    requirement: str | None,
) -> list[WriteResult]:
    results: list[WriteResult] = []
    task_folder = slugify(task_folder_arg or active_task) if active_task else None

    results.append(
        write_if_missing(
            root / "AGENTS.md",
            agents_content(),
            collision_path=root / "AGENTS.project-init.generated.md",
        )
    )
    results.append(
        write_if_missing(
            root / "SOUL.md",
            soul_content(),
            collision_path=root / "SOUL.project-init.generated.md",
        )
    )
    results.append(write_if_missing(root / "memory" / "INDEX.md", memory_index_content()))
    current_root = root / "memory" / "current"
    current_root.mkdir(parents=True, exist_ok=True)
    results.append(
        write_if_missing(
            root / "memory" / "ongoing" / "index.md",
            ongoing_index_content(active_task, task_folder, requirement),
        )
    )
    results.append(write_if_missing(root / "memory" / "history" / "index.md", history_index_content()))

    if active_task and task_folder:
        current_task_root = current_root / task_folder
        results.append(
            write_if_missing(
                current_task_root / "requirement.md",
                current_requirement_content(active_task, requirement),
            )
        )
        results.append(write_if_missing(current_task_root / "plan.md", current_plan_content(active_task)))
        results.append(write_if_missing(current_task_root / "sprint.md", current_sprint_content(active_task)))
        results.append(write_if_missing(current_task_root / "task.md", current_task_content(active_task)))
        results.append(write_if_missing(current_task_root / "subtasks.md", current_subtasks_content(active_task)))
        results.append(write_if_missing(current_task_root / "summary.md", current_summary_content(active_task)))

        task_root = root / "memory" / "ongoing" / task_folder
        results.append(
            write_if_missing(
                task_root / "requirement.md",
                current_requirement_content(active_task, requirement),
            )
        )
        results.append(write_if_missing(task_root / "plan.md", current_plan_content(active_task)))
        results.append(write_if_missing(task_root / "sprint.md", current_sprint_content(active_task)))
        results.append(write_if_missing(task_root / "task.md", current_task_content(active_task)))
        results.append(write_if_missing(task_root / "subtasks.md", current_subtasks_content(active_task)))
        results.append(write_if_missing(task_root / "summary.md", current_summary_content(active_task)))

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize project constraints and layered memory.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Target project root.")
    parser.add_argument("--active-task", help="Optional initial active task name.")
    parser.add_argument("--task-folder", help="Optional folder name for the initial active task.")
    parser.add_argument("--requirement", help="Optional initial active task requirement.")
    parser.add_argument("--goal", help="Deprecated alias for --requirement.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"project root is not a directory: {root}")

    requirement = args.requirement or args.goal
    results = initialize(root, args.active_task, args.task_folder, requirement)
    for result in results:
        print(f"{result.action}: {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
