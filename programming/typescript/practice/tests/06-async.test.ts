import assert from 'node:assert/strict';
import { test } from 'node:test';
import type * as M from '../exercises/06-async.ts';
import { target } from './target.ts';

const { withTimeout, retry, mapLimit, partitionSettled, sleep, TimeoutError }: typeof M = await import(target('06-async'));

test('Q1 withTimeout resolves fast promises', async () => {
  assert.equal(await withTimeout(sleep(5).then(() => 'x'), 200), 'x');
});

test('Q1 withTimeout rejects slow promises', async () => {
  await assert.rejects(withTimeout(sleep(200), 10), TimeoutError);
});

test('Q2 retry succeeds after failures', async () => {
  let calls = 0;
  const fn = async () => {
    calls++;
    if (calls < 3) throw new Error(`fail ${calls}`);
    return 'ok';
  };
  assert.equal(await retry(fn, 5, 1), 'ok');
  assert.equal(calls, 3);
});

test('Q2 retry rethrows the last error', async () => {
  let calls = 0;
  await assert.rejects(
    retry(async () => { throw new Error(`fail ${++calls}`); }, 3, 1),
    { message: 'fail 3' },
  );
});

test('Q3 mapLimit keeps order and respects the limit', async () => {
  let inFlight = 0;
  let peak = 0;
  const out = await mapLimit([30, 5, 20, 1, 10], 2, async (ms) => {
    peak = Math.max(peak, ++inFlight);
    await sleep(ms);
    inFlight--;
    return ms * 2;
  });
  assert.deepEqual(out, [60, 10, 40, 2, 20]);
  assert.equal(peak, 2);
});

test('Q4 partitionSettled', async () => {
  const { ok, errors } = await partitionSettled([Promise.resolve(1), Promise.reject(new Error('x')), Promise.resolve(3)]);
  assert.deepEqual(ok, [1, 3]);
  assert.equal(errors.length, 1);
});
