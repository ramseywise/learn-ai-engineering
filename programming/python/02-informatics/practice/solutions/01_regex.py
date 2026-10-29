"""01 — Regular expressions. Run: python3 01_regex.py"""

import re

LOG = """\
From stephen.marquard@uct.ac.za Sat Jan  5 09:14:16 2008
X-DSPAM-Confidence: 0.8475
Details: http://source.example.org/viewsvn/?view=rev&rev=39772
From louis@media.berkeley.edu Fri Jan  4 18:10:48 2008
X-DSPAM-Confidence: 0.6178
Received: from murder (mail.umich.edu [141.211.14.90]) by frankenstein.mail.umich.edu
From zqian@umich.edu Fri Jan  4 16:10:39 2008
X-DSPAM-Confidence: 0.6961
"""


def emails(text: str) -> list[str]:
    """Q1. Every email address: non-whitespace, @, non-whitespace; must start and end with a letter."""
    return re.findall(r"[a-zA-Z]\S*@\S*[a-zA-Z]", text)


def confidences(text: str) -> list[float]:
    """Q2. The numbers on 'X-DSPAM-Confidence:' lines, as floats. Use a group and re.MULTILINE."""
    return [float(x) for x in re.findall(r"^X-DSPAM-Confidence: ([0-9.]+)", text, re.MULTILINE)]


def hours(text: str) -> list[str]:
    """Q3. The two-digit hour from each 'From ' line: 'From x Sat Jan  5 09:14:16 2008' -> '09'."""
    return re.findall(r"^From .* (\d\d):\d\d:\d\d", text, re.MULTILINE)


def ip_addresses(text: str) -> list[str]:
    """Q4. Every IPv4 address in square brackets, without the brackets."""
    return re.findall(r"\[(\d{1,3}(?:\.\d{1,3}){3})\]", text)


def query_params(url: str) -> dict[str, str]:
    """Q5. 'http://x/?view=rev&rev=39772' -> {'view': 'rev', 'rev': '39772'} using named groups."""
    return {m["key"]: m["value"] for m in re.finditer(r"[?&](?P<key>\w+)=(?P<value>[^&#]*)", url)}


def tags(html: str) -> list[str]:
    """Q6. Tag names of every opening tag, in order: '<b>hi</b><a href=x>' -> ['b', 'a']. Non-greedy."""
    return [re.match(r"<(\w+)", t).group(1) for t in re.findall(r"<\w.*?>", html)]


if __name__ == "__main__":
    assert emails(LOG) == ["stephen.marquard@uct.ac.za", "louis@media.berkeley.edu", "zqian@umich.edu"]
    assert confidences(LOG) == [0.8475, 0.6178, 0.6961]
    assert hours(LOG) == ["09", "18", "16"]
    assert ip_addresses(LOG) == ["141.211.14.90"]
    assert query_params("http://source.example.org/viewsvn/?view=rev&rev=39772") == {"view": "rev", "rev": "39772"}
    assert tags('<p>Hi <b>there</b>, <a href="x.html">link</a></p>') == ["p", "b", "a"]
    print("all good")
