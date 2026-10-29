import assert from 'node:assert/strict';
import { test } from 'node:test';
import type * as M from '../exercises/08-zod.ts';
import { target } from './target.ts';

const { parseConfig, parseMessages, safeParseUser, parseUserFromLLM }: typeof M = await import(target('08-zod'));

test('Q1 parseConfig defaults', () => {
  assert.deepEqual(parseConfig({}), { model: 'claude-opus-5-5', maxTokens: 1024, debug: false });
});

test('Q1 parseConfig coerces', () => {
  assert.deepEqual(parseConfig({ MODEL: 'm', MAX_TOKENS: '64', DEBUG: 'true' }), { model: 'm', maxTokens: 64, debug: true });
  assert.throws(() => parseConfig({ MAX_TOKENS: '-3' }));
  assert.throws(() => parseConfig({ MAX_TOKENS: 'lots' }));
});

test('Q2 parseMessages', () => {
  assert.deepEqual(parseMessages([{ role: 'user', content: '  hi  ' }]), [{ role: 'user', content: 'hi' }]);
  assert.throws(() => parseMessages([{ role: 'system', content: 'x' }]));
  assert.throws(() => parseMessages([{ role: 'user', content: '   ' }]));
  assert.throws(() => parseMessages({ role: 'user', content: 'x' }));
});

test('Q3 safeParseUser', () => {
  assert.deepEqual(safeParseUser({ id: 1, email: 'a@b.co' }), { ok: true, value: { id: 1, email: 'a@b.co', tags: [] } });
  const bad = safeParseUser({ id: 0, email: 'nope' });
  assert.equal(bad.ok, false);
  if (!bad.ok) {
    assert.equal(bad.errors.length, 2);
    assert.ok(bad.errors.some((e) => e.startsWith('id: ')));
    assert.ok(bad.errors.some((e) => e.startsWith('email: ')));
  }
});

test('Q4 parseUserFromLLM', () => {
  const fenced = '```json\n{"id": 7, "email": "x@y.io", "tags": ["vip"]}\n```';
  assert.deepEqual(parseUserFromLLM(fenced), { ok: true, value: { id: 7, email: 'x@y.io', tags: ['vip'] } });
  assert.deepEqual(parseUserFromLLM('Sure! {"id": 7'), { ok: false, errors: ['invalid JSON'] });
  assert.equal(parseUserFromLLM('{"id": "7", "email": "x@y.io"}').ok, false);
});
