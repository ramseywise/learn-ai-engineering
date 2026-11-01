"""Claude prices used by every chapter. Dated, because prices change.

Source: https://platform.claude.com/docs/en/about-claude/pricing, read 2026-11-01.
USD per million tokens. Haiku 5.5 is the rate for prompts up to 100,000 tokens.
"""

PRICES_AS_OF = "2026-11-01"
PRICES_SOURCE = "https://platform.claude.com/docs/en/about-claude/pricing"

PRICES = {
    "claude-opus-5-5": {"input": 4.00, "cache_write": 5.00, "cache_read": 0.20, "output": 20.00},
    "claude-sonnet-5-5": {"input": 2.00, "cache_write": 2.50, "cache_read": 0.10, "output": 10.00},
    "claude-haiku-5-5": {"input": 0.10, "cache_write": 0.125, "cache_read": 0.01, "output": 0.50},
}


def llm_cost(model, input_tokens=0, output_tokens=0, cache_read_tokens=0, cache_write_tokens=0):
    """Cost in USD. `input_tokens` is the uncached remainder, as the API reports it."""
    p = PRICES[model]
    return (
        input_tokens * p["input"]
        + output_tokens * p["output"]
        + cache_read_tokens * p["cache_read"]
        + cache_write_tokens * p["cache_write"]
    ) / 1_000_000
