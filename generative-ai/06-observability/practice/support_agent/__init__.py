"""Stubbed support agent and synthetic traces for the observability chapters."""

from .pricing import PRICES, PRICES_AS_OF, PRICES_SOURCE, llm_cost
from .scorers import online_scores
from .traces import Span, Trace, generate_traces, load_jsonl, print_tree, to_jsonl
