"""Chat cards and blocks show the Effect across all options, and each option's own impact.

The decisions skill follows the answer page: a card's or block's Impact line gives the
Effect across all the decision's options, favouring none (`(a) …; (b) …` where their outcomes
differ); each option on a card carries its own effect, reach, undo and cost on an italic line
under it, in facet order, a facet that does not apply left out; a block carries the same
facets in its Impact table, under the card's Impact line; a list line carries none of an
option's facets. Checked against the templates in `references/rendering.md`, every card and
block in `references/gallery.md`, and the stored card in the gallery.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest

from test_chat_context import GALLERY, RENDERING, SKILL_MD, fenced, views
from test_impact import LIST_LINE

REFS = RENDERING.parent
WORKSHEET = REFS / "worksheet.md"

OPTION = re.compile(r"^- (\*\*)?\(([a-y])\) ")
DECIDE_LATER = re.compile(r"^- \(z\) ")
FACET_LINE = re.compile(r"^  \*→ (.+)\*$")
LABELS = ("reach", "undo", "cost")
EMPTY = re.compile(r"(?i)^(none|n/a|—|-|nothing|not recorded)?$")


def facets(line):
    """An option's impact line as [(label, text)], the effect labelled 'effect'; None when
    the line is not one."""
    m = FACET_LINE.match(line)
    if not m:
        return None
    parts = m.group(1).split(" · ")
    out = [("effect", parts[0])]
    for p in parts[1:]:
        label, _, text = p.partition(": ")
        out.append((label, text))
    return out


def impact_effect(line):
    """The Effect on an **Impact:** line: the text after the arrow, up to `· later:`."""
    m = re.match(r"^\*\*Impact:\*\* → (.*?) · later: ", line)
    return m and m.group(1)


def check_options(test, where, body):
    """Each option but (z) is followed by its impact line; (z) stays one line. Returns the
    number of options checked."""
    seen = 0
    for k, line in enumerate(body):
        if DECIDE_LATER.match(line):
            test.assertIn(" — *", line, f"{where}: (z) keeps its one line")
            nxt = body[k + 1] if k + 1 < len(body) else ""
            test.assertIsNone(facets(nxt), f"{where}: (z) carries no impact line")
            continue
        m = OPTION.match(line)
        if not m:
            continue
        seen += 1
        test.assertNotIn(" — *", line, f"{where}: ({m.group(2)})'s impact is under it, not after a dash")
        fs = facets(body[k + 1]) if k + 1 < len(body) else None
        test.assertIsNotNone(fs, f"{where}: ({m.group(2)}) has no impact line under it")
        labels = [lab for lab, _ in fs[1:]]
        test.assertTrue(set(labels) <= set(LABELS), f"{where}: ({m.group(2)}) labels {labels}")
        test.assertEqual(labels, [x for x in LABELS if x in labels],
                         f"{where}: ({m.group(2)}) facets out of order")
        test.assertEqual(len(labels), len(set(labels)), f"{where}: ({m.group(2)}) a facet twice")
        for lab, text in fs:
            # a facet that is empty or does not apply is left out; a one-way option's undo
            # stays, and says why ("none, it cannot be recovered"), never a bare "none"
            test.assertIsNone(EMPTY.match(text.strip()),
                              f"{where}: ({m.group(2)}) an empty {lab} facet is left out")
    return seen


class Templates(unittest.TestCase):

    def test_the_card_template_puts_each_options_impact_under_it(self):
        card = fenced(RENDERING.read_text(), "**N — Title as a question?**\n**What:**")
        self.assertGreaterEqual(check_options(self, "rendering.md card", card), 2)
        lines = [facets(x) for x in card if facets(x)]
        # the template shows every facet once, in order
        self.assertEqual([lab for lab, _ in lines[0]], ["effect", "reach", "undo", "cost"])

    def test_the_card_and_block_templates_give_the_effect_across_the_options(self):
        text = RENDERING.read_text()
        for opener in ("**N — Title as a question?**\n**What:**",
                       "**N — Title as a question?** ⚠ one-way"):
            body = fenced(text, opener)
            imp = next(x for x in body if x.startswith("**Impact:**"))
            self.assertRegex(impact_effect(imp), r"^\(a\) .+; \(b\) ", opener[:30])

    def test_the_block_template_has_the_impact_line_above_its_table(self):
        block = fenced(RENDERING.read_text(), "**N — Title as a question?** ⚠ one-way")
        k = next(i for i, x in enumerate(block) if x.startswith("**Impact:**"))
        rest = [x for x in block[k + 1:] if x.strip()]
        self.assertTrue(rest[0].startswith("| Impact | Effect | Reach | Undo | Cost |"))

    def test_effect_is_no_longer_the_recommendations(self):
        for f in (RENDERING, WORKSHEET, SKILL_MD):
            text = f.read_text()
            self.assertNotIn("what changes if the recommendation is taken", text, f.name)
            self.assertNotIn("Effect is the recommended option's", text, f.name)
            self.assertNotIn("what the recommended option does to the world", text, f.name)
        self.assertIn("across all its options, favouring none", RENDERING.read_text())

    def test_older_stored_lines_read_as_written(self):
        text = RENDERING.read_text()
        self.assertIn("**Older stored lines read as written.**", text)
        self.assertIn("renders as stored", text)


class Checks(unittest.TestCase):
    """Each check fails on the form it exists to catch, so a clean run means something."""

    def refused(self, body):
        with self.assertRaises(AssertionError):
            check_options(self, "mutant", body)

    def test_the_old_one_line_form_is_caught(self):
        self.refused(["- **(a) Resume now** — *the snapshot finishes · undo: delete it*",
                      "- (z) Decide later — *it waits*"])

    def test_facets_out_of_order_or_empty_are_caught(self):
        self.refused(["- (a) X", "  *→ it happens · undo: one edit · reach: staging*"])
        self.refused(["- (a) X", "  *→ it happens · cost: none*"])
        self.refused(["- (a) X", "  *→ it happens · undo: none*"])
        self.refused(["- (a) X", "  *→ it happens · stakes: narrow*"])

    def test_a_good_option_passes(self):
        self.assertEqual(check_options(self, "good", [
            "- **(a) X**", "  *→ it happens · reach: staging · undo: one edit · cost: an hour*",
            "- (b) Y", "  *→ nothing happens*",
            "- (z) Decide later — *it waits*"]), 2)

    def test_an_effect_favouring_one_option_is_caught(self):
        self.assertIsNone(re.search(r"\(([a-y])\) .*\(([a-y])\) ",
                                    impact_effect("**Impact:** → the backup finishes · later: x")))


class Gallery(unittest.TestCase):

    def test_every_card_puts_each_options_impact_under_it(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            if kind == "card":
                seen += check_options(self, f"gallery.md:{n}", body)
        self.assertGreaterEqual(seen, 25)

    def test_every_card_and_block_gives_the_effect_across_the_options(self):
        for n, kind, body in views(GALLERY):
            imp = next((x for x in body if x.startswith("**Impact:**")), None)
            self.assertIsNotNone(imp, f"gallery.md:{n}: no Impact line")
            effect = impact_effect(imp)
            self.assertTrue(effect, f"gallery.md:{n}: no effect before later:")
            letters = set(re.findall(r"\(([a-y])\) ", effect))
            self.assertGreaterEqual(len(letters), 2, f"gallery.md:{n}: the effect favours one option")

    def test_every_block_carries_the_facets_in_its_table(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            if kind != "block":
                continue
            seen += 1
            rows = [x for x in body if x.startswith("| ") and not x.startswith(("| Impact", "|---"))]
            self.assertGreaterEqual(len(rows), 3, f"gallery.md:{n}")
            for r in rows:
                self.assertEqual(r.count("|"), 6, f"gallery.md:{n}: {r[:40]}")
            self.assertFalse(any(facets(x) for x in body), f"gallery.md:{n}: the table replaces the lines")
        self.assertGreaterEqual(seen, 2)

    def test_a_one_way_option_keeps_its_undo(self):
        lines = GALLERY.read_text().splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("- **(a) Delete it**"))
        self.assertIn(("undo", "none, it cannot be recovered"), facets(lines[k + 1]))

    def test_no_list_line_carries_an_options_facets(self):
        seen = 0
        for path in (GALLERY, RENDERING):
            lines = path.read_text().splitlines()
            for n, line in enumerate(lines, 1):
                if not LIST_LINE.match(line):
                    continue
                seen += 1
                self.assertNotRegex(line, r"\b(reach|undo|cost): ", f"{path.name}:{n}")
                nxt = lines[n] if n < len(lines) else ""
                self.assertIsNone(facets(nxt), f"{path.name}:{n}")
        self.assertGreater(seen, 20)

    def test_the_stored_card_keeps_each_options_impact(self):
        lines = GALLERY.read_text().splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("decision 85:"))
        stored = []
        for x in lines[k + 1:]:
            if not x.startswith("  "):
                break
            stored.append(x.strip())
        imp = next(x for x in stored if x.startswith("impact: "))
        self.assertRegex(imp, r"^impact: → \(a\) .+; \(b\) .+ · later: ")
        opts = [x for x in stored if re.match(r"^\([a-y]\) ", x)]
        self.assertEqual(len(opts), 2)
        self.assertTrue(all(" — undo: " in x for x in opts))


if __name__ == "__main__":
    unittest.main()
