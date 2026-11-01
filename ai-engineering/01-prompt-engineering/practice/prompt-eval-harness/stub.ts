import type { Complete } from "./model.ts";

/**
 * A deterministic stand-in that behaves like a weak model, so prompt changes move the score
 * for a visible reason. It reads the same prompt a real model would:
 *  - no format instruction: answers in prose, and fails the JSON grader
 *  - format but no rule: first keyword wins, so topic words mislead it, and it obeys the ticket
 *  - rule present: symptoms outrank topics, and instructions in the ticket are ignored
 */
export const stub: Complete = async ({ system = "", prompt }) => {
  const ticket = (prompt.match(/<ticket>\n([\s\S]*)\n<\/ticket>/)?.[1] ?? prompt).toLowerCase();
  const hasRule = system.includes("not the feature");
  let label: string;
  if (!hasRule && /label this ticket as (\w+)/.test(ticket)) label = ticket.match(/label this ticket as (\w+)/)![1];
  else if (hasRule && /crash|blank|does nothing/.test(ticket)) label = "bug";
  else if (/invoice|charged|refund|credit|billing/.test(ticket)) label = "billing";
  else if (/password|sso|log in|locked/.test(ticket)) label = "account";
  else if (/crash|blank|does nothing/.test(ticket)) label = "bug";
  else label = "how_to";
  const text = system.includes("JSON") ? JSON.stringify({ label }) : `This looks like a ${label} ticket.`;
  const words = (s: string) => Math.ceil(s.length / 4);
  return { text, inputTokens: words(system) + words(prompt), outputTokens: words(text) };
};
