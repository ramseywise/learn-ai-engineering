---
origin: notion-export
confidence: medium
sources:
  - https://developers.openai.com/api/docs/guides/compaction
cleaned: 2026-07-17
---

**Context Augmentation in RAG**

Memory management 

### context layers:

*(missing diagram — not exported from Notion)*

manage information according to its **usage frequency, stability, and enforcement requirements**. 

the system should keep the active context small and selectively retrieve or inject information only when it becomes relevant.

**1. Persistent Instruction Layer**

This layer contains information that must remain valid in every session, such as: Agent identity and role, Project-wide conventions, Architectural invariants, Critical safety constraints, Explicitly prohibited actions, Rules that should apply to nearly every task

The content in this layer should be: Short, Explicit, Stable, Operational, Easy for the model to follow

In Claude Code, this role is typically handled by `CLAUDE.md`.

**2. On-Demand Knowledge Layer**

This layer contains reusable procedures and domain-specific knowledge that are useful only for certain tasks.

Typical examples include: Skills, Domain playbooks, Deployment procedures, Evaluation methodologies, Debugging checklists, API-specific instructions, Long reference documents

progressive-disclosure: Only a short name and description(what + when) should remain permanently visible. The full content should be loaded only when the task activates it.

**3. Runtime Injection Layer**

This layer contains dynamic information that may change between sessions, turns, users, or execution environments.

Examples include: Current date and time, User or tenant ID, Channel ID, Environment variables,  Permission state(for each skill it also can be a permanent thing within skill?), Current task status

This information should be assembled programmatically at runtime rather than stored permanently in the system prompt.

Runtime injection has two advantages:

- The information remains current.
- Irrelevant dynamic data does not consume context in every interaction.

The system should inject only the runtime state required for the current task or turn.

**4. Long-Term Memory Layer**

This layer stores knowledge learned across sessions, including: User preferences, Repeated corrections, Project-specific discoveries, Effective workflows, Previous decisions, Known failure patterns

Long-term memory should not be treated as a full transcript that is always inserted into the prompt. It should instead be organized as a compact index plus retrievable detail.

In Claude Code, auto memory uses a `MEMORY.md` index together with separate topic files. The first 200 lines or 25 KB of `MEMORY.md` are loaded at the start of a session, while detailed topic files are not loaded automatically. They are read only when needed.

Long-term memory should also be treated as editable and auditable. Incorrect, outdated, or contradictory memories must be removable rather than accumulating indefinitely.

**5. Deterministic System Layer**

Deterministic behavior should be implemented through code, hooks, permissions, schemas, validators, or tool constraints rather than context.

Examples include: Blocking dangerous commands, Enforcing allowed file paths, Validating structured outputs, Checking argument schemas

The model may ignore, misunderstand, or inconsistently follow a textual instruction. A code-level control is significantly more reliable.

# Context Compression and Compaction Strategies

**Compaction** is an orchestration process that transforms a large interaction history into a smaller continuation state.

Compaction: 

```markdown
Raw interaction history 
↓ 
Prune irrelevant content 
↓ 
Replace bulky tool outputs 
↓ 
Extract structured task state 
↓ 
Summarize older reasoning 
↓ 
Preserve recent messages verbatim 
↓ 
Produce compact continuation context
```

```markdown
### Compact Instructions: How to Retain Key Information

Retention Priority:

1. Architectural decisions: Do not summarize.

2. Modified files and critical changes.

3. Verification status: pass/fail.

4. Unresolved TODOs and rollback notes.

5. Tool output: Can be deleted; only retain pass/fail conclusions.
```

sliding windows, summarization, pruning, state extraction, and tool-result replacement can all be components of compaction.

## Salvaged from table_of_contents.md (Notion): prompt caching + compaction notes

### *Prompt caching*

LLM inference pipelines typically use a prefill phase that processes the prompt and a decode phase that generates output tokens.

*(missing diagram — not exported from Notion)*

The intuition behind caching is that the prefill computation can be performed once, saved (e.g., cached), and then re-used if (part of) a future prompt is identical

Prompt caching works by prefix matching — so the order you put things in matters enormously — The best way to do this is static content first, dynamic content last. — to maximize how many sessions share cache hits.

*(missing diagram — not exported from Notion)*
 One early pattern we’ve seen is a loss of accuracy in the gap between single tool invocation and multi-tool orchestration. Skills can close that gap by making tool reasoning more procedural without bloating system prompts. 

 How OpenClaw recovers from long tasks? 

write the task progress to disk and restart to continue from the breakpoint. If the task is longer than half an hour, crash recovery is a must, not an option.



### context management:

Latency tip from OpenAI developershttps://developers.openai.com/api/docs/guides/compaction After appending output items to the previous input items, you can drop items that came before the most recent compaction item to keep requests smaller and reduce long-tail latency. The latest compaction item carries the necessary context to continue the conversation.

1. workflow VS agent 

*(missing diagram — not exported from Notion)*

*(missing diagram — not exported from Notion)*

1. 5 patterns in Agent system 
    
    *(missing diagram — not exported from Notion)*
    
    Agent sweet spot: 
    
    *(missing diagram — not exported from Notion)*
    

Context rot from the limitation of Transformer, how to deal with it: Context Management 
