"""The only file in this lab that knows about a provider.

Default: the stub passed in by the caller, so the lab runs offline with no key.
Set MODEL=claude-opus-5-5 and run with `uv run --with anthropic` to use a real model.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable


@dataclass
class Completion:
    text: str
    input_tokens: int
    output_tokens: int


Complete = Callable[..., Completion]  # complete(prompt, system="", max_tokens=16000)


def real_model(model: str) -> Complete:
    import anthropic  # imported here so the stub path needs no dependency at all

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY or an `ant auth login` profile

    def complete(prompt: str, system: str = "", max_tokens: int = 16000) -> Completion:
        res = client.beta.messages.create(
            model=model,
            max_tokens=max_tokens,
            **({"system": system} if system else {}),
            messages=[{"role": "user", "content": prompt}],
            # Re-runs a safety decline on Anthropic's recommended fallback model. Delete both
            # lines if you would rather see the refusal, or on Bedrock, Vertex and Foundry.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if res.stop_reason == "refusal":
            category = res.stop_details.category if res.stop_details else "unknown"
            raise RuntimeError(f"model refused: {category}")
        text = "".join(b.text for b in res.content if b.type == "text")
        return Completion(text, res.usage.input_tokens, res.usage.output_tokens)

    return complete


def choose_model(stub: Complete) -> tuple[str, Complete]:
    """`MODEL` set: the real model. Unset: the stub."""
    model = os.environ.get("MODEL")
    return (model, real_model(model)) if model else ("stub", stub)
