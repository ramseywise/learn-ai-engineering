# Pillar 9 — System Design (putting the pieces together)

The integration pillar: given a vague problem, design the whole system — components,
data flow, trade-offs, failure modes, measurement. It has no new domain content of its
own; it's the *method* for deploying pillars 3–8 under time pressure, and the
highest-weight technical round in AIE/MLE interviews.

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
[system-design-round](../../rounds/system-design-round.md) (logistics + curveballs),
[case-study](../../rounds/case-study.md) (the business-flavored variant).
