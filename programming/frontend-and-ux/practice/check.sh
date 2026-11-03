#!/usr/bin/env bash
# Runs the lab. Needs Node 22.18+ and a Chromium that Playwright can find. No API key.
#
#   bash check.sh              the worked solutions: everything
#   bash check.sh exercises    your copy; fails until you have written it
#   bash check.sh no-browser   skips everything that needs Chromium, and says so
#
# First run: npm ci happens by itself. For the browser: npx playwright-core install chromium
#
# What a pass means: the behaviours tested below hold in headless Chromium and axe
# finds no violation in the states it looked at. It does not mean the page works in
# Safari or Firefox or with a screen reader, because none of those is run here.
set -uo pipefail
cd "$(dirname "$0")"

side=${1:-solutions}
browser=yes
if [ "$side" = "no-browser" ]; then side=solutions; browser=no; fi
export TARGET=$side
fail=0

report() { # name status summary
  if [ "$2" -eq 0 ]; then printf 'ok    %-22s (%s)\n' "$1" "$3"
  else printf 'FAIL  %-22s (%s)\n' "$1" "$3"; fail=1; fi
}
counts() { # tap output -> "N of M tests pass"
  awk '/^# tests /{t=$3} /^# pass /{p=$3} END{printf "%s of %s tests pass", p+0, t+0}' "$1"
}

major=$(node -p 'process.versions.node.split(".")[0]')
minor=$(node -p 'process.versions.node.split(".")[1]')
if [ "$major" -lt 22 ] || { [ "$major" -eq 22 ] && [ "$minor" -lt 18 ]; }; then
  echo "FAIL  node                   (need 22.18 or newer, found $(node -v))"; exit 1
fi

if [ ! -d node_modules ]; then
  npm ci --no-audit --no-fund >/dev/null || { echo "FAIL  npm ci"; exit 1; }
fi
mkdir -p .out
log=.out/check.log

if [ "$side" = solutions ]; then
  npx tsc --noEmit >"$log" 2>&1; s=$?
  report typecheck $s "tsc --noEmit, $(grep -c 'error TS' "$log") errors"
  [ $s -eq 0 ] || cat "$log"
fi

node --test --test-reporter=tap tests/sse.test.ts tests/state.test.ts tests/server.test.ts tests/client.test.ts >"$log" 2>&1; s=$?
report "unit tests" $s "$(counts "$log"), target: $side"
[ $s -eq 0 ] || grep -E '^not ok' "$log"

if [ "$browser" = no ]; then
  node run_notes.ts --no-browser >"$log" 2>&1; s=$?
  report "notes' code" $s "$(tail -1 "$log")"
  [ $s -eq 0 ] || cat "$log"
  echo "NOT RUN  browser tests, axe and the teeth check: no-browser mode. Nothing here shows the page works."
  exit $fail
fi

if ! node -e 'import("playwright-core").then(({chromium})=>chromium.launch()).then(b=>b.close()).catch(()=>process.exit(1))'; then
  echo "FAIL  browser                (no Chromium: run npx playwright-core install chromium, or bash check.sh no-browser)"
  exit 1
fi

node --test --test-reporter=tap --test-concurrency=1 tests/browser.test.ts >"$log" 2>&1; s=$?
report "browser tests" $s "$(counts "$log") in headless Chromium, target: $side"
[ $s -eq 0 ] || grep -E '^not ok' "$log"

if [ "$side" = solutions ]; then
  node --test --test-reporter=tap tests/axe-limits.test.ts >"$log" 2>&1; s=$?
  report "axe blind spots" $s "$(counts "$log"): planted faults axe does not report"
  [ $s -eq 0 ] || grep -E '^not ok' "$log"

  # Tests that cannot fail prove nothing. Break the solution one way at a time and
  # require the matching test to notice.
  if [ $fail -eq 0 ]; then
    node tests/mutants.ts >"$log" 2>&1; s=$?
    report "planted faults" $s "$(tail -1 "$log")"
    [ $s -eq 0 ] || cat "$log"
  else
    echo "FAIL  planted faults         (not run: the tests must pass on the solution first)"
  fi

  node run_notes.ts >"$log" 2>&1; s=$?
  report "notes' code" $s "$(tail -1 "$log")"
  [ $s -eq 0 ] || cat "$log"
fi

[ $fail -eq 0 ] && echo "All checks pass. Not run: Safari, Firefox, any screen reader, any test with people."
exit $fail
