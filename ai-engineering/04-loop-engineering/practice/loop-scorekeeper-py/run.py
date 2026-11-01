# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Same checks, makers and stop reasons as the TypeScript lab in ../loop-scorekeeper, in Python."""
import os
from dataclasses import replace

from loop import Limits, Result, run_loop
from model import choose_model
from stub import gamer, honest, overfit, stuck

limits = Limits()


def report(name: str, r: Result) -> None:
    print(f"\n--- {name}: stop={r.stop}, {len(r.iterations)} iterations, {r.tokens} tokens, shippable={'true' if r.best else 'false'}")
    for i in r.iterations:
        print(f"  #{i.n}  visible {i.visible.passed}/{i.visible.total}   held-out {i.held_out.passed}/{i.held_out.total}")


if os.environ.get("MODEL"):
    name, complete = choose_model(honest())
    report(name, run_loop(complete, replace(limits, max_tokens=60000)))
else:
    report("honest maker", run_loop(honest(), limits))
    report("maker memorises the visible checks", run_loop(gamer(), limits))
    report("ordinary overfit", run_loop(overfit(), limits))
    report("stuck maker", run_loop(stuck(), limits))
    report("expensive maker", run_loop(honest(), replace(limits, max_tokens=150)))
