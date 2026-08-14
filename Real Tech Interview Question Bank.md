# Real Tech Interview Question Bank

This bank contains 23 questions organized into 9 themes. Each question is a collapsible entry — click to expand the researched answer and its sources. Answers were drafted by parallel research agents that searched the web (Anthropic engineering blog, LangChain/LangSmith, Langfuse, LiteLLM, Braintrust, academic RAG-eval papers, etc.) and this repo's own notes for citable material — verify against your own experience before using them verbatim in an interview.


---

## 1. Provider-Agnostic Model Configuration

<details>
<summary><b>Q: How would you redesign this model configuration so that it can work with any model provider?</b></summary>

The core move is separating the *stable contract* (what my code needs: prompt in, text/tool-calls out, usage stats, errors) from the *provider-specific translation layer*. Concretely:

1. **Define a canonical request/response schema** — a small set of normalized fields (messages, tools, max_tokens, temperature, stop sequences, response format) that every call site in the app uses, independent of any single SDK's shape.
2. **Use an adapter/factory per provider** that translates the canonical schema into that provider's actual API call, and translates the response back. This is the same "contract vs. implementation" separation used for tool design: the contract is versioned and provider-agnostic; adapters are swappable code.
3. **Route through a model registry keyed by a logical name** (e.g. `"fast-writer"`, `"strong-reasoner"`) rather than hardcoding `gpt-4o` or `claude-sonnet-4-5` at call sites, so swapping providers is a config change, not a code change. LangChain's `init_chat_model` and LiteLLM both implement this pattern at the library level — a single function signature that resolves to any of 100+ providers.
4. **Push provider quirks to the edges.** Auth, base URLs, and param name differences live only inside the adapter; everything upstream (retries, logging, evals) operates on the normalized types.
5. **Version the config separately from the code**, so a prompt/model swap doesn't require a deploy.

This mirrors the local repo's harness principle of keeping prompt-engineering artifacts (contracts) decoupled from execution logic (implementations) — the same reasoning applied to model config instead of tool schemas.

**Sources:**
- [LiteLLM — Compatibility & Extensibility](https://docs.litellm.ai/docs/guides/compatibility_extensibility) — unified I/O format across 100+ providers via one call interface.
- [LangChain — init_chat_model](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model) — provider-agnostic model initializer with standard kwargs (temperature, timeout, max_tokens).
- (this repo: `ai-engineering/03-harness/notes/03-tool-design.md`) — "separate the contract from the execution logic via a factory pattern," the same principle applied here to model config.

</details>

<details>
<summary><b>Q: How would you handle a provider-specific parameter that would cause another provider's API request to fail?</b></summary>

Never let a provider-specific parameter reach a provider that doesn't support it — handle it at the adapter boundary, not by hoping providers silently ignore unknown fields (most don't; they 400).

Concrete patterns, in order of preference:

1. **Whitelist-per-provider translation.** Each adapter declares which canonical fields it accepts and maps or drops the rest. A real example: OpenAI's reasoning models (`o1`, `o3-mini`) reject `temperature` entirely — passing anything but the default `1` returns `400 Unsupported parameter: 'temperature'`. Anthropic's Claude accepts `temperature` but not OpenAI's `frequency_penalty`/`presence_penalty`. The adapter for each model family needs to know its own supported set.
2. **A `drop_params`-style escape hatch** for parameters that are convenience-only (not correctness-critical) — LiteLLM's `drop_params=True` strips unsupported OpenAI-shaped params instead of raising, which keeps calling code portable across providers without per-call conditionals. Use this for cosmetic params; never for things like `max_tokens` where dropping it silently changes behavior.
3. **Capability flags in the model registry** (e.g. `supports_temperature: bool`, `supports_system_prompt: bool`, `supports_streaming: bool`) so the calling code can branch deliberately rather than relying on runtime exceptions.
4. **Fail loud in dev, degrade gracefully in prod** — validate the outgoing payload against the target provider's schema before the call in tests/CI; in production, prefer dropping/clamping over crashing the whole agent turn, but log every drop so silent behavior drift is visible.

**Sources:**
- [LiteLLM — Drop Unsupported Params](https://docs.litellm.ai/docs/completion/drop_params) — raises by default on unsupported params; `drop_params=True` strips them instead.
- [OpenAI Community — o3-mini "Unsupported parameter: temperature"](https://community.openai.com/t/o3-mini-unsupported-parameter-temperature/1140846) — concrete failure mode this design must guard against.
- [LiteLLM — Provider-specific Params](https://docs.litellm.ai/docs/completion/provider_specific_params) — pattern for passing through non-standard kwargs per provider.

</details>

---

## 2. Agent Reliability & Determinism

<details>
<summary><b>Q: [Main] What are the ways to make a nondeterministic agent system more reliable?</b></summary>

Accept that the model core stays probabilistic — even `temperature=0` doesn't guarantee bit-identical output — and build **deterministic scaffolding around a nondeterministic core** instead of chasing determinism inside the model call:

- **Constrain the output surface.** Structured outputs/schema-validated JSON, enums over free text, and tool-call parameters validated before execution turn "did it phrase this right" into "did it satisfy the schema," which is checkable deterministically.
- **Use deterministic tools for precision work**, and leave only judgment/planning to the LLM. Math, lookups, and state mutations should be code, not model-generated text.
- **Verification loops / reflection**, ideally with a verifier that is a *different, stronger* model than the executor (asymmetric QA) so the system isn't grading its own homework.
- **Retry with bounded budgets and error-as-context** — feed the failure back into the next attempt rather than blindly re-sampling; cap retries (a two-retry rule is common) since more than that usually signals a spec or context problem, not bad luck.
- **State persistence / checkpointing** so a mid-workflow failure resumes from the last good step instead of restarting and re-rolling the dice on every prior step.
- **Cross-provider/model fallback** behind a uniform interface, since provider outages are outside your control.
- **Human-in-the-loop gates** on high-stakes or ambiguous decisions (an "Approve" gate on the plan is cheap and catches errors before expensive execution).
- **Continuous evals in CI + on live traffic**, measured with `pass@k` (did it succeed at least once) and `pass^k` (did it succeed consistently) rather than a single pass/fail run, since agent behavior varies run to run.
- **Tight tool design** (clear, non-overlapping tool descriptions) — a large share of "nondeterministic" failures are actually deterministic tool-selection ambiguity that better descriptions fix.

**Sources:**
- [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — ground truth from the environment at each step, simple composable patterns over complex frameworks.
- [Charles Sieg — Achieving Determinism with LLM Agents: An Architecture Guide](https://charlessieg.com/articles/achieving-determinism-with-llm-agents-architecture-guide.html) — "deterministic scaffolding around a non-deterministic core"; temperature=0 does not guarantee determinism.
- (this repo: `ai-engineering/03-harness/reliable-agents.md`) — Bayer/PRINCE case study: retries at LLM-call and node level, cross-provider fallback, resume-from-failed-node via checkpointing, asymmetric QA, error fed back as context.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — pass@k vs. pass^k for measuring non-deterministic agent reliability across repeated trials.

</details>

<details>
<summary><b>Q: [Follow-up] Focusing on this system with three tools, how would you check whether it works correctly after the PR is merged?</b></summary>

For a small, fixed toolset, correctness checking has to cover both *outcome* (did the task get done) and *trajectory* (did it use the right tools, in a reasonable order, without unsafe or wasteful calls) — grading only the final answer can hide an agent that got lucky through the wrong path, or missed an efficient path.

Practical layers, in order I'd stand them up:

1. **Unit tests per tool** — deterministic checks that each of the three tools, called directly (bypassing the LLM), does the right thing given valid/invalid/edge-case inputs. This isolates "is the tool broken" from "did the agent pick the right tool."
2. **A small regression eval set (20–50 real or realistic tasks)** run through the full agent harness, each with a defined task, multiple trials (since output varies run to run), and graders: code-based checks where there's a clear right answer (correct tool called, correct args, correct final state), LLM-as-judge for open-ended quality, spot human review to calibrate the judge.
3. **Trajectory assertions**, not just outcome assertions — e.g. "tool X must never be called before tool Y," or "at most N tool calls for task type Z" — since the same wrong-tool selection bug can produce a right answer by luck one run and a wrong one the next.
4. **Run this suite in CI on the PR** (gated merge, e.g. via LangSmith's pytest/GitHub integration or an equivalent harness) with a regression threshold — fail the PR if pass rate on the *existing* task set drops meaningfully; a capability eval with a near-100% target becomes the regression suite once it's this small.
5. **Post-merge**, sample a slice of live traffic for a short window (first 24–48h) for manual/LLM-judge review to catch anything the offline set didn't cover, since three tools is small enough that new interaction patterns in production are the main residual risk.

**Sources:**
- [LangSmith — Trajectory Evals](https://docs.langchain.com/langsmith/trajectory-evals) — grading the sequence of tool calls/messages, not just final output.
- [Langfuse — AI Agent Evaluation: trajectory, tool calls, and task completion](https://langfuse.com/resources/engineering/ai-agent-evaluation) — outcome vs. trajectory as distinct, both-necessary evaluation axes.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — task/trial/grader structure, code vs. LLM vs. human graders, "run multiple trials because agent behavior is non-deterministic," full review within 48h after a change.

</details>

---

## 3. Testing Strategy & CI

<details>
<summary><b>Q: [Main] Do you have a rule of thumb for when unit tests should run? Should the tests run after every code change?</b></summary>

Yes — unit tests should run on every commit/PR, essentially continuously, because they're the cheap, fast layer of the pyramid and their entire value is fast feedback while the change is still fresh in the developer's head. The rule of thumb I use: **run tests at the same layer as the change, and run the fastest layer as often as physically possible.**

Practically, that means:
- **Unit tests**: on every save locally (watch mode) or at minimum every push/PR — they should run in seconds, so there's no excuse not to run them constantly.
- **Integration tests**: on every PR/merge to main, since they're heavier but still bounded.
- **End-to-end / expensive evals** (e.g. full agent trajectory runs against live models): on PR for the specific surface touched, or nightly/pre-release for the full suite — too slow and costly to run on every keystroke.

For an LLM-agent codebase specifically, this maps onto the eval gate structure directly: cheap deterministic checks (schema validation, metric math, code-based graders) run on every change; LLM-judged and live-traffic evals run on a coarser cadence (per significant change to prompts/workflow/model, or daily as a batch). The general software-engineering test pyramid (roughly 70% unit / 20% integration / 10% E2E) still applies — LLM calls just add a slow, non-deterministic top layer on top of it, not a replacement for the fast bottom layers.

**Sources:**
- [Testsigma — What is Testing Pyramid?](https://testsigma.com/blog/testing-pyramid/) — unit tests on every commit, E2E reserved for release/nightly.
- [DevRocks — Automated Tests in CI/CD: The Test Pyramid](https://www.devrocks.de/en/blog/automatisierte-tests-cicd-test-pyramide) — unit and integration on every commit because they're fast; E2E gated to PRs into main or nightly.
- (this repo: `ai-engineering/06-eval/evals/gate-contract.md`) — "run tests at the same layer as the change," with fast metric/schema tests distinct from slower report-rendering and grader-recalibration runs.

</details>

<details>
<summary><b>Q: [Follow-up] If the system supports ten models from five providers, would you run the complete test suite on every model for every change?</b></summary>

No — that's an N×cost, N×latency multiplier on every PR for marginal signal, since most code changes (a tool schema tweak, a retry policy fix, a prompt wording change) don't interact with model-specific behavior at all. I'd apply a **risk-tiered matrix** instead of a flat full-matrix run:

1. **Unit/integration tests stay model-agnostic** wherever possible — mock the model call, test the harness logic (retries, tool routing, schema validation) without hitting any provider. These run on every change, every model, effectively for free.
2. **On every PR**, run the agent-behavior eval suite against **one cheap, fast representative model per provider family** (or even just 1–2 models total) — a smoke test that catches gross regressions in minutes, not a full ten-model sweep.
3. **Full ten-model matrix runs on a coarser trigger**: nightly, on release candidates, or specifically when the change touches the model-adapter/config layer (new provider param mapping, model registry update, prompt change likely to interact with model-specific quirks).
4. **Track cost/quality per model** as an ongoing leaderboard rather than a pass/fail gate on every commit — sort by score-per-dollar, and only re-run the full comparison when something changes that could shift that ranking.
5. Reserve full-matrix runs for changes explicitly flagged as **cross-provider-risk** (e.g. touching the adapter layer from Theme 1) — that's exactly the class of change where per-provider quirks are likeliest to surface.

This is the same "test at the layer of the change" principle from the previous answer, applied to the provider dimension: cheap and universal on every commit, expensive and full-matrix on a schedule or when the diff specifically touches multi-provider logic.

**Sources:**
- [Hadley Works (dev.to) — LLM Evaluation in CI: Stop Manual Testing Before It Costs You](https://dev.to/hadleyworks/llm-evaluation-in-ci-stop-manual-testing-before-it-costs-you-59i7) — use a cheaper/faster model for PR-time checks, reserve the full/expensive model for release or nightly runs to keep CI feedback fast and cheap.
- [Digital Applied — LLM Model Routing 2026: Cost-Quality Optimization](https://www.digitalapplied.com/blog/llm-model-routing-2026-cost-quality-optimization-engineering-guide) — sort providers by score/cost to find the tradeoff frontier rather than treating every model as equally worth testing on every change.
- (this repo: `ai-engineering/06-eval/evals/gate-contract.md`, Gate 4 "Model And Runtime Comparison") — model/runtime comparison is its own gate, run and exported separately from the fast per-commit metric tests, precisely because it's a coarser-cadence, higher-cost evaluation.

</details>

---

## 4. Observability & Tracing

<details>
<summary><b>Q: How would you collect traces from the agent system?</b></summary>

Instrument every agent call to emit a structured trace, modeled as a **trace tree**: one root span per agent run, with child spans per LLM call, tool invocation, and retrieval step.

- **Capture the essentials on every span** — full prompt / `messages[]` history across turns, every tool call with its arguments and return value, intermediate reasoning, final output, token/latency metadata.
- **Follow a standard schema** — the OpenTelemetry GenAI semantic conventions (`invoke_agent` root span, `chat` spans per LLM call, `execute_tool` spans per tool call, `gen_ai.usage.*` / `gen_ai.response.finish_reasons` attributes) keep traces comparable across frameworks.
- **Wire into each framework's native instrumentation** rather than one generic wrapper — LangGraph's `CallbackHandler`, Langfuse's `@observe` decorator for a normal call stack, or `lf.trace()` + a `ContextVar` for runner/event-loop frameworks (e.g. Google ADK) where propagation doesn't follow a normal Python call stack. Native instrumentation captures framework-specific structure (graph node transitions, tool sequences) that a unified adapter would flatten.
- **Attach a stable metadata contract** to every trace — `run_id`, `session_id`, `prompt_version`, `git_commit`, `model`, `latency_ms`, input/output tokens, escalation/guardrail flags — so runs are reproducible and diffable across prompt or config changes.
- **Export over OTLP** to a backend (Langfuse, LangSmith, Arize Phoenix, Datadog) for storage and querying.

**Sources:**
- [OpenTelemetry: Inside the LLM Call — GenAI Observability with OpenTelemetry](https://opentelemetry.io/blog/2026/genai-observability/) — span structure and semantic conventions for LLM/agent tracing.
- [Langfuse Docs — LLM Observability & Application Tracing](https://langfuse.com/docs/observability/overview) — trace/observation/session data model and framework wiring.
- (this repo: `generative-ai/06-observability/support-agent-observability.md`) — base trace metadata schema and per-framework wiring used in this repo's support-agent system.
- (this repo: `generative-ai/04-agentic-frameworks/notes/langfuse.md`) — concrete `lf.trace()` + `ContextVar` pattern for non-call-stack agents.

</details>

<details>
<summary><b>Q: Once the traces have been collected, how would you go through and analyze them?</b></summary>

Use a **two-layer strategy** rather than relying on one:

1. **Layer 1 — rule-based manual sampling.** Pull traces flagged by negative user feedback, unusually long/high-token dialogues (a proxy for the agent circling), and a fixed daily time-window sample for baseline coverage; humans label execution quality and failure reason.
2. **Layer 2 — LLM-as-judge at scale.** Run judge scoring over a much larger slice of traffic (typically 10–20% sampled, not 100%, for cost), calibrated against the layer-1 labels.

Neither layer works alone — pure LLM-judge scoring drifts without human calibration, and pure human sampling never covers production volume. One special rule: after any prompt or model change, run **full review** (not sampled) on traces for the first 24–48 hours to catch regressions early.

When reading individual traces, don't stop at the aggregate score — walk the **trajectory** to see where it broke: which tool was called, with what arguments, what came back, and where the reasoning diverged from the plan. Aggregate metrics tell you *that* something regressed; traces tell you *why*. Trace-level querying also pays off here — e.g. "show me every trace where two specific tools were both called" or "show me traces where `finish_reason` was `tool_calls` but no final answer followed" — turning debugging into targeted investigation instead of reading transcripts one by one.

**Sources:**
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — trajectory vs. outcome grading, reading traces not just scores.
- [Langfuse — What does a good trace look like?](https://langfuse.com/docs/observability/best-practices) — practical trace-reading and debugging guidance.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — two-layer manual/LLM-judge evaluation strategy and online sampling rules (negative-feedback triggers, high-cost dialogues, time-window sampling, 48h post-change review).
- (this repo: `interviewing/guides/6-evals-observability/interview-guide.md`) — condensed observability section with the same sampling rules.

</details>

---

## 5. Prompt Change Management & Regression

<details>
<summary><b>Q: [Main] What is a good way to introduce a prompt change into a codebase?</b></summary>

Treat the prompt exactly like production code:

- **Version it as its own artifact** — a file or prompt-management entry with metadata (version, target model, temperature, description, changelog) rather than an inline string scattered across the codebase.
- **Route it through the same review pipeline as code** — a branch/PR that shows the prompt diff, runs the eval suite automatically in CI, and requires human review before merge. Never edit the live prompt directly in a dashboard with no diff trail.
- **Pin the exact model snapshot** the prompt was validated against, not a moving alias — an alias that shifts underneath you is an undocumented, unrevertable deploy.
- **Roll out progressively**, not as a hard cutover — start behind a flag or a small traffic percentage, compare against the existing prompt with an A/B or shadow run, and only promote to 100% once the eval gate and online monitoring both clear.

This repo's own support-agent system does this concretely — `prompt_version` and `git_commit` are logged on every trace so any output can be tied back to the exact prompt text and code state that produced it, and prompts are fetched from a managed store (Langfuse) rather than hardcoded.

**Sources:**
- [Langfuse — Prompt CI/CD: version, gate, and roll out prompts like code](https://langfuse.com/resources/engineering/prompt-cicd) — versioning, gating, and rollout workflow for prompts.
- [Braintrust — Best Prompt Versioning Tools for Production Teams (2026)](https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025) — prompt file/metadata/changelog pattern, PR-based review of prompt diffs.
- (this repo: `generative-ai/06-observability/support-agent-observability.md`) — `prompt_version` + `git_commit` fields logged on every trace; remote prompt fetch pattern.

</details>

<details>
<summary><b>Q: [Follow-up] How would you evaluate a prompt change before releasing it?</b></summary>

Run the change through the existing eval harness before it ever reaches production traffic, using a **tiered set of graders in cost order**:

1. **Deterministic checks first** — schema/format validity, expected tool calls. Cheap, CI-safe, catches the majority of regressions.
2. **Trajectory checks** — did the sequence of tool calls stay correct against a golden set.
3. **LLM-judge or human-reviewed quality pass** for the cases requiring semantic judgment.

Compare old vs. new prompt on the **same fixed dataset** — an A/B or experiment run — rather than eyeballing a handful of examples, and include adversarial/negative cases (injection attempts, out-of-scope requests) so the new prompt isn't just optimizing for the happy path. Gate the merge/deploy on this: block if the pass rate on the regression suite drops beyond a set threshold, and treat any new failing category as a signal to inspect traces before shipping, not after. In this repo's own eval pipeline, model/prompt comparisons are exported with full run metadata (`prompt_version`, retrieval config, sample size) specifically so a prompt change can be diffed against its baseline rather than judged in isolation.

**Sources:**
- [LangSmith CI/CD Integration: Automated Regression Testing](https://markaicode.com/langsmith-cicd-automated-regression-testing/) — PR-triggered eval run, pass/fail gate against a dataset threshold.
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — grading trajectory + outcome, capability vs. regression suite distinction.
- (this repo: `ai-engineering/06-eval/evals/eval-harness-patterns.md`) — "prompt change confidence," tool-trajectory scoring, two-phase run/assert CI pattern, regression gate example.
- (this repo: `ai-engineering/06-eval/evals/gate-contract.md`) — `prompt_version` as a required field in every model/runtime comparison export.

</details>

<details>
<summary><b>Q: [Main] How would you track whether a prompt change made the system better or worse over time? — regression detection</b></summary>

Two mechanisms, run continuously rather than once at ship time:

1. **A standing regression suite** — a curated set of previously-passing cases (seeded from real production failures, not synthetic ones) that must stay at a near-100% pass rate. Any capability eval that saturates gets promoted into this suite so it keeps being checked on every future change. Run it in CI on every prompt PR and again nightly against the deployed version, diffing run-over-run scores rather than eyeballing single numbers.
2. **Production drift monitoring** — apply the same scoring pipeline used at validation time to a sample of live traffic on a schedule, tracking metrics against a fixed baseline and alerting on divergence. This catches slow degradation a point-in-time eval run misses (input distribution shift, upstream API/tool changes, seasonality, a prompt interacting badly with a model version bump).

Full review of traces for the first 24–48 hours after any prompt or model change is the cheap early-warning layer before drift-alert thresholds would even fire. When a metric drops, **debug the eval system before blaming the prompt** — check for infra errors/timeouts, grader bugs, and whether the drop concentrates in one task category — only then treat it as a real regression.

**Sources:**
- [Galileo — 9 Best LLM Drift Monitoring Platforms](https://galileo.ai/blog/best-llm-output-drift-monitoring-platforms) — production drift monitoring approach and tooling landscape (Arize, Evidently, Phoenix).
- [Markaicode — LangSmith CI/CD Integration: Automated Regression Testing](https://markaicode.com/langsmith-cicd-automated-regression-testing/) — CI regression gate blocking on pass-rate drop.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — capability→regression eval graduation, "fix the eval system before the agent" debugging order, 48h full-review-after-change rule.
- (this repo: `ai-engineering/06-eval/eval-maturity-ladder.md`) — Level 4 "continuous sampling with drift alerts" as the maturity target.

</details>

<details>
<summary><b>Q: How would you obtain reliable results when repeated runs of the same prompt can produce different outputs?</b></summary>

Accept non-determinism as structural rather than a bug to eliminate — even temperature 0 doesn't guarantee identical outputs across calls, since batching, hardware/kernel non-determinism, and floating-point accumulation on the serving side introduce variance regardless of sampling settings.

- **Evaluate over multiple trials per task**, not a single run, and report two complementary metrics: **pass@k** — the probability at least one of *k* trials succeeds (capability ceiling) — and **pass^k** — the probability *all k* trials succeed (deployment reliability). A 75%-per-trial agent only clears all 3 trials ~42% of the time. Customer-facing systems should be judged on pass^k, since users experience a single draw, not the best of several.
- **Reduce variance in the outputs themselves** — lower temperature/top_p where determinism matters more than diversity, use self-consistency (sample several reasoning paths and take a majority vote) for reasoning-heavy tasks, and pin the exact model snapshot so version drift isn't mistaken for prompt instability.
- **Run the grader multiple times too** if it's LLM-based, since judge variance stacks on top of generator variance.

**Sources:**
- [QAnswer — Why LLMs Are Not Deterministic Even at Temperature 0](https://www.qanswer.ai/blog/llm-non-determinism-temperature-zero) — sources of residual non-determinism at temp=0.
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — pass@k vs. pass^k definitions and when each applies.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — "run an eval set multiple times instead of once," pass@k / pass^k worked example.

</details>

---

## 6. Tool & Workflow Design

<details>
<summary><b>Q: What makes a good tool design for an agent?</b></summary>

Design for the **Agent-Computer Interface**, not an API: the model sees only a name, a description, and a parameter schema — no docs, no autocomplete, no follow-up question. The description has to do the work a human colleague would otherwise infer.

- **Write for disambiguation, not just description** — what the tool does, when to use it, when *not* to use it, and hard "do not use for" negatives that separate it from neighboring tools. The negative cases are what actually stop tools from overlapping.
- **Apply the clarity test** — if a human engineer given three realistic tasks can't confidently say which tool to reach for, an agent can't either.
- **Structure the contract carefully** — snake_case verb-noun names as the first routing signal, enums over free strings, absolute over relative paths, typed and token-efficient return values (a human-readable summary, not a raw dump — offload bulk data to disk with a path reference), and structured errors with a stable error code the agent can reason about.
- **Check every tool against four gates before shipping** — is it reversible (else it needs a confirmation step), idempotent (else it must never be auto-retried), observable (does it emit a trace), and parallel-safe.

Anthropic's own guidance converges on the same point from the opposite direction: the dominant failure mode is too many overlapping tools, and cutting tools is often a bigger win than adding better descriptions to bad ones — **tool quality beats tool quantity**.

**Sources:**
- [Anthropic — Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — namespacing, meaningful context in returns, tool-description as the highest-leverage lever.
- [Vercel — Build an AI Agent Harness](https://vercel.com/academy/build-ai-agent-harness) — five-section tool contract (what/when/when-not/do-not-use-for/examples).
- (this repo: `ai-engineering/03-harness/notes/03-tool-design.md`) — ACI framing, the clarity test, four gating questions, schema rules, write-operation safety.

</details>

<details>
<summary><b>Q: [Main] At what point would you introduce skills into an agent system, instead of prompts and tools?</b></summary>

Introduce skills when a capability needs to be **reused across many invocations or many agents/teams**, *and* the procedure is bulky enough that keeping it always-resident in the system prompt would waste context and degrade tool-selection accuracy.

- **The mechanism is progressive disclosure** — a skill's name and one-line description (~10 tokens) stay resident so the agent can route to it, while the full procedure (steps, templates, worked examples) only loads into context when the task actually activates it.
- **This differs from the alternatives**: baking instructions into the system prompt is always resident and doesn't scale past a handful of procedures before "prompt sprawl" degrades everything else; letting the model improvise the procedure fresh every time is inconsistent and hard to audit or version.
- **Concrete triggers**: the same multi-step procedure keeps getting re-explained across sessions or teams; the procedure needs versioning/governance the way code does; loading every available tool/MCP server at startup is already measurably hurting selection accuracy as the tool set grows; or the task calls for bundled reference material too large to keep inline.

Skills work best layered on top of a small, sharp tool set — they make the *reasoning about how to combine tools* procedural, without bloating the tools themselves.

**Sources:**
- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — progressive disclosure, avoiding prompt sprawl, skills as reusable/auditable capability modules.
- (this repo: `ai-engineering/03-harness/skills-design.md`) — description-as-routing-logic, token cost vs. routing precision, templates-inside-skill pattern.
- (this repo: `ai-engineering/03-harness/notes/03-tool-design.md`) — "loading every tool/MCP server at startup degrades performance before the agent starts working," motivating progressive disclosure via skills.

</details>

<details>
<summary><b>Q: Do skills completely replace a regular agent that has only a few tools?</b></summary>

No — skills are **additive to tools**, not a replacement for the agent/tool layer, and for a small, well-scoped tool set they're often unnecessary overhead.

- **A skill still needs an agent with tools underneath it** to actually execute anything; the skill supplies the *procedure* (when to use which tool, in what order, with what conventions), while the tools remain the actual action surface.
- **A small, clear tool set already passes the "clarity test" on its own** — if a human (or the agent) can already tell which tool to use from the descriptions alone, adding a skill layer on top mainly adds indirection and a routing decision that wasn't needed.
- **Skills earn their cost when tool orchestration itself is the hard part** — a fixed multi-step workflow, a specific report format, domain conventions that keep drifting between sessions — not simply "the agent has tools."

So the right mental model isn't "skills vs. tools" but "skills sit above tools, and are worth the token/complexity cost only once combining tools well becomes the hard problem."

**Sources:**
- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — skills as composable capabilities layered on existing agent/tool infrastructure, not a replacement for it.
- (this repo: `ai-engineering/03-harness/notes/07-orchestration.md`) — "what matters is tool quality, not tool quantity"; skills close the gap between single tool invocation and multi-tool orchestration without bloating system prompts.

</details>

<details>
<summary><b>Q: When would you use a skill, a tool, a deterministic workflow, or a separate agent?</b></summary>

Start from Anthropic's core guidance: find the simplest structure that solves the problem, and only add complexity — and especially model-driven autonomy — when it's actually needed. In order of increasing flexibility and cost:

- **Deterministic workflow** (predefined code path orchestrating LLM calls and tools) when the task has a fixed, well-understood sequence of steps and you want predictability, low latency, and easy debugging — most production tasks fit here and don't need an "agent" at all.
- **Tool** when the capability is a single, well-bounded action the model needs to invoke as part of its own reasoning (fetch data, mutate state, run a calculation) — the action itself is atomic and doesn't need multi-step judgment.
- **Skill** when a multi-step *procedure* using one or more tools needs to be reusable, versioned, and consistently applied across many tasks or sessions, and keeping it always-loaded in the prompt would bloat context or degrade tool-routing accuracy — i.e. you want progressive disclosure of a known-good playbook, not the model re-deriving the approach each time.
- **Separate agent** when the task genuinely needs open-ended, model-driven control over its own process — the number of steps can't be predicted in advance, the agent must adapt its plan based on environment feedback, or a distinct trust/tool boundary (least-privilege scoping, isolated context) is required. This is the most expensive option in latency, cost, and predictability, so it should be the last one reached for, and Anthropic explicitly frames "not building agentic systems at all" as a legitimate outcome of this evaluation.

**Sources:**
- [Anthropic — Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows-vs-agents distinction, "find the simplest solution possible," cost/latency trade-off of agentic autonomy.
- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — skills as the reusable-procedure layer distinct from both tools and agents.
- (this repo: `ai-engineering/03-harness/notes/03-tool-design.md`) — MCP vs. in-process decision table, applicable to the tool/skill boundary question by analogy (promote complexity only when a specific condition holds, not in anticipation).
- (this repo: `ai-engineering/03-harness/agents-design.md`) — multi-agent decomposition patterns and when a separate agent (vs. a single agent with more tools) is warranted, including least-privilege scoping per agent.

</details>

---

## 7. Context Window & Large Data Handling

<details>
<summary><b>Q: [Main] Given the model's limited context window, what is the right way to handle an operation that can return a huge amount of data?</b></summary>

Never let a tool dump its full payload into the window — treat the boundary between the tool and the model as a filtering layer, not a pipe. Four techniques compose:

1. **Paginate/truncate with a continuation affordance.** Cap output at a sane size (Claude Code defaults tool responses to ~25k tokens) and return an explicit "showing rows 1–50 of 4,000, pass `offset=50` to continue" marker so the agent can deliberately ask for more rather than silently losing data.
2. **Filter and summarize at the tool boundary**, where filtering is cheap and deterministic, not in the model where it costs attention. Return structured summaries plus drill-down identifiers (IDs, file paths, row keys) rather than full records — "just-in-time" retrieval: a path costs ~10 tokens, the file costs 5,000; load the identifier, fetch content only when actually needed.
3. **Isolate in a sub-agent** for genuinely large exploratory operations — let it burn 100k tokens searching/reading and return only a condensed 1-2k token summary to the orchestrator, discarding the rest.
4. **Compact/checkpoint** for long-running operations: write structured state (what was found, what's left) to disk as you go so a token-heavy operation doesn't have to be replayed or held in-window to survive.

The unifying principle: return what the agent needs to *decide*, not everything the operation *could* produce. A tool that returns 50k tokens of raw output defeats the point of selective retrieval and just re-introduces the bulk-loading problem one layer down.

**Sources:**
- [Anthropic — Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — pagination/truncation/filtering guidance, 25k-token default, MCP `maxResultSizeChars` annotation.
- [Arize AI — Context management in agent harnesses](https://arize.com/blog/context-management-in-agent-harnesses/) — memory, files, and subagent patterns for bounding context.
- (this repo: `ai-engineering/02-context/notes/03-retrieval-strategies.md`) — just-in-time context and identifier-vs-payload cost tradeoff.
- (this repo: `ai-engineering/02-context/notes/06-multi-agent-context.md`) — token-efficient tool design and sub-agent isolation for large operations.
- (this repo: `ai-engineering/02-context/notes/04-compression-compaction.md`) — checkpointing to disk for long-running operations.

</details>

---

## 8. Production RAG Evaluation

<details>
<summary><b>Q: How would your evaluation approach handle customers from different industries and documents in different languages?</b></summary>

Treat "one global eval set" as the failure mode — industry and language are both segmentation axes that need their own slices, not an average that hides them.

For **industry variation**: build per-customer or per-vertical eval sets seeded from that customer's real queries and documents, not a generic benchmark — terminology, acceptable answer format, and what counts as "grounded" differ (legal citations vs. support-macro tone vs. clinical terminology). Track metrics per-segment, not only in aggregate, since a strong blended score can hide one industry silently regressing.

For **language variation**: don't assume an English-tuned pipeline or English-only judge generalizes — retrieval quality, chunking, and embedding models can degrade non-uniformly across languages, and off-the-shelf frameworks like RAGAS have historically had thin non-English support (question generation in RAGAS v2 dropped the multilingual adapter that existed in v1). Practical approach: evaluate faithfulness/relevance with native-language judges or human review per language, watch for language-mismatch as its own failure mode (answer language ≠ query language), and consider starting new checks as **log-only diagnostics** before they become hard gates — exactly what one production system in this repo did for a Danish/English support agent, where over-aggressive grounding checks in a multilingual, paraphrase-heavy context caused excessive false escalations.

**Sources:**
- [MEMERAG: Multilingual End-to-End Meta-Evaluation Benchmark for RAG](https://arxiv.org/html/2502.17163v2) — native-language QA and expert annotation approach for multilingual RAG eval.
- [Multi-lingual support for question generation in Ragas v2 — GitHub issue](https://github.com/vibrantlabsai/ragas/issues/1732) — documents the gap in current multilingual tooling.
- (this repo: `generative-ai/06-observability/support-agent-observability.md`) — grounding tier promotion policy and log-only phase for a multilingual (Danish/English) support agent.

</details>

<details>
<summary><b>Q: [Main] If a customer says, "The results are bad," what would you do first, how would you determine what actually failed?</b></summary>

First, resist the urge to touch the model or prompt — go get the trace. "Bad" is not a diagnosis; it's a symptom that can originate at any of several distinct layers, and the fix differs completely depending on which one failed. Practical order:

1. **Reproduce with the actual trace.** Pull the specific query, retrieved passages, and generated answer for that customer's session (not a re-run — the original). Without full input/tool-call/output logging this step is impossible, which is why tracing is a prerequisite to debugging, not a nice-to-have.
2. **Rule out infrastructure/eval-system bugs before blaming the agent** — timeouts, stale index, broken parser on a document type, a grader bug. It's common for the evaluation system itself to be the noisy signal.
3. **Localize the failure layer**, walking the pipeline in order: was the *right document even retrieved* (retrieval failure — chunking, embedding mismatch, stale index)? Was it retrieved but the *wrong passage highlighted/cited* (extraction failure)? Was the *right evidence retrieved but ignored or misstated* in generation (grounding/hallucination failure — research shows this, not retrieval, is often the dominant cause)? Or is it a *data quality* problem — the source document itself is outdated or wrong?
4. **Use claim/citation-level tracing** if available: which cited passage backs which sentence in the answer immediately tells you whether it's a retrieval, extraction, or generation problem — same document, different symptom, different fix.
5. **Check whether the failure is isolated or systemic** — one customer/query, or a category (industry, language, document type) — before deciding this is a one-off vs. a regression worth a suite addition.

Every confirmed failure becomes a new row in the eval set so it can't silently regress again.

**Sources:**
- [The RAG Debugging Playbook — DEV Community](https://dev.to/kuldeep_paul/the-rag-debugging-playbook-a-step-by-step-guide-to-trace-level-failures-and-fixes-56pa) — trace-level failure localization across data/retrieval/generation/pipeline layers.
- [RAG Fails Silently: Debugging Retrieval, Citations, and Unsupported Claims — Towards AI](https://pub.towardsai.net/rag-fails-silently-debugging-retrieval-citations-and-unsupported-claims-aa6f730b730a) — evidence that generation-side grounding failure, not retrieval, is often the primary cause.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — "fix the evaluation system before changing the agent" practical debugging order (infra → traces → category concentration → agent).
- (this repo: `ai-engineering/06-eval/grounding-methodology.md`) — claim extraction as a debugging tool: wrong document = retrieval problem, wrong highlighted sentence = extraction problem, right claim/wrong explanation = generation problem.

</details>

<details>
<summary><b>Q: [Main] How would you construct a real customer-specific evaluation dataset whose results you could trust?</b></summary>

Trustworthiness comes from where the rows originate and how disagreement is handled, not from dataset size. Concretely:

1. **Seed from real production data, not synthetic invention** — actual customer queries against actual customer documents, especially rows drawn from confirmed failures (support escalations, negative feedback, corrected answers). A small set (20–50 rows) of *real* failure cases beats a large but noisy synthetic benchmark.
2. **Include positive and negative examples deliberately.** Positive rows test capability; negative rows test restraint (does it correctly refuse / say "I don't know" instead of hallucinating on out-of-scope or unanswerable questions for this customer's corpus). Without negatives, a system can "improve" simply by answering more confidently.
3. **Write unambiguous tasks with reference answers/grounding sources**, such that two domain experts independently reach the same pass/fail. Ambiguous rubrics are noise, not signal.
4. **Version the dataset and the corpus snapshot together** — a customer's documents change, so an eval row is only valid against the document version it was written for; re-validate or retire rows when the underlying KB updates.
5. **Calibrate any LLM judge against a human-labeled sample** (5–10%) before trusting its scores at volume, and re-check periodically — an uncalibrated judge should be tracking-only, never a release gate.
6. **Reset environment/state per trial** and run each row multiple times if the agent is non-deterministic, so a single unlucky sample isn't mistaken for a systemic failure.
7. **Keep expanding the frontier** — once pass rate saturates, it usually means the suite stopped exposing new failure modes, not that the system is solved; keep adding newly discovered production failures.

**Sources:**
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — start small with real failures, positive/negative case design, environment reset, saturation signal.
- [LangChain — Agent evaluation readiness checklist](https://www.langchain.com/blog/agent-evaluation-readiness-checklist) — ruling out infra/data issues, trace inspection for grader fairness.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — the full "collect real failures → clear criteria → isolated tasks → repeated trials → code/model/human grading → inspect traces → expand" pipeline.
- (this repo: `ai-engineering/06-eval/README.md`, `agent-eval.md` reference) — golden dataset curation rules: real user queries, balanced coverage, eligibility labels per gate, versioned, 50–200 rows for LLM grading.

</details>

---

## 9. Feedback Signals & Evaluation Dataset Construction

<details>
<summary><b>Q: [Main] After shipping the system, how would you collect explicit and implicit signals that can be used for evaluation?</b></summary>

Collect both, because they cover different populations and biases. **Explicit** signals — thumbs up/down, star ratings, free-text corrections, "was this helpful" — are cheap to read and directly labeled, but only 1–3% of users ever leave one, and those who do skew toward extreme (very happy / very angry) experiences, so they're a biased sample. **Implicit** signals cover effectively 100% of traffic: query rephrasing/reformulation within a session (a strong proxy for "the last answer didn't work"), conversation abandonment, follow-up "that's wrong" turns, copy actions, session return rate, escalation to a human, and — where available — dwell time or click-through on cited sources.

Practically, this means instrumenting the product itself, not just the model call:
- A feedback UI (thumbs, correction box) wired to the trace ID of the turn it applies to, so a rating is always attachable to the exact query/retrieval/answer that produced it.
- Full tracing on every turn (prompt, retrieved passages, tool calls, final output, tokens/latency) — signals are worthless without the trace they refer to.
- Rule-based online sampling rather than pure random sampling: prioritize traces with negative feedback, unusually long/high-token dialogues (often circling/failure), and a fixed time-window random sample for baseline coverage; do a full review pass in the 48 hours after any prompt or model change.
- Escalation and "contact support" flags as a structured implicit signal, since they mark exactly where the system judged itself unable to help.

**Sources:**
- [Eugene Yan — Patterns for Building LLM-based Systems & Products](https://eugeneyan.com/writing/llm-patterns/) — explicit vs. implicit feedback UX and their role in building eval/fine-tuning datasets.
- [Nebuly — User intent and implicit feedback in conversational AI](https://www.nebuly.com/blog/explicit-implicit-llm-user-feedback-quick-guide) — explicit feedback capturing only 1–3% of users vs. 100% implicit coverage; rephrasing as a failure signal.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — online sampling rules (negative-feedback triggering, high-cost dialogues, time-window sampling, post-change full review).
- (this repo: `generative-ai/06-observability/support-agent-observability.md`) — trace schema (`escalated`, `contact_support`, `grounding_score` fields) that makes feedback attributable to a specific run.

</details>

<details>
<summary><b>Q: [Main] How would you use those signals to begin constructing positive and negative examples for an evaluation dataset?</b></summary>

The signals are raw material; turning them into trustworthy eval rows takes a deliberate pipeline, not a direct dump:

1. **Extract candidate rows from feedback-adjacent traces.** Thumbs-down, escalations, rephrased queries, and abandoned sessions become negative candidates; thumbs-up, low-latency single-turn resolutions, and sessions with no follow-up correction become positive candidates.
2. **Cluster by intent/failure type** before labeling individually — many raw negative signals collapse into a handful of recurring root causes (a specific document out of date, a chunking gap for one doc type, a language-mismatch pattern). Label at the cluster level so the dataset gets *coverage* of failure modes, not just volume of similar rows.
3. **Human-verify before trusting**, especially negatives: a thumbs-down can mean "wrong answer" or "right answer, annoying tone" or "user was venting" — these need different fixes and only some belong in a correctness eval. Don't take raw feedback as ground truth without a domain-expert pass.
4. **Attach the reference answer/grounding source to each row** at labeling time (what *should* the retrieval + answer have been), so the row can be graded deterministically or by a calibrated judge later, not just replayed.
5. **Keep negatives intentionally including restraint cases** — inputs the system should refuse or hedge on — pulled from confirmed hallucination/overreach incidents, not only "wrong answer" cases, so the dataset also protects against the system becoming falsely confident.
6. **Version and re-run periodically** — as the underlying corpus and model change, previously-negative rows may need re-validation, and the dataset should keep absorbing newly observed failures rather than freezing at v1.

**Sources:**
- [Microsoft Data Science + AI — Beyond thumbs up and thumbs down: A human-centered approach to evaluation design](https://medium.com/data-science-at-microsoft/beyond-thumbs-up-and-thumbs-down-a-human-centered-approach-to-evaluation-design-for-llm-products-d2df5c821da5) — limits of raw explicit ratings and need for human-centered labeling.
- [Eugene Yan — Patterns for Building LLM-based Systems & Products](https://eugeneyan.com/writing/llm-patterns/) — feedback → eval/fine-tuning dataset pipeline, organizational discipline of sample→annotate→improve.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — positive/negative case design, "include both to test capability and restraint," failure-seeded eval rows.
- (this repo: `ai-engineering/06-eval/README.md`, `agent-eval.md` reference) — failure taxonomy labels (`citation_hallucination`, `unsupported_claim`, `rank_miss`, `wrong_escalation`) used to cluster and tag negative rows.

</details>

<details>
<summary><b>Q: Which metrics or behavioral signals showed that the previous chatbot was performing poorly?</b></summary>

*This question references a specific "previous chatbot" from an interview scenario with no details provided here, so I can't cite its actual numbers — treat this as the generic playbook for diagnosing a poorly-performing production chatbot, and adapt to whatever the interviewer's scenario supplies.*

Signals to cross-check against each other, rather than trusting any single one:

- **Explicit dissatisfaction** — thumbs-down rate, CSAT/star ratings, explicit "this didn't help" replies.
- **Escalation/deflection rate** — how often the bot hands off to a human or a "contact support" fallback; a rising rate is one of the cleanest proxies for the bot silently failing.
- **Rephrasing/re-ask rate** — users repeating or rewording the same question within a session is a strong implicit signal the first answer missed the mark.
- **Abandonment rate** — sessions ending without resolution (no confirmation, no follow-up satisfaction, user simply leaves).
- **Conversation length outliers** — unusually long dialogues often indicate the bot is circling rather than resolving, which is why long-dialogue traces get prioritized for manual review.
- **Grounding/citation-quality metrics** — hallucinated citations, unsupported claims, or zero-overlap "supporting quotes" if the system tracks claim-level grounding.
- **Task/containment success rate** — did the interaction actually resolve the stated intent, measured against a labeled eval set of real queries, not just "did it respond."
- **Trend over time / drift** — a metric that was fine at launch but degraded is as diagnostic as a metric that was always bad; requires a baseline captured at validation time to compare against.

The right way to actually answer this for a specific scenario is the same triage used for "results are bad": pull traces, segment by failure category, and let the concentration of a specific signal (e.g. escalation spikes on one intent, or rephrasing spikes on one document type) point to the root cause rather than assuming from the aggregate metric alone.

**Sources:**
- [Nick Talwar — 6 things your AI agents need that most teams skip](https://nicktalwar.substack.com/p/6-things-your-ai-agents-need-that) — drift monitoring via baseline-vs-production scoring gap as a concrete regression signal.
- [Nebuly — User intent and implicit feedback in conversational AI](https://www.nebuly.com/blog/explicit-implicit-llm-user-feedback-quick-guide) — rephrasing/abandonment as implicit failure signals.
- (this repo: `ai-engineering/06-eval/eval-harness.md`) — rule-based sampling on negative feedback and high-cost/long dialogues as failure-concentration signals.
- (this repo: `generative-ai/06-observability/support-agent-observability.md`) — `escalated`, `contact_support`, `grounding_score` as trace-level fields that operationalize these signals.

</details>
