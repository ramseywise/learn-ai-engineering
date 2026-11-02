#!/usr/bin/env bash
# Run the lab's tests and every code block in the chapters, and report ok / FAIL.
#   bash check.sh              # the worked solution, then the chapters' code blocks
#   bash check.sh exercises    # your copy of the lab. It fails until you've written it
#   bash check.sh network      # as the first, plus the blocks that need the internet
set -uo pipefail
cd "$(dirname "$0")"
mode=${1:-solutions}
side=$mode
[ "$mode" = network ] && side=solutions
fail=0
for d in "$side"/*/; do
  [ -f "$d/pyproject.toml" ] || continue
  if out=$(cd "$d" && uv run --quiet pytest -q 2>&1); then
    printf 'ok    %s  (%s)\n' "$d" "$(tail -1 <<<"$out")"
  else
    printf 'FAIL  %s  (%s)\n' "$d" "$(tail -1 <<<"$out")"; fail=1
  fi
done
if [ "$side" = solutions ]; then
  flags=()
  [ "$mode" = network ] && flags+=(--network)
  uv run --quiet --no-project --python 3.14 python run_notes.py ${flags[@]+"${flags[@]}"} || fail=1
fi
find . \( -name __pycache__ -o -name .pytest_cache -o -name .venv \) -prune -exec rm -rf {} +
exit $fail
