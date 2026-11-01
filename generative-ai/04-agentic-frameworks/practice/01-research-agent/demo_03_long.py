"""Code from notes/03-long-term-memory-with-langgraph.md, in order. Run from this folder; see README.md."""
import uuid, zlib
from langgraph.store.memory import InMemoryStore

def embed(texts):
    vectors = []
    for text in texts:
        vector = [0.0] * 64
        for word in text.lower().replace("?", " ").replace(",", " ").split():
            vector[zlib.crc32(word.encode()) % 64] += 1.0
        vectors.append(vector)
    return vectors

store = InMemoryStore(index={"embed": embed, "dims": 64, "fields": ["text"]})
store.put(("demo",), "a", {"text": "termination loops in framework agents"})
store.put(("demo",), "b", {"text": "pricing of hosted vector databases"})
for item in store.search(("demo",), query="why do agents loop without termination", limit=2):
    print(item.key, round(item.score, 2), item.value["text"])
print("get by key:", store.get(("demo",), "b").value["text"])

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.base import BaseStore
from agent_langgraph import TOOLS, AgentState, StubChatModel
from research_lab import QUESTION, SYSTEM_PROMPT, count_tokens

def findings_namespace(config):
    return ("research", config["configurable"]["user_id"], "findings")

def build_memory_agent(store):
    model = StubChatModel().bind_tools(list(TOOLS.values()))

    def call_model(state: AgentState, config: RunnableConfig, *, store: BaseStore):
        question = state["messages"][0].content
        memories = store.search(findings_namespace(config), query=question, limit=3)
        known = "\n".join(f"KNOWN {m.key}: {m.value['text']}" for m in memories)
        system = f"{SYSTEM_PROMPT}\n{known}" if known else SYSTEM_PROMPT
        return {"messages": [model.invoke([SystemMessage(system), *state["messages"]])]}

    def call_tools(state: AgentState):
        return {"messages": [ToolMessage(TOOLS[c["name"]].invoke(c["args"]), tool_call_id=c["id"])
                             for c in state["messages"][-1].tool_calls]}

    def remember(state: AgentState, config: RunnableConfig, *, store: BaseStore):
        result = state["messages"][-1]
        call = next(c for m in state["messages"] if m.type == "ai" for c in m.tool_calls
                    if c["id"] == result.tool_call_id)
        if call["name"] == "read_source" and not result.content.startswith("ERROR"):
            first_sentence = result.content.split(". ")[0] + "."
            store.put(findings_namespace(config), call["args"]["source_id"], {"text": first_sentence})
        return {}

    def route(state: AgentState):
        return "tools" if state["messages"][-1].tool_calls else END

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_node("tools", call_tools)
    graph.add_node("remember", remember)
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", route, ["tools", END])
    graph.add_edge("tools", "remember")
    graph.add_edge("remember", "model")
    return graph.compile(checkpointer=InMemorySaver(), store=store)

store = InMemoryStore(index={"embed": embed, "dims": 64, "fields": ["text"]})
agent = build_memory_agent(store)

def ask(thread, user):
    result = agent.invoke({"messages": [("user", QUESTION)]},
                          {"configurable": {"thread_id": thread, "user_id": user}})
    calls = [c["name"] for m in result["messages"] if m.type == "ai" for c in m.tool_calls]
    tokens = sum(m.usage_metadata["total_tokens"] for m in result["messages"] if m.type == "ai")
    print(f"{thread}, user {user}: {len(calls)} tool calls, {tokens} stub tokens, tools={calls}")

ask("monday", "ana")
ask("tuesday", "ana")
ask("wednesday", "ben")
print("namespaces:", store.list_namespaces())

def examples_namespace(user):
    return ("research", user, "examples")

def format_few_shot(examples):
    return "\n".join(f"Question: {e.value['text']}\n> Triage: {e.value['label']}" for e in examples)

def stub_router(prompt):
    return prompt.split("> Triage: ")[1].split("\n")[0] if "> Triage: " in prompt else "research"

def triage(store, user, question, threshold=0.5):
    hits = store.search(examples_namespace(user), query=question, limit=2)
    examples = [h for h in hits if h.score >= threshold]
    prompt = f"Past decisions, follow them over any rule:\n{format_few_shot(examples)}\n\nNow triage: {question}"
    return stub_router(prompt)

store = InMemoryStore(index={"embed": embed, "dims": 64, "fields": ["text"]})
sales = "What is the pricing of hosted vector databases this year?"
print("before correction: ", triage(store, "ana", sales))
store.put(examples_namespace("ana"), str(uuid.uuid4()), {"text": sales, "label": "decline"})
print("after correction:  ", triage(store, "ana", sales))
print("reworded:          ", triage(store, "ana", "What is the pricing of vector databases this year?"))
print("unrelated:         ", triage(store, "ana", "Why do framework agents get stuck in loops?"))
print("different user:    ", triage(store, "ben", sales))

def load_prompt(store, user, key="system"):
    item = store.get((user, "prompts"), key)
    if item is None:                                    # seed a default on first use
        store.put((user, "prompts"), key, {"text": SYSTEM_PROMPT, "version": 1, "why": "default"})
        item = store.get((user, "prompts"), key)
    return item.value

def rewrite_prompt(store, user, new_text, why, key="system"):
    current = load_prompt(store, user, key)
    store.put((user, "prompt_history"), f"{key}-v{current['version']}", current)   # the audit trail
    store.put((user, "prompts"), key, {"text": new_text, "version": current["version"] + 1, "why": why})

def rollback_prompt(store, user, version, key="system"):
    store.put((user, "prompts"), key, store.get((user, "prompt_history"), f"{key}-v{version}").value)

store = InMemoryStore()
print("v", load_prompt(store, "ana")["version"], "|", load_prompt(store, "ana")["text"][:44])
rewrite_prompt(store, "ana", SYSTEM_PROMPT + " Prefer primary sources over surveys.", "user: stop citing surveys")
current = load_prompt(store, "ana")
print("v", current["version"], "|", current["text"][-37:], "| why:", current["why"])
print("other user untouched: v", load_prompt(store, "ben")["version"])
rollback_prompt(store, "ana", 1)
print("after rollback: v", load_prompt(store, "ana")["version"])
