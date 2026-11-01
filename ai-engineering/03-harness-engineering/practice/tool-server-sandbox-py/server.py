# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""An MCP-shaped tool server: JSON-RPC 2.0 over stdio with `initialize`, `tools/list` and
`tools/call`, hand-written so every boundary is visible. A tool failure is a normal result with
`isError: true`, which the model can read and act on. A protocol failure is a JSON-RPC error.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from sandbox import Denied, Policy, jail, run_command


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    handler: Callable[[dict], str]
    write: bool = False  # a write changes the world, so it needs an approver as well as a valid path


def _schema(**props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def make_tools(policy: Policy) -> list[Tool]:
    def read_file(a: dict) -> str:
        text = Path(jail(policy.root, a["path"])).read_text()
        cap = policy.max_output_bytes
        return f"{text[:cap]}\n[truncated: {len(text) - cap} more characters. Narrow your read.]" if len(text) > cap else text

    def write_file(a: dict) -> str:
        target = Path(jail(policy.root, a["path"]))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(a["content"])
        return f"wrote {len(a['content'].encode())} bytes to {a['path']}"

    def command(a: dict) -> str:
        r = run_command(policy, a["command"], a["args"])
        if r.timed_out:
            raise Denied(f"timed out after {int(policy.timeout_s * 1000)} ms")
        return f"{r.stdout}{chr(10) + '[output truncated]' if r.truncated else ''}\n[exit {r.exit_code}]"

    string = {"type": "string"}
    return [
        Tool("read_file", "Read a UTF-8 text file in the workspace. Paths are relative to the workspace root.", _schema(path=string), read_file),
        Tool("list_dir", "List the entries of a workspace folder. Use before read_file when you do not know a name.", _schema(path=string),
             lambda a: "\n".join(sorted(os.listdir(jail(policy.root, a["path"]))))),
        Tool("write_file", "Create or overwrite a workspace file. Requires approval.", _schema(path=string, content=string), write_file, write=True),
        Tool("run_command", f"Run one allowlisted program with arguments. No shell. Allowed: {', '.join(policy.commands)}.",
             _schema(command=string, args={"type": "array", "items": string}), command),
    ]


def validate(tool: Tool, args: Any) -> str | None:
    """Rejects unknown keys and wrong types before a handler runs."""
    if not isinstance(args, dict):
        return "arguments must be an object"
    props = tool.input_schema["properties"]
    for key in tool.input_schema["required"]:
        if key not in args:
            return f"missing argument: {key}"
    for k, v in args.items():
        spec = props.get(k)
        if spec is None:
            return f"unknown argument: {k}"
        if spec["type"] == "array":
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                return f"{k} must be an array of string"
        elif not isinstance(v, str):
            return f"{k} must be a string"
    return None


class Server:
    def __init__(self, policy: Policy, approve: Callable[[str, Any], bool] = lambda n, i: False):
        self.tools = make_tools(policy)
        self.approve = approve
        self.audit: list[dict] = []

    def _log(self, name: str, args: Any, outcome: str) -> None:
        self.audit.append({"tool": name, "input": args, "outcome": outcome})

    def call(self, name: str, args: Any) -> dict:
        def text(t: str, is_error: bool = False) -> dict:
            return {"content": [{"type": "text", "text": t}], **({"isError": True} if is_error else {})}

        tool = next((t for t in self.tools if t.name == name), None)
        if tool is None:
            return text(f"unknown tool: {name}. Available: {', '.join(t.name for t in self.tools)}", True)
        bad = validate(tool, args)
        if bad:
            self._log(name, args, "denied")
            return text(bad, True)
        if tool.write and not self.approve(name, args):
            self._log(name, args, "denied")
            return text("denied: this write needs approval and did not get it. Do not retry it.", True)
        try:
            out = tool.handler(args)
        except Denied as e:
            self._log(name, args, "denied")
            return text(f"denied: {e}", True)
        except OSError as e:
            self._log(name, args, "error")
            return text(f"error: {e.strerror}", True)
        self._log(name, args, "ok")
        return text(out)

    def handle(self, msg: dict) -> dict | None:
        def reply(result: Any) -> dict:
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}

        method, params = msg.get("method"), msg.get("params") or {}
        if method == "initialize":
            return reply({
                "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "tool-server-sandbox", "version": "0.1.0"},
            })
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return reply({"tools": [{"name": t.name, "description": t.description, "inputSchema": t.input_schema} for t in self.tools]})
        if method == "tools/call":
            return reply(self.call(params.get("name"), params.get("arguments", {})))
        if "id" not in msg:
            return None
        return {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": f"method not found: {method}"}}


def default_policy(root: str) -> Policy:
    return Policy(root=root, commands=["ls", "wc", "grep"], timeout_s=2.0, max_output_bytes=4000)


WORKSPACE = str(Path(__file__).parent / "../tool-server-sandbox/workspace")

if __name__ == "__main__":  # serves over stdio: `uv run server.py`. Writes stay denied.
    server = Server(default_policy(WORKSPACE))
    for line in sys.stdin:
        if line.strip():
            out = server.handle(json.loads(line))
            if out:
                print(json.dumps(out), flush=True)
