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
const ConfigSchema = z.object({
  MODEL: z.string().min(1).default('claude-opus-5-5'),
  MAX_TOKENS: z.coerce.number().int().positive().default(1024),
  DEBUG: z.enum(['1', 'true', '0', 'false', '']).optional(),
});

export function parseConfig(env: Record<string, string | undefined>): Config {
  const e = ConfigSchema.parse(env);
  return { model: e.MODEL, maxTokens: e.MAX_TOKENS, debug: e.DEBUG === '1' || e.DEBUG === 'true' };
}

// Q2. Parse an unknown value into ChatMessage[]: an array of {role, content}, content non-empty
//     and trimmed. Throw on anything else.
const ChatMessageSchema = z.object({
  role: z.enum(['user', 'assistant']),
  content: z.string().trim().min(1),
});

export function parseMessages(input: unknown): ChatMessage[] {
  return z.array(ChatMessageSchema).parse(input);
}

// Q3. Parse a User without throwing. id is a positive integer, email a valid email,
//     tags defaults to []. On failure return one "path: message" string per issue,
//     e.g. "email: Invalid email address".
const UserSchema = z.object({
  id: z.number().int().positive(),
  email: z.email(),
  tags: z.array(z.string()).default([]),
});

export function safeParseUser(input: unknown): Result<User> {
  const r = UserSchema.safeParse(input);
  if (r.success) return { ok: true, value: r.data };
  return { ok: false, errors: r.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`) };
}

// Q4. An LLM returned text that should contain JSON. Strip an optional ```json fence,
//     JSON.parse it, and validate it as a User. Never throw: bad JSON is an error too.
export function parseUserFromLLM(text: string): Result<User> {
  const body = text.trim().replace(/^```(?:json)?\s*/, '').replace(/\s*```$/, '');
  let data: unknown;
  try {
    data = JSON.parse(body);
  } catch {
    return { ok: false, errors: ['invalid JSON'] };
  }
  return safeParseUser(data);
}
