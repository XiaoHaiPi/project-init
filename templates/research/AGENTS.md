# Research Project Agent Instructions

## Project Type

This is a research project workspace. The root folder name is defined by the user and usually equals the topic name or network name. Do not rename the root folder during initialization.

## Session Start Rule

At the start of every session:

1. Read `AGENTS.md`.
2. Read `SOUL.md`.
3. Read `memory/model_iter.md`.
4. Identify the latest model configuration recorded there.
5. Read `memory/mission/INDEX.md` and the relevant task folders under `memory/mission/active/`.
6. Read only the additional memory files needed for the current task.
7. Use the latest model configuration name to find the corresponding model information in `memory/architectures/<config-name>.md` and experiment information in `memory/experiments/<config-name>.md` when needed.
8. If the matching architecture or experiment record does not exist, state that it is missing before making assumptions.

## Clarification Rule

When the user's idea or requirement is unclear, stop before planning or editing code. Ask for the specific missing information and provide two or three reasonable options or suggestions. Do not turn an unclear research idea into an implementation plan without confirmation.

## Model Iteration Rules

For every model-code iteration:

- Create a new code file for the new model version instead of modifying the original model file in place.
- Preserve old model configurations so previous experiments remain runnable.
- Name the new task folder by the new model configuration name or another short readable task name.
- Before implementation, create `memory/mission/active/<task-name>/requirements.md`, `plan.md`, `task.md`, and `summary.md`.
- Create `subtask.md` only when the iteration is complex enough to need smaller units.
- `requirements.md` records the user requirement and experiment or model constraints.
- `plan.md` records the detailed iteration implementation steps and reasoning. `memory/templates/mission_plan.md` may be used as source material for the plan when useful.
- `task.md` records the same work as a short TODO list.
- During implementation, follow the TODO steps in `task.md`.
- When executing each TODO item, read the corresponding details in `plan.md` to confirm intent before editing.

## Mission Workflow Rules

Use this workflow for every task, including literature work, model iteration, experiments, writing, and general project operations:

```text
requirements -> plan -> task -> subtask(optional) -> work -> summary
```

Task state belongs under `memory/mission/`:

- `active/<task-name>/`: task currently being worked on.
- `ongoing/<task-name>/`: task not completed but temporarily paused.
- `history/<task-name>/`: done task archive.

Every task starts in `active`. Multiple active tasks may exist at the same time. A task may update only its own folder and its own entry in the mission indexes; it must not change another task's state unless the user explicitly asks about that task.

When a task completes, update `summary.md` with what was done, expected result, and actual result, then move only that task folder to `memory/mission/history/<task-name>/`. When a task is paused before completion, update `summary.md` and move only that task folder to `memory/mission/ongoing/<task-name>/`.

## Root Structure

The root folder contains these top-level folders:

- `memory/`: records project state, model evolution, datasets, experiment results, ideas, and execution lessons.
- `<project-root-name>/`: stores project code. This folder is the code directory; its name must match the root folder name, so do not create a literal `code/` folder unless the user explicitly asks for that name.
- `reference/`: stores papers, reading notes, translations, literature code repositories, and paper indexes.
- `writing/`: stores manuscripts, response letters, revisions, and other writing artifacts. Leave it empty during initialization.
- `outputs/`: stores model outputs and packaged archives.
- `data/`: stores datasets. Usually managed by the user.

## Memory Structure

`memory/` contains:

- `experiments/`: store one Markdown file per model configuration as `memory/experiments/<config-name>.md`. Do not create subfolders inside `memory/experiments/`.
- `experiments_4user/`: store generated static HTML browser pages for experiment records as `memory/experiments_4user/<config-name>.html`, plus `memory/experiments_4user/index.html`. These files are derived views, not evidence sources.
- `report_assets/`: store shared CSS and JS used by generated static browser pages.
- `index_4user.html`: store the generated static browser entry page for user-facing memory views.
- `architectures/`: store one Markdown file per model configuration as `memory/architectures/<config-name>.md`. Do not create subfolders inside `memory/architectures/`.
- `datasets/`: store one Markdown file per dataset as `memory/datasets/<dataset-name>.md`. Do not create subfolders inside `memory/datasets/`.
- `mission/`: store task folders by state under `active/`, `ongoing/`, and `history/`. Each task folder uses `requirements.md`, `plan.md`, `task.md`, optional `subtask.md`, and `summary.md`.
- `templates/`: store reusable memory templates. Use `memory/templates/mission_plan.md` as optional source material for detailed research iteration plans, `memory/templates/experiment.md` when creating an experiment record, `memory/templates/architecture.md` when creating an architecture record, and `memory/templates/dataset.md` when creating a dataset record.
- `model_iter.md`: record the latest model configuration, code file, architecture record, experiment record, verification status, compact baseline description, and model series grouped by encoder-decoder.
- `ideas.md`: record ideas produced during or after experiments. Use three states: active, pending, and verified. Active means implemented and waiting for results; pending means not implemented yet; verified means tested.
- `ideas_4user.html`: store a generated static HTML browser view of `memory/ideas.md`. This file is a derived view, not an evidence source.
- `lesson.md`: record every failed command or instruction execution. For each failure, record the original command or instruction, the observed failure, the reason, and the corrected command or procedure that should be used next time.

## Code Structure

The code directory is initialized empty and handled by the user. Its folder name must match the root folder name.

## Reference Structure

`reference/` contains:

- `papers/`: store reference papers. Name files by paper title only; do not include author names in filenames.
- `notes/`: store reading notes named by paper title.
- `trans/`: store Chinese translations named by paper title.
- `code/`: store code repositories associated with papers.
- `index.md`: store the index that links each paper to its corresponding note, translation, and code repository.

## Literature Search Rules

- When searching literature, give the highest priority to papers from the most recent three years.
- Prefer top conferences and journals in computer science, remote sensing, and related fields.
- Examples of preferred venues include ISPRS, TGRS, RSE, AAAI, ICCV, and CVPR.
- Older papers can be included when they are foundational, directly comparable, or necessary for historical context, but recent top-venue papers should be checked first.

## Writing Structure

`writing/` is handled by the user. Do not proactively create manuscripts, response letters, or revision drafts unless the user asks.

## Outputs Structure

`outputs/` contains:

- `logs/`: organize logs by model configuration name. Under `outputs/logs/<config-name>/`, create one timestamped folder per run. Store training logs and visualization outputs there, but do not store model files there.
- `models/`: organize model files by model configuration name. Store the model file for the best-metric iteration under `outputs/models/<config-name>/`.
- `zips/`: store all packaged archive files. Put every generated `.zip`, `.tar`, `.tar.gz`, `.7z`, and similar delivery archive under `outputs/zips/`; do not place packaged files in the project root, `writing/`, `reference/`, or `data/`.

## Data Structure

`data/` stores datasets. It is usually managed by the user. Do not move, rename, or rewrite dataset files unless the user asks.

## Record Keeping Rules

- Keep `memory/experiments/` as flat Markdown files named by model configuration, such as `memory/experiments/<config-name>.md`.
- Keep `memory/experiments_4user/` as generated flat HTML reports named by the same model configuration, such as `memory/experiments_4user/<config-name>.html`.
- Keep `memory/architectures/` as flat Markdown files named by model configuration, such as `memory/architectures/<config-name>.md`.
- Keep `memory/datasets/` as flat Markdown files named by dataset, such as `memory/datasets/<dataset-name>.md`.
- When adding a new Markdown document under `memory/experiments/` or updating any existing experiment Markdown record, regenerate the corresponding HTML report with `python memory/build_user_reports.py --experiments <config-name-or-md-path>` before reporting completion. Use `python memory/build_user_reports.py` only when a full static report refresh is needed.
- When adding a new Markdown document for research ideas or updating `memory/ideas.md`, regenerate `memory/ideas_4user.html` with `python memory/build_user_reports.py --ideas` before reporting completion. Use `python memory/build_user_reports.py` only when a full static report refresh is needed.
- In every Markdown and generated HTML table, keep column names in readable natural casing. Do not convert metric or field names to all-uppercase unless the name is an established acronym or code token. Use `mIoU`, `mAcc`, `aAcc`, `mFscore`, `Precision`, and `Recall`, not `MIOU`, `MACC`, `AACC`, `MFSCORE`, `PRECISION`, or `RECALL`.
- When adding experiment records, use `memory/templates/experiment.md`.
- When adding or updating an experiment record, run `python memory/build_user_reports.py --experiments <config-name-or-md-path>` to update the matching static HTML browser page in `memory/experiments_4user/`. Generate HTML from the Markdown record and referenced logs; include source Markdown path, source log path when available, and generation time.
- Treat experiment HTML reports as derived browsing artifacts. Do not use them as the source for metrics, evidence, or model status.
- In experiment reports under `memory/experiments/`, write analysis content in Chinese. Keep code identifiers, metric names, config paths, log paths, and established English field names unchanged.
- In each experiment file, record run time, dataset, best iter, total iter, reference log, reference code, and reference config as normal fields.
- In each experiment file, record best-iter metrics in separate tables: per-modality average metrics when multiple modalities exist, per-class overall metrics, and global metrics.
- In the per-modality table, put metric names in the header row and use one row per modality.
- In the global metrics table, use only two rows: one header row with metric names and one value row with metric values.
- For all metric comparisons, compare against best checkpoint metrics. Do not compare against final metrics unless the user explicitly requests a final-metric comparison.
- Fill metric names and values from the referenced log only. Do not fabricate metric names or values. Remove all reminder sentences from the final experiment record.
- When adding architecture records, use `memory/templates/architecture.md`. Keep records readable and concise. If a model does not contain a listed structure such as neck, head, or decoder, mark that section as N/A instead of deleting the section.
- When adding dataset records, use `memory/templates/dataset.md`.
- When updating `ideas.md`, move ideas between active, pending, and verified instead of duplicating the same idea in multiple states.
- When updating `ideas.md`, run `python memory/build_user_reports.py --ideas` so `memory/ideas_4user.html` is regenerated from the Markdown content. The HTML view should preserve active, pending, and verified sections and include source path and generation time.
- Treat `memory/ideas_4user.html` as a derived browsing artifact. Do not edit it as the source for research ideas.
- Active ideas must not include experiment or log references. If an idea already has training or test results, move it to Verified.
- Active and Pending ideas must include proposed time.
- Every ideas table must include theory support, listing the literature that supports the idea.
- When updating `memory/model_iter.md`, use only `未验证` or `已验证` for `Status`, and keep `Baseline` as a compact encoder+decoder+module description.
- When any command or instruction execution fails, update `memory/lesson.md` before reporting completion. Keep the failed command, reason, and corrected command concrete enough to prevent repeating the same failure.
- Before deleting any file, ask the user for explicit permission. Do not delete files proactively.
