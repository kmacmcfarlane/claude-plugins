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

from test_impact import NODE, PAGE, CARD_HEAD, example, page_free_script, finding_end, FENCE_OPEN
from test_context import runner, RUNNER, SKILL
from test_record import run_record, record_of
from test_items import mutant_runner
from test_chat_context import fenced, views, heads, GALLERY, RENDERING, SKILL_MD, REFS


DESCRIPTION_MAX = 1024


def description(skill_md):
    """A SKILL.md's frontmatter description, its quotes off."""
    m = re.search(r'^description: "(.*)"$', skill_md, re.M)
    assert m, "no description"
    return m.group(1)


def src_shown(head, src_rest):
    """Whether a Finding head ends on its excerpt's src (the part after the location)."""
    m = FINDING_HEAD.match(head)
    return bool(m and m.group("src") and src_rest in m.group("src"))


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

    def test_the_heads_short_name_is_plain_text(self):
        # drawn with esc, as the title's label is: no code mark, no slug
        d = example()
        c43(d)["label"] = c43(d)["finding"]["label"] = {"id": "D3", "name": "`blue` off [[41]]"}
        h = one(d)["cards"]["43"]["fnd"]
        self.assertIn("(`blue` off [[41]])", h)
        h = one(d, mutant_page("+'</span> ('+esc(f.label.name)+')'",
                               "+'</span> ('+fmt(f.label.name)+')'"))["cards"]["43"]["fnd"]
        self.assertNotIn("(`blue` off [[41]])", h)

    def test_check_refuses_a_malformed_finding(self):
        cases = {
            "finding must be {label, title, where, mechanism, excerpt}": lambda c: c.__setitem__("finding", "x"),
            "finding needs its mechanism": lambda c: c["finding"].pop("mechanism"),
            "finding mechanism must be one paragraph": lambda c: c["finding"].__setitem__("mechanism", "a\nb"),
            "finding title must be one line of text": lambda c: c["finding"].__setitem__("title", "a\nb"),
            "finding where must be one line of text": lambda c: c["finding"].__setitem__("where", 3),
            "finding label must be {id, name}": lambda c: c["finding"].__setitem__("label", "D3"),
            "finding label D4 (site colour off the logo) must be the card's own label, D3 (site colour off the logo)":
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

    def test_an_excerpt_holds_only_text_lang_and_src(self):
        # an excerpt with another key is refused, so the reference scan's excerpt (isExcerpt) and the
        # check's are the same object, and an excerpt's text is never scanned as text
        d = example()
        c43(d)["finding"]["excerpt"] = {"text": "see [[99]]", "lang": "toml", "src": "theme/colors.toml", "note": "x"}
        bad = one(d)["bad"]
        self.assertTrue(any("finding excerpt: an excerpt holds only text, lang and src: note" in b for b in bad), bad)
        old = '{const k=Object.keys(x).find(k=>!["text","lang","src"].includes(k));if(k!=null)return'
        bad = one(d, mutant_page(old, '{const k=null;if(k!=null)return'))["bad"]
        self.assertFalse(any("holds only text, lang and src" in b for b in bad), bad)
        # the three keys alone: the text is not scanned, and passes
        del c43(d)["finding"]["excerpt"]["note"]
        self.assertEqual(one(d)["bad"], [])

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

    def test_a_long_short_name_on_the_finding_alone_is_linted(self):
        d = example()
        del c43(d)["label"]
        c43(d)["finding"]["label"]["name"] = "the site colour does not match the logo"
        out = runner(d)[1]
        self.assertIn("lint: card 43: shape: the label D3's short name is 8 words", out)
        js = mutant_runner("const l = c.label || (c.finding && c.finding.label);", "const l = c.label;")
        self.assertNotIn("short name is 8 words", runner(d, script=js)[1])

    def test_the_tag_set_is_the_pages_and_the_schema_lists_it(self):
        for ch in ("\u0000", "\u000d", "\u00ad", "\u202e", "\U000e0001", "\U000e0100", "\ufffa", "\u034f",
                   "\u3164", "\u17b5", "\u180b"):
            self.assertTrue(RAW_CTRL.match(ch), repr(ch))
        for ch in ("\t", "\n", "a", "\u00e9"):
            self.assertIsNone(RAW_CTRL.match(ch), repr(ch))
        schema = " ".join((SKILL / "references" / "cards-schema.md").read_text().split())
        for part in ("U+0000–U+0008 and U+000B–U+001F", "U+007F–U+009F", "U+00AD", "U+061C", "U+180E",
                     "U+200B–U+200F", "U+2028–U+202E", "U+2060–U+2069", "U+FEFF", "U+E0000–U+E007F",
                     "U+E0100–U+E01EF", "U+FFF9–U+FFFB", "U+034F", "U+115F, U+1160, U+3164 and U+FFA0",
                     "U+17B4 and U+17B5", "U+180B–U+180F"):
            self.assertIn(part, schema)
        self.assertIn("each character the page tags (the `decision-page` skill's `references/cards-schema.md` "
                      "§ An excerpt), in the excerpt and its `src`, as its `U+` tag",
                      " ".join(RENDERING.read_text().split()))

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
# **Finding:** label (short name)[: title] — `where`[ <the rest of src> | · from `src`], or a head with no label
CODE = r"(?:`[^`]+`|``+ .+? ``+)"  # a code span, a longer delimiter with spaces inside when it holds a backtick
FINDING_HEAD = re.compile(r"^\*\*Finding:\*\* (?:(?P<id>\S+) \((?P<name>[^)]+)\)(?:: (?P<t1>(?:(?! — | · from )[^`])+))?|(?P<t2>(?:(?! — | · from )[^`])+))"
                          r"(?: — (?P<where>" + CODE + r"))?(?P<src> " + CODE + r"| · from " + CODE + r")?$")
# a control or bidirectional character an excerpt writes as its U+ tag in chat (the page's own class, in short)
def xc_ctrl():
    """The page's own XC_CTRL class (index.html), as a Python pattern: the characters it tags."""
    m = re.search(r"const XC_CTRL=/(\[.*?\])/gu;", PAGE.read_text())
    assert m, "no XC_CTRL in the template"
    return re.compile(re.sub(r"\\u\{([0-9A-Fa-f]+)\}", lambda x: "\\U%08X" % int(x.group(1), 16), m.group(1)))


RAW_CTRL = xc_ctrl()
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
    if not mech.strip() or mech.startswith(("```", "~~~", "**", "▸", "▾", "- ")):
        out.append(where + ": no mechanism line under the Finding's head")
    elif len(mech.split()) <= 4:
        out.append(where + ": the mechanism is a bare label")
    if k + 2 < len(body) and FENCE_OPEN.match(body[k + 2]):
        out += fence_problems(where, body[k + 2:finding_end(body, k)], finding_end(body, k) > len(body))
    return out


def fence_problems(where, block, unclosed=False):
    """An excerpt's fenced block against the chat rules: a language on the opener; a fence no line
    of the text can close (longer than any backtick run in it, or tildes over a text with none at
    a line's start); every control or bidirectional character written as its U+ tag."""
    out = []
    m = re.match(r"^(`{3,}|~{3,})([A-Za-z0-9][A-Za-z0-9+#._-]*)$", block[0])
    if not m:
        return [where + ": the excerpt's fence has no language"]
    fence, text = m.group(1), block[1:-1]
    if unclosed or block[-1].strip() != fence:
        out.append(where + ": the excerpt's fence is not closed by its own fence")
    if fence[0] == "`":
        run = max([len(r) for x in text for r in re.findall(r"`+", x)] or [0])
        if run >= len(fence):
            out.append(where + ": a run of %d backticks in the excerpt, inside a fence of %d" % (run, len(fence)))
    elif any("~" in x for x in text):
        out.append(where + ": a tilde in the excerpt, inside a ~~~ fence")
    for x in text:
        c = RAW_CTRL.search(x)
        if c:
            out.append(where + ": a raw U+%04X in the excerpt: write it as its tag" % ord(c.group(0)))
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
            "a location not in code": body[:k] + [body[k].replace("`templates/welcome.html:14-16` `at 3f2a9c1`",
                                                                  "templates/welcome.html:14-16")] + body[k + 1:],
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
        # its head ends on the excerpt's src, the rest after the location (M1)
        m = FINDING_HEAD.match(body[k])
        self.assertEqual(m.group("src"), " `at 3f2a9c1`")
        self.assertTrue(src_shown(body[k], "3f2a9c1"))
        # mutant: the head without its src
        m = FINDING_HEAD.match(body[k].replace(" `at 3f2a9c1`", ""))
        self.assertIsNotNone(m)
        self.assertIsNone(m.group("src"))

    def test_the_head_forms(self):
        ok = ["**Finding:** F3 (raw name): its title — `a/b.py:3`",
              "**Finding:** F3 (raw name): its title — `a/b.py:3` `at 3f2a9c1`",
              "**Finding:** F3 (raw name): its title — `a/b.py:3` · from `c/d.py:1-9 at 3f2a9c1`",
              "**Finding:** its title · from `c/d.py:1-9`",
              "**Finding:** F3 (raw name): its title — `` a`b.py:3 `` · from `` run `make` at 10:02 ``"]
        for h in ok:
            with self.subTest(h):
                self.assertIsNotNone(FINDING_HEAD.match(h))
        self.assertIsNone(FINDING_HEAD.match("**Finding:** F3 (raw name): its title — a/b.py:3"))
        self.assertEqual(FINDING_HEAD.match(ok[3]).group("where"), None)

    def test_the_rendering_shows_the_src_and_a_fence_safe_excerpt(self):
        text = " ".join(RENDERING.read_text().split())
        self.assertIn("then the excerpt's `src` when it is given", text)
        self.assertIn("longer than the longest run of backticks in it", text)
        self.assertIn("as its `U+` tag (`U+200B`, `U+202E`); tabs and line breaks stay as they are", text)
        self.assertIn("when it is the location exactly, nothing more", text)
        self.assertIn("With no location, the head ends on its title, then ` · from ` and the `src`", text)
        self.assertIn("takes a longer code-span delimiter", text)
        self.assertIn("its one Finding may cover the set", text)

    def test_the_gallery_fences_are_safe_and_the_checks_fail_on_unsafe_ones(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**52 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("**Finding:**"))
        block = body[k + 2:finding_end(body, k)]
        self.assertEqual(block[0], "````go")  # its text holds a run of three backticks
        self.assertEqual(fence_problems("52", block), [])
        mutants = {
            "a three-backtick fence": ["```go"] + block[1:-1] + ["```"],
            "a raw right-to-left override": block[:2] + ["\u202e" + block[2]] + block[3:],
            "a raw zero-width space": block[:2] + [block[2] + "\u200b"] + block[3:],
            "a tilde line in a tilde fence": ["~~~go", "~~~", "x", "~~~"],
            "a tilde in a tilde fence": ["~~~go", "x := ~y", "~~~"],
            "no language": ["````"] + block[1:],
        }
        for name, b in mutants.items():
            with self.subTest(name):
                self.assertTrue(fence_problems("mutant", b), name)
        # a tilde fence over backticks is safe
        self.assertEqual(fence_problems("ok", ["~~~go"] + block[1:-1] + ["~~~"]), [])

    def test_a_findings_set_is_offered_the_page(self):
        page = (SKILL / "SKILL.md").read_text()
        rationale = (REFS / "rationale.md").read_text()
        for text in (SKILL_MD.read_text(), RENDERING.read_text(), page, rationale):
            self.assertNotIn("until the page can show each finding", text)
            self.assertNotIn("until the page shows findings", text)
            self.assertNotIn("findings-style sets go there until the page can", text)
        self.assertIn("The page\n  now shows each finding, after What (F7, answer 337 (a))", rationale)
        # each skill's description within the 1024-character limit
        for path in (page, SKILL_MD.read_text()):
            self.assertLessEqual(len(description(path)), DESCRIPTION_MAX)
        self.assertIn("a set of review or audit findings goes to chat by default, and the page is offered for it too",
                      page.split("\n---\n")[0])
        self.assertIn("so offer the page for such a set as for any other", RENDERING.read_text())
        self.assertIn("**The finding after What, both surfaces**", (REFS / "rulings.md").read_text())


if __name__ == "__main__":
    unittest.main()
