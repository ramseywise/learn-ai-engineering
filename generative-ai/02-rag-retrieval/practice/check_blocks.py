"""Run every Python block in the pillar's notes and compare it with its printed output.

    uv run --with numpy --with scikit-learn --with faiss-cpu --with duckdb --with pydantic \
        --with opentelemetry-sdk --with fastembed python check_blocks.py [note-prefix ...]

A block whose first lines contain "# illustrative" is skipped: it needs paid APIs or
infrastructure and says which. A ```text fence directly after a block is treated as
that block's output. --write replaces those fences with what the block printed.
"""
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
NOTES = HERE.parent / "notes"
FENCE = re.compile(r"```python\n(.*?)```(\n\s*```text\n(.*?)```)?", re.S)


def run(code: str) -> tuple[int, str, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
    p = subprocess.run([sys.executable, f.name], cwd=HERE, capture_output=True, text=True,
                       timeout=280, env={"PYTHONPATH": str(HERE), "PATH": "/usr/bin:/bin",
                                         "HOME": str(pathlib.Path.home()),
                                         "HF_HUB_DISABLE_PROGRESS_BARS": "1"})
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    args = sys.argv[1:]
    write = "--write" in args
    prefixes = [a for a in args if not a.startswith("--")]
    failures = 0
    for path in sorted(NOTES.glob("*.md")):
        if prefixes and not any(path.name.startswith(p) for p in prefixes):
            continue
        text = path.read_text()
        ran = skipped = 0

        def handle(m: re.Match) -> str:
            nonlocal ran, skipped, failures
            code, tail, expected = m.group(1), m.group(2), m.group(3)
            if "# illustrative" in "\n".join(code.splitlines()[:3]):
                skipped += 1
                return m.group(0)
            ran += 1
            rc, out, err = run(code)
            if rc:
                failures += 1
                print(f"FAIL {path.name} block {ran}: {err.strip().splitlines()[-1] if err.strip() else rc}")
                return m.group(0)
            if tail is None:
                return m.group(0)
            if write:
                return f"```python\n{code}```\n\n```text\n{out.rstrip()}\n```"
            if expected.strip() != out.strip():
                failures += 1
                print(f"DIFF {path.name} block {ran}:\n{out}")
            return m.group(0)

        new = FENCE.sub(handle, text)
        if write and new != text:
            path.write_text(new)
        print(f"{path.name}: ran {ran}, skipped {skipped} illustrative")
    print("failures:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
