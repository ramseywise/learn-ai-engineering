"""The shape of a model call. The stub implements it, and a real provider adapter would too.
Every request carries tenant_id and run_id, because the budget key has to be something every call carries."""
from __future__ import annotations

import math
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


class ModelError(Exception):
    """A clean provider failure: nothing was billed, so the reservation is released."""


def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)  # a rough estimate; a real adapter would use the provider's counter


@dataclass(frozen=True)
class ModelRequest:
    tenant_id: str
    run_id: str
    alias: str
    system: str
    prompt: str
    max_tokens: int
    turn: int = 0


@dataclass(frozen=True)
class Completion:
    text: str = ""
    tool_call: tuple[str, dict] | None = None
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


Model = Callable[[ModelRequest], Awaitable[Completion]]
