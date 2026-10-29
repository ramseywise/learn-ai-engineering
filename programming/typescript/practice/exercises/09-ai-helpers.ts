// 09 — Helpers for a Claude tool-use loop. Run: npm test (no API key needed; nothing here calls the API)
// See ../examples/claude.ts for the same ideas against the real API.
import type Anthropic from '@anthropic-ai/sdk';

export type ToolHandler = (input: unknown) => Promise<string>;

// Q1. Join every text block of a response with "\n". Ignore thinking and tool_use blocks.
export function textOf(message: Anthropic.Message): string {
  throw new Error('TODO');
}

// Q2. Return the tool_use blocks of a response, narrowed to Anthropic.ToolUseBlock.
export function toolUses(message: Anthropic.Message): Anthropic.ToolUseBlock[] {
  throw new Error('TODO');
}

// Q3. Run every tool_use block with its handler and build the next user turn of tool_result blocks,
//     in the same order. An unknown tool or a handler that throws becomes a result with
//     is_error: true and the error message as content — never let one tool crash the loop.
export async function runToolCalls(
  message: Anthropic.Message,
  handlers: Record<string, ToolHandler>,
): Promise<Anthropic.MessageParam> {
  throw new Error('TODO');
}

// Q4. Decide what the loop does next from stop_reason:
//     'tool_use' → 'run_tools'; 'end_turn' or 'stop_sequence' → 'done';
//     'max_tokens' → 'truncated'; 'refusal' → 'refused'; 'pause_turn' → 'continue'.
//     Anything else (null, or a value added to the API later) → 'done'.
export type NextStep = 'run_tools' | 'done' | 'truncated' | 'refused' | 'continue';

export function nextStep(message: Anthropic.Message): NextStep {
  throw new Error('TODO');
}
