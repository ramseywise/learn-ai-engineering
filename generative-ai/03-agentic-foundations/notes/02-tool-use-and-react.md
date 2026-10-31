---
origin: course-synthesis
sources:
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 7: P21 Tool Calling, P22 Code Execution — ../sources/lakshmanan-hapke-genai-design-patterns-ch07-enabling-agents-to-take-action.pdf"
  - "DeepLearning.AI, LLMs as Operating Systems: Agent Memory, Lab 1 (self-editing memory from scratch) — https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory"
  - "DeepLearning.AI, AI Agentic Design Patterns with AutoGen, L4 tool use and L5 coding — https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen"
  - "adv-11/AgenticAIFrameworks: AutoGen/react_prompting.py, AutoGen/tool_use_calculator.py, MCP/server.py, MCP/chatbot.py — https://github.com/adv-11/AgenticAIFrameworks"
  - "Yao et al. 2022, ReAct — https://arxiv.org/abs/2210.03629"
  - "Schick et al. 2023, Toolformer — https://arxiv.org/abs/2302.04761"
  - "Beurer-Kellner et al. 2025, Design Patterns for Securing LLM Agents against Prompt Injections — https://arxiv.org/abs/2506.08837"
confidence: high
cleaned: 2026-10-31
---

# 2 — Tool use and the ReAct loop

> The model never runs a tool: it emits a name and arguments, your code runs it and feeds the result back, and a loop of those turns is an agent.

---

## The one mechanism under every framework

Every agent framework in [05](05-framework-survey.md) wraps the same four steps:

| Step | Who | What crosses the wire |
|---|---|---|
| 1. Advertise | client | tool name, description, JSON schema of the arguments |
| 2. Decide | model | either text for the user, or a tool call `{name, arguments}` |
| 3. Execute | client | your code parses the arguments and runs the function |
| 4. Observe | client → model | the result goes back as a tool message; return to step 2 |

The loop stops when the model answers without a tool call, or when a step or token budget runs out. The names differ by vendor: Toolformer called it tool use, Andrew Ng and Anthropic say **tool use**, OpenAI and Gemini say **function calling**. Lakshmanan and Hapke file it as pattern **P21 Tool Calling** and note that ReAct is "just CoT + Tool Calling".

Toolformer ([arXiv:2302.04761](https://arxiv.org/abs/2302.04761), Schick et al., 2023-02) is also the clearest evidence that tool calls help where the model is weakest. GPT-J (6.7B) was shown a few demonstrations per API and wrote candidate calls into its own training text. A call was kept only when inserting its result made the following tokens easier to predict. The model was then fine-tuned on what survived. With a calculator it scored 40.4 on ASDiv, against 14.0 for GPT-3 175B and 14.8 for the same model with tools disabled. With a QA tool it scored 53.5 on LAMA T-REx against GPT-3's 39.8. Each call was a single inline lookup with no chaining. Multi-step tool use needed ReAct-style loops and, later, models trained for function calling.

![ReAct trajectory: thought, action, observation repeated until an answer](../sources/images/li-ai-agents-in-depth-fig1-4.svg)

*Figure: a ReAct trajectory (Li, AI Agents in Depth, ch 1).*

---

## The raw loop, no framework

Lab 1 of the Letta course builds a memory-editing agent in about thirty lines of OpenAI calls. Strip the memory part and what is left is the loop every SDK hides:

```python
# One tool, described by a JSON schema; the enum constrains the section argument.
core_memory_save_metadata = {
    "type": "function",
    "function": {
        "name": "core_memory_save",
        "description": "Save important information about you, the agent or the human you are chatting with.",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {"type": "string", "enum": ["human", "agent"]},
                "memory": {"type": "string"},
            },
            "required": ["section", "memory"],
        },
    },
}

def agent_step(user_message, chat_history):
    chat_history.append({"role": "user", "content": user_message})
    while True:                                   # the agent loop
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "system", "content": "[MEMORY]\n" + json.dumps(agent_memory)}]
                     + chat_history,
            tools=[core_memory_save_metadata],
        )
        msg = response.choices[0].message
        if not msg.tool_calls:                    # plain text: done
            chat_history.append({"role": "assistant", "content": msg.content})
            return msg.content
        chat_history.append(msg)                  # keep the call in history
        call = msg.tool_calls[0]
        result = core_memory_save(**json.loads(call.function.arguments))
        chat_history.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
```

Two details carry over to every real system:

- **The tool call goes back into history before the result.** Most APIs reject a tool result whose call ID they have not seen.
- **The system prompt states the policy.** The lab appends "You must either call a tool (core_memory_save) or write a response to the user. Do not take the same actions multiple times!" Without the second sentence the model can loop on the same call.

The Anthropic Messages API has the same shape with different field names (`MCP/chatbot.py` in AgenticAIFrameworks):

```python
# Anthropic: the model returns content blocks; a tool_use block carries id, name, input.
for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": block.id, "content": result}
        ]})
```

---

## ReAct as a prompt

Before native function calling, ReAct (Yao et al. 2022) was a prompt format that the client parsed. AutoGen's `react_prompting.py` still shows it:

```python
ReAct_prompt = """
Answer the following questions as best you can. You have access to tools provided.
Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take
Action Input: the input to the action
Observation: the result of the action
... (this process can repeat multiple times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
Begin!
Question: {input}
"""
```

| ReAct as text | ReAct with native tool calls |
|---|---|
| Client regex-parses `Action:` lines | Provider returns a structured call |
| Model can hallucinate an `Observation:` | Observation only comes from your code |
| Works on any completion model | Needs a model trained for tool calls |
| Thought is visible text | Thought is optional (reasoning field or omitted) |

Use native calls. Keep the ReAct prompt as a reading of what the loop is doing.

---

## Caller and executor are different agents

AutoGen makes the split explicit: one agent proposes the call, another runs it. That separation is where a human approval step or a sandbox goes.

```python
from typing import Annotated, Literal
from autogen import register_function

Operator = Literal["+", "-", "*", "/"]          # becomes an enum in the schema

def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:
    if operator == "+": return a + b
    if operator == "-": return a - b
    if operator == "*": return a * b
    if operator == "/": return int(a / b)
    raise ValueError("Invalid operator")

register_function(
    calculator,
    caller=assistant,       # the LLM agent that sees the schema
    executor=user_proxy,    # the agent that runs the code (no LLM)
    description="A simple calculator",
)
```

The chess lesson (AutoGen L4) uses the same pattern with `make_move(move: Annotated[str, "A move in UCI format."])`: each player is a caller, a board proxy with `llm_config=False` is the executor, and the board proxy ends the chat as soon as a legal move is made. See [04](04-multi-agent-design-patterns.md) for the conversation structure.

---

## MCP: tools served over a protocol

The Model Context Protocol moves the tool list out of the client process. A server declares tools, resources and prompts; any MCP client can list and call them.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("research", port=8001)

@mcp.tool()                                  # callable by the model
def search_papers(topic: str, max_results: int = 5) -> list[str]:
    """Search arXiv for a topic and store the results."""
    ...

@mcp.resource("papers://{topic}")            # readable data, addressed by URI
def get_topic_papers(topic: str) -> str: ...

@mcp.prompt()                                # a reusable prompt template
def generate_search_prompt(topic: str, num_papers: int = 5) -> str: ...

if __name__ == "__main__":
    mcp.run(transport="stdio")               # or "sse" for a remote server
```

The book lists three limits of MCP as of May 2025:

| Limit | Workaround |
|---|---|
| No auth enforcement in the spec | OAuth in front of the server (Cloudflare Workers) |
| Mostly one-way: client calls server | A2A or ACP for agent-to-agent collaboration |
| Calls time out at 30–60 s | Streamable HTTP transport, or return a job ID and poll |

For when MCP beats an in-process function, and the tool-contract rules, see [harness 03 — tool design](../../../ai-engineering/03-harness-engineering/notes/03-tool-design.md).

---

## Code execution instead of a tool list

Pattern **P22 Code Execution**: when the task is easier to express as a program than as a sequence of calls, let the model write code and run it in a sandbox. AutoGen L5 gives the model a code executor and a set of pre-written functions it may import:

```python
from autogen.coding import LocalCommandLineCodeExecutor

executor = LocalCommandLineCodeExecutor(
    timeout=60,
    work_dir="coding",
    functions=[get_stock_prices, plot_stock_prices],   # importable by generated code
)
code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    llm_config=False,
    code_execution_config={"executor": executor},
    human_input_mode="ALWAYS",                        # approve every run
)
code_writer_agent.update_system_message(
    code_writer_agent.system_message + executor.format_functions_for_prompt()
)
```

| Use tool calling when | Use code execution when |
|---|---|
| A handful of fixed actions | Open-ended data work, loops, plotting |
| Each action has side effects you must gate | The output is a program or a DSL (SQL, Graphviz) |
| The arguments are short | Many calls would be chained anyway |

The book's rules for P22: run in a sandbox with CPU, memory, network and time limits (Docker or a VM); validate before running (parse, static analysis); send errors back so the model can repair them (P18 Reflection). It works best with a narrow DSL plus a parser. `LocalCommandLineCodeExecutor` runs on the host: the lab is fine, production is not. Execution boundaries are covered in [harness 04](../../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md).

---

## Making tool calls reliable

From the P21 section of the book, plus what the labs show:

| Rule | Why |
|---|---|
| Clear names and descriptions; one job per tool | The description is the only documentation the model reads |
| State a usage policy in the system prompt | "Call X before Y", "never call Z twice" |
| Constrain arguments with enums and examples (P2 Grammar) | Removes a whole class of invalid calls |
| Keep the tool list short: 3–10 tools as of June 2025 | Selection accuracy drops as the list grows |
| Don't make the model fill in deterministic values | Inject IDs, dates and user context in code |
| Return descriptive errors, not stack traces | The model can retry (P18 Reflection) |
| Prefer code execution when the input is a DSL | SQL as a string beats twenty filter parameters |

---

## Prompt injection: six defenses

A tool result is untrusted input that lands in the context. Beurer-Kellner et al. (2025), as summarized in ch 7:

| Pattern | Idea |
|---|---|
| Action-Selector | The model picks from fixed actions; tool output never returns to it |
| Plan-Then-Execute | Fix the plan before reading untrusted data; data cannot add steps |
| Map-Reduce | Process each untrusted item in an isolated call; aggregate safe outputs |
| Dual-LLM | A privileged model plans; a quarantined model reads untrusted text and returns symbols |
| Code-Then-Execute | The model writes a program up front; the program, not the model, handles data |
| Context-Minimization | Drop the user prompt or untrusted spans from context before later steps |

Each trades capability for safety. Pick the weakest one that blocks the attack paths your tools open up.

---

## Interview questions

| Question | Short answer |
|---|---|
| Who executes a tool call? | The client. The model only emits name and arguments |
| Why does ReAct work better than CoT alone? | Observations ground the next thought in real data |
| Why put a caller and an executor in different agents? | Approval, sandboxing and auditing sit between them |
| When would you choose code execution over tools? | Open-ended computation or a DSL; when many calls would chain |
| What does MCP add over function calling? | A protocol: tools live in a separate server any client can use |

→ Next: [03 — memory as an operating system](03-memory-as-an-operating-system.md) — what the loop remembers between turns, and how the agent edits it with the same tool calls.
