"""Load a step by file name with fresh globals, and observe one call to it."""
import contextlib
import importlib.util
import io
import itertools
import pathlib
import tempfile

HERE = pathlib.Path(__file__).parent
STEPS = HERE / "steps"
CALLS = HERE / "calls.jsonl"


def load(step):
    spec = importlib.util.spec_from_file_location(step, STEPS / f"{step}.py")
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[step] = module  # dataclasses look the module up by name
    spec.loader.exec_module(module)
    return module


def observe(step, path=CALLS, **flags):
    module = load(step)
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
