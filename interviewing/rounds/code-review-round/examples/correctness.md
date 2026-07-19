# Correctness & Interfaces

## Example 1: Tool schema drift — agent can't call updated tool

**The diff**
```python
# tools/search_tool.py
- def search_documents(query: str) -> list[Document]:
-     """Search the document store."""
-     results = vector_store.similarity_search(query, k=5)
-     return results
+ def search_documents(query: str, filters: dict, top_k: int = 5) -> list[Document]:
+     """Search the document store with optional metadata filters."""
+     results = vector_store.similarity_search(query, k=top_k, filter=filters)
+     return results

# tools/tool_registry.py
  TOOLS = [
      {
          "name": "search_documents",
-         "description": "Search the document store by semantic similarity",
+         "description": "Search the document store by semantic similarity with filters",
          "parameters": {
              "type": "object",
              "properties": {
                  "query": {"type": "string", "description": "The search query"},
              },
              "required": ["query"],
          },
      },
  ]
```

**Surface read**: Added filter support to search. Description updated. Clean feature addition.

**Model review**

> **[Blocker]** `tool_registry.py` — The tool schema wasn't updated to include the new `filters` parameter, but `search_documents()` now requires it (no default value). When the agent calls this tool with just `{"query": "..."}`, it will get a `TypeError: missing required argument 'filters'`.
>
> Either add `filters` to the schema:
> ```python
> "filters": {"type": "object", "description": "Metadata filters (e.g. {'department': 'engineering'})", "default": {}}
> ```
> Or make `filters` optional in the function: `filters: dict | None = None`
>
> **[Warning]** — The `top_k` parameter exists in the function but not in the schema. The agent can't use it. If it's intentionally hidden, document why; if it should be exposed, add it to the schema with a sensible description.
>
> **[Info]** — Tool description says "with filters" but doesn't explain what filters are available or their format. For agent tool design (ACI), the description should include a usage example: `"Filter by metadata fields, e.g. {'department': 'engineering', 'year': 2026}"`.

**What this teaches**: Tool schema and implementation drifting apart is the agent-world equivalent of API contract drift. The model can only see the schema — if the schema is stale, the tool breaks silently or throws at runtime. See [agents guide §3](../../../guides/4-agents/interview-guide.md) on ACI and tool design.

---

## Example 2: Swallowed error in agent loop — silent failure on tool call

**The diff**
```python
# agents/research_agent.py
  async def run_step(self, state: AgentState) -> AgentState:
      tool_call = await self.llm.get_tool_call(state.messages)

      try:
          result = await self.execute_tool(tool_call)
-         state.messages.append({"role": "tool", "content": result})
      except Exception as e:
-         state.messages.append({"role": "tool", "content": f"Error: {e}"})
-         state.error_count += 1
-         if state.error_count >= 3:
-             raise AgentError("Too many tool failures")
+         result = "Tool execution completed."

+     state.messages.append({"role": "tool", "content": result})
      return state
```

**Surface read**: Simplified error handling. Fewer branches.

**Model review**

> **[Blocker]** `research_agent.py:8-9` — On any tool failure, the agent now receives `"Tool execution completed."` — a lie. The model will proceed as if the tool succeeded, building on nonexistent results. This creates compounding hallucination: the agent "saw" a result that never existed and reasons from it.
>
> **[Blocker]** `research_agent.py:10-12` — The error counter and circuit breaker were removed. Without them, a persistently failing tool (API down, bad credentials, rate-limited) causes an infinite loop — the agent keeps calling, keeps getting the fake success, keeps building on nothing. This is a denial-of-wallet risk.
>
> The error message to the model should be honest. The agent can recover from knowing a tool failed; it can't recover from false data:
> ```python
> except Exception as e:
>     result = f"Tool '{tool_call.name}' failed: {e}. Try a different approach."
>     state.error_count += 1
>     if state.error_count >= 3:
>         raise AgentError("Too many tool failures")
> ```

**What this teaches**: Agent loops need honest feedback signals. Swallowing errors in an agent context is worse than in traditional code — the model compounds the false signal across turns. The missing circuit breaker is a cost/reliability concern. See [agents guide §5](../../../guides/4-agents/interview-guide.md) on loop engineering; [security guide §4](../../../guides/7-security-safety/interview-guide.md) on denial-of-wallet.

---

## Example 3: Schema drift — callers not updated

**The diff**
```typescript
// api/users.ts
export interface UserResponse {
-   name: string;
+   firstName: string;
+   lastName: string;
    email: string;
    role: string;
}
```

**Surface read**: Interface updated. Types match internally.

**Model review**

> **[Blocker]** `users.ts:2-4` — `UserResponse` shape changed: `name` split into `firstName`/`lastName`. Every consumer accessing `.name` breaks. Questions: how many callers? Frontend renders? API consumers? Deprecation period needed?
>
> **[Info]** — If all callers are updated in the same PR, fine. But the diff only shows the provider side — want to see consumer updates too.

**What this teaches**: Interface changes that look self-consistent in isolation break callers you can't see in the diff. The instinct to ask "who consumes this?" is the signal.
