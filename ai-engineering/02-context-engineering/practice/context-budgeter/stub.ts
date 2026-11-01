import type { Complete } from "./model.ts";

/** Answers only from what it can see: a stub cannot use a document the budgeter dropped. */
export const stub: Complete = async ({ prompt }) => {
  const m = prompt.match(/<retrieved id="([^"]+)">[^<]*?REFUND WINDOW: ([^.]+)\./);
  const text = m ? `${m[2]} [${m[1]}]` : "I can't find that in the supplied documents.";
  return { text, inputTokens: Math.ceil(prompt.length / 4), outputTokens: Math.ceil(text.length / 4) };
};
