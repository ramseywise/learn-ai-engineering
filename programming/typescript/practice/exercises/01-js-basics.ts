// 01 — JavaScript for Python developers. Run: npm test
// Each function has a Python equivalent in its comment; write the idiomatic TS version.

// Q1. Like collections.Counter(re.findall(r"[a-z']+", text.lower())).
export function wordCounts(text: string): Map<string, number> {
  throw new Error('TODO');
}

// Q2. Like counter.most_common(n), with ties broken alphabetically.
export function topN(counts: Map<string, number>, n: number): [string, number][] {
  throw new Error('TODO');
}

// Q3. Like [xs[i:i + size] for i in range(0, len(xs), size)].
export function chunk<T>(xs: readonly T[], size: number): T[][] {
  throw new Error('TODO');
}

// Q4. Like list(zip(a, b)): stops at the shorter input.
export function zip<A, B>(a: readonly A[], b: readonly B[]): [A, B][] {
  throw new Error('TODO');
}

// Q5. Keep the first item for each key, in order. Like {key(x): x for x in reversed(xs)} but order-preserving.
export function uniqueBy<T, K>(xs: readonly T[], key: (x: T) => K): T[] {
  throw new Error('TODO');
}

// Q6. Like {k: v for k, v in d.items() if v is not None}. Note: null and undefined are both "None" here.
export function compact<T extends object>(obj: T): Partial<T> {
  throw new Error('TODO');
}
