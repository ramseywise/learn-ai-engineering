# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Measures what the simulation assumes: TTFT, TPOT and cached tokens on a real streaming call.
With no MODEL it times a fake stream, so you can read the code path offline."""
import math
import os
import time

SYSTEM = "You are a support agent. " + "Policy text that stays the same between requests. " * 800
PROMPT = "In two sentences, why does a stable prompt prefix matter?"


def fake_stream():
    for word in ("A stable prefix lets the server reuse its cached work on every request. " * 3).split():
        time.sleep(0.005)
        yield word + " "


def report(label, start, first, end, chunks, output_tokens, cached):
    tpot = (end - first) / max(output_tokens - 1, 1)
    print(f"{label}: TTFT {1000 * (first - start):.0f} ms, total {1000 * (end - start):.0f} ms, "
          f"{output_tokens} output tokens, {1000 * tpot:.1f} ms per token after the first, {chunks} chunks, {cached} tokens read from cache")


model = os.environ.get("MODEL")
if not model:
    start = time.perf_counter()
    first, chunks = None, 0
    for _ in fake_stream():
        first = first or time.perf_counter()
        chunks += 1
    report("fake stream, not a measurement", start, first, time.perf_counter(), chunks, chunks, 0)
else:
    import anthropic

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY or an `ant auth login` profile
    for label in ["call 1, writes the cache", "call 2, reads the cache"]:
        start = time.perf_counter()
        first, chunks = None, 0
        with client.messages.stream(
            model=model,
            max_tokens=4000,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": PROMPT}],
        ) as stream:
            for _ in stream.text_stream:  # first visible text, so any thinking counts toward TTFT
                first = first or time.perf_counter()
                chunks += 1
            final = stream.get_final_message()
        end = time.perf_counter()
        if final.stop_reason == "refusal":
            raise SystemExit("model refused")
        report(label, start, first or end, end, chunks, final.usage.output_tokens, final.usage.cache_read_input_tokens or 0)
