#!/usr/bin/env python3
"""Tests for the structured extractions: python3 scripts/test_extract.py"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent / "papers"))
import extract

TEXT = """Attention Is All You Need
We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs.
We used the Adam optimizer with β1 = 0.9, β2 = 0.98 and ε = 10−9. We trained the base models for a total
of 100,000 steps on 8 NVIDIA P100 GPUs. On the WMT 2014 English-to-German translation task, the big trans-
former model outperforms the best previously reported models by more than 2.0 BLEU, establishing a new
state-of-the-art BLEU score of 28.4."""


def texts(t=TEXT):
    return [{"norm": extract.norm_text(t), "squash": extract.squash(t)}]


def full(**over):
    """A minimal passing schema-1 extraction built from the template."""
    x = json.loads(extract.TEMPLATE.read_text())
    x = {k: v for k, v in x.items() if not k.startswith("_")}
    x.update(key="1706.03762", pdf="p.pdf", type="empirical", question="q", hypothesis=None,
             read={"by": "source-reader", "at": "2026-11-07", "chars_read": 10, "chars_total": 10,
                   "engine": "pymupdf", "skipped": None})
    m = {k: v for k, v in x["method"].items() if not k.startswith("_")}
    m.update(datasets=[{"name": "WMT 2014 En-De", "role": "train", "size": "4.5 million sentence pairs"}],
             models=[{"name": "Transformer big", "role": "proposed", "params": None}],
             training={**m["training"], "optimizer": "Adam", "steps": "100,000", "hardware": "8 NVIDIA P100"},
             inference={**m["inference"], "samples": None, "prompting": None, "parameters": {}},
             prompts=[], evidence=[])
    x["method"] = m
    x["results"] = [{"claim": "Big model sets SOTA on En-De", "metric": "BLEU", "value": "28.4", "unit": "BLEU",
                     "setup": "WMT 2014 En-De", "quote": "establishing a new state-of-the-art BLEU score of 28.4",
                     "where": "abstract"}]
    x["lineage"] = [{"work": "Adam", "relation": "uses-method"}]
    x.update(over)
    return x


class Schema(unittest.TestCase):
    def test_full_extraction_passes(self):
        self.assertEqual(extract.schema_errors(full()), [])

    def test_empirical_needs_method_block(self):
        self.assertTrue(any("method block" in e for e in extract.schema_errors(full(method=None))))

    def test_book_chapter_needs_no_method(self):
        self.assertEqual(extract.schema_errors(full(type="book-chapter", method=None)), [])

    def test_result_value_needs_quote_and_setup(self):
        x = full()
        x["results"][0].update(quote=None, setup="")
        errs = extract.schema_errors(x)
        self.assertTrue(any("no quote" in e for e in errs))
        self.assertTrue(any("no setup" in e for e in errs))

    def test_unknown_relation_and_type(self):
        x = full(type="essay")
        x["lineage"][0]["relation"] = "inspired"
        errs = extract.schema_errors(x)
        self.assertTrue(any("type" in e for e in errs))
        self.assertTrue(any("relation" in e for e in errs))

    def test_salvaged_needs_report(self):
        self.assertEqual(extract.schema_errors({"schema": 0, "key": "k", "pdf": "p", "legacy_report": "CLAIMS"}), [])
        self.assertTrue(extract.schema_errors({"schema": 0, "key": "k", "pdf": "p"}))


    def test_table_reference_stands_in_for_quote(self):
        x = full()
        x["results"][0].update(quote=None, table="Table 2, row Transformer (big), column EN-DE")
        self.assertEqual(extract.schema_errors(x), [])

    def test_files_without_new_method_keys_pass(self):
        x = full()
        for k in extract.OPTIONAL_METHOD:
            x["method"].pop(k, None)
        self.assertEqual(extract.schema_errors(x), [])

    def test_evaluates_relation(self):
        x = full()
        x["lineage"][0]["relation"] = "evaluates"
        self.assertEqual(extract.schema_errors(x), [])


    def test_result_kind(self):
        x = full()
        x["results"][0]["kind"] = "reported"
        self.assertEqual(extract.schema_errors(x), [])
        x["results"][0]["kind"] = "anecdote"
        self.assertTrue(any("kind" in e for e in extract.schema_errors(x)))


class Evidence(unittest.TestCase):
    def test_quote_survives_line_break_hyphen_and_case(self):
        self.assertTrue(extract.contains(texts(), "The big transformer model outperforms"))

    def test_quote_with_ellipsis(self):
        self.assertTrue(extract.contains(texts(), "We used the Adam optimizer ... 8 NVIDIA P100 GPUs"))

    def test_invented_quote_fails(self):
        errs, _ = extract.evidence_problems(full(results=[{**full()["results"][0], "quote": "a BLEU of 41.0"}]), texts())
        self.assertEqual(len(errs), 1)

    def test_method_numbers_found_in_text(self):
        _, warns = extract.evidence_problems(full(), texts())
        self.assertEqual(warns, [])

    def test_invented_hyperparameter_is_flagged(self):
        x = full()
        x["method"]["training"]["lr"] = "3e-4"
        _, warns = extract.evidence_problems(x, texts())
        self.assertTrue(any("training.lr" in w for w in warns))

    def test_table_value_must_be_in_text(self):
        x = full()
        x["results"][0].update(quote=None, table="Table 2", value="28.4")
        self.assertEqual(extract.evidence_problems(x, texts())[0], [])
        x["results"][0]["value"] = "29.7"
        self.assertEqual(len(extract.evidence_problems(x, texts())[0]), 1)

    def test_inferred_values_are_not_checked(self):
        x = full()
        x["method"]["training"]["lr"] = "inferred: 3e-4 from the cited recipe"
        self.assertEqual(extract.evidence_problems(x, texts())[1], [])

    def test_scientific_notation_forms(self):
        self.assertTrue(any(f in extract.squash(TEXT) for f in extract.number_forms("1e-9")) or
                        any(f in extract.squash("ε = 1e-9") for f in extract.number_forms("1e-9")))
        self.assertIn(extract.squash("0.0003"), extract.number_forms("3e-4"))
        self.assertIn("100000", extract.number_forms("100,000"))


class Repro(unittest.TestCase):
    def test_counts_stated_fields(self):
        score, have, missing = extract.repro(full())
        self.assertIn("optimizer", have)
        self.assertIn("learning rate", missing)
        self.assertEqual(score, 1)

    def test_no_training_work_is_scored_on_rerun_fields(self):
        x = full()
        x["method"]["trains"] = False
        x["method"]["inference"] = {**x["method"]["inference"], "decoding": "greedy", "samples": "32 samples",
                                    "parameters": {"alpha": "3"}}
        x["method"]["prompts"] = [{"purpose": "p", "text": "t", "where": "A"}]
        score, have, missing = extract.repro(x)
        self.assertNotIn("learning rate", have + missing)
        self.assertIn("prompts", have)
        self.assertEqual(score, 2)

    def test_not_scored_for_surveys_or_salvaged(self):
        self.assertIsNone(extract.repro(full(type="survey")))
        self.assertIsNone(extract.repro({"schema": 0}))


class Resolve(unittest.TestCase):
    ROWS = {"2501.18585": {"key": "2501.18585", "slug": "wang-2025-thoughts-all-over-place",
                           "local_pdf": "ai/sources/wang-2025-thoughts-all-over-place.pdf"}}

    def test_slug_stem_basename_and_path(self):
        for arg in ("2501.18585", "wang-2025-thoughts-all-over-place", "wang-2025-thoughts-all-over-place.pdf",
                    "ai/sources/wang-2025-thoughts-all-over-place.pdf"):
            self.assertEqual(extract.resolve(arg, self.ROWS)["key"], "2501.18585", arg)
        self.assertIsNone(extract.resolve("nobody-2020", self.ROWS))


class Keys(unittest.TestCase):
    def test_safe_key(self):
        self.assertEqual(extract.safe_key("1706.03762"), "1706.03762")
        self.assertEqual(extract.safe_key("sha1:b889bf99e580"), "sha1-b889bf99e580")
        k = extract.safe_key("https://github.com/x/y/blob/main/report.pdf")
        self.assertRegex(k, r"^[\w.-]+$")
        self.assertNotEqual(k, extract.safe_key("https://github.com/x/y/blob/main/report2.pdf"))


class Salvage(unittest.TestCase):
    ROWS = {
        "1706.03762": {"key": "1706.03762", "title": "Attention", "local_pdf": "g/sources/vaswani-2017.pdf"},
        "2005.11401": {"key": "2005.11401", "title": "RAG", "local_pdf": "g/sources/lewis-2020.pdf"},
    }

    def run_salvage(self, reports, existing=None):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(extract, "EXTRACTIONS", Path(d)):
            for key, x in (existing or {}).items():
                extract.path_for(key).write_text(json.dumps(x))
            stats = extract.salvage(copy.deepcopy(self.ROWS), reports)
            files = {p.stem: json.loads(p.read_text()) for p in Path(d).glob("*.json")}
        return stats, files

    def test_matches_by_path_and_prefers_full_read(self):
        reports = [
            ("2026-11-04T00:00", "s1", "Read g/sources/vaswani-2017.pdf", "COVERAGE: partial, skipped appendix\nCLAIMS"),
            ("2026-11-03T00:00", "s2", "Read g/sources/vaswani-2017.pdf", "COVERAGE: all 40,000 chars\nCLAIMS full"),
            ("2026-11-05T00:00", "s3", "Read lewis-2020.pdf please", "COVERAGE: all\nCLAIMS"),
            ("2026-11-05T00:00", "s4", "Read some-other.pdf", "COVERAGE: all\nCLAIMS"),
        ]
        stats, files = self.run_salvage(reports)
        self.assertEqual(stats["unmatched"], 1)
        self.assertEqual(files["1706.03762"]["legacy_report"], "COVERAGE: all 40,000 chars\nCLAIMS full")
        self.assertEqual(files["1706.03762"]["schema"], 0)
        self.assertIn("2005.11401", files)

    def test_never_overwrites_a_full_extraction(self):
        reports = [("2026-11-04T00:00", "s1", "Read g/sources/vaswani-2017.pdf", "COVERAGE: all\nCLAIMS")]
        stats, files = self.run_salvage(reports, existing={"1706.03762": {"schema": 1, "key": "1706.03762"}})
        self.assertEqual(files["1706.03762"]["schema"], 1)
        self.assertEqual(stats["kept_full"], 1)


if __name__ == "__main__":
    unittest.main()
