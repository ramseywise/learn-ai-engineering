# Pillar 9 — System Design (putting the pieces together)

The integration pillar: given a vague problem, design the whole system — components,
data flow, trade-offs, failure modes, measurement. Largely the *method* for deploying
pillars 3–8 under time pressure, plus the generic backend substrate the LLM-flavored
round assumes (scaling, storage, APIs). The highest-weight technical round in AIE/MLE
interviews.

## Detailed notes

| Note | What it carries |
|---|---|
| [01-distributed-systems.md](01-distributed-systems.md) | Scaling, load balancing, data modeling, SQL vs NoSQL, indexes, caching, replication, sharding |
| [02-api-design.md](02-api-design.md) | REST/GraphQL/gRPC, pagination, auth — the ~5-minute API section |
| [03-ml-system-design.md](03-ml-system-design.md) | Business problem → ML problem → data → approach; the ML-flavored variant |
| [04-decision-tree.md](04-decision-tree.md) | **The four spines** — pick one, walk it node by node under pressure |
| [05-ai-product-design.md](05-ai-product-design.md) | Mission/goals, segmentation, prioritization, AI risk framing |
| [06-component-cheatsheet.md](06-component-cheatsheet.md) | Component-by-component reference for the LLM request path |

## Learning path

1. **The method** — the [interview guide](interview-guide.md) here *is* the curriculum:
   the 5-step process, trade-off narration formula, reference architecture,
   bottleneck/failure tables. Source material:
   [case-interview.md](../../notes/case-interview.md) (System Design Interview Handbook
   section).
2. **Architecture pattern language** — *Generative AI Design Patterns* (all 10 chapters,
   `ai-engineering/readings/ai_engineering/ai design/`) + `agentic_architectural_patterns.pdf`
   (`readings/`): named patterns you can draw and defend.
3. **App-level architecture** — *AI Engineering* ch 10 (Architecture & User Feedback);
   *Building Applications with AI Agents* chs 5, 8 (orchestration, multi-agent).
4. **Study worked designs** — librarian's three interview-format writeups (shared
   code-index service · unified eval harness · serverless agent backends) — real systems
   written as interview answers; rehearse them aloud.
5. **Drill** — the four classic prompts in the interview guide §6, 8 minutes per step,
   whiteboard or paper. Design is a performance skill; reps matter more than reading.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| case-interview.md | note | [../../notes/case-interview.md](../../notes/case-interview.md) | the round's process + trade-off technique |
| *Generative AI Design Patterns* | pdf | `ai-engineering/readings/ai_engineering/ai design/` | the pattern vocabulary |
| agentic_architectural_patterns.pdf | pdf | `ai-engineering/readings/ai_engineering/` | agent architecture survey |
| *AI Engineering* ch 10 | pdf | `ai-engineering/readings/ai_engineering/ai engineer/` | full-app architecture + feedback loops |
| System Design — Shared Code-Index Service · Unified Eval Harness · Serverless Agent Backends | wiki | librarian | worked designs of real systems |
| Orchestration Architecture Decision · Runtime Topology pages | wiki | librarian | decision records to cite |
| evaluation-dimensions diagram | image | [../../images/case-interview-evaluation-dimensions.png](../../images/case-interview-evaluation-dimensions.png) | what's actually graded |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round/README.md) (logistics + curveballs),
[case-study](../../rounds/case-study/README.md) (the business-flavored variant).
