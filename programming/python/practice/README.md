# Running the Python exercises

How the track's exercises are laid out, run and checked. What to do after which note is in the [syllabus](../README.md#syllabus).

## Layout

```
python/
├── README.md
├── check.sh                      ok / FAIL for every exercise or solution file; runs pytest for 06_tooling
├── 01-foundations/
│   ├── notes/                    01–05
│   ├── slides/                   deck.yaml and the built deck
│   └── practice/
│       ├── exercises/            01_…05_.py, stubs with the asserts at the bottom
│       └── solutions/            same names, worked
├── 02-informatics/               same shape, notes and exercises 01–05
└── 03-language-for-engineers/    same shape, notes 01–09; 06_tooling/ is a uv package (pyproject.toml, src/, tests/); 09 has no practice file
```

## Run it

```bash
cd programming/python
python3 --version                         # 3.12+ (the course is tested on 3.14)
python3 01-foundations/practice/exercises/01_values_and_conditionals.py
bash check.sh                             # ok / FAIL for every exercise
bash check.sh exercises 03                # one module
bash check.sh solutions                   # every worked answer must pass
```

01–03 need only the standard library. 03 · 06 is a small package run with [uv](https://docs.astral.sh/uv/)
(`uv run pytest`), which installs pytest and ruff for you. The scientific stack belongs to the
[next pillar](../../../data-analytics/01-python-for-data-analysis/README.md), and its practice README has the setup.

## How exercises work

Every exercise file is a set of functions (or classes) whose docstrings start with `Q1.`, `Q2.` …
and whose bodies are `raise NotImplementedError`. The bottom of each file is a block of `assert`s
under `if __name__ == "__main__":`. Run the file: it stops at the first unsolved question, and it
prints `all good` once everything passes. Note 03 · 08 has one (`08_objects_mro.py`, from its Try it); 03 · 09 keeps its Try it in the note because the results depend on the machine. Exercises run offline. The HTTP exercise starts its own
local server, and the concurrency exercise simulates the network with sleeps.

## Drills

Timed and interview-style Python problems are in [`programming/drills/`](../../drills/README.md). The [advanced Python](../../drills/python/advanced/README.md) concept list covers the same ground as steps 3 to 5 of the syllabus.
