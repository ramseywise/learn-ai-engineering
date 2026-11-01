"""Rule-based stand-in for the model, so the routing is what you are watching.
The one misbehaviour is on purpose: its first draft on a blank-page ticket forgets the citation."""
import math
import re

from model import Completion


def stub(prompt: str, system: str = "", max_tokens: int = 16000) -> Completion:
    ticket = re.search(r"<ticket>\n([\s\S]*?)\n</ticket>", prompt).group(1).lower()
    if system.startswith("CLASSIFY"):
        if "blank" in ticket:
            text = "bug"
        elif re.search(r"refund|charged", ticket):
            text = "billing"
        else:
            text = "how_to"
    else:
        m = re.search(r"^\[([\w-]+)\] (.+)$", prompt, re.M)
        forgets = "blank" in ticket and "Your last draft" not in prompt
        text = m.group(2) if forgets else f"{m.group(2)} [{m.group(1)}]"
    return Completion(text, math.ceil((len(system) + len(prompt)) / 4), math.ceil(len(text) / 4))
