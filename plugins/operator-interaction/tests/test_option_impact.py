"""Chat cards and blocks show no card-level Effect, and each option's own impact.

The decisions skill follows the answer page: a card's or block's Impact line carries no effect
(the operator's v5 ruling, 2026-10-22): it starts at `later:` (Wait), then Reach, Undo and
Cost; each option on a card carries its own effect, reach, undo and cost on an italic line
under it, in facet order, a facet that does not apply left out; a block carries the same
facets in its Impact table, under the card's Impact line; a list line carries none of an
option's facets. Since answer 260 (2026-10-20), undo is shown only on an option that is
one-way or costly to undo, marked `⚠ undo:`: on its line, in its block's Undo cell (`—` on a
reversible row), and on the Impact line, which carries it only then. No program can tell a
one-way option written without its marker; what is checked is that every undo shown is
marked, and the cold read checks the rest. Checked against the templates in `references/rendering.md`, every card and
block in `references/gallery.md`, and the stored card in the gallery (the store's own line
form, which keeps an `impact: →` effect until the store keeps card records).

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest

from test_chat_context import GALLERY, RENDERING, SKILL_MD, fenced, views
from test_impact import LIST_LINE

REFS = RENDERING.parent
WORKSHEET = REFS / "worksheet.md"
LEGACY = REFS / "legacy-cards.md"

OPTION = re.compile(r"^- (\*\*)?\(([a-y])\) ")
DECIDE_LATER = re.compile(r"^- \(z\) ")
FACET_LINE = re.compile(r"^  \*→ (.+)\*$")
LABELS = ("reach", "⚠ undo", "cost")
# an undo on the Impact line without its marker
BARE_UNDO = re.compile(r"(?<!⚠ )\bundo: ")
EMPTY = re.compile(r"(?i)^(none|n/a|—|-|nothing|not recorded)?$")


def impact_rows(body):
    """A block's Impact table rows (its header and rule dropped): the table under the `| Impact |`
    head, up to its first line that is not a row. A block's other tables (each option's Pros | Cons,
    F5) are not its Impact table."""
    out, inside = [], False
    for line in body:
        if line.startswith("| Impact |"):
            inside = True
            continue
        if inside:
            if not line.startswith("|"):
                break
            if not line.startswith("|---"):
                out.append(line)
    return out


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


def impact_line_problems(where, line):
    """An **Impact:** line that carries a card-level effect: it opens on anything but `later:`,
    or holds an arrow. Returns the problems, empty when clean."""
    out = []
    if not line.startswith("**Impact:** later: "):
        out.append(f"{where}: the Impact line does not open on later:")
    if "→" in line:
        out.append(f"{where}: the Impact line carries an effect (→)")
    return out


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


def check_undo_marked(test, where, body):
    """Every undo a card or block shows is marked: `⚠ undo:` on the Impact line and an
    option's line, and a block's Undo cell either `—` (reversible) or opening on ⚠. Returns
    the number of marked undos seen."""
    marked = 0
    rows = impact_rows(body)
    for line in body:
        if line.startswith("**Impact:**"):
            test.assertIsNone(BARE_UNDO.search(line), f"{where}: an unmarked undo on the Impact line")
            marked += line.count("⚠ undo: ")
        fs = facets(line)
        if fs:
            test.assertNotIn("undo", [lab for lab, _ in fs], f"{where}: an unmarked undo on an option")
            marked += sum(1 for lab, _ in fs if lab == "⚠ undo")
        if line in rows:
            cell = line.split("|")[4].strip()
            test.assertTrue(cell == "—" or cell.startswith("⚠ "),
                            f"{where}: Undo cell {cell[:30]!r} is neither — nor marked")
            marked += cell.startswith("⚠ ")
    return marked


class Templates(unittest.TestCase):

    def test_the_card_template_puts_each_options_impact_under_it(self):
        card = fenced(RENDERING.read_text(), "**N — Title as a question?**\n**Context:**")
        self.assertGreaterEqual(check_options(self, "rendering.md card", card), 2)
        lines = [facets(x) for x in card if facets(x)]
        # the template shows every facet once, in order, the undo marked
        self.assertEqual([lab for lab, _ in lines[0]], ["effect", "reach", "⚠ undo", "cost"])
        # and a reversible option with none
        self.assertNotIn("⚠ undo", [lab for lab, _ in lines[1]])

    def test_the_card_and_block_templates_carry_no_card_level_effect(self):
        text = RENDERING.read_text()
        for opener in ("**N — Title as a question?**\n**Context:**",
                       "**N — Title as a question?** ⚠ one-way"):
            body = fenced(text, opener)
            imp = next(x for x in body if x.startswith("**Impact:**"))
            self.assertEqual(impact_line_problems(opener[:30], imp), [])
        # the Impact line's own template, cost optional at its end
        self.assertIn("later: <wait> · reach: <reach> · ⚠ undo: <the one-way or costly option's undo> · cost: <cost>",
                      text)

    def test_the_block_template_has_the_impact_line_above_its_table(self):
        block = fenced(RENDERING.read_text(), "**N — Title as a question?** ⚠ one-way")
        k = next(i for i, x in enumerate(block) if x.startswith("**Impact:**"))
        rest = [x for x in block[k + 1:] if x.strip()]
        self.assertTrue(rest[0].startswith("| Impact | Effect | Reach | Undo | Cost |"))

    def test_effect_is_an_options_never_the_decisions(self):
        for f in (RENDERING, WORKSHEET, SKILL_MD):
            text = " ".join(f.read_text().split())
            self.assertNotIn("what changes if the recommendation is taken", text, f.name)
            self.assertNotIn("Effect is the recommended option's", text, f.name)
            self.assertNotIn("what the recommended option does to the world", text, f.name)
            # the Effect across the options went with the v5 ruling
            self.assertNotIn("across all its options, favouring none", text, f.name)
            self.assertNotIn("Effect across all the options", text, f.name)
        self.assertIn("**No card-level effect.**", RENDERING.read_text())
        self.assertIn("each option's own effect, never the decision's", WORKSHEET.read_text())
        self.assertIn("each option's own **Effect**", " ".join(SKILL_MD.read_text().split()))

    def test_older_stored_lines_read_as_written(self):
        # the dated clause moved to the legacy reference: all but the effect, which no view shows
        text = LEGACY.read_text()
        self.assertIn("**Older stored lines read as written**, all but the effect.", text)
        self.assertIn("renders as stored", text)
        self.assertIn("`references/legacy-cards.md`", RENDERING.read_text())


class Checks(unittest.TestCase):
    """Each check fails on the form it exists to catch, so a clean run means something."""

    def refused(self, body):
        with self.assertRaises(AssertionError):
            check_options(self, "mutant", body)

    def test_the_old_one_line_form_is_caught(self):
        self.refused(["- **(a) Resume now** — *the snapshot finishes · undo: delete it*",
                      "- (z) Decide later — *it waits*"])

    def test_facets_out_of_order_or_empty_are_caught(self):
        self.refused(["- (a) X", "  *→ it happens · ⚠ undo: none, gone · reach: staging*"])
        self.refused(["- (a) X", "  *→ it happens · cost: none*"])
        self.refused(["- (a) X", "  *→ it happens · ⚠ undo: none*"])
        self.refused(["- (a) X", "  *→ it happens · stakes: narrow*"])

    def test_an_unmarked_undo_is_caught(self):
        # the form answer 260 retired: an undo on a reversible option, with no marker
        self.refused(["- (a) X", "  *→ it happens · undo: one edit*"])

    def test_a_good_option_passes(self):
        self.assertEqual(check_options(self, "good", [
            "- **(a) X**", "  *→ it happens · reach: staging · ⚠ undo: none, gone · cost: an hour*",
            "- (b) Y", "  *→ nothing happens*",
            "- (z) Decide later — *it waits*"]), 2)

    def test_a_card_level_effect_is_caught(self):
        self.assertEqual(impact_line_problems("good", "**Impact:** later: x · reach: y"), [])
        # an Impact line with its → restored, across the options or as one sentence
        for bad in ("**Impact:** → (a) the backup finishes; (b) no backup · later: x · reach: y",
                    "**Impact:** → sets which units the dashboard shows · later: x",
                    "**Impact:** later: x · reach: y → (a) z"):
            self.assertTrue(impact_line_problems("mutant", bad), bad)

    def test_an_unmarked_undo_anywhere_is_caught(self):
        good = ["**43 — Remove the old endpoint?**",
                "**Impact:** later: w · reach: r · ⚠ undo: (a) a hotfix, after the outage",
                "- (a) Remove it", "  *→ partners break · ⚠ undo: a hotfix, after the outage*",
                "- **(b) Keep it**", "  *→ nothing breaks*",
                "| Impact | Effect | Reach | Undo | Cost |", "|---|---|---|---|---|",
                "| (a) Remove it | x | r | ⚠ a hotfix, after the outage | an hour |",
                "| **(b) Keep it** | y | — | — | an hour |",
                # an option's Pros | Cons table under the Impact table (F5) is not one of its rows
                "", "**(a) Remove it**", "*plan in brief:* the route goes on Thursday.", "",
                "| Pros | Cons |", "|---|---|", "| the old code goes | partners break |"]
        self.assertEqual(check_undo_marked(self, "good", good), 3)
        self.assertEqual(impact_rows(good), good[8:10])
        for k, bad in ((1, good[1].replace("⚠ undo", "undo")),
                       (5, "  *→ nothing breaks · undo: drop the header*"),
                       (9, "| **(b) Keep it** | y | — | drop the header | an hour |")):
            card = list(good)
            card[k] = bad
            with self.assertRaises(AssertionError):
                check_undo_marked(self, "mutant", card)


class Gallery(unittest.TestCase):

    def test_every_card_puts_each_options_impact_under_it(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            if kind == "card":
                seen += check_options(self, f"gallery.md:{n}", body)
        self.assertGreaterEqual(seen, 25)

    def test_no_card_or_block_impact_line_carries_an_effect(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            imp = next((x for x in body if x.startswith("**Impact:**")), None)
            self.assertIsNotNone(imp, f"gallery.md:{n}: no Impact line")
            self.assertEqual(impact_line_problems(f"gallery.md:{n}", imp), [])
            seen += 1
        self.assertGreaterEqual(seen, 20)

    def test_every_undo_shown_is_marked(self):
        # undo only where it bites (answer 260): every undo the gallery shows is marked, and
        # some are, on cards and on blocks
        seen = {"card": 0, "block": 0}
        for n, kind, body in views(GALLERY):
            seen[kind] += check_undo_marked(self, f"gallery.md:{n}", body)
        self.assertGreaterEqual(seen["card"], 6)
        self.assertGreaterEqual(seen["block"], 2)
        flat = " ".join(RENDERING.read_text().split())
        self.assertIn("An option with no undo shown is reversible at little cost", flat)
        self.assertIn("The marker marks the option only", flat)
        self.assertNotIn("on a ⚠ decision every option's line carries its undo", flat)

    def test_every_block_with_a_one_way_row_marks_it(self):
        for n, kind, body in views(GALLERY):
            if kind == "block":
                cells = [x.split("|")[4].strip() for x in impact_rows(body)]
                self.assertTrue(any(c.startswith("⚠ ") for c in cells), f"gallery.md:{n}")
                self.assertIn("—", cells, f"gallery.md:{n}: a reversible row reads —")

    def test_every_block_carries_the_facets_in_its_table(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            if kind != "block":
                continue
            seen += 1
            rows = impact_rows(body)
            self.assertGreaterEqual(len(rows), 3, f"gallery.md:{n}")
            for r in rows:
                self.assertEqual(r.count("|"), 6, f"gallery.md:{n}: {r[:40]}")
            self.assertFalse(any(facets(x) for x in body), f"gallery.md:{n}: the table replaces the lines")
        self.assertGreaterEqual(seen, 2)

    def test_a_one_way_option_keeps_its_undo(self):
        lines = GALLERY.read_text().splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("- **(a) Delete it**"))
        self.assertIn(("⚠ undo", "none, it cannot be recovered"), facets(lines[k + 1]))

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
        # an undo is stored only where it bites, and marked; 85's options are both reversible
        self.assertFalse(any(" — undo: " in x for x in opts))
        self.assertIsNone(BARE_UNDO.search(imp))


# Impact names the system (answer 259), the mechanism (268), and label echoes (269)
REPLIES = REFS / "replies.md"
PROCESS = re.compile(r"(?i)\b(review|comment|round|your attention)\b")
ECHO = re.compile(r"Read as: (.*?)→")
SOURCE_LABEL = re.compile(r"\b[A-Z]{1,3}[0-9]+[a-z]?\b")
NAMED_ECHO = re.compile(r"^\d+ — [A-Z]{1,3}[0-9]+[a-z]? \([a-z][^)]*\) $")


def check_system_rules(test, where, rendering, worksheet):
    """The rules are stated: Impact names the system, and says the mechanism, in the
    rendering reference and the worksheet."""
    flat_r, flat_w = " ".join(rendering.split()), " ".join(worksheet.split())
    test.assertIn("**Impact names the system, not the process.**", flat_r, where)
    test.assertIn("**Say the mechanism, not the label.**", flat_r, where)
    test.assertIn("goes here and nowhere else", flat_w, where)
    test.assertIn("said by its mechanism", flat_w, where)
    test.assertIn("Can you say how it happens", flat_w, where)


def system_slots(body):
    """A card's or block's Effect and Reach text: the Impact line's reach, each option's
    effect and reach, a block row's Effect and Reach cells."""
    out = []
    rows = impact_rows(body)
    for line in body:
        if line.startswith("**Impact:**"):
            m = re.search(r" · reach: (.*?)( · ⚠ undo: | · cost: |$)", line)
            out.append(m.group(1) if m else "")
        fs = facets(line)
        if fs:
            out += [text for lab, text in fs if lab in ("effect", "reach")]
        if line in rows and not line.startswith("| (z)"):
            cells = line.split("|")
            out += [cells[2], cells[3]]
    return out


def check_no_process(test, where, body):
    """Outside a round ask, no Effect or Reach names the process."""
    if any(x.startswith("**If left:**") for x in body):
        return
    for text in system_slots(body):
        m = PROCESS.search(text)
        test.assertIsNone(m, f"{where}: {m and m.group(0)!r} in Effect or Reach: {text[:50]}")


def check_label_echoes(test, where, text):
    """Every echo that names a source label carries the number, the label and its short
    name: *Read as: 52 — F7 (retry storm) → …*. Returns the number checked."""
    seen = 0
    for m in ECHO.finditer(" ".join(text.split())):
        head = m.group(1)
        if SOURCE_LABEL.search(head):
            seen += 1
            test.assertRegex(head, NAMED_ECHO, f"{where}: echo {head!r}")
    return seen


class SystemMechanismLabels(unittest.TestCase):

    def test_the_rules_are_stated(self):
        check_system_rules(self, "skill", RENDERING.read_text(), WORKSHEET.read_text())

    def test_no_effect_or_reach_names_the_process(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            seen += 1
            check_no_process(self, f"gallery.md:{n}", body)
        self.assertGreaterEqual(seen, 20)

    def test_every_label_echo_carries_number_label_and_name(self):
        seen = sum(check_label_echoes(self, f.name, f.read_text())
                   for f in (GALLERY, REPLIES, RENDERING))
        self.assertGreaterEqual(seen, 3)

    def test_the_checks_catch_what_they_are_for(self):
        r, w = RENDERING.read_text(), WORKSHEET.read_text()
        for cut in ("**Impact names the system, not the process.**",
                    "**Say the mechanism, not the label.**"):
            with self.assertRaises(AssertionError):
                check_system_rules(self, "mutant", r.replace(cut, ""), w)
        for cut in ("goes here and nowhere else", "said by its mechanism"):
            with self.assertRaises(AssertionError):
                check_system_rules(self, "mutant", r, " ".join(w.split()).replace(cut, ""))
        card = ["**41 — X?**", "**Impact:** later: w · reach: the comment to the developer"]
        with self.assertRaises(AssertionError):
            check_no_process(self, "mutant", card)
        with self.assertRaises(AssertionError):
            check_no_process(self, "mutant", ["**41 — X?**", "- (a) X", "  *→ it ships · reach: the design review*"])
        check_no_process(self, "round ask", card + ["**If left:** *one finding*"])
        # the Impact line's reach ends at its cost: a process word in the cost is not read as reach
        check_no_process(self, "cost", ["**41 — X?**", "**Impact:** later: w · reach: the upload service · cost: one review round"])
        for bad in ("*Read as: F7 → (b).*", "*Read as: 52 — F7 → (b).*",
                    "*Read as: F7 (retry storm) → (b).*"):
            with self.assertRaises(AssertionError):
                check_label_echoes(self, "mutant", bad)
        self.assertEqual(check_label_echoes(self, "good", "*Read as: 52 — F7 (retry storm) → (b).*"), 1)


if __name__ == "__main__":
    unittest.main()
