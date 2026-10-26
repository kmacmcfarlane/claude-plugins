"""The finding, after What (F7, answer 337 (a)): on a card raised from a finding, on both surfaces.

Three parts:

- the decision page (`decision-page` skill, under node): `findingPart` renders the record's
  `finding`, `{label, title, where, mechanism, excerpt}`, after the What part and before the folds
  above the Impact, never folded: its head (the label with its short name, the title, where it
  lives), its mechanism, and its excerpt through the page's one code-block renderer (`codeBlock`,
  escaped and never parsed); every other field through `fmt`. `check()` refuses a malformed
  finding, and a label other than the card's own;
- the pre-publish runner (`scripts/check_cards.js`, under node): the id lint reads the finding's
  label, title, where and mechanism (a label the finding declares passes with its short name),
  never its excerpt; the cold read reads its title and mechanism; the `mech` lint reads its
  mechanism;
- the chat card (the `decisions` skill): the **Finding:** line after **What:** in the card and
  block templates, its head form, its label the title's own, its mechanism line and its fenced
  excerpt, on every gallery card raised from a finding; the findings-set texts offering the page.

Each check is proved by a mutation: a broken template, runner or text fails it.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import json
import re
import subprocess
import sys
import unittest

from test_impact import NODE, PAGE, CARD_HEAD, example, page_free_script, finding_end
from test_context import runner, RUNNER, SKILL
from test_record import run_record, record_of
from test_items import mutant_runner
from test_chat_context import fenced, views, heads, GALLERY, RENDERING, SKILL_MD, REFS


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the Finding's page and runner tests (FindingPage, "
              "FindingRunner) are skipped, so its render, its check and its lints went untested",
              file=sys.stderr)


HARNESS = r"""
const ds = JSON.parse(require("fs").readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(ds.map(d => {
  const bad = check(d);
  if (bad.length) return {bad, cards: {}};
  CARDS = d.cards; REFS = d.refs || {}; FOLLOW = d.follow;
  byN = new Map(CARDS.map(c => [String(c.n), c])); FOLLOW_KEYS = new Set(FOLLOW.map(f => f[0]));
  answers = {};
  return {bad, cards: Object.fromEntries(CARDS.map(c => [c.n, {fnd: findingPart(c), card: cardHtml(c)}]))};
})));
"""


def render(datasets, script=None):
    out = subprocess.run([NODE, "-e", (script or page_free_script()) + HARNESS],
                         input=json.dumps(datasets), capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr[:400])
    return json.loads(out.stdout)


def one(d, script=None):
    return render([d], script)[0]


def c43(d):
    return next(c for c in d["cards"] if c["n"] == 43)


def mutant_page(old, new):
    script = page_free_script()
    assert script.count(old) == 1, old
    return script.replace(old, new)


HOSTILE = ['<script>alert(1)</script>', '<img src=x onerror="alert(1)">']


@unittest.skipUnless(NODE, "node is not installed")
class FindingPage(unittest.TestCase):

    def test_the_example_shows_card_43s_finding(self):
        res = one(example())
        self.assertEqual(res["bad"], [])
        f = res["cards"]["43"]["fnd"]
        self.assertTrue(f.startswith('<div class="fnd"><span class="lbl">Finding</span>'), f)
        self.assertIn('<p class="fndh"><span class="slab">D3</span> (site colour off the logo): Links and headings '
                      'keep the launch blue — <span class="fwhere">theme/colors.toml, lines 3 to 6</span></p>', f)
        self.assertIn("<p>The theme file sets the accent colour", f)
        # the excerpt through the one code-block renderer, verbatim and escaped
        self.assertIn('<figure class="xc" data-lines="4">', f)
        self.assertIn('<span class="pill cls">toml</span>', f)
        self.assertIn('link = &quot;#1f5fbf&quot;', f)
        # the other cards have none
        self.assertEqual(res["cards"]["41"]["fnd"], "")
        self.assertEqual(res["cards"]["42"]["fnd"], "")
        # mutant: the part left out of the card
        res = one(example(), mutant_page("+whatPart(c)+findingPart(c)+openFold(c)", "+whatPart(c)+openFold(c)"))
        self.assertNotIn('<div class="fnd">', res["cards"]["43"]["card"])

    def test_it_sits_after_what_before_the_folds_and_is_never_folded(self):
        def problems(script=None):
            card = one(example(), script)["cards"]["43"]["card"]
            if '<div class="fnd">' not in card:
                return ["no finding"]
            at = card.index('<div class="fnd">')
            out = []
            if not card.index('<div class="what">') < at:
                out.append("before What")
            if not at < card.index('class="gfold afold"') or not at < card.index('class="impline"'):
                out.append("after the folds or the Impact")
            if card[:at].count("<details") - card[:at].count("</details>") != 1:
                out.append("inside a fold")
            return out
        self.assertEqual(problems(), [])
        # mutants: before What; inside the Assumptions fold
        self.assertTrue(problems(mutant_page("+whatPart(c)+findingPart(c)+", "+findingPart(c)+whatPart(c)+")))
        self.assertTrue(problems(mutant_page(
            "+whatPart(c)+findingPart(c)+openFold(c)+assumeFold(c,P)",
            "+whatPart(c)+openFold(c)+assumeFold(c,P).replace('<div>','<div>'+findingPart(c))")))

    def test_every_field_is_escaped_and_the_excerpt_never_parsed(self):
        def problems(script=None):
            out = []
            for v in HOSTILE:
                d = example()
                f = c43(d)["finding"]
                c43(d)["label"] = f["label"] = {"id": "D3", "name": v}
                f.update({"title": v, "where": v, "mechanism": v + " — see [[41]]",
                          "excerpt": {"text": v + "\n`code` [[41]] https://example.com", "src": v}})
                res = one(d, script)
                if res["bad"]:
                    return ["refused: %s" % res["bad"]]
                h = res["cards"]["43"]["fnd"]
                for bad in ("<script", "<img"):
                    if bad in h:
                        out.append("%r renders %s" % (v, bad))
                code = h[h.index("<pre"):] if "<pre" in h else ""
                if not code:
                    out.append("no code block")
                for mark in ("slug", "<code>code</code>", "<a ", "<button"):
                    if mark in code:
                        out.append("the excerpt rendered a mark: " + mark)
            return out
        self.assertEqual(problems(), [])
        # a slug in the mechanism is a mark, as in every text field
        d = example()
        c43(d)["finding"]["mechanism"] = "it follows [[41]] (b)"
        self.assertIn("slug", one(d)["cards"]["43"]["fnd"])
        # mutants: the mechanism drawn raw; the excerpt drawn through the mark renderer
        self.assertTrue(problems(mutant_page("+'<p>'+fmt(f.mechanism)+'</p>'", "+'<p>'+f.mechanism+'</p>'")))
        self.assertTrue(problems(mutant_page("?codeBlock(f.excerpt):''", "?'<pre>'+fmtD(f.excerpt.text)+'</pre>':''")))
        self.assertTrue(problems(mutant_page("<span class=\"fwhere\">'+fmt(f.where)", "<span class=\"fwhere\">'+f.where")))

    def test_check_refuses_a_malformed_finding(self):
        cases = {
            "finding must be {label, title, where, mechanism, excerpt}": lambda c: c.__setitem__("finding", "x"),
            "finding needs its mechanism": lambda c: c["finding"].pop("mechanism"),
            "finding mechanism must be one paragraph": lambda c: c["finding"].__setitem__("mechanism", "a\nb"),
            "finding title must be one line of text": lambda c: c["finding"].__setitem__("title", "a\nb"),
            "finding where must be one line of text": lambda c: c["finding"].__setitem__("where", 3),
            "finding label must be {id, name}": lambda c: c["finding"].__setitem__("label", "D3"),
            "finding label must be the card's own label, D3 (site colour off the logo)":
                lambda c: c["finding"].__setitem__("label", {"id": "D4", "name": "site colour off the logo"}),
            "finding excerpt: an excerpt's lang must be a short label":
                lambda c: c["finding"]["excerpt"].__setitem__("lang", "<b>"),
            "finding excerpt: an excerpt needs text": lambda c: c["finding"]["excerpt"].__setitem__("text", " "),
        }
        for needle, put in cases.items():
            with self.subTest(needle):
                d = example()
                put(c43(d))
                bad = one(d)["bad"]
                self.assertTrue(any(b.startswith("card 43: ") and needle in b for b in bad), bad)
        # the same short name under another label, or the card with no label of its own: both pass where sound
        d = example()
        del c43(d)["label"]
        self.assertEqual(one(d)["bad"], [])
        # mutant: the label agreement gone, another label passes
        old = 'else if(isLabel(c.label)&&(f.label.id!==c.label.id||f.label.name!==c.label.name))'
        d = example()
        c43(d)["finding"]["label"] = {"id": "D4", "name": "another name"}
        self.assertEqual(one(d, mutant_page(old, "else if(false)"))["bad"], [])

    def test_none_is_not_shown(self):
        d = example()
        f = c43(d)["finding"]
        f["where"], f["title"] = "n/a", "none"
        h = one(d)["cards"]["43"]["fnd"]
        self.assertNotIn("n/a", h)
        self.assertNotIn('class="fwhere"', h)
        self.assertIn('<p class="fndh"><span class="slab">D3</span> (site colour off the logo)</p>', h)
        # a none mechanism: no part at all
        f["mechanism"] = "none"
        self.assertEqual(one(d)["cards"]["43"]["fnd"], "")

    def test_a_slug_in_the_finding_is_checked_and_one_in_its_excerpt_is_not(self):
        d = example()
        c43(d)["finding"]["mechanism"] = "it follows [[99]]"
        self.assertTrue(any("[[99]] is neither" in b for b in one(d)["bad"]))
        d = example()
        c43(d)["finding"]["excerpt"]["text"] = "see [[99]]"
        self.assertEqual(one(d)["bad"], [])


def lints(out):
    return [x for x in out.splitlines() if x.startswith("lint:")]


@unittest.skipUnless(NODE, "node is not installed")
class FindingRunner(unittest.TestCase):

    def test_the_example_is_clean_and_so_is_its_record(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        self.assertEqual(run_record(record_of(c43(example()))), (0, ""))

    def test_the_id_lint_reads_the_finding_but_never_its_excerpt(self):
        for k in ("title", "where", "mechanism"):
            with self.subTest(k):
                d = example()
                c43(d)["finding"][k] = "raised as OQ3 in the review"
                self.assertIn("lint: card 43: OQ3 looks like an id (finding)", runner(d)[1])
        d = example()
        c43(d)["finding"]["excerpt"]["src"] = "theme/colors.toml at 8ea8a3c, OQ3"
        c43(d)["finding"]["excerpt"]["text"] = "OQ3 = 7c41e0d"
        self.assertEqual(runner(d)[:2], (0, ""))
        # mutant: the finding left out of the id lint
        d = example()
        c43(d)["finding"]["mechanism"] = "raised as OQ3 in the review"
        js = mutant_runner('put("finding", [', 'put("finding", [] || [')
        self.assertNotIn("OQ3 looks like an id", runner(d, script=js)[1])

    def test_a_label_the_finding_declares_passes_with_its_short_name(self):
        # the card without a label of its own: the finding's declares D3 for the whole page
        d = example()
        del c43(d)["label"]
        self.assertEqual(runner(d)[:2], (0, ""))
        # mutant: the finding's label not declared, and the context's D3 is an id
        js = mutant_runner('cards.flatMap(c => [c.label, c.finding && typeof c.finding === "object" ? c.finding.label : null])',
                           'cards.flatMap(c => [c.label])')
        self.assertIn("lint: card 43: D3 looks like an id (context)", runner(d, script=js)[1])

    def test_the_cold_read_reads_its_title_and_mechanism(self):
        for k in ("title", "mechanism"):
            with self.subTest(k):
                d = example()
                c43(d)["finding"][k] = "the theme sets seven colours from the launch palette, so links stay blue"
                self.assertIn('lint: card 43: "seven" (the finding) counts things its context does not name',
                              runner(d)[1])
        # where is a location and is not read: a line range counts nothing
        d = example()
        c43(d)["finding"]["where"] = "theme/colors.toml, lines 30 and 31"
        self.assertEqual(runner(d)[:2], (0, ""))
        # mutant: the finding left out of the cold read
        d = example()
        c43(d)["finding"]["mechanism"] = "the theme sets seven colours from the launch palette, so links stay blue"
        js = mutant_runner('terms(findingTexts(c), " (the finding)");', '')
        self.assertNotIn("(the finding)", runner(d, script=js)[1])

    def test_a_bare_label_for_a_mechanism_is_the_mech_lint(self):
        d = example()
        c43(d)["finding"]["mechanism"] = "wrong accent colour"
        out = runner(d)[1]
        self.assertIn('lint: card 43: impact: the finding\'s mechanism is 3 words ("wrong accent colour")', out)
        js = mutant_runner("if (typeof fm === \"string\" && words(fm) <= MECH_MIN)", "if (false)")
        self.assertNotIn("the finding's mechanism", runner(d, script=js)[1])

    def test_the_finding_counts_in_the_card_in_all_but_not_its_excerpt(self):
        d = example()
        long = " ".join(["word"] * 900)
        c43(d)["finding"]["excerpt"]["text"] = long
        self.assertNotIn("in all", runner(d)[1])
        c43(d)["finding"]["mechanism"] = "The theme sets the colour. " + long
        self.assertIn("lint: card 43: depth: the card is", runner(d)[1])
        js = mutant_runner("+ words(findingWords(c)) ", "")
        self.assertNotIn("depth: the card is", runner(d, script=js)[1])


# the gallery's cards raised from a finding: a review's (51-53, 97) and an audit's (88)
FINDING_CARDS = {51, 52, 53, 88, 97}
# **Finding:** label (short name)[: title] — `where`, or a head with no label
FINDING_HEAD = re.compile(r"^\*\*Finding:\*\* (?:(?P<id>\S+) \((?P<name>[^)]+)\)(?:: (?P<t1>.+?))?|(?P<t2>[^`]+?))"
                          r" — `[^`]+`$")
TITLE_LABEL = re.compile(r"^\*\*\d+ — (\S+) \(([^)]+)\) · ")


def finding_problems(where, body, raised):
    """A view's Finding against the rules: present on a card raised from a finding, after What
    and its bullets, before the folds and the Impact; its head's form; its label the title's;
    its mechanism line; any excerpt fenced with its language."""
    out = []
    at = [i for i, x in enumerate(body) if x.startswith("**Finding:**")]
    if not at:
        return [where + ": no Finding"] if raised else []
    if len(at) > 1:
        out.append(where + ": more than one Finding")
    k = at[0]
    w = next((i for i, x in enumerate(body) if x.startswith("**What:**")), None)
    if w is None or w > k:
        out.append(where + ": the Finding is not after What")
    elif any(not x.startswith("- ") for x in body[w + 1:k]):
        out.append(where + ": something but What's items stands between What and the Finding")
    later = [i for i, x in enumerate(body) if x.startswith(("▸ ", "▾ ", "**Impact:**"))]
    if not later or min(later) < k:
        out.append(where + ": the Finding is not before the folds and the Impact")
    m = FINDING_HEAD.match(body[k])
    if not m:
        out.append(where + ": the Finding's head is not `**Finding:** label (name): title — `where``")
    else:
        t = TITLE_LABEL.match(body[0])
        if t and (m.group("id"), m.group("name")) != t.groups():
            out.append(where + ": the Finding's label is not the title's, with its short name")
    mech = body[k + 1] if k + 1 < len(body) else ""
    if not mech.strip() or mech.startswith(("```", "**", "▸", "▾", "- ")):
        out.append(where + ": no mechanism line under the Finding's head")
    elif len(mech.split()) <= 4:
        out.append(where + ": the mechanism is a bare label")
    if k + 2 < len(body) and body[k + 2].startswith("```"):
        if not re.match(r"^```[A-Za-z0-9][A-Za-z0-9+#._-]*$", body[k + 2]):
            out.append(where + ": the excerpt's fence has no language")
        if finding_end(body, k) > len(body):
            out.append(where + ": the excerpt's fence is not closed")
    return out


class FindingChat(unittest.TestCase):

    def test_the_templates_put_the_finding_after_what(self):
        text = RENDERING.read_text()
        card = fenced(text, "**N — Title as a question?**\n**Context:**")
        self.assertEqual(heads(card)[:4], ["Context", "What", "Finding", "Impact"])
        k = next(i for i, x in enumerate(card) if x.startswith("**Finding:**"))
        self.assertRegex(card[k], r"^\*\*Finding:\*\* F7 \(short name\): .+ — `[^`]+`")
        self.assertTrue(card[k + 1].startswith("how it happens"), card[k + 1])
        self.assertIn("fenced block", card[k + 2])
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(heads(block)[:3], ["Context", "What", "Finding"])
        # the rule's words
        self.assertIn("- **Finding:** on a card raised from a finding", text)
        self.assertIn("answer 337 (a)", text)

    def test_every_gallery_card_raised_from_a_finding_shows_it(self):
        seen = set()
        for n, kind, body in views(GALLERY):
            num = int(re.match(r"^\*\*(\d+)", body[0]).group(1)) if re.match(r"^\*\*\d+ — ", body[0]) else None
            raised = num in FINDING_CARDS or bool(TITLE_LABEL.match(body[0]))
            if any(x.startswith("**Finding:**") for x in body):
                seen.add(num)
            self.assertEqual(finding_problems(f"gallery.md:{n}", body, raised), [])
        self.assertEqual(seen, FINDING_CARDS)

    def test_the_finding_checks_fail_on_broken_cards(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**97 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("**Finding:**"))
        w = next(i for i, x in enumerate(body) if x.startswith("**What:**"))
        mutants = {
            "left out": body[:k] + body[finding_end(body, k):],
            "before What": body[:w] + body[k:finding_end(body, k)] + body[w:k] + body[finding_end(body, k):],
            "another short name": body[:k] + [body[k].replace("(unescaped display name)", "(raw name)")] + body[k + 1:],
            "no location": body[:k] + [body[k].split(" — `")[0]] + body[k + 1:],
            "a bare mechanism": body[:k + 1] + ["XSS in the email"] + body[k + 2:],
            "no language": body[:k + 2] + ["```"] + body[k + 3:],
        }
        for name, b in mutants.items():
            with self.subTest(name):
                self.assertTrue(finding_problems("mutant", b, True), name)

    def test_a_gallery_finding_card_shows_it_whole(self):
        text = GALLERY.read_text()
        self.assertIn("## 33. A finding, after What", text)
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**97 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("**Finding:**"))
        self.assertEqual(body[k + 2], "```jinja")

    def test_a_findings_set_is_offered_the_page(self):
        page = (SKILL / "SKILL.md").read_text()
        for text in (SKILL_MD.read_text(), RENDERING.read_text(), page):
            self.assertNotIn("until the page can show each finding", text)
            self.assertNotIn("until the page shows findings", text)
        self.assertIn("a set of review or audit findings goes to chat by default, and the page is offered for it too",
                      page.split("\n---\n")[0])
        self.assertIn("so offer the page for such a set as for any other", RENDERING.read_text())
        self.assertIn("**The finding after What, both surfaces**", (REFS / "rulings.md").read_text())


if __name__ == "__main__":
    unittest.main()
