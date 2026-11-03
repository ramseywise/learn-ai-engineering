#!/usr/bin/env bash
# Run the lab's tests, every code block in the chapters, and the deploy example.
#   bash check.sh              # the worked solution, the chapters' blocks, then deploy/verify.sh
#   bash check.sh exercises    # your copy of the lab. It fails until you've written it
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
if [ "$side" = solutions ]; then
  uv run --quiet --no-project --python 3.14 python run_notes.py || fail=1
  if docker info >/dev/null 2>&1; then
    if out=$(bash deploy/verify.sh 2>&1); then
      printf '%s\n' "$out"
    else
      printf '%s\nFAIL  deploy/verify.sh\n' "$out"; fail=1
    fi
  else
    echo "skip  deploy/verify.sh  (no Docker daemon; manifests and image not checked)"
  fi
fi
find . \( -name __pycache__ -o -name .pytest_cache -o -name .venv \) -prune -exec rm -rf {} +
exit $fail
