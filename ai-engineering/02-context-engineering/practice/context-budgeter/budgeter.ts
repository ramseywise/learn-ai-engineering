/** Rough token estimate. Swap for a real counter via `Budget.count` (see README). */
export const estimate = (s: string) => Math.ceil(s.length / 4);

export type Layer = "system" | "tools" | "memory" | "retrieved" | "history" | "task";

export interface Item {
  id: string;
  layer: Layer;
  text: string;
  /** Higher survives longer. Pinned items are never touched. */
  priority: number;
  pinned?: boolean;
  /** Retrieved and tool text can be cut. Instructions and the task cannot. */
  truncatable?: boolean;
  /** History turn index: older turns go first among equals. */
  turn?: number;
}

export interface Budget {
  window: number;
  /** Space kept free for the answer. Forgetting this is how answers get cut off. */
  reserveOutput: number;
  /** Margin for estimator error, as a fraction of the window. */
  safety: number;
  count?: (s: string) => number;
  /** A truncated item keeps at least this many tokens, or is dropped outright. */
  minKept?: number;
}

export interface Decision { id: string; layer: Layer; action: "kept" | "truncated" | "dropped"; before: number; after: number }
export interface Packed {
  items: Item[];
  decisions: Decision[];
  used: number;
  limit: number;
  byLayer: Record<string, number>;
}

/** The prompt's reading order. Stable layers first, so a provider's prefix cache can hit. */
const ORDER: Layer[] = ["system", "tools", "memory", "retrieved", "history", "task"];

export function limitOf(b: Budget): number {
  return Math.floor(b.window * (1 - b.safety)) - b.reserveOutput;
}

function cut(text: string, tokens: number, count: (s: string) => number): string {
  const marker = " [truncated]";
  let lo = 0;
  let hi = text.length;
  while (lo < hi) {
    const mid = Math.ceil((lo + hi) / 2);
    if (count(text.slice(0, mid) + marker) <= tokens) lo = mid;
    else hi = mid - 1;
  }
  return text.slice(0, lo) + marker;
}

/**
 * Packs in two passes. First everything is admitted; then, while over budget, the cheapest
 * loss is taken: lowest priority first, oldest first among equals. A truncatable item is cut
 * down to what still fits; anything else is dropped whole.
 * Throws if the pinned items alone do not fit, because silently dropping an instruction is
 * worse than failing loudly.
 */
export function pack(items: Item[], budget: Budget): Packed {
  const count = budget.count ?? estimate;
  const minKept = budget.minKept ?? 40;
  const limit = limitOf(budget);
  const working = items.map((i) => ({ ...i }));
  const size = () => working.reduce((n, i) => n + count(i.text), 0);
  const decisions = new Map<string, Decision>(
    items.map((i) => [i.id, { id: i.id, layer: i.layer, action: "kept", before: count(i.text), after: count(i.text) }]),
  );

  const pinned = working.filter((i) => i.pinned).reduce((n, i) => n + count(i.text), 0);
  if (pinned > limit) throw new Error(`pinned items need ${pinned} tokens, limit is ${limit}`);

  const victims = working
    .filter((i) => !i.pinned)
    .sort((a, b) => a.priority - b.priority || (a.turn ?? 0) - (b.turn ?? 0));

  for (const v of victims) {
    const over = size() - limit;
    if (over <= 0) break;
    const d = decisions.get(v.id)!;
    const have = count(v.text);
    const keep = have - over;
    if (v.truncatable && keep >= minKept) {
      v.text = cut(v.text, keep, count);
      d.action = "truncated";
      d.after = count(v.text);
    } else {
      working.splice(working.indexOf(v), 1);
      d.action = "dropped";
      d.after = 0;
    }
  }

  const ordered = ORDER.flatMap((l) =>
    working.filter((i) => i.layer === l).sort((a, b) => (a.turn ?? 0) - (b.turn ?? 0)),
  );
  const byLayer: Record<string, number> = {};
  for (const i of ordered) byLayer[i.layer] = (byLayer[i.layer] ?? 0) + count(i.text);
  return { items: ordered, decisions: [...decisions.values()], used: size(), limit, byLayer };
}

export const render = (p: Packed) => p.items.map((i) => `<${i.layer} id="${i.id}">\n${i.text}\n</${i.layer}>`).join("\n");
