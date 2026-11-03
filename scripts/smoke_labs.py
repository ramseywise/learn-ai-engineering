#!/usr/bin/env python3
"""Run a practice folder's labs headless, each with a time limit, and report which ones fail.

Each lab runs with `uv run --script` in a temporary copy of the folder, so charts and other output files never touch
the working tree. MPLBACKEND=Agg stops matplotlib opening windows.

    make da06-smoke
    python3 scripts/smoke_labs.py data-analytics/06-applied-analyses/practice --pattern 'ch[0-9]*.py' --timeout 600
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Result:
    lab: str
    status: str  # ok, FAILED or TIMEOUT
    seconds: float
    tail: str = ""


def run_lab(lab: str, cmd: list[str], cwd: Path, timeout: float) -> Result:
    """Run one command in its own process group, so a timeout also kills anything it started."""
    env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONUNBUFFERED": "1"}
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        return Result(lab, "TIMEOUT", time.monotonic() - start, "\n".join((out or "").splitlines()[-8:]))
    status = "ok" if proc.returncode == 0 else "FAILED"
    tail = "" if status == "ok" else "\n".join(out.splitlines()[-8:])
    return Result(lab, status, time.monotonic() - start, tail)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--pattern", default="*.py")
    ap.add_argument("--timeout", type=float, default=600, help="seconds allowed for each lab")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--offline", action="store_true", help="use only packages already in uv's cache")
    args = ap.parse_args()

    labs = sorted(p.name for p in args.folder.glob(args.pattern))
    if not labs:
        print(f"no labs match {args.pattern} in {args.folder}")
        return 2
    uv = ["uv", "run", *(["--offline"] if args.offline else []), "--script"]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "labs"
        shutil.copytree(args.folder, work, ignore=shutil.ignore_patterns("__pycache__"))
        with ThreadPoolExecutor(args.jobs) as pool:
            results = list(pool.map(lambda lab: run_lab(lab, [*uv, lab], work, args.timeout), labs))

    for r in results:
        print(f"{r.status:8} {r.seconds:7.1f}s  {r.lab}")
        if r.tail:
            print("\n".join("    " + line for line in r.tail.splitlines()))
    failed = [r for r in results if r.status != "ok"]
    print(f"{len(results) - len(failed)} of {len(results)} labs passed, limit {args.timeout:.0f}s each")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
