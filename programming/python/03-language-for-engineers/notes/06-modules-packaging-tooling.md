---
origin: curated
sources:
  - "Jake VanderPlas, A Whirlwind Tour of Python, ch. 13 — https://github.com/jakevdp/WhirlwindTourOfPython (CC0)"
  - "uv docs — https://docs.astral.sh/uv/"
  - "Ruff docs — https://docs.astral.sh/ruff/"
  - "pytest docs — https://docs.pytest.org/"
concepts: [python-modules, python-packaging, uv, ruff, pytest, pyproject]
cleaned: 2026-10-29
---
# 6 — Modules, packaging and tooling

> A modern Python project is a `pyproject.toml`, a `src/` folder, `tests/`, and three tools: **uv** for environments and dependencies, **ruff** for lint and format, **pytest** for tests.

---

## Modules and imports

- A **module** is a `.py` file. A **package** is a folder of modules (with an `__init__.py`).
- `import pkg.mod` runs the module once and caches it in `sys.modules`. Later imports reuse it.
- `if __name__ == "__main__":` guards code that should run only when the file is executed, not when it is imported. Every practice file in this course uses it.
- Avoid `from x import *`. Avoid naming your file after a stdlib module (`json.py`, `random.py`): it shadows the real one.
- Python finds modules via `sys.path`, which starts with the script's directory. "Works when I run it from here" bugs come from that. Install your project (`uv sync` does this) instead of editing `sys.path`.

## Project layout

```text
my-tool/
├── pyproject.toml
├── src/my_tool/
│   ├── __init__.py
│   └── core.py
└── tests/
    └── test_core.py
```

```toml
[project]
name = "my-tool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27"]

[project.scripts]
my-tool = "my_tool.core:main"

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

## uv

```bash
uv init my-tool --package       # scaffold the layout above
uv add httpx                    # add a dependency, update uv.lock
uv add --dev pytest             # dev-only dependency
uv run pytest                   # run inside the project env (creates it if needed)
uv run python -m my_tool.core
uvx ruff check .                # run a tool without installing it into the project
uv python install 3.13          # manage Python versions too
```

Commit `uv.lock`. It pins every transitive version, so CI and teammates get the same environment.

## ruff and pytest

```bash
uv run ruff check --fix .       # lint (replaces flake8, isort, pyupgrade…)
uv run ruff format .            # format (replaces black)
uv run pytest -q                # run tests
uv run pytest -k parse -x       # only tests matching "parse", stop at first failure
```

```python
# tests/test_core.py
import pytest
from my_tool.core import parse_price

@pytest.mark.parametrize("raw, expected", [("$1.50", 1.5), ("2", 2.0)])
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected

def test_parse_price_rejects_garbage():
    with pytest.raises(ValueError, match="price"):
        parse_price("abc")

def test_writes_file(tmp_path):            # fixtures are injected by name
    out = tmp_path / "out.csv"
    ...
```

Plain `assert` is enough. pytest rewrites it to show both sides on failure. `tmp_path`, `monkeypatch` and `capsys` are the built-in fixtures you'll use most.

---

## Exercises

[`practice/exercises/06_tooling/`](../practice/exercises/06_tooling/) is a tiny package with failing tests. Make `uv run pytest` green and `uvx ruff check` clean.
