# Memory

项目记忆按 mission 任务状态和工作流程分层。

- `mission/active/`：正在执行的任务集合，允许多个任务同时 active。
- `mission/ongoing/`：未结束但暂时搁置的任务集合。
- `mission/history/`：已经完成的 done 任务档案。

读取当前状态时先看 `mission/INDEX.md` 和 `mission/active/` 里的任务文件夹。查找 ongoing 任务看 `mission/ongoing/index.md`。查找 done 任务看 `mission/history/index.md`。

每个任务按下面流程组织：

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

- `requirements.md`：用户需求、约束和验收标准。
- `plan.md`：针对需求的完整方案。
- `task.md`：TODO 形式的任务步骤。
- `subtask.md`：仅在任务复杂时创建，用于分解子任务。
- `summary.md`：任务结束后记录做了什么、预期结果如何、实际结果如何。

`work` 是执行阶段，不创建单独文档。
