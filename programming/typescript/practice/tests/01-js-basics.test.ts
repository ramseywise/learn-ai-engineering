import assert from 'node:assert/strict';
import { test } from 'node:test';
import type * as M from '../exercises/01-js-basics.ts';
import { target } from './target.ts';

const { wordCounts, topN, chunk, zip, uniqueBy, compact }: typeof M = await import(target('01-js-basics'));

test('Q1 wordCounts', () => {
  const c = wordCounts("The cat and the hat. THE end, isn't it?");
  assert.equal(c.get('the'), 3);
  assert.equal(c.get("isn't"), 1);
  assert.equal(c.size, 7);
  assert.equal(wordCounts('').size, 0);
});

test('Q2 topN', () => {
  const c = new Map([['b', 2], ['a', 2], ['c', 5], ['d', 1]]);
  assert.deepEqual(topN(c, 3), [['c', 5], ['a', 2], ['b', 2]]);
  assert.deepEqual(topN(c, 0), []);
});

test('Q3 chunk', () => {
  assert.deepEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
  assert.deepEqual(chunk([], 3), []);
  assert.throws(() => chunk([1], 0), RangeError);
});

test('Q4 zip', () => {
  assert.deepEqual(zip([1, 2, 3], ['a', 'b']), [[1, 'a'], [2, 'b']]);
});

test('Q5 uniqueBy', () => {
  const people = [{ id: 1, n: 'a' }, { id: 2, n: 'b' }, { id: 1, n: 'c' }];
  assert.deepEqual(uniqueBy(people, (p) => p.id).map((p) => p.n), ['a', 'b']);
});

test('Q6 compact', () => {
  assert.deepEqual(compact({ a: 1, b: null, c: undefined, d: 0, e: '' }), { a: 1, d: 0, e: '' });
});
