// Rule-based stand-in for the model, so the routing is what you are watching.
// The one misbehaviour is on purpose: its first draft on a blank-page ticket forgets the citation.
import type { Complete } from "./model.ts";

export const stub: Complete = async ({ system = "", prompt }) => {
  const ticket = /<ticket>\n([\s\S]*?)\n<\/ticket>/.exec(prompt)![1].toLowerCase();
  let text: string;
  if (system.startsWith("CLASSIFY")) {
    text = ticket.includes("blank") ? "bug" : /refund|charged/.test(ticket) ? "billing" : "how_to";
  } else {
    const m = /^\[([\w-]+)\] (.+)$/m.exec(prompt)!;
    const forgets = ticket.includes("blank") && !prompt.includes("Your last draft");
    text = forgets ? m[2] : `${m[2]} [${m[1]}]`;
  }
  return { text, inputTokens: Math.ceil((system.length + prompt.length) / 4), outputTokens: Math.ceil(text.length / 4) };
};
