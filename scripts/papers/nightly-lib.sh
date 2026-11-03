# shellcheck shell=bash
# Functions for papers-nightly.sh, kept apart so the tests can load them without starting a run.

# limit_hit EXIT_STATUS OUTPUT: did this claude session end on a usage limit? A session can exit 0 and
# still say so, in a line of its own. A paper's summary can mention "rate limit" and exit 0, so that
# wording counts only on a failed exit.
limit_hit() {
    if echo "$2" | grep -qE "^(Claude usage limit reached|You've hit your (session|usage|weekly|[a-z]+ )?.*limit)"; then
        return 0
    fi
    [ "$1" -ne 0 ] && echo "$2" | grep -qiE "usage limit|session limit|rate limit|limit reached|resets [0-9a]"
}

# limit_text OUTPUT: the line naming the limit, for the log: "You've hit your session limit · resets 2:10am".
limit_text() {
    echo "$1" | grep -iE "limit|resets [0-9a]" | tail -1
}

# past_stop HOUR STOP_HOUR: is the run past its stop hour? 23:00 onward counts as the night before.
past_stop() {
    [ "$1" -ge "$2" ] && [ "$1" -lt 23 ]
}
