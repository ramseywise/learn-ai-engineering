// 06 — Async patterns. Run: npm test
// Promise is asyncio's awaitable; Promise.all is asyncio.gather.

export class TimeoutError extends Error {
  override name = 'TimeoutError';
}

// Given.
export const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

// Q1. Resolve with p's value, or reject with TimeoutError if it takes longer than ms.
//     Clear the timer either way so the process can exit.
export function withTimeout<T>(p: Promise<T>, ms: number): Promise<T> {
  throw new Error('TODO');
}

// Q2. Call fn up to `attempts` times. Wait baseMs, 2*baseMs, 4*baseMs … between tries.
//     Rethrow the last error if every attempt fails.
export async function retry<T>(fn: () => Promise<T>, attempts: number, baseMs = 100): Promise<T> {
  throw new Error('TODO');
}

// Q3. Like Promise.all(items.map(fn)) but with at most `limit` calls in flight.
//     Results keep the input order.
export async function mapLimit<T, R>(items: readonly T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  throw new Error('TODO');
}

// Q4. Run every task; split the outcomes instead of failing fast (Promise.allSettled).
export async function partitionSettled<T>(tasks: Promise<T>[]): Promise<{ ok: T[]; errors: unknown[] }> {
  throw new Error('TODO');
}
