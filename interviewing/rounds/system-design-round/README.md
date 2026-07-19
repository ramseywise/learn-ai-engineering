# System Design Round (ML/LLM/Agent)

## What's tested
The highest-weight technical round in 2026 AIE/MLE loops: structured ambiguity handling — clarify, requirements, design, shortcomings, iterate — with trade-off narration as the actual graded skill. Interviewers score the *process* (strategic questions, adapting to curveballs, growth mindset) as much as the design.

## Format & trends
45-60 min whiteboard/virtual-whiteboard. The prompt is deliberately vague ("design a support chatbot"). 2026 versions are LLM-flavored by default: RAG pipelines, agent systems, eval/monitoring, cost/latency budgets. Curveballs mid-round are deliberate adaptability tests; the best interviews meander through options before converging.

In 2026, the LLM is maybe 20% of a production agent system — interviewers want to see the full harness: orchestration, tool design, state management, observability, safety, eval. "What breaks?" matters more than "what's the architecture?"

## The method
The five-step process, trade-off narration formula, reference architecture, bottleneck tables, and measurement close live in the [study guide](study-guide.md). This file is overview and logistics.

## Prep checklist
- [ ] Rehearse the five-step process until the clarifying questions are automatic (the two openers: priorities question + data-sensitivity question)
- [ ] Draw the reference architecture from memory in under 3 minutes
- [ ] Dry-run the four classic prompts against a timer (8 min/step)
- [ ] Rehearse the three librarian drill systems as full spoken answers — designs you've actually built beat memorized generic ones
- [ ] Prepare the closing move: success metrics with numbers + a future-improvements list
- [ ] Practice the recovery move: interviewer challenges a trade-off -> adapt visibly, don't defend

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| High | High | Medium | High |

Highest-weight round for AIE/MLE. For FDE the case study and customer simulation outweigh it — but the same design method underpins the case. DS gets a lighter "design the analytics/ML pipeline" variant.

## Folder contents
- [study-guide.md](study-guide.md) — the method: process, trade-offs, reference architecture, bottlenecks, measurement
- [sources.md](sources.md) — curated references (internal guides + librarian wiki + external)
- [examples/](examples/) — worked system design walkthroughs by topic
- [questions.md](questions.md) — sample prompts with model answer structures
