"""The answer page keeps parity with the chat card (the 2026-10-21 *Both surfaces* ruling).

A decision-format change lands on the chat card (the `decisions` skill) and on the answer page
(the `decision-page` skill), and on the librarian's stored card where it applies. These checks
read the rulings, the page's text and, under node, the page and its pre-publish runner:

- *Both surfaces*: the ruling, its date and its alternative not taken, in both skills;
- the page forms of the card rules that landed chat-only at first, each with its ruling.

Each check is a function returning its problems, run on the real files (no problems) and on a
mutated copy (a problem), so a check that cannot fail does not pass for one.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import sys
import unittest
from pathlib import Path

import json
import subprocess

from test_impact import NODE, PAGE, example, page_free_script
from test_context import runner

PLUGIN = Path(__file__).resolve().parent.parent
PAGE_SKILL = PLUGIN / "skills" / "decision-page"
RULINGS = PLUGIN / "skills" / "decisions" / "references" / "rulings.md"
PAGE_SKILL_MD = PAGE_SKILL / "SKILL.md"
SCHEMA = PAGE_SKILL / "references" / "cards-schema.md"
DIGEST = PAGE_SKILL / "references" / "writer-digest.md"
FALLBACK = PAGE_SKILL / "references" / "fallback.md"


def setUpModule():
    # the runner tests need node; without it they skip, and say so where the Check's output
    # shows it rather than passing in silence
    if not NODE:
        print("WARNING: node is not installed: the decision page's parity tests (SystemLint and "
              "the other runner and render checks) are skipped, so the page forms of the card "
              "rules went untested", file=sys.stderr)


def flat(text):
    return re.sub(r"\s+", " ", text)


def bullet(text, name):
    """The rulings bullet opening `- **name**`, joined onto one line; "" when there is none."""
    m = re.search(r"^- \*\*" + re.escape(name) + r"\*\*.*?(?=^- |^## |\Z)", text, re.S | re.M)
    return flat(m.group(0)) if m else ""


BOTH_CORE = ("planned together; a surface left out names its obvious reason, and one that is "
             "unclear goes to the operator. Not taken: a rule scoped to the surface whose "
             "feedback raised it")


def both_surfaces_problems(text):
    b = bullet(text, "Both surfaces")
    if not b:
        return ["no Both surfaces bullet"]
    out = []
    if "(2026-10-21" not in b:
        out.append("Both surfaces: no date")
    if BOTH_CORE not in b:
        out.append("Both surfaces: the rule or its Not taken differs")
    return out


class BothSurfaces(unittest.TestCase):
    def setUp(self):
        self.rulings = RULINGS.read_text()
        self.page = PAGE_SKILL_MD.read_text()

    def test_in_both_skills(self):
        self.assertEqual(both_surfaces_problems(self.rulings), [])
        self.assertEqual(both_surfaces_problems(self.page), [])

    def test_the_page_skill_has_a_rulings_section_pointing_at_the_decisions_rulings(self):
        m = re.search(r"^## Rulings\n(.*?)(?=^## )", self.page, re.S | re.M)
        self.assertTrue(m)
        self.assertIn("the `decisions` skill's `references/rulings.md`", flat(m.group(1)))

    def test_mutations(self):
        for text in (self.rulings, self.page):
            self.assertEqual(both_surfaces_problems(text.replace("**Both surfaces**", "**Both**")),
                             ["no Both surfaces bullet"])
            self.assertIn("Both surfaces: no date",
                          both_surfaces_problems(text.replace("**Both surfaces** (2026-10-21",
                                                              "**Both surfaces** (")))
            self.assertIn("Not taken: a rule scoped", text)
            cut = text.replace("Not taken: a rule scoped", "Not taken: nothing scoped")
            self.assertIn("Both surfaces: the rule or its Not taken differs",
                          both_surfaces_problems(cut))


# ---- S1 (system impact on the page), rule 259

def static_lede(html):
    m = re.search(r'<p class="lede">(For each decision.*?)</p>', html, re.S)
    return m.group(1) if m else ""


SYSTEM_LEDE = "An Impact describes the system the work builds, never the review or the process"


def system_text_problems(html, fallback, schema, rulings):
    out = []
    lede = static_lede(html)
    if SYSTEM_LEDE not in lede or "changes in the system the work builds" not in lede:
        out.append("the lede does not say the Impact describes the system")
    if "describing the system the work builds, never the review or the process" not in flat(fallback):
        out.append("the doc fallback does not say it")
    if "An Impact describes the system the work builds, never the review or the process" not in flat(schema):
        out.append("the schema does not say it")
    b = bullet(rulings, "Impact names the system")
    if "On the answer page (2026-10-22, *Both surfaces*" not in b or "`process` lint" not in b:
        out.append("rule 259 does not name its page form")
    return out


class SystemText(unittest.TestCase):
    def setUp(self):
        self.args = [PAGE.read_text(), FALLBACK.read_text(), SCHEMA.read_text(), RULINGS.read_text()]

    def test_the_page_says_it(self):
        self.assertEqual(system_text_problems(*self.args), [])

    def test_mutations(self):
        html, fb, sc, ru = self.args
        self.assertEqual(system_text_problems(html.replace(SYSTEM_LEDE, "An Impact"), fb, sc, ru),
                         ["the lede does not say the Impact describes the system"])
        self.assertTrue(system_text_problems(html, fb.replace("describing the system", "on"), sc, ru))
        self.assertTrue(system_text_problems(html, fb, sc.replace("An Impact describes the system", "It"), ru))
        self.assertTrue(system_text_problems(html, fb, sc, ru.replace("`process` lint", "lint")))


PROCESS_FIRES = [
    # (where on card 41, a setter, the line's place)
    ("effect", lambda c: c["impact"].__setitem__("effect", "review comments wait"), "the effect"),
    ("reach", lambda c: c["impact"].__setitem__("reach", "another round of review"), "the reach"),
    ("happens", lambda c: c["blocks"]["b"].__setitem__("happens", "the change waits on review"), "(b)'s effect"),
    ("who", lambda c: c["blocks"]["a"].__setitem__("who", "a blocked session"), "(a)'s reach"),
    ("option", lambda c: c["o"][1].__setitem__(2, "the session is blocked"), "(b)'s impact"),
    ("medium", lambda c: c["detail"]["impact"][0]["effect"].__setitem__("t", "costs your time each run"),
     "the effect (more detail)"),
    ("high", lambda c: c["detail"]["impact"][1].__setitem__("reach", ["your attention each week"]),
     "the reach (full detail)"),
]
PROCESS_CLEAN = ["the code review checklist gains a step", "a comment in the hook explains the guard",
                 "a round-trip per request", "the reviewer agent reads the new rule"]


@unittest.skipUnless(NODE, "node is not installed")
class SystemLint(unittest.TestCase):
    """The runner's `process` lint: process phrases in an Effect or Reach, never bare words."""

    def process_lines(self, d):
        return [x for x in runner(d)[1].splitlines() if "names the process" in x]

    def test_the_example_is_clean(self):
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_each_phrase_fires_where_effect_and_reach_are_read(self):
        for name, put, where in PROCESS_FIRES:
            with self.subTest(field=name):
                d = example()
                put(d["cards"][0])
                code, out, _ = runner(d)
                self.assertEqual(code, 2, out)
                self.assertIn("lint: card 41: impact: " + where + " names the process", out)

    def test_wait_z_and_a_round_ask_are_never_read(self):
        d = example()
        d["cards"][0]["impact"]["wait"] = "review comments wait for you"
        d["cards"][0]["o"][-1][2] = "another round of review waits"
        self.assertEqual(self.process_lines(d), [])
        d = example()
        d["cards"][0]["impact"]["effect"] = "review comments wait"
        d["cards"][0]["ifleft"] = "the leftover findings stay open"
        self.assertEqual(self.process_lines(d), [])

    def test_system_effects_that_share_a_word_stay_clean(self):
        for s in PROCESS_CLEAN:
            with self.subTest(text=s):
                d = example()
                d["cards"][0]["impact"]["effect"] = s
                d["cards"][0]["impact"]["reach"] = s
                self.assertEqual(self.process_lines(d), [])


# ---- S2 (mechanism on the page), rule 268

def mechanism_text_problems(digest, schema, skill, rulings):
    out = []
    if "the options, each with its consequence by its mechanism: how it happens, who meets it and when, and the before and after" not in flat(digest):
        out.append("the digest's floor does not ask for the mechanism")
    if "Could you say how it happens, not only that it does?" not in flat(digest):
        out.append("the digest's cold read does not ask it")
    if "`happens` the effect by its mechanism" not in flat(schema):
        out.append("the schema's blocks row does not say it")
    if "each effect by its mechanism" not in flat(skill):
        out.append("SKILL.md does not say it")
    b = bullet(rulings, "Explain the mechanism")
    if "On the answer page (2026-10-22, *Both surfaces*" not in b or "`mech` lint" not in b:
        out.append("rule 268 does not name its page form")
    return out


class MechanismText(unittest.TestCase):
    def setUp(self):
        self.args = [DIGEST.read_text(), SCHEMA.read_text(), PAGE_SKILL_MD.read_text(), RULINGS.read_text()]

    def test_the_page_says_it(self):
        self.assertEqual(mechanism_text_problems(*self.args), [])

    def test_mutations(self):
        for i, (old, new) in enumerate([("by its mechanism: how", "by its: how"),
                                        ("`happens` the effect by its mechanism", "`happens` the effect"),
                                        ("each effect by its mechanism", "each effect"),
                                        ("`mech` lint", "lint")]):
            with self.subTest(old=old):
                args = list(self.args)
                j = [0, 1, 2, 3][i]
                self.assertIn(old, args[j])
                args[j] = args[j].replace(old, new)
                self.assertTrue(mechanism_text_problems(*args))


@unittest.skipUnless(NODE, "node is not installed")
class MechanismLint(unittest.TestCase):
    """The runner's `mech` lint: an option's effect of a bare label, four words or fewer."""

    def mech_lines(self, d):
        return [x for x in runner(d)[1].splitlines() if "say its mechanism" in x]

    def test_the_example_is_clean(self):
        self.assertEqual(runner(example())[:2], (0, ""))

    def test_a_bare_label_fires(self):
        d = example()
        d["cards"][0]["blocks"]["a"]["happens"] = "importers break"
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn('lint: card 41: impact: (a)\'s effect is 2 words ("importers break"): say its '
                      "mechanism", out)

    def test_a_no_change_statement_and_z_stay_clean(self):
        d = example()
        d["cards"][0]["blocks"]["a"]["happens"] = "Nothing changes."
        d["cards"][0]["o"][-1][2] = "it waits"
        self.assertEqual(self.mech_lines(d), [])

    def test_an_option_with_no_row_is_read_from_its_impact(self):
        d = example()
        del d["cards"][2]["blocks"]
        d["cards"][2]["o"][1][2] = "screenshots break"
        self.assertEqual(self.mech_lines(d), ["lint: card 43: impact: (b)'s effect is 2 words "
                                              '("screenshots break"): say its mechanism, how it '
                                              "happens, who meets it and when, and the before and "
                                              "after; or leave it knowingly"])

    def test_the_threshold_is_four_words(self):
        d = example()
        d["cards"][0]["blocks"]["a"]["happens"] = "the importers break downstream"
        self.assertEqual(len(self.mech_lines(d)), 1)
        d["cards"][0]["blocks"]["a"]["happens"] = "the importers break downstream today"
        self.assertEqual(self.mech_lines(d), [])


# ---- S4 (bundles as page groups), rule 263

# data in; check() and each layer's heading, rendered by the page-free helper, out
LAYER_HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
const bad = check(d);
let layers = [];
if (!bad.length) {
  CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow; LAYERS = d.layers;
  byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
  layers = LAYERS.map(l => layerHtml(l, CARDS.filter(c => c.L === l[0])));
}
process.stdout.write(JSON.stringify({bad, layers}));
"""


def node_page(data, harness, script=None):
    out = subprocess.run([NODE, "-e", (script or page_free_script()) + harness],
                         input=json.dumps(data), capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


SHARED = ("A redirect is one config line that sends a reader from an old URL to its new one. "
          "Both cards follow the move to CI.")


def bundle():
    d = example()
    d["layers"][1].append(SHARED)
    return d


def heading(h):
    """The band before the cards."""
    return h[:h.index('<div class="gcards">')]


def band_problems(h, n, shared):
    """What a layer's band lacks: the Group label, its count, the share line, and the Shared context
    fold, closed, its summary the first sentence (only when the layer has shared context)."""
    out = []
    head = heading(h)
    if '<span class="lbl">Group</span>' not in head:
        out.append("no Group label")
    if '<span class="pill cls">%d decision%s</span>' % (n, "" if n == 1 else "s") not in head:
        out.append("no count")
    if '<span class="lbl inl">What they share:</span>' not in head:
        out.append("no share line")
    fold = re.search(r'<details class="gfold"( open)?><summary>(.*?)</summary>', head)
    if shared is None:
        if fold:
            out.append("a plain layer shows a Shared context fold")
        return out
    if not fold:
        out.append("no Shared context fold")
    elif fold.group(1):
        out.append("the Shared context fold is open")
    elif shared.split(". ")[0] not in fold.group(2) or "Both cards" in fold.group(2):
        out.append("the fold's summary is not the first sentence")
    return out


@unittest.skipUnless(NODE, "node is not installed")
class BundleGroups(unittest.TestCase):

    def test_the_example_and_a_bundle_pass_the_check(self):
        self.assertEqual(node_page(example(), LAYER_HARNESS)["bad"], [])
        self.assertEqual(node_page(bundle(), LAYER_HARNESS)["bad"], [])

    def test_a_non_text_shared_is_refused(self):
        for v in (3, ["x"], {"t": "x"}):
            d = example()
            d["layers"][1].append(v)
            self.assertIn("layer 1: shared (its fourth element) must be text: the context every card "
                          "in the bundle shares", node_page(d, LAYER_HARNESS)["bad"])

    def test_a_bundle_shows_its_band_and_a_closed_fold(self):
        res = node_page(bundle(), LAYER_HARNESS)
        self.assertEqual(band_problems(res["layers"][1], 2, SHARED), [])
        self.assertIn(SHARED, res["layers"][1])
        # the cards follow, under the rail
        self.assertLess(res["layers"][1].index('<div class="gcards">'), res["layers"][1].index('id="card-42"'))

    def test_a_plain_layer_shows_no_fold(self):
        res = node_page(example(), LAYER_HARNESS)
        self.assertEqual(band_problems(res["layers"][0], 1, None), [])
        self.assertEqual(band_problems(res["layers"][1], 2, None), [])

    def test_mutations(self):
        h = node_page(bundle(), LAYER_HARNESS)["layers"][1]
        self.assertIn("the Shared context fold is open",
                      band_problems(h.replace('<details class="gfold">', '<details class="gfold" open>'), 2, SHARED))
        plain = node_page(example(), LAYER_HARNESS)["layers"][1]
        self.assertIn("no Shared context fold", band_problems(plain, 2, SHARED))
        self.assertIn("a plain layer shows a Shared context fold", band_problems(h, 2, None))
        self.assertIn("no count", band_problems(h, 3, SHARED))

    def test_the_heading_is_escaped(self):
        d = example()
        d["layers"][1][1] = "<script>x</script>"
        d["layers"][1].append('<img src=x onerror="alert(1)"> shared.')
        h = node_page(d, LAYER_HARNESS)["layers"][1]
        self.assertNotIn("<script>", h)
        self.assertNotIn("<img", h)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", h)


@unittest.skipUnless(NODE, "node is not installed")
class BundleRunner(unittest.TestCase):

    def test_a_count_glossed_only_in_the_shared_context(self):
        d = bundle()
        d["layers"][1][3] = SHARED + " The three are the build, the cache and the publish step."
        d["cards"][2]["tldr"][-1] = "Start the three now"
        self.assertEqual(runner(d)[:2], (0, ""))
        # the same card in a plain layer: its Context alone does not name the three
        d["layers"][1].pop()
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn('lint: card 43: "three" counts things its context does not name', out)

    def test_a_one_card_bundle_is_linted(self):
        d = example()
        d["layers"][0].append("The build moves to CI.")
        code, out, _ = runner(d)
        self.assertEqual(code, 2, out)
        self.assertIn("lint: page: group direction holds 1 card: a bundle", out)
        # two cards: clean
        self.assertEqual(runner(bundle())[:2], (0, ""))

    def test_an_id_in_the_shared_context_is_linted(self):
        d = bundle()
        d["layers"][1][3] += " See KAPPA-3570."
        self.assertIn("lint: page: KAPPA-3570 looks like an id (the shared context of layer details)",
                      runner(d)[1])


def bundle_text_problems(rendering, rulings, schema):
    out = []
    if "On an answer page a group is a layer carrying its shared context" not in flat(rendering):
        out.append("rendering.md does not say a page group carries its shared context")
    b = bullet(rulings, "Bundles as groups of whole item cards")
    if "On the answer page (2026-10-22, *Both surfaces*" not in b or "Shared context fold" not in b:
        out.append("rule 263 does not name its page form")
    if "A `cards.json` written before bundle groups (2026-10-22)" not in flat(schema):
        out.append("no older-data paragraph")
    return out


class BundleText(unittest.TestCase):
    def setUp(self):
        self.args = [(PLUGIN / "skills" / "decisions" / "references" / "rendering.md").read_text(),
                     RULINGS.read_text(), SCHEMA.read_text()]

    def test_both_skills_say_it(self):
        self.assertEqual(bundle_text_problems(*self.args), [])

    def test_mutations(self):
        r, ru, sc = self.args
        self.assertTrue(bundle_text_problems(r.replace("On an answer page a\n  group is a layer", "A group"), ru, sc))
        self.assertTrue(bundle_text_problems(r, ru.replace("Shared context fold", "fold"), sc))
        self.assertTrue(bundle_text_problems(r, ru, sc.replace("before bundle groups", "before")))


# ---- V2 (the label after the title on the page), answer 313

TITLE_HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(d.cards.map(c => titleHtml(c))));
"""
TITLE_DEF = "const titleHtml=c=>esc(c.t)+srcLabel(c);"


def title_problems(h, t, label_id):
    """A labelled title that does not open on its title, or whose label is not muted after it."""
    if not h.startswith(t):
        return ["the title does not come first"]
    if not re.search(r'<span class="slabm"> · <span class="slab">' + re.escape(label_id) + r'</span>', h):
        return ["the label is not after the title, muted"]
    return []


@unittest.skipUnless(NODE, "node is not installed")
class LabelAfterTitle(unittest.TestCase):

    def test_the_title_comes_first(self):
        titles = node_page(example(), TITLE_HARNESS)
        self.assertEqual(title_problems(titles[2], "Theme colour", "D3"), [])
        # a card with no label keeps its title alone
        self.assertEqual(titles[0], "Docs build home")

    def test_mutant_label_first(self):
        script = page_free_script()
        self.assertIn(TITLE_DEF, script)
        mutant = script.replace(TITLE_DEF, "const titleHtml=c=>srcLabel(c)+esc(c.t);")
        titles = node_page(example(), TITLE_HARNESS, mutant)
        self.assertEqual(title_problems(titles[2], "Theme colour", "D3"), ["the title does not come first"])


LABEL_CLAUSE = "On an answer page the label follows the title (the `decision-page` skill)"


def label_text_problems(rendering, plain, rulings):
    out = []
    if LABEL_CLAUSE not in flat(rendering):
        out.append("rendering.md lacks the page clause")
    if LABEL_CLAUSE not in flat(plain):
        out.append("plain-names lacks the page clause")
    b = bullet(rulings, "The label after the title on an answer page")
    if "(2026-10-22, answer 313" not in b or "Not taken: the label first on the page too" not in b:
        out.append("no ruling for the label after the title, dated, with its Not taken")
    if "since answer 313 the page puts the title first" not in bullet(rulings, "Source labels first, with a short name"):
        out.append("269's ruling does not say the page half changed")
    return out


class LabelText(unittest.TestCase):
    def setUp(self):
        self.args = [(PLUGIN / "skills" / "decisions" / "references" / "rendering.md").read_text(),
                     (PLUGIN / "skills" / "plain-names" / "SKILL.md").read_text(), RULINGS.read_text()]

    def test_both_skills_say_it(self):
        self.assertEqual(label_text_problems(*self.args), [])

    def test_mutations(self):
        r, p, ru = self.args
        cut = lambda s: s.replace("On an answer page the label follows the title", "")
        self.assertIn("rendering.md lacks the page clause", label_text_problems(cut(r), p, ru))
        self.assertIn("plain-names lacks the page clause", label_text_problems(r, cut(p), ru))
        self.assertTrue(label_text_problems(r, p, ru.replace("**The label after the title on an answer page**", "**Labels**")))
        self.assertTrue(label_text_problems(r, p, ru.replace("Not taken: the label first on the page too", "Not taken: none")))
        self.assertTrue(label_text_problems(r, p, ru.replace("since answer 313 the page puts", "the page puts")))


# ---- V1 (the page shell): the group map, the rows and their quick answers

CARD_HARNESS = r"""
const d = JSON.parse(require("fs").readFileSync(0, "utf8"));
const bad = check(d);
let out = {bad};
if (!bad.length) {
  CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow; LAYERS = d.layers;
  byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
  out.cards = CARDS.map(c => ({n: c.n, html: cardHtml(c), row: rowHtml(c)}));
  out.map = mapHtml();
  out.set = (d._hows || []).map(how => { const ds = [{open: false}, {open: true}]; setAll(ds, how); return ds.map(x => x.open); });
}
process.stdout.write(JSON.stringify(out));
"""


def quick_problems(h, rec):
    """Quick answers inside the row's open-and-close control, or the wrong ones beside it."""
    out = []
    inside = h[h.index("<details"):h.rindex("</details>")]
    if "data-quick" in inside:
        out.append("a quick answer sits inside the row's toggle")
    tail = h[h.rindex("</details>"):]
    if ('data-quick="rec"' in tail) != rec:
        out.append("Use recommendation is wrong for the card")
    if 'data-quick="later"' not in tail:
        out.append("no Later")
    return out


def row_extra_problems(row, cls):
    out = []
    if cls in row:
        out.append("the row shows the class")
    if "depends on" in row:
        out.append("the row shows what the card depends on")
    return out


def row_order_problems(row):
    marks = ['class="tw"', 'class="n"', "<h3>", 'class="pill warn"', 'class="rrec"', 'class="ans"']
    pos = [row.find(m) for m in marks]
    return [] if -1 not in pos and pos == sorted(pos) else ["the row's parts are out of order or missing"]


def map_problems(m, want):
    got = re.findall(r'<button class="btn" type="button" data-go="layer-([^"]+)">([^<]*)</button>', m)
    out = [] if got == want else ["the map's groups are %r, not %r" % (got, want)]
    for label in ("Expand all", "Collapse all"):
        if ">%s</button>" % label not in m:
            out.append("no " + label)
    return out


@unittest.skipUnless(NODE, "node is not installed")
class PageShell(unittest.TestCase):

    def test_quick_answers_sit_beside_the_row(self):
        res = node_page(example(), CARD_HARNESS)
        for c, d in zip(res["cards"], example()["cards"]):
            self.assertEqual(quick_problems(c["html"], bool(d["rec"])), [], c["n"])
        # card 43 has no recommendation: Later only
        self.assertNotIn('data-quick="rec"', res["cards"][2]["html"])
        # mutant: the buttons inside the row's toggle
        h = res["cards"][0]["html"]
        quick = h[h.rindex('<span class="quick">'):h.rindex("</span>") + len("</span>")]
        moved = h.replace(quick, "").replace("</summary>", quick + "</summary>", 1)
        self.assertIn("a quick answer sits inside the row's toggle", quick_problems(moved, True))

    def test_a_click_writes_the_answer_and_the_pressed_state_follows(self):
        html = PAGE.read_text()
        click = html[html.index('document.addEventListener("click"'):html.index('addEventListener("resize"')]
        self.assertIn('choose(n,q.dataset.quick==="rec"?c.rec:"later")', click)
        sync = html[html.index("function syncCard("):html.index("function syncAll(")]
        self.assertIn('b.setAttribute("aria-pressed"', sync)

    def test_the_row(self):
        d = example()
        d["cards"][0]["dep"] = "[[42]] (a)"
        res = node_page(d, CARD_HARNESS)
        r41, r42 = res["cards"][0]["row"], res["cards"][1]["row"]
        # the class pill and the depends on clause are not on the row
        self.assertEqual(row_extra_problems(r41, "trust"), [])
        self.assertEqual(row_order_problems(r42), [])
        # the row holds no control and no link: it is the card's toggle
        for c in res["cards"]:
            self.assertNotIn("<button", c["row"])
            self.assertNotIn("<a ", c["row"])
        # mutants: a class pill, or the depends on clause, restored in the row
        self.assertTrue(row_extra_problems(r41 + '<span class="pill cls">trust</span>', "trust"))
        self.assertTrue(row_extra_problems(r41 + '<span>depends on: 42</span>', "trust"))

    def test_the_map(self):
        res = node_page(example(), CARD_HARNESS)
        want = [("direction", "Direction · 1"), ("details", "Details · 2")]
        self.assertEqual(map_problems(res["map"], want), [])
        # mutant: a group dropped from the map
        dropped = res["map"].replace('<button class="btn" type="button" data-go="layer-direction">Direction · 1</button>', "")
        self.assertTrue(map_problems(dropped, want))

    def test_expand_all_and_collapse_all(self):
        m = node_page(example(), CARD_HARNESS)["map"]
        how = dict((label, v) for v, label in re.findall(r'data-all="([a-z]+)">([^<]+)</button>', m))
        d = example()
        d["_hows"] = [how["Expand all"], how["Collapse all"]]
        self.assertEqual(node_page(d, CARD_HARNESS)["set"], [[True, True], [False, False]])
        # mutant: Collapse all left opening
        d["_hows"] = [how["Expand all"], how["Expand all"]]
        self.assertNotEqual(node_page(d, CARD_HARNESS)["set"][1], [False, False])


def popup_problems(schema, html):
    out = []
    if re.search(r"popup", schema, re.I):
        out.append("the schema names a popup")
    if re.search(r"tag size[^.|]*\bin\s+the\s+map|\bthe map and a closed card", flat(schema)):
        out.append("the schema puts the effect in the map")
    lede = static_lede(html)
    if ("hover over it or focus it to see it, and click it to open its card" not in lede
            or "a second tap, a tap elsewhere or Escape closes it" not in lede
            or "hover or click it to see that decision" in lede):
        out.append("the lede's reference sentence is not the tooltip's")
    if "At a glance" in html or 'id="pop"' in html:
        out.append("the page keeps the heads-up map or the popup")
    return out


class ShellText(unittest.TestCase):
    def setUp(self):
        self.schema = SCHEMA.read_text()
        self.html = PAGE.read_text()
        self.rulings = RULINGS.read_text()

    def test_no_popup_and_the_lede(self):
        self.assertEqual(popup_problems(self.schema, self.html), [])

    def test_mutations(self):
        restored = self.schema.replace("first on the open card; its medium", "first on the open card and in the popup; its medium")
        self.assertNotEqual(restored, self.schema)
        self.assertIn("the schema names a popup", popup_problems(restored, self.html))
        old = self.html.replace("hover over it or focus it to see it, and click it to open its card",
                                "hover or click it to see that decision")
        self.assertIn("the lede's reference sentence is not the tooltip's", popup_problems(self.schema, old))

    def test_the_ruling(self):
        b = bullet(self.rulings, "Cards as rows under a group map")
        self.assertIn("(2026-10-22, the operator's prototype feedback", b)
        self.assertIn("Not taken: the \"At a glance\" map beside open cards (as built)", b)
        self.assertIn("are the operator's words (2026-10-22); the tooltip's layout", b)
        self.assertIn("a reference's tooltip shows a card's Context", bullet(self.rulings, "TLDR first on an answer page"))
        cut = self.rulings.replace("**Cards as rows under a group map**", "**Rows**")
        self.assertEqual(bullet(cut, "Cards as rows under a group map"), "")


if __name__ == "__main__":
    unittest.main()
