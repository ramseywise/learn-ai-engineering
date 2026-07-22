import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// Define the shape we want Claude to return
interface BookReview {
  title: string;
  author: string;
  rating: number; // 1-5
  summary: string;
  themes: string[];
}

// --- Tool-use approach: define a tool whose input IS the structured data ---
// Claude is forced to call this tool, which means its response is valid JSON
// matching the input schema. No parsing heuristics needed.
async function structuredViaToolUse(bookDescription: string) {
  console.log("--- Structured output via tool_use ---");

  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 512,
    tools: [
      {
        name: "record_book_review",
        description:
          "Record a structured review of a book. Always call this tool with your analysis.",
        input_schema: {
          type: "object" as const,
          properties: {
            title: { type: "string", description: "Book title" },
            author: { type: "string", description: "Author name" },
            rating: {
              type: "number",
              description: "Rating from 1 (poor) to 5 (excellent)",
            },
            summary: {
              type: "string",
              description: "One-sentence summary of the book",
            },
            themes: {
              type: "array",
              items: { type: "string" },
              description: "List of major themes",
            },
          },
          required: ["title", "author", "rating", "summary", "themes"],
        },
      },
    ],
    // tool_choice forces Claude to call a specific tool rather than choosing
    tool_choice: { type: "tool", name: "record_book_review" },
    messages: [
      {
        role: "user",
        content: `Analyze this book and record a structured review: ${bookDescription}`,
      },
    ],
  });

  // Find the tool_use block in the response
  const toolUseBlock = response.content.find(
    (block) => block.type === "tool_use"
  );

  if (!toolUseBlock || toolUseBlock.type !== "tool_use") {
    throw new Error("Expected a tool_use block in the response");
  }

  // The input field IS our structured data — no JSON.parse needed
  const review = toolUseBlock.input as BookReview;

  console.log("Structured review:");
  console.log(`  Title:   ${review.title}`);
  console.log(`  Author:  ${review.author}`);
  console.log(`  Rating:  ${review.rating}/5`);
  console.log(`  Summary: ${review.summary}`);
  console.log(`  Themes:  ${review.themes.join(", ")}`);

  return review;
}

async function main() {
  await structuredViaToolUse(
    "Dune by Frank Herbert — an epic science fiction novel set in a desert world " +
      "where noble houses compete for control of a precious spice called melange."
  );
}

main().catch(console.error);
