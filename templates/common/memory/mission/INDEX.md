# Mission

任务记忆按状态分在三个目录：

- `active/`：正在执行的任务。允许多个 active 任务同时存在，每个任务只能更新自己的状态和文档。
- `ongoing/`：未结束但暂时搁置的任务。
- `history/`：已经完成的 done 任务档案。

每个任务从 `active/<task_name>/` 开始，`<task_name>` 使用简短、可读的文件夹名。任务完成后移动到 `history/<task_name>/`；任务未结束但暂时搁置时移动到 `ongoing/<task_name>/`。

每个任务文件夹按下面流程组织：

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

文档职责：

- `requirements.md`：记录用户需求、约束和验收标准。
- `plan.md`：记录针对需求的完整方案。
- `task.md`：用 TODO 形式记录任务步骤。
- `subtask.md`：仅在任务复杂时创建，用于将 `task.md` 分解成多个子任务。
- `summary.md`：任务结束后记录做了什么、预期结果如何、实际结果如何。

`work` 是执行阶段，不创建单独文档。执行时必须按 `task.md` 的步骤推进，并持续更新本任务自己的文档。
