// Calls the real Claude API. Needs ANTHROPIC_API_KEY; costs a few cents per run.
//   node examples/claude.ts
// Three patterns from note 09: streaming text, structured output with zod, and a tool loop.
import Anthropic from '@anthropic-ai/sdk';
import { betaZodOutputFormat, betaZodTool } from '@anthropic-ai/sdk/helpers/beta/zod';
import { z } from 'zod';

if (!process.env.ANTHROPIC_API_KEY) {
  console.log('Set ANTHROPIC_API_KEY to run this example.');
  process.exit(0);
}

const client = new Anthropic(); // reads ANTHROPIC_API_KEY
const MODEL = 'claude-opus-5-5';

// If a safety classifier declines a request, `fallbacks: "default"` re-runs it on
// Anthropic's recommended fallback model inside the same call instead of returning a refusal.
const FALLBACK: Pick<Anthropic.Beta.MessageCreateParams, 'betas' | 'fallbacks'> = {
  betas: ['server-side-fallback-2026-07-01'],
  fallbacks: 'default',
};

// 1. Streaming: print text as it arrives, then read the complete message.
async function streamText(): Promise<void> {
  const stream = client.beta.messages.stream({
    model: MODEL,
    max_tokens: 2000,
    ...FALLBACK,
    messages: [{ role: 'user', content: 'In three sentences, why does TypeScript erase types at runtime?' }],
  });
  stream.on('text', (delta) => process.stdout.write(delta));
  const message = await stream.finalMessage();
  console.log(`\n[stop_reason=${message.stop_reason}, output_tokens=${message.usage.output_tokens}]\n`);
}

// 2. Structured output: the response is constrained to the schema and parsed for you.
const Review = z.object({
  sentiment: z.enum(['positive', 'neutral', 'negative']),
  topics: z.array(z.string()),
  summary: z.string(),
});

async function extract(): Promise<z.infer<typeof Review>> {
  const response = await client.beta.messages.parse({
    model: MODEL,
    max_tokens: 4000,
    ...FALLBACK,
    messages: [{ role: 'user', content: 'Review: "Setup took an hour, but the type errors caught two real bugs on day one."' }],
    output_config: { format: betaZodOutputFormat(Review) },
  });
  if (response.stop_reason === 'refusal' || !response.parsed_output) throw new Error('no structured output');
  return response.parsed_output;
}

// 3. Tool use: the tool runner calls `run` for each tool_use block and loops until Claude is done.
//    Inputs are validated against the zod schema before `run` sees them.
const getStock = betaZodTool({
  name: 'get_stock',
  description: 'Units in stock for a product SKU.',
  inputSchema: z.object({ sku: z.string().describe('Product SKU, e.g. "TS-101"') }),
  run: async ({ sku }) => JSON.stringify({ sku, units: sku === 'TS-101' ? 12 : 0 }),
});

async function toolLoop(): Promise<string> {
  const final = await client.beta.messages.toolRunner({
    model: MODEL,
    max_tokens: 16000,
    thinking: { type: 'adaptive' },
    ...FALLBACK,
    tools: [getStock],
    messages: [{ role: 'user', content: 'Are TS-101 and TS-202 both in stock?' }],
  });
  return final.content.flatMap((b) => (b.type === 'text' ? [b.text] : [])).join('\n');
}

try {
  await streamText();
  console.log(await extract());
  console.log(await toolLoop());
} catch (err) {
  if (err instanceof Anthropic.RateLimitError) console.error('Rate limited; try again shortly.');
  else if (err instanceof Anthropic.APIError) console.error(`API error ${err.status}: ${err.message}`);
  else throw err;
  process.exitCode = 1;
}
