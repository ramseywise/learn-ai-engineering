#!/usr/bin/env bash
# Nightly /papers and /chapter run: integrate PDFs into the notes, one headless Claude session (fresh
# context) per home and tier, or per chapter. Every home's tier 1 comes first (tiers: `potw.py tier`),
# then ready book chapters one at a time, then every home's tier 2 and so on. Within a tier the biggest
# backlog goes first; a home with nothing ready gets no session.
#
# Scheduled by launchd (com.wiseer.papers-nightly.plist). Install with `make papers-nightly-install`,
# remove with `make papers-nightly-uninstall`. The start hour is not tuned to the usage window, which
# moves with use: a limit is detected and ends the run instead.
#
# Edits notes, references.md, sources/images/ and the ledger. Never commits (git
# commit/push are disallowed below); review with `git status` in the morning.
# A run rarely clears a big home, so each home and tier repeats until its ready count stops falling.
# Stops starting new runs at STOP_HOUR (STOP_HOUR=24 never stops), or as soon as a run hits
# the usage limit, whichever pass it is in.
# After the integration tiers, an /extract pass backfills structured extractions for PDFs read before
# every read left one (scripts/papers/extractions/). EXTRACT=0 skips it.

set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
NVM_BIN="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | tail -1)"
export PATH="${NVM_BIN:+$NVM_BIN:}/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
# claude's keychain login lookup needs these; without them -p reports "Not logged in"
export USER="${USER:-$(id -un)}" LOGNAME="${LOGNAME:-$(id -un)}"
# by default claude -p kills background agents after 600s, losing their unreported work
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0

STOP_HOUR="${STOP_HOUR:-8}"
read -ra TIERS <<< "${TIERS:-1 2 3 4 5 6}"  # TIERS="1 2" limits a run
EXTRACT="${EXTRACT:-1}"
LOCK="$REPO/.claude/logs/papers-nightly.lock"

cd "$REPO" || exit 1
mkdir -p .claude/logs
if ! mkdir "$LOCK" 2>/dev/null; then
    echo "$(date '+%F %T') another nightly run holds $LOCK; exiting"
    exit 0
fi
trap 'rmdir "$LOCK"' EXIT

# shellcheck source=scripts/papers/nightly-lib.sh
source "$REPO/scripts/papers/nightly-lib.sh"

PROMPT_TAIL="This is an unattended overnight run: nobody is available to answer questions, so make the sensible call and record it in your final report. Read each PDF in full, and tell any subagent to as well. Every PDF read must leave a passing extraction in scripts/papers/extractions/ (the source-reader writes it); check it before marking the paper integrated. Material a note already covers counts as sharpens: add the citation and the references.md row, never drop it silently. A usage limit can end this run at any moment, so write each paper's note edit and references.md row before you mark it integrated, in small batches. \`potw.py mark integrated\` refuses a key no note or references.md in its home cites, so write the citation first; use --no-citation only for a real exception, with the reason. Do not commit or push; stage with git add only if the repo rules say so."

LIMIT_HIT=0
# session LABEL PROMPT: one headless claude session; sets LIMIT_HIT if it ended on a usage limit
session() {
    local out status
    out="$(claude -p "$2

$PROMPT_TAIL" \
        --permission-mode auto \
        --disallowedTools "Bash(git commit:*)" "Bash(git push:*)" "Bash(gh pr:*)" 2>&1)"
    status=$?
    echo "$out" | tail -40
    echo "$(date '+%F %T') $1 exit $status"
    if limit_hit "$status" "$out"; then
        echo "$(date '+%F %T') usage limit hit, stopping: $(limit_text "$out")"
        LIMIT_HIT=1
    fi
}

stop_now() {
    [ "$LIMIT_HIT" -eq 1 ] && return 0
    if past_stop "$(date +%H)" "$STOP_HOUR"; then
        echo "$(date '+%F %T') past ${STOP_HOUR}:00; stopping"
        return 0
    fi
    return 1
}

# One chapter per session (the /chapter skill's rule). A chapter a session leaves unfinished is
# passed over for the rest of the run: what's left needs a person.
chapters() {
    local skip=() pick book chapter key
    while ! stop_now; do
        pick="$(python3 scripts/papers/potw.py ready --next-chapter --exclude ${skip[@]+"${skip[@]}"})"
        [ -n "$pick" ] || { echo "$(date '+%F %T') /chapter: nothing ready"; return; }
        read -r book chapter key <<< "$pick"
        echo "$(date '+%F %T') /chapter $book $chapter"
        session "/chapter $book $chapter" "/chapter $book $chapter"
        skip+=("$key")
    done
}

papers() {
    local tier="$1" home n left
    for home in $(python3 scripts/papers/potw.py ready --tier "$tier"); do
        while ! stop_now; do
            n="$(python3 scripts/papers/potw.py ready --tier "$tier" --count "$home")"
            [ "$n" -gt 0 ] || break
            echo "$(date '+%F %T') /papers $home tier:$tier ($n ready)"
            session "/papers $home tier:$tier" "/papers $home tier:$tier"
            left="$(python3 scripts/papers/potw.py ready --tier "$tier" --count "$home")"
            echo "$(date '+%F %T') /papers $home tier:$tier: $left still ready"
            [ "$left" -lt "$n" ] || break  # no progress: what's left needs a person
        done
    done
}

# Backfill extractions, best first, until the backlog stops shrinking. Notes are not touched.
extractions() {
    local n left
    while ! stop_now; do
        n="$(python3 scripts/papers/extract.py next --count)"
        [ "$n" -gt 0 ] || { echo "$(date '+%F %T') /extract: nothing left"; return; }
        echo "$(date '+%F %T') /extract ($n left)"
        session "/extract" "/extract 12"
        left="$(python3 scripts/papers/extract.py next --count)"
        [ "$left" -lt "$n" ] || break  # no progress: what's left needs a person
    done
}

python3 scripts/papers/potw.py tier

first=1
for tier in "${TIERS[@]}"; do
    stop_now && break
    papers "$tier"
    if [ "$first" -eq 1 ]; then  # chapters come ahead of the lower paper tiers, or those starve them
        chapters
        first=0
    fi
done
[ "$EXTRACT" = "1" ] && ! stop_now && extractions
python3 scripts/papers/potw.py status
python3 scripts/papers/extract.py status | tail -2
