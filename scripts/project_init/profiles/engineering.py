from __future__ import annotations

from pathlib import Path

from ..core import WriteResult, copy_mission_memory, copy_template_file, slugify, template_context


def initialize_engineering(
    root: Path,
    active_task: str | None,
    task_folder_arg: str | None,
    requirement: str | None,
    with_subtask: bool = False,
) -> list[WriteResult]:
    task_folder = slugify(task_folder_arg or active_task) if active_task else None
    context = template_context(
        root,
        ACTIVE_TASK=active_task,
        TASK_FOLDER=task_folder,
        REQUIREMENT=requirement or "需求待补充。",
        REQUIREMENT_OR_DEFAULT=requirement or "待补充。",
    )

    results: list[WriteResult] = [
        copy_template_file(
            root,
            "engineering/AGENTS.md",
            "AGENTS.md",
            context,
            collision_relative_path="AGENTS.project-init.generated.md",
        ),
        copy_template_file(
            root,
            "engineering/SOUL.md",
            "SOUL.md",
            context,
            collision_relative_path="SOUL.project-init.generated.md",
        ),
        copy_template_file(root, "engineering/memory/INDEX.md", "memory/INDEX.md", context),
    ]

    results.extend(
        copy_mission_memory(
            root,
            context,
            active_task=active_task,
            task_folder=task_folder,
            with_subtask=with_subtask,
        )
    )

    return results
