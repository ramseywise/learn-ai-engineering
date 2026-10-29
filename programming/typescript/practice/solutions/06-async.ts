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
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_, reject) => {
    timer = setTimeout(() => reject(new TimeoutError(`timed out after ${ms}ms`)), ms);
  });
  return Promise.race([p, timeout]).finally(() => clearTimeout(timer));
}

// Q2. Call fn up to `attempts` times. Wait baseMs, 2*baseMs, 4*baseMs … between tries.
//     Rethrow the last error if every attempt fails.
export async function retry<T>(fn: () => Promise<T>, attempts: number, baseMs = 100): Promise<T> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (i < attempts - 1) await sleep(baseMs * 2 ** i);
    }
  }
  throw lastError;
}

// Q3. Like Promise.all(items.map(fn)) but with at most `limit` calls in flight.
//     Results keep the input order.
export async function mapLimit<T, R>(items: readonly T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const results = new Array<R>(items.length);
  let next = 0;
  async function worker(): Promise<void> {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i]!);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return results;
}

// Q4. Run every task; split the outcomes instead of failing fast (Promise.allSettled).
export async function partitionSettled<T>(tasks: Promise<T>[]): Promise<{ ok: T[]; errors: unknown[] }> {
  const ok: T[] = [];
  const errors: unknown[] = [];
  for (const r of await Promise.allSettled(tasks)) {
    if (r.status === 'fulfilled') ok.push(r.value);
    else errors.push(r.reason);
  }
  return { ok, errors };
}
