#!/usr/bin/env python3
import os
import re
import sys
import urllib.parse

SKIP_DIRS = {
    ".git", "node_modules", "Context-Engineering-main",
    "DataTalks Data Engineering", "DataTalks MLOps",
}
SKIP_PATHS = {"./.claude/docs"}
SKIP_PREFIXES = ("/oss/", "/use-these-docs", "/langsmith/")
link_re = re.compile(r"\[[^\]]*\]\(([^)#]+)\)")

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
            text = open(fpath).read()
        except Exception:
            continue
        for m in link_re.finditer(text):
            link = m.group(1)
            if link.startswith("http") or any(link.startswith(p) for p in SKIP_PREFIXES):
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
