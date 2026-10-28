#!/usr/bin/env bash
# Weekly AI Papers of the Week sync: fetch new weeks -> triage -> download PDFs.
#
# Scheduled by launchd (com.wiseer.potw.plist, Monday 11:00), not crontab — cron skips
# windows while the Mac is asleep; launchd re-fires on wake. Install with
# `make papers-install`.
#
# Writes only the ledger and new PDFs under <pillar>/sources/. Never edits notes or
# commits; run /papers to integrate findings into the notes.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
# launchd starts with a bare PATH; claude lives under nvm
NVM_BIN="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | tail -1)"
export PATH="${NVM_BIN:+$NVM_BIN:}/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

cd "$REPO"
python3 scripts/papers/potw.py run
python3 scripts/papers/potw.py status
