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
# every read left one (scripts/papers/extractions/): tier 1, tier 2 and book chapters first, paper tiers
# 3-6 once those are done. EXTRACT=0 skips it.
# PAPERS=0 skips the /papers and /chapter passes: PAPERS=0 STOP_HOUR=24 runs the backfill alone.
# Last, the run carries what was read into librarian's search index (the vector DB), in the sibling
# checkout at LIBRARIAN (default ../librarian):
#   1. `librarian scrape extractions` copies new extractions to its data/raw/papers/ (no model);
#   2. /ingest sessions there compile pending extractions into wiki pages, one batch of ten per session,
#      until the pending count stops falling, STOP_HOUR passes or a usage limit is hit;
#   3. `librarian courses import` mirrors the notes and `librarian index build` re-embeds (no model).
# Steps 1 and 3 cost no usage, so they run even after a limit or STOP_HOUR ended the passes above.
# Step 2 edits librarian's data/wiki/ and stages each batch there; it never commits either.
# INGEST=0 skips all three. PAPERS=0 EXTRACT=0 STOP_HOUR=24 runs the ingestion alone.

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
PAPERS="${PAPERS:-1}"
INGEST="${INGEST:-1}"
LIBRARIAN="${LIBRARIAN:-$REPO/../librarian}"
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

# The human gate in /ingest's Bulk Mode (stop for a go-ahead after each batch) is replaced by one batch
# per session: the next session starts from the manifest, with a fresh context.
WIKI_TAIL="This is an unattended overnight run in Bulk Mode: nobody is available to answer questions or to give the go-ahead between batches, so make the sensible call and record it in your final report. Compile ONE batch of ten pending paper extractions, grouped by topic as the skill says, and no more. Run the batch's checks and reviewers and fix what they find, then close it out with \`ingest closeout --mark\`, stage the batch with git add, and end the session with the report instead of waiting: the next session takes the next batch. A source you cannot compile cleanly stays unmarked and goes under Not ingested. A usage limit can end this run at any moment, so mark a source only once its pages pass \`wiki verify\`. Never write under data/raw/ or a private/ directory. Do not commit or push."
WIKI_DENY=("Write(data/raw/**)" "Edit(data/raw/**)" "Write(**/private/**)" "Edit(**/private/**)")

LIMIT_HIT=0
# session LABEL PROMPT [DIR TAIL DENY...]: one headless claude session, in DIR when given (default: this
# repo, with PROMPT_TAIL); sets LIMIT_HIT if it ended on a usage limit
session() {
    local out status label="$1" prompt="$2" dir="${3:-$REPO}" closing="${4:-$PROMPT_TAIL}"
    shift $(( $# < 4 ? $# : 4 ))
    out="$(cd "$dir" && claude -p "$prompt

$closing" \
        --permission-mode auto \
        --disallowedTools "Bash(git commit:*)" "Bash(git push:*)" "Bash(gh pr:*)" "$@" 2>&1)"
    status=$?
    echo "$out" | tail -40
    echo "$(date '+%F %T') $label exit $status"
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
# The core (tier 1, tier 2, book chapters) goes first; paper tiers 3-6 only once the core is empty.
# Papers the /papers passes above read already left their extraction, so they are not in either count.
extractions() {
    local n left scope flag
    for scope in core all; do
        flag=""; [ "$scope" = "all" ] && flag="--all"
        while ! stop_now; do
            n="$(python3 scripts/papers/extract.py next --count $flag)"
            [ "$n" -gt 0 ] || { echo "$(date '+%F %T') /extract $scope: nothing left"; break; }
            echo "$(date '+%F %T') /extract $scope ($n left)"
            session "/extract $scope" "/extract ${flag:+all }12"
            left="$(python3 scripts/papers/extract.py next --count $flag)"
            [ "$left" -lt "$n" ] || return  # no progress: what's left needs a person
        done
        [ "$n" -gt 0 ] && return  # stopped inside the core: don't start on the rest
    done
}

# librarian VERB...: one `librarian` command in the sibling checkout, logged; a failure does not end the run
librarian() {
    echo "$(date '+%F %T') librarian $*"
    (cd "$LIBRARIAN" && uv run librarian "$@" 2>&1 | tail -5)  # pipefail: uv's failure is the status
    local status=$?
    [ "$status" -eq 0 ] || echo "$(date '+%F %T') librarian $* failed (exit $status)"
    return "$status"
}

# Paper extractions in librarian's data/raw/papers/ that no wiki page has been compiled from yet.
wiki_pending() {
    (cd "$LIBRARIAN" && uv run librarian ingest pending --count 'data/raw/papers/*.md' 2>/dev/null) || echo 0
}

# Compile pending extractions into the wiki, a batch per session, until the count stops falling.
wiki() {
    local n left
    while ! stop_now; do
        n="$(wiki_pending)"
        [ "$n" -gt 0 ] || { echo "$(date '+%F %T') /ingest papers: nothing pending"; return; }
        echo "$(date '+%F %T') /ingest papers ($n pending)"
        session "/ingest papers" "/ingest data/raw/papers/" "$LIBRARIAN" "$WIKI_TAIL" "${WIKI_DENY[@]}"
        left="$(wiki_pending)"
        echo "$(date '+%F %T') /ingest papers: $left still pending"
        [ "$left" -lt "$n" ] || return  # no progress: what's left needs a person
    done
}

ingestion() {
    if [ ! -d "$LIBRARIAN/src/librarian" ]; then
        echo "$(date '+%F %T') no librarian checkout at $LIBRARIAN; skipping ingestion"
        return
    fi
    librarian scrape extractions && wiki
    librarian courses import
    librarian index build
}

python3 scripts/papers/potw.py tier

[ "$PAPERS" = "1" ] || TIERS=()
first=1
for tier in ${TIERS[@]+"${TIERS[@]}"}; do
    stop_now && break
    papers "$tier"
    if [ "$first" -eq 1 ]; then  # chapters come ahead of the lower paper tiers, or those starve them
        chapters
        first=0
    fi
done
[ "$EXTRACT" = "1" ] && ! stop_now && extractions
[ "$INGEST" = "1" ] && ingestion
python3 scripts/papers/potw.py status
python3 scripts/papers/extract.py status | tail -2
