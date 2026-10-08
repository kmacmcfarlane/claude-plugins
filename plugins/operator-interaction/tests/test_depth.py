"""Every page card carries the decisions block's depth, a click away (decision 198).

Two parts:

- the decision page (`decision-page` skill): the `detail` field and its check, the
  `evidence` shapes, each part's detail levels and its toggle, the **More** button and its
  option detail, links in the levels only, and the folds kept; loaded from
  `assets/index.html` and run under node against `assets/cards.example.json` and copies of it;
- the pre-publish runner's depth lints, `scripts/check_cards.js`: the visible levels
  expected, each level longer than the one below, the sizes read at the top level, the
  missing `blocks` rows, the long card, an unknown `detail` key, and the term lints on the
  visible parts' levels, against Context's summary.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import copy
import json
import re
import subprocess
import sys
import unittest

from test_impact import NODE, PAGE, example, page_free_script
from test_context import runner


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
    cards = CARDS.map(c => ({n: c.n, html: cardHtml(c), table: impactTable(c), parts: parts(c),
      more: Object.fromEntries(c.o.map(o => [o[0], optionDetail(c, o[0])])),
      act: Object.fromEntries(c.o.map(o => [o[0], actList(c, o[0])]))}));
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
    """Each part with levels: (key, data-max, the HTML of its renditions in order)."""
    out = []
    for m in re.finditer(r'<div class="sec" data-n="\d+" data-sec="([^"]+)" data-lvl="0" '
                         r'data-max="(\d+)">', html):
        body = html[m.end():]
        out.append((m.group(1), int(m.group(2)), body))
    return out


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


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageDepth(unittest.TestCase):

    def assert_refused(self, data, needle):
        bad = run_page(data)["bad"]
        self.assertTrue(any(needle in b for b in bad), bad)

    # ---- the data

    def test_the_example_passes_with_blocks_on_every_option_and_detail_on_every_card(self):
        d = example()
        self.assertEqual(run_page(d)["bad"], [])
        for c in d["cards"]:
            for o in c["o"][:-1]:
                self.assertIn(o[0], c["blocks"], c["n"])
            for k in ("context", "impact", "tldr", "rec"):
                self.assertEqual(len(c["detail"][k]), 2, (c["n"], k))
        self.assertIsInstance(d["cards"][0]["evidence"], str)
        self.assertIsInstance(d["cards"][0]["detail"]["evidence"][1], list)

    def test_older_data_renders_as_today_with_more_buttons(self):
        d = example()
        for c in d["cards"]:
            c.pop("detail")
            if not c.get("warn"):
                c.pop("blocks", None)
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        for c in res["cards"]:
            self.assertNotIn("lvb", c["html"], c["n"])
            self.assertNotIn('class="sec"', c["html"], c["n"])
            self.assertEqual(c["html"].count(">More</button>"), 2, c["n"])
        self.assertIn("<td>—</td><td>—</td>", card(res, 43)["table"])
        # with no blocks row, the option detail shows the option's impact as its effect
        self.assertIn("No visual change.", card(res, 43)["more"]["a"])
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
            (lambda c: c["detail"].__setitem__("impact", [{"wait": "x"}]), "card 41: detail.impact must be"),
            (lambda c: c["detail"].__setitem__("impact", [{"effect": "x", "cost": 4}]), "card 41: detail.impact must be"),
            (lambda c: c["detail"].__setitem__("tldr", ["a bullet"]), "card 41: detail.tldr must be"),
            (lambda c: c["detail"].__setitem__("tldr", [[]]), "card 41: detail.tldr must be"),
            (lambda c: c["detail"]["o"].__setitem__("z", ["x"]), "card 41: detail.o is keyed by option letter, not (z)"),
            (lambda c: c["detail"]["o"].__setitem__("q", ["x"]), "card 41: detail.o is keyed by option letter"),
            (lambda c: c["detail"].__setitem__("o", ["x"]), "card 41: detail.o is keyed by option letter"),
            (lambda c: c["detail"]["o"].__setitem__("a", "x"), "card 41: detail.o.a must be"),
        ]
        datasets = []
        for put, _ in cases:
            d = example()
            put(d["cards"][0])
            datasets.append(d)
        for (_, needle), res in zip(cases, run_pages(datasets)["out"]):
            self.assertTrue(any(needle in b for b in res["bad"]), (needle, res["bad"]))

    def test_a_rec_bullet_in_a_detail_tldr_is_refused_naming_its_level_and_bullet(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][1][2] = "Rec: move it to CI"
        self.assert_refused(d, "card 41: detail.tldr high bullet 3 carries the recommendation: "
                               "the options mark it; say what is decided instead")
        d = example()
        d["cards"][0]["detail"]["tldr"][0][0] = "I recommend CI"
        self.assert_refused(d, "card 41: detail.tldr medium bullet 1 carries the recommendation")

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
                self.assertEqual([h for h, _ in rs], [False] + [True] * mx, (c["n"], key))
                self.assertEqual(rs[0][1], c["parts"][key][0], (c["n"], key))
                seen.add(key)
        self.assertTrue({"ctx", "imp", "tldr", "rec", "why", "whyask", "ev", "opt-a"} <= seen, seen)
        # a part with only its summary has no toggle: card 43's fold items, any card's Depends on
        h43 = card(res, 43)["html"]
        for key in ("why", "whyask", "ev", "opt-a", "dep"):
            self.assertNotIn('data-sec="%s"' % key, h43)
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
                self.assertIn('aria-expanded="false"', tag)
                self.assertEqual(m.group(1), "more detail")
                label = re.search(r'data-lbl="([^"]+)"', tag).group(1)
                self.assertIn('aria-label="%s: more detail"' % label, tag)
            for ctl in re.findall(r'aria-controls="([^"]+)"', html):
                self.assertIn('id="%s"' % ctl, html)
        self.assertEqual(len(ids), len(set(ids)), "ids are unique across the page")

    def test_a_level_replaces_the_text_and_context_keeps_its_label(self):
        res = run_page(example())
        c = card(res, 41)
        ctx = c["parts"]["ctx"]
        for r in ctx:
            self.assertTrue(r.startswith('<div class="ctx"><span class="lbl">Context</span>'), r[:60])
        self.assertIn("answered: clear it", ctx[2])
        self.assertNotIn("answered: clear it", ctx[1])
        # the impact levels are facet lines in the one vocabulary
        imp = c["parts"]["imp"][2]
        pos = [imp.index(t) for t in ("<b>→</b>", "<i>later:</i>", "<i>reach:</i>", "<i>undo:</i>", "<i>cost:</i>")]
        self.assertEqual(pos, sorted(pos))
        # the rec line keeps its head, and shows the merged unknown as the summary does
        rec = c["parts"]["rec"][1]
        self.assertIn("Rec <strong>(b)</strong> · basis <strong>strong</strong> — <em>", rec)
        self.assertIn("</em> · unknown: whether anyone publishes from a fork", rec)
        # Why ask keeps its class first at every level
        for r in c["parts"]["whyask"]:
            self.assertIn("<em>wider scope</em> — ", r)

    def test_the_folds_stay_in_order_closed_but_options_in_full_on_a_warn_card(self):
        res = run_page(example())
        for c in res["cards"]:
            panes = re.findall(r'<details class="pane"( open)?><summary>([^<]+)</summary>', c["html"])
            self.assertEqual([p[1] for p in panes],
                             ["Background", "Options in full", "Dependencies", "Evidence and unknowns"])
            self.assertEqual([p[0] for p in panes],
                             ["", " open" if c["n"] == 42 else "", "", ""], c["n"])

    def test_the_rendered_order_of_a_card(self):
        res = run_page(example())
        h = card(res, 41)["html"]
        marks = ['data-sec="ctx"', 'data-sec="imp"', 'data-sec="tldr"', "If unanswered:", "<fieldset>",
                 'id="d41-a"', 'data-omore="a"', 'id="d41-a-more"', 'id="d41-b"', 'data-omore="b"',
                 'class="act"', 'id="d41-b-more"', 'class="follow"', 'data-sec="rec"',
                 "<summary>Background</summary>", 'data-sec="why"', 'data-sec="whyask"',
                 "<summary>Options in full</summary>", '<table class="imp">', 'data-sec="opt-a"',
                 "<summary>Dependencies</summary>", "<summary>Evidence and unknowns</summary>",
                 '<span class="lbl">Basis</span>', 'data-sec="ev"', '<span class="lbl">Unknown</span>']
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

    def test_more_sits_beside_each_option_but_z_outside_its_label(self):
        res = run_page(example())
        for c in res["cards"]:
            h = c["html"]
            # a slug may sit in a one line; the More button never does
            for lab in re.findall(r'<label class="optl">.*?</label>', h, re.S):
                self.assertNotIn("omore", lab, c["n"])
                self.assertNotIn(">More</button>", lab, c["n"])
            for opt in re.findall(r'<div class="opt(?: isrec)?">.*?(?=<div class="opt[ "]|</div><div class="follow")', h, re.S):
                k = re.search(r'value="([a-z])"', opt).group(1)
                if k == "z":
                    self.assertNotIn("omore", opt)
                    continue
                self.assertEqual(opt.count(">More</button>"), 1, (c["n"], k))
                btn = re.search(r'<button[^>]*data-omore[^>]*>More</button>', opt).group(0)
                self.assertTrue(btn.startswith('<button type="button" class="btn omore"'), btn)
                self.assertIn('aria-label="More decision detail on option (%s)"' % k, btn)
                self.assertIn('aria-expanded="false"', btn)
                self.assertIn('aria-controls="d%s-%s-more"' % (c["n"], k), btn)
                self.assertIn('<div class="odet" id="d%s-%s-more" hidden>' % (c["n"], k), opt)
                self.assertLess(opt.index("</label>"), opt.index(btn))
                self.assertLess(opt.index(btn), opt.index('class="odet"'))

    def test_the_option_detail_is_its_fullest_text_then_its_facets(self):
        d = example()
        del d["cards"][0]["blocks"]["a"]["cost"]
        res = run_page(d)
        more = card(res, 41)["more"]
        self.assertTrue(more["b"].startswith("<p>Build and publish from CI on every merge to <code>main</code>; "
                                             "the laptop build stays for previews only."), more["b"][:90])
        pos = [more["b"].index('<span class="lbl">' + f + "</span>") for f in ("Effect", "Reach", "Undo", "Cost")]
        self.assertEqual(pos, sorted(pos))
        self.assertNotIn(">Cost<", more["a"])
        self.assertEqual(more["z"], "")
        # without detail.o, the option's own text
        d["cards"][0]["detail"].pop("o")
        self.assertTrue(card(run_page(d), 41)["more"]["a"].startswith("<p>Keep building on a laptop."))

    # ---- escaping and links

    def test_every_level_and_the_option_detail_escape(self):
        x = '<img src=x onerror="alert(1)">'
        d = example()
        c = d["cards"][0]
        c["detail"]["context"][1] += x
        c["detail"]["impact"][1]["reach"] += x
        c["detail"]["tldr"][0][0] += x
        c["detail"]["rec"][1] += x
        c["detail"]["why"][1] += x
        c["detail"]["o"]["a"][1] += x
        c["detail"]["evidence"][1][0] += x
        c["blocks"]["a"]["who"] += x
        c["evidence"] = ["one " + x]
        res = run_page(d)
        self.assertEqual(res["bad"], [])
        h = card(res, 41)["html"]
        self.assertNotIn("<img", h)
        self.assertGreaterEqual(h.count("&lt;img"), 9)

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
        c["o"][0][2] += " " + url          # o[2], static
        c["blocks"]["a"]["who"] += " " + url  # a table cell, static
        c["act"]["b"].append("Read " + url)
        c["detail"]["tldr"][0][0] += " " + url
        c["why"] += " " + url               # a fold part's summary links
        res = run_page(d)
        p = card(res, 41)["parts"]
        self.assertNotIn("<a ", p["tldr"][0])
        self.assertNotIn("<a ", p["imp"][0])
        self.assertIn('<a href="%s"' % url, p["tldr"][1])
        self.assertIn('<a href="%s"' % url, p["why"][0])
        self.assertNotIn("<a ", card(res, 41)["table"])
        self.assertNotIn("<a ", card(res, 41)["act"]["b"])
        full = card(res, 41)["html"]
        impact_lines = re.findall(r'<p class="impact">.*?</p>', full)
        self.assertTrue(impact_lines)
        for x in impact_lines:
            self.assertNotIn("<a ", x)
        # the option detail may link: its Reach cell is the blocks row's
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
        self.assertIn('if(e.target.id==="toggleall"){const all=[...document.querySelectorAll("details.card")]', click)
        pop = html[html.index("function fillPop"):html.index("function place(")]
        self.assertNotIn("data-lv", pop)
        self.assertNotIn("omore", pop)
        self.assertNotIn("fmtD", pop)
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
        self.assertTrue(all(x.startswith("lint: card ") for x in out.splitlines()), out)
        for n in needles:
            self.assertIn(n, out)
        return out

    def clean(self, d):
        code, out, err = runner(d)
        self.assertEqual((code, out), (0, ""), err)

    def test_the_example_is_clean(self):
        self.clean(example())

    def test_the_visible_levels_are_expected_on_every_card(self):
        self.lint(without(example(), 43, "detail", "rec"),
                  "lint: card 43: depth: the rec line has no medium or high level: write them from the "
                  "sources (the operator asked for every visible part to toggle), or leave it knowingly")
        d = example()
        d["cards"][0]["detail"]["context"].pop()
        out = self.lint(d, "lint: card 41: depth: Context has no high level")
        self.assertEqual(len(out.splitlines()), 1, out)
        # fold items carry levels where there is depth to give: none expected
        d = example()
        for k in ("why", "whyask", "evidence", "o"):
            d["cards"][1]["detail"].pop(k)
        d["cards"][1]["why"] = d["cards"][1]["why"] + " " + " ".join(["more"] * 50)
        d["cards"][1]["evidence"] = d["cards"][1]["evidence"] + " " + " ".join(["more"] * 50)
        for o in d["cards"][1]["o"][:2]:
            o[1] += " " + " ".join(["more"] * 10)
        self.clean(d)

    def test_the_main_example_lints_thin_folds_and_missing_rows(self):
        d = example()
        for c in d["cards"]:
            c.pop("detail")
            c.pop("evidence", None)
        d["cards"][0]["why"] = "Two broken publishes."
        d["cards"][0]["whyask"] = "Who can publish changes."
        d["cards"][2].pop("blocks")
        d["cards"][2]["o"][0][1] = "Keep the blue."
        out = self.lint(d, "lint: card 41: depth: Background is 7 words at its fullest",
                        "lint: card 41: depth: evidence is 0 words",
                        "lint: card 43: depth: (a) has no blocks row: give it happens, who, undo and cost",
                        "lint: card 43: depth: (b) has no blocks row",
                        "lint: card 43: depth: (a)'s detail is 3 words")
        # the ⚠ card's rows are the page's to refuse, never a lint
        self.assertNotIn("card 42: depth: (a) has no blocks row", out)

    def test_a_level_not_longer_than_the_one_below(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][0] = ["Laptop or CI"]
        self.lint(d, "lint: card 41: depth: the TLDR medium is not longer than its summary")
        d = example()
        d["cards"][1]["detail"]["o"]["a"][1] = "Add the redirects."
        self.lint(d, "lint: card 42: depth: (a)'s text high is not longer than its medium")

    def test_the_sizes_are_read_at_the_top_level(self):
        d = example()
        d["cards"][0]["detail"]["o"]["a"][1] = WORDS200
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
            d["cards"][0]["detail"]["o"][k][1] = " ".join(["o"] * 170)
        self.lint(d, "lint: card 41: depth: the card is")

    def test_basis_none_waives_the_evidence_floor(self):
        d = example()
        c = d["cards"][2]
        c["basis"] = "none"
        c.pop("evidence")
        self.clean(d)
        c["basis"] = "partial"
        self.lint(d, "lint: card 43: depth: evidence is 0 words")

    def test_an_unknown_detail_key_is_linted(self):
        d = example()
        d["cards"][0]["detail"]["later"] = ["x"]
        self.lint(d, "lint: card 41: depth: detail.later is not a part the page shows")

    def test_terms_in_the_visible_levels_are_checked_against_contexts_summary(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][1].append("Closes KAPPA-3570")
        self.lint(d, "lint: card 41: KAPPA-3570 (the TLDR, full detail) is not introduced in its context")
        # glossed in Context's summary: clean
        g = copy.deepcopy(d)
        g["cards"][0]["context"] += " KAPPA-3570 is the docs team's ticket for the move."
        for k in (0, 1):
            g["cards"][0]["detail"]["context"][k] += " KAPPA-3570 is the docs team's ticket for the move."
        self.clean(g)
        # glossed only in Context's high: a reader may see the TLDR at high beside Context's summary
        h = copy.deepcopy(d)
        h["cards"][0]["detail"]["context"][1] += " KAPPA-3570 is the docs team's ticket for the move."
        self.lint(h, "KAPPA-3570 (the TLDR, full detail) is not introduced")
        # the Impact line and the rec line too, and counts and named things
        d = example()
        d["cards"][0]["detail"]["impact"][0]["reach"] += ", and the three reviewers"
        d["cards"][0]["detail"]["rec"][0] += "; the content mode is off"
        self.lint(d, '"three" (the Impact line, more detail) counts things its context does not name',
                  '"content mode" (the rec line, more detail) is not glossed in its context')

    def test_the_broad_tldr_lint_reaches_the_tldr_levels(self):
        d = example()
        d["cards"][0]["detail"]["tldr"][0][1] = "Suggest moving to CI on every merge, or keeping the laptop build"
        self.lint(d, "lint: card 41: tldr bullet 2 (more detail) may carry the recommendation")


if __name__ == "__main__":
    unittest.main()
