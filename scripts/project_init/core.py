from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class WriteResult:
    path: Path
    action: str


def skill_root() -> Path:
    return Path(__file__).resolve().parents[2]


def templates_root() -> Path:
    return skill_root() / "templates"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower().strip()).strip("-")
    if slug:
        return slug[:40]
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"task-{digest}"


def generated_at() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def template_context(root: Path, **extra: str | None) -> dict[str, str]:
    context = {
        "PROJECT_NAME": html.escape(root.name),
        "PROJECT_ROOT_NAME": root.name,
        "GENERATED_AT": generated_at(),
    }
    for key, value in extra.items():
        context[key] = "" if value is None else str(value)
    return context


def render_template(text: str, context: dict[str, str]) -> str:
    rendered = text
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def read_template(relative_path: str, context: dict[str, str]) -> str:
    source = templates_root() / relative_path
    return render_template(source.read_text(encoding="utf-8"), context)


def write_if_missing(path: Path, content: str, *, collision_path: Path | None = None) -> WriteResult:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if collision_path is None:
            return WriteResult(path, "exists")
        collision_path.write_text(content, encoding="utf-8", newline="\n")
        return WriteResult(collision_path, f"generated-for-merge:{path.name}")
    path.write_text(content, encoding="utf-8", newline="\n")
    return WriteResult(path, "created")


def copy_template_file(
    root: Path,
    template_relative_path: str,
    target_relative_path: str,
    context: dict[str, str],
    *,
    collision_relative_path: str | None = None,
) -> WriteResult:
    content = read_template(template_relative_path, context)
    collision_path = root / collision_relative_path if collision_relative_path else None
    return write_if_missing(root / target_relative_path, content, collision_path=collision_path)


def copy_template_tree(
    root: Path,
    template_dir_relative_path: str,
    target_dir_relative_path: str,
    context: dict[str, str],
) -> list[WriteResult]:
    source_root = templates_root() / template_dir_relative_path
    target_root = root / target_dir_relative_path
    results: list[WriteResult] = []
    for source in sorted(source_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root)
        content = render_template(source.read_text(encoding="utf-8"), context)
        results.append(write_if_missing(target_root / relative, content))
    return results


def ensure_directories(directories: list[Path]) -> list[WriteResult]:
    results: list[WriteResult] = []
    for directory in directories:
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        results.append(WriteResult(directory, "exists" if existed else "created-dir"))
    return results


MISSION_REQUIRED_FILES = [
    "requirements.md",
    "plan.md",
    "task.md",
    "summary.md",
]


def copy_mission_memory(
    root: Path,
    context: dict[str, str],
    *,
    active_task: str | None,
    task_folder: str | None,
    with_subtask: bool = False,
) -> list[WriteResult]:
    results = [
        copy_template_file(root, "common/memory/mission/INDEX.md", "memory/mission/INDEX.md", context),
        copy_template_file(
            root,
            "common/memory/mission/active/index.active.md"
            if active_task and task_folder
            else "common/memory/mission/active/index.empty.md",
            "memory/mission/active/index.md",
            context,
        ),
        copy_template_file(
            root,
            "common/memory/mission/ongoing/index.md",
            "memory/mission/ongoing/index.md",
            context,
        ),
        copy_template_file(
            root,
            "common/memory/mission/history/index.md",
            "memory/mission/history/index.md",
            context,
        ),
    ]

    if active_task and task_folder:
        filenames = MISSION_REQUIRED_FILES + (["subtask.md"] if with_subtask else [])
        for filename in filenames:
            results.append(
                copy_template_file(
                    root,
                    f"common/memory/mission/task/{filename}",
                    f"memory/mission/active/{task_folder}/{filename}",
                    context,
                )
            )

    return results
