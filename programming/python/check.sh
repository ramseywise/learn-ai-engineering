#!/usr/bin/env bash
# Run every practice file in Python 01–03 and report ok / FAIL.
#   bash check.sh              # your exercises (unsolved ones fail with NotImplementedError)
#   bash check.sh solutions    # the worked answers: all must pass
#   bash check.sh exercises 03 # one module
set -uo pipefail
cd "$(dirname "$0")"
side=${1:-exercises}
module=${2:-}
pass=0 fail=0

for f in 0${module#0}*/practice/"$side"/*.py; do
  [ -e "$f" ] || continue
  if out=$(python3 "$f" 2>&1) && [[ $out == *"all good"* ]]; then
    printf 'ok    %s\n' "$f"; pass=$((pass + 1))
  else
    printf 'FAIL  %s  (%s)\n' "$f" "$(tail -1 <<<"$out")"; fail=$((fail + 1))
  fi
done

for d in 0${module#0}*/practice/"$side"/*/; do
  [ -f "$d/pyproject.toml" ] || continue
  if out=$(cd "$d" && uv run --quiet pytest -q 2>&1); then
    printf 'ok    %s (pytest)\n' "$d"; pass=$((pass + 1))
  else
    printf 'FAIL  %s (pytest: %s)\n' "$d" "$(tail -1 <<<"$out")"; fail=$((fail + 1))
  fi
done

find . \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
