"""A coding agent harness: read, edit and test inside a throwaway workspace.

The loop has the shape of a Claude tool-use loop, so a real model can replace the
scripted one by providing the same create(messages, tools) method. Every limit lives
in the harness. The model cannot reason its way past any of them.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOY_REPO = HERE / "toy_repo"
HELDOUT = HERE / "heldout"


@dataclass(frozen=True)
class Limits:
    max_steps: int = 20
    test_timeout_s: float = 5.0
    cpu_seconds: int = 5
    max_file_bytes: int = 1_000_000
    max_output_chars: int = 1_200
    repeat_limit: int = 3
    writable: tuple[str, ...] = ("tipkit/",)


class ToolError(Exception):
    """A refused or failed call. The message tells the model what to do next."""


def head_tail(text: str, limit: int) -> str:
    """Keep both ends of long output: the command at the top, the failure at the bottom."""
    if len(text) <= limit:
        return text
    half = limit // 2
    return f"{text[:half]}\n[... {len(text) - limit} characters omitted ...]\n{text[-half:]}"


class Workspace:
    """A temporary copy of the repo, plus the tools that act on it."""

    def __init__(self, limits: Limits, source: Path = TOY_REPO):
        self.limits = limits
        self._tmp = tempfile.TemporaryDirectory(prefix="coding-agent-")
        self.outside = Path(self._tmp.name).resolve()
        self.root = self.outside / "repo"
        shutil.copytree(source, self.root, ignore=shutil.ignore_patterns("__pycache__"))
        self.read_hashes: dict[str, str] = {}
        self.tests_green = False
        self.finished = False

    def close(self) -> None:
        self._tmp.cleanup()

    def _resolve(self, rel: str) -> Path:
        # resolve() follows symlinks, so a link inside the repo cannot point out of it.
        path = (self.root / rel).resolve()
        if not path.is_relative_to(self.root):
            raise ToolError(f"{rel!r} is outside the workspace. Use a path relative to the repo root.")
        return path

    def _rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def tree_digest(self) -> str:
        digest = hashlib.sha256()
        for path in sorted(self.root.rglob("*.py")):
            digest.update(self._rel(path).encode())
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def read_file(self, path: str) -> str:
        target = self._resolve(path)
        if not target.is_file():
            raise ToolError(f"{path!r} does not exist.")
        text = target.read_text()
        self.read_hashes[self._rel(target)] = hashlib.sha256(text.encode()).hexdigest()
        return "\n".join(f"{n:>4}  {line}" for n, line in enumerate(text.splitlines(), 1))

    def edit_file(self, path: str, old: str, new: str) -> str:
        target = self._resolve(path)
        rel = self._rel(target)
        if not rel.startswith(self.limits.writable):
            raise ToolError(f"{rel} is read-only. Fix the code under {self.limits.writable}, not the tests.")
        if rel not in self.read_hashes:
            raise ToolError(f"Read {rel} before editing it.")
        text = target.read_text()
        if hashlib.sha256(text.encode()).hexdigest() != self.read_hashes[rel]:
            del self.read_hashes[rel]
            raise ToolError(f"{rel} changed since you read it. Read it again, then retry the edit.")
        count = text.count(old)
        if count == 0:
            raise ToolError(f"`old` was not found in {rel}. Read the file and copy the text exactly.")
        if count > 1:
            raise ToolError(f"`old` matches {count} places in {rel}. Include more surrounding lines.")
        updated = text.replace(old, new)
        if rel.endswith(".py"):
            try:
                ast.parse(updated)
            except SyntaxError as err:
                raise ToolError(f"Edit discarded, {rel} would not parse: {err.msg} (line {err.lineno}).")
        target.write_text(updated)
        self.read_hashes[rel] = hashlib.sha256(updated.encode()).hexdigest()
        self.tests_green = False
        return f"Edited {rel}. Run the tests to check it."

    def _limit_child(self) -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (self.limits.cpu_seconds, self.limits.cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (self.limits.max_file_bytes, self.limits.max_file_bytes))

    def _unittest(self) -> tuple[int, str]:
        """Run the fixed test command with a clean environment and a wall-clock limit."""
        env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "HOME": str(self.outside)}
        proc = subprocess.Popen(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
            cwd=self.root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            preexec_fn=self._limit_child, start_new_session=True,
        )
        try:
            output, _ = proc.communicate(timeout=self.limits.test_timeout_s)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
            raise ToolError(f"Tests killed after {self.limits.test_timeout_s:g} s. Look for an infinite loop.")
        return proc.returncode, output

    def run_tests(self) -> str:
        code, output = self._unittest()
        self.tests_green = code == 0
        return f"exit={code}\n{head_tail(output, self.limits.max_output_chars)}"

    def finish(self, summary: str) -> str:
        if not self.tests_green:
            raise ToolError("Not finished: the tests have not passed since the last edit. Run them.")
        self.finished = True
        return "Accepted."

    def score_heldout(self) -> tuple[bool, str]:
        """After the run, add tests the agent never saw and run the whole suite."""
        for test in HELDOUT.glob("test_*.py"):
            shutil.copy(test, self.root / "tests" / test.name)
        code, output = self._unittest()
        return code == 0, output.strip().splitlines()[-1]


TOOLS = [
    {"name": "read_file",
     "description": "Read a text file from the repo, with line numbers. Paths are relative to the repo root.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["path"],
                      "properties": {"path": {"type": "string"}}}},
    {"name": "edit_file",
     "description": "Replace one exact, unique string in a file you have read. Only code under tipkit/ is writable.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["path", "old", "new"],
                      "properties": {"path": {"type": "string"}, "old": {"type": "string"},
                                     "new": {"type": "string"}}}},
    {"name": "run_tests",
     "description": "Run the repo's unit tests. Takes no arguments. Returns the exit code and output.",
     "input_schema": {"type": "object", "additionalProperties": False, "properties": {}}},
    {"name": "finish",
     "description": "End the task with a summary. Refused unless the tests pass after your last edit.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["summary"],
                      "properties": {"summary": {"type": "string"}}}},
]


# The model can only reach what is named here: no shell, and no private harness methods.
TOOL_NAMES = {tool["name"] for tool in TOOLS}


@dataclass
class Result:
    status: str
    steps: int
    refused: int = 0
    log: list[dict] = field(default_factory=list)


def fingerprint(name: str, args: dict, workspace: Workspace) -> str:
    # The tree digest is part of the key: re-running tests after an edit is progress,
    # re-running them against identical files is a loop.
    payload = json.dumps([name, args, workspace.tree_digest()], sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()


def run_agent(model, workspace: Workspace, task: str, trace=print) -> Result:
    limits = workspace.limits
    messages = [{"role": "user", "content": task}]
    seen: dict[str, int] = {}
    result = Result(status="step_limit", steps=0)

    for step in range(1, limits.max_steps + 1):
        result.steps = step
        response = model.create(messages=messages, tools=TOOLS)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            # A model that stops talking has not proved anything.
            result.status = f"stopped_without_finish:{response.stop_reason}"
            return result

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            key = fingerprint(block.name, block.input, workspace)
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > limits.repeat_limit:
                # Text can be ignored, a halt cannot. See the first warning below.
                trace(f"{step:>2}  {block.name}  HALT: same call on unchanged files, {seen[key]} times")
                result.status = "halted_repeat"
                return result
            try:
                if seen[key] == limits.repeat_limit:
                    raise ToolError("You have made this same call on unchanged files repeatedly. Change approach.")
                if block.name not in TOOL_NAMES:
                    raise ToolError(f"There is no tool called {block.name}. You have: {sorted(TOOL_NAMES)}.")
                output, is_error = getattr(workspace, block.name)(**block.input), False
            except (ToolError, TypeError) as err:
                output, is_error = str(err), True
                result.refused += 1
            label = "REFUSED" if is_error else "ok"
            first_line = output.splitlines()[0] if output else ""
            trace(f"{step:>2}  {block.name}  {label}: {first_line[:88]}")
            result.log.append({"tool": block.name, "input": block.input, "is_error": is_error, "output": output})
            tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                 "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": tool_results})
        if workspace.finished:
            result.status = "finished"
            return result
    return result
