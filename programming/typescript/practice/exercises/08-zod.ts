// 08 — Runtime validation with zod. Run: npm test
// Types vanish at runtime; anything from outside (JSON, env, an LLM) must be parsed.
import { z } from 'zod';

export interface Config {
  model: string;
  maxTokens: number;
  debug: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface User {
  id: number;
  email: string;
  tags: string[];
}

export type Result<T> = { ok: true; value: T } | { ok: false; errors: string[] };

// Q1. Parse environment variables into a Config.
//     MODEL defaults to 'claude-opus-5-5'; MAX_TOKENS is a positive integer string, default 1024;
//     DEBUG is true only for '1' or 'true'. Throw (a ZodError) on a bad MAX_TOKENS.
export function parseConfig(env: Record<string, string | undefined>): Config {
  throw new Error('TODO');
}

// Q2. Parse an unknown value into ChatMessage[]: an array of {role, content}, content non-empty
//     and trimmed. Throw on anything else.
export function parseMessages(input: unknown): ChatMessage[] {
  throw new Error('TODO');
}

// Q3. Parse a User without throwing. id is a positive integer, email a valid email,
//     tags defaults to []. On failure return one "path: message" string per issue,
//     e.g. "email: Invalid email address".
export function safeParseUser(input: unknown): Result<User> {
  throw new Error('TODO');
}

// Q4. An LLM returned text that should contain JSON. Strip an optional ```json fence,
//     JSON.parse it, and validate it as a User. Never throw: bad JSON is an error too.
export function parseUserFromLLM(text: string): Result<User> {
  throw new Error('TODO');
}

void z; // remove once you use it
