"""Tiny mutation tester: flip one operator at a time and see whether the tests notice.

Usage:  cd exercises/usage_report_lab && uv run python ../../mutate.py

Each mutant changes one comparison, arithmetic operator or boolean connective in
report-producing code, then runs the lab's tests. A survivor is a changed program that
every test still accepts. Real tools (mutmut, cosmic-ray) have many more operators.
"""
import ast
import copy
import subprocess
import sys
from pathlib import Path

SWAPS = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Add: ast.Sub, ast.Sub: ast.Add,
    ast.Mult: ast.Div, ast.Div: ast.Mult, ast.And: ast.Or, ast.Or: ast.And,
}


def mutation_points(tree: ast.Module) -> list[tuple[int, str]]:
    """(index among walk order, kind) for every operator we know how to swap."""
    points = []
    for index, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and type(node.ops[0]) in SWAPS:
            points.append((index, "compare"))
        elif isinstance(node, (ast.BinOp, ast.BoolOp)) and type(node.op) in SWAPS:
            points.append((index, "op"))
    return points


def mutated(tree: ast.Module, index: int) -> tuple[str, int, str]:
    clone = copy.deepcopy(tree)
    node = list(ast.walk(clone))[index]
    if isinstance(node, ast.Compare):
        before = node.ops[0]
        node.ops[0] = SWAPS[type(before)]()
        after = node.ops[0]
    else:
        before = node.op
        node.op = SWAPS[type(before)]()
        after = node.op
    return ast.unparse(clone), node.lineno, f"{type(before).__name__} -> {type(after).__name__}"


def tests_pass() -> bool:
    run = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider"],
                         capture_output=True, timeout=120)
    return run.returncode == 0


def main() -> None:
    target = Path("usage_report.py")
    original = target.read_text()
    tree = ast.parse(original)
    points = mutation_points(tree)
    survivors = []
    if not tests_pass():
        raise SystemExit("the tests fail before any mutation; a kill would mean nothing")
    try:
        for index, _ in points:
            source, line, change = mutated(tree, index)
            target.write_text(source)
            if tests_pass():
                survivors.append((line, change))
    finally:
        target.write_text(original)
    print(f"{len(points)} mutants, {len(points) - len(survivors)} killed, {len(survivors)} survived")
    lines = original.splitlines()
    for line, change in sorted(survivors):
        print(f"  line {line}: {change}: {lines[line - 1].strip()}")


if __name__ == "__main__":
    main()
