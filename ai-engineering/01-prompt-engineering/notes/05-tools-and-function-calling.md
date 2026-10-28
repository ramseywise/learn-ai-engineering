---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 8"
  - https://www.promptingguide.ai/agents/function-calling
  - https://www.promptingguide.ai/applications/function_calling
confidence: high
cleaned: 2026-10-28
---
# 5 — Tools and Function Calling

> The prompt-side view of tools: how a tool definition becomes part of the prompt, and how to write one the model uses correctly. Designing the tool surface of a whole agent belongs to [03-harness/03-tool-design](../../03-harness/notes/03-tool-design.md).

---

## The loop

The model never touches the world. It **proposes** a call, and your code **executes** it and appends the result.

```
messages + tools ──► model ──► tool_calls? ──no──► final answer
                       ▲            │yes
                       │            ▼
                       └── append {"role":"tool", tool_call_id, content} ◄── app runs the function
```

1. Define real functions.
2. Describe them as a JSON schema — `name`, `description`, typed `parameters`.
3. Keep a name → function lookup for dispatch.
4. Loop: send messages and tools → for each returned `tool_call`, parse its arguments, run the function, and append a `tool` message → send again. Stop when the reply has no tool calls.

In a conversational agent, wrap that in an outer user-input loop. The **observation** (tool result) becomes context for the next step, which is ReAct with the bookkeeping done by the API ([03](03-core-techniques.md#react--reason--act)).

---

## Under the hood: it's still document completion

Tool calling is fine-tuning plus API sugar, not a new mechanism ([01](01-how-models-read-prompts.md)). The book's reconstruction of OpenAI's internal format:

- Tool schemas are rendered into the system message as **TypeScript-style declarations** in a `namespace functions {}` block, with descriptions as doc comments.
- A call is just more tokens: `<|im_start|>assistant to=functions.set_room_temp\n{"temp": 76}<|im_end|>`.
- Results come back as a `tool` role message.

Token by token, the model makes a chain of decisions: *tool or text? → which tool? → which argument? → what value? → done?* Every part of your definition — names, descriptions, enums — is prompt text that steers those decisions. **Writing a tool definition is writing a prompt.**

The book also notes the limits of that rendering (as of late 2023, OpenAI): `minimum`, `maximum`, `pattern`, `format`, `minItems` and nested descriptions **didn't make it into the internal prompt**. Validate constraints in code rather than relying on the schema to communicate them.

---

## Writing tool definitions

| Rule | Why |
|---|---|
| **Few tools that partition the domain** — cover the ground, don't overlap | Every extra tool is a distractor; overlapping tools force a coin flip |
| **Self-documenting names** (`get_current_weather`, not `retrieveemail`) | Unbroken lowercase is hard to tokenize and read |
| **Descriptions say *when* to use it**, not just what it does | "Search the web for current information. Use when the user asks about recent events or data that may have changed since training." |
| **Mirror public APIs the model already knows** | Copilot found the model could recite GitHub's docs; matching argument names reduced errors |
| **Few, simple arguments; use `enum`s** | Complex parameter lists burn tokens and accuracy. Never paste a whole web API — design a simplified surface |
| **Avoid long free-text arguments in JSON** | Escaping newlines and quotes is error-prone at length. Claude's XML-style tool format handles this better |
| **Drop arguments the app already knows** | The model will invent plausible placeholders (`"my-org"`, `"my-repo"`) for values it can't see |
| **Lean outputs** | Don't pad results "just in case" — it's noise in the next prompt |
| **Errors that teach** | Phrase errors in the tool's own terms ("`date` must be YYYY-MM-DD"), not raw stack traces, so the model can retry correctly |

Reinforce choices in the system prompt as well, e.g. "Prefer `knowledge_base` for company-specific questions before `web_search`." It seems redundant, but it helps when tools are close in purpose.

---

## Safety: gate in code, not in the prompt

"Always confirm with the user before booking" **will eventually be skipped.** Let the model request any call freely, then intercept side-effecting calls in the application layer and require explicit user approval showing the exact arguments. Tool results are also untrusted input — a fetched web page can carry instructions ([10-adversarial-prompting](10-adversarial-prompting.md#indirect-prompt-injection)). Execution boundaries in depth: [03-harness/04-execution-boundaries](../../03-harness/notes/04-execution-boundaries.md).

---

## Context for a tool-using agent

| Part | Contents |
|---|---|
| Preamble | System rules, tool definitions, optional examples |
| Prior conversation | Earlier turns plus attached **artifacts** (a flight list, a document) |
| Current exchange | The latest user message and the tool traffic it triggers |
| Agent response | The final message — usually the only part that stays in history verbatim |

Practical choices:
- **Expose only the tools relevant to the current state** of the conversation.
- **Summarize large artifacts** and offer a `details(section)` tool to expand them, rather than inlining the whole document.
- **Drop stale history** when the topic shifts.

Context selection is the subject of [02-context](../../02-context/README.md).

---

## Debugging tool calls

Log every step: the tool chosen, its arguments, the observation, and token counts. Most failures fall into four buckets:

| Symptom | Usual fix |
|---|---|
| Wrong tool chosen | Sharpen descriptions; remove overlapping tools; add a routing rule to the system prompt |
| Bad or invented arguments | Add enums and examples in the parameter descriptions; remove arguments the app knows |
| Tool not called when it should be | Say *when* in the description; check the tool is actually being passed |
| Observation misread | Simplify the output format; return less |

For UX, show tool activity to users and let them inspect and **edit arguments and resubmit**, which turns a derailed conversation into a quick correction.

---

## Go deeper

- Book: [Ch 8](../sources/prompt-eng-for-llms/08-conversational-agency.md) (internal format, tool guidelines, conversational agent, UX)
- Agent-level tool design, MCP, skills: [03-harness/notes/03-tool-design.md](../../03-harness/notes/03-tool-design.md)
- Runnable: [notebooks/pe-function-calling.ipynb](../notebooks/pe-function-calling.ipynb) · [notebooks/react.ipynb](../notebooks/react.ipynb) · [notebooks/pe-chatgpt-langchain.ipynb](../notebooks/pe-chatgpt-langchain.ipynb)
- Vendor tool-use docs and benchmarks: [references.md](../references.md#vendor-guides)

---

→ Next: [06-chaining-and-workflows.md](06-chaining-and-workflows.md) — composing many prompts into a pipeline.
