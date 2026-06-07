from __future__ import annotations

import argparse
from pathlib import Path

from .core import WriteResult
from .profiles import PROFILES


def initialize(
    root: Path,
    project_type: str,
    active_task: str | None,
    task_folder_arg: str | None,
    requirement: str | None,
    with_subtask: bool,
) -> list[WriteResult]:
    try:
        initializer = PROFILES[project_type]
    except KeyError as exc:
        valid = ", ".join(sorted(PROFILES))
        raise ValueError(f"unknown project type: {project_type}; valid values: {valid}") from exc
    return initializer(root, active_task, task_folder_arg, requirement, with_subtask)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize project constraints and memory.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Target project root.")
    parser.add_argument(
        "--project-type",
        choices=tuple(sorted(PROFILES)),
        default="engineering",
        help="Project initialization template to use.",
    )
    parser.add_argument("--active-task", help="Optional initial active task name.")
    parser.add_argument("--task-folder", help="Optional folder name for the initial active task.")
    parser.add_argument("--requirement", help="Optional initial active task requirement.")
    parser.add_argument("--goal", help="Deprecated alias for --requirement.")
    parser.add_argument(
        "--with-subtask",
        action="store_true",
        help="Create optional subtask.md for the initial active task.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"project root is not a directory: {root}")

    requirement = args.requirement or args.goal
    results = initialize(
        root,
        args.project_type,
        args.active_task,
        args.task_folder,
        requirement,
        args.with_subtask,
    )
    for result in results:
        print(f"{result.action}: {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
