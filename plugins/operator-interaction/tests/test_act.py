"""Every decision carries what it takes to act on it.

Two halves:

- the decision page (`decision-page` skill): its `act` field, the data check that refuses a
  malformed one or a fill-in placeholder, and `actList`, which renders an option's steps;
  loaded from `assets/index.html` and run under node against `assets/cards.example.json`
  and broken copies of it;
- the decisions skill's worked examples: no fill-in placeholder, no source label a cold
  reader cannot resolve outside a "Not this" paragraph, and every path in a **To act on**
  part absolute.

Undefined terms on a card are not decidable by a program; they stay the cold read's
(`references/worksheet.md` § The cold read).

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import re
import subprocess
import sys
import unittest

from test_impact import NODE, PAGE, DECISIONS, example, page_free_script

GALLERY = DECISIONS / "references" / "gallery.md"


def setUpModule():
    # the page tests need node; without it they skip, and say so where the Check's
    # output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's act tests "
              "(DecisionPageAct) are skipped, so the page's act check and actList "
              "went untested", file=sys.stderr)

# the same shape the page's check refuses: an angle-bracketed word with no spaces
PLACEHOLDER = re.compile(r"<[A-Za-z][\w-]*>")
# a source document's label: one to three capitals and a number (a step, a gate, a finding)
LABEL = re.compile(r"\b[A-Z]{1,3}[0-9]+[a-z]?\b")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
ACT_HEAD = re.compile(r"^\*\*To act on \([a-y]\):\*\*")
CODE_SPAN = re.compile(r"`([^`]+)`")

HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
const bad = check(d);
let acts = [];
if (!bad.length) {
  CARDS = d.cards; REFS = d.refs || {};
  byN = new Map(CARDS.map(c => [String(c.n), c]));
  acts = CARDS.map(c => ({n: c.n, html: Object.fromEntries(c.o.map(o => [o[0], actList(c, o[0])]))}));
}
process.stdout.write(JSON.stringify({bad, acts}));
"""


def run_page(data):
    out = subprocess.run([NODE, "-e", page_free_script() + HARNESS],
                         input=json.dumps(data), capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageAct(unittest.TestCase):

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    def test_the_example_carries_act_and_passes(self):
        d = example()
        self.assertIn("b", d["cards"][0]["act"])
        res = run_page(d)
        self.assertEqual(res["bad"], [])

    def test_act_is_optional(self):
        d = example()
        del d["cards"][0]["act"]
        self.assertEqual(run_page(d)["bad"], [])

    def test_act_keyed_by_z_or_an_unknown_letter_is_refused(self):
        for key in ("z", "q"):
            d = example()
            d["cards"][0]["act"][key] = ["a step"]
            self.assert_refused(d, "card 41: act is keyed by option letter")

    def test_act_that_is_not_an_object_is_refused(self):
        for bad in (["a step"], "a step", 3):
            d = example()
            d["cards"][0]["act"] = bad
            self.assert_refused(d, "card 41: act is keyed by option letter")

    def test_an_empty_or_non_text_step_list_is_refused(self):
        for steps in ([], [""], ["  "], [3], ["ok", None], "a step"):
            d = example()
            d["cards"][0]["act"]["b"] = steps
            self.assert_refused(d, "card 41: act is keyed by option letter")

    def test_a_fill_in_placeholder_is_refused(self):
        for step in ("run it from <kit>/run.sh", "open <path>", "paste <br> as is"):
            d = example()
            d["cards"][0]["act"]["b"] = ["first step", step]
            self.assert_refused(d, "card 41: act (b) has a fill-in placeholder")

    def test_an_angle_bracket_with_a_space_is_not_a_placeholder(self):
        d = example()
        d["cards"][0]["act"]["b"] = ["run it when the count is < 5 and > 2"]
        self.assertEqual(run_page(d)["bad"], [])

    def test_act_list_renders_each_step_in_order_under_its_option(self):
        res = run_page(example())
        html = res["acts"][0]["html"]
        self.assertEqual(html["a"], "")
        self.assertEqual(html["z"], "")
        b = html["b"]
        self.assertIn("To act on (b):", b)
        self.assertEqual(b.count("<li>"), 2)
        self.assertLess(b.index("ci.example.com"), b.index("done in your words"))
        # backtick code renders as code
        self.assertIn("<code>DOCS_DEPLOY_TOKEN</code>", b)
        # cards with no act render nothing
        for v in res["acts"][1:]:
            self.assertTrue(all(h == "" for h in v["html"].values()), v)

    def test_act_text_is_escaped(self):
        d = example()
        d["cards"][0]["act"]["b"] = ['<img src=x onerror="alert(1)" >', "<script >x</script >"]
        b = run_page(d)["acts"][0]["html"]["b"]
        self.assertNotIn("<img", b)
        self.assertNotIn("<script", b)
        self.assertIn("&lt;img", b)

    def test_the_page_renders_act_under_each_option(self):
        html = PAGE.read_text()
        cards = html[html.index("function renderCards"):html.index("function placeholderFor")]
        self.assertIn("actList(c,k)", cards)
        # inside the option, never in a fold: before the follow-ups and the panes
        self.assertLess(cards.index("actList(c,k)"), cards.index('class="follow"'))
        self.assertLess(cards.index("actList(c,k)"), cards.index('class="panes"'))


def gallery_blocks():
    """The gallery as (line number, line, in_fence, in_act_part, in_not_this) tuples.

    A To act on part runs from its heading to the next blank line that is followed by a
    line that is neither a step nor indented (the Rec line, a "Not this" paragraph, a rule).
    A "Not this" paragraph opens with `*Not this` and runs to the next blank line."""
    lines = GALLERY.read_text().splitlines()
    out = []
    fence = None
    act = False
    not_this = False
    for i, line in enumerate(lines):
        n = i + 1
        f = FENCE.match(line)
        if ACT_HEAD.match(line):
            act = True
        elif act and not line.strip() and fence is None:
            nxt = next((x for x in lines[i + 1:] if x.strip()), "")
            if not (re.match(r"^\d+\. ", nxt) or nxt.startswith((" ", "\t"))):
                act = False
        if line.startswith("*Not this"):
            not_this = True
        elif not line.strip():
            not_this = False
        if f:
            run = f.group(1)
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1]:
                fence = None
            out.append((n, line, True, act, not_this))
            continue
        out.append((n, line, fence is not None, act, not_this))
    return out


class GalleryActsAndTerms(unittest.TestCase):
    """The worked examples are what a card is checked against: none of them carries either
    failure the floor's item 10 and its widened item 1 exist to prevent."""

    def test_the_gallery_has_to_act_on_parts(self):
        heads = [n for n, line, *_ in gallery_blocks() if ACT_HEAD.match(line)]
        self.assertGreaterEqual(len(heads), 1)

    def test_no_placeholder_outside_fences_or_in_paste_text(self):
        for n, line, in_fence, in_act, _ in gallery_blocks():
            if in_fence and not in_act:
                continue  # an example of a caller's store, not text for the operator
            m = PLACEHOLDER.search(line)
            self.assertIsNone(m, f"gallery.md:{n}: fill-in placeholder {m and m.group(0)}")

    def test_no_source_label_outside_not_this_and_fences(self):
        for n, line, in_fence, _, in_not_this in gallery_blocks():
            if in_fence or in_not_this:
                continue
            m = LABEL.search(line)
            self.assertIsNone(m, f"gallery.md:{n}: label-shaped token {m and m.group(0)}")

    def test_every_path_in_a_to_act_on_part_is_absolute(self):
        seen = 0
        for n, line, in_fence, in_act, _ in gallery_blocks():
            if not in_act or in_fence:
                continue  # a fenced paste block is the placeholder lint's
            for span in CODE_SPAN.findall(line):
                for word in span.split():
                    # quotes and brackets off both ends, trailing punctuation only:
                    # a leading dot is part of a relative path (./run.sh)
                    word = word.lstrip("'\"(").rstrip("'\".,;:)")
                    if "/" not in word:
                        continue
                    seen += 1
                    self.assertTrue(word.startswith("/") or word.startswith("https://"),
                                    f"gallery.md:{n}: {word!r} is not a /… path or an https:// URL")
        self.assertGreaterEqual(seen, 2)

    def test_the_lints_catch_what_they_are_for(self):
        """Each lint fails on the failure it names, so a clean run means something."""
        self.assertTrue(PLACEHOLDER.search("from <kit>/pb.settings.json"))
        self.assertTrue(LABEL.search("What: L2, the cleanup scope"))
        self.assertTrue(LABEL.search("serial 08, step A3"))
        self.assertFalse(LABEL.search("level 1 in the cleanup plan"))
        self.assertFalse(LABEL.search("3 of 3 pages signed in"))
        # the path lint's word cleanup keeps a relative path relative
        self.assertEqual("./run.sh,".lstrip("'\"(").rstrip("'\".,;:)"), "./run.sh")


if __name__ == "__main__":
    unittest.main()
