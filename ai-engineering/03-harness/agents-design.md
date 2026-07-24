---
origin: notion-export
confidence: medium
sources:
  - https://medium.com/data-science-collective/ai-agents-complete-course-f226aa4550a1
cleaned: 2026-07-17
---


## https://medium.com/data-science-collective/ai-agents-complete-course-f226aa4550a1

**Multi-agent System Design**

Patterns:

**Pattern 1: Sequential**

*(missing diagram — not exported from Notion)*

**Pattern 2: Parallel**

*(missing diagram — not exported from Notion)*

**Pattern 3: Single Manager Hierarchy**

*(missing diagram — not exported from Notion)*

and there is a deeper **Hierarchy**

*(missing diagram — not exported from Notion)*

**Pattern 4: All-to-All (Free-for-All Chat)**

This is rare in production because it’s hard to predict and control.

work for more brainstormy, creative, or low-stakes tasks.

*(missing diagram — not exported from Notion)*

**Best Practices**

*1. Define interfaces, not vibes.*

Each agent needs a clear schema for inputs and outputs: What fields? What types? What IDs or references get passed along?

Handoffs break more often than the models do.

*2. Scope tools per agent.*

Give each agent only the tools it actually needs. Least-privilege access.

*3. Log the trace.*

Keep per-step artifacts执行记录. What did each agent plan? What prompts did it use? What tool calls did it make? What results came back?

When something breaks this trace makes error analysis fast. You can see exactly where things went wrong.

*4. Evaluate components AND end-to-end*

two types of evals:

Component-level: Is the research relevant? Are the images high quality? Is the copy tone appropriate?

And end-to-end: Is the final brochure good? Does it meet the requirements?

If your end-to-end eval shows problems but your component evals all look fine, you know it’s a handoff or integration issue. If a specific component eval fails, you know which agent to improve.

### **Advanced Task Decomposition for Multi-Agent Systems**

**Pattern 1: Functional Decomposition**

split the tasks by technical domain or expertise — breaking tasks by what kind of work needs to be done.

*(missing diagram — not exported from Notion)*

**Pattern 2: Spatial Decomposition**

split by file or directory structure. — This is especially powerful when you’re working with large codebases with many files that could be processed independently.

They can work in parallel. But if your files have complex dependencies on each other, spatial decomposition breaks down.

**Pattern 3: Temporal Decomposition**

breaking tasks into sequential stages where later stages depend on earlier ones being complete.

**Pattern 4: Data-Driven Decomposition**

split by data partitions. This one’s less common but really powerful for certain use cases, especially tasks involving large datasets where you can partition the data and process chunks independently.



## Salvaged from table_of_contents.md (Notion): tool quality over quantity

One early pattern we’ve seen is a loss of accuracy in the gap between single tool invocation and multi-tool orchestration. Skills can close that gap by making tool reasoning more procedural without bloating system prompts. Tool Calling and Evals

What matters is tool quality, not tool quantity.

*(missing diagram — not exported from Notion)*

don’t put all the tool messages into context/ llm / agent, the message sent to llms can be: user, assistant, tool_result


## Salvaged from table_of_contents.md (Notion): protocol-driven multi-agent collaboration


### Protocol-Driven Multi-Agent Collaboration

*(missing diagram — `Screenshot 2026-07-12 at 18.30.18.png` not exported from Notion)*

**Why Collaboration Must Be Defined as a Protocol**

Use natural language inside a task, but use protocols to coordinate tasks.

If agents coordinate only through conversational instructions, the system quickly encounters problems such as:

- An agent forgets what it committed to do.
- Two agents believe they own the same task.
- An agent starts before its dependency is complete.
- A result is delivered but never acknowledged.
- A failed task is silently treated as completed.
- Two workers modify the same files.
- A retried request is executed twice.
- The orchestrator cannot determine the current global state.
- The system cannot recover reliably after a crash.

For reliable collaboration, the system must define:

1. What messages mean
2. Which state transitions are valid
3. Who owns each task
4. Which tasks depend on which others
5. What files or resources each agent may modify
6. How failures, retries, acknowledgements, and recovery work

**The Three Foundations**

1. Communication Protocol: The protocol defines how agents send requests, return results, report failures, and acknowledge state changes.

2. Task Graph: The task graph defines what work exists, who owns it, and which tasks depend on other tasks.

3. Isolation Boundary: The isolation boundary controls which files, branches, tools, or external resources each agent may modify.

*(missing diagram — `Screenshot 2026-07-12 at 18.31.54.png` not exported from Notion)*

Hallucinations amplify each other under multiple agents. — how to avoid: cross-validation

*(missing diagram — not exported from Notion)*

Give each subagent the minimum context, authority, and execution budget required to complete one clearly defined task.
