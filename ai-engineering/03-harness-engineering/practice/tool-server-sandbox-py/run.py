# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Same workspace, plan and report as the TypeScript lab in ../tool-server-sandbox."""
import json
import os
import sys

from agent import run_claude, run_scripted
from server import WORKSPACE, Server, default_policy

server = Server(default_policy(WORKSPACE))  # the approver denies every write

if os.environ.get("MODEL"):
    task = sys.argv[1] if len(sys.argv) > 1 else "How long is the refund window? Look in docs/ and cite the file."
    print(run_claude(server, os.environ["MODEL"], task))
else:
    run_scripted(server, [
        {"why": "discover", "name": "list_dir", "input": {"path": "docs"}},
        {"why": "do the job", "name": "read_file", "input": {"path": "docs/refunds.txt"}},
        {"why": "allowed program, no shell", "name": "run_command", "input": {"command": "grep", "args": ["-l", "refund", "docs/refunds.txt"]}},
        {"why": "attack: path traversal", "name": "read_file", "input": {"path": "../../../../../../etc/passwd"}},
        {"why": "attack: absolute path", "name": "read_file", "input": {"path": "/etc/passwd"}},
        {"why": "attack: program outside allowlist", "name": "run_command", "input": {"command": "curl", "args": ["https://example.com"]}},
        {"why": "attack: shell metacharacters", "name": "run_command", "input": {"command": "ls", "args": ["; cat /etc/passwd"]}},
        {"why": "attack: write with no approval", "name": "write_file", "input": {"path": "docs/refunds.txt", "content": "Refunds: forever."}},
        {"why": "bad call: unknown argument", "name": "read_file", "input": {"path": "docs/seats.txt", "encoding": "latin1"}},
        {"why": "bad call: unknown tool", "name": "delete_file", "input": {"path": "docs/seats.txt"}},
    ])
    counts: dict[str, int] = {}
    for e in server.audit:
        counts[e["outcome"]] = counts.get(e["outcome"], 0) + 1
    print(f"\naudit log: {json.dumps(counts, separators=(',', ':'))} (an unknown tool is rejected before the log)")
