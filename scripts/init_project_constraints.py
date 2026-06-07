#!/usr/bin/env python3
"""Compatibility entrypoint for the project-init skill."""

from __future__ import annotations

from project_init.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
