"""Every page card carries the decisions block's depth, a click away (decision 198).

Two parts:

- the decision page (`decision-page` skill): the `detail` field and its check, the
  `evidence` shapes, each part's detail levels and its toggle, the **More** button and its
  option detail, links in the levels only, and the folds kept; loaded from
  `assets/index.html` and run under node against `assets/cards.example.json` and copies of it;
- the pre-publish runner's depth lints, `scripts/check_cards.js`: levels optional on every
  part (decision 201), each level longer than the one below, the sizes read at the top
  level with thin depth linted only where a part has levels, an option but (z) with no reach, the
  long card, an unknown `detail` key, and the term lints on the visible parts' levels,
  against Context's summary.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_impact import NODE, PAGE, example, page_free_script
from test_context import RUNNER, runner


def setUpModule():
    # the page and runner tests need node; without it they skip, and say so where the
    # Check's output shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's depth tests "
              "(DecisionPageDepth, DepthRunner) are skipped, so the detail levels, the More "
              "button and the depth lints went untested", file=sys.stderr)


# a list of data files in; each one's check() result and its cards rendered out, with
# the page-free helpers the tests probe one by one
HARNESS = r"""
const ds = JSON.parse(require("fs").readFileSync(0, "utf8"));
const out = ds.map(d => {
  const bad = check(d);
  let cards = [];
  if (!bad.length) {
    CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow;
    byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
    cards = CARDS.map(c => ({n: c.n, html: cardHtml(c), parts: parts(c),
      more: Object.fromEntries(c.options.map(o => [o.k, optionDetail(c, o.k)])),
      act: Object.fromEntries(c.options.map(o => [o.k, actList(c, o.k)]))}));
  }
  return {bad, cards};
});
const steps = {two: [nextLevel(0, 2), nextLevel(1, 2), nextLevel(2, 2)], one: [nextLevel(0, 1), nextLevel(1, 1)],
  text: [lvText(0, 2), lvText(1, 2), lvText(2, 2), lvText(0, 1), lvText(1, 1)]};
process.stdout.write(JSON.stringify({out, steps}));
"""

LINK_HARNESS = r"""
const xs = JSON.parse(require("fs").readFileSync(0, "utf8"));
REFS = {"38": {short: "see https://x.example.com/p", q: "q", a: "a", when: "w"}};
process.stdout.write(JSON.stringify(xs.map(s => ({d: fmtD(s), f: fmt(s), p: fmtPlain(s)}))));
"""


def node(script, data):
    out = subprocess.run([NODE, "-e", page_free_script() + script], input=json.dumps(data),
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def run_pages(datasets):
    return node(HARNESS, datasets)


def run_page(data):
    return run_pages([data])["out"][0]


def card(res, n):
    return next(c for c in res["cards"] if c["n"] == n)


def secs(html):
    """Each part with levels: (key, data-max, the HTML of its renditions in order). Every part opens
    at its summary (data-lvl 0) but an option's text in its More, which opens at its fullest."""
    out = []
    for m in re.finditer(r'<div class="sec" data-n="\d+" data-sec="([^"]+)" data-lvl="(\d+)" '
                         r'data-max="(\d+)">', html):
        start = opens_at(html, m.group(1), int(m.group(3)))
        assert int(m.group(2)) == start, m.group(0)
        body = html[m.end():]
        out.append((m.group(1), int(m.group(3)), body))
    return out


def opens_at(html, key, mx):
    """The level a part opens at: its summary, but an older option's text in its view, which opens at its fullest.
    An option's Plan in brief (F5) opens at its summary, the plan."""
    if not key.startswith("opt-"):
        return 0
    plan = r'<span class="lbl">Plan in brief</span><div class="sec" data-n="\d+" data-sec="%s"' % key
    return 0 if re.search(plan, html) else mx


def renditions(html, n, key):
    """The renditions of part key on card n, as rendered: [(hidden, inner html), …]."""
    start = html.index('<div id="d%s-%s" data-secbody>' % (n, key))
    rest = html[start:]
    out = []
    pos = len('<div id="d%s-%s" data-secbody>' % (n, key))
    while rest.startswith('<div class="lv"', pos):
        hidden = rest.startswith('<div class="lv" hidden>', pos)
        open_tag = '<div class="lv" hidden>' if hidden else '<div class="lv">'
        i, depth = pos + len(open_tag), 1
        j = i
        while depth:
            a, b = rest.find("<div", j), rest.find("</div>", j)
            if a != -1 and a < b:
                depth, j = depth + 1, a + 4
            else:
                depth, j = depth - 1, b + 6
        out.append((hidden, rest[i:j - 6]))
        pos = j
    return out


WORDS200 = " ".join(["word"] * 200)


def upper_folds(html):
    """The labels of a card's folds above its Impact (Open questions, Assumptions), in order."""
    head = html[:html.index('class="impline"')]
    return re.findall(r'<details class="gfold [a-z]+fold"><summary><span class="lbl">([^<]+)</span>', head)


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageDepth(unittest.TestCase):

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    # ---- the data

    def test_the_example_passes_with_facets_on_every_option_and_levels_scaled_to_each_card(self):
        d = example()
        self.assertEqual(run_page(d)["bad"], [])
        for c in d["cards"]:
            for o in c["options"][:-1]:
                self.assertTrue(o.get("effect") and o.get("reach"), (c["n"], o["k"]))
            if c["n"] == 43:
                # the small call carries no levels (decision 201)
                self.assertNotIn("detail", c)
                continue
            for k in ("context", "impact", "tldr", "rec"):
                self.assertEqual(len(c["detail"][k]), 2, (c["n"], k))
        self.assertIsInstance(d["cards"][0]["evidence"], str)
        high = d["cards"][0]["detail"]["evidence"][1]
        self.assertTrue(all(isinstance(x, dict) and "h" in x for x in high), high)

    def test_a_card_with_no_levels_renders_with_more_buttons(self):
        d = example()
        for c in d["cards"]:
            c.pop("detail", None)
            for o in c["options"]:
                o.pop("detail", None)
                if not c.get("oneway"):
                    o.pop("reach", None)
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        for c in res["cards"]:
            self.assertNotIn("lvb", c["html"], c["n"])
            self.assertNotIn('class="sec"', c["html"], c["n"])
            self.assertEqual(c["html"].count(">More</button>"), 3, c["n"])
        # with no reach, the option detail shows its effect and leaves Reach out
        self.assertIn("No visual change; the site stays blue.", card(res, 43)["more"]["a"])
        self.assertNotIn(">Reach<", card(res, 43)["more"]["a"])

    def test_detail_null_is_absent_and_an_unknown_key_passes_the_page(self):
        d = example()
        d["cards"][0]["detail"] = None
        d["cards"][1]["detail"]["later"] = ["x"]
        self.assertEqual(run_page(d)["bad"], [])

    def test_malformed_detail_is_refused_with_its_message(self):
        cases = [
            (lambda c: c.__setitem__("detail", ["x"]), "card 41: detail must be an object"),
            (lambda c: c.__setitem__("detail", "x"), "card 41: detail must be an object"),
            (lambda c: c["detail"].__setitem__("why", []), "card 41: detail.why must be [medium, high]"),
            (lambda c: c["detail"].__setitem__("why", ["a", "b", "c"]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [3]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("context", ["a", []]), "card 41: detail.context must be"),
            (lambda c: c["detail"].__setitem__("impact", [{"effect": "x"}]), "card 41: detail.impact must be"),
            (lambda c: c["detail"].__setitem__("impact", [{"wait": "x", "cost": 4}]), "card 41: detail.impact must be"),
            (lambda c: c["detail"].__setitem__("tldr", ["a bullet"]), "card 41: detail.tldr must be"),
            (lambda c: c["detail"].__setitem__("tldr", [[]]), "card 41: detail.tldr must be"),
            (lambda c: c["detail"].__setitem__("o", {"a": ["x"]}), "card 41: detail.o is an older field"),
            (lambda c: c["options"][0].__setitem__("detail", "x"), "card 41: (a) detail must be [medium, high]"),
            (lambda c: c["options"][0].__setitem__("detail", ["a", "b", "c"]), "card 41: (a) detail must be"),
            # the shapes: a bullet {t, sub}, a section {h, b}; nothing deeper, nothing mixed
            (lambda c: c["detail"].__setitem__("why", [[{"t": 3}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [[{"t": "x", "sub": [3]}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [[{"t": "x", "sub": [{"t": "y"}]}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [[{"h": "", "b": ["x"]}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [[{"h": "x", "b": []}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [["x", {"h": "y", "b": ["z"]}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("why", [[{"t": "x", "h": "y", "b": ["z"]}]]), "card 41: detail.why must be"),
            (lambda c: c["detail"].__setitem__("impact", [{"wait": [3]}]), "card 41: detail.impact must be"),
            (lambda c: c["detail"].__setitem__("impact", [{"reach": {"t": "x", "h": "y"}}]), "card 41: detail.impact must be"),
            (lambda c: c["detail"].__setitem__("tldr", ["a bullet", "b"]), "card 41: detail.tldr must be"),
        ]
        datasets = []
        for put, _ in cases:
            d = example()
            put(d["cards"][0])
            datasets.append(d)
        for (_, needle), res in zip(cases, run_pages(datasets)["out"]):
            self.assertTrue(any(needle in b for b in res["bad"]), (needle, res["bad"]))

    def test_a_rec_bullet_in_a_detail_tldr_is_refused_naming_its_level_and_bullet(self):
        # numbered in reading order: each heading, then each bullet and its sub-bullets
        d = example()
        d["cards"][0]["detail"]["tldr"][1][1]["b"][0] = "Rec: move it to CI"
        self.assert_refused(d, "card 41: detail.tldr high bullet 5 carries the recommendation: "
                               "the options mark it; say what is decided instead")
        d = example()
        d["cards"][0]["detail"]["tldr"][0][1]["sub"][0] = "I recommend CI"
        self.assert_refused(d, "card 41: detail.tldr medium bullet 4 carries the recommendation")
        d = example()
        d["cards"][0]["detail"]["tldr"][1][0]["h"] = "Recommended: (b)"
        self.assert_refused(d, "card 41: detail.tldr high bullet 1 carries the recommendation")

    def test_evidence_is_text_or_a_non_empty_list_of_text(self):
        for bad in (3, [], [1], [""], {"a": "b"}):
            d = example()
            d["cards"][0]["evidence"] = bad
            self.assert_refused(d, "card 41: evidence must be text or a non-empty list of text")
        d = example()
        d["cards"][0]["evidence"] = ["Observed: one.", "Inferred: two."]
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        ev = card(res, 41)["parts"]["ev"][0]
        self.assertEqual(ev.count("<li>"), 2)
        self.assertTrue(ev.startswith("<ul"))

    # ---- the levels

    def test_every_part_with_levels_opens_at_its_summary_with_one_rendition_shown(self):
        res = run_page(example())
        seen = set()
        for c in res["cards"]:
            for key, mx, _ in secs(c["html"]):
                rs = renditions(c["html"], c["n"], key)
                self.assertEqual(len(rs), mx + 1, (c["n"], key))
                self.assertEqual(len(c["parts"][key]), mx + 1, (c["n"], key))
                # shown: the summary (a plan in brief too), or an older option's fullest level in its view
                at = opens_at(c["html"], key, mx)
                self.assertEqual([h for h, _ in rs], [i != at for i in range(mx + 1)], (c["n"], key))
                self.assertEqual(rs[0][1], c["parts"][key][0], (c["n"], key))
                seen.add(key)
        self.assertTrue({"ctx", "imp", "tldr", "rec", "why", "whyask", "ev", "opt-a"} <= seen, seen)
        # a part with only its summary has no toggle: every part of card 43, any card's Depends on,
        # an option's text in its More with no levels ((z)'s)
        self.assertNotIn('class="sec"', card(res, 43)["html"])
        self.assertNotIn('data-sec="dep"', card(res, 42)["html"])
        self.assertNotIn('data-sec="opt-z"', card(res, 41)["html"])

    def test_each_toggle_is_a_button_naming_its_part_and_next_step(self):
        res = run_page(example())
        ids = []
        for c in res["cards"]:
            html = c["html"]
            ids += re.findall(r'\bid="([^"]+)"', html)
            for m in re.finditer(r'<button[^>]*class="btn lvb"[^>]*>([^<]*)</button>', html):
                tag = m.group(0)
                self.assertTrue(tag.startswith('<button type="button"'), tag)
                # an older option's text in its view opens at its fullest: its button steps to less detail; a plan
                # in brief opens at the plan
                older = 'data-lv="opt-' in tag and 'data-lbl="Plan in brief' not in tag
                step, exp = (("less detail", "true") if older else ("more detail", "false"))
                self.assertIn('aria-expanded="%s"' % exp, tag)
                self.assertEqual(m.group(1), step)
                label = re.search(r'data-lbl="([^"]+)"', tag).group(1)
                self.assertIn('aria-label="%s: %s"' % (label, step), tag)
            for ctl in re.findall(r'aria-controls="([^"]+)"', html):
                self.assertIn('id="%s"' % ctl, html)
        self.assertEqual(len(ids), len(set(ids)), "ids are unique across the page")

    def test_a_level_replaces_the_text_and_context_keeps_its_label(self):
        res = run_page(example())
        c = card(res, 41)
        ctx = c["parts"]["ctx"]
        for r in ctx:
            self.assertTrue(r.startswith('<div class="ctx"><span class="lbl">Context</span>'), r[:60])
        # more detail is bullets, full detail headed sections
        self.assertIn('<ul class="lvl">', ctx[1])
        self.assertNotIn('<h4 class="lvh">', ctx[1])
        self.assertIn('<h4 class="lvh">', ctx[2])
        self.assertIn("answered: clear it", ctx[2])
        self.assertNotIn("answered: clear it", ctx[1])
        # the Impact: medium one bullet per facet, high a section per facet, in the one vocabulary
        med = c["parts"]["imp"][1]
        # card 41's options are both reversible at little cost, so it has no undo at any level
        pos = [med.index(t) for t in ("<li><i>later:</i>", "<li><i>reach:</i>", "<li><i>cost:</i>")]
        self.assertEqual(pos, sorted(pos))
        self.assertNotIn("undo:", med)
        self.assertNotIn("→", med)
        self.assertIn('<ul class="lvl sub">', med)
        high = c["parts"]["imp"][2]
        pos = [high.index('<h4 class="lvh">%s</h4>' % t) for t in ("Wait", "Reach", "Cost")]
        self.assertEqual(pos, sorted(pos))
        self.assertNotIn(">Undo<", high)
        self.assertNotIn(">Effect<", high)
        # card 42's undo is its one-way option's, marked at every level
        imp = card(res, 42)["parts"]["imp"]
        self.assertIn('<p><i class="owu">⚠ undo:</i> (b) none', imp[0])
        self.assertIn('<li><i class="owu">⚠ undo:</i> (b) one-way', imp[1])
        self.assertIn('<h4 class="lvh">⚠ Undo</h4>', imp[2])
        # the basis line, in the Assumptions fold: its label and word in a box at every level, then the
        # reason, which a level replaces (its bullets)
        rec = c["parts"]["rec"]
        for r in rec:
            self.assertTrue(r.startswith('<div class="basisl"><span class="lbl">Basis</span>'
                                         '<span class="bw">strong</span>'), r[:120])
        self.assertTrue(rec[1].startswith('<div class="basisl"><span class="lbl">Basis</span><span class="bw">'
                                          'strong</span><ul class="lvl">'), rec[1][:120])
        self.assertIn("both failures were read in the build logs", rec[0])
        self.assertNotIn("unknown", rec[1])
        # no Rec head: the recommendation is marked on its option, never on the basis line
        self.assertNotIn("Rec <strong>", c["html"])
        # a rec level as one string shows as the reason does
        d = example()
        d["cards"][0]["detail"]["rec"] = ["both failures read in the build logs",
                                          "both failures read in the build logs, the same cache both times"]
        old = card(run_page(d), 41)["parts"]["rec"]
        # a space between the word's box and the reason, at the summary and at a one-string level
        self.assertEqual(old[1], '<div class="basisl"><span class="lbl">Basis</span><span class="bw">strong'
                                 '</span> both failures read in the build logs</div>')
        self.assertIn('<span class="bw">strong</span> both failures were read', rec[0])
        # the summary basis line holds no unknown: what is not known is the Open questions fold
        self.assertNotIn("unknown", c["parts"]["rec"][0])
        # Why ask keeps its class first at every level
        for r in c["parts"]["whyask"]:
            self.assertIn("<em>trust</em>", r)
            self.assertLess(r.index("<em>trust</em>"), r.index("Moving the build") if "Moving the build" in r
                            else r.index("Today one person"))

    def test_the_folds_stay_in_order_and_closed_with_no_options_in_full(self):
        # the operator (2026-10-14): Options in full repeated each option's More, so it is gone;
        # Dependencies shows only on a card that depends on something (card 41 does not)
        # the v5 layout: the upper folds (Open questions where there is one, Assumptions on every card) above
        # the Impact; the bottom folds (Background, then Dependencies until the dependency line lands, then
        # Rejected alternatives, last: F2) after the answer. The Evidence pane is gone into the Assumptions fold
        res = run_page(example())
        for c in res["cards"]:
            panes = re.findall(r'<details class="pane"( open)?><summary>([^<]+?)(?: <span class="fsum">.*?</span>)?</summary>', c["html"])
            want = (["Background"] + (["Attached"] if c["n"] == 41 else []) + (["Dependencies"] if c["n"] != 41 else [])
                    + (["Rejected alternatives"] if c["n"] == 41 else []))
            self.assertEqual([p[1] for p in panes], want, c["n"])
            self.assertEqual([p[0] for p in panes], [""] * len(want), c["n"])
            self.assertEqual(upper_folds(c["html"]), (["Open questions"] if c["n"] != 43 else []) + ["Assumptions"],
                             c["n"])
            self.assertNotIn('<details class="gfold afold" open', c["html"])
            self.assertLess(c["html"].index('<details class="gfold afold">'), c["html"].index('class="impline"'), c["n"])
            self.assertNotIn("Options in full", c["html"])
            from test_impact import before_attached
            self.assertNotIn("<table", before_attached(c["html"]))

    def test_the_rendered_order_of_a_card(self):
        res = run_page(example())
        h = card(res, 41)["html"]
        marks = ['data-sec="tldr"', 'data-sec="ctx"', '<details class="gfold ofold">',
                 '<details class="gfold afold">', '<span class="gsum">basis: strong · 2 assumptions with tripwires',
                 'data-sec="rec"', '<span class="lbl">Basis</span>', 'data-sec="ev"', '<ul class="asm">',
                 'data-sec="imp"',
                 "If unanswered:", "<fieldset>",
                 'id="d41-a"', 'data-omore="a"', 'id="d41-a-more"', 'data-sec="opt-a"', 'id="d41-b"',
                 'data-omore="b"', 'class="act"', 'id="d41-b-more"', 'data-sec="opt-b"', 'id="d41-z"',
                 'id="d41-z-more"', 'class="follow"',
                 '<summary>Background <span class="fsum">why now: ', 'data-sec="why"', 'data-sec="whyask"']
        self.assertNotIn("<summary>Evidence</summary>", h)
        self.assertNotIn("Recommendation", h)
        pos = [h.index(m) for m in marks]
        self.assertEqual(pos, sorted(pos), [m for m, p in zip(marks, pos)])

    def test_the_evidence_placeholder_holds_a_summary_it_lacks(self):
        d = example()
        d["cards"][1].pop("evidence")
        res = run_page(d)
        ev = card(res, 42)["parts"]["ev"]
        self.assertEqual(len(ev), 3)
        self.assertIn("Not summarised: more detail shows the evidence.", ev[0])
        # neither: no Evidence part, as today
        d["cards"][1]["detail"].pop("evidence")
        h = card(run_page(d), 42)["html"]
        self.assertNotIn('data-sec="ev"', h)
        self.assertNotIn("Not summarised", h)

    # ---- the More button

    def test_more_sits_beside_each_option_outside_its_label(self):
        res = run_page(example())
        for c in res["cards"]:
            h = c["html"]
            # a slug may sit in a one line; the More button never does
            for lab in re.findall(r'<label class="optl">.*?</label>', h, re.S):
                self.assertNotIn("omore", lab, c["n"])
                self.assertNotIn(">More</button>", lab, c["n"])
            for opt in re.findall(r'<div class="opt(?: isrec)?">.*?(?=<div class="opt[ "]|</div><div class="follow")', h, re.S):
                k = re.search(r'value="([a-z])"', opt).group(1)
                # (z) too, since Options in full went: its view and its impact live there now.
                # Every view starts closed, a ⚠ one-way card's too (F5, 08 § L1): picking opens it
                is_open = False
                self.assertEqual(opt.count(">More</button>"), 1, (c["n"], k))
                btn = re.search(r'<button[^>]*data-omore[^>]*>More</button>', opt).group(0)
                self.assertTrue(btn.startswith('<button type="button" class="btn omore%s"' % (" on" if is_open else "")), btn)
                self.assertIn('aria-label="More decision detail on option (%s)"' % k, btn)
                self.assertIn('aria-expanded="%s"' % str(is_open).lower(), btn)
                self.assertIn('aria-controls="d%s-%s-more"' % (c["n"], k), btn)
                self.assertIn('<div class="odet" id="d%s-%s-more"%s>' % (c["n"], k, "" if is_open else " hidden"), opt)
                self.assertLess(opt.index("</label>"), opt.index(btn))
                self.assertLess(opt.index(btn), opt.index('class="odet"'))

    def test_the_option_view_opens_on_its_plan_then_its_facets(self):
        d = example()
        del d["cards"][0]["options"][0]["cost"]
        res = run_page(d)
        more = card(res, 41)["more"]
        # its plan in brief, labelled, opens at the plan, and its levels step from it, so none is lost
        self.assertTrue(more["b"].startswith('<div class="oplan"><span class="lbl">Plan in brief</span><div class="sec"'), more["b"][:120])
        rs = renditions(more["b"], 41, "opt-b")
        self.assertEqual([h for h, _ in rs], [False, True, True])
        self.assertEqual(rs[0][1], "<p>CI builds and publishes the site on every merge to <code>main</code>, with a deploy token "
                                   "you add as a CI secret. The laptop build stays for previews only.</p>")
        self.assertTrue(rs[2][1].startswith('<div class="lvs"><h4 class="lvh">What happens</h4><ul class="lvl">'
                                            "<li>Build and publish from CI on every merge to <code>main</code>; "
                                            "the laptop build stays for previews only."), rs[2][1][:200])
        # its plan, then its own facets; the separate impact line is gone (it is the option's effect)
        self.assertNotIn('<p class="impact">', more["b"])
        self.assertLess(more["b"].index('class="sec"'), more["b"].index('<span class="lbl">Effect</span>'))
        pos = [more["b"].index('<span class="lbl">' + f + "</span>") for f in ("Effect", "Reach", "Cost")]
        self.assertEqual(pos, sorted(pos))
        # an option with no undo is reversible at little cost: no Undo line
        self.assertNotIn(">Undo<", more["b"])
        self.assertNotIn(">Cost<", more["a"])
        # (z): its plan and its effect, labelled Wait
        self.assertTrue(more["z"].startswith('<div class="oplan"><span class="lbl">Plan in brief</span><p>Nothing is set up;'), more["z"])
        self.assertIn('<span class="lbl">Wait</span><span>The local build stays until you answer', more["z"])

    def test_an_older_option_with_no_plan_shows_its_text_at_its_fullest(self):
        # 07 § F5's older slot: a card with no plan shows its text in the plan's place, at its fullest level
        d = example()
        o = d["cards"][0]["options"][1]
        o.pop("plan")
        o["text"] = "Build and publish from CI on every merge to main, with the local build kept for previews."
        d["cards"][0]["options"][2].pop("plan")
        d["cards"][0]["options"][2]["text"] = "Decide later."
        more = card(run_page(d), 41)["more"]
        self.assertNotIn("Plan in brief", more["b"])
        rs = renditions(more["b"], 41, "opt-b")
        self.assertEqual([h for h, _ in rs], [True, True, False])
        self.assertTrue(rs[2][1].startswith('<div><span class="mono ol">(b)</span><div class="lvs"><h4 class="lvh">'
                                            'What happens</h4>'), rs[2][1][:200])
        self.assertIn("Build and publish from CI on every merge to main, with the local build kept", rs[0][1])
        # the text in the plan's place: then the table, then the facets
        self.assertLess(more["b"].index('class="sec"'), more["b"].index('class="opc"'))
        self.assertLess(more["b"].index('class="opc"'), more["b"].index('<span class="lbl">Effect</span>'))
        self.assertTrue(more["z"].startswith('<p><span class="mono ol">(z)</span> Decide later.</p>'), more["z"])
        # without levels, the option's own text; with neither plan nor text, its levels alone
        o.pop("detail")
        self.assertTrue(card(run_page(d), 41)["more"]["b"].startswith('<p><span class="mono ol">(b)</span> Build and publish'))
        # a none plan is no plan
        d = example()
        d["cards"][0]["options"][0]["plan"] = "None."
        d["cards"][0]["options"][0]["text"] = "Keep building on a laptop."
        self.assertNotIn("Plan in brief", card(run_page(d), 41)["more"]["a"])

    # ---- escaping and links

    def test_every_level_and_the_option_detail_escape(self):
        x = '<img src=x onerror="alert(1)">'
        d = example()
        c = d["cards"][0]
        dt = c["detail"]
        dt["context"][0][1]["sub"][0] += x          # a sub-bullet
        dt["context"][1][0]["h"] += x               # a section heading
        dt["why"][1][0]["b"][0] += x                # a section bullet
        dt["impact"][1]["reach"][0] += x            # an impact facet's list item
        dt["impact"][0]["wait"]["sub"][0] += x      # an impact facet's sub-bullet
        dt["tldr"][0][0]["t"] += x
        dt["rec"][1][0]["b"][0] += x
        c["options"][0]["detail"][1][0]["b"][0] += x
        dt["evidence"][1][0]["b"][0] += x
        c["options"][0]["reach"] += x
        c["evidence"] = ["one " + x]
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        h = card(res, 41)["html"]
        self.assertNotIn("<img", h)
        self.assertGreaterEqual(h.count("&lt;img"), 11)

    def test_links_are_https_only_and_stay_clean(self):
        probes = [
            "see https://a.example.com/x?b=1&c=2.",
            "(https://a.example.com/p)",
            "javascript:alert(1) and http://a.example.com",
            'at https://a.example.com/q" onmouseover="x',
            "https://a.example.com/p's page",
            "`https://a.example.com/c`",
            "[[38]] then https://b.example.com/",
        ]
        r = node(LINK_HARNESS, probes)
        a = lambda u: '<a href="%s" target="_blank" rel="noopener">%s</a>' % (u, u)
        self.assertIn(a("https://a.example.com/x?b=1&amp;c=2") + ".", r[0]["d"])
        self.assertIn("(" + a("https://a.example.com/p") + ")", r[1]["d"])
        self.assertNotIn("<a ", r[2]["d"])
        self.assertIn(a("https://a.example.com/q") + "&quot;", r[3]["d"])
        self.assertIn(a("https://a.example.com/p") + "&#39;s", r[4]["d"])
        self.assertIn("<code>" + a("https://a.example.com/c") + "</code>", r[5]["d"])
        # a URL inside a slug's short name stays text; one beside it links
        slug = re.search(r"<button[^>]*>.*?</button>", r[6]["d"]).group(0)
        self.assertNotIn("<a", slug)
        self.assertIn(a("https://b.example.com/"), r[6]["d"])
        for x in r:
            self.assertNotIn("<a ", x["f"])
            self.assertNotIn("<a ", x["p"])

    def test_a_closing_bracket_the_url_opened_stays_in_the_link(self):
        probes = [
            "see https://en.wikipedia.org/wiki/Foo_(bar).",
            "(see https://en.wikipedia.org/wiki/Foo_(bar))",
            "(https://a.example.com/p).",
            "https://a.example.com/x[1]",
            "[https://a.example.com/y]",
        ]
        r = node(LINK_HARNESS, probes)
        a = lambda u: '<a href="%s" target="_blank" rel="noopener">%s</a>' % (u, u)
        self.assertIn(a("https://en.wikipedia.org/wiki/Foo_(bar)") + ".", r[0]["d"])
        self.assertIn(a("https://en.wikipedia.org/wiki/Foo_(bar)") + ")", r[1]["d"])
        self.assertIn("(" + a("https://a.example.com/p") + ").", r[2]["d"])
        self.assertIn(a("https://a.example.com/x[1]"), r[3]["d"])
        self.assertIn("[" + a("https://a.example.com/y") + "]", r[4]["d"])

    def test_links_in_levels_and_folds_never_in_summaries_or_static_parts(self):
        url = "https://z.example.com/doc"
        d = example()
        c = d["cards"][0]
        c["tldr"][0] += " " + url
        c["impact"]["reach"] += " " + url
        c["options"][0]["line"] += " " + url    # an option's one line, static
        c["options"][0]["reach"] += " " + url   # an option's facet: links in More
        c["options"][1]["act"].append("Read " + url)
        c["detail"]["tldr"][0][0]["t"] += " " + url
        c["detail"]["context"][1][0]["h"] += " " + url        # a heading never links
        c["detail"]["context"][1][1]["b"][0] += " " + url     # a section bullet links
        c["why"] += " " + url               # a fold part's summary links
        res = run_page(d)
        p = card(res, 41)["parts"]
        head = re.search(r'<h4 class="lvh">.*?</h4>', p["ctx"][2]).group(0)
        self.assertIn(url, head)
        self.assertNotIn("<a ", head)
        sec2 = p["ctx"][2][p["ctx"][2].index("What CI changes"):]
        self.assertIn('<a href="%s"' % url, sec2)
        self.assertNotIn("<a ", p["tldr"][0])
        self.assertNotIn("<a ", p["imp"][0])
        self.assertIn('<a href="%s"' % url, p["tldr"][1])
        self.assertIn('<a href="%s"' % url, p["why"][0])
        self.assertNotIn("<a ", card(res, 41)["act"]["b"])
        full = card(res, 41)["html"]
        one_lines = re.findall(r'<span class="oi">.*?</span>', full)
        self.assertTrue(one_lines)
        for x in one_lines:
            self.assertNotIn("<a ", x)
        # the option detail may link: its Reach
        self.assertIn('<a href="%s"' % url, card(res, 41)["more"]["a"])

    # ---- the steps and the page side

    def test_the_steps_cycle_and_name_the_next_step(self):
        s = run_pages([example()])["steps"]
        self.assertEqual(s["two"], [1, 2, 0])
        self.assertEqual(s["one"], [1, 0])
        self.assertEqual(s["text"], ["more detail", "full detail", "less detail", "more detail", "less detail"])

    def test_no_control_sits_inside_a_parts_text(self):
        res = run_page(example())
        for c in res["cards"]:
            for key, _, _ in secs(c["html"]):
                for _, r in renditions(c["html"], c["n"], key):
                    self.assertNotIn("<input", r, (c["n"], key))
                    self.assertNotIn("<textarea", r, (c["n"], key))

    def test_the_page_side_guards_and_the_hidden_rule(self):
        html = PAGE.read_text()
        click = html[html.index('document.addEventListener("click"'):html.index('addEventListener("resize"')]
        self.assertIn('e.target.closest("a,button,input,label,textarea,select,summary")', click)
        self.assertIn("getSelection()", click)
        self.assertIn("[data-lv]", click)
        self.assertIn("[data-omore]", click)
        # Expand all and Collapse all open or close every card (the group map, V1)
        self.assertIn('setAll(document.querySelectorAll("details.card"),all.dataset.all)', click)
        # a reference's tooltip is a peek: no detail levels, no More, no links
        tip = html[html.index("function tipHtml("):html.index("/* ---- end of the page-free part")]
        self.assertNotIn("data-lv", tip)
        self.assertNotIn("omore", tip)
        self.assertNotIn("fmtD", tip)
        style = html[html.index("<style>"):html.index("</style>")]
        self.assertIn("[hidden]{display:none !important}", style)
        self.assertRegex(style, r"\n\.lv\{[^}]*overflow-wrap:anywhere")
        self.assertRegex(style, r"\n\.odet\{[^}]*overflow-wrap:anywhere")


def without(d, n, *path):
    c = next(x for x in d["cards"] if x["n"] == n)
    for k in path[:-1]:
        c = c[k]
    c.pop(path[-1])
    return d


@unittest.skipUnless(NODE, "node is not installed")
class DepthRunner(unittest.TestCase):

    def lint(self, d, *needles):
        code, out, err = runner(d)
        self.assertEqual(code, 2, out + err)
        self.assertTrue(out.splitlines())
        self.assertTrue(all(x.startswith(("lint: card ", "lint: page: ")) for x in out.splitlines()),
                        out)
        for n in needles:
            self.assertIn(n, out)
        return out

    def clean(self, d):
        code, out, err = runner(d)
        self.assertEqual((code, out), (0, ""), err)

    def test_the_example_is_clean(self):
        self.clean(example())

    def test_levels_are_optional_on_every_part(self):
        # decision 201 (c): levels scale with the decision; a card may carry none, or some
        d = example()
        for c in d["cards"]:
            c.pop("detail", None)
        self.clean(d)
        d = example()
        d["cards"][0]["detail"]["context"].pop()
        d["cards"][1]["detail"].pop("rec")
        self.clean(d)

    def test_thin_depth_is_linted_only_where_levels_exist(self):
        d = example()
        for c in d["cards"]:
            c.pop("detail", None)
            c.pop("evidence", None)
        d["cards"][0]["why"] = "Two broken publishes."
        d["cards"][0]["whyask"] = "Who can publish changes."
        for o in d["cards"][2]["options"]:
            o.pop("reach", None)
            o.pop("cost", None)
            o.pop("detail", None)
        d["cards"][2]["options"][0]["text"] = "Keep the blue."
        out = self.lint(d, "lint: card 43: depth: (a) has no reach: give it who or what it reaches, its undo where it is one-way or costly, and its cost where it has one",
                        "lint: card 43: depth: (b) has no reach")
        # a short part with no levels is a small call's, never thin
        self.assertNotIn("Background is", out)
        self.assertNotIn("evidence is", out)
        self.assertNotIn("'s detail is", out)
        # the ⚠ card's reach is the page's to refuse, never a lint
        self.assertNotIn("card 42: depth: (a) has no reach", out)
        # once a part carries levels, its depth is sized at its top level
        d["cards"][0]["detail"] = {"why": ["Two broken publishes this month."],
                                   "evidence": ["Observed: both failures in the build logs."]}
        d["cards"][2]["options"][0]["detail"] = ["Keep the current blue."]
        self.lint(d, "lint: card 41: depth: Background is 9 words at its fullest",
                  "lint: card 41: depth: evidence is 7 words",
                  "lint: card 43: depth: (a)'s detail is 11 words")

    def test_a_level_not_longer_than_the_one_below(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][0] = ["Laptop or CI"]
        self.lint(d, "lint: card 41: depth: the TLDR medium is not longer than its summary")
        d = example()
        d["cards"][1]["options"][0]["detail"][1] = "Add the redirects."
        self.lint(d, "lint: card 42: depth: (a)'s plan high is not longer than its medium")
        # a plan's levels grow from the plan
        d = example()
        d["cards"][1]["options"][0]["plan"] = " ".join(["word"] * 60)
        self.lint(d, "lint: card 42: depth: (a)'s plan medium is not longer than its summary")
        # an older option's from its text
        d = example()
        d["cards"][1]["options"][0].pop("plan")
        d["cards"][1]["options"][0]["text"] = "Add a redirect for each of the twelve URLs."
        d["cards"][1]["options"][0]["detail"][1] = "Add the redirects."
        self.lint(d, "lint: card 42: depth: (a)'s text high is not longer than its medium")

    def test_the_sizes_are_read_at_the_top_level(self):
        d = example()
        d["cards"][0]["options"][0]["detail"][1] = WORDS200
        self.lint(d, "lint: card 41: depth: (a)'s detail is")
        d = example()
        d["cards"][0]["detail"]["evidence"][1] = [WORDS200, "and more " + " ".join(["x"] * 40)]
        self.lint(d, "lint: card 41: depth: evidence is")
        d = example()
        d["cards"][0]["detail"]["why"][1] = WORDS200
        self.lint(d, "lint: card 41: depth: Background is")
        d = example()
        for k in ("why", "whyask"):
            d["cards"][0]["detail"][k][1] = " ".join(["w"] * 350)
        d["cards"][0]["detail"]["evidence"][1] = [" ".join(["e"] * 220)]
        for k in ("a", "b"):
            d["cards"][0]["options"]["ab".index(k)]["detail"][1] = " ".join(["o"] * 170)
        self.lint(d, "lint: card 41: depth: the card is")

    def test_basis_none_waives_the_evidence_floor(self):
        d = example()
        c = d["cards"][0]
        c["basis"] = "none"
        c["evidence"] = "Not observed."
        c["detail"]["evidence"] = [["Not observed: nothing was read"],
                                   [{"h": "Not observed", "b": ["Nothing was read or run."]}]]
        self.clean(d)
        c["basis"] = "partial"
        self.lint(d, "lint: card 41: depth: evidence is 7 words")

    def test_an_unknown_detail_key_is_linted(self):
        d = example()
        d["cards"][0]["detail"]["later"] = ["x"]
        self.lint(d, "lint: card 41: depth: detail.later is not a part the page shows")

    def test_terms_in_the_visible_levels_are_checked_against_contexts_summary(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][1][-1]["b"].append("The three reviewers agree.")
        self.lint(d, 'lint: card 41: "three" (the TLDR, full detail) counts things its context does not name')
        # glossed in Context's summary: clean
        g = copy.deepcopy(d)
        g["cards"][0]["context"] = g["cards"][0]["context"][:-1] + "; three reviewers check it."
        self.clean(g)
        # glossed only in Context's high: a reader may see the TLDR at high beside Context's summary
        h = copy.deepcopy(d)
        h["cards"][0]["detail"]["context"][1][-1]["b"].append("Three reviewers check it.")
        self.lint(h, '"three" (the TLDR, full detail) counts things')
        # an id is linted in a level, never cleared by a gloss (test_context covers Context)
        i = copy.deepcopy(g)
        i["cards"][0]["detail"]["tldr"][1][-1]["b"].append("Closes KAPPA-3570.")
        self.lint(i, "lint: card 41: KAPPA-3570 looks like an id (detail.tldr)")
        # the Impact line too, and counts and named things
        d = example()
        d["cards"][0]["detail"]["impact"][0]["reach"]["t"] += ", and three reviewers"
        d["cards"][0]["detail"]["rec"][0].append("the content mode is off")
        out = self.lint(d, '"three" (the Impact line, more detail) counts things its context does not name')
        # the basis line sits in the closed Assumptions fold: neither its reason nor its levels are the
        # flat part, so their terms are not read (an id in them still is)
        self.assertNotIn("content mode", out)
        d = example()
        d["cards"][0]["reason"] = "both failures were read in the build logs by three reviewers"
        self.clean(d)
        d["cards"][0]["reason"] += " (KAPPA-3570)"
        self.lint(d, "lint: card 41: KAPPA-3570 looks like an id (reason)")

    def test_the_broad_tldr_lint_reaches_the_tldr_levels(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][0][1] = "Suggest moving to CI on every merge"
        # numbered in reading order: the first bullet, its sub-bullet, then this one
        self.lint(d, "lint: card 41: tldr bullet 3 (more detail) may carry the recommendation")


BG_HARNESS = r"""
const cs = JSON.parse(require("fs").readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(cs.map(c => ({first: bgFirst(c), sum: bgSum(c)}))));
"""

BGSUM_LINE = "shape: the Background fold's summary, the first sentence of why, is "


@unittest.skipUnless(NODE, "node is not installed")
class BackgroundSummary(unittest.TestCase):
    """The Background fold (answer 338): first of the bottom folds, closed, its summary *why now:* and
    the first sentence of `why`; the runner's `bgsum` lint measures the same sentence."""

    def test_the_summary_is_the_first_sentence_of_why_now(self):
        cs = [{"why": "Two broken publishes came from a cache. Blocks [[42]] and [[43]]."},
              {"why": "Is it [[42]] first? Then the rest."},
              {"why": "No stop at all"},
              {"why": "<img src=x onerror=alert(1)> moves now. Later."},
              {"why": "none"}, {}, {"why": "  "},
              {"why": "The `cards.json` file moves now. Later."}]
        got = node(BG_HARNESS, cs)
        self.assertEqual(got[0]["first"], "Two broken publishes came from a cache.")
        self.assertEqual(got[0]["sum"],
                         ' <span class="fsum">why now: Two broken publishes came from a cache.</span>')
        # a slug is its bare number; the cut is at ? too
        self.assertEqual(got[1]["first"], "Is it 42 first?")
        self.assertEqual(got[2]["first"], "No stop at all")
        # escaped, never markup
        self.assertNotIn("<img", got[3]["sum"])
        self.assertIn("&lt;img", got[3]["sum"])
        # none is not shown: no summary span
        for g in got[4:7]:
            self.assertEqual(g, {"first": "", "sum": ""})
        # a backtick span renders as code, as everywhere on the page
        self.assertEqual(got[7]["sum"],
                         ' <span class="fsum">why now: The <code>cards.json</code> file moves now.</span>')

    def test_backticks_in_the_summary_cannot_pass_as_text(self):
        # mutant: the summary escaped but not given its code spans
        src = page_free_script()
        mutant = src.replace("code(esc(s))+'</span>'", "esc(s)+'</span>'", 1)
        self.assertNotEqual(mutant, src)
        out = subprocess.run([NODE, "-e", mutant + BG_HARNESS],
                             input=json.dumps([{"why": "The `cards.json` file moves now."}]),
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertNotIn("<code>cards.json</code>", json.loads(out.stdout)[0]["sum"])

    def test_the_fold_is_first_of_the_bottom_folds_closed_with_its_summary(self):
        res = run_page(example())
        for c in res["cards"]:
            h = c["html"]
            m = re.search(r'<details class="pane"><summary>Background <span class="fsum">why now: '
                          r'([^<]*)</span></summary>', h)
            self.assertTrue(m, c["n"])
            self.assertTrue(m.group(1).strip(), c["n"])
            # first of the panes, after the answer fieldset
            self.assertEqual(h.index('<details class="pane">'), m.start(), c["n"])
            self.assertLess(h.index("</fieldset>"), m.start(), c["n"])
        self.assertIn("why now: Two broken publishes this month came from a local cache.</span>",
                      card(res, 41)["html"])
        # the summary hides while the fold is open
        self.assertIn("details.pane[open]>summary>.fsum{display:none}", PAGE.read_text())

    def test_a_long_first_sentence_lints_and_a_long_why_does_not(self):
        d = example()
        d["cards"][0]["why"] = " ".join(["word"] * 25) + " ends. Short second."
        code, out, err = runner(d)
        self.assertEqual(code, 2, out + err)
        self.assertIn("lint: card 41: " + BGSUM_LINE + "26 words", out)
        # 25 words is at the cap; a long why whose first sentence is short is not linted
        d = example()
        d["cards"][0]["why"] = " ".join(["word"] * 24) + " ends. " + " ".join(["more"] * 30) + "."
        code, out, err = runner(d)
        self.assertNotIn(BGSUM_LINE, out)

    def test_the_lint_cannot_pass_for_one(self):
        # mutants: the lint removed; the lint taking all of why rather than its first sentence
        src = RUNNER.read_text()
        removed = src.replace('if (bgs > BGSUM_CAP) say("bgsum"', 'if (false) say("bgsum"', 1)
        whole = src.replace("words(page.bgFirst(c))", "words(c.why)", 1)
        self.assertNotEqual(removed, src)
        self.assertNotEqual(whole, src)
        long_first = example()
        long_first["cards"][0]["why"] = " ".join(["word"] * 25) + " ends. Short second."
        short_first = example()
        short_first["cards"][0]["why"] = (" ".join(["word"] * 24) + " ends. "
                                          + " ".join(["more"] * 30) + ".")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "scripts").mkdir()
            (root / "assets").mkdir()
            shutil.copy(PAGE, root / "assets" / "index.html")
            script = root / "scripts" / "check_cards.js"
            script.write_text(removed)
            self.assertNotIn(BGSUM_LINE, runner(long_first, script=script)[1])
            script.write_text(whole)
            self.assertIn(BGSUM_LINE, runner(short_first, script=script)[1])


def afold(html):
    """A card's Assumptions fold: (its summary text, its body html)."""
    start = html.index('<details class="gfold afold">')
    rest = html[start:]
    m = re.match(r'<details class="gfold afold"><summary><span class="lbl">Assumptions</span>'
                 r'<span class="gsum">([^<]*)</span></summary>', rest)
    assert m, rest[:200]
    # the fold holds no nested details, so its first </details> closes it
    return m.group(1), rest[m.end():rest.index("</details>")]


@unittest.skipUnless(NODE, "node is not installed")
class AssumptionsFold(unittest.TestCase):
    """The Assumptions fold (A1, the v5 layout, 9168): closed, after Open questions and before the
    Impact, on every card; its summary the basis line, `basis: <word>`, then the count of assumptions
    with their tripwires; inside, the Basis line (the word in a box, then the reason and its levels),
    the evidence, then each assumption in bold with its tripwire. The Recommendation part and the
    Evidence fold are gone into it; `assume` is refused in another shape; the runner lints a card with
    a recommendation and none."""

    def test_the_fold_holds_the_basis_the_evidence_and_each_assumption_with_its_tripwire(self):
        res = run_page(example())
        d = example()
        for c in res["cards"]:
            src = next(x for x in d["cards"] if x["n"] == c["n"])
            summ, body = afold(c["html"])
            n = len(src.get("assume", []))
            want = "basis: " + src["basis"] + ("" if not n else " · %d assumptions with tripwires" % n)
            self.assertEqual(summ, want, c["n"])
            self.assertIn('<span class="lbl">Basis</span><span class="bw">%s</span>' % src["basis"], body)
            self.assertLess(body.index('class="basisl"'), body.index("Observed" if c["n"] == 42 else src["evidence"][:20]))
            self.assertEqual(body.count('<p class="rests">'), n, c["n"])
            self.assertEqual(body.count('<p class="tw"><em>tripwire:</em>'), n, c["n"])
            for a in src.get("assume", []):
                esc = lambda t: t.replace("&", "&amp;").replace("'", "&#39;")
                self.assertLess(body.index(esc(a["rests"].split("`")[0])), body.index(esc(a["tw"])), c["n"])
            # the evidence, then the assumptions
            if n:
                self.assertLess(body.index('data-sec="ev"') if 'data-sec="ev"' in body else 0,
                                body.index('<ul class="asm">'))
        # card 43 has no recommendation and names no assumption: its basis alone, no list
        summ, body = afold(card(res, 43)["html"])
        self.assertEqual(summ, "basis: strong")
        self.assertNotIn('<ul class="asm">', body)

    def test_one_assumption_reads_with_its_tripwire(self):
        d = example()
        d["cards"][0]["assume"] = d["cards"][0]["assume"][:1]
        self.assertEqual(afold(card(run_page(d), 41)["html"])[0],
                         "basis: strong · 1 assumption with its tripwire")

    def test_none_is_not_shown_and_no_zero_count_or_unknown(self):
        for v in (None, [], [{"rests": "none", "tw": "n/a"}]):
            d = example()
            if v is None:
                d["cards"][0].pop("assume")
            else:
                d["cards"][0]["assume"] = v
            res = run_page(d)
            self.assertEqual(res["bad"], [], v)
            summ, body = afold(card(res, 41)["html"])
            self.assertEqual(summ, "basis: strong", v)
            self.assertNotIn('<ul class="asm">', body, v)
        # an open question never reaches the fold
        for c in run_page(example())["cards"]:
            summ, body = afold(c["html"])
            self.assertNotRegex(summ + body, r"(?i)unknown|not known|open:")
        # mutants: a template that renders a zero count, or an unknowns clause
        src = page_free_script()
        zero = src.replace("+(n?' · '+n+", "+(true?' · '+n+", 1)
        unk = src.replace("'basis: '+esc(c.basis)+", "'basis: '+esc(c.basis)+' · no unknowns'+", 1)
        for m in (zero, unk):
            self.assertNotEqual(m, src)
            d = example()
            d["cards"][0].pop("assume")
            out = subprocess.run([NODE, "-e", m + HARNESS], input=json.dumps([d]), capture_output=True,
                                 text=True, timeout=60)
            html = json.loads(out.stdout)["out"][0]["cards"][0]["html"]
            self.assertNotEqual(afold(html)[0], "basis: strong")

    def test_assume_in_another_shape_is_refused(self):
        msg = "card 41: assume must be a list of {rests, tw}"
        for bad in ("rests on the cache", {"rests": "x", "tw": "y"}, [{"rests": "x"}], [{"rests": "x", "tw": ""}],
                    [{"rests": 3, "tw": "y"}], ["x"], [["x", "y"]]):
            d = example()
            d["cards"][0]["assume"] = bad
            self.assertTrue(any(msg in b for b in run_page(d)["bad"]), bad)
        d = example()
        d["cards"][0]["assume"] = []
        self.assertEqual(run_page(d)["bad"], [])

    def test_rests_and_tripwires_are_escaped(self):
        d = example()
        d["cards"][0]["assume"] = [{"rests": "<script>alert(1)</script> holds", "tw": "<img src=x onerror=alert(1)>"}]
        _, body = afold(card(run_page(d), 41)["html"])
        self.assertNotIn("<script>", body)
        self.assertNotIn("<img", body)
        self.assertIn("&lt;script&gt;", body)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", body)

    def test_the_recommendation_part_and_the_evidence_fold_are_gone(self):
        html = PAGE.read_text()
        for gone in ("recLine", "recHeadHtml", "class=\"recline\"", "<summary>Evidence</summary>",
                     '"Recommendation"'):
            self.assertNotIn(gone, html)
        for c in run_page(example())["cards"]:
            self.assertEqual(c["html"].count('data-sec="rec"'), c["html"].count('<div class="sec" data-n="%d" data-sec="rec"' % c["n"]))
            # the basis line sits inside the fold, never after the answer
            if 'data-sec="rec"' in c["html"]:
                self.assertLess(c["html"].index('data-sec="rec"'), c["html"].index("<fieldset>"))

    def test_the_runner_lints_a_recommended_card_with_no_assumptions(self):
        d = example()
        d["cards"][0].pop("assume")
        code, out, err = runner(d)
        self.assertEqual(code, 2, out + err)
        self.assertIn("lint: card 41: depth: no assumptions: a card with a recommendation names", out)
        # it counts what the page shows: assumptions whose rests is none show none, so they lint too
        for v in ([{"rests": "none", "tw": "x"}], [{"rests": "n/a", "tw": "x"}, {"rests": "None.", "tw": "y"}]):
            d = example()
            d["cards"][0]["assume"] = v
            res = run_page(d)
            self.assertEqual(res["bad"], [], v)
            self.assertNotIn('<ul class="asm">', afold(card(res, 41)["html"])[1], v)
            self.assertIn("lint: card 41: depth: no assumptions", runner(d)[1], v)
        # one shown assumption beside a none one clears it
        d = example()
        d["cards"][0]["assume"] = [{"rests": "none", "tw": "x"}, d["cards"][0]["assume"][0]]
        self.assertEqual(runner(d)[:2], (0, ""))
        # mutant: the runner counting the raw list again
        js = RUNNER.read_text()
        raw = js.replace("const as = page.assumeOf(c);", "const as = Array.isArray(c.assume) ? c.assume : [];", 1)
        self.assertNotEqual(raw, js)
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "scripts").mkdir()
            (root / "assets").mkdir()
            shutil.copy(PAGE, root / "assets" / "index.html")
            script = root / "scripts" / "check_cards.js"
            script.write_text(raw)
            d = example()
            d["cards"][0]["assume"] = [{"rests": "none", "tw": "x"}]
            self.assertNotIn("no assumptions", runner(d, script=script)[1])
        # card 43 has no recommendation: never linted; the example, with its assumptions, is clean
        self.assertNotIn("card 43: depth: no assumptions", out)
        self.assertEqual(runner(example())[:2], (0, ""))
        # an id in an assumption is linted like any card text
        d = example()
        d["cards"][1]["assume"][0]["tw"] = "the guides drop, as KAPPA-3570 warned"
        self.assertIn("lint: card 42: KAPPA-3570 looks like an id (assume)", runner(d)[1])
        # mutant: the lint removed
        js = RUNNER.read_text()
        removed = js.replace('if (c.rec && !as.length)', 'if (false)', 1)
        self.assertNotEqual(removed, js)
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "scripts").mkdir()
            (root / "assets").mkdir()
            shutil.copy(PAGE, root / "assets" / "index.html")
            script = root / "scripts" / "check_cards.js"
            script.write_text(removed)
            d = example()
            d["cards"][0].pop("assume")
            self.assertNotIn("no assumptions", runner(d, script=script)[1])


if __name__ == "__main__":
    unittest.main()
