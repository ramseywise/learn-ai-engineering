import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// --- Simulated tool implementations ---
// In a real application these would call APIs, databases, etc.

function getCurrentWeather(location: string, unit: "celsius" | "fahrenheit") {
  // Fake data — substitute a real weather API call here
  const fakeData: Record<string, { temp: number; condition: string }> = {
    "New York": { temp: 22, condition: "partly cloudy" },
    London: { temp: 15, condition: "rainy" },
    Tokyo: { temp: 28, condition: "sunny" },
  };

  const data = fakeData[location] ?? { temp: 20, condition: "unknown" };
  const temp =
    unit === "fahrenheit" ? Math.round(data.temp * 9/5 + 32) : data.temp;
  const unitLabel = unit === "fahrenheit" ? "°F" : "°C";

  return { location, temperature: `${temp}${unitLabel}`, condition: data.condition };
}

function searchWeb(query: string, maxResults: number) {
  // Fake results — substitute a real search API call here
  return {
    query,
    results: Array.from({ length: Math.min(maxResults, 3) }, (_, i) => ({
      title: `Result ${i + 1} for "${query}"`,
      url: `https://example.com/search?q=${encodeURIComponent(query)}&r=${i + 1}`,
    })),
  };
}

// --- Tool definitions (sent to Claude so it knows what's available) ---
const tools: Anthropic.Tool[] = [
  {
    name: "get_current_weather",
    description:
      "Get the current weather for a city. Returns temperature and conditions.",
    input_schema: {
      type: "object" as const,
      properties: {
        location: {
          type: "string",
          description: 'City name, e.g. "London"',
        },
        unit: {
          type: "string",
          enum: ["celsius", "fahrenheit"],
          description: "Temperature unit",
        },
      },
      required: ["location", "unit"],
    },
  },
  {
    name: "search_web",
    description: "Search the web for information on a topic.",
    input_schema: {
      type: "object" as const,
      properties: {
        query: { type: "string", description: "Search query" },
        max_results: {
          type: "number",
          description: "Maximum number of results to return (1-5)",
        },
      },
      required: ["query", "max_results"],
    },
  },
];

// --- Dispatch a tool call to the right implementation ---
function callTool(name: string, input: Record<string, unknown>): unknown {
  switch (name) {
    case "get_current_weather":
      return getCurrentWeather(
        input.location as string,
        input.unit as "celsius" | "fahrenheit"
      );
    case "search_web":
      return searchWeb(input.query as string, input.max_results as number);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// --- Agentic loop: keep going until Claude stops calling tools ---
async function runWithTools(userMessage: string) {
  console.log(`User: ${userMessage}\n`);

  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: userMessage },
  ];

  while (true) {
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      tools,
      messages,
    });

    // Collect any tool calls in this response
    const toolUseBlocks = response.content.filter(
      (block) => block.type === "tool_use"
    );

    if (response.stop_reason === "end_turn" || toolUseBlocks.length === 0) {
      // Claude is done — print the final text response
      const text = response.content
        .filter((block) => block.type === "text")
        .map((block) => (block as Anthropic.TextBlock).text)
        .join("");
      console.log("Claude:", text);
      break;
    }

    // Claude wants to call tools — execute them and feed results back
    console.log(`Claude is calling ${toolUseBlocks.length} tool(s)...`);

    // Add Claude's response (including the tool_use blocks) to history
    messages.push({ role: "assistant", content: response.content });

    // Build a tool_result block for each tool call
    const toolResults: Anthropic.ToolResultBlockParam[] = toolUseBlocks.map(
      (block) => {
        if (block.type !== "tool_use") throw new Error("Unexpected block type");
        const result = callTool(
          block.name,
          block.input as Record<string, unknown>
        );
        console.log(`  → ${block.name}(${JSON.stringify(block.input)}) =>`, result);
        return {
          type: "tool_result" as const,
          tool_use_id: block.id,
          content: JSON.stringify(result),
        };
      }
    );

    // Feed all results back in a single user turn
    messages.push({ role: "user", content: toolResults });
  }
}

async function main() {
  await runWithTools(
    "What's the weather like in Tokyo (in celsius) and what are the top 2 search results for 'Anthropic Claude'?"
  );
}

main().catch(console.error);
