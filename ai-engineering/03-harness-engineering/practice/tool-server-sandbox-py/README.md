# Lab: a tool server with sandboxing (Python)

The Python twin of the [TypeScript lab](../tool-server-sandbox/README.md). It serves the same
`workspace/` from that folder, with the same tools, policy and scripted plan. Read the TypeScript
README for why the lab exists, what this boundary does not stop, and the exercises.

```bash
uv run run.py      # a scripted agent does its job, then tries each attack
uv run test.py     # the assertions, including a symlink escape and the stdio protocol
uv run server.py   # serve over stdio; send it one JSON-RPC message per line
```

Real output with the scripted agent, identical to the TypeScript version:

```text
ok       discover                               refunds.txt seats.txt
ok       do the job                             Refunds: annual plans can be refunded within 30 days of renewal.
ok       allowed program, no shell              docs/refunds.txt [exit 0]
BLOCKED  attack: path traversal                 denied: path escapes the workspace: ../../../../../../etc/passwd
BLOCKED  attack: absolute path                  denied: path escapes the workspace: /etc/passwd
BLOCKED  attack: program outside allowlist      denied: command not allowed: curl
ok       attack: shell metacharacters           ls: ; cat /etc/passwd: No such file or directory [exit 1]
BLOCKED  attack: write with no approval         denied: this write needs approval and did not get it. Do not retry it.
BLOCKED  bad call: unknown argument             unknown argument: encoding
BLOCKED  bad call: unknown tool                 unknown tool: delete_file. Available: read_file, list_dir, write_file,

audit log: {"ok":4,"denied":5} (an unknown tool is rejected before the log)
```

## Swap in a real model

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 uv run --with anthropic run.py "How long is the refund window? Look in docs/ and cite the file."
```

`agent.py` holds a manual tool loop capped at 8 turns. For real MCP clients, register the same
handlers with the official `mcp` Python SDK and keep `sandbox.py` as it is.
