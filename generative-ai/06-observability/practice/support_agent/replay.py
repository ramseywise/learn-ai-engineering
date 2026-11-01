"""Send a synthetic trace through the real Langfuse SDK."""

from langfuse import Langfuse, propagate_attributes


def usage_details(span):
    """Langfuse usage keys are exclusive buckets: each token is counted in exactly one."""
    return {"input": span.input_tokens, "output": span.output_tokens,
            "cache_read_input_tokens": span.cache_read_tokens,
            "cache_creation_input_tokens": span.cache_write_tokens}


def replay(lf, trace):
    """Re-emit `trace` with its id seeded from ours. Returns the Langfuse trace id."""
    trace_id = Langfuse.create_trace_id(seed=trace.trace_id)
    with propagate_attributes(user_id=None, session_id=trace.session_id, version=trace.release, trace_name="support_turn",
                              tags=[trace.route, trace.language],
                              metadata={"route": trace.route, "language": trace.language, "outcome": trace.outcome,
                                        "prompt_version": trace.prompt_version, "git_commit": trace.git_commit}):
        with lf.start_as_current_observation(name="agent_turn", as_type="agent", trace_context={"trace_id": trace_id},
                                             input={"message": trace.question},
                                             output={"message": trace.answer, "escalated": trace.escalated}) as root:
            for s in trace.spans[1:]:
                kw = {"model": s.model, "usage_details": usage_details(s), "cost_details": {"total": s.cost_usd}} if s.model else {}
                child = root.start_observation(name=s.name, as_type=s.kind, input=s.tool_args, output=s.tool_result, level=s.level,
                                               status_message=s.error, metadata={"latency_ms": s.latency_ms}, **kw)
                child.end()
    return trace_id
