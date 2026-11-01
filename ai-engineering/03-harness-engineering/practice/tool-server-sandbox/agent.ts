import { makeServer } from "./server.ts";

type Server = ReturnType<typeof makeServer>;
export type Step = { name: string; input: unknown } | { answer: string };
export type Log = (line: string) => void;

/** A scripted stand-in for the model: a fixed plan, including the attacks a real model might be talked into. */
export async function runScripted(server: Server, plan: { why: string; name: string; input: unknown }[], log: Log = console.log) {
  const results = [];
  for (const step of plan) {
    const r: any = await server.call(step.name, step.input);
    const text = r.content[0].text.replace(/\s+/g, " ").slice(0, 70);
    log(`${(r.isError ? "BLOCKED" : "ok").padEnd(8)} ${step.why.padEnd(38)} ${text}`);
    results.push({ ...step, isError: Boolean(r.isError), text: r.content[0].text });
  }
  return results;
}

/** The real loop: Claude picks the tools. Used only when MODEL is set. Manual, so every step is visible. */
export async function runClaude(server: Server, model: string, task: string, maxTurns = 8) {
  const { default: Anthropic } = await import("@anthropic-ai/sdk");
  const client = new Anthropic();
  const tools = server.tools.map((t) => ({ name: t.name, description: t.description, input_schema: t.inputSchema }));
  const messages: any[] = [{ role: "user", content: task }];
  for (let turn = 0; turn < maxTurns; turn++) {
    const res = await client.messages.create({ model, max_tokens: 16000, tools, messages });
    if (res.stop_reason === "refusal") return `model refused: ${res.stop_details?.category ?? "unknown"}`;
    messages.push({ role: "assistant", content: res.content });
    if (res.stop_reason !== "tool_use") return res.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("");
    const results = [];
    for (const block of res.content) {
      if (block.type !== "tool_use") continue;
      const out: any = await server.call(block.name, block.input);
      console.log(`${out.isError ? "BLOCKED" : "ok"} ${block.name} ${JSON.stringify(block.input)}`);
      results.push({ type: "tool_result", tool_use_id: block.id, content: out.content[0].text, is_error: Boolean(out.isError) });
    }
    messages.push({ role: "user", content: results }); // all results in one message
  }
  return `stopped: hit the limit of ${maxTurns} turns`;
}
