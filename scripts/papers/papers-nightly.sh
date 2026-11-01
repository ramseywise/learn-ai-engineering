#!/usr/bin/env bash
# Nightly /papers run: integrate downloaded PDFs into the notes, one home per headless
# Claude session (fresh context each), biggest backlog first.
#
# Scheduled by launchd (com.wiseer.papers-nightly.plist, daily 01:00). Install with
# `make papers-nightly-install`, remove with `make papers-nightly-uninstall`.
#
# Edits notes, references.md, sources/images/ and the ledger. Never commits (git
# commit/push are disallowed below); review with `git status` in the morning.
# A run rarely clears a big home, so each home repeats until its ready count stops falling.
# Stops starting new runs at STOP_HOUR (STOP_HOUR=24 never stops), or as soon as a run hits
# the usage limit.

set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
NVM_BIN="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | tail -1)"
export PATH="${NVM_BIN:+$NVM_BIN:}/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
# claude's keychain login lookup needs these; without them -p reports "Not logged in"
export USER="${USER:-$(id -un)}" LOGNAME="${LOGNAME:-$(id -un)}"
# by default claude -p kills background agents after 600s, losing their unreported work
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0

STOP_HOUR="${STOP_HOUR:-8}"
HOMES=(post-training llm-fundamentals eval agents inference multimodal agentic-apps
       prompt context rag loop classical-ml safety ml-systems harness graph frameworks
       analytics data-systems)
LOCK="$REPO/.claude/logs/papers-nightly.lock"

cd "$REPO"
mkdir -p .claude/logs
if ! mkdir "$LOCK" 2>/dev/null; then
    echo "$(date '+%F %T') another nightly run holds $LOCK; exiting"
    exit 0
fi
trap 'rmdir "$LOCK"' EXIT

# PDFs ready for /papers in a home: downloaded rows, plus queued rows whose PDF is
# already in the repo (outside the inbox, not a /chapter book chapter).
ready() {
    python3 - "$1" <<'EOF'
import json, re, sys
home = sys.argv[1]
n = 0
for line in open("scripts/papers/ledger.jsonl"):
    if not line.strip():
        continue
    r = json.loads(line)
    if r.get("pillar") != home:
        continue
    pdf = r.get("local_pdf") or ""
    if r["status"] == "downloaded" or (
        r["status"] == "queued" and r.get("have_pdf")
        and not pdf.startswith("scripts/papers/inbox/") and not re.search(r"/ch\d\d-", pdf)):
        n += 1
print(n)
EOF
}

PROMPT_TAIL="This is an unattended overnight run: nobody is available to answer questions, so make the sensible call and record it in your final report. Read each PDF in full, and tell any subagent to as well. Material a note already covers counts as sharpens: add the citation and the references.md row, never drop it silently. Do not commit or push; stage with git add only if the repo rules say so."

for home in "${HOMES[@]}"; do
    while :; do
        if [ "$(date +%H)" -ge "$STOP_HOUR" ] && [ "$(date +%H)" -lt 23 ]; then
            echo "$(date '+%F %T') past ${STOP_HOUR}:00; stopping before $home"
            break 2
        fi
        n="$(ready "$home")"
        [ "$n" -gt 0 ] || break
        echo "$(date '+%F %T') /papers $home ($n ready)"
        out="$(claude -p "/papers $home

$PROMPT_TAIL" \
            --permission-mode auto \
            --disallowedTools "Bash(git commit:*)" "Bash(git push:*)" "Bash(gh pr:*)" 2>&1)"
        status=$?
        echo "$out" | tail -40
        left="$(ready "$home")"
        echo "$(date '+%F %T') /papers $home exit $status; $left still ready"
        if [ $status -ne 0 ] && echo "$out" | grep -qiE "usage limit|rate limit|limit reached|resets at"; then
            echo "$(date '+%F %T') usage limit hit; stopping"
            break 2
        fi
        [ "$left" -lt "$n" ] || break  # no progress: what's left needs a person
    done
done
python3 scripts/papers/potw.py status
