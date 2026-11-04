#!/usr/bin/env python3
"""Tests for the practice manifest validator: python3 scripts/test_check_manifest.py"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "practice"))
import check_manifest as cm

PILLAR = "ai-engineering/01-prompt-engineering"
TRACKED = {
    f"{PILLAR}/README.md",
    f"{PILLAR}/notes/04-controlling-output.md",
    f"{PILLAR}/practice/README.md",
    f"{PILLAR}/practice/.gitignore",
    f"{PILLAR}/practice/data/x.csv",
    f"{PILLAR}/practice/harness/run.ts",
    f"{PILLAR}/practice/harness/test.ts",
    f"{PILLAR}/practice/harness-py/run.py",
    f"{PILLAR}/practice/helper.py",
    f"{PILLAR}/practice/vendored/a.ipynb",
}
THIRD = f"| `{PILLAR}/practice/vendored/` | upstream | MIT |"


def entry(path, **over):
    e = {
        "path": path, "purpose": "Does one thing.", "demonstrates": [], "pattern": "eval", "language": "python",
        "runs_offline": True, "verified_by": "cd x && uv run test.py", "licence": "course",
    }
    e.update(over)
    return e


def dump(entries):
    out = ["examples:"]
    for e in entries:
        first = True
        for k, v in e.items():
            lead = "  - " if first else "    "
            first = False
            if isinstance(v, list):
                out.append(f"{lead}{k}:" if v else f"{lead}{k}: []")
                out += [f"      - {json.dumps(x)}" for x in v]
            elif isinstance(v, bool):
                out.append(f"{lead}{k}: {str(v).lower()}")
            elif v is None:
                out.append(f"{lead}{k}: none")
            elif k in ("pattern", "language", "licence"):
                out.append(f"{lead}{k}: {v}")
            else:
                out.append(f"{lead}{k}: {json.dumps(v)}")
    return "\n".join(out) + "\n"


def full_set():
    return [
        entry("practice/harness", language="typescript"),
        entry("practice/harness-py"),
        entry("practice/helper.py", pattern="other", verified_by=None),
        entry("practice/vendored", language="jupyter", verified_by=None, licence="MIT"),
    ]


def check(entries=None, tracked=TRACKED, text=None):
    return cm.check_pillar(PILLAR, text if text is not None else dump(entries), set(tracked), THIRD)


class ParseTests(unittest.TestCase):
    def test_round_trip(self):
        got = cm.parse(dump([entry("practice/a", demonstrates=["notes/x.md", "notes/y.md"], verified_by=None)]))
        self.assertEqual(got[0]["demonstrates"], ["notes/x.md", "notes/y.md"])
        self.assertIsNone(got[0]["verified_by"])
        self.assertIs(got[0]["runs_offline"], True)

    def test_empty_list_forms(self):
        self.assertEqual(cm.parse(dump([entry("practice/a")]))[0]["demonstrates"], [])
        text = dump([entry("practice/a")]).replace("demonstrates: []", "demonstrates:")
        self.assertEqual(cm.parse(text)[0]["demonstrates"], [])

    def test_rejects_unquoted_prose_and_tabs_and_repeats(self):
        for bad in ("examples:\n  - path: practice/a b c\n", "examples:\n  - path: \"a\"\n\tpurpose: \"x\"\n",
                    "examples:\n  - path: \"a\"\n    path: \"b\"\n", "examples:\n    path: \"a\"\n", "nope: 1\n"):
            with self.assertRaises(cm.ManifestError, msg=bad):
                cm.parse(bad)

    def test_comments_and_quotes(self):
        got = cm.parse('# top\nexamples:\n  - path: "practice/a"\n    purpose: "says \\"hi\\": ok"\n')
        self.assertEqual(got[0]["purpose"], 'says "hi": ok')


class CheckTests(unittest.TestCase):
    def test_complete_manifest_is_clean(self):
        self.assertEqual(check(full_set()), [])

    def test_unparseable_manifest_is_one_problem(self):
        self.assertEqual(len(check(text="examples:\n  - path: practice/a b\n")), 1)

    def test_missing_manifest(self):
        self.assertTrue(cm.check_pillar(PILLAR, None, set(TRACKED), THIRD))
        self.assertEqual(cm.check_pillar(PILLAR, None, {f"{PILLAR}/practice/README.md"}, THIRD), [])

    def test_uncovered_example_is_reported_but_exempt_names_are_not(self):
        got = check(full_set()[:2])
        self.assertEqual(len(got), 2)
        self.assertTrue(any("practice/helper.py has no entry" in g for g in got))
        self.assertFalse(any("README" in g or "data" in g or ".gitignore" in g for g in got))

    def test_entry_for_a_deeper_path_covers_its_unit(self):
        es = full_set()
        es[0]["path"] = "practice/harness/run.ts"
        self.assertEqual(check(es), [])

    def test_missing_path_and_duplicate(self):
        es = full_set() + [entry("practice/ghost"), entry("practice/helper.py", pattern="other", verified_by=None)]
        got = check(es)
        self.assertTrue(any("ghost" in g and "does not exist" in g for g in got))
        self.assertTrue(any("helper.py" in g and "twice" in g for g in got))

    def test_bad_path_shapes(self):
        for p in ("harness", "practice/harness/", "practice/../notes"):
            es = full_set()
            es[1]["path"] = p
            self.assertTrue(any("path must be" in g for g in check(es)), p)

    def test_enums(self):
        es = full_set()
        es[0]["pattern"] = "rag"
        es[1]["language"] = "rust"
        got = check(es)
        self.assertTrue(any("pattern 'rag'" in g for g in got))
        self.assertTrue(any("language 'rust'" in g for g in got))

    def test_schema_keys_and_types(self):
        es = full_set()
        del es[1]["purpose"]
        es[2]["extra"] = "x"
        es[0]["runs_offline"] = "yes"
        got = "\n".join(check(es))
        self.assertIn("missing key(s) ['purpose']", got)
        self.assertIn("unknown key(s) ['extra']", got)
        self.assertIn("runs_offline must be true or false", got)

    def test_demonstrates_must_resolve(self):
        es = full_set()
        es[1]["demonstrates"] = ["notes/04-controlling-output.md", "notes/nope.md"]
        got = check(es)
        self.assertEqual(len(got), 1)
        self.assertIn("notes/nope.md", got[0])

    def test_test_without_verification_needs_a_note(self):
        es = full_set()
        es[0]["verified_by"] = None
        self.assertTrue(any("ships a test" in g for g in check(es)))
        es[0]["verification_note"] = "Needs npx tsx, which was not installed here."
        self.assertEqual(check(es), [])

    def test_note_on_a_verified_entry_is_rejected(self):
        es = full_set()
        es[1]["verification_note"] = "stale"
        self.assertTrue(any("only belongs" in g for g in check(es)))

    def test_no_note_needed_when_no_test_ships(self):
        self.assertEqual(check(full_set()), [])  # helper.py and vendored have verified_by none and no test

    def test_licence_must_be_in_third_party(self):
        es = full_set()
        es[3]["licence"] = "unrecorded"
        self.assertEqual(check(es), [])
        es[3]["licence"] = "MIT"
        es[2]["licence"] = "Apache-2.0"
        got = check(es)
        self.assertEqual(len(got), 1)
        self.assertIn("THIRD_PARTY", got[0])

    def test_purpose_must_be_one_line(self):
        es = full_set()
        es[1]["purpose"] = "  "
        self.assertTrue(any("purpose" in g for g in check(es)))

    def test_pillars_found_from_tracked_paths(self):
        self.assertEqual(cm.pillars(TRACKED | {"programming/x/practice/a/b.py", "scripts/a/b/c/d.py"}), [PILLAR])


if __name__ == "__main__":
    unittest.main()
