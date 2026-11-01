import type { Item } from "./budgeter.ts";

const filler = (topic: string, tokens: number) =>
  Array.from({ length: Math.ceil((tokens * 4) / (topic.length + 2)) }, () => topic).join(". ").slice(0, tokens * 4);

/** A support agent on turn 8. The answer to the task is in exactly one document: doc-refunds. */
export const items: Item[] = [
  { id: "system", layer: "system", priority: 100, pinned: true, text: "You are the support agent. Answer only from the supplied documents and cite the document id." + filler(" Policy detail", 150) },
  { id: "tools", layer: "tools", priority: 90, pinned: true, text: filler("lookup_order(order_id) returns order status", 300) },
  { id: "memory", layer: "memory", priority: 60, text: "Customer is on the Team plan and prefers email." + filler(" Earlier preference note", 150) },
  { id: "doc-refunds", layer: "retrieved", priority: 80, truncatable: true, text: "REFUND WINDOW: annual plans can be refunded within 30 days of renewal." + filler(" Refund procedure detail", 700) },
  { id: "doc-seats", layer: "retrieved", priority: 50, truncatable: true, text: filler("Seat management detail", 900) },
  { id: "doc-sso", layer: "retrieved", priority: 40, truncatable: true, text: filler("SSO configuration detail", 900) },
  ...Array.from({ length: 7 }, (_, t): Item => ({
    id: `turn-${t + 1}`,
    layer: "history",
    turn: t + 1,
    priority: 30 + t * 5,
    text: `Turn ${t + 1}: ` + filler("earlier conversation", 200),
  })),
  { id: "task", layer: "task", priority: 100, pinned: true, text: "How long do I have to get a refund on my annual plan?" },
];
