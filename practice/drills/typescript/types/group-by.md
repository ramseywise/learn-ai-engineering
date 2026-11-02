---
title: Typed groupBy
track: typescript
topic: types
difficulty: easy
timebox_min: 15
concepts: [generics, keyof-propertykey, record-types]
source: original
units: [programming/typescript]
---

## Prompt

Implement `groupBy(items, key)`: return an object mapping each key to the items that
produced it, in input order. It has to be **generic** — the result's keys and values are
typed from the inputs, with no `any`. Don't mutate the input.

Say out loud before writing: why `K extends PropertyKey` and not `K extends string`? What is
the type of `groupBy(orders, o => o.status)`?

## Starter

[`group-by.ts`](group-by.ts) — keep the signature, replace the body.

## Tests

```bash
node --test group-by.test.ts   # Node 22.18+ runs .ts directly
```

[`group-by.test.ts`](group-by.test.ts): string keys, number keys, empty input, no mutation.

<details>
<summary>Solution</summary>

```ts
export function groupBy<T, K extends PropertyKey>(
  items: readonly T[],
  key: (item: T) => K,
): Record<K, T[]> {
  const out = {} as Record<K, T[]>;
  for (const item of items) {
    const k = key(item);
    (out[k] ??= []).push(item);
  }
  return out;
}
```

</details>

## Notes

- **`PropertyKey`** is `string | number | symbol`, the set of valid object keys; it lets
  `n => n % 2` work. `K` then narrows to the literal union, so
  `groupBy(orders, o => o.status)` is `Record<"open" | "paid", Order[]>`.
- **`readonly T[]`** accepts both mutable and readonly arrays and documents that you won't
  mutate.
- **The `as` cast** on `{}` is the one honest cast here: the object starts empty and fills
  up. Alternatives are `Partial<Record<K, T[]>>` (more honest about missing keys) or `Map<K, T[]>`.
- **`??=`** creates the bucket on first sight; no `if (!out[k])` branch.
- **Follow-ups**: return a `Map` instead; `Object.groupBy` (ES2024) and why its return type
  is `Partial<Record<…>>`; group then aggregate (`sumBy`).
