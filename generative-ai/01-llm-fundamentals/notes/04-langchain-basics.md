---
origin: book-condensed
sources:
  - "Oshin & Campos, Learning LangChain (O'Reilly, 2025), ch. 1, 8, 11"
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 4"
  - https://python.langchain.com/docs/concepts/
confidence: medium
cleaned: 2026-10-31
---

# 4 — LangChain Basics

> LangChain wraps models, prompts and parsers in one interface (the Runnable) so they can be swapped and composed. Learn the five building blocks and the pipe; LangGraph and RAG build on exactly these.

---

## Why a framework at all

The [TypeScript examples](06-calling-models-from-code.md) show that calling a model needs no framework. LangChain earns its place when you want:

| Need | LangChain answer |
|---|---|
| Swap providers without rewriting code | One chat-model interface over Anthropic, OpenAI, Google, local models |
| Reusable prompts with variables | Prompt templates |
| Parsed, validated output | Structured output and output parsers |
| Compose steps and get streaming, batching and async for free | The Runnable interface and LCEL |
| Retrieval plumbing | Document loaders, splitters, embeddings, vector stores, retrievers ([02-rag-retrieval](../../02-rag-retrieval/README.md)) |

*Learning LangChain* (ch. 1) frames the value as prebuilt common patterns plus interchangeable building blocks. The cost is an extra abstraction layer, frequent API churn and harder debugging. The versions in both books are already dated; check the current docs before copying code. Both books also show every example in JavaScript; this note uses Python.

---

## Building block 1: chat models and messages

A chat model takes a list of messages and returns a message.

| Message | Role | Holds |
|---|---|---|
| `SystemMessage` | system | Instructions the model should follow for the whole conversation |
| `HumanMessage` | user | The user's input |
| `AIMessage` | assistant | Model output, including any tool calls |
| `ToolMessage` | tool | The result of a tool call, linked by id |

```python
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

model = init_chat_model(MODEL_ID, model_provider="anthropic")   # pick a current id from the provider's docs
reply = model.invoke([
    SystemMessage("Answer in one word, then three exclamation marks."),
    HumanMessage("What is the capital of France?"),
])
reply.content   # 'Paris!!!'
```

---

## Building block 2: prompt templates

Templates separate the fixed instruction from the variables, which is how you apply [note 03's](03-prompting-fundamentals.md) principles once and reuse them.

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the context. If it is not there, say \"I don't know\"."),
    ("human", "Context: {context}\n\nQuestion: {question}"),
])
prompt.invoke({"context": "...", "question": "Which providers offer LLMs?"})   # -> a list of messages
```

Templates validate that all variables are supplied, compose with each other, and can be saved to and loaded from YAML or JSON (O'Reilly ch. 4). `FewShotChatMessagePromptTemplate` adds examples, with selectors that pick a fixed number of examples or as many as fit a length budget.

---

## Building block 3: structured output and parsers

Two ways to get machine-readable output:

**`with_structured_output`** (preferred). Pass a Pydantic model or JSON Schema. LangChain converts it to the provider's tool-calling or JSON mode and validates the result.

```python
from pydantic import BaseModel

class AnswerWithJustification(BaseModel):
    answer: str
    justification: str

structured = model.with_structured_output(AnswerWithJustification)
structured.invoke("What weighs more, a pound of bricks or a pound of feathers?")
# AnswerWithJustification(answer='They weigh the same', justification='...')
```

**Output parsers** for formats a provider cannot enforce. A parser does two jobs: it injects format instructions into the prompt (`parser.get_format_instructions()`) and it parses the text that comes back. O'Reilly ch. 4 tours the set: list, datetime, enum, Pydantic/JSON, XML, and the **auto-fixing** and **retry** parsers that send a malformed output back to a model for repair. That is the "specify format, retry on failure" loop from [note 03](03-prompting-fundamentals.md), packaged.

---

## Building block 4: the Runnable interface

Models, prompts, parsers, retrievers and chains all implement the same methods:

| Method | Does |
|---|---|
| `invoke(input)` | One input → one output |
| `batch([inputs])` | Many inputs, run in parallel |
| `stream(input)` | Yields output chunks as they are produced |
| `ainvoke`, `abatch`, `astream` | Async versions |

Because everything is a Runnable, anything can be dropped into a chain, and the chain gets all six methods for free.

---

## Building block 5: composition

*Learning LangChain* ch. 1 contrasts two styles.

**Declarative: LCEL.** The `|` operator pipes one Runnable's output into the next.

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | model | StrOutputParser()
chain.invoke({"context": "...", "question": "..."})
for chunk in chain.stream({"context": "...", "question": "..."}):
    print(chunk, end="")
```

**Imperative: plain functions** wrapped with `@chain`, for logic LCEL expresses awkwardly (branches, loops, early exits).

```python
from langchain_core.runnables import chain

@chain
def answer(values):
    messages = prompt.invoke(values)
    return model.invoke(messages)
```

| | Imperative (`@chain`) | Declarative (LCEL) |
|---|---|---|
| Parallel execution | You write threads or `asyncio.gather` | Automatic |
| Streaming | You `yield` | Automatic |
| Async | You write `async def` | Automatic |
| Readability for branching logic | Better | Worse |

When the flow needs loops, persistent state or human approval, move up to LangGraph ([04-agentic-frameworks](../../04-agentic-frameworks/README.md)).

---

## Patterns from the books worth knowing

- **Sequential chains** (O'Reilly ch. 4): a story generator that produces characters, then plot, then scenes, each step a chain fed by the last. "Divide labor" as code.
- **Document chains** for text longer than the context window:

  | Strategy | How | Trade-off |
  |---|---|---|
  | Stuff | Put all documents in one prompt | Simplest; fails past the context limit |
  | Refine | Answer from doc 1, then refine with each next doc | Sequential, slow; order matters |
  | Map-reduce | Summarize each doc in parallel, then combine | Parallel; loses cross-document detail |
  | Map-rerank | Answer from each doc with a confidence score, keep the best | Good for lookup; bad for synthesis |

- **Function calling with Pydantic tools**: define tools as Pydantic classes, `bind_tools` them to the model, parse the calls with a tools parser. Covered in depth in [ai-engineering/01-prompt-engineering note 05](../../../ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling.md).
- **Patterns to make the most of LLMs** (*Learning LangChain* ch. 8): the agency–reliability trade-off. The more freedom an architecture has, the more it needs structured output, streamed intermediate output, human-in-the-loop checkpoints and a policy for "double texting" (a user sending a new message while the last one is still running).
- **Building with LLMs** (ch. 11) closes the book with three product shapes: interactive chatbots, collaborative editing (shared state, versioning, undo), and ambient agents that run in the background with long-term memory and reflection.

---

## Where the rest of *Learning LangChain* lives

| Chapters | Topic | Home |
|---|---|---|
| 2–3 | RAG: indexing and retrieval | [02-rag-retrieval](../../02-rag-retrieval/README.md) |
| 4–7 | LangGraph memory, cognitive architectures, agents | [04-agentic-frameworks](../../04-agentic-frameworks/README.md), [03-agentic-foundations](../../03-agentic-foundations/README.md) |
| 9–10 | Deployment, testing, evaluation, monitoring | [06-observability](../../06-observability/README.md), [ai-engineering/06-eval](../../../ai-engineering/06-eval/README.md) |

---

**Next:** [05 — Build a tiny GPT](05-build-a-tiny-gpt.md) goes below the API and builds the model itself.
