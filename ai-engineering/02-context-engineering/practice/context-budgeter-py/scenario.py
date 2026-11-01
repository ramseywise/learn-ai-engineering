"""A support agent on turn 8. The answer to the task is in exactly one document: doc-refunds."""
import math

from budgeter import Item


def filler(topic: str, tokens: int) -> str:
    n = math.ceil(tokens * 4 / (len(topic) + 2))
    return ". ".join([topic] * n)[: tokens * 4]


ITEMS = [
    Item("system", "system", "You are the support agent. Answer only from the supplied documents and cite the document id." + filler(" Policy detail", 150), 100, pinned=True),
    Item("tools", "tools", filler("lookup_order(order_id) returns order status", 300), 90, pinned=True),
    Item("memory", "memory", "Customer is on the Team plan and prefers email." + filler(" Earlier preference note", 150), 60),
    Item("doc-refunds", "retrieved", "REFUND WINDOW: annual plans can be refunded within 30 days of renewal." + filler(" Refund procedure detail", 700), 80, truncatable=True),
    Item("doc-seats", "retrieved", filler("Seat management detail", 900), 50, truncatable=True),
    Item("doc-sso", "retrieved", filler("SSO configuration detail", 900), 40, truncatable=True),
    *[Item(f"turn-{t + 1}", "history", f"Turn {t + 1}: " + filler("earlier conversation", 200), 30 + t * 5, turn=t + 1) for t in range(7)],
    Item("task", "task", "How long do I have to get a refund on my annual plan?", 100, pinned=True),
]
