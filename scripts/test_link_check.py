import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import link_check  # noqa: E402


class Slugs(unittest.TestCase):
    def test_github_rule(self):
        self.assertEqual(link_check.slug("PyMC3 to current PyMC"), "pymc3-to-current-pymc")
        self.assertEqual(link_check.slug("Agent system prompts: procedures, not rule piles"),
                         "agent-system-prompts-procedures-not-rule-piles")
        self.assertEqual(link_check.slug("`np.finfo`, measured"), "npfinfo-measured")
        self.assertEqual(link_check.slug("See [the map](x.md) here"), "see-the-map-here")

    def test_duplicates_and_html_anchors(self):
        text = "## Try it\n\n## Try it\n\n<a id=\"custom\"></a>\n"
        self.assertEqual(link_check.anchors(text), {"try-it", "try-it-1", "custom"})

    def test_headings_inside_fences_are_not_anchors(self):
        text = "## Real\n\n````markdown\n```\n## Fake\n```\n````\n\n## After\n"
        self.assertEqual(link_check.anchors(text), {"real", "after"})


class CheckFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        with open(os.path.join(self.root, "b.md"), "w") as fh:
            fh.write("# B\n\n## Log-sum-exp\n")

    def tearDown(self):
        self.tmp.cleanup()

    def problems(self, body):
        path = os.path.join(self.root, "a.md")
        with open(path, "w") as fh:
            fh.write("## Here\n\n" + body)
        return link_check.check_file(path, self.root)

    def test_good_links_pass(self):
        self.assertEqual(self.problems("[x](b.md#log-sum-exp) [y](#here) [z](b.md) [w](https://e.com#q)"), [])

    def test_missing_file_and_anchor_are_reported(self):
        found = self.problems("[x](c.md) [y](b.md#nope) [z](#gone)")
        self.assertEqual(len(found), 3)
        self.assertTrue(found[0].startswith("BROKEN: "))
        self.assertTrue(all(p.startswith("BROKEN ANCHOR: ") for p in found[1:]))

    def test_links_in_code_are_ignored(self):
        self.assertEqual(self.problems("```\n[x](b.md#nope)\n```\n"), [])


if __name__ == "__main__":
    unittest.main()
