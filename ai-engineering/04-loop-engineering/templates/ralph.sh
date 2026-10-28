#!/usr/bin/env bash
# Ralph loop with the guardrails the one-liner lacks: iteration cap, wall-clock cap,
# a done check run by the scorekeeper (not the agent's own claim), stall detection,
# and roll-back on a score drop. See notes/05-long-running-loops.md#the-ralph-loop.
#
# Usage: SCORE_CMD='pytest -q | tail -1' ./ralph.sh PROMPT.md
#   SCORE_CMD must print a single number (higher is better) as its last line.
#   DONE_CMD (optional) exits 0 when the goal is met; defaults to SCORE_CMD's exit code.
set -euo pipefail

PROMPT_FILE="${1:?usage: ralph.sh PROMPT.md}"
MAX_ITERS="${MAX_ITERS:-20}"
MAX_MINUTES="${MAX_MINUTES:-60}"
STALL_LIMIT="${STALL_LIMIT:-3}"
SCORE_CMD="${SCORE_CMD:?set SCORE_CMD}"
DONE_CMD="${DONE_CMD:-$SCORE_CMD}"
AGENT_CMD="${AGENT_CMD:-claude -p}"
LOG="${LOG:-ralph.log}"

score() { bash -c "$SCORE_CMD" 2>/dev/null | tail -1 | grep -Eo '[0-9]+(\.[0-9]+)?' | tail -1 || echo 0; }

deadline=$(( $(date +%s) + MAX_MINUTES * 60 ))
best=$(score)
stall=0
echo "$(date -u +%FT%TZ) start score=$best" | tee -a "$LOG"

for ((i = 1; i <= MAX_ITERS; i++)); do
  if (( $(date +%s) > deadline )); then
    echo "$(date -u +%FT%TZ) STOP wall-clock cap" | tee -a "$LOG"; exit 2
  fi

  $AGENT_CMD < "$PROMPT_FILE" >> "$LOG" 2>&1 || true
  now=$(score)

  if awk "BEGIN{exit !($now < $best)}"; then
    # Score went down: the ratchet says undo.
    git reset --hard -q HEAD && git clean -fdq
    echo "$(date -u +%FT%TZ) pass=$i score=$now < $best ROLLED BACK" | tee -a "$LOG"
    stall=$((stall + 1))
  elif awk "BEGIN{exit !($now > $best)}"; then
    git add -A && git commit -qm "ralph pass $i: score $best -> $now" || true
    echo "$(date -u +%FT%TZ) pass=$i score=$now SAVED" | tee -a "$LOG"
    best=$now; stall=0
  else
    echo "$(date -u +%FT%TZ) pass=$i score=$now no change" | tee -a "$LOG"
    stall=$((stall + 1))
  fi

  if bash -c "$DONE_CMD" > /dev/null 2>&1; then
    echo "$(date -u +%FT%TZ) DONE pass=$i score=$best" | tee -a "$LOG"; exit 0
  fi
  if (( stall >= STALL_LIMIT )); then
    echo "$(date -u +%FT%TZ) STOP stalled $stall passes; escalate" | tee -a "$LOG"; exit 3
  fi
done

echo "$(date -u +%FT%TZ) STOP iteration cap ($MAX_ITERS); escalate" | tee -a "$LOG"
exit 1
