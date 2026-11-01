// The only file in this lab that knows about a provider.
// Default: the stub passed in by the caller, so the lab runs offline with no key.
// Set MODEL=claude-opus-5-5 (the SDK is an optional dependency) to use a real model.

export interface Completion {
  text: string;
  inputTokens: number;
  outputTokens: number;
}
export interface Request {
  system?: string;
  prompt: string;
  maxTokens?: number;
}
export type Complete = (req: Request) => Promise<Completion>;

export async function realModel(model: string): Promise<Complete> {
  // Loaded lazily so the stub path needs no dependency at all.
  const { default: Anthropic } = await import("@anthropic-ai/sdk");
  const client = new Anthropic(); // ANTHROPIC_API_KEY or an `ant auth login` profile
  return async ({ system, prompt, maxTokens = 16000 }) => {
    const res = await client.beta.messages.create({
      model,
      max_tokens: maxTokens,
      ...(system ? { system } : {}),
      messages: [{ role: "user", content: prompt }],
      // Re-runs a safety decline on Anthropic's recommended fallback model. Delete both
      // lines if you would rather see the refusal, or on Bedrock, Vertex and Foundry.
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
    });
    if (res.stop_reason === "refusal") throw new Error(`model refused: ${res.stop_details?.category ?? "unknown"}`);
    const text = res.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("");
    return { text, inputTokens: res.usage.input_tokens, outputTokens: res.usage.output_tokens };
  };
}

/** `MODEL` set: the real model. Unset: the stub. */
export async function chooseModel(stub: Complete): Promise<{ name: string; complete: Complete }> {
  const id = process.env.MODEL;
  return id ? { name: id, complete: await realModel(id) } : { name: "stub", complete: stub };
}
