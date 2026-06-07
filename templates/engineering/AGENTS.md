# Project Agent Instructions

## Reading Order

1. Read `AGENTS.md` first.
2. If `SOUL.md` exists, read it next.
3. To recover the active project state, read `memory/INDEX.md`, `memory/mission/INDEX.md`, and all task folders under `memory/mission/active/`.
4. To find paused unfinished tasks, read `memory/mission/ongoing/index.md`.
5. To find completed tasks, read `memory/mission/history/index.md`.

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
- Before deleting any file, ask the user for explicit permission. Do not delete files proactively.

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

Use this workflow for every task:

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

Definitions:

- `requirements.md`: the user's requirement, constraints, and acceptance criteria.
- `plan.md`: the complete solution plan for the requirement.
- `task.md`: TODO steps for the task.
- `subtask.md`: optional file used only when a complex task needs smaller subtask units.
- `work`: the execution stage. Do not create a separate `work.md`; execute according to `task.md`.
- `summary.md`: written or updated at task end, recording what was done, expected result, and actual result.

Requirement rules:

- When the user provides a requirement, check whether it is clear enough to implement.
- If required information is missing, ask for the missing information before planning or coding.
- Do not start implementation from an ambiguous requirement.
- After the requirement is clear, update `requirements.md`, write `plan.md`, then continue the workflow.

Task and SubTask execution:

- Execute the main task in the main conversation.
- When the task is complex, create `subtask.md` and divide `task.md` into ordered subtask items.
- Run subtask work in subagents when the environment allows subagent delegation.
- If subagents are unavailable, execute subtask items sequentially in the main conversation and state that limitation.
- Complete task items according to the planned order.
- Review each completed subtask before integrating it into the main task.
- After all task items are complete, review the full task for code correctness, functional completeness, and implementation coverage.

## Memory Constraints

任务状态只有三个词：`active`、`ongoing`、`done`。

- `active`：`memory/mission/active/<task-name>/` 中正在执行的任务。
- `ongoing`：`memory/mission/ongoing/<task-name>/` 中未结束但暂时搁置的任务。
- `done`：`memory/mission/history/<task-name>/` 中已经完成的任务档案。

每个任务从 `memory/mission/active/<task-name>/` 开始。`<task-name>` 使用简短、可读的文件夹名。

允许多个 active 任务同时存在。每个任务只能主动更新自己的状态、索引条目和任务文档，不能主动修改其他任务的状态。

任务完成后，更新 `summary.md`，把本任务移动到 `memory/mission/history/<task-name>/`，并更新 `memory/mission/history/index.md`。任务未结束但暂时搁置时，把本任务移动到 `memory/mission/ongoing/<task-name>/`，并更新 `memory/mission/ongoing/index.md`。

每个任务文件夹包含：

- `requirements.md`
- `plan.md`
- `task.md`
- `summary.md`

Create `subtask.md` only when the task is complex enough to need subtask tracking.

`memory/mission/active/index.md`, `memory/mission/ongoing/index.md`, and `memory/mission/history/index.md` are navigation indexes only. Each task entry should describe the task in one or two sentences.

## Task Switching Flow

When the user starts a new task:

1. Create `memory/mission/active/<new-task>/`.
2. Create `requirements.md`, `plan.md`, `task.md`, and `summary.md` in that folder.
3. Create `subtask.md` only if the task is complex.
4. Update only the new task's entry in `memory/mission/active/index.md`.
5. Do not move or edit other active, ongoing, or done task folders unless the user explicitly asks about that task.

When a task is completed:

1. Update that task's `summary.md` with what was done, expected result, and actual result.
2. Move only that task folder to `memory/mission/history/<task-name>/`.
3. Remove that task entry from `memory/mission/active/index.md` or `memory/mission/ongoing/index.md`.
4. Add or update that task entry in `memory/mission/history/index.md`.

When a task is paused before completion:

1. Update that task's `summary.md` with current progress and the reason it is paused.
2. Move only that task folder to `memory/mission/ongoing/<task-name>/`.
3. Remove that task entry from `memory/mission/active/index.md`.
4. Add or update that task entry in `memory/mission/ongoing/index.md`.

## State File Constraints

Do not create a second project memory or task-state system. Project memory belongs only in `memory/`.
