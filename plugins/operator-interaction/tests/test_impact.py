"""Every view of a decision shows its impact.

Two halves:

- the decision page (`decision-page` skill): its template's data check and impact
  renderers, loaded from `assets/index.html` and run under node against
  `assets/cards.example.json` and broken copies of it. A card has no card-level effect (the
  operator's v5 ruling, 2026-10-22): its Impact is wait, reach, undo and cost, each option
  carries its own effect, and the closed row shows the recommended option's, its letter first
  (answer 340 (a));
- the decisions skill's worked examples: every list line carries its effect and its
  wait, every tag-size mention the recommended option's effect, its letter first (answer
  340 (a)), and every card or block shows its impact right after its Context and any fold
  above the Impact (▸ Open questions).

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
PAGE = PLUGIN / "skills" / "decision-page" / "assets" / "index.html"
EXAMPLE = PLUGIN / "skills" / "decision-page" / "assets" / "cards.example.json"
DECISIONS = PLUGIN / "skills" / "decisions"
END_MARK = "/* ---- end of the page-free part"

NODE = shutil.which("node")
# what the page's isNone treats as saying nothing (trimmed, any case): the operator's rule of 2026-10-14
NONE = {"", "none", "none.", "n/a", "n/a.", "-", "–", "—"}


def setUpModule():
    # the page tests need node; without it they skip, and say so where the Check's
    # output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's impact tests "
              "(DecisionPageImpact) are skipped, so the page's check and renderers "
              "went untested", file=sys.stderr)

HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
const bad = check(d);
let views = [];
if (!bad.length) {
  CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow;
  byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
  views = CARDS.map(c => ({n: c.n, tag: rowEffect(c), line: impactLine(c), row: rowHtml(c),
                           more: Object.fromEntries(c.options.map(o => [o.k, optionDetail(c, o.k)])),
                           card: cardHtml(c)}));
}
process.stdout.write(JSON.stringify({bad, views}));
"""


def page_free_script():
    """The template's script up to the end-of-page-free-part marker: the helpers, the
    impact renderers and the data check, none of which touch the page."""
    html = PAGE.read_text()
    start = html.index("<script>") + len("<script>")
    end = html.index(END_MARK)
    return html[start:end]


def run_page(data, script=None):
    out = subprocess.run([NODE, "-e", (script or page_free_script()) + HARNESS],
                         input=json.dumps(data), capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def example():
    return json.loads(EXAMPLE.read_text())


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageImpact(unittest.TestCase):

    def test_example_passes_the_page_check(self):
        self.assertEqual(run_page(example())["bad"], [])

    def test_every_example_card_has_its_facets_undo_where_one_way_and_each_option_its_effect(self):
        for c in example()["cards"]:
            imp = c["impact"]
            for k in ("wait", "reach"):
                self.assertTrue(isinstance(imp.get(k), str) and imp[k].strip(), f"card {c['n']}: impact.{k}")
            # no card-level effect (the operator's v5 ruling, 2026-10-22): each option carries its own
            self.assertNotIn("effect", imp, f"card {c['n']}")
            for o in c["options"]:
                if o["k"] != "z":
                    self.assertTrue(o.get("effect", "").strip(), (c["n"], o["k"]))
            # undo only where an option is one-way or costly (answer 260 (a)): the flagged options
            flagged = [o["k"] for o in c["options"] if o.get("oneway")]
            self.assertEqual("undo" in imp, bool(flagged), f"card {c['n']}")
            for k in flagged:
                self.assertIn("(%s)" % k, imp["undo"], f"card {c['n']}")
            for o in c["options"]:
                self.assertEqual("undo" in o, bool(o.get("oneway")), (c["n"], o["k"]))
            self.assertNotIn("stakes", c, f"card {c['n']}: stakes is replaced by impact")
            # a decision with a one-way option names that option's undo, not only the rec's
            if c.get("oneway"):
                self.assertIn("(b) none", imp["undo"], f"card {c['n']}")

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    def test_a_card_without_impact_is_refused(self):
        d = example()
        del d["cards"][0]["impact"]
        self.assert_refused(d, "card 41: impact needs")

    def test_undo_is_optional_but_text(self):
        d = example()
        del d["cards"][1]["impact"]["undo"]
        self.assertEqual(run_page(d)["bad"], [])
        d = example()
        d["cards"][0]["impact"]["undo"] = "(b) switch the pipeline off"
        self.assertEqual(run_page(d)["bad"], [])
        d["cards"][0]["impact"]["undo"] = ["(b) switch the pipeline off"]
        self.assert_refused(d, "card 41: impact needs wait and reach as text (undo and cost optional, as text; "
                               "there is no card-level effect)")

    def test_each_facet_is_required_and_non_empty(self):
        for k in ("wait", "reach"):
            d = example()
            del d["cards"][1]["impact"][k]
            self.assert_refused(d, "card 42: impact needs")
            d = example()
            d["cards"][2]["impact"][k] = "  "
            self.assert_refused(d, "card 43: impact needs")

    def test_cost_is_optional_but_text(self):
        d = example()
        d["cards"][0]["impact"]["cost"] = "about 4 minutes of CI per merge"
        self.assertEqual(run_page(d)["bad"], [])
        d["cards"][0]["impact"]["cost"] = 4
        self.assert_refused(d, "card 41: impact needs")

    def test_an_options_facets_are_text_and_its_effect_required(self):
        d = example()
        d["cards"][0]["options"][0]["reach"] = ["the maintainer"]
        self.assert_refused(d, "card 41: (a) reach must be text")
        d = example()
        del d["cards"][0]["options"][1]["effect"]
        self.assert_refused(d, "card 41: (b) needs its effect")
        d = example()
        d["cards"][1]["options"][0]["cost"] = ["twelve lines"]
        self.assert_refused(d, "card 42: (a) cost must be text")
        # (z)'s effect, what waiting does, is optional
        d = example()
        del d["cards"][0]["options"][2]["effect"]
        self.assertEqual(run_page(d)["bad"], [])

    def test_a_one_way_card_needs_every_options_reach(self):
        d = example()
        del d["cards"][1]["options"][1]["reach"]
        self.assert_refused(d, "card 42: (b) needs its reach: a ⚠ one-way card gives every option but (z) its reach")

    def test_an_option_without_reach_still_shows_its_effect(self):
        d = example()
        for o in d["cards"][2]["options"]:
            o.pop("reach", None)
            o.pop("cost", None)
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        more = res["views"][2]["more"]
        self.assertIn('<span class="lbl">Effect</span><span>Links and headings turn the logo', more["b"])
        for k in ("a", "b"):
            self.assertNotIn(">Reach<", more[k])

    def test_impact_line_order_and_no_effect(self):
        res = run_page(example())
        for v, c in zip(res["views"], example()["cards"]):
            line = v["line"]
            pos = [line.index(t) for t in ("later:", "reach:", "undo:") if t != "undo:" or "undo" in c["impact"]]
            self.assertEqual(pos, sorted(pos), line)
            # one facet a line: a paragraph per facet given, no separator between them
            given = sum(1 for k in ("wait", "reach", "undo", "cost") if c["impact"].get(k))
            self.assertEqual(line.count("<p>"), given, line)
            self.assertNotIn(" · <i>", line)
            self.assertNotIn("→", line)

    def test_each_options_more_carries_its_own_facets(self):
        # Options in full went (the operator, 2026-10-14): each option's More holds its Effect, Reach, Undo, Cost
        # in that order; the Wait is the card's Impact line (later:) and (z)'s More
        d = example()
        res = run_page(d)
        for v, c in zip(res["views"], d["cards"]):
            for o in c["options"]:
                if o["k"] == "z":
                    continue
                more = v["more"][o["k"]]
                cells = [(f, x) for f, x in (("Effect", "effect"), ("Reach", "reach"), ("Undo", "undo"),
                                             ("Cost", "cost")) if x in o and (x == "undo" or o[x].strip().lower() not in NONE)]
                # an option flagged one-way marks its Undo
                lbl = lambda f: ('<span class="lbl owu">⚠ Undo</span>' if f == "Undo" and o.get("oneway")
                                 else '<span class="lbl">%s</span>' % f)
                pos = [more.index(lbl(f)) for f, _ in cells]
                # the Plan in brief comes first on every card, a ⚠ one-way card's too (F5, 08 § L1)
                self.assertTrue(more.startswith('<div class="oplan"><span class="lbl">Plan in brief</span>'), (c["n"], o["k"]))
                self.assertEqual(pos, sorted(pos), (c["n"], o["k"]))
                for _, x in cells:
                    self.assertIn(o[x][:20], more, (c["n"], o["k"], x))
            self.assertIn("<i>later:</i>", v["line"])
            self.assertIn('<span class="lbl">Wait</span>', v["more"]["z"])
            self.assertNotIn("Options in full", v["card"])
            self.assertNotIn("<table", v["card"])
        warn = res["views"][1]
        self.assertIn("The first CI publish waits for this answer.", warn["more"]["z"])
        self.assertIn("Twelve lines of redirect config to keep.", warn["more"]["a"])

    def test_impact_text_is_escaped(self):
        d = example()
        d["cards"][0]["options"][1]["effect"] = '<img src=x onerror="alert(1)">'
        d["cards"][0]["impact"]["reach"] = "<script>x</script>"
        d["cards"][0]["options"][1]["cost"] = "<b>bold</b>"
        v = run_page(d)["views"][0]
        for html in (v["tag"], v["line"], v["more"]["b"], v["row"]):
            self.assertNotIn("<img", html)
            self.assertNotIn("<script>", html)
        self.assertIn("&lt;img", v["tag"])
        self.assertIn("&lt;b&gt;bold", v["more"]["b"])

    def test_the_row_shows_the_recommended_options_effect_with_its_letter(self):
        # answer 340 (a): the closed row shows the recommended option's own effect, its letter first; with no
        # recommendation, each real option's effect in a few words
        d = example()
        for v, c in zip(run_page(d)["views"], d["cards"]):
            self.assertEqual(row_problems(v, c), [], v["n"])
        # mutants: the letter dropped; the first option's effect taken in place of the recommended one's
        for old, new, want in ((ROW_LETTER, ROW_NO_LETTER, "the row does not mark the effect with its letter"),
                               (ROW_REC, ROW_FIRST, "the row does not show the recommended option's effect")):
            with self.subTest(mutant=new):
                mutant = page_free_script().replace(old, new)
                self.assertNotEqual(mutant, page_free_script())
                v41 = run_page(example(), mutant)["views"][0]
                self.assertIn(want, row_problems(v41, d["cards"][0]))

    def test_with_no_recommendation_each_effect_is_cut_to_a_few_words(self):
        # ROW_FEW (6): card 43 has no recommendation; its (a) effect is 7 words, its (b) 12
        self.assertIn("const ROW_FEW=6;", page_free_script())
        tag = run_page(example())["views"][2]["tag"]
        self.assertEqual(few_problems(tag), [])
        mutant = page_free_script().replace("const ROW_FEW=6;", "const ROW_FEW=12;")
        self.assertTrue(few_problems(run_page(example(), mutant)["views"][2]["tag"]))

    def test_the_page_renders_impact_in_every_view(self):
        # the open card, rendered: its Impact line, the effect on its row (its summary), and each option's own
        # effect in its More; the Impact has no effect facet (no card-level effect)
        for v in run_page(example())["views"]:
            card = v["card"]
            self.assertIn('class="impline"', card, v["n"])
            self.assertIn(v["line"], card, v["n"])
            summary = card[:card.index("</summary>")]
            self.assertIn('class="eff"', summary, v["n"])
            self.assertEqual(effect_facet_problems(card), [], v["n"])
            for k, more in v["more"].items():
                self.assertIn(more, card, (v["n"], k))
                if k != "z":
                    self.assertIn('<span class="lbl">Effect</span>', more, (v["n"], k))
        # mutant: an effect facet restored in the Impact (and an effect given)
        d = example()
        d["cards"][0]["impact"]["effect"] = "sets where the docs build runs"
        mutant = page_free_script().replace('const IMP_FACETS=[["wait"', 'const IMP_FACETS=[["effect","→","Effect"],["wait"')
        self.assertNotEqual(mutant, page_free_script())
        card = run_page(d, mutant)["views"][0]["card"]
        self.assertTrue(effect_facet_problems(card))
        # the real template ignores an effect an older writer left
        self.assertEqual(effect_facet_problems(run_page(d)["views"][0]["card"]), [])


ROW_LETTER = "'<span class=\"rl\">('+esc(c.rec)+')</span>'+fmtPlain(o.effect)"
ROW_NO_LETTER = "fmtPlain(o.effect)"
ROW_REC = "const o=optOf(c,c.rec);"
ROW_FIRST = "const o=optsOf(c)[0];"


def few_problems(tag):
    """Card 43's row with no recommendation: each option's effect cut at six words, then an ellipsis."""
    out = []
    for want in ('<span class="rl">(a)</span>No visual change; the site stays …',
                 '<span class="rl">(b)</span>Links and headings turn the logo&#39;s …'):
        if want not in tag:
            out.append("not cut at six words: " + want)
    if "blue." in tag or "CI publish" in tag:
        out.append("an effect shown past six words")
    return out


def effect_facet_problems(card):
    """An Impact that shows a card-level effect: an arrow or an Effect heading inside the Impact block."""
    out = []
    for m in re.finditer(r'<div class="impline">.*?</div>', card, re.S):
        if "→" in m.group(0) or ">Effect</h4>" in m.group(0):
            out.append("the Impact shows a card-level effect")
    return out


def row_problems(v, c):
    """A row without the rec pill (or its no-recommendation label), or without the recommended option's effect
    marked with its letter (each real option's, lettered, with no recommendation)."""
    out = []
    row = v["row"]
    if v["tag"] not in row or "<b>→</b>" not in v["tag"]:
        out.append("the row shows no effect")
    if 'class="pill rec"' not in row and 'class="pill none"' not in row:
        out.append("the row has no rec pill")
    eff = {o["k"]: o.get("effect", "") for o in c["options"]}
    if c["rec"]:
        if '<span class="rl">(%s)</span>' % c["rec"] not in v["tag"]:
            out.append("the row does not mark the effect with its letter")
        if eff[c["rec"]].split("[[")[0][:20] not in v["tag"]:
            out.append("the row does not show the recommended option's effect")
    else:
        for k, e in eff.items():
            if k != "z" and ('<span class="rl">(%s)</span>' % k not in v["tag"] or e.split()[0] not in v["tag"]):
                out.append("the row does not show option (%s)'s effect" % k)
    return out
LIST_LINE = re.compile(r"^- \*\*\d+ .+\?\*\* — ")
CARD_HEAD = re.compile(r"^\*\*\d+ — [^*]+\?\*\*")


FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})")


def finding_end(lines, j):
    """The index after a card's Finding part (F7, answer 337 (a)), which opens at lines[j] on
    **Finding:**: its head line, its mechanism on the next line, then any fenced excerpt, its
    fence of three or more backticks or tildes closed by a run of the same mark at least as long."""
    j += 1
    if j < len(lines) and lines[j].strip() and not lines[j].startswith(("```", "~~~", "▸ ", "▾ ", "**")):
        j += 1  # the mechanism
    m = FENCE_OPEN.match(lines[j]) if j < len(lines) else None
    if m:
        fence = m.group(1)
        close = re.compile("^" + re.escape(fence[0]) + "{%d,}\\s*$" % len(fence))
        j += 1
        while j < len(lines) and not close.match(lines[j]):
            j += 1
        j += 1  # the closing fence
    return j
# a tag-size mention, `46 (→ …)`
TAG_SIZE = re.compile(r"\b\d+ \(→ ")
TAG_EXAMPLE = "46 (→ (a) preview up in about 4 minutes)"
OLD_TAG_EXAMPLE = "46 (→ (a) preview up in about 4 minutes; (b) yesterday's page)"


def tag_size_problems(where, text):
    """Each tag-size mention opens on an option's letter, `N (→ (x) …`, and the worked example
    shows the recommended option's effect alone. Returns the problems, empty when clean."""
    out = []
    flat = " ".join(text.split())
    for m in TAG_SIZE.finditer(flat):
        if not re.match(r"\(([a-y]|x)\) ", flat[m.end():]):
            out.append(f"{where}: a tag size without its letter first: {flat[m.start():m.start() + 40]!r}")
    if OLD_TAG_EXAMPLE in flat:
        out.append(f"{where}: the tag size gives every option's effect where one is recommended")
    return out


class GalleryShowsImpact(unittest.TestCase):
    """The worked examples are what a rendering is checked against: each shows impact at
    its size."""

    def files(self):
        return [DECISIONS / "references" / "gallery.md",
                DECISIONS / "references" / "rendering.md"]

    def test_every_list_line_has_effect_and_wait(self):
        seen = 0
        for f in self.files():
            for n, line in enumerate(f.read_text().splitlines(), 1):
                if LIST_LINE.match(line):
                    seen += 1
                    self.assertIn(" → ", line, f"{f.name}:{n}")
                    self.assertIn("*later: ", line, f"{f.name}:{n}")
                    self.assertNotRegex(line, r"reversible, (narrow|wide)|one-way, narrow",
                                        f"{f.name}:{n}: a stakes word on a line")
        self.assertGreater(seen, 20)

    def test_tag_size_shows_the_recommended_options_effect_with_its_letter(self):
        files = self.files() + [DECISIONS / "SKILL.md"]
        for f in files:
            self.assertEqual(tag_size_problems(f.name, f.read_text()), [])
        for f in self.files():
            self.assertIn(TAG_EXAMPLE, " ".join(f.read_text().split()), f.name)
        # mutants: the old example, across the options; a tag size with no letter
        self.assertTrue(tag_size_problems("mutant", "`decisions needed: " + OLD_TAG_EXAMPLE + "`"))
        self.assertTrue(tag_size_problems("mutant", "*46 (→ preview up in about 4 minutes)*"))

    def test_every_card_and_block_shows_its_impact_right_after_its_context(self):
        # the answer page's order: the title, Context, What (a set's item bullets under it), any Finding, then the folds
        # above the Impact (▸ Open questions, then ▸ Assumptions, open as ▾ with their contents in
        # a block), then the impact; a Context section is a line, or a heading over bullets (a block)
        seen = 0
        for f in self.files():
            lines = f.read_text().splitlines()
            for i, line in enumerate(lines):
                if not CARD_HEAD.match(line):
                    continue
                seen += 1
                j = i + 1
                in_context = False
                while j < len(lines):
                    x = lines[j]
                    if x.startswith("**Context:**"):
                        in_context = True
                    elif x.startswith(("▸ ", "▾ ")):
                        in_context = True  # a fold above the Impact, and an open fold's bullets
                    elif in_context and x.startswith(("- ", "  - ")):
                        pass  # a block's Context bullets
                    elif in_context and x.startswith(("**Basis:**", "*Evidence:*", "  *tripwire:*")):
                        pass  # an open Assumptions fold: its Basis line, evidence and tripwires
                    elif x.startswith("**Finding:**"):
                        j = finding_end(lines, j)  # the Finding, after What (F7)
                        continue
                    elif x.strip() and not x.startswith(("*While it waited", "**What:**", "**Scope:**", "**Likelihood:**", "**Best response?:**")):
                        break
                    else:
                        in_context = in_context and bool(x.strip())
                    j += 1
                self.assertTrue(lines[j].startswith("**Impact:**")
                                or lines[j].startswith("| Impact |"),
                                f"{f.name}:{i + 1}: {line[:60]} is followed by {lines[j][:40]!r}")
        self.assertGreaterEqual(seen, 10)


if __name__ == "__main__":
    unittest.main()
