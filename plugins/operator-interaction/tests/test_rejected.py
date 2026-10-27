"""Rejected alternatives (F2; answer 286 (b) and the operator's prototype feedback 2), on both surfaces.

Four parts:

- the decision page (`decision-page` skill, under node): `rejectedFold` renders the record's
  `rejected`, `[{t, why}]`, as the last of the bottom folds, closed, its summary the count and
  the titles (`N: title · title`, a slug as its number); open, each title on a bold line and its
  reasons as bullets, every text escaped. `check()` refuses a malformed list, which also runs in
  the runner's `--record` mode;
- the pre-publish runner (`scripts/check_cards.js`, under node): the id lint and the cold read
  read each title and reason, and they count in the card in all;
- the upgrader (`scripts/upgrade_cards.js`, under node): the kit's `[{bold, bullets}]` maps to
  `[{t, why}]`, and any other shape is refused, all or nothing;
- the chat card (the `decisions` skill): the `▸ Rejected alternatives — N: <titles>` line, the
  last fold, after ▸ Background, closed on a card and open in a block, each title on a bold line
  over its reason bullets, in the templates and every gallery card that carries one.

Each check is proved by a mutation: a broken template, runner, upgrader or text fails it.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import sys
import unittest

from test_impact import NODE, example
from test_context import runner, RECORD
from test_record import run_record, record_of
from test_items import mutant_runner
from test_upgrade import upgrade, load, KIT, UPGRADER
from test_chat_context import fenced, views, GALLERY, RENDERING, SKILL_MD, REFS, FOLD
from test_finding import one, mutant_page, HOSTILE


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the Rejected alternatives page, runner and upgrader tests "
              "(RejectedPage, RejectedRunner, RejectedUpgrade) are skipped, so its render, its check, its lints "
              "and its upgrade went untested", file=sys.stderr)


def card(d, n):
    return next(c for c in d["cards"] if c["n"] == n)


def rej(res, n):
    """Card n's Rejected alternatives fold as rendered: "" when there is none."""
    m = re.search(r'<details class="pane"><summary>Rejected alternatives.*?</ul></div></details>',
                  res["cards"][str(n)]["card"])
    return m.group(0) if m else ""


def cards_of(d):
    return d["cards"] if isinstance(d, dict) else d


def panes(html):
    return re.findall(r'<details class="pane"(?: open)?><summary>(Background|Dependencies|Rejected alternatives)', html)


EXAMPLE_41 = ('<details class="pane"><summary>Rejected alternatives <span class="fsum">1: Build on a shared office '
              'machine</span></summary><div><ul class="rej"><li><p class="rt">Build on a shared office machine</p><ul>'
              '<li>it is still one machine whose cache can go stale</li><li>publishing would wait on whoever looks '
              'after that machine</li></ul></li></ul></div></details>')


@unittest.skipUnless(NODE, "node is not installed")
class RejectedPage(unittest.TestCase):

    def test_the_example_shows_card_41s_fold(self):
        res = one(example())
        self.assertEqual(res["bad"], [])
        self.assertEqual(rej(res, 41), EXAMPLE_41)
        self.assertEqual(rej(res, 42), "")
        self.assertEqual(rej(res, 43), "")
        # mutant: the fold left out of the card
        res = one(example(), mutant_page("    +rejectedFold(c)\n", ""))
        self.assertEqual(rej(res, 41), "")

    def test_it_is_the_last_bottom_fold_and_closed(self):
        def problems(script=None):
            d = example()
            card(d, 42)["rejected"] = [{"t": "Keep both addresses", "why": ["two copies of every page to keep"]}]
            out = []
            for n in (41, 42):
                h = one(d, script)["cards"][str(n)]["card"]
                ps = panes(h)
                if not ps or ps[-1] != "Rejected alternatives":
                    out.append("%d: not the last fold: %s" % (n, ps))
                if '<details class="pane" open><summary>Rejected' in h:
                    out.append("%d: open" % n)
                if "Rejected alternatives" in h and h.index('class="follow"') > h.index("<summary>Rejected alternatives"):
                    out.append("%d: above the answer" % n)
            return out
        self.assertEqual(problems(), [])
        # card 42 has Dependencies too: Background, Dependencies, then Rejected alternatives
        d = example()
        card(d, 42)["rejected"] = [{"t": "Keep both addresses", "why": ["two copies of every page to keep"]}]
        self.assertEqual(panes(one(d)["cards"]["42"]["card"]), ["Background", "Dependencies", "Rejected alternatives"])
        # mutants: before Background; open
        moved = mutant_page("    +rejectedFold(c)\n", "").replace(
            "+'<div class=\"panes\">'", "+'<div class=\"panes\">'+rejectedFold(c)", 1)
        self.assertTrue(problems(moved))
        self.assertTrue(problems(mutant_page(
            "return '<details class=\"pane\"><summary>Rejected alternatives'",
            "return '<details class=\"pane\" open><summary>Rejected alternatives'")))

    def test_the_summary_counts_and_names_each_title(self):
        d = example()
        card(d, 41)["rejected"] = [{"t": "Build on a shared office machine", "why": ["x"]},
                                   {"t": "Publish from [[42]]'s `docs-old` branch", "why": ["y"]}]
        h = rej(one(d), 41)
        self.assertIn('<span class="fsum">2: Build on a shared office machine · Publish from 42\'s '
                      '<code>docs-old</code> branch</span></summary>', h.replace("&#39;", "'"))
        self.assertNotIn("<button", h[:h.index("</summary>")])
        # in the open fold the slug is a mark, as in every text field
        self.assertIn("slug", h[h.index("</summary>"):])
        # mutant: the count dropped from the summary
        h = rej(one(d, mutant_page("'+rs.length+': '+rs.map", "'+rs.map")), 41)
        self.assertNotIn(">2: ", h)

    def test_none_is_not_shown(self):
        for v in ([], [{"t": "none", "why": ["x"]}], [{"t": " n/a ", "why": ["x"]}]):
            d = example()
            card(d, 41)["rejected"] = v
            res = one(d)
            self.assertEqual(res["bad"], [], v)
            self.assertNotIn("Rejected alternatives", res["cards"]["41"]["card"], v)
        # a none reason is left out; one none alternative among others is left out and not counted
        d = example()
        card(d, 41)["rejected"] = [{"t": "none", "why": ["x"]}, {"t": "Keep it", "why": ["none", "it stays slow"]}]
        h = rej(one(d), 41)
        self.assertIn('<span class="fsum">1: Keep it</span>', h)
        self.assertIn("<ul><li>it stays slow</li></ul>", h)
        # mutant: the none test gone from the titles
        h = rej(one(d, mutant_page("c.rejected.filter(r=>isObj(r)&&isTxt(r.t)&&shown(r.t))",
                                   "c.rejected.filter(r=>isObj(r)&&isTxt(r.t))")), 41)
        self.assertIn(">2: ", h)

    def test_every_text_is_escaped(self):
        def problems(script=None):
            out = []
            for v in HOSTILE:
                for where in ("t", "why"):
                    d = example()
                    r = card(d, 41)["rejected"][0]
                    if where == "t":
                        r["t"] = v
                    else:
                        r["why"] = [v]
                    h = rej(one(d, script), 41)
                    if not h:
                        out.append("%s %r: no fold" % (where, v))
                    elif "<script" in h or "<img" in h:
                        out.append("%s %r renders raw" % (where, v))
            return out
        self.assertEqual(problems(), [])
        # mutants: the title in the fold, the summary's titles and a reason drawn raw
        self.assertTrue(problems(mutant_page("'<li><p class=\"rt\">'+fmt(r.t)+'</p>'", "'<li><p class=\"rt\">'+r.t+'</p>'")))
        self.assertTrue(problems(mutant_page('rs.map(r=>code(esc(r.t.trim()', 'rs.map(r=>code((r.t.trim()')))
        self.assertTrue(problems(mutant_page("ws.map(x=>'<li>'+fmtD(x)+'</li>')", "ws.map(x=>'<li>'+x+'</li>')")))

    CASES = {
        "rejected must be a list of {t, why}": [
            lambda c: c.__setitem__("rejected", "a shared office machine"),
            lambda c: c.__setitem__("rejected", {"t": "x", "why": ["y"]}),
        ],
        "rejected 1 needs its title t": [
            lambda c: c["rejected"].__setitem__(0, "a shared office machine"),
            lambda c: c["rejected"][0].pop("t"),
            lambda c: c["rejected"][0].__setitem__("t", "  "),
            lambda c: c["rejected"][0].__setitem__("t", 3),
        ],
        "rejected 1 t must be one line of text": [
            lambda c: c["rejected"][0].__setitem__("t", "a\nb"),
            lambda c: c["rejected"][0].__setitem__("t", "a\u2028b"),
        ],
        "rejected 1 why must be a list of one or more reasons": [
            lambda c: c["rejected"][0].pop("why"),
            lambda c: c["rejected"][0].__setitem__("why", []),
            lambda c: c["rejected"][0].__setitem__("why", "it goes stale"),
        ],
        "rejected 1 why reason 2 is not text": [
            lambda c: c["rejected"][0]["why"].__setitem__(1, 3),
            lambda c: c["rejected"][0]["why"].__setitem__(1, " "),
        ],
        "rejected 1 why reason 1 has a line break": [
            lambda c: c["rejected"][0]["why"].__setitem__(0, "a\nb"),
        ],
    }

    def test_check_refuses_a_malformed_list(self):
        for needle, puts in self.CASES.items():
            for i, put in enumerate(puts):
                with self.subTest(needle=needle, i=i):
                    d = example()
                    put(card(d, 41))
                    bad = one(d)["bad"]
                    self.assertTrue(any(b.startswith("card 41: ") and needle in b for b in bad), bad)
        # mutants: each test gone
        d = example()
        card(d, 41)["rejected"] = {"t": "x", "why": ["y"]}
        # with the list test gone the check stops on the object instead of refusing it
        js = mutant_page("if(!Array.isArray(c.rejected))bad.push(", "if(false)bad.push(")
        with self.assertRaisesRegex(AssertionError, "node failed"):
            one(d, js)
        # L4: the title test and the reason-text test each gone
        d = example()
        card(d, 41)["rejected"][0].pop("t")
        self.assertEqual(one(d, mutant_page("if(!isObj(r)||!isTxt(r.t)){bad.push(", "if(false){bad.push("))["bad"], [])
        d = example()
        card(d, 41)["rejected"][0]["why"][1] = 3
        self.assertEqual(one(d, mutant_page('if(j>=0)bad.push(x+" why reason "', 'if(false)bad.push(x+" why reason "'))["bad"], [])
        d = example()
        card(d, 41)["rejected"][0]["t"] = "a\nb"
        self.assertEqual(one(d, mutant_page("if(LINE_BREAK.test(r.t))bad.push(", "if(false)bad.push("))["bad"], [])
        d = example()
        card(d, 41)["rejected"][0]["why"] = []
        self.assertEqual(one(d, mutant_page("if(!Array.isArray(r.why)||!r.why.length)bad.push(",
                                            "if(!Array.isArray(r.why))bad.push("))["bad"], [])
        d = example()
        card(d, 41)["rejected"][0]["why"] = ["a\nb"]
        self.assertEqual(one(d, mutant_page("else if(k>=0)bad.push(", "else if(false)bad.push("))["bad"], [])


@unittest.skipUnless(NODE, "node is not installed")
class RejectedRunner(unittest.TestCase):

    def test_the_example_is_clean_and_so_is_its_record(self):
        self.assertEqual(runner(example())[:2], (0, ""))
        self.assertEqual(run_record(record_of(card(example(), 41))), (0, ""))

    def test_a_record_with_a_malformed_list_is_refused(self):
        rec = record_of(card(example(), 41))
        rec["rejected"][0]["why"] = []
        code, out = run_record(rec)
        self.assertEqual(code, 1, out)
        self.assertIn("record 41: rejected 1 why must be a list of one or more reasons", out)

    def test_the_id_lint_reads_titles_and_reasons(self):
        for where in ("t", "why"):
            d = example()
            r = card(d, 41)["rejected"][0]
            if where == "t":
                r["t"] = "Build on the OQ3 machine"
            else:
                r["why"] = ["the OQ3 machine is shared"]
            self.assertIn("lint: card 41: OQ3 looks like an id (rejected)", runner(d)[1], where)
            js = mutant_runner('  put("rejected", rejectedTexts(c));\n', "")
            self.assertNotIn("OQ3 looks like an id", runner(d, script=js)[1], where)

    def test_the_cold_read_reads_titles_and_reasons(self):
        # the titles, which the fold's summary shows, are read; the reasons sit in the closed fold and are not
        d = example()
        card(d, 41)["rejected"][0]["t"] = "Build on the seven office machines"
        self.assertIn('lint: card 41: "seven" (rejected alternatives) counts things its context does not name',
                      runner(d)[1])
        js = mutant_runner('  terms(page.rejectedOf(c).map(r => r.t), " (rejected alternatives)");\n', "")
        self.assertNotIn("(rejected alternatives)", runner(d, script=js)[1])
        # a carried-over card's fold is read the same: the cold read is no lint a new card owes
        d["cards"][0]["upgraded"] = {"from": "kit", "rev": d["cards"][0]["rev"]}
        self.assertIn('"seven" (rejected alternatives)', runner(d)[1])
        # a count in a reason is not read; mutant: the reasons read again
        d = example()
        card(d, 41)["rejected"][0]["why"] = ["the seven office machines all share one cache"]
        self.assertNotIn("(rejected alternatives)", runner(d)[1])
        js = mutant_runner('terms(page.rejectedOf(c).map(r => r.t), " (rejected', 'terms(rejectedTexts(c), " (rejected')
        self.assertIn('"seven" (rejected alternatives)', runner(d, script=js)[1])

    def test_they_count_in_the_card_in_all(self):
        d = example()
        card(d, 41)["rejected"][0]["why"] = [" ".join(["word"] * 1400)]
        self.assertIn("lint: card 41: depth: the card is", runner(d)[1])
        js = mutant_runner("+ words(rejectedTexts(c)) ", "")
        self.assertNotIn("depth: the card is", runner(d, script=js)[1])


@unittest.skipUnless(NODE, "node is not installed")
class RejectedUpgrade(unittest.TestCase):

    def test_the_kit_shape_maps_and_any_other_is_refused(self):
        code, out, d = upgrade(load(KIT))[:3]
        self.assertEqual(code, 0, out)
        c51 = next(c for c in cards_of(d) if c["n"] == 51)
        self.assertEqual(c51["rejected"], [{"t": "A second local disk", "why": ["It burns with the first."]}])
        bads = [{"bold": "x"}, {"bold": "x", "bullets": []}, {"bold": "x", "bullets": ["a\nb"]},
                {"bold": " ", "bullets": ["a"]}, {"t": "x", "why": ["a"]}, "x"]
        for r in bads + [None]:
            with self.subTest(r=r):
                kit = load(KIT)
                k51 = next(c for c in cards_of(kit) if c["n"] == 51)
                k51["rejected"] = {"bold": "x", "bullets": ["a"]} if r is None else [r]
                code, out, d = upgrade(kit)[:3]
                self.assertEqual(code, 1, out)
                self.assertIn("card 51: rejected is not a list of {bold, bullets}", out)
                self.assertIsNone(d)
        # a null rejected is no list: left out, never refused; mutant: any rejected key read as a list
        kit = load(KIT)
        next(c for c in cards_of(kit) if c["n"] == 51)["rejected"] = None
        code, out, d = upgrade(kit)[:3]
        self.assertEqual(code, 0, out)
        self.assertNotIn("rejected", next(c for c in cards_of(d) if c["n"] == 51))
        import pathlib as _p
        import tempfile as _t
        with _t.TemporaryDirectory() as tmp:
            js = _p.Path(tmp) / "upgrade_cards.js"
            src = UPGRADER.read_text()
            self.assertEqual(src.count("  if (c.rejected != null) {"), 1)
            js.write_text(src.replace("  if (c.rejected != null) {", '  if ("rejected" in c) {'))
            self.assertEqual(upgrade(kit, script=js)[0], 1)
        # mutant: the refusal gone, a malformed list passes the upgrader
        import pathlib
        import tempfile
        src = UPGRADER.read_text()
        old = "if (!Array.isArray(c.rejected) || !c.rejected.every(ok)) bad.push("
        self.assertEqual(src.count(old), 1)
        with tempfile.TemporaryDirectory() as tmp:
            js = pathlib.Path(tmp) / "upgrade_cards.js"
            js.write_text(src.replace(old, "if (false) bad.push("))
            kit = load(KIT)
            next(c for c in cards_of(kit) if c["n"] == 51)["rejected"] = [{"bold": "x", "bullets": []}]
            code, out = upgrade(kit, script=js)[:2]
            self.assertNotIn("rejected is not a list", out)


# the gallery's cards with a Rejected alternatives line
REJECTED_CARDS = {43, 81, 99}
REJ_NAME = "Rejected alternatives"
SUMMARY = re.compile(r"^(\d+): (\S.*)$")
BOLD_TITLE = re.compile(r"^\*\*([^*].*)\*\*$")


def fold_problems(where, body, block=False):
    """A view's Rejected alternatives fold against the rules: one at most; after ▸ Background and
    the last fold line; its summary `N: title · title`, N the titles' count; closed on a card, open
    in a block, where each title stands on a bold line, in the summary's order, each with one or
    more reason bullets under it, and nothing else."""
    at = [i for i, x in enumerate(body) if (m := FOLD.match(x)) and m.group(2) == REJ_NAME]
    if not at:
        return []
    out = []
    if len(at) > 1:
        out.append(where + ": more than one Rejected alternatives line")
    k = at[0]
    m = FOLD.match(body[k])
    if m.group(1) != ("▾" if block else "▸"):
        out.append(where + ": the fold is " + ("closed in a block" if block else "open on a card"))
    bg = [i for i, x in enumerate(body) if (f := FOLD.match(x)) and f.group(2) == "Background"]
    if bg and bg[0] > k:
        out.append(where + ": the Rejected alternatives line is above Background")
    if any(FOLD.match(x) for x in body[k + 1:]):
        out.append(where + ": a fold line after Rejected alternatives: it is the last")
    if any(re.match(r"^- \(?[a-z]\)", x) or re.match(r"^- \*\*\([a-z]\)", x) for x in body[k + 1:]):
        out.append(where + ": an option after Rejected alternatives")
    s = SUMMARY.match(m.group(3).replace(" *(only where one was)*", ""))
    if not s:
        return out + [where + ": the summary is not 'N: title · title'"]
    titles = s.group(2).split(" · ")
    if int(s.group(1)) != len(titles):
        out.append(where + ": the summary counts %s and names %d" % (s.group(1), len(titles)))
    if block:
        j, seen = k + 1, []
        while j < len(body):
            if seen:
                # a title after the first stands after a blank line, or CommonMark reads it into the bullet above
                b = j
                while j < len(body) and not body[j].strip():
                    j += 1
                if not (j < len(body) and BOLD_TITLE.match(body[j])):
                    break
                if j == b:
                    out.append(where + ": no blank line before %s" % body[j])
            t = BOLD_TITLE.match(body[j])
            if not t:
                break
            seen.append(t.group(1))
            j += 1
            n = 0
            while j < len(body) and body[j].startswith("- "):
                n += 1
                j += 1
            if not n:
                out.append(where + ": %s has no reason under it" % t.group(1))
        if seen != titles:
            out.append(where + ": the open fold's titles %s are not the summary's %s" % (seen, titles))
    return out


class RejectedChat(unittest.TestCase):

    def test_the_templates_end_on_the_fold(self):
        text = RENDERING.read_text()
        card_t = fenced(text, "**N — Title as a question?**\n- the TLDR")
        self.assertTrue(card_t[-1].startswith("▸ Rejected alternatives — 1: "), card_t[-1])
        self.assertEqual(fold_problems("rendering.md card", card_t), [])
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertTrue(any(x.startswith("▾ Rejected alternatives — ") for x in block))
        self.assertEqual(fold_problems("rendering.md block", block, block=True), [])
        fold = fenced(text, "▾ Rejected alternatives — ")
        self.assertEqual(fold_problems("rendering.md fold", fold, block=True), [])
        flat = " ".join(text.split())
        self.assertIn("**▸ Rejected alternatives** — the alternatives weighed and not offered", flat)
        self.assertIn("`tell me rejected` (or `tell me rejected alternatives`)", flat)
        self.assertIn("A rejected alternative is never an option", flat)

    def test_every_gallery_fold_is_well_formed_and_last(self):
        seen = set()
        for n, kind, body in views(GALLERY):
            if any((m := FOLD.match(x)) and m.group(2) == REJ_NAME for x in body):
                seen.add(int(re.match(r"^\*\*(\d+)", body[0]).group(1)))
            self.assertEqual(fold_problems(f"gallery.md:{n}", body, kind == "block"), [])
        self.assertEqual(seen, REJECTED_CARDS)
        # the tell me answer in § 36 opens 99's fold, the same titles as the card's line
        text = GALLERY.read_text()
        sec = text[text.index("## 36. Rejected alternatives, folded last"):]
        lines = sec.splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("▾ Rejected alternatives — "))
        self.assertEqual(fold_problems("gallery.md § 36", lines[k:k + 8], block=True), [])
        # mutant: the blank line before the second title dropped
        cut = lines[k:k + 3] + lines[k + 4:k + 8]
        self.assertIn("gallery.md § 36: no blank line before **Ask customers to pay again later**",
                      fold_problems("gallery.md § 36", cut, block=True))
        self.assertIn("*Read as: 99 → tell me (rejected alternatives).*", sec)
        self.assertIn("▸ Rejected alternatives — 2: Take payment on delivery · Ask customers to pay again later", text)

    def test_the_fold_checks_fail_on_broken_cards(self):
        n, kind, body = next(v for v in views(GALLERY) if v[2][0].startswith("**99 — "))
        k = next(i for i, x in enumerate(body) if x.startswith("▸ Rejected alternatives — "))
        bg = next(i for i, x in enumerate(body) if x.startswith("▸ Background — "))
        mutants = {
            "above Background": body[:bg] + [body[k]] + body[bg:k] + body[k + 1:],
            "a fold after it": body[:k + 1] + ["▸ Attached — 1: a status page"] + body[k + 1:],
            "a miscount": body[:k] + [body[k].replace("— 2: ", "— 3: ")] + body[k + 1:],
            "no summary": body[:k] + ["▸ Rejected alternatives — Take payment on delivery"] + body[k + 1:],
            "open on a card": body[:k] + ["▾" + body[k][1:]] + body[k + 1:],
            "twice": body[:k + 1] + [body[k]] + body[k + 1:],
        }
        for name, b in mutants.items():
            with self.subTest(name):
                self.assertTrue(fold_problems("mutant", b), name)
        n, kind, block = next(v for v in views(GALLERY) if v[2][0].startswith("**43 — "))
        self.assertEqual(kind, "block")
        k = next(i for i, x in enumerate(block) if x.startswith("▾ Rejected alternatives — "))
        bmut = {
            "closed in a block": block[:k] + ["▸" + block[k][1:]] + block[k + 1:],
            "no reason": block[:k + 2] + block[k + 3:],
            "a title not bold": block[:k + 1] + [block[k + 1].strip("*")] + block[k + 2:],
            "another title": block[:k + 1] + ["**Something else**"] + block[k + 2:],
        }
        for name, b in bmut.items():
            with self.subTest(name):
                self.assertTrue(fold_problems("mutant", b, block=True), name)

    def test_the_skills_the_record_the_worksheet_and_the_ruling_say_it(self):
        skill = " ".join(SKILL_MD.read_text().split())
        self.assertIn("the ▸ Rejected alternatives fold line (their count and titles)", skill)
        self.assertIn("then any Rejected alternatives fold open, each title in bold over its reasons as bullets", skill)
        page_skill = " ".join((REFS.parent.parent / "decision-page" / "SKILL.md").read_text().split())
        self.assertIn("set `rejected`, `[{t, why}]`: shown in the **Rejected alternatives** fold", page_skill)
        record = RECORD.read_text()
        self.assertRegex(record, r"\n\| `rejected` \| list of `\{t, why\}` \| optional \| \*\*Rejected alternatives\*\*")
        # no longer among the fields an upgraded card may carry unshown
        upgraded = record.split("## Fields an upgraded card may already carry")[1].split("\n## ")[0]
        self.assertIn("every part of the kit now has its row above", " ".join(upgraded.split()))
        self.assertNotIn("have no row above yet", " ".join(upgraded.split()))
        self.assertIn("| Rejected alternatives | each alternative you weighed", (REFS / "worksheet.md").read_text())
        self.assertIn("- **Rejected alternatives in a fold, both surfaces** (2026-10-21, answer 286 (b)",
                      (REFS / "rulings.md").read_text())
        self.assertIn("`rejected [{t: bold, why: bullets}]`, shown as the Rejected alternatives fold",
                      (REFS / "legacy-cards.md").read_text())


if __name__ == "__main__":
    unittest.main()
