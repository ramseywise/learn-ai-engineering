#!/usr/bin/env python3
"""Check relative links in tracked markdown: the file must exist, and a #anchor into a .md file must
name a heading (or an <a id>/<a name>) in it. Slugs follow GitHub's rule: lowercase, drop punctuation
other than hyphens, each space becomes a hyphen, and a repeated heading gets -1, -2, ..."""
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
# Vendored upstream snapshots: their files are checked, but their anchors are the upstream's to fix
SKIP_ANCHOR_PATHS = ("./data-engineering/03-transform-and-orchestrate/practice/datatalks-de/",)
# A link: optional path part, optional #anchor
link_re = re.compile(r"\[[^\]]*\]\(([^)#]*)(#[^)]*)?\)")
fence_open_re = re.compile(r"^ {0,3}(`{3,}|~{3,})")
heading_re = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)
html_anchor_re = re.compile(r"<a\s+(?:[^>]*\s)?(?:id|name)=[\"']([^\"']+)[\"']", re.IGNORECASE)
inline_link_re = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


def strip_fences(text):
    """Blank out fenced code blocks, line by line. A fence closes only on the same character, at least
    as long as the opener, so a ```` block can quote a ``` one."""
    out, fence = [], None
    for line in text.split("\n"):
        m = fence_open_re.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                out.append("")
                continue
            out.append(line)
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not line.strip()[len(m.group(1)):].strip():
                fence = None
            out.append("")
    return "\n".join(out)


def slug(heading):
    """GitHub's heading slug, before the duplicate suffix."""
    text = inline_link_re.sub(r"\1", heading)
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(text):
    """Every anchor a markdown text defines."""
    found, seen = set(), {}
    for h in heading_re.findall(strip_fences(text)):
        s = slug(h)
        n = seen.get(s, 0)
        found.add(s if n == 0 else f"{s}-{n}")
        seen[s] = n + 1
    found.update(html_anchor_re.findall(text))
    return found


def git_ignored(paths):
    """The paths git ignores, so private local files under practice/ don't fail the check."""
    if not paths:
        return set()
    out = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(paths), capture_output=True, text=True)
    return set(out.stdout.splitlines())


_anchor_cache = {}


def anchors_of(path):
    if path not in _anchor_cache:
        with open(path, encoding="utf-8") as fh:
            _anchor_cache[path] = anchors(fh.read())
    return _anchor_cache[path]


def check_file(fpath, root):
    """Problems in one markdown file, as printable lines."""
    problems = []
    with open(fpath, encoding="utf-8") as fh:
        text = fh.read()
    # Strip fenced code blocks so illustrative links aren't checked
    for m in link_re.finditer(strip_fences(text)):
        link, frag = m.group(1).strip().strip("<>"), m.group(2)
        if link.startswith(("http", "mailto:")) or any(link.startswith(p) for p in SKIP_PREFIXES):
            continue
        if not link and not frag:
            continue
        target = os.path.join(root, urllib.parse.unquote(link)) if link else fpath
        if not os.path.exists(target):
            print_link = link + (frag or "")
            problems.append(f"BROKEN: {fpath} -> {print_link}")
            continue
        if not frag or frag == "#" or not target.endswith(".md") or fpath.startswith(SKIP_ANCHOR_PATHS):
            continue
        anchor = urllib.parse.unquote(frag[1:])
        if anchor.startswith(("L", ":~:")) and re.match(r"^(L\d+(-L\d+)?|:~:.*)$", anchor):
            continue  # GitHub line links and text fragments
        if anchor not in anchors_of(target) and anchor.lower() not in anchors_of(target):
            problems.append(f"BROKEN ANCHOR: {fpath} -> {link}{frag}")
    return problems


def main():
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
                problems = check_file(fpath, root)
            except OSError as exc:
                print(f"SKIPPED: {fpath} -> {exc}")
                continue
            for p in problems:
                print(p)
            errors += len(problems)
    if errors:
        print(f"{errors} broken links found")
        return 1
    print("All links OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
