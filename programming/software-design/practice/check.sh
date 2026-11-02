#!/usr/bin/env bash
# Run the lab's tests and report ok / FAIL.
#   bash check.sh              # the worked solution: every step
#   bash check.sh exercises    # your copy of the module, against its characterization tests
set -uo pipefail
cd "$(dirname "$0")"
side=${1:-solutions}
fail=0
for d in "$side"/*/; do
  [ -f "$d/pyproject.toml" ] || continue
  if out=$(cd "$d" && uv run --quiet pytest -q 2>&1); then
    printf 'ok    %s  (%s)\n' "$d" "$(tail -1 <<<"$out")"
  else
    printf 'FAIL  %s  (%s)\n' "$d" "$(tail -1 <<<"$out")"; fail=1
  fi
done
find . \( -name __pycache__ -o -name .pytest_cache -o -name .venv \) -prune -exec rm -rf {} +
exit $fail
