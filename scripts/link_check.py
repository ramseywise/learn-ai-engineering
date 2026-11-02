#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import urllib.parse

SKIP_DIRS = {
    ".git",
    "node_modules",
    "prompt-eng-for-llms",
}
SKIP_PATHS = {"./.claude/docs"}
SKIP_PREFIXES = ("/oss/", "/use-these-docs", "/langsmith/", "~/", "/guides/")
# The path part of a link; a trailing #anchor is allowed (the file is checked, not the anchor)
link_re = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)")
fence_re = re.compile(r"```.*?```", re.DOTALL)



def git_ignored(paths):
    """The paths git ignores, so private local files under practice/ don't fail the check."""
    if not paths:
        return set()
    out = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(paths), capture_output=True, text=True)
    return set(out.stdout.splitlines())


errors = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    if any(root.startswith(sp) for sp in SKIP_PATHS):
        continue
    markdown = [os.path.join(root, f) for f in files if f.endswith(".md")]
    ignored = git_ignored(markdown)
    for fpath in markdown:
        if fpath in ignored:
            continue
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
