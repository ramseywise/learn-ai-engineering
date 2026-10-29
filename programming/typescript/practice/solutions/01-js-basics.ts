// 01 — JavaScript for Python developers. Run: npm test
// Each function has a Python equivalent in its comment; write the idiomatic TS version.

// Q1. Like collections.Counter(re.findall(r"[a-z']+", text.lower())).
export function wordCounts(text: string): Map<string, number> {
  const counts = new Map<string, number>();
  for (const word of text.toLowerCase().match(/[a-z']+/g) ?? []) {
    counts.set(word, (counts.get(word) ?? 0) + 1);
  }
  return counts;
}

// Q2. Like counter.most_common(n), with ties broken alphabetically.
export function topN(counts: Map<string, number>, n: number): [string, number][] {
  return [...counts.entries()]
    .sort(([a, x], [b, y]) => y - x || a.localeCompare(b))
    .slice(0, n);
}

// Q3. Like [xs[i:i + size] for i in range(0, len(xs), size)].
export function chunk<T>(xs: readonly T[], size: number): T[][] {
  if (size < 1) throw new RangeError('size must be >= 1');
  const out: T[][] = [];
  for (let i = 0; i < xs.length; i += size) out.push(xs.slice(i, i + size));
  return out;
}

// Q4. Like list(zip(a, b)): stops at the shorter input.
export function zip<A, B>(a: readonly A[], b: readonly B[]): [A, B][] {
  return Array.from({ length: Math.min(a.length, b.length) }, (_, i): [A, B] => [a[i]!, b[i]!]);
}

// Q5. Keep the first item for each key, in order. Like {key(x): x for x in reversed(xs)} but order-preserving.
export function uniqueBy<T, K>(xs: readonly T[], key: (x: T) => K): T[] {
  const seen = new Set<K>();
  return xs.filter((x) => {
    const k = key(x);
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

// Q6. Like {k: v for k, v in d.items() if v is not None}. Note: null and undefined are both "None" here.
export function compact<T extends object>(obj: T): Partial<T> {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => v != null)) as Partial<T>;
}
