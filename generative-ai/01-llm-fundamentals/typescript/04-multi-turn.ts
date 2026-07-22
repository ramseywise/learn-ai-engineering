import Anthropic from "@anthropic-ai/sdk";
import * as readline from "readline";

const client = new Anthropic();

// Message history accumulates the full conversation.
// Each entry is a MessageParam: { role: "user" | "assistant", content: string }
const history: Anthropic.MessageParam[] = [];

// System prompt sets persistent context for all turns
const SYSTEM = `You are a helpful coding tutor. Keep answers concise and include
short code examples when relevant. If the user says "quit" or "exit", acknowledge
that you're ending the session.`;

async function chat(userMessage: string): Promise<string> {
  // Append the new user turn to history before sending
  history.push({ role: "user", content: userMessage });

  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    system: SYSTEM,
    // Send the full history so Claude has context from prior turns
    messages: history,
  });

  const assistantText = response.content
    .filter((block) => block.type === "text")
    .map((block) => (block as Anthropic.TextBlock).text)
    .join("");

  // Append Claude's reply to history for the next turn
  history.push({ role: "assistant", content: assistantText });

  return assistantText;
}

// --- Context window management ---
// Token counts grow with each turn. Two strategies:
//
// 1. Sliding window: keep only the last N turns
//    history.splice(0, history.length - MAX_TURNS * 2);
//
// 2. Summarise: send a "summarise the conversation so far" message,
//    replace history with a single user turn containing the summary,
//    then continue.
//
// This example uses neither (fine for short demos), but both approaches
// are shown as commented stubs below.
function trimHistoryIfNeeded(maxTurns = 20) {
  // Each turn = 2 entries (user + assistant). Keep the last maxTurns turns.
  const maxEntries = maxTurns * 2;
  if (history.length > maxEntries) {
    history.splice(0, history.length - maxEntries);
  }
}

async function interactiveLoop() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log('Coding tutor ready. Type "quit" to exit.\n');

  const ask = (prompt: string) =>
    new Promise<string>((resolve) => rl.question(prompt, resolve));

  while (true) {
    const userInput = (await ask("You: ")).trim();
    if (!userInput) continue;

    if (userInput.toLowerCase() === "quit" || userInput.toLowerCase() === "exit") {
      const farewell = await chat(userInput);
      console.log(`\nClaude: ${farewell}\n`);
      break;
    }

    try {
      trimHistoryIfNeeded();
      const reply = await chat(userInput);
      console.log(`\nClaude: ${reply}\n`);
    } catch (err) {
      if (err instanceof Anthropic.APIError) {
        console.error(`API error ${err.status}: ${err.message}`);
      } else {
        throw err;
      }
    }
  }

  rl.close();
  console.log(`Session ended. Total turns: ${history.length / 2}`);
}

// --- Non-interactive demo: runs a scripted 3-turn conversation ---
async function scriptedDemo() {
  const turns = [
    "What's the difference between a Promise and async/await in JavaScript?",
    "Can you show me a quick example comparing both styles for fetching JSON?",
    "What happens if the fetch fails? How do I handle errors in both styles?",
  ];

  for (const turn of turns) {
    console.log(`You: ${turn}`);
    const reply = await chat(turn);
    console.log(`Claude: ${reply}\n`);
  }

  console.log(`History length: ${history.length} messages`);
}

async function main() {
  // Run the scripted demo when stdin is not a TTY (e.g. npx tsx 04-multi-turn.ts)
  // Switch to interactiveLoop() for a live REPL.
  if (process.stdin.isTTY) {
    await interactiveLoop();
  } else {
    await scriptedDemo();
  }
}

main().catch(console.error);
