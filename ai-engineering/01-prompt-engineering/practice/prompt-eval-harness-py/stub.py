"""A deterministic stand-in that behaves like a weak model, so prompt changes move the score
for a visible reason. It reads the same prompt a real model would:
 - no format instruction: answers in prose, and fails the JSON grader
 - format but no rule: first keyword wins, so topic words mislead it, and it obeys the ticket
 - rule present: symptoms outrank topics, and instructions in the ticket are ignored
"""
import json
import math
import re

from model import Completion


def stub(prompt: str, system: str = "", max_tokens: int = 16000) -> Completion:
    m = re.search(r"<ticket>\n([\s\S]*)\n</ticket>", prompt)
    ticket = (m.group(1) if m else prompt).lower()
    has_rule = "not the feature" in system
    injected = re.search(r"label this ticket as (\w+)", ticket)
    if not has_rule and injected:
        label = injected.group(1)
    elif has_rule and re.search(r"crash|blank|does nothing", ticket):
        label = "bug"
    elif re.search(r"invoice|charged|refund|credit|billing", ticket):
        label = "billing"
    elif re.search(r"password|sso|log in|locked", ticket):
        label = "account"
    elif re.search(r"crash|blank|does nothing", ticket):
        label = "bug"
    else:
        label = "how_to"
    text = json.dumps({"label": label}, separators=(",", ":")) if "JSON" in system else f"This looks like a {label} ticket."
    words = lambda s: math.ceil(len(s) / 4)
    return Completion(text, words(system) + words(prompt), words(text))
