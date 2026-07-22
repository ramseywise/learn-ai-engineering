import Anthropic from "@anthropic-ai/sdk";

// Initialize the Anthropic client — reads ANTHROPIC_API_KEY from environment
const client = new Anthropic();

// --- 1. Basic non-streaming message ---
async function basicMessage() {
  console.log("--- Basic message ---");

  const message = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 256,
    messages: [{ role: "user", content: "What is a large language model?" }],
  });

  // message.content is an array of content blocks; grab the first text block
  const text = message.content
    .filter((block) => block.type === "text")
    .map((block) => (block as { type: "text"; text: string }).text)
    .join("");

  console.log("Response:", text);
  console.log("Usage:", message.usage);
}

// --- 2. Streaming message (tokens arrive incrementally) ---
async function streamingMessage() {
  console.log("\n--- Streaming message ---");
  process.stdout.write("Response: ");

  // stream() returns an async iterable of server-sent events
  const stream = await client.messages.stream({
    model: "claude-sonnet-4-20250514",
    max_tokens: 256,
    messages: [
      { role: "user", content: "Count from 1 to 5, one number per line." },
    ],
  });

  for await (const event of stream) {
    // content_block_delta carries incremental text
    if (
      event.type === "content_block_delta" &&
      event.delta.type === "text_delta"
    ) {
      process.stdout.write(event.delta.text);
    }
  }

  const finalMessage = await stream.finalMessage();
  console.log("\nStop reason:", finalMessage.stop_reason);
}

// --- 3. Error handling ---
async function withErrorHandling() {
  console.log("\n--- Error handling ---");
  try {
    await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1, // intentionally tiny to show stop_reason: max_tokens
      messages: [{ role: "user", content: "Tell me a long story." }],
    });
  } catch (err) {
    // Anthropic SDK throws typed errors; check for API errors specifically
    if (err instanceof Anthropic.APIError) {
      console.error(`API error ${err.status}: ${err.message}`);
    } else {
      throw err;
    }
  }
}

async function main() {
  await basicMessage();
  await streamingMessage();
  await withErrorHandling();
}

main().catch(console.error);
