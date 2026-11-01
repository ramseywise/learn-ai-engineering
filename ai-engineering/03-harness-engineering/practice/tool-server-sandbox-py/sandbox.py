from __future__ import annotations

import os
import subprocess
import threading
from dataclasses import dataclass


class Denied(Exception):
    """Refused by policy. Returned to the model as a tool error, so it can adapt."""


@dataclass
class Policy:
    root: str
    commands: list[str]
    timeout_s: float
    max_output_bytes: int


def jail(root: str, requested: str) -> str:
    """Resolves a path inside the jail. realpath follows symlinks, so one pointing out of the root
    is caught, and a new file under a linked folder is too. A prefix check on the raw string catches
    neither."""
    real_root = os.path.realpath(root)
    real = os.path.realpath(os.path.join(real_root, requested))
    if real != real_root and not real.startswith(real_root + os.sep):
        raise Denied(f"path escapes the workspace: {requested}")
    return real


@dataclass
class RunResult:
    stdout: str
    exit_code: int | None
    timed_out: bool
    truncated: bool


def run_command(p: Policy, command: str, args: list[str]) -> RunResult:
    """Runs an allowlisted binary with an argv list and no shell, so `;`, `|` and `$()` are plain
    text. The environment is scrubbed: a child cannot read the API key it was never given.
    This is a teaching boundary and not a security product. See the README for what it misses."""
    if command not in p.commands:
        raise Denied(f"command not allowed: {command}")
    child = subprocess.Popen(
        [command, *args],
        cwd=os.path.realpath(p.root),
        env={"PATH": os.environ.get("PATH", "")},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    out = bytearray()
    truncated = threading.Event()

    def drain() -> None:  # keeps reading past the cap so a noisy child cannot block on a full pipe
        for chunk in iter(lambda: child.stdout.read(4096), b""):
            room = p.max_output_bytes - len(out)
            if len(chunk) > room:
                truncated.set()
            out.extend(chunk[: max(room, 0)])

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    timed_out = False
    try:
        child.wait(timeout=p.timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        child.wait()
    reader.join(timeout=1)
    return RunResult(out.decode("utf8", "replace"), child.returncode, timed_out, truncated.is_set())
