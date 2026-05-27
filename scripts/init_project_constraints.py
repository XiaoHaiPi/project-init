#!/usr/bin/env python3
"""Initialize project constraints and layered memory files."""

from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
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


def engineering_agents_content() -> str:
    return """# Project Agent Instructions

## Reading Order

1. Read `AGENTS.md` first.
2. If `SOUL.md` exists, read it next.
3. To recover the active project state, read `memory/INDEX.md` and all folders under `memory/current/`.
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

任务状态分成四个词：`active`、`hold`、`ongoing`、`done`。

- `active`：`memory/current/<task-folder>/` 中的任务状态。
- `hold`：`memory/ongoing/<task-folder>/` 中的任务状态。
- `ongoing`：未完成任务的归档层，里面保存所有 `hold` 状态任务。
- `done`：`memory/history/<task-folder>/` 中的任务状态。

`memory/current/` 是 active 任务集合，可同时存在多个任务；每个 active 任务都在自己的文件夹里，彼此独立。

`memory/ongoing/` 是 hold 任务集合。hold 任务可以复制到 `memory/current/` 重新变成 active；active 暂停时再同步回 `memory/ongoing/` 变回 hold。

`memory/history/` 是 done 任务档案。任务完成后进入这里，并且不能同时留在 `ongoing` 和 `history`。

每个 task folder 在 `memory/current/` 和 `memory/ongoing/` 中都存放这六个文件：

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
2. If an active task is paused, remove it from `memory/current/` after syncing it back to `memory/ongoing/<task-folder>/`.
3. If an active task is completed, place it in `memory/history/<task-folder>/` and remove the same folder from `memory/current/` and `ongoing`.
4. Create `memory/ongoing/<new-task>/`.
5. Write the new task into both `memory/current/<new-task>/` and `memory/ongoing/<new-task>/`.
6. Sync the same requirement, plan, sprint, task, subtasks, and summary files into `memory/ongoing/<new-task>/`.
7. Update `memory/ongoing/index.md` and `memory/history/index.md`.

When a task is completed:

1. Move the task folder from `memory/ongoing/` to `memory/history/`.
2. Remove the same task folder from `memory/current/`.
3. Remove the task from `memory/ongoing/index.md`.
4. Add or update the task entry in `memory/history/index.md`.

## State File Constraints

Do not create a second project memory or task-state system. Project memory belongs only in `memory/`.
"""


def engineering_soul_content() -> str:
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


def research_agents_content() -> str:
    return "# Research Project Agent Instructions\n\n## Project Type\n\nThis is a research project workspace. The root folder name is defined by the user and usually equals the topic name or network name. Do not rename the root folder during initialization.\n\n## Session Start Rule\n\nAt the start of every session:\n\n1. Read `AGENTS.md`.\n2. Read `SOUL.md`.\n3. Read `memory/model_iter.md`.\n4. Identify the latest model configuration recorded there.\n5. Read only the memory files needed for the current task.\n6. Use the latest model configuration name to find the corresponding model information in `memory/architectures/<config-name>.md` and experiment information in `memory/experiments/<config-name>.md` when needed.\n7. If the matching architecture or experiment record does not exist, state that it is missing before making assumptions.\n\n## Clarification Rule\n\nWhen the user's idea or requirement is unclear, stop before planning or editing code. Ask for the specific missing information and provide two or three reasonable options or suggestions. Do not turn an unclear research idea into an implementation plan without confirmation.\n\n## Model Iteration Rules\n\nFor every model-code iteration:\n\n- Create a new code file for the new model version instead of modifying the original model file in place.\n- Preserve old model configurations so previous experiments remain runnable.\n- Name the new mission folder by the new model configuration name.\n- Before implementation, create `memory/mission/<new-config-name>/plan.md` and `memory/mission/<new-config-name>/task.md`.\n- Create `plan.md` from `memory/templates/mission_plan.md` and replace `<new-config-name>` with the actual new model configuration name.\n- `plan.md` records the detailed iteration implementation steps and reasoning.\n- `task.md` records the same work as a short TODO list.\n- During implementation, follow the TODO steps in `task.md`.\n- When executing each TODO item, read the corresponding details in `plan.md` to confirm intent before editing.\n\n## Root Structure\n\nThe root folder contains these top-level folders:\n\n- `memory/`: records project state, model evolution, datasets, experiment results, ideas, and execution lessons.\n- `<project-root-name>/`: stores project code. This folder is the code directory; its name must match the root folder name, so do not create a literal `code/` folder unless the user explicitly asks for that name.\n- `reference/`: stores papers, reading notes, translations, literature code repositories, and paper indexes.\n- `writing/`: stores manuscripts, response letters, revisions, and other writing artifacts. Leave it empty during initialization.\n- `outputs/`: stores model outputs and packaged archives.\n- `data/`: stores datasets. Usually managed by the user.\n\n## Memory Structure\n\n`memory/` contains:\n\n- `experiments/`: store one Markdown file per model configuration as `memory/experiments/<config-name>.md`. Do not create subfolders inside `memory/experiments/`.\n- `experiments_4user/`: store generated static HTML browser pages for experiment records as `memory/experiments_4user/<config-name>.html`, plus `memory/experiments_4user/index.html`. These files are derived views, not evidence sources.\n- `report_assets/`: store shared CSS and JS used by generated static browser pages.\n- `index_4user.html`: store the generated static browser entry page for user-facing memory views.\n- `architectures/`: store one Markdown file per model configuration as `memory/architectures/<config-name>.md`. Do not create subfolders inside `memory/architectures/`.\n- `datasets/`: store one Markdown file per dataset as `memory/datasets/<dataset-name>.md`. Do not create subfolders inside `memory/datasets/`.\n- `mission/`: store iteration mission folders. Each model iteration uses `memory/mission/<new-config-name>/` with `plan.md` and `task.md`.\n- `templates/`: store reusable memory templates. Use `memory/templates/mission_plan.md` when creating a mission plan, `memory/templates/experiment.md` when creating an experiment record, `memory/templates/architecture.md` when creating an architecture record, and `memory/templates/dataset.md` when creating a dataset record.\n- `model_iter.md`: record the latest model configuration, code file, architecture record, experiment record, verification status, compact baseline description, and model series grouped by encoder-decoder.\n- `ideas.md`: record ideas produced during or after experiments. Use three states: active, pending, and verified. Active means implemented and waiting for results; pending means not implemented yet; verified means tested.\n- `ideas_4user.html`: store a generated static HTML browser view of `memory/ideas.md`. This file is a derived view, not an evidence source.\n- `lesson.md`: record every failed command or instruction execution. For each failure, record the original command or instruction, the observed failure, the reason, and the corrected command or procedure that should be used next time.\n\n## Code Structure\n\nThe code directory is initialized empty and handled by the user. Its folder name must match the root folder name.\n\n## Reference Structure\n\n`reference/` contains:\n\n- `papers/`: store reference papers. Name files by paper title only; do not include author names in filenames.\n- `notes/`: store reading notes named by paper title.\n- `trans/`: store Chinese translations named by paper title.\n- `code/`: store code repositories associated with papers.\n- `index.md`: store the index that links each paper to its corresponding note, translation, and code repository.\n\n## Literature Search Rules\n\n- When searching literature, give the highest priority to papers from the most recent three years.\n- Prefer top conferences and journals in computer science, remote sensing, and related fields.\n- Examples of preferred venues include ISPRS, TGRS, RSE, AAAI, ICCV, and CVPR.\n- Older papers can be included when they are foundational, directly comparable, or necessary for historical context, but recent top-venue papers should be checked first.\n\n## Writing Structure\n\n`writing/` is handled by the user. Do not proactively create manuscripts, response letters, or revision drafts unless the user asks.\n\n## Outputs Structure\n\n`outputs/` contains:\n\n- `logs/`: organize logs by model configuration name. Under `outputs/logs/<config-name>/`, create one timestamped folder per run. Store training logs and visualization outputs there, but do not store model files there.\n- `models/`: organize model files by model configuration name. Store the model file for the best-metric iteration under `outputs/models/<config-name>/`.\n- `zips/`: store all packaged archive files. Put every generated `.zip`, `.tar`, `.tar.gz`, `.7z`, and similar delivery archive under `outputs/zips/`; do not place packaged files in the project root, `writing/`, `reference/`, or `data/`.\n\n## Data Structure\n\n`data/` stores datasets. It is usually managed by the user. Do not move, rename, or rewrite dataset files unless the user asks.\n\n## Record Keeping Rules\n\n- Keep `memory/experiments/` as flat Markdown files named by model configuration, such as `memory/experiments/<config-name>.md`.\n- Keep `memory/experiments_4user/` as generated flat HTML reports named by the same model configuration, such as `memory/experiments_4user/<config-name>.html`.\n- Keep `memory/architectures/` as flat Markdown files named by model configuration, such as `memory/architectures/<config-name>.md`.\n- Keep `memory/datasets/` as flat Markdown files named by dataset, such as `memory/datasets/<dataset-name>.md`.\n- When adding a new Markdown document under `memory/experiments/` or updating any existing experiment Markdown record, regenerate the corresponding HTML report with `python memory/build_user_reports.py --experiments <config-name-or-md-path>` before reporting completion. Use `python memory/build_user_reports.py` only when a full static report refresh is needed.\n- When adding a new Markdown document for research ideas or updating `memory/ideas.md`, regenerate `memory/ideas_4user.html` with `python memory/build_user_reports.py --ideas` before reporting completion. Use `python memory/build_user_reports.py` only when a full static report refresh is needed.\n- In every Markdown and generated HTML table, keep column names in readable natural casing. Do not convert metric or field names to all-uppercase unless the name is an established acronym or code token. Use `mIoU`, `mAcc`, `aAcc`, `mFscore`, `Precision`, and `Recall`, not `MIOU`, `MACC`, `AACC`, `MFSCORE`, `PRECISION`, or `RECALL`.\n- When adding experiment records, use `memory/templates/experiment.md`.\n- When adding or updating an experiment record, run `python memory/build_user_reports.py --experiments <config-name-or-md-path>` to update the matching static HTML browser page in `memory/experiments_4user/`. Generate HTML from the Markdown record and referenced logs; include source Markdown path, source log path when available, and generation time.\n- Treat experiment HTML reports as derived browsing artifacts. Do not use them as the source for metrics, evidence, or model status.\n- In experiment reports under `memory/experiments/`, write analysis content in Chinese. Keep code identifiers, metric names, config paths, log paths, and established English field names unchanged.\n- In each experiment file, record run time, dataset, best iter, total iter, reference log, reference code, and reference config as normal fields.\n- In each experiment file, record best-iter metrics in separate tables: per-modality average metrics when multiple modalities exist, per-class overall metrics, and global metrics.\n- In the per-modality table, put metric names in the header row and use one row per modality.\n- In the global metrics table, use only two rows: one header row with metric names and one value row with metric values.\n- For all metric comparisons, compare against best checkpoint metrics. Do not compare against final metrics unless the user explicitly requests a final-metric comparison.\n- Fill metric names and values from the referenced log only. Do not fabricate metric names or values. Remove all reminder sentences from the final experiment record.\n- When adding architecture records, use `memory/templates/architecture.md`. Keep records readable and concise. If a model does not contain a listed structure such as neck, head, or decoder, mark that section as N/A instead of deleting the section.\n- When adding dataset records, use `memory/templates/dataset.md`.\n- When updating `ideas.md`, move ideas between active, pending, and verified instead of duplicating the same idea in multiple states.\n- When updating `ideas.md`, run `python memory/build_user_reports.py --ideas` so `memory/ideas_4user.html` is regenerated from the Markdown content. The HTML view should preserve active, pending, and verified sections and include source path and generation time.\n- Treat `memory/ideas_4user.html` as a derived browsing artifact. Do not edit it as the source for research ideas.\n- Active ideas must not include experiment or log references. If an idea already has training or test results, move it to Verified.\n- Active and Pending ideas must include proposed time.\n- Every ideas table must include theory support, listing the literature that supports the idea.\n- When updating `memory/model_iter.md`, use only `未验证` or `已验证` for `Status`, and keep `Baseline` as a compact encoder+decoder+module description.\n- When any command or instruction execution fails, update `memory/lesson.md` before reporting completion. Keep the failed command, reason, and corrected command concrete enough to prevent repeating the same failure.\n- Before deleting any file, ask the user for explicit permission. Do not delete files proactively.\n"

def research_soul_content() -> str:
    return '# Research Project Style Constraints\n\n## Core Values\n\n- Be rigorous.\n- Be truthful.\n- Be careful.\n- Treat research records, experiment results, citations, and code behavior as evidence that must be checked.\n\n## Integrity\n\n- Do not fabricate experiment results, metrics, logs, citations, paper claims, code behavior, or implementation status.\n- Do not claim that an experiment has run if it has not run.\n- Do not claim that a result has been verified if it has not been verified.\n- Do not hide failed runs, missing logs, uncertain conclusions, or incomplete verification.\n- When evidence is missing, state what is missing and what can still be inferred.\n\n## Writing Discipline\n\n- Separate observed evidence from interpretation.\n- Keep claims proportional to the available evidence.\n- Cite or reference the supporting paper, log, code file, or experiment record when making a technical claim.\n- Use concise research notes, but keep enough detail for another researcher to reconstruct the reasoning.\n'


def research_build_user_reports_content() -> str:
    return 'from __future__ import annotations\n\nimport argparse\nimport html as html_lib\nimport os\nimport re\nfrom dataclasses import dataclass\nfrom datetime import datetime\nfrom pathlib import Path\nfrom typing import Sequence\nfrom urllib.parse import quote\n\n\nMEMORY_DIR = Path(__file__).resolve().parent\nPROJECT_ROOT = MEMORY_DIR.parent\nEXPERIMENTS_DIR = MEMORY_DIR / "experiments"\nEXPERIMENTS_SITE_DIR = MEMORY_DIR / "experiments_4user"\nASSETS_DIR = MEMORY_DIR / "report_assets"\n\n\n@dataclass\nclass ExperimentSummary:\n    title: str\n    stem: str\n    page: Path\n    source: Path\n    run_time: str\n    best_iter: str\n    total_iter: str\n    reference_log: str\n    best_miou: str\n\n\ndef escape(text: object) -> str:\n    return html_lib.escape(str(text), quote=True)\n\n\ndef generated_at() -> str:\n    dt = datetime.now().astimezone()\n    zone = dt.strftime("%z")\n    if len(zone) == 5:\n        zone = f"{zone[:3]}:{zone[3:]}"\n    return dt.strftime("%Y-%m-%d %H:%M:%S ") + zone\n\n\ndef href_from(page: Path, target: Path) -> str:\n    rel = os.path.relpath(target, start=page.parent).replace(os.sep, "/")\n    return quote(rel, safe="/#:.?=&%")\n\n\ndef safe_href(raw: str) -> str:\n    href = raw.strip()\n    if re.match(r"(?i)^\\s*javascript:", href):\n        return "#"\n    return escape(href)\n\n\ndef split_table_row(line: str) -> list[str]:\n    text = line.strip()\n    if text.startswith("|"):\n        text = text[1:]\n    if text.endswith("|"):\n        text = text[:-1]\n    cells: list[str] = []\n    buf: list[str] = []\n    escaped = False\n    for char in text:\n        if char == "\\\\" and not escaped:\n            escaped = True\n            continue\n        if char == "|" and not escaped:\n            cells.append("".join(buf).strip())\n            buf = []\n            continue\n        if escaped:\n            buf.append("\\\\")\n            escaped = False\n        buf.append(char)\n    if escaped:\n        buf.append("\\\\")\n    cells.append("".join(buf).strip())\n    return cells\n\n\ndef is_table_separator(line: str) -> bool:\n    cells = split_table_row(line)\n    if not cells:\n        return False\n    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)\n\n\ndef looks_like_table(lines: list[str], index: int) -> bool:\n    return (\n        index + 1 < len(lines)\n        and lines[index].strip().startswith("|")\n        and is_table_separator(lines[index + 1])\n    )\n\n\ndef align_from_separator(cell: str) -> str:\n    text = cell.strip()\n    if text.startswith(":") and text.endswith(":"):\n        return "center"\n    if text.endswith(":"):\n        return "right"\n    return "left"\n\n\nclass MarkdownRenderer:\n    def __init__(self) -> None:\n        self.heading_ids: dict[str, int] = {}\n\n    def inline(self, text: str) -> str:\n        parts = re.split(r"(`[^`]*`)", text)\n        rendered: list[str] = []\n        for part in parts:\n            if part.startswith("`") and part.endswith("`"):\n                rendered.append(f"<code>{escape(part[1:-1])}</code>")\n                continue\n            segment = escape(part)\n            segment = re.sub(\n                r"\\[([^\\]]+)\\]\\(([^)]+)\\)",\n                lambda match: (\n                    f\'<a href="{safe_href(match.group(2))}">\'\n                    f"{match.group(1)}</a>"\n                ),\n                segment,\n            )\n            segment = re.sub(r"\\*\\*([^*]+)\\*\\*", r"<strong>\\1</strong>", segment)\n            segment = re.sub(r"\\*([^*]+)\\*", r"<em>\\1</em>", segment)\n            rendered.append(segment)\n        return "".join(rendered)\n\n    def heading_id(self, text: str) -> str:\n        raw = re.sub(r"`([^`]+)`", r"\\1", text)\n        raw = re.sub(r"\\[([^\\]]+)\\]\\([^)]+\\)", r"\\1", raw)\n        slug = re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-").lower()\n        if not slug:\n            slug = "section"\n        seen = self.heading_ids.get(slug, 0)\n        self.heading_ids[slug] = seen + 1\n        if seen:\n            return f"{slug}-{seen + 1}"\n        return slug\n\n    def table(self, lines: list[str], index: int) -> tuple[str, int]:\n        headers = split_table_row(lines[index])\n        aligns = [align_from_separator(cell) for cell in split_table_row(lines[index + 1])]\n        rows: list[list[str]] = []\n        i = index + 2\n        while i < len(lines) and lines[i].strip().startswith("|"):\n            rows.append(split_table_row(lines[i]))\n            i += 1\n\n        column_count = len(headers)\n        head = []\n        for col, header in enumerate(headers):\n            align = aligns[col] if col < len(aligns) else "left"\n            head.append(\n                f\'<th scope="col" style="text-align:{align}">{self.inline(header)}</th>\'\n            )\n\n        body_rows = []\n        for row in rows:\n            cells = row[:column_count] + [""] * max(0, column_count - len(row))\n            rendered_cells = []\n            for col, cell in enumerate(cells):\n                label = headers[col] if col < len(headers) else "Field"\n                align = aligns[col] if col < len(aligns) else "left"\n                rendered_cells.append(\n                    f\'<td data-label="{escape(label)}" style="text-align:{align}">\'\n                    f"{self.inline(cell)}</td>"\n                )\n            body_rows.append("<tr>" + "".join(rendered_cells) + "</tr>")\n\n        html = (\n            \'<div class="table-frame">\'\n            \'<table class="data-table">\'\n            "<thead><tr>"\n            + "".join(head)\n            + "</tr></thead><tbody>"\n            + "".join(body_rows)\n            + "</tbody></table></div>"\n        )\n        return html, i\n\n    def list_block(self, lines: list[str], index: int, ordered: bool) -> tuple[str, int]:\n        pattern = r"^\\s*\\d+\\.\\s+" if ordered else r"^\\s*[-*]\\s+"\n        tag = "ol" if ordered else "ul"\n        items: list[str] = []\n        i = index\n        while i < len(lines) and re.match(pattern, lines[i]):\n            item = re.sub(pattern, "", lines[i]).strip()\n            items.append(f"<li>{self.inline(item)}</li>")\n            i += 1\n        return f"<{tag}>" + "".join(items) + f"</{tag}>", i\n\n    def fenced_code(self, lines: list[str], index: int) -> tuple[str, int]:\n        language = lines[index].strip().strip("`").strip()\n        i = index + 1\n        code_lines: list[str] = []\n        while i < len(lines) and not lines[i].strip().startswith("```"):\n            code_lines.append(lines[i])\n            i += 1\n        if i < len(lines):\n            i += 1\n        class_name = f\' class="language-{escape(language)}"\' if language else ""\n        return f"<pre><code{class_name}>{escape(chr(10).join(code_lines))}</code></pre>", i\n\n    def paragraph(self, lines: list[str], index: int) -> tuple[str, int]:\n        chunks: list[str] = []\n        i = index\n        while i < len(lines):\n            line = lines[i]\n            stripped = line.strip()\n            if not stripped:\n                break\n            if stripped.startswith("```"):\n                break\n            if re.match(r"^#{1,6}\\s+", stripped):\n                break\n            if looks_like_table(lines, i):\n                break\n            if re.match(r"^\\s*[-*]\\s+", line) or re.match(r"^\\s*\\d+\\.\\s+", line):\n                break\n            chunks.append(stripped)\n            i += 1\n        return f"<p>{self.inline(\' \'.join(chunks))}</p>", i\n\n    def render(self, markdown: str) -> str:\n        lines = markdown.splitlines()\n        blocks: list[str] = []\n        i = 0\n        while i < len(lines):\n            stripped = lines[i].strip()\n            if not stripped:\n                i += 1\n                continue\n            if stripped.startswith("```"):\n                block, i = self.fenced_code(lines, i)\n                blocks.append(block)\n                continue\n            if looks_like_table(lines, i):\n                block, i = self.table(lines, i)\n                blocks.append(block)\n                continue\n            heading = re.match(r"^(#{1,6})\\s+(.+)$", stripped)\n            if heading:\n                level = len(heading.group(1))\n                text = heading.group(2).strip()\n                hid = self.heading_id(text)\n                blocks.append(\n                    f\'<h{level} id="{escape(hid)}">{self.inline(text)}</h{level}>\'\n                )\n                i += 1\n                continue\n            if re.match(r"^\\s*[-*]\\s+", lines[i]):\n                block, i = self.list_block(lines, i, ordered=False)\n                blocks.append(block)\n                continue\n            if re.match(r"^\\s*\\d+\\.\\s+", lines[i]):\n                block, i = self.list_block(lines, i, ordered=True)\n                blocks.append(block)\n                continue\n            block, i = self.paragraph(lines, i)\n            blocks.append(block)\n        return "\\n".join(blocks)\n\n\ndef render_markdown(markdown: str) -> str:\n    return MarkdownRenderer().render(markdown)\n\n\ndef extract_title(markdown: str, default: str) -> str:\n    match = re.search(r"^#\\s+(.+)$", markdown, flags=re.MULTILINE)\n    if not match:\n        return default\n    title = match.group(1).strip()\n    if title.lower().startswith("experiment:"):\n        title = title.split(":", 1)[1].strip()\n    return title or default\n\n\ndef extract_run_info(markdown: str) -> dict[str, str]:\n    match = re.search(r"^## Run Info\\s*(.*?)(?=^##\\s+|\\Z)", markdown, flags=re.S | re.M)\n    if not match:\n        return {}\n    info: dict[str, str] = {}\n    for line in match.group(1).splitlines():\n        row = re.match(r"^-\\s+([^:：]+)[:：]\\s*(.*)$", line.strip())\n        if row:\n            info[row.group(1).strip()] = row.group(2).strip()\n    return info\n\n\ndef extract_global_miou(markdown: str) -> str:\n    lines = markdown.splitlines()\n    for idx, line in enumerate(lines):\n        if line.strip() == "### Global Metrics":\n            probe = idx + 1\n            while probe < len(lines) and not lines[probe].strip():\n                probe += 1\n            if looks_like_table(lines, probe):\n                headers = split_table_row(lines[probe])\n                rows: list[list[str]] = []\n                j = probe + 2\n                while j < len(lines) and lines[j].strip().startswith("|"):\n                    rows.append(split_table_row(lines[j]))\n                    j += 1\n                for metric in ("mIoU", "IoU"):\n                    if metric in headers and rows:\n                        pos = headers.index(metric)\n                        if pos < len(rows[0]):\n                            return rows[0][pos].strip()\n    return ""\n\n\ndef run_time_datetime(run_time: str) -> datetime:\n    match = re.search(r"\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}(?::\\d{2})?", run_time)\n    if not match:\n        return datetime.min\n    raw = match.group(0)\n    fmt = "%Y-%m-%d %H:%M:%S" if raw.count(":") == 2 else "%Y-%m-%d %H:%M"\n    try:\n        return datetime.strptime(raw, fmt)\n    except ValueError:\n        return datetime.min\n\n\ndef run_time_sort_token(run_time: str) -> str:\n    value = run_time_datetime(run_time)\n    if value == datetime.min:\n        return ""\n    return value.strftime("%Y%m%d%H%M%S")\n\n\ndef experiment_run_time_sort_key(summary: ExperimentSummary) -> tuple[datetime, float]:\n    return (run_time_datetime(summary.run_time), summary.source.stat().st_mtime)\n\n\ndef experiment_summary_from_markdown(source: Path, markdown: str) -> ExperimentSummary:\n    title = extract_title(markdown, source.stem)\n    run_info = extract_run_info(markdown)\n    best_miou = extract_global_miou(markdown)\n    return ExperimentSummary(\n        title=title,\n        stem=source.stem,\n        page=EXPERIMENTS_SITE_DIR / f"{source.stem}.html",\n        source=source,\n        run_time=run_info.get("Run time", ""),\n        best_iter=run_info.get("Best iter", ""),\n        total_iter=run_info.get("Total iter", ""),\n        reference_log=run_info.get("Reference log", ""),\n        best_miou=best_miou,\n    )\n\n\ndef experiment_summary_from_source(source: Path) -> ExperimentSummary:\n    return experiment_summary_from_markdown(source, source.read_text(encoding="utf-8"))\n\n\ndef collect_experiment_summaries() -> list[ExperimentSummary]:\n    return [\n        experiment_summary_from_source(source)\n        for source in sorted(EXPERIMENTS_DIR.glob("*.md"))\n    ]\n\n\ndef count_rows_after_heading(markdown: str, heading: str) -> int:\n    lines = markdown.splitlines()\n    for idx, line in enumerate(lines):\n        if line.strip().lower() == f"## {heading}".lower():\n            i = idx + 1\n            while i < len(lines):\n                if lines[i].strip().startswith("## "):\n                    return 0\n                if looks_like_table(lines, i):\n                    count = 0\n                    j = i + 2\n                    while j < len(lines) and lines[j].strip().startswith("|"):\n                        if any(cell.strip() for cell in split_table_row(lines[j])):\n                            count += 1\n                        j += 1\n                    return count\n                i += 1\n    return 0\n\n\ndef count_idea_sections(markdown: str) -> dict[str, int]:\n    return {\n        "Active": count_rows_after_heading(markdown, "Active"),\n        "Pending": count_rows_after_heading(markdown, "Pending"),\n        "Verified": count_rows_after_heading(markdown, "Verified"),\n    }\n\n\ndef collect_idea_counts() -> dict[str, int]:\n    source = MEMORY_DIR / "ideas.md"\n    return count_idea_sections(source.read_text(encoding="utf-8"))\n\n\ndef page_shell(output_path: Path, title: str, body: str, active: str) -> str:\n    home_href = href_from(output_path, MEMORY_DIR / "index_4user.html")\n    ideas_href = href_from(output_path, MEMORY_DIR / "ideas_4user.html")\n    experiments_href = href_from(output_path, EXPERIMENTS_SITE_DIR / "index.html")\n    css_href = href_from(output_path, ASSETS_DIR / "report.css")\n    js_href = href_from(output_path, ASSETS_DIR / "report.js")\n\n    def nav_link(label: str, href: str, key: str) -> str:\n        current = \' aria-current="page"\' if key == active else ""\n        return f\'<a href="{href}"{current}>{label}</a>\'\n\n    return f"""<!doctype html>\n<html lang="zh-CN">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>{escape(title)}</title>\n  <link rel="icon" href="data:,">\n  <link rel="stylesheet" href="{css_href}">\n</head>\n<body>\n  <a class="skip-link" href="#content">Skip to content</a>\n  <header class="site-header">\n    <div class="site-shell site-nav">\n      <a class="brand" href="{home_href}">{PROJECT_ROOT.name} Memory</a>\n      <div class="nav-actions">\n        <nav aria-label="Report navigation">\n          {nav_link("Home", home_href, "home")}\n          {nav_link("Ideas", ideas_href, "ideas")}\n          {nav_link("Experiments", experiments_href, "experiments")}\n        </nav>\n        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle color theme">\n          <span class="theme-toggle-icon" aria-hidden="true"></span>\n          <span data-theme-label>Theme</span>\n        </button>\n      </div>\n    </div>\n  </header>\n  <main id="content" class="site-shell">\n{body}\n  </main>\n  <script src="{js_href}"></script>\n</body>\n</html>\n"""\n\n\ndef stat_card(label: str, value: str, note: str = "") -> str:\n    note_html = f"<span>{escape(note)}</span>" if note else ""\n    return (\n        \'<div class="stat-card">\'\n        f"<b>{escape(value)}</b>"\n        f"<small>{escape(label)}</small>"\n        f"{note_html}</div>"\n    )\n\n\ndef build_ideas(generated: str) -> tuple[Path, dict[str, int]]:\n    source = MEMORY_DIR / "ideas.md"\n    markdown = source.read_text(encoding="utf-8")\n    counts = count_idea_sections(markdown)\n    output = MEMORY_DIR / "ideas_4user.html"\n    meta = (\n        \'<section class="report-hero">\'\n        "<p>Ideas</p>"\n        "<h1>Research idea browser</h1>"\n        \'<div class="meta-line">\'\n        f\'Source: <a href="{href_from(output, source)}"><code>memory/ideas.md</code></a>\'\n        f" | Generated: {escape(generated)}"\n        "</div></section>"\n    )\n    summary = (\n        \'<section class="stat-grid" aria-label="Idea summary">\'\n        + stat_card("Active", str(counts["Active"]))\n        + stat_card("Pending", str(counts["Pending"]))\n        + stat_card("Verified", str(counts["Verified"]))\n        + "</section>"\n    )\n    content = f\'{meta}\\n{summary}\\n<section class="markdown-body">{render_markdown(markdown)}</section>\'\n    write_file(output, page_shell(output, "Research Ideas", content, "ideas"))\n    return output, counts\n\n\ndef build_experiment_page(source: Path, generated: str) -> ExperimentSummary:\n    markdown = source.read_text(encoding="utf-8")\n    summary = experiment_summary_from_markdown(source, markdown)\n    title = summary.title\n    run_info = extract_run_info(markdown)\n    output = summary.page\n    index_href = href_from(output, EXPERIMENTS_SITE_DIR / "index.html")\n    reference_log = summary.reference_log\n\n    meta_items = [\n        ("Run time", summary.run_time),\n        ("Best iter", summary.best_iter),\n        ("Total iter", summary.total_iter),\n        ("Best mIoU", summary.best_miou),\n        ("Reference log", reference_log),\n        ("Reference config", run_info.get("Reference config", "")),\n    ]\n    stats = "".join(\n        stat_card(label, value or "N/A") for label, value in meta_items[:4]\n    )\n    source_line = (\n        \'<div class="meta-line">\'\n        f\'<a href="{index_href}">Experiment index</a>\'\n        f\' | Source: <a href="{href_from(output, source)}"><code>{escape(os.path.relpath(source, MEMORY_DIR.parent).replace(os.sep, "/"))}</code></a>\'\n        f" | Generated: {escape(generated)}"\n        "</div>"\n    )\n    if reference_log:\n        source_line = source_line.replace(\n            "</div>",\n            f\' | Log: <code>{escape(reference_log)}</code></div>\',\n        )\n\n    hero = (\n        \'<section class="report-hero">\'\n        "<p>Experiment</p>"\n        f"<h1>{escape(title)}</h1>"\n        f"{source_line}</section>"\n        f\'<section class="stat-grid" aria-label="Experiment summary">{stats}</section>\'\n    )\n    content = f\'{hero}\\n<section class="markdown-body">{render_markdown(markdown)}</section>\'\n    write_file(output, page_shell(output, title, content, "experiments"))\n    return summary\n\n\ndef build_experiments(generated: str) -> list[ExperimentSummary]:\n    summaries = []\n    EXPERIMENTS_SITE_DIR.mkdir(parents=True, exist_ok=True)\n    for source in sorted(EXPERIMENTS_DIR.glob("*.md")):\n        summaries.append(build_experiment_page(source, generated))\n    return summaries\n\n\ndef build_experiment_index(summaries: list[ExperimentSummary], generated: str) -> Path:\n    output = EXPERIMENTS_SITE_DIR / "index.html"\n    rows = []\n    for item in sorted(summaries, key=experiment_run_time_sort_key, reverse=True):\n        rows.append(\n            "<tr>"\n            f\'<td data-label="Experiment"><a href="{href_from(output, item.page)}">{escape(item.title)}</a></td>\'\n            f\'<td data-label="Run time" data-sort-value="{escape(run_time_sort_token(item.run_time))}">{escape(item.run_time or "N/A")}</td>\'\n            f\'<td data-label="Best iter">{escape(item.best_iter or "N/A")}</td>\'\n            f\'<td data-label="Total iter">{escape(item.total_iter or "N/A")}</td>\'\n            f\'<td data-label="Best mIoU">{escape(item.best_miou or "N/A")}</td>\'\n            f\'<td data-label="Reference log"><code>{escape(item.reference_log or "N/A")}</code></td>\'\n            f\'<td data-label="Source"><a href="{href_from(output, item.source)}">Markdown</a></td>\'\n            "</tr>"\n        )\n    table = (\n        \'<div class="table-tools">\'\n        \'<label for="experiment-filter">Filter experiments</label>\'\n        \'<input id="experiment-filter" class="filter-input" type="search" \'\n        \'data-filter-input data-filter-target="#experiments-table" \'\n        \'placeholder="type config, metric, or log path">\'\n        \'<span class="sort-badge">Run time desc</span>\'\n        "</div>"\n        \'<div class="table-frame">\'\n        \'<table id="experiments-table" class="data-table" data-default-sort="run-time-desc">\'\n        "<thead><tr>"\n        \'<th>Experiment</th><th data-sort-key="run-time">Run time</th><th>Best iter</th>\'\n        "<th>Total iter</th><th>Best mIoU</th><th>Reference log</th><th>Source</th>"\n        "</tr></thead><tbody>"\n        + "".join(rows)\n        + "</tbody></table></div>"\n    )\n    body = (\n        \'<section class="report-hero">\'\n        "<p>Experiments</p>"\n        "<h1>Experiment report index</h1>"\n        f\'<div class="meta-line">Generated: {escape(generated)} | Reports: {len(summaries)}</div>\'\n        "</section>"\n        \'<section class="stat-grid" aria-label="Experiment summary">\'\n        + stat_card("Reports", str(len(summaries)))\n        + stat_card("Source folder", "memory/experiments")\n        + stat_card("HTML folder", "memory/experiments_4user")\n        + "</section>"\n        + table\n    )\n    write_file(output, page_shell(output, "Experiment Reports", body, "experiments"))\n    return output\n\n\ndef build_home(\n    generated: str, idea_counts: dict[str, int], summaries: list[ExperimentSummary]\n) -> Path:\n    output = MEMORY_DIR / "index_4user.html"\n    ideas_href = href_from(output, MEMORY_DIR / "ideas_4user.html")\n    experiments_href = href_from(output, EXPERIMENTS_SITE_DIR / "index.html")\n    latest = sorted(summaries, key=lambda row: row.source.stat().st_mtime, reverse=True)[:5]\n    latest_rows = []\n    for item in latest:\n        latest_rows.append(\n            "<tr>"\n            f\'<td data-label="Experiment"><a href="{href_from(output, item.page)}">{escape(item.title)}</a></td>\'\n            f\'<td data-label="Best iter">{escape(item.best_iter or "N/A")}</td>\'\n            f\'<td data-label="Best mIoU">{escape(item.best_miou or "N/A")}</td>\'\n            f\'<td data-label="Run time">{escape(item.run_time or "N/A")}</td>\'\n            "</tr>"\n        )\n    latest_table = (\n        \'<div class="table-frame">\'\n        \'<table class="data-table">\'\n        "<thead><tr><th>Experiment</th><th>Best iter</th><th>Best mIoU</th><th>Run time</th></tr></thead>"\n        "<tbody>"\n        + "".join(latest_rows)\n        + "</tbody></table></div>"\n    )\n    body = (\n        \'<section class="report-hero">\'\n        "<p>Static reports</p>"\n        f"<h1>{PROJECT_ROOT.name} memory browser</h1>"\n        f\'<div class="meta-line">Generated: {escape(generated)} | Source folder: <code>memory/</code></div>\'\n        "</section>"\n        \'<section class="link-grid" aria-label="Report sections">\'\n        f\'<a class="link-card" href="{ideas_href}"><strong>Ideas</strong><span>{idea_counts["Active"]} active, {idea_counts["Pending"]} pending, {idea_counts["Verified"]} verified</span></a>\'\n        f\'<a class="link-card" href="{experiments_href}"><strong>Experiments</strong><span>{len(summaries)} generated reports</span></a>\'\n        "</section>"\n        "<h2>Recently updated experiments</h2>"\n        f"{latest_table}"\n    )\n    write_file(output, page_shell(output, f"{PROJECT_ROOT.name} Memory Browser", body, "home"))\n    return output\n\n\ndef write_file(path: Path, content: str) -> None:\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_text(content, encoding="utf-8", newline="\\n")\n\n\ndef resolve_experiment_source(raw: str) -> Path:\n    raw_path = Path(raw)\n    candidates: list[Path] = []\n\n    def add_candidate(path: Path) -> None:\n        full_path = path if path.is_absolute() else PROJECT_ROOT / path\n        if full_path not in candidates:\n            candidates.append(full_path)\n\n    if raw_path.suffix.lower() == ".md":\n        add_candidate(raw_path)\n    elif len(raw_path.parts) == 1:\n        stem = raw_path.stem if raw_path.suffix else raw_path.name\n        candidates.append(EXPERIMENTS_DIR / f"{stem}.md")\n    else:\n        add_candidate(raw_path.with_suffix(".md"))\n        candidates.append(EXPERIMENTS_DIR / f"{raw_path.stem}.md")\n\n    experiments_root = EXPERIMENTS_DIR.resolve()\n    for candidate in candidates:\n        source = candidate.resolve()\n        if source.exists():\n            if source.suffix.lower() != ".md":\n                raise SystemExit(f"Experiment source is not Markdown: {source}")\n            if source.parent.resolve() != experiments_root:\n                raise SystemExit(\n                    "Experiment source must be under memory/experiments: "\n                    f"{source}"\n                )\n            return source\n    raise SystemExit(f"Experiment Markdown not found: {raw}")\n\n\ndef unique_sources(raw_sources: Sequence[str]) -> list[Path]:\n    sources: list[Path] = []\n    seen: set[Path] = set()\n    for raw in raw_sources:\n        source = resolve_experiment_source(raw)\n        if source not in seen:\n            sources.append(source)\n            seen.add(source)\n    return sources\n\n\ndef parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:\n    parser = argparse.ArgumentParser(\n        description="Build static HTML views for project memory Markdown records."\n    )\n    parser.add_argument(\n        "--experiments",\n        "--experiment",\n        nargs="+",\n        metavar="SOURCE",\n        help=(\n            "Render selected experiment Markdown files. SOURCE can be a config stem, "\n            "a .py config name, or a path under memory/experiments."\n        ),\n    )\n    parser.add_argument(\n        "--ideas",\n        action="store_true",\n        help="Render memory/ideas_4user.html from memory/ideas.md.",\n    )\n    return parser.parse_args(argv)\n\n\ndef main(argv: Sequence[str] | None = None) -> None:\n    args = parse_args(argv)\n    generated = generated_at()\n    ASSETS_DIR.mkdir(parents=True, exist_ok=True)\n\n    if not args.experiments and not args.ideas:\n        ideas_path, idea_counts = build_ideas(generated)\n        summaries = build_experiments(generated)\n        experiments_index = build_experiment_index(summaries, generated)\n        home_path = build_home(generated, idea_counts, summaries)\n        print(f"Generated {home_path}")\n        print(f"Generated {ideas_path}")\n        print(f"Generated {experiments_index}")\n        print(f"Generated {len(summaries)} experiment pages")\n        return\n\n    experiment_pages: list[Path] = []\n    experiments_index: Path | None = None\n    if args.experiments:\n        for source in unique_sources(args.experiments):\n            summary = build_experiment_page(source, generated)\n            experiment_pages.append(summary.page)\n        summaries = collect_experiment_summaries()\n        experiments_index = build_experiment_index(summaries, generated)\n    else:\n        summaries = collect_experiment_summaries()\n\n    if args.ideas:\n        ideas_path, idea_counts = build_ideas(generated)\n    else:\n        ideas_path = None\n        idea_counts = collect_idea_counts()\n\n    home_path = build_home(generated, idea_counts, summaries)\n    print(f"Generated {home_path}")\n    if ideas_path:\n        print(f"Generated {ideas_path}")\n    if experiments_index:\n        print(f"Generated {experiments_index}")\n    for page in experiment_pages:\n        print(f"Generated {page}")\n    if experiment_pages:\n        print(f"Generated {len(experiment_pages)} selected experiment pages")\n\n\nif __name__ == "__main__":\n    main()\n'

def research_report_css_content() -> str:
    return ':root {\n  color-scheme: light;\n  --bg: #eef8ff;\n  --paper: #ffffff;\n  --paper-soft: #dff3ff;\n  --ink: #12304a;\n  --muted: #5e7890;\n  --line: #2d8cc9;\n  --line-soft: rgba(45, 140, 201, 0.22);\n  --line-strong: #176fa9;\n  --accent: #158fd3;\n  --accent-2: #4bb8ea;\n  --accent-3: #246ca8;\n  --soft: #d9f2ff;\n  --soft-2: #cceeff;\n  --row-alt: rgba(75, 184, 234, 0.1);\n  --shadow: 5px 5px 0 rgba(45, 140, 201, 0.18);\n  --focus: 0 0 0 3px rgba(21, 143, 211, 0.24);\n}\n\nhtml[data-theme="dark"] {\n  color-scheme: dark;\n  --bg: #082235;\n  --paper: #0d334d;\n  --paper-soft: #123e5c;\n  --ink: #eaf8ff;\n  --muted: #a8cadd;\n  --line: #7fd3ff;\n  --line-soft: rgba(127, 211, 255, 0.2);\n  --line-strong: #9de0ff;\n  --accent: #8bd9ff;\n  --accent-2: #58bee9;\n  --accent-3: #bde9ff;\n  --soft: #164965;\n  --soft-2: #1b5a7d;\n  --row-alt: rgba(127, 211, 255, 0.08);\n  --shadow: 5px 5px 0 rgba(0, 0, 0, 0.28);\n  --focus: 0 0 0 3px rgba(139, 217, 255, 0.34);\n}\n\n* {\n  box-sizing: border-box;\n}\n\nhtml {\n  min-width: 0;\n}\n\nbody {\n  min-width: 0;\n  margin: 0;\n  background: var(--bg);\n  color: var(--ink);\n  font-family: "Trebuchet MS", "Microsoft YaHei", "Segoe UI", sans-serif;\n  font-size: 15px;\n  line-height: 1.58;\n}\n\na {\n  color: var(--accent);\n  text-decoration-thickness: 2px;\n  text-underline-offset: 4px;\n}\n\ncode {\n  max-width: 100%;\n  border: 1px solid var(--line-soft);\n  border-radius: 5px;\n  background: var(--soft);\n  color: var(--accent);\n  padding: 1px 5px;\n  white-space: normal;\n  overflow-wrap: anywhere;\n}\n\npre {\n  max-width: 100%;\n  border: 2px solid var(--line);\n  border-radius: 8px;\n  background: var(--paper);\n  color: var(--ink);\n  padding: 16px;\n  white-space: pre-wrap;\n  overflow-wrap: anywhere;\n  box-shadow: var(--shadow);\n}\n\npre code {\n  border: 0;\n  background: transparent;\n  color: inherit;\n  padding: 0;\n}\n\n.skip-link {\n  position: absolute;\n  left: 16px;\n  top: -80px;\n  z-index: 10;\n  border: 2px solid var(--line);\n  border-radius: 6px;\n  background: var(--paper);\n  padding: 8px 10px;\n  box-shadow: var(--shadow);\n}\n\n.skip-link:focus {\n  top: 12px;\n}\n\n.site-shell {\n  width: min(1420px, calc(100% - 48px));\n  margin-inline: auto;\n}\n\n.site-header {\n  position: sticky;\n  top: 0;\n  z-index: 5;\n  border-bottom: 2px solid var(--line);\n  background: var(--bg);\n  backdrop-filter: blur(10px);\n}\n\n.site-nav {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 18px;\n  min-height: 58px;\n}\n\n.brand {\n  color: var(--ink);\n  font-family: "Segoe Print", "Bradley Hand ITC", "Microsoft YaHei", cursive;\n  font-size: 18px;\n  font-weight: 900;\n  text-decoration: none;\n}\n\n.nav-actions {\n  display: flex;\n  align-items: center;\n  gap: 12px;\n  flex-wrap: wrap;\n  justify-content: flex-end;\n}\n\n.site-nav nav {\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  flex-wrap: wrap;\n  justify-content: flex-end;\n}\n\n.site-nav nav a {\n  border: 1px solid transparent;\n  border-radius: 999px;\n  color: var(--ink);\n  padding: 6px 11px;\n  text-decoration: none;\n  transition: transform 140ms ease, background 140ms ease, box-shadow 140ms ease;\n}\n\n.site-nav nav a[aria-current="page"] {\n  border-color: var(--line);\n  background: var(--soft);\n  box-shadow: 2px 2px 0 var(--line-soft);\n}\n\n.theme-toggle {\n  display: inline-flex;\n  align-items: center;\n  gap: 8px;\n  min-height: 34px;\n  border: 2px solid var(--line);\n  border-radius: 999px;\n  background: var(--paper);\n  color: var(--ink);\n  cursor: pointer;\n  font: inherit;\n  font-size: 13px;\n  font-weight: 800;\n  padding: 5px 12px;\n  box-shadow: 3px 3px 0 var(--line-soft);\n  transition: transform 140ms ease, background 140ms ease, box-shadow 140ms ease;\n}\n\n.theme-toggle:focus-visible,\n.filter-input:focus-visible,\na:focus-visible {\n  outline: none;\n  box-shadow: var(--focus);\n}\n\n.theme-toggle:hover,\n.site-nav nav a:hover,\n.link-card:hover {\n  transform: translate(-1px, -1px);\n}\n\n.theme-toggle-icon {\n  position: relative;\n  width: 18px;\n  height: 18px;\n  border: 2px solid var(--line);\n  border-radius: 50%;\n  background: linear-gradient(90deg, var(--ink) 0 50%, transparent 50% 100%);\n}\n\nhtml[data-theme="dark"] .theme-toggle-icon {\n  background: linear-gradient(90deg, transparent 0 50%, var(--ink) 50% 100%);\n}\n\nmain {\n  padding: 34px 0 64px;\n}\n\n.report-hero {\n  border-bottom: 2px solid var(--ink);\n  padding: 20px 0 24px;\n}\n\n.report-hero p {\n  margin: 0 0 8px;\n  color: var(--accent-2);\n  font-size: 13px;\n  font-weight: 800;\n  letter-spacing: 0;\n  text-transform: uppercase;\n}\n\nh1,\nh2,\nh3,\nh4,\nh5,\nh6 {\n  font-family: "Segoe Print", "Bradley Hand ITC", "Microsoft YaHei", cursive;\n  letter-spacing: 0;\n  line-height: 1.18;\n  overflow-wrap: anywhere;\n}\n\nh1 {\n  max-width: 1050px;\n  margin: 0;\n  font-size: 36px;\n}\n\nh2 {\n  margin: 36px 0 14px;\n  font-size: 22px;\n}\n\nh3 {\n  margin: 28px 0 12px;\n  color: var(--accent-3);\n  font-size: 18px;\n}\n\nh4,\nh5,\nh6 {\n  margin: 22px 0 10px;\n  font-size: 16px;\n}\n\n.meta-line {\n  margin-top: 12px;\n  color: var(--muted);\n  font-size: 13px;\n  overflow-wrap: anywhere;\n}\n\n.stat-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n  gap: 12px;\n  margin: 20px 0 24px;\n}\n\n.stat-card,\n.link-card {\n  min-width: 0;\n  border: 2px solid var(--line);\n  border-radius: 8px;\n  background: var(--paper);\n  box-shadow: var(--shadow);\n}\n\n.stat-card {\n  padding: 14px 16px;\n}\n\n.stat-card b {\n  display: block;\n  color: var(--ink);\n  font-size: 24px;\n  line-height: 1.1;\n  overflow-wrap: anywhere;\n}\n\n.stat-card small,\n.stat-card span {\n  display: block;\n  margin-top: 6px;\n  color: var(--muted);\n  font-size: 12px;\n  overflow-wrap: anywhere;\n}\n\n.link-grid {\n  display: grid;\n  grid-template-columns: repeat(2, minmax(0, 1fr));\n  gap: 14px;\n  margin: 22px 0 28px;\n}\n\n.link-card {\n  display: block;\n  padding: 18px;\n  color: var(--ink);\n  text-decoration: none;\n  transition: transform 140ms ease, box-shadow 140ms ease;\n}\n\n.link-card strong {\n  display: block;\n  font-size: 20px;\n}\n\n.link-card span {\n  display: block;\n  margin-top: 6px;\n  color: var(--muted);\n}\n\n.markdown-body {\n  min-width: 0;\n}\n\n.markdown-body > h1:first-child {\n  display: none;\n}\n\n.markdown-body p,\n.markdown-body li {\n  max-width: 1120px;\n  overflow-wrap: anywhere;\n}\n\n.markdown-body ul,\n.markdown-body ol {\n  padding-left: 22px;\n}\n\n.markdown-body li + li {\n  margin-top: 4px;\n}\n\n.table-tools {\n  display: grid;\n  grid-template-columns: minmax(120px, 180px) minmax(0, 1fr) auto;\n  align-items: center;\n  gap: 12px;\n  margin: 20px 0 10px;\n}\n\n.table-tools label {\n  color: var(--muted);\n  font-size: 13px;\n  font-weight: 700;\n}\n\n.filter-input {\n  width: 100%;\n  min-width: 0;\n  border: 2px solid var(--line);\n  border-radius: 999px;\n  background: var(--paper);\n  color: var(--ink);\n  font: inherit;\n  padding: 10px 12px;\n  box-shadow: 3px 3px 0 var(--line-soft);\n}\n\n.sort-badge {\n  border: 2px solid var(--line);\n  border-radius: 999px;\n  background: var(--soft-2);\n  color: var(--ink);\n  font-size: 12px;\n  font-weight: 800;\n  padding: 7px 11px;\n  white-space: nowrap;\n}\n\n.table-frame {\n  max-width: 100%;\n  min-width: 0;\n  margin: 12px 0 20px;\n  border: 2px solid var(--line);\n  border-radius: 8px;\n  background: var(--paper);\n  box-shadow: var(--shadow);\n  overflow: visible;\n}\n\n.data-table {\n  width: 100%;\n  max-width: 100%;\n  min-width: 0;\n  border-collapse: collapse;\n  table-layout: fixed;\n}\n\n.data-table th,\n.data-table td {\n  min-width: 0;\n  border-bottom: 1px solid var(--line-soft);\n  padding: 10px 11px;\n  text-align: left;\n  vertical-align: top;\n  white-space: normal;\n  overflow-wrap: anywhere;\n  word-break: normal;\n}\n\n.data-table th {\n  background: var(--paper-soft);\n  color: var(--ink);\n  font-size: 12px;\n  font-weight: 800;\n}\n\n.data-table tbody tr:nth-child(even) td {\n  background: var(--row-alt);\n}\n\n.data-table tbody tr:hover td {\n  background: var(--soft);\n}\n\n.data-table tr:last-child td {\n  border-bottom: 0;\n}\n\n.data-table td:empty::after {\n  content: "N/A";\n  color: var(--muted);\n}\n\n.data-table [hidden] {\n  display: none;\n}\n\n#experiments-table th:nth-child(1) {\n  width: 26%;\n}\n\n#experiments-table th:nth-child(2) {\n  width: 18%;\n}\n\n#experiments-table th:nth-child(3),\n#experiments-table th:nth-child(4),\n#experiments-table th:nth-child(5) {\n  width: 9%;\n}\n\n#experiments-table th:nth-child(6) {\n  width: 20%;\n}\n\n#experiments-table th:nth-child(7) {\n  width: 9%;\n}\n\n@media (max-width: 980px) {\n  .stat-grid {\n    grid-template-columns: repeat(2, minmax(0, 1fr));\n  }\n}\n\n@media (max-width: 760px) {\n  .site-shell {\n    width: min(100% - 24px, 1420px);\n  }\n\n  .site-nav {\n    align-items: flex-start;\n    flex-direction: column;\n    padding: 12px 0;\n  }\n\n  .nav-actions {\n    align-items: flex-start;\n    justify-content: flex-start;\n  }\n\n  .site-nav nav {\n    justify-content: flex-start;\n  }\n\n  main {\n    padding-top: 24px;\n  }\n\n  h1 {\n    font-size: 26px;\n  }\n\n  .stat-grid,\n  .link-grid,\n  .table-tools {\n    grid-template-columns: 1fr;\n  }\n\n  .table-frame {\n    border: 0;\n    background: transparent;\n    box-shadow: none;\n  }\n\n  .data-table,\n  .data-table thead,\n  .data-table tbody,\n  .data-table tr,\n  .data-table th,\n  .data-table td {\n    display: block;\n    width: 100%;\n  }\n\n  .data-table thead {\n    display: none;\n  }\n\n  .data-table tbody tr {\n    border: 2px solid var(--line);\n    border-radius: 8px;\n    background: var(--paper);\n    box-shadow: var(--shadow);\n    margin-bottom: 12px;\n    overflow: hidden;\n  }\n\n  .data-table th,\n  .data-table td {\n    border-bottom: 1px solid var(--line-soft);\n    padding: 10px 12px;\n  }\n\n  .data-table td {\n    display: grid;\n    grid-template-columns: minmax(90px, 34%) minmax(0, 1fr);\n    gap: 10px;\n    text-align: left !important;\n  }\n\n  .data-table td::before {\n    content: attr(data-label);\n    color: var(--muted);\n    font-size: 12px;\n    font-weight: 800;\n    overflow-wrap: anywhere;\n  }\n\n  .data-table tr:last-child td {\n    border-bottom: 1px solid var(--line-soft);\n  }\n\n  .data-table td:last-child {\n    border-bottom: 0;\n  }\n}\n'


def research_report_js_content() -> str:
    return '(function () {\n  function storedTheme() {\n    try {\n      return window.localStorage.getItem("seg-report-theme");\n    } catch (error) {\n      return null;\n    }\n  }\n\n  function saveTheme(theme) {\n    try {\n      window.localStorage.setItem("seg-report-theme", theme);\n    } catch (error) {\n      return;\n    }\n  }\n\n  function systemTheme() {\n    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {\n      return "dark";\n    }\n    return "light";\n  }\n\n  function applyTheme(theme) {\n    var nextTheme = theme === "dark" ? "dark" : "light";\n    document.documentElement.setAttribute("data-theme", nextTheme);\n    document.querySelectorAll("[data-theme-label]").forEach(function (label) {\n      label.textContent = nextTheme === "dark" ? "Dark" : "Light";\n    });\n  }\n\n  function attachThemeToggle() {\n    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {\n      button.addEventListener("click", function () {\n        var current = document.documentElement.getAttribute("data-theme") || systemTheme();\n        var nextTheme = current === "dark" ? "light" : "dark";\n        applyTheme(nextTheme);\n        saveTheme(nextTheme);\n      });\n    });\n  }\n\n  function labelTables() {\n    document.querySelectorAll(".data-table").forEach(function (table) {\n      var headers = Array.from(table.querySelectorAll("thead th")).map(function (th) {\n        return th.textContent.trim() || "Field";\n      });\n      table.querySelectorAll("tbody tr").forEach(function (row) {\n        Array.from(row.children).forEach(function (cell, index) {\n          if (!cell.getAttribute("data-label")) {\n            cell.setAttribute("data-label", headers[index] || "Field");\n          }\n        });\n      });\n    });\n  }\n\n  function sortDefaultTables() {\n    document.querySelectorAll(\'[data-default-sort="run-time-desc"]\').forEach(function (table) {\n      var sortHeader = table.querySelector(\'[data-sort-key="run-time"]\');\n      var headers = Array.from(table.querySelectorAll("thead th"));\n      var index = headers.indexOf(sortHeader);\n      var body = table.querySelector("tbody");\n      if (index < 0 || !body) {\n        return;\n      }\n      Array.from(body.querySelectorAll("tr"))\n        .sort(function (left, right) {\n          var leftValue = Number(left.children[index].getAttribute("data-sort-value") || 0);\n          var rightValue = Number(right.children[index].getAttribute("data-sort-value") || 0);\n          return rightValue - leftValue;\n        })\n        .forEach(function (row) {\n          body.appendChild(row);\n        });\n    });\n  }\n\n  function attachFilters() {\n    document.querySelectorAll("[data-filter-input]").forEach(function (input) {\n      var target = document.querySelector(input.getAttribute("data-filter-target"));\n      if (!target) {\n        return;\n      }\n      input.addEventListener("input", function () {\n        var query = input.value.trim().toLowerCase();\n        target.querySelectorAll("tbody tr").forEach(function (row) {\n          var text = row.textContent.toLowerCase();\n          row.hidden = query.length > 0 && text.indexOf(query) === -1;\n        });\n      });\n    });\n  }\n\n  applyTheme(storedTheme() || systemTheme());\n  labelTables();\n  sortDefaultTables();\n  attachFilters();\n  attachThemeToggle();\n})();\n'

def research_memory_index_content() -> str:
    return """# Memory

科研类项目记忆用于记录课题状态、模型迭代、实验结果、数据集、模型结构、想法和执行失败经验。

- `experiments/`：不包含子文件夹，直接按模型配置名称创建 `.md` 文件，记录对应实验指标。
- `experiments_4user/`：存放由实验 Markdown 和日志生成的自包含 HTML 浏览报告，不作为指标或证据来源。
- `architectures/`：不包含子文件夹，直接按模型配置名称创建 `.md` 文件，记录模型结构、模块作用、对应代码文件或函数。
- `datasets/`：不包含子文件夹，直接按数据集名称创建 `.md` 文件，记录数据集信息。
- `mission/`：按新的模型配置名称分文件夹，存放每次迭代任务的 `plan.md` 和 `task.md`。
- `templates/`：存放可复用模板。创建迭代任务的 plan 时使用 `memory/templates/mission_plan.md`，创建实验记录时使用 `memory/templates/experiment.md`，创建模型结构记录时使用 `memory/templates/architecture.md`，创建数据集记录时使用 `memory/templates/dataset.md`。
- `model_iter.md`：按 encoder-decoder 结构记录模型迭代，相同系列放在一起。
- `ideas.md`：记录 active、pending、verified 三类想法。
- `ideas_4user.html`：存放由 `ideas.md` 生成的自包含 HTML 浏览页，不作为想法来源。
- `lesson.md`：记录每次指令或命令执行失败时的原指令、失败现象、原因和之后应使用的正确指令。
"""


def research_model_iter_content() -> str:
    return """# Model Iteration

## Latest

- Latest config:<模型配置代码文件>
- Latest code file:<模型代码>
- Latest architecture:<对应<architecture>.md文档>
- Latest experiment record:<对应<experiments>.md文档>
- Status:<未验证、已验证>
- Baseline:<encoder+decoder+模块（极简描述，比如prior，entropy）>

## Series: <encoder+decoder>

| Config | Parent | Main Change | Status | Best Metric | Experiment |
|---|---|---|---|---:|---|
"""


def research_ideas_content() -> str:
    return """# Ideas

## Active

已实现，正在等待结果。Active 中不记录 experiment 和 logs；如果已有训练或测试结果，需要移动到 Verified。

| Idea | Proposed Time | Hypothesis | Theory Support | Config | Code Location | Status |
|---|---|---|---|---|---|---|

## Pending

待实现。

| Idea | Proposed Time | Hypothesis | Theory Support | Expected Change | Priority | Notes |
|---|---|---|---|---|---|---|

## Verified

已验证。记录对应 experiments、logs、代码文件和函数位置。

| Idea | Theory Support | Result | Config | Experiment | Logs | Code Location | Decision |
|---|---|---|---|---|---|---|---|
"""


def research_ideas_html_content() -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ideas</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --surface: #ffffff;
      --text: #1d2433;
      --muted: #667085;
      --line: #d9dee8;
      --accent: #2563eb;
      --active: #0f766e;
      --pending: #b45309;
      --verified: #166534;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.55;
    }
    main {
      width: min(1180px, calc(100vw - 40px));
      margin: 32px auto 56px;
    }
    h1 { margin: 0 0 8px; font-size: 30px; }
    h2 { margin: 28px 0 12px; font-size: 20px; }
    .meta {
      margin: 0 0 24px;
      color: var(--muted);
      font-size: 14px;
    }
    .section {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin-top: 18px;
      overflow-x: auto;
    }
    .tag {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      color: #fff;
      font-size: 12px;
      font-weight: 600;
      margin-right: 8px;
    }
    .active { background: var(--active); }
    .pending { background: var(--pending); }
    .verified { background: var(--verified); }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
      vertical-align: top;
      text-align: left;
    }
    th {
      color: var(--muted);
      font-weight: 650;
      white-space: nowrap;
      background: #fbfcff;
    }
    tr:last-child td { border-bottom: 0; }
    .empty {
      color: var(--muted);
      padding: 12px 0 2px;
    }
    code {
      color: var(--accent);
      background: #eef4ff;
      border-radius: 4px;
      padding: 1px 4px;
    }
  </style>
</head>
<body>
  <main>
    <h1>Ideas</h1>
    <p class="meta">Source: <code>memory/ideas.md</code> | Generated: __GENERATED_AT__ UTC | This HTML file is a derived browser view.</p>

    <section class="section">
      <h2><span class="tag active">Active</span>已实现，正在等待结果</h2>
      <p class="empty">No active ideas yet.</p>
      <table>
        <thead>
          <tr><th>Idea</th><th>Proposed Time</th><th>Hypothesis</th><th>Theory Support</th><th>Config</th><th>Code Location</th><th>Status</th></tr>
        </thead>
        <tbody></tbody>
      </table>
    </section>

    <section class="section">
      <h2><span class="tag pending">Pending</span>待实现</h2>
      <p class="empty">No pending ideas yet.</p>
      <table>
        <thead>
          <tr><th>Idea</th><th>Proposed Time</th><th>Hypothesis</th><th>Theory Support</th><th>Expected Change</th><th>Priority</th><th>Notes</th></tr>
        </thead>
        <tbody></tbody>
      </table>
    </section>

    <section class="section">
      <h2><span class="tag verified">Verified</span>已验证</h2>
      <p class="empty">No verified ideas yet.</p>
      <table>
        <thead>
          <tr><th>Idea</th><th>Theory Support</th><th>Result</th><th>Config</th><th>Experiment</th><th>Logs</th><th>Code Location</th><th>Decision</th></tr>
        </thead>
        <tbody></tbody>
      </table>
    </section>
  </main>
</body>
</html>
""".replace("__GENERATED_AT__", generated_at)


def research_index_html_content(project_name: str) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    escaped_name = project_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_name} Memory Browser</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="report_assets/report.css">
</head>
<body>
  <main class="site-shell">
    <section class="report-hero">
      <p>Static reports</p>
      <h1>{escaped_name} memory browser</h1>
      <div class="meta-line">Generated: {generated_at} UTC | Source folder: <code>memory/</code></div>
    </section>
    <section class="link-grid" aria-label="Report sections">
      <a class="link-card" href="ideas_4user.html"><strong>Ideas</strong><span>Generated from memory/ideas.md</span></a>
      <a class="link-card" href="experiments_4user/index.html"><strong>Experiments</strong><span>Generated from memory/experiments/*.md</span></a>
    </section>
  </main>
  <script src="report_assets/report.js"></script>
</body>
</html>
"""


def research_experiments_index_html_content(project_name: str) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    escaped_name = project_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_name} Experiments</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="../report_assets/report.css">
</head>
<body>
  <main class="site-shell">
    <section class="report-hero">
      <p>Static reports</p>
      <h1>Experiments</h1>
      <div class="meta-line">Generated: {generated_at} UTC | Source folder: <code>memory/experiments/</code></div>
    </section>
    <p>No experiment reports yet.</p>
  </main>
  <script src="../report_assets/report.js"></script>
</body>
</html>
"""


def research_lesson_content() -> str:
    return """# Lesson

记录每次指令或命令执行失败时的原始指令、失败现象、原因和正确执行方式。只记录真实发生的失败，不预设不存在的问题。

| Time | Failed Instruction | Failure | Reason | Correct Instruction |
|---|---|---|---|---|
"""


def research_reference_index_content() -> str:
    return """# Reference Index

记录每篇论文与其对应 notes、trans、code 的索引。

| Paper | Notes | Translation | Code Repository |
|---|---|---|---|
"""


def research_mission_plan_template_content() -> str:
    return """# Plan: <new-config-name>

## Goal

本次迭代要验证什么假设。

## Base

- Base config:
- Base code file:
- Base metrics:
- Relevant logs:

## Changes

- Encoder:
- Decoder:
- Loss:
- Data:
- Training:
- Inference:

## Implementation Steps

### Step1

### Step2

### Step3

### Step...

## Expected Evidence

需要哪些实验结果才能判断有效。

## Risks

可能失败的原因，以及如何识别。
"""


def research_experiment_template_content() -> str:
    return """# Experiment: <config-name>

具体指标内容和数值必须按照 reference log 中的内容填写，禁止虚构和编造。（此句为提醒）

撰写正式实验记录时，删除模板内所有提醒句。（此句为提醒）

所有表格列名保留指标和字段的自然大小写，例如 `mIoU`、`mAcc`、`aAcc`、`mFscore`，不要写成全大写。（此句为提醒）

## Run Info

- Run time:
- Dataset:
- Best iter:
- Total iter:
- Reference log:
- Reference code:
- Reference config:

## Best Iter Metrics

### Per-Modality Average Metrics

Use this table when the experiment has multiple modalities. Compute the mean of each metric for each modality.（此句为提醒）

| Modality | mIoU | F1 | Precision | Recall |
|---|---|---|---|---|

### Per-Class Overall Metrics

| Class | Metric | Value |
|---|---|---|

### Global Metrics

| mIoU | F1 | Precision | Recall |
|---|---|---|---|
|  |  |  |  |
"""


def research_architecture_template_content() -> str:
    return """# Architecture: <config-name>

模型结构记录应从数据输入开始，按实际前向流程记录。没有使用的结构保留标题并写 N/A。（此句为提醒）

撰写正式模型结构记录时，删除模板内所有提醒句。（此句为提醒）

所有表格列名保留字段的自然大小写，不要写成全大写；已有缩写或代码名除外。（此句为提醒）

## Overview

- Config:
- Code file:
- Main class/function:
- Parent/base config:
- Task type:

## Input

输入数据形状、模态、关键字段和进入模型前的张量格式。（此句为提醒）

| Item | Description | Code Location |
|---|---|---|

## Preprocess / Embedding

记录输入归一化、patch embedding、tokenization、positional encoding 等进入主干网络前的处理。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Backbone

记录 CNN、Transformer、Mamba、RNN 或其他主干特征提取结构。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Encoder

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Neck / Feature Aggregation

记录 FPN、ASPP、feature pyramid、multi-scale aggregation、projection 等中间特征整合结构；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Fusion

记录多模态、多分支或多尺度融合方式；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Decoder

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Head

记录 classification head、segmentation head、detection head、regression head 或 task-specific predictor；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Auxiliary Branches

记录 auxiliary head、deep supervision branch、contrastive branch、regularization branch 等辅助结构；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Loss

| Component | Purpose | Code Location |
|---|---|---|

## Postprocess / Inference

记录 threshold、NMS、CRF、resize、argmax、ensemble 或其他推理后处理；没有则写 N/A。（此句为提醒）

| Step | Purpose | Code Location |
|---|---|---|

## Output

记录模型输出张量、预测格式、保存格式或评估入口。（此句为提醒）

| Output | Shape / Format | Purpose | Code Location |
|---|---|---|---|

## Notes

关键设计原因，不超过 5 条。（此句为提醒）
"""


def research_dataset_template_content() -> str:
    return """# Dataset: <dataset-name>

## Source

- 数据集官方链接
- GitHub仓库
- 数据集发布日期
- 数据对应区域
- 数据总数
- 原始数据尺寸

## Split

训练、验证、测试划分。

## Format

输入文件格式、标签格式、关键字段。

## Caveats

数据问题、缺失、偏差、注意事项（官方说的）
"""


def engineering_memory_index_content() -> str:
    return """# Memory

项目记忆按任务状态和开发流程分层。

- `current/`：active 任务集合，可同时存在多个任务；每个任务一个文件夹，彼此独立。
- `ongoing/`：hold 任务集合，也是未完成任务总集，每个任务一个文件夹。
- `history/`：done 任务档案，每个任务一个文件夹。

读取当前状态时先看 `current/` 里的所有任务文件夹。查找 hold 任务看 `ongoing/index.md`。查找 done 任务看 `history/index.md`。

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
        "这里索引所有处于 hold 状态的任务。每条索引用一到两句话说明任务内容。",
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

这里索引已经完成并归档的 done 任务。每条索引用一到两句话说明任务内容。

当前没有已完成任务。
"""


def initialize(
    root: Path,
    project_type: str,
    active_task: str | None,
    task_folder_arg: str | None,
    requirement: str | None,
) -> list[WriteResult]:
    results: list[WriteResult] = []
    task_folder = slugify(task_folder_arg or active_task) if active_task else None
    is_research = project_type == "research"

    results.append(
        write_if_missing(
            root / "AGENTS.md",
            research_agents_content() if is_research else engineering_agents_content(),
            collision_path=root / "AGENTS.project-init.generated.md",
        )
    )
    results.append(
        write_if_missing(
            root / "SOUL.md",
            research_soul_content() if is_research else engineering_soul_content(),
            collision_path=root / "SOUL.project-init.generated.md",
        )
    )

    if is_research:
        results.append(write_if_missing(root / "memory" / "INDEX.md", research_memory_index_content()))
        results.append(
            write_if_missing(
                root / "memory" / "build_user_reports.py",
                research_build_user_reports_content(),
            )
        )
        results.append(write_if_missing(root / "memory" / "model_iter.md", research_model_iter_content()))
        results.append(write_if_missing(root / "memory" / "ideas.md", research_ideas_content()))
        results.append(write_if_missing(root / "memory" / "ideas_4user.html", research_ideas_html_content()))
        results.append(write_if_missing(root / "memory" / "index_4user.html", research_index_html_content(root.name)))
        results.append(
            write_if_missing(
                root / "memory" / "experiments_4user" / "index.html",
                research_experiments_index_html_content(root.name),
            )
        )
        results.append(write_if_missing(root / "memory" / "lesson.md", research_lesson_content()))
        results.append(
            write_if_missing(
                root / "memory" / "report_assets" / "report.css",
                research_report_css_content(),
            )
        )
        results.append(
            write_if_missing(
                root / "memory" / "report_assets" / "report.js",
                research_report_js_content(),
            )
        )
        results.append(
            write_if_missing(
                root / "memory" / "templates" / "mission_plan.md",
                research_mission_plan_template_content(),
            )
        )
        results.append(
            write_if_missing(
                root / "memory" / "templates" / "experiment.md",
                research_experiment_template_content(),
            )
        )
        results.append(
            write_if_missing(
                root / "memory" / "templates" / "architecture.md",
                research_architecture_template_content(),
            )
        )
        results.append(
            write_if_missing(
                root / "memory" / "templates" / "dataset.md",
                research_dataset_template_content(),
            )
        )
        results.append(write_if_missing(root / "reference" / "index.md", research_reference_index_content()))
        for directory in (
            root / root.name,
            root / "memory" / "experiments",
            root / "memory" / "experiments_4user",
            root / "memory" / "architectures",
            root / "memory" / "datasets",
            root / "memory" / "mission",
            root / "memory" / "report_assets",
            root / "memory" / "templates",
            root / "reference" / "papers",
            root / "reference" / "notes",
            root / "reference" / "trans",
            root / "reference" / "code",
            root / "writing",
            root / "outputs" / "logs",
            root / "outputs" / "models",
            root / "outputs" / "zips",
            root / "data",
        ):
            directory.mkdir(parents=True, exist_ok=True)
        return results

    results.append(write_if_missing(root / "memory" / "INDEX.md", engineering_memory_index_content()))
    current_root = root / "memory" / "current"
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
    parser.add_argument(
        "--project-type",
        choices=("engineering", "research"),
        default="engineering",
        help="Project initialization template to use.",
    )
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
    results = initialize(root, args.project_type, args.active_task, args.task_folder, requirement)
    for result in results:
        print(f"{result.action}: {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
