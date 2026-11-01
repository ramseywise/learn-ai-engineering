# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from sandbox import Denied, Policy, jail, run_command
from server import Server


def raises(fn, exc=Denied) -> bool:
    try:
        fn()
    except exc:
        return True
    return False


tmp = tempfile.TemporaryDirectory()
root = Path(tmp.name, "sandbox")
outside = Path(tmp.name, "outside")
root.mkdir(), outside.mkdir()
(outside / "secret.txt").write_text("secret")
(root / "a.txt").write_text("hello\n")
(root / "sub").mkdir()
(root / "link").symlink_to(outside)
r = str(root)

# The jail
assert raises(lambda: jail(r, "../x"))
assert raises(lambda: jail(r, "/etc/passwd"))
assert raises(lambda: jail(r, "link/secret.txt")), "symlink to outside"
assert raises(lambda: jail(r, "link/new.txt")), "new file through a symlinked folder"
assert raises(lambda: jail(r, f"../{root.name}-evil/x")), "sibling sharing the prefix"
assert jail(r, "sub/new.txt").endswith(os.path.join("sub", "new.txt"))

policy = Policy(r, ["ls", "sleep", "yes", "env"], 0.3, 1000)

# Execution limits
assert raises(lambda: run_command(policy, "curl", []))
assert run_command(policy, "sleep", ["5"]).timed_out, "slow command is killed"
noisy = run_command(policy, "yes", [])
assert noisy.truncated and len(noisy.stdout) <= 1000, "output is capped"
os.environ["LAB_SECRET"] = "hunter2"
assert "hunter2" not in run_command(policy, "env", []).stdout, "environment is scrubbed"
assert run_command(policy, "ls", ["; touch pwned"]).exit_code != 0
assert not (root / "pwned").exists(), "metacharacters are plain text"

# Tool results
deny_all = Server(policy)
assert deny_all.call("write_file", {"path": "b.txt", "content": "x"}).get("isError")
assert not (root / "b.txt").exists(), "denied write left no file"
allow = Server(policy, lambda n, i: True)
assert not allow.call("write_file", {"path": "sub/b.txt", "content": "x"}).get("isError")
assert (root / "sub/b.txt").read_text() == "x"
assert allow.call("write_file", {"path": "link/x", "content": "x"}).get("isError"), "approval does not bypass the jail"
assert deny_all.call("read_file", {"path": "a.txt", "extra": 1}).get("isError")
assert deny_all.call("read_file", {"path": 7}).get("isError")
assert any(e["outcome"] == "denied" for e in deny_all.audit)

# The wire protocol, end to end against a child process
here = Path(__file__).parent
msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "docs/refunds.txt"}}},
    {"jsonrpc": "2.0", "id": 4, "method": "no/such"},
]
done = subprocess.run([sys.executable, "server.py"], cwd=here, input="\n".join(map(json.dumps, msgs)) + "\n", capture_output=True, text=True, timeout=20)
replies = [json.loads(l) for l in done.stdout.splitlines()]
assert replies[0]["result"]["serverInfo"]["name"] == "tool-server-sandbox"
assert len(replies[1]["result"]["tools"]) == 4
assert "30 days" in replies[2]["result"]["content"][0]["text"]
assert replies[3]["error"]["code"] == -32601

tmp.cleanup()
print("ok: all assertions passed")
