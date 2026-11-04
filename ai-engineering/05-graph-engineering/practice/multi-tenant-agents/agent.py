"""One agent core. Nothing here names a tenant: prompt, rubric, tools, scopes, model alias and limits all come from the
config resolved for this run, and every enforcement point is reached through Controls.

It is a plain loop rather than a LangGraph graph. Budgets, scoped retrieval and the tool allowlist have to sit where
calls converge, under whatever orchestrates the run, so a graph here would add nodes without changing one result.
To use them from a graph, call complete_call, retriever.retrieve and tools.call inside your nodes.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from enforce import BudgetBusy, BudgetExceeded, FairQueue, Request, TokenBucket, ToolDenied
from model import Completion, Model, ModelError, ModelRequest, count_tokens
from tenancy import TenantConfig, score_answer

TOP_K = 3
MAX_TURNS = 3
MAX_BUDGET_WAIT = 5_000  # event-loop yields a call will wait for other runs' holds to settle before giving up


@dataclass(frozen=True)
class RunContext:
    run_id: str
    tenant_id: str
    config: TenantConfig


@dataclass
class Controls:
    store: object
    budget: object
    retriever: object
    tools: object
    traces: object
    model: Model


@dataclass
class RunResult:
    run_id: str
    tenant_id: str
    config_version: int
    status: str  # answered, escalated, budget_refused, model_error, out_of_turns
    answer: str = ""
    doc_ids: list[str] = field(default_factory=list)
    score: int = 0
    passed: bool = False


def build_prompt(cfg, ticket: str, docs: list, tool_results: list[str]) -> str:
    lines = "\n".join(f"[{d.id}] {d.text}" for d in docs)
    results = "".join(f"\n<tool_result>{r}</tool_result>" for r in tool_results)
    return (f"Tools you may use: {', '.join(cfg.tools)}. Do not use any other tool.\n"  # advice to the model, not a control
            f"<ticket>\n{ticket}\n</ticket>\n<docs>\n{lines}\n</docs>{results}")


async def complete_call(c: Controls, ctx: RunContext, prompt: str, turn: int) -> Completion:
    """Every model call passes here: reserve the worst case, await, settle to the actual."""
    cfg = ctx.config
    need = count_tokens(cfg.system_prompt + prompt) + cfg.max_tokens
    for _ in range(MAX_BUDGET_WAIT):
        try:
            hold = c.budget.before_call(ctx.tenant_id, ctx.run_id, need)
            break
        except BudgetBusy:
            await asyncio.sleep(0)
    else:
        raise BudgetExceeded(f"{ctx.tenant_id}: gave up waiting for holds")
    request = ModelRequest(ctx.tenant_id, ctx.run_id, cfg.model_alias, cfg.system_prompt, prompt, cfg.max_tokens, turn)
    try:
        result = await c.model(request)
    except ModelError:
        c.budget.after_call(hold, 0)  # a clean failure was not billed, so release it
        raise
    except BaseException:
        c.budget.after_call(hold, hold.tokens)  # cancelled mid-call: the bill is unknown, assume all
        raise
    c.budget.after_call(hold, result.total)
    return result


async def run_agent(c: Controls, tenant_id: str, run_id: str, ticket: str) -> RunResult:
    cfg = c.store.resolve(tenant_id, run_id)  # pinned: a rollback affects new runs, not this one
    ctx = RunContext(run_id, tenant_id, cfg)
    c.traces.begin(ctx)
    got = c.retriever.retrieve(cfg.knowledge_scopes, ticket, TOP_K)
    doc_ids = [d.id for d in got.docs]
    c.traces.record(ctx, "retrieve", detail=",".join(doc_ids))
    result = RunResult(run_id, tenant_id, cfg.version, "escalated", doc_ids=doc_ids)
    if not got.docs:
        c.traces.record(ctx, "escalate", status="no_evidence")  # nothing to answer from, so nothing is invented
        return result

    tool_results: list[str] = []
    for turn in range(MAX_TURNS):
        prompt = build_prompt(cfg, ticket, got.docs, tool_results)
        try:
            completion = await complete_call(c, ctx, prompt, turn)
        except BudgetExceeded:
            c.traces.record(ctx, "model", status="budget_refused")
            result.status = "budget_refused"
            return result
        except ModelError:
            c.traces.record(ctx, "model", status="model_error")
            result.status = "model_error"
            return result
        c.traces.record(ctx, "model", tokens=completion.total)
        if completion.tool_call is None:
            result.answer = completion.text
            result.score = score_answer(cfg, completion.text, doc_ids)
            result.passed = result.score >= cfg.rubric["min_score"]
            result.status = "answered"
            c.traces.record(ctx, "score", detail=str(result.score))
            return result
        name, args = completion.tool_call
        try:
            output = c.tools.call(tenant_id, cfg.tools, name, args)
            c.traces.record(ctx, f"tool:{name}")
        except ToolDenied as denied:
            output = f"denied: {denied}"
            c.traces.record(ctx, f"tool:{name}", status="denied")
        tool_results.append(output)
    result.status = "out_of_turns"
    return result


async def serve(c: Controls, requests: list[Request], workers: int, queue=None, limiters=None):
    """The whole path: admit against the tenant's rate limit, queue fairly, run on a fixed pool of workers."""
    configs = {t: c.store.get(t) for t in {r.tenant for r in requests}}
    if queue is None:
        queue = FairQueue({t: cfg.queue_weight for t, cfg in configs.items()})
    if limiters is None:
        limiters = {t: TokenBucket(cfg.rate_per_s, cfg.burst) for t, cfg in configs.items()}
    rejected = []
    for r in sorted(requests, key=lambda r: (r.arrival, r.id)):
        if limiters[r.tenant].allow(r.arrival):
            queue.push(r)
        else:
            rejected.append(r)
    results: list[RunResult] = []

    async def worker():
        while len(queue):
            r = queue.pop()
            results.append(await run_agent(c, r.tenant, r.id, r.ticket))

    await asyncio.gather(*(worker() for _ in range(workers)))
    return results, rejected
