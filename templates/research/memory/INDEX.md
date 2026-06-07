# Memory

科研类项目记忆用于记录课题状态、模型迭代、实验结果、数据集、模型结构、想法和执行失败经验。

- `experiments/`：不包含子文件夹，直接按模型配置名称创建 `.md` 文件，记录对应实验指标。
- `experiments_4user/`：存放由实验 Markdown 和日志生成的自包含 HTML 浏览报告，不作为指标或证据来源。
- `architectures/`：不包含子文件夹，直接按模型配置名称创建 `.md` 文件，记录模型结构、模块作用、对应代码文件或函数。
- `datasets/`：不包含子文件夹，直接按数据集名称创建 `.md` 文件，记录数据集信息。
- `mission/`：按 `active/`、`ongoing/`、`history/` 三个状态存放任务文件夹。每个任务文件夹使用 `requirements.md`、`plan.md`、`task.md`、可选 `subtask.md` 和 `summary.md`。
- `templates/`：存放可复用模板。创建科研迭代 plan 时可参考 `memory/templates/mission_plan.md`，创建实验记录时使用 `memory/templates/experiment.md`，创建模型结构记录时使用 `memory/templates/architecture.md`，创建数据集记录时使用 `memory/templates/dataset.md`。
- `model_iter.md`：按 encoder-decoder 结构记录模型迭代，相同系列放在一起。
- `ideas.md`：记录 active、pending、verified 三类想法。
- `ideas_4user.html`：存放由 `ideas.md` 生成的自包含 HTML 浏览页，不作为想法来源。
- `lesson.md`：记录每次指令或命令执行失败时的原指令、失败现象、原因和之后应使用的正确指令。
