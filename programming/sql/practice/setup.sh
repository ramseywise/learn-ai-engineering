#!/usr/bin/env bash
# Build the practice databases. Safe to re-run.
#   data/survey.db               committed (Software Carpentry, CC-BY 4.0)
#   data/clubdata.db             built from data/clubdata.sql (PGExercises, CC BY-SA 3.0)
#   data/sql-murder-mystery.db   downloaded (Knight Lab, MIT)
set -euo pipefail
cd "$(dirname "$0")/data"

command -v sqlite3 >/dev/null || { echo "sqlite3 not found (macOS ships it; apt install sqlite3)"; exit 1; }

rm -f clubdata.db
sqlite3 clubdata.db < clubdata.sql
echo "built data/clubdata.db ($(sqlite3 clubdata.db 'SELECT count(*) FROM bookings') bookings)"

if [ ! -f sql-murder-mystery.db ]; then
  curl -fsSL -o sql-murder-mystery.db \
    https://raw.githubusercontent.com/NUKnightLab/sql-mysteries/master/sql-murder-mystery.db
  echo "downloaded data/sql-murder-mystery.db"
fi
