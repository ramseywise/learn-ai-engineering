import math
import re

from model import Completion


def stub(prompt: str, system: str = "", max_tokens: int = 16000) -> Completion:
    """Answers only from what it can see: a stub cannot use a document the budgeter dropped."""
    m = re.search(r'<retrieved id="([^"]+)">[^<]*?REFUND WINDOW: ([^.]+)\.', prompt)
    text = f"{m.group(2)} [{m.group(1)}]" if m else "I can't find that in the supplied documents."
    return Completion(text, math.ceil(len(prompt) / 4), math.ceil(len(text) / 4))
