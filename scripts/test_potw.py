#!/usr/bin/env python3
"""Tests for the paper ledger's fetch step: python3 scripts/test_potw.py"""
import argparse
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent / "papers"))
import potw

PAGE = "2026 page"


def paper(key, week_start):
    return {"key": key, "title": key, "blurb": "", "week_start": week_start, "status": "new"}


def fetch(rows, parsed, since=None):
    """Run cmd_fetch against an in-memory ledger and return the rows it would save."""
    args = argparse.Namespace(since=since, years=[2026])
    with mock.patch.object(potw, "load_ledger", return_value=rows), \
            mock.patch.object(potw, "http_get", return_value=PAGE.encode()), \
            mock.patch.object(potw, "parse_year", return_value=parsed), \
            mock.patch.object(potw, "log"), \
            mock.patch.object(potw, "save_ledger") as save:
        potw.cmd_fetch(args)
    return save.call_args.args[0]


class Fetch(unittest.TestCase):
    def test_rows_without_week_start_do_not_break_fetch(self):
        curated = {"key": "curated", "title": "c", "blurb": "", "status": "integrated"}
        saved = fetch([curated, paper("old", "2026-03-02")], [paper("new", "2026-03-09")])
        self.assertEqual([r["key"] for r in saved], ["curated", "old", "new"])

    def test_no_backfill_before_newest_week_with_a_date(self):
        curated = {"key": "curated", "title": "c", "blurb": "", "status": "integrated"}
        saved = fetch([curated, paper("old", "2026-03-02")], [paper("earlier", "2026-02-02")])
        self.assertEqual([r["key"] for r in saved], ["curated", "old"])

    def test_ledger_with_only_undated_rows_takes_everything(self):
        curated = {"key": "curated", "title": "c", "blurb": "", "status": "integrated"}
        saved = fetch([curated], [paper("earlier", "2026-02-02")])
        self.assertEqual([r["key"] for r in saved], ["curated", "earlier"])


if __name__ == "__main__":
    unittest.main()
