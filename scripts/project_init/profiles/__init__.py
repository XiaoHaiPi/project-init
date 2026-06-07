from __future__ import annotations

from collections.abc import Callable

from .engineering import initialize_engineering
from .general import initialize_general
from .research import initialize_research

PROFILES: dict[str, Callable] = {
    "engineering": initialize_engineering,
    "research": initialize_research,
    "general": initialize_general,
}
