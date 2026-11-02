// Starter for group-by.md. Implement groupBy; keep the signature.

export function groupBy<T, K extends PropertyKey>(
  items: readonly T[],
  key: (item: T) => K,
): Record<K, T[]> {
  throw new Error("not implemented");
}
