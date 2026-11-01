---
origin: course-synthesis
sources:
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 7: P21 Tool Calling, P22 Code Execution — ../sources/lakshmanan-hapke-genai-design-patterns-ch07-enabling-agents-to-take-action.pdf"
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly 2025), ch 5: P13 Chain of Thought; ch 9: P32 Guardrails"
  - "DeepLearning.AI, LLMs as Operating Systems: Agent Memory, Lab 1 (self-editing memory from scratch) — https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory"
  - "DeepLearning.AI, AI Agentic Design Patterns with AutoGen, L4 tool use and L5 coding — https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen"
  - "adv-11/AgenticAIFrameworks: AutoGen/react_prompting.py, AutoGen/tool_use_calculator.py, MCP/server.py, MCP/chatbot.py — https://github.com/adv-11/AgenticAIFrameworks"
  - "Yao et al. 2022, ReAct — https://arxiv.org/abs/2210.03629"
  - "Schick et al. 2023, Toolformer — https://arxiv.org/abs/2302.04761"
  - "Patil et al. 2023, Gorilla — https://arxiv.org/abs/2305.15334"
  - "Qin et al. 2023, ToolLLM — https://arxiv.org/abs/2307.16789"
  - "Beurer-Kellner et al. 2025, Design Patterns for Securing LLM Agents against Prompt Injections — https://arxiv.org/abs/2506.08837"
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 6"
  - "James Phoenix & Mike Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 6"
  - "Nicole Koenigstein, AI Agents: The Definitive Guide (O'Reilly, 2026), ch. 1"
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 2"
  - "Salvatore Raieli & Gabriele Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 11"
  - "Sprague et al. 2024, To CoT or not to CoT? — https://arxiv.org/abs/2409.12183"
  - "Mirzadeh et al. 2024, GSM-Symbolic — https://arxiv.org/abs/2410.05229"
  - "Bran et al. 2023, ChemCrow: Augmenting large-language models with chemistry tools — https://arxiv.org/abs/2304.05376"
  - "Hao et al. 2024, Training Large Language Models to Reason in a Continuous Latent Space (Coconut) — https://arxiv.org/abs/2412.06769"
  - https://arxiv.org/abs/2112.15594
  - https://arxiv.org/abs/2304.09842
  - https://arxiv.org/abs/2305.11554
  - https://arxiv.org/abs/2410.03439
  - https://arxiv.org/abs/2412.00722
  - https://arxiv.org/abs/2502.08235
  - https://arxiv.org/abs/2504.03553
  - https://arxiv.org/abs/2505.10543
  - https://arxiv.org/abs/2602.20502
  - https://arxiv.org/abs/2610.18861
  - https://arxiv.org/abs/2205.12255
  - https://arxiv.org/abs/2209.07753
confidence: high
cleaned: 2026-11-01
---

# 2 — Tool use and the ReAct loop

> The model never runs a tool: it emits a name and arguments, your code runs it and feeds the result back, and a loop of those turns is an agent.

The restock agent from [01](01-agent-fundamentals.md) can only recommend an order until it can see stock and place one. Giving it that reach looks like the model gaining new powers, but the model gains nothing: it still only produces text, some of which your code agrees to treat as a request. Almost everything that matters about tools follows from that split, including who can approve a call, what happens when the arguments are wrong, and why text from a web page can end up steering what runs on your machine.

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

The training recipe came nine months earlier in TALM ([arXiv:2205.12255](https://arxiv.org/abs/2205.12255) (Parisi et al., 2022 ⚑)). It fine-tuned T5 models (220M–3B) to write a text tool call, read the result and then answer. Starting from about 150 hand-written tool demonstrations, it sampled many tool calls per training example and kept only those that led to the right answer, for several rounds. With a BM25 retriever on Natural Questions, the 220M TALM beat a 3B T5 without tools. The paper reports these gains only as figures, and every call was single-hop.

Toolformer ([arXiv:2302.04761](https://arxiv.org/abs/2302.04761), Schick et al., 2023-02) is also the clearest evidence that tool calls help where the model is weakest. GPT-J (6.7B) was shown a few demonstrations per API and wrote candidate calls into its own training text. A call was kept only when inserting its result made the following tokens easier to predict. The model was then fine-tuned on what survived. With a calculator it scored 40.4 on ASDiv, against 14.0 for GPT-3 175B and 14.8 for the same model with tools disabled. With a QA tool it scored 53.5 on LAMA T-REx against GPT-3's 39.8. Each call was a single inline lookup with no chaining. Multi-step tool use needed ReAct-style loops and, later, models trained for function calling.

ChemCrow ([arXiv:2304.05376](https://arxiv.org/abs/2304.05376) (Bran et al., 2023-04)) shows the same effect in a ReAct loop. GPT-4 at temperature 0.1 was given 18 chemistry tools, including name-to-SMILES conversion, reaction planning and a cloud robot lab. It planned and ran real syntheses of DEET and three thiourea organocatalysts. On 14 tasks graded by four expert chemists, tool-less GPT-4 won only the easy tasks it could answer from memory, and ChemCrow won on the harder and novel ones. Two caveats apply. A GPT-4 grader preferred tool-less GPT-4's fluent but wrong answers. And in the authors' own reproducibility check, the tools returned the right product in all 5 runs of one task, but in 2 of them the model misread that product's SMILES string and drew the wrong conclusion about the mechanism.

![ReAct trajectory: thought, action, observation repeated until an answer](../sources/images/li-ai-agents-in-depth-fig1-4.svg)

*Figure: a ReAct trajectory (Li, AI Agents in Depth, ch 1).*

---

## The raw loop, no framework

Lab 1 of the Letta course builds a memory-editing agent in about thirty lines of OpenAI calls. Strip the memory part and what is left is the loop every SDK hides:

```python
# illustrative: needs an OpenAI API key plus `client`, `system_prompt`, `agent_memory` and `core_memory_save` from the Letta lab
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

The Anthropic Messages API has the same shape with different field names: the model returns content blocks, a `tool_use` block carries `id`, `name` and `input`, and results go back in a user message (`MCP/chatbot.py` in AgenticAIFrameworks does this with an older model). Here it is for the restock agent's first tool, with a stub client that replays what the API would return:

```python
# The Messages API loop, with a stub client so it runs offline.
# Replace StubClient() with anthropic.Anthropic() and this loop stays the same.
from types import SimpleNamespace as NS

STOCK = {"itemB": {"on_hand": 100, "peak_weekly": 90, "weeks_to_deliver": 2}}

TOOLS = [{
    "name": "get_stock",
    "description": "Stock on hand, peak weekly sales and delivery time for one item. "
                   "Use before any reorder decision. Unknown items return an error.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {"item": {"type": "string", "description": "Item ID, such as itemB"}},
        "required": ["item"],
        "additionalProperties": False,
    },
}]

def execute_tool(name, args):
    if name != "get_stock":
        return f"Error: unknown tool {name}"
    if args["item"] not in STOCK:                     # an error the model can act on
        return f"Error: no item {args['item']!r}. Known items: {sorted(STOCK)}"
    return str(STOCK[args["item"]])

def tool_use(id_, item):
    return NS(type="tool_use", id=id_, name="get_stock", input={"item": item})

SCRIPT = [
    NS(stop_reason="tool_use", content=[tool_use("t1", "item-B")]),   # a wrong ID, as models do
    NS(stop_reason="tool_use", content=[tool_use("t2", "itemB")]),    # corrected from the error
    NS(stop_reason="end_turn", content=[NS(type="text", text="itemB runs out before delivery. Reorder.")]),
]

class StubClient:
    def __init__(self):
        self.messages = self
        self.sizes = []

    def create(self, **kwargs):
        self.sizes.append(len(kwargs["messages"]))    # what each call re-sends
        return SCRIPT[len(self.sizes) - 1]

client = StubClient()
messages = [{"role": "user", "content": "Should we reorder itemB?"}]

while True:
    response = client.messages.create(
        model="claude-opus-5-5", max_tokens=16000, tools=TOOLS, messages=messages)
    if response.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:                    # one turn can hold several calls
        if block.type == "tool_use":
            output = execute_tool(block.name, block.input)
            print(f"{block.name}({block.input}) -> {output}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
    messages.append({"role": "user", "content": results})

print("stop_reason:", response.stop_reason)
print("answer:", next(b.text for b in response.content if b.type == "text"))
print("messages sent per call:", client.sizes)
```

```text
get_stock({'item': 'item-B'}) -> Error: no item 'item-B'. Known items: ['itemB']
get_stock({'item': 'itemB'}) -> {'on_hand': 100, 'peak_weekly': 90, 'weeks_to_deliver': 2}
stop_reason: end_turn
answer: itemB runs out before delivery. Reorder.
messages sent per call: [1, 3, 5]
```

Three lines in this output are the lesson. The first call fails on a wrong ID, and because the error names the valid items, the model can fix it without help. The message count grows by two per round, which is the quadratic cost from [01](01-agent-fundamentals.md#the-react-loop) in miniature. And the loop tests `stop_reason`, not the presence of text, because a response can stop for other reasons, such as hitting `max_tokens`, that a real system must handle separately. All the tool results from one turn go back in a single user message; sending one message per result, as many older examples do, breaks when the model makes parallel calls.

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

Use native calls. Keep the ReAct prompt as a reading of what the loop is doing. A few lines of parsing show what the left column costs:

```python
# Why text-parsed ReAct is fragile: the client has to find the action in free text.
import re

ACTION = re.compile(r"(?i)action\s*:\s*([^\n]+)")
INPUT = re.compile(r"(?i)action input\s*:\s*([^\n]+)")

def parse(text):
    actions, inputs = ACTION.findall(text), INPUT.findall(text)
    if not actions or not inputs:
        return "parse failure: retry or repair"
    return actions[-1].strip(), inputs[-1].strip()    # the last match, as Phoenix & Taylor advise

good = "Thought: I need the stock.\nAction: get_stock\nAction Input: itemB"
reworded = "Thought: I need the stock, so I'll call get_stock on itemB."
invented = good + "\nObservation: on_hand=100\nThought: done\nAction: place_order\nAction Input: itemB, 300"

for label, text in [("good", good), ("reworded", reworded), ("invented", invented)]:
    print(f"{label:9}", parse(text))
```

```text
good      ('get_stock', 'itemB')
reworded  parse failure: retry or repair
invented  ('place_order', 'itemB, 300')
```

The reworded reply says the right thing and still fails to parse. The third reply is worse: the model invented its own observation and went on to an order, and a last-match parser would run it. The stop sequence described below exists to prevent exactly this.

The switch is measurable. In OpenHands on SWE-bench Verified, o1 at high reasoning effort resolved 29.1% of issues with a text-parsed action format and **47.7% with native function calling**, and its overthinking score fell from 2.43 to 1.05 ([arXiv:2502.08235](https://arxiv.org/abs/2502.08235) (Cuadron et al., 2025-02, preprint)). Overthinking here is a Claude 3.5 Sonnet judge's 0–10 rating of how much the agent reasoned about actions instead of taking them and reading the result. Across about 4,000 trajectories, a higher score went with fewer resolved issues, and reasoning models scored higher than non-reasoning ones (3.5 against 2.2 on average). The format is not the whole story: on BFCL's multi-turn set the same switch moved o1 only from 36% to 41%. The judge was checked against four experts on just 20 traces.

**Acting does not beat thinking on every task.** In the ReAct paper's own HotpotQA result with PaLM-540B, ReAct scored 27.4 EM against 29.4 for CoT. The best score, 35.1, came from falling back to self-consistent CoT when ReAct ran out of steps (Yao et al., ICLR 2023). ALAMA ([arXiv:2412.00722](https://arxiv.org/abs/2412.00722) (Huang et al., COLING 2025)) found the same with one-shot prompts. With Llama-3-8B-Instruct, a ReAct-style retrieval mechanism was the weakest of five on GSM8K (71.8% against 80.1% for Reflection) and no better than plain CoT on HotpotQA (15.8 against 17.6 EM; GPT-3.5 tied them at 22.2). All five mechanisms solved only 42.6% of the GSM8K questions, but an oracle that picked the right mechanism per question solved 96.9%. Training the model to choose for itself reached 82.2%, well short of that ceiling. KnowSelf ([arXiv:2504.03553](https://arxiv.org/abs/2504.03553) (Qiao et al., ACL 2025)) makes the same choice at every step. A fine-tuned Llama-3.1-8B emitted a `[Knowledge]` token to fetch a rule from a knowledge base on 15% of its ALFWorld steps. It scored 84.3, against 77.6 for WKM, which injects knowledge at every step. On Gemma-2B, injecting knowledge at every step scored below reflection alone. So the design question is not ReAct or CoT. It is when the model should reach outside itself.

If you do run ReAct as text, Phoenix and Taylor's hand-built loop shows the three parts you need (*Prompt Engineering for Generative AI*, ch. 6):

- **Parse the last action, not the first.** Use a case-insensitive regex such as `(?i)action\s*:\s*([^\n]+)`, which captures up to the end of the line, and a second one for `action_input`. Take the last match in the response.
- **Stop before the observation.** Pass a stop sequence such as `"tool_result:"` so generation halts where the observation would start. Without it the model writes its own, fabricated, tool result.
- **Expect parse failures.** Either send the bad response to a model to repair it, or retry the request from the previous state.

Their comparison table (Table 6-2) is dated. It credits OpenAI function calling with single tool execution but not with sequential tool execution or an iterative thought process, and it calls ReAct less stable. That described 2023 agent wrappers, not the mechanism. Today a native tool-calling loop does both multi-step sequential calls and parallel calls in one turn, so the right column above is the one to build on.

---

## What reasoning steps fix, and what they do not

ReAct is "CoT + Tool Calling", so it inherits the strengths and limits of chain of thought. Lakshmanan and Hapke's pattern P13 is the clearest statement of both (*Generative AI Design Patterns*, ch. 5).

CoT helps when a model knows the rule but does not apply it, and it comes in three strengths. **Zero-shot** just asks for step-by-step reasoning. **Few-shot** shows worked examples, and it fixes what zero-shot misses: on a baggage question for a Singapore–Dallas–Toronto trip under a 50 kg/40 kg rule, zero-shot Gemini answered 50 kg, while few-shot examples got the correct 40 kg. **Auto-CoT** retrieves the closest examples from a store. Their image for the difference from RAG is that RAG gives the model a few fish, while few-shot CoT shows it how to fish.

Three failure modes matter more for agents than the technique itself:

| CoT fails on | Their example | The fix |
|---|---|---|
| **Gaps in knowledge** | "300 km west of Hyderabad" produces confident steps ending in the wrong city; the answer is Solapur | Supply the fact. Given a map, the model gets it right. For an agent this means a tool, not more reasoning |
| **Exact computation** | 84 m² × 10.7639 written out as 903.20; the true product is 904.1676 | A calculator or code tool |
| **Non-sequential expertise** | Bridge play, where experts weigh the whole hand instead of stepping through it | Examples from an expert, or a specialist model |

The reasoning a model shows can also be a story told after the fact, so asking "why" does not audit it. The book's own success case makes this point by accident. Asked for the flow of crude oil through a 25 cm pipe, zero-shot Claude applied the laminar-flow formula and reported 84 m³/s, while itself remarking that the figure seemed very high and the flow would be turbulent. Dividing by the pipe's area gives a speed of about 1,700 m/s, so the formula does not apply and the number is meaningless. The book still counts this as the prompt triggering the right behavior. Well-formed steps are not evidence of a correct answer, so check the result independently, as with the restock arithmetic.

Providers now apply much of this inside their models, so zero-shot CoT helps small models more than reasoning models, and thinking modes replace the hand-written instruction. The authors' practical advice is to use a thinking model as a teacher that writes examples for a smaller one, and to set a reminder to retest any CoT prompt every six months, since a hotfix or new model may make it unnecessary.

---

## Caller and executor are different agents

AutoGen makes the split explicit: one agent proposes the call, another runs it. That separation is where a human approval step or a sandbox goes.

```python
# illustrative: needs `autogen-agentchat` 0.2 and an LLM API key; `calculator` and the two agents come from the lab
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
# illustrative: needs `mcp` and a client to connect to it; `mcp.run` blocks waiting on stdio
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

**MCP does not bypass the tool call.** Albada describes MCP as a way to "inject rich, dynamic context ... directly into the model's reasoning process without invoking separate tools", unlike API calls that "require full round-trip execution" (*Building Applications with AI Agents*, ch. 2). That is wrong. An MCP tool is invoked through a `tools/call` request and its result returns as an ordinary tool result: a full round trip. Resources and prompts are separate primitives that the client or user chooses to put into context. MCP standardizes how tools and context are discovered and transported. It doesn't give the model a cheaper channel into its reasoning.

For when MCP beats an in-process function, and the tool-contract rules, see [harness 03 — tool design](../../../ai-engineering/03-harness-engineering/notes/03-tool-design.md).

---

## Code execution instead of a tool list

Pattern **P22 Code Execution**: when the task is easier to express as a program than as a sequence of calls, let the model write code and run it in a sandbox. AutoGen L5 gives the model a code executor and a set of pre-written functions it may import:

```python
# illustrative: needs `autogen-agentchat` 0.2 and an LLM API key, and it runs generated code, so use a sandbox
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

Code can also replace the loop itself. Chameleon ([arXiv:2304.09842](https://arxiv.org/abs/2304.09842) (Lu et al., NeurIPS 2023)) had the LLM write the whole tool sequence before running any of it: a short program over modules such as Bing search, an image captioner and a Python generator. With GPT-4 it beat GPT-4 CoT by only 2.55 points on ScienceQA (86.54%). The ChatGPT planner mostly copied the tool habits of its in-context examples: it called knowledge retrieval on 72% of ScienceQA questions and Bing search on 3%. ActionEngine ([arXiv:2602.20502](https://arxiv.org/abs/2602.20502) (Zhong et al., 2026-02, preprint)) adds what Chameleon lacked, a model of the environment. A crawler explores a web app offline and records a state machine: its pages, the operations on each and the transitions between them. At run time one LLM call writes a program against that map, which then runs without further model calls. On 655 WebArena tasks, with Claude Opus 4.6 behind every system, it **succeeded on 91.2% against 82.7% for Claude Code driving Playwright MCP step by step**. It used 1.5–3.5 LLM calls per task instead of 7–16, and $0.05 per task instead of $0.40. There are three caveats. The map was refined in a warm-up pass over every WebArena task template, and with the crawler's map alone it scored 73.1%. Failed tasks were re-graded by hand for all systems. And crawling cost $12–37 per site. Search-dependent tasks still failed, because the program must choose its search terms before seeing any results. That failure is the case for ReAct: when the next step depends on an observation, keep the loop.

There is evidence that the interpreter does work that chain-of-thought (CoT) can't. The earliest large demonstration predates the CoT critiques. Drori et al. ([arXiv:2112.15594](https://arxiv.org/abs/2112.15594), PNAS 2022) had Codex write and run programs for 175 randomly sampled questions from seven MIT and Columbia math courses. Zero-shot, its programs were correct on 71%, against 18% for GPT-3 (text-davinci-002) answering in prose. Few-shot examples raised that to 81%. But the few-shot loop kept adding examples until the program's output matched the known answer, and even the zero-shot figure let the authors try prompt prefixes such as "using sympy". So read the gap as large, not the 81% as a benchmark score. Code as Policies ([arXiv:2209.07753](https://arxiv.org/abs/2209.07753) (Liang et al., ICRA 2023)) ran the same comparison on a robot's spatial questions, such as "find the block closest to the blue bowl" given a list of object positions. On 51 such questions Codex (code-davinci-002) answered 35% correctly in plain prose and 58% with CoT. When it wrote Python instead, often calling NumPy, it got 98% right. The CoT failures were in precise, multi-step arithmetic. The same paper had Codex write robot policies as code that calls perception and control APIs. On a simulated tabletop, given instructions and object attributes it had never seen, the code solved 80% of long-horizon tasks. An LLM planner that picked from fixed pick-and-place steps solved 64%, and CLIPort, trained on 30k demonstrations, solved none. The code could only be as good as those APIs, and it could not tell in advance whether an instruction was feasible. Sprague et al. (2024) found that up to 95% of CoT's gain on MMLU comes from questions whose question or output contains "=", meaning symbolic or math problems. For other questions, nothing predicted when CoT would help. They also found that CoT is good at producing a plan but weaker at executing it, so the gain is larger when the plan goes to a Python interpreter. Wong et al. ([arXiv:2505.10543](https://arxiv.org/abs/2505.10543), FLLM 2025) saw the same gap in an environment. Mistral-NeMo-12B could recite the seven-move solution to Tower of Hanoi. Playing the 3-disk game move by move in SmartPlay, it never finished, made an invalid move 79% of the time and did worse than a random policy. Listing the valid actions each turn cut invalid moves to 56%. Mirzadeh et al.'s GSM-Symbolic (2024) rewrites GSM8K problems as templates. Accuracy drops when only the numbers change, falls sharply as problems get more complex, and is thrown off by irrelevant clauses, which the model turns into operations (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 11). For arithmetic and symbolic steps, have the model write the expression and let code evaluate it.

Coconut ([arXiv:2412.06769](https://arxiv.org/abs/2412.06769) (Hao et al., 2024-12)) goes the other way: it makes the reasoning invisible instead of executable. It feeds the last hidden state back in as the next input embedding instead of decoding a token, and it uses a curriculum that swaps written CoT steps for these continuous thoughts. On GSM8k with GPT-2 it scored 34.1% using 8.2 generated tokens, against 42.9% and 25 tokens for written CoT and 16.5% for no CoT. Without the curriculum it fell to 14.4%. On ProsQA, a graph-search task, it beat written CoT, 97.0% to 77.5%. On Llama 3-8B the gain over no CoT shrank to 42.2% → 43.6%. For an agent builder, the price is the trace: no tool can check a step it can't read, which is exactly what the interpreter route gives you.

Hybrid Reasoning Agents ([arXiv:2610.18861](https://arxiv.org/abs/2610.18861) (Zou et al., 2026-10, preprint)) keep the latent route but switch back to text for every tool call. A small residual adapter, about 10M parameters at 4B, maps the last hidden state back into the input embedding space. The model enters latent mode when it emits a `<latent>` token and leaves it to write text, tool calls and the answer. Qwen3-8B-Base trained this way with SFT and then RL scored **43.7 on GAIA, against 38.8 for the same base trained with ARPO**, a text-only tool-use RL method. Coconut, with no path to tools, scored 3.9. HybridAgent also wrote 43–49% fewer text tokens than a matched text agent. The audit cost is smaller than Coconut's. Each latent step can be read back as its nearest token ("pseudo-text"). A GPT-4o-mini monitor that saw only the visible text and tool calls predicted whether a MATH500 answer was right at least as well as for the text agent (AUROC 0.84 against 0.77 at 8B). Two caveats. Replacing every latent step with its nearest token embedding cost only 2 points on MATH500 (84.6 to 82.6 at 8B), so these "latent" thoughts sit close to ordinary tokens. And the audit was measured on math alone.

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
| Write the docstring as the tool's contract | LangChain's `@tool` builds the schema from the signature and docstring, and raises an error if the docstring is missing. A vague docstring makes invalid calls more likely (*AI Agents: The Definitive Guide*, ch. 1). |
| Validate arguments before the tool runs | A Pydantic `args_schema` with `file_type: Literal["pdf", "txt"]` rejects bad calls at the boundary (*Prompt Engineering for Generative AI*, ch. 6) |
| Use the return string to steer the next turn | A tool can return instructions as well as data: "Interview saved! ... You must tell the user that the interview is saved" (*Prompt Engineering for Generative AI*, ch. 6). The same channel carries prompt injection, so only your own tools should do this. |
| Return tool exceptions as messages | LangGraph's `ToolNode` turns an exception into a `ToolMessage` carrying the error, so the model decides whether to retry (*Learning LangChain*, ch. 6) |

Oshin and Campos add two structural fixes for when the model's choice of tool is the problem (*Learning LangChain*, ch. 6).

**Always call a tool first.** If every query should start with a search, don't spend an LLM call deciding that. Make the entry node build the tool call itself:

```python
# illustrative: needs LangChain, a model API key, and `State` and the tool retriever from *Learning LangChain*
def first_model(state: State) -> State:
    query = state["messages"][-1].content
    call = ToolCall(name="duckduckgo_search", args={"query": query}, id=uuid4().hex)
    return {"messages": AIMessage(content="", tool_calls=[call])}

builder.add_edge(START, "first_model")
builder.add_edge("first_model", "tools")   # then the usual model <-> tools loop
```

This saves one model call of latency and stops the model from deciding it doesn't need to search. It makes the agent worse if the rule isn't truly universal.

**Preselect tools by retrieval.** Above roughly 10 tools, the model gets worse at picking the right one. Embed each tool's description in a vector store. Add a `select_tools` node that retrieves the relevant names for the query, and bind only those (`model.bind_tools(selected)`) before the loop starts. This also shortens the prompt. The retrieval step adds latency, so add it only once accuracy measurably drops as tools are added.

![Agent graph with a select_tools node: start, select_tools, then a model and tools loop, then end](../sources/images/learning-langchain-fig6-3.png)
*Image Source: Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025), Fig. 6-3*

A caution from the same chapter: its calculator tool calls `ast.literal_eval`, which rejects any arithmetic expression, so `"1933-1872"` raises an error. And when the model does the subtraction itself, it says Coolidge died at 61; the search result it had already retrieved says 60 (born July 1872, died January 1933). A correct tool beats model arithmetic, but only if the tool is actually correct. Test each tool on its own before blaming the loop.

When the catalogue is too large to list, the field tried two fixes in 2023: fine-tune on API documentation, and retrieve the few relevant tools per request. Gorilla ([arXiv:2305.15334](https://arxiv.org/abs/2305.15334), Patil et al., 2023-05) fine-tuned LLaMA-7B on 1,645 TorchHub, TensorHub and HuggingFace calls. With no retriever it reached **71.7% AST accuracy on HuggingFace calls, against 19.8% for zero-shot GPT-4**. GPT-4's errors were mostly invented models and repos: 37% of its HuggingFace calls named an API that doesn't exist. Retrieval cut both ways. With the oracle document in the prompt, GPT-3.5 reached 89.7%. With BM25, every model fell below 20% on HuggingFace, and Gorilla dropped from 71.7% to 17.0%. A weak retriever is worse than none. ToolLLM ([arXiv:2307.16789](https://arxiv.org/abs/2307.16789), Qin et al., 2023-07) scaled to 16,464 RapidAPI endpoints with ChatGPT-generated instructions and solution paths. Swapping the ReAct loop for a depth-first search over call trees, which lets the model back up after a failed call, raised **ChatGPT's pass rate from 40.2% to 64.8%**. That beat GPT-4 with ReAct (57.2%). The fine-tuned 7B ToolLLaMA reached 66.7% with the same search, while Vicuna and Alpaca passed nothing. The pass rates are judged by ChatGPT, which agreed with human annotators 87.1% of the time, so read them as relative.

ToolGen ([arXiv:2410.03439](https://arxiv.org/abs/2410.03439) (Wang et al., ICLR 2025)) tries a third fix: make each tool a token, an idea from ToolkenGPT (Hao et al., NeurIPS 2023). It adds one vocabulary token for each of 47,000 RapidAPI tools and fine-tunes Llama-3-8B in three stages: memorize each tool's documentation, map queries to tool tokens, then act as an agent. As a retriever over all domains it reached **NDCG@1 of 79.0 on ToolBench's I3 (multi-tool) split, against 52.0 for a contrastively trained retriever**. With constrained decoding it cannot name a tool that doesn't exist, whereas ToolLlama named a nonexistent tool over 50% of the time when no tools were listed in its prompt. End to end the gain was small: a solvable pass rate of 53.3 against 51.6 for ToolLlama with a retriever, judged on StableToolBench. And a tool added after training stays invisible until the model is retrained, which the authors concede. So tool tokens suit a fixed catalogue, and retrieval still wins when tools change.

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

## Pitfalls

- **Vague tool descriptions.** The description is the model's only documentation. Say when to use the tool and what it returns, and include an example ID.
- **Raising on bad arguments.** A stack trace ends the run or teaches the model nothing. Return an error it can act on, naming the valid values.
- **One result message per tool call.** It works until the model makes parallel calls. Collect the results of a turn into one message.
- **Letting the model write its own observation.** In text-parsed ReAct, without a stop sequence, it will. Use native tool calls.
- **Loading every tool on every call.** Selection accuracy and cost both suffer as the list grows. Retrieve the few relevant tools per query.
- **Using more reasoning when a fact is missing.** A longer chain gives a more convincing wrong answer. Add a tool or data.
- **Reading CoT steps as an audit trail.** They can be written after the fact. Verify the result independently.
- **Treating tool output as trusted.** A web page or an email is attacker-writable data. Separate it from instructions, as in the [six defenses](#prompt-injection-six-defenses), and check parameters at the [execution gate](07-guardrails-and-autonomy.md#permissions-and-people).
- **Running generated code outside a sandbox.** Filesystem and network limits belong to the executor, not the prompt.

---

## Try it

1. In the stub loop, add a `place_order` tool and script a turn that calls `get_stock` for two items in parallel. How many entries go in the user message that follows, and what links each to its call?
2. Change the error message in `execute_tool` to just `"Error"`. In a real run, what would the model likely do next, and what would it cost?
3. Extend `parse` so that the `invented` reply is rejected. What is the simplest rule that does it, and which API feature makes the rule unnecessary?
4. The agent keeps saying itemB's delivery time is 2 weeks after the supplier changed it to 4. Would "think step by step" help? What would?

<details>
<summary>Answers</summary>

1. Two `tool_result` entries in one user message, each with the `tool_use_id` of its call.
2. It has nothing to act on, so it would probably retry the same ID or guess. Each retry re-sends the whole conversation, so a vague error costs tokens and may use up the step cap.
3. Reject any reply that contains `Observation:`, since only your code may write one. A stop sequence prevents the text from being generated, and native tool calls remove the need to parse at all.
4. No. This is a knowledge gap, and reasoning over a stale figure gives a tidy wrong answer. Read the delivery time from a tool on each run instead of holding it in the prompt or in memory.

</details>

---

## Interview checklist

| Question | Short answer |
|---|---|
| Who executes a tool call? | The client. The model only emits name and arguments |
| Does ReAct always beat CoT? | No. Observations help when the task needs facts the model lacks. On HotpotQA the original ReAct scored below CoT (27.4 against 29.4 EM with PaLM-540B), and the best result combined the two. Decide per task, or per step, when to call out |
| Why put a caller and an executor in different agents? | Approval, sandboxing and auditing sit between them |
| When would you choose code execution over tools? | Open-ended computation or a DSL; when many calls would chain |
| What does MCP add over function calling? | A protocol: tools live in a separate server any client can use |
| Does MCP let the model use context without a tool round trip? | No. MCP tools are still `tools/call` round trips; resources and prompts are separate primitives the client chooses to load |
| You have 40 tools and selection accuracy drops. What do you do? | Retrieve the few relevant tools per query and bind only those; measure that the extra latency pays off |
| Why does CoT not fix a knowledge gap? | Reasoning cannot supply a missing fact: the steps stay plausible and the answer stays wrong. Give the agent a tool or the data |
| Why group tool results in one message? | A single turn can carry several parallel calls, and each result must answer its `tool_use_id`. Results for one turn belong together |
| Why return errors as tool results? | So the model can correct itself, which it can do only if the error says what was wrong and what is valid |

---

## Next

→ [03 — memory as an operating system](03-memory-as-an-operating-system.md): what the loop remembers between turns, and how the agent edits it with the same tool calls.
