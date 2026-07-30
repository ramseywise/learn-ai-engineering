#!/usr/bin/env python3
import os
import re
import sys
import urllib.parse

SKIP_DIRS = {
    ".git",
    "node_modules",
    "idk",
    "Context-Engineering-main",
    "DataTalks Data Engineering",
    "DataTalks MLOps",
    "Prompt-Engineering-Guide-main",
    "prompt-eng-for-llms",
    "Evaluating-AI-Agents-master",
    "evaluation",
}
SKIP_PATHS = {"./.claude/docs"}
SKIP_PREFIXES = ("/oss/", "/use-these-docs", "/langsmith/", "~/", "/guides/")
link_re = re.compile(r"\[[^\]]*\]\(([^)#]+)\)")
fence_re = re.compile(r"```.*?```", re.DOTALL)

errors = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    if any(root.startswith(sp) for sp in SKIP_PATHS):
        continue
    for fname in files:
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"SKIPPED: {fpath} -> {exc}")
            continue
        # Strip fenced code blocks so illustrative links aren't checked
        text_no_fences = fence_re.sub("", text)
        for m in link_re.finditer(text_no_fences):
            link = m.group(1)
            if link.startswith("http") or any(
                link.startswith(p) for p in SKIP_PREFIXES
            ):
                continue
            link = link.strip("<>")
            target = os.path.join(root, urllib.parse.unquote(link))
            if not os.path.exists(target):
                print(f"BROKEN: {fpath} -> {link}")
                errors += 1

if errors:
    print(f"{errors} broken links found")
    sys.exit(1)
else:
    print("All links OK")
