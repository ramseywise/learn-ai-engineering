"""Run every Python block in the notes as written and compare it to its printed output.

Each ```python block runs in a fresh process with cwd=practice/. A ```text fence directly
after a block is that block's expected output. Blocks marked `# illustrative` need a paid key
in real life; here they run against the local fakes, so their logic and request shapes are
tested, and they carry no output fence because a fake's reply is not a result.

  python check_blocks.py            check, exit 1 on any difference
  python check_blocks.py --write    fill in the output fences
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from support_agent.fakes import serve

HERE = Path(__file__).parent
FENCE = re.compile(r"```python\n(.*?)```\n(\n```text\n(.*?)```\n)?", re.S)


def run(code, env):
    return subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=120)


def main():
    write = "--write" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    failures = 0
    with serve() as url:
        env = {**os.environ, "PYTHONPATH": str(HERE), "ANTHROPIC_BASE_URL": url, "ANTHROPIC_API_KEY": "local",
               "LANGFUSE_BASE_URL": url, "LANGFUSE_PUBLIC_KEY": "pk-lf-local", "LANGFUSE_SECRET_KEY": "sk-lf-local"}
        for path in sorted((HERE.parent / "notes").glob("*.md")):
            if only and not any(o in path.name for o in only):
                continue
            text = path.read_text()
            count = [0]

            def visit(m):
                nonlocal failures
                count[0] += 1
                code, expected = m.group(1), m.group(3)
                illustrative = "# illustrative" in code
                r = run(code, env)
                label = f"{path.name} block {count[0]}"
                if r.returncode != 0:
                    failures += 1
                    print(f"FAIL {label}\n{r.stderr[-1500:]}")
                    return m.group(0)
                if illustrative:
                    print(f"ok (illustrative, against fakes) {label}")
                    return f"```python\n{code}```\n"
                if write:
                    print(f"ok {label}")
                    return f"```python\n{code}```\n" + (f"\n```text\n{r.stdout}```\n" if r.stdout else "")
                if (expected or "") != r.stdout:
                    failures += 1
                    print(f"DIFF {label}\n--- expected\n{expected}\n--- got\n{r.stdout}")
                else:
                    print(f"ok {label}")
                return m.group(0)

            new = FENCE.sub(visit, text)
            if write and new != text:
                path.write_text(new)
    print("failures:", failures)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
