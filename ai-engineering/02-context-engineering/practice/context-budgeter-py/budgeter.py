from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Callable


def estimate(s: str) -> int:
    """Rough token estimate. Swap for a real counter via `Budget.count` (see README)."""
    return math.ceil(len(s) / 4)


@dataclass
class Item:
    id: str
    layer: str  # system | tools | memory | retrieved | history | task
    text: str
    priority: int  # higher survives longer; pinned items are never touched
    pinned: bool = False
    truncatable: bool = False  # retrieved and tool text can be cut; instructions and the task cannot
    turn: int = 0  # history turn index: older turns go first among equals


@dataclass
class Budget:
    window: int
    reserve_output: int  # space kept free for the answer; forgetting this cuts answers off
    safety: float  # margin for estimator error, as a fraction of the window
    count: Callable[[str], int] = estimate
    min_kept: int = 40  # a truncated item keeps at least this many tokens, or is dropped outright


@dataclass
class Decision:
    id: str
    layer: str
    action: str  # kept | truncated | dropped
    before: int
    after: int


@dataclass
class Packed:
    items: list[Item]
    decisions: list[Decision]
    used: int
    limit: int
    by_layer: dict[str, int] = field(default_factory=dict)


# The prompt's reading order. Stable layers first, so a provider's prefix cache can hit.
ORDER = ["system", "tools", "memory", "retrieved", "history", "task"]


def limit_of(b: Budget) -> int:
    return math.floor(b.window * (1 - b.safety)) - b.reserve_output


def _cut(text: str, tokens: int, count: Callable[[str], int]) -> str:
    marker = " [truncated]"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if count(text[:mid] + marker) <= tokens:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + marker


def pack(items: list[Item], budget: Budget) -> Packed:
    """Admit everything, then take the cheapest loss while over budget: lowest priority first,
    oldest first among equals. A truncatable item is cut to what still fits; anything else is
    dropped whole. Raises if the pinned items alone do not fit, because silently dropping an
    instruction is worse than failing loudly.
    """
    count = budget.count
    limit = limit_of(budget)
    working = [replace(i) for i in items]
    size = lambda: sum(count(i.text) for i in working)
    decisions = {i.id: Decision(i.id, i.layer, "kept", count(i.text), count(i.text)) for i in items}

    pinned = sum(count(i.text) for i in working if i.pinned)
    if pinned > limit:
        raise ValueError(f"pinned items need {pinned} tokens, limit is {limit}")

    for v in sorted((i for i in working if not i.pinned), key=lambda i: (i.priority, i.turn)):
        over = size() - limit
        if over <= 0:
            break
        d = decisions[v.id]
        keep = count(v.text) - over
        if v.truncatable and keep >= budget.min_kept:
            v.text = _cut(v.text, keep, count)
            d.action, d.after = "truncated", count(v.text)
        else:
            working.remove(v)
            d.action, d.after = "dropped", 0

    ordered = [i for layer in ORDER for i in sorted((x for x in working if x.layer == layer), key=lambda x: x.turn)]
    by_layer: dict[str, int] = {}
    for i in ordered:
        by_layer[i.layer] = by_layer.get(i.layer, 0) + count(i.text)
    return Packed(ordered, list(decisions.values()), size(), limit, by_layer)


def render(p: Packed) -> str:
    return "\n".join(f'<{i.layer} id="{i.id}">\n{i.text}\n</{i.layer}>' for i in p.items)
