"""Free online scores: heuristics that need no model and run on every trace."""

DANISH_MARKERS = {"jeg", "du", "og", "er", "på", "af", "til", "der", "det", "en", "hvis", "med", "før", "eller", "kan", "har", "inden", "for"}
ENGLISH_MARKERS = {"the", "you", "is", "of", "to", "and", "can", "for", "with", "a", "it", "before", "are", "up", "what", "how"}


def language_of(text):
    """Guess en or da from stopwords. Crude on purpose, and cheap enough for every turn."""
    words = {w.strip(".,?!").lower() for w in text.split()}
    return "da" if len(words & DANISH_MARKERS) > len(words & ENGLISH_MARKERS) else "en"


def citation_hallucination(trace):
    """1 if the answer cites a URL that retrieval never returned."""
    return float(any(u not in trace.retrieved_urls for u in trace.citations))


def missing_citation(trace):
    """1 if a substantive answer cites nothing."""
    return float(len(trace.answer.split()) > 8 and not trace.citations)


def language_consistency(trace):
    """1 if the answer is in the language of the question."""
    return float(language_of(trace.question) == language_of(trace.answer))


def retrieval_quality(trace):
    """The best retrieval score of any search in the turn."""
    tops = [s.tool_result["top_score"] for s in trace.spans if s.name == "kb_search" and s.tool_result]
    return max(tops) if tops else 0.0


def online_scores(trace):
    return {
        "citation_hallucination": citation_hallucination(trace),
        "missing_citation": missing_citation(trace),
        "language_consistency": language_consistency(trace),
        "retrieval_quality": retrieval_quality(trace),
    }
