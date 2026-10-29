#!/usr/bin/env bash
# Run every file in solutions/ (or exercises/ with: bash check.sh exercises) and report errors.
set -uo pipefail
cd "$(dirname "$0")"
dir="${1:-solutions}"
[ -f data/clubdata.db ] || bash setup.sh
fail=0
for f in "$dir"/*.sql; do
  [ -e "$f" ] || continue
  case "$f" in
    *07-*) db=":memory:" ;;   # DDL module works on a throwaway in-memory copy
    *)     db="data/survey.db" ;;
  esac
  if out=$(sqlite3 -bail "$db" < "$f" 2>&1 >/dev/null) && [ -z "$out" ]; then
    echo "ok    $f"
  else
    echo "FAIL  $f: $out"; fail=1
  fi
done
for f in "$dir"/*.py; do
  [ -e "$f" ] || continue
  if python3 "$f" >/dev/null 2>&1; then echo "ok    $f"; else echo "FAIL  $f"; fail=1; fi
done
exit $fail
