"""Record what usage_report.py does today, bugs included, into golden.json.

Run this once, against the code as you found it. Rerunning it after you start
refactoring would bless whatever you broke.
"""
import contextlib
import importlib
import io
import itertools
import json
import pathlib
import tempfile

HERE = pathlib.Path(__file__).parent


def observe(module_name, path, **flags):
    """Everything a caller can see from one fresh call: stdout, return value, file."""
    module = importlib.import_module(module_name)
    module = importlib.reload(module)  # fresh globals, as in a new process
    with tempfile.TemporaryDirectory() as tmp:
        module.OUT = str(pathlib.Path(tmp) / "report_out.txt")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = module.report(str(path), **flags)
        written = pathlib.Path(module.OUT)
        return {
            "stdout": out.getvalue(),
            "returned": result,
            "file": written.read_text() if written.exists() else None,
        }


def grid():
    for mode, show_cost, write, dedupe in itertools.product(
        ("full", "summary"), (True, False), (True, False), (True, False)
    ):
        yield {"mode": mode, "show_cost": show_cost, "write": write, "dedupe": dedupe}


if __name__ == "__main__":
    golden = {json.dumps(f, sort_keys=True): observe("usage_report", HERE / "calls.jsonl", **f) for f in grid()}
    (HERE / "golden.json").write_text(json.dumps(golden, indent=1, sort_keys=True) + "\n")
    print(f"recorded {len(golden)} cases")
