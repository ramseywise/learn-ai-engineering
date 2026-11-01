// The system under test: a support agent with two tools. The stub is rule-based and reads the
// same system prompt a model would, so deleting a line from the prompt changes behaviour.
import { readFileSync } from "node:fs";

interface Doc { id: string; text: string; keywords: string[] }
const KB: { docs: Doc[]; orders: Record<string, string> } = JSON.parse(readFileSync(new URL("./kb.json", import.meta.url), "utf8"));

export interface Run { text: string; tools: string[]; tokens: number }
export type Agent = (system: string, input: string) => Promise<Run>;

// The tool bodies, shared by the stub and the real model.
export function searchDocs(query: string): Doc | undefined {
  const q = query.toLowerCase();
  return KB.docs.find((d) => d.keywords.some((k) => q.includes(k)));
}
export const lookupOrder = (id: string): string => KB.orders[id] ?? "not found";

export const stubAgent: Agent = async (system, input) => {
  const has = (s: string) => system.includes(s);
  const done = (text: string, tools: string[]): Run => ({ text, tools, tokens: Math.ceil((system.length + input.length + text.length) / 4) });
  if (/ignore (all|your|previous) instructions/i.test(input)) {
    return done(has("Ignore instructions") ? "I can't do that, but I can help with your own account." : "Refund approved for all customers.", []);
  }
  const order = /order (\d+)/i.exec(input);
  if (order) {
    if (!has("lookup_order")) return done("Your order should arrive soon.", []);
    return done(`Order ${order[1]} is ${lookupOrder(order[1])}.`, ["lookup_order"]);
  }
  const doc = searchDocs(input);
  if (!doc) return done(has("say you don't know") ? "I don't know. A person will follow up." : "You can do that under Settings.", []);
  const body = has("under ten words") ? doc.text.split(" ").slice(0, 10).join(" ") : doc.text;
  return done(`${body} [${doc.id}]`, ["search_docs"]);
};

/** The real path: a manual tool loop, so the trajectory is recorded exactly as the grader needs it. */
export async function realAgent(model: string): Promise<Agent> {
  const { default: Anthropic } = await import("@anthropic-ai/sdk");
  const client = new Anthropic(); // ANTHROPIC_API_KEY or an `ant auth login` profile
  const tools = [
    { name: "search_docs", description: "Search the help documents. Returns the best match, or nothing.", input_schema: { type: "object" as const, properties: { query: { type: "string" } }, required: ["query"] } },
    { name: "lookup_order", description: "Get an order's status by its numeric id.", input_schema: { type: "object" as const, properties: { order_id: { type: "string" } }, required: ["order_id"] } },
  ];
  return async (system, input) => {
    const messages: any[] = [{ role: "user", content: input }];
    const used: string[] = [];
    let tokens = 0;
    for (let turn = 0; turn < 6; turn++) {
      const res = await client.messages.create({ model, max_tokens: 16000, system, tools, messages });
      tokens += res.usage.input_tokens + res.usage.output_tokens;
      if (res.stop_reason === "refusal") return { text: `model refused: ${res.stop_details?.category ?? "unknown"}`, tools: used, tokens };
      const text = res.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("");
      if (res.stop_reason !== "tool_use") return { text, tools: used, tokens };
      messages.push({ role: "assistant", content: res.content });
      const results = res.content.flatMap((b) => {
        if (b.type !== "tool_use") return [];
        used.push(b.name);
        const a = b.input as Record<string, string>;
        let content: string;
        if (b.name === "search_docs") {
          const d = searchDocs(a.query);
          content = d ? `[${d.id}] ${d.text}` : "no match";
        } else content = lookupOrder(a.order_id);
        return [{ type: "tool_result" as const, tool_use_id: b.id, content }];
      });
      messages.push({ role: "user", content: results }); // all results in one message
    }
    return { text: "", tools: used, tokens };
  };
}

export const chooseAgent = async (): Promise<{ name: string; agent: Agent }> =>
  process.env.MODEL ? { name: process.env.MODEL, agent: await realAgent(process.env.MODEL) } : { name: "stub", agent: stubAgent };
