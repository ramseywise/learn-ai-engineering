// Measures what the simulation assumes: TTFT, TPOT and cached tokens on a real streaming call.
// With no MODEL it times a fake stream, so you can read the code path offline.
const SYSTEM = "You are a support agent. " + "Policy text that stays the same between requests. ".repeat(800);
const PROMPT = "In two sentences, why does a stable prompt prefix matter?";
const clock = () => performance.now();

async function* fakeStream() {
  for (const word of "A stable prefix lets the server reuse its cached work on every request. ".repeat(3).trim().split(" ")) {
    await new Promise((res) => setTimeout(res, 5));
    yield word + " ";
  }
}

function report(label: string, start: number, first: number, end: number, chunks: number, outputTokens: number, cached: number) {
  const tpot = (end - first) / Math.max(outputTokens - 1, 1);
  console.log(`${label}: TTFT ${(first - start).toFixed(0)} ms, total ${(end - start).toFixed(0)} ms, ${outputTokens} output tokens, ${tpot.toFixed(1)} ms per token after the first, ${chunks} chunks, ${cached} tokens read from cache`);
}

const model = process.env.MODEL;
if (!model) {
  const start = clock();
  let first = 0, chunks = 0;
  for await (const _ of fakeStream()) {
    first ||= clock();
    chunks++;
  }
  report("fake stream, not a measurement", start, first, clock(), chunks, chunks, 0);
} else {
  const { default: Anthropic } = await import("@anthropic-ai/sdk");
  const client = new Anthropic(); // ANTHROPIC_API_KEY or an `ant auth login` profile
  for (const label of ["call 1, writes the cache", "call 2, reads the cache"]) {
    const start = clock();
    let first = 0, chunks = 0;
    const stream = client.messages.stream({
      model,
      max_tokens: 4000,
      system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
      messages: [{ role: "user", content: PROMPT }],
    });
    stream.on("text", () => { // first visible text, so any thinking counts toward TTFT
      first ||= clock();
      chunks++;
    });
    const final = await stream.finalMessage();
    const end = clock();
    if (final.stop_reason === "refusal") throw new Error("model refused");
    report(label, start, first || end, end, chunks, final.usage.output_tokens, final.usage.cache_read_input_tokens ?? 0);
  }
}
