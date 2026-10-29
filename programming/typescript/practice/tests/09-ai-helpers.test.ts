import assert from 'node:assert/strict';
import { test } from 'node:test';
import type Anthropic from '@anthropic-ai/sdk';
import type * as M from '../exercises/09-ai-helpers.ts';
import { target } from './target.ts';

const { textOf, toolUses, runToolCalls, nextStep }: typeof M = await import(target('09-ai-helpers'));

// A fake response: only the fields the helpers read. The cast is fine in a test.
const fake = (content: unknown[], stop_reason: string | null = 'end_turn') =>
  ({ id: 'msg_1', type: 'message', role: 'assistant', model: 'claude-opus-5-5', content, stop_reason }) as unknown as Anthropic.Message;

const response = fake(
  [
    { type: 'thinking', thinking: 'hmm', signature: 's' },
    { type: 'text', text: 'Let me check.' },
    { type: 'tool_use', id: 'tu_1', name: 'add', input: { a: 2, b: 3 } },
    { type: 'tool_use', id: 'tu_2', name: 'nope', input: {} },
    { type: 'tool_use', id: 'tu_3', name: 'boom', input: {} },
    { type: 'text', text: 'Done.' },
  ],
  'tool_use',
);

test('Q1 textOf', () => {
  assert.equal(textOf(response), 'Let me check.\nDone.');
  assert.equal(textOf(fake([])), '');
});

test('Q2 toolUses', () => {
  assert.deepEqual(toolUses(response).map((b) => b.id), ['tu_1', 'tu_2', 'tu_3']);
});

test('Q3 runToolCalls', async () => {
  const turn = await runToolCalls(response, {
    add: async (input) => {
      const { a, b } = input as { a: number; b: number };
      return String(a + b);
    },
    boom: async () => {
      throw new Error('kaboom');
    },
  });
  assert.equal(turn.role, 'user');
  assert.deepEqual(turn.content, [
    { type: 'tool_result', tool_use_id: 'tu_1', content: '5' },
    { type: 'tool_result', tool_use_id: 'tu_2', content: 'unknown tool: nope', is_error: true },
    { type: 'tool_result', tool_use_id: 'tu_3', content: 'kaboom', is_error: true },
  ]);
});

test('Q4 nextStep', () => {
  const cases: [string | null, M.NextStep][] = [
    ['tool_use', 'run_tools'],
    ['end_turn', 'done'],
    ['stop_sequence', 'done'],
    ['max_tokens', 'truncated'],
    ['refusal', 'refused'],
    ['pause_turn', 'continue'],
    [null, 'done'],
  ];
  for (const [reason, step] of cases) assert.equal(nextStep(fake([], reason)), step, String(reason));
});
