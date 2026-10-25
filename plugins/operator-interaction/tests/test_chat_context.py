"""Every card and block in chat carries a Context section, in the answer page's order.

The decisions skill's cards and blocks follow the page's `context` field: the decision line
(the title, then What), then Context, then the Impact and the options. A card's Context is
one or two sentences at the page's summary size, ending on the resume cue; a block's is a
bullet list at the page's medium size, its first bullet the card's Context, and a block's
Impact line stands above its table. A list line
carries none. A card's why now and why ask share one **Why you, why now:** line just above
its Rec line (answer 261, 2026-10-20); a block keeps them as two lines under its table. A
bundle whose items need different answers is a group: a heading, then one whole card per
item (answer 263). What is still open about a decision is a folded `▸ Open questions —
<summary>` line after Context and before the Impact (open as `▾` in a block), and the Rec line
says no *unknown* (the v5 layout, 2026-10-22). Checked against the templates in
`references/rendering.md` and every card and block in `references/gallery.md`; a card stored
in an earlier form is read by `references/legacy-cards.md`.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest

from test_impact import CARD_HEAD, DECISIONS, LIST_LINE

REFS = DECISIONS / "references"
RENDERING = REFS / "rendering.md"
GALLERY = REFS / "gallery.md"
SKILL_MD = DECISIONS / "SKILL.md"

CUE = " · "  # where you left it · what you decide now
SENTENCE_END = re.compile(r"[.!?](?=\s+[A-Za-z`])")
# a re-show's title: "**62 — back, as you asked (...):** the question?"
RESHOW_HEAD = re.compile(r"^\*\*\d+ — back[^*]*:\*\* .+\?")
# a group heading (a bundle, A4b) or a finding heading (finding first, when it lands): a view
# stops at either, so neither is read as the tail of the card above it
GROUP_OR_FINDING = re.compile(r"^\*\*(Group|Finding): ")
GROUP_HEAD = re.compile(r"^\*\*Group: [^*]+\*\* — \*(\d+) decisions, [^*]+\*$")
WHY_LINE = "**Why you, why now:**"
REC_LINE = re.compile(r"^(Rec \*\*\(|\*No recommendation)")
LEGACY = REFS / "legacy-cards.md"
# a fold line: closed on a card, open (its items under it) in a block
FOLD = re.compile(r"^([▸▾]) ([A-Z][^—]+) — (.+)$")
OPEN_SUMMARY = re.compile(r"^(\d+) open: \S")


def fenced(text, opener):
    """The lines of the first fenced block whose first line starts with `opener`."""
    blocks = re.findall(r"^```\n(.*?)^```", text, re.S | re.M)
    for b in blocks:
        if b.startswith(opener):
            return b.splitlines()
    raise AssertionError(f"no template opening {opener!r}")


def heads(lines):
    """The bold lead-in of each line that has one ('**What:**' -> 'What'), and the
    table head as 'table'; other lines dropped."""
    out = []
    for line in lines:
        m = re.match(r"^\*\*([A-Za-z ,]+):\*\*", line)
        if m:
            out.append(m.group(1))
        elif line.startswith("| Impact |"):
            out.append("table")
    return out


def views(path):
    """Each card or block in a file: (line number, kind, lines), kind 'block' when it has
    an Impact table. A view runs from its title to the next title, rule or heading; a
    re-show's title counts when the card follows it in full (it has a What line)."""
    lines = path.read_text().splitlines()
    out = []

    def title(x):
        return CARD_HEAD.match(x) or RESHOW_HEAD.match(x)

    for i, line in enumerate(lines):
        if not title(line):
            continue
        j = i + 1
        while j < len(lines) and not (title(lines[j]) or lines[j] == "---"
                                      or lines[j].startswith("#")
                                      or GROUP_OR_FINDING.match(lines[j])):
            j += 1
        body = lines[i:j]
        if RESHOW_HEAD.match(line) and not any(x.startswith("**What:**") for x in body):
            continue  # "...followed by the card": the card itself is shown elsewhere
        kind = "block" if any(x.startswith("| Impact |") for x in body) else "card"
        out.append((i + 1, kind, body))
    return out


def context_of(body):
    """A view's Context: (the text on its Context line, the bullets under it as
    (depth, text))."""
    for k, line in enumerate(body):
        if line.startswith("**Context:**"):
            text = line[len("**Context:**"):].strip()
            bullets = []
            for b in body[k + 1:]:
                m = re.match(r"^( *)- (.*)$", b)
                if not m:
                    break
                bullets.append((len(m.group(1)) // 2, m.group(2)))
            return text, bullets
    return None, []


class Templates(unittest.TestCase):
    """rendering.md's card and block templates run in the page's order."""

    def test_the_card_template_runs_what_context_impact(self):
        card = fenced(RENDERING.read_text(), "**N — Title as a question?**\n**What:**")
        self.assertEqual(heads(card)[:3], ["What", "Context", "Impact"])
        self.assertNotIn("Why now", heads(card))
        self.assertNotIn("Why ask", heads(card))
        self.assertNotIn("cold reader only", "\n".join(card))

    def test_the_card_template_puts_the_why_line_above_the_rec_line(self):
        card = fenced(RENDERING.read_text(), "**N — Title as a question?**\n**What:**")
        check_why_line(self, "rendering.md card", card)

    def test_the_block_template_runs_what_context_bullets_table(self):
        block = fenced(RENDERING.read_text(), "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(heads(block)[:6],
                         ["What", "Context", "Impact", "table", "Why now", "Why ask"])
        k = next(i for i, x in enumerate(block) if x.startswith("**Context:**"))
        self.assertTrue(block[k + 1].startswith("- the card's Context"), block[k + 1])

    def test_the_lost_context_label_is_gone_from_the_skill(self):
        for f in [SKILL_MD, *sorted(REFS.glob("*.md"))]:
            if f.name == "rulings.md":
                continue  # the record of what was ruled keeps the old shape's words
            self.assertNotIn("Context you may have lost", f.read_text(), f.name)

    def test_older_stored_cards_render_as_before(self):
        # the dated clause moved to the legacy reference; rendering.md points there
        text = LEGACY.read_text()
        self.assertIn("**Older stored cards render as before.**", text)
        self.assertIn("renders as it did before Context existed", text)
        self.assertIn("`references/legacy-cards.md`", RENDERING.read_text())

    def test_the_templates_fold_open_questions_above_the_impact(self):
        text = RENDERING.read_text()
        card = fenced(text, "**N — Title as a question?**\n**What:**")
        self.assertEqual(open_question_problems("rendering.md card", card), [])
        self.assertTrue(any(x.startswith("▸ Open questions — ") for x in card))
        block = fenced(text, "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(open_question_problems("rendering.md block", block, block=True), [])
        self.assertTrue(any(x.startswith("▾ Open questions — ") for x in block))
        flat = " ".join(text.split())
        self.assertIn("## Folds", text)
        self.assertIn("`▾ <name> — <summary>`", flat)
        self.assertIn("`N open: <the first, cut at about 12 words>`", flat)


def open_question_problems(where, body, block=False):
    """A view's ▸ Open questions line: after Context and before the Impact, its summary
    `N open: …`, closed on a card and open in a block with N bullets under it; and no Rec line
    that says *unknown*. Returns the problems, empty when clean."""
    out = []
    for k, line in enumerate(body):
        if REC_LINE.match(line) and "unknown" in line:
            out.append(f"{where}: the Rec line says unknown")
        m = FOLD.match(line)
        if not m:
            continue
        if m.group(2) != "Open questions":
            continue
        ctx = next((i for i, x in enumerate(body) if x.startswith("**Context:**")), None)
        imp = next((i for i, x in enumerate(body) if x.startswith("**Impact:**")), None)
        if ctx is None or imp is None or not ctx < k < imp:
            out.append(f"{where}: the Open questions line is not between Context and Impact")
        s = OPEN_SUMMARY.match(m.group(3))
        if not s:
            out.append(f"{where}: the Open questions summary is not 'N open: …'")
        if m.group(1) != ("▾" if block else "▸"):
            out.append(f"{where}: the fold is {'closed in a block' if block else 'open on a card'}")
        if block and s:
            items = 0
            for x in body[k + 1:]:
                if not x.startswith("- "):
                    break
                items += 1
            if items != int(s.group(1)):
                out.append(f"{where}: the open fold lists {items}, its summary says {s.group(1)}")
    return out


def empty_fold_problems(where, body):
    """A fold with nothing in it is left out, line and all: no fold line whose summary says
    none or a count of zero, and no open fold with no bullet under it."""
    out = []
    for k, line in enumerate(body):
        m = FOLD.match(line)
        if not m:
            continue
        if re.match(r"(?i)^(0 open\b|none\b|nothing\b|—|-)", m.group(3).strip()):
            out.append(f"{where}: an empty {m.group(2)} fold is shown")
        if m.group(1) == "▾" and not (k + 1 < len(body) and body[k + 1].startswith("- ")):
            out.append(f"{where}: an open {m.group(2)} fold with nothing under it")
    return out


def check_why_line(test, where, body):
    """A card's one **Why you, why now:** line: after its options (and any To act on, If left
    or If unanswered part), the line just above its Rec line, about 25 words at most; no
    separate Why now or Why ask line."""
    hs = heads(body)
    test.assertNotIn("Why now", hs, f"{where}: a separate Why now line")
    test.assertNotIn("Why ask", hs, f"{where}: a separate Why ask line")
    test.assertEqual(hs.count("Why you, why now"), 1, f"{where}: one why line")
    k = next(i for i, x in enumerate(body) if x.startswith(WHY_LINE))
    z = max(i for i, x in enumerate(body) if x.startswith("- (z) "))
    test.assertLess(z, k, f"{where}: the why line is above the options")
    test.assertTrue(k + 1 < len(body) and REC_LINE.match(body[k + 1]),
                    f"{where}: the why line is not just above the Rec line")
    words = body[k][len(WHY_LINE):].split()
    test.assertLessEqual(len(words), 30, f"{where}: the why line runs {len(words)} words")


def groups(path):
    """Each group heading in a file: (line number, the N it claims, the card titles after
    it up to the next rule, heading or group)."""
    lines = path.read_text().splitlines()
    out = []
    for i, line in enumerate(lines):
        m = GROUP_HEAD.match(line)
        if not m:
            continue
        cards = []
        for x in lines[i + 1:]:
            if x == "---" or x.startswith("#") or GROUP_OR_FINDING.match(x):
                break
            if CARD_HEAD.match(x):
                cards.append(x)
        out.append((i + 1, int(m.group(1)), cards, lines[i + 1] if i + 1 < len(lines) else ""))
    return out


def check_group(test, where, n, cards, after, bodies):
    """A group heading counts its cards, carries its shared context on the next line, and
    each card under it is whole: its own number and its own Rec line."""
    test.assertTrue(after.startswith("**Shared context:**"), f"{where}: no shared context")
    test.assertEqual(len(cards), n, f"{where}: the heading counts {n}, {len(cards)} follow")
    nums = [re.match(r"^\*\*(\d+) — ", c).group(1) for c in cards]
    test.assertEqual(len(set(nums)), len(nums), f"{where}: a number shared")
    for body in bodies:
        test.assertEqual(sum(1 for x in body if REC_LINE.match(x)), 1,
                         f"{where}: {body[0][:30]} has no Rec line of its own")


class GalleryContexts(unittest.TestCase):
    """Every worked card and block carries its Context, in the page's order and size."""

    def test_the_gallery_has_cards_and_blocks(self):
        kinds = [k for _, k, _ in views(GALLERY)]
        self.assertGreaterEqual(kinds.count("card"), 12)
        self.assertGreaterEqual(kinds.count("block"), 2)

    def test_every_card_and_block_runs_what_context_impact(self):
        for n, kind, body in views(GALLERY):
            want = ["What", "Context", "Impact"] + (["table"] if kind == "block" else [])
            self.assertEqual(heads(body)[:len(want)], want, f"gallery.md:{n} ({kind})")

    def test_a_cards_context_is_one_or_two_sentences_ending_on_the_cue(self):
        for n, kind, body in views(GALLERY):
            if kind != "card":
                continue
            text, bullets = context_of(body)
            self.assertTrue(text, f"gallery.md:{n}: an empty Context line")
            self.assertEqual(bullets, [], f"gallery.md:{n}: a card's Context is a line")
            self.assertLessEqual(len(SENTENCE_END.findall(text)) + 1, 2, f"gallery.md:{n}")
            self.assertLessEqual(len(text.split()), 60, f"gallery.md:{n}")
            # the cue folds in as Context's last clause, after the terms
            last = SENTENCE_END.split(text)[-1]
            self.assertIn(CUE, last, f"gallery.md:{n}: the cue is not Context's last part")
            self.assertTrue(SENTENCE_END.search(text), f"gallery.md:{n}: no terms before the cue")

    def test_the_origin_clause_stays_true_after_a_showing(self):
        # Context is stored and re-shown: "new to you" is false from the second showing
        for n, kind, body in views(GALLERY):
            text, bullets = context_of(body)
            whole = " ".join([text] + [b for _, b in bullets])
            self.assertNotRegex(whole, r"(?i)new to you", f"gallery.md:{n}")
        stored = [x for x in GALLERY.read_text().splitlines() if x.lstrip().startswith("context:")]
        self.assertTrue(stored)
        for x in stored:
            self.assertNotRegex(x, r"(?i)new to you")

    def test_a_blocks_context_is_bullets_its_first_the_cards(self):
        for n, kind, body in views(GALLERY):
            if kind != "block":
                continue
            text, bullets = context_of(body)
            self.assertEqual(text, "", f"gallery.md:{n}: a block's Context is bullets")
            self.assertGreaterEqual(len(bullets), 2, f"gallery.md:{n}")
            self.assertEqual(bullets[0][0], 0, f"gallery.md:{n}")
            self.assertIn(CUE, bullets[0][1], f"gallery.md:{n}: the first bullet lacks the cue")
            # medium: a sub-bullet or two at most under any bullet
            run = 0
            for depth, _ in bullets:
                run = run + 1 if depth == 1 else 0
                self.assertLessEqual(run, 2, f"gallery.md:{n}")
                self.assertLessEqual(depth, 1, f"gallery.md:{n}")

    def test_a_list_line_carries_no_context(self):
        for path in (GALLERY, RENDERING):
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if LIST_LINE.match(line):
                    self.assertNotIn("Context", line, f"{path.name}:{n}")

    def test_every_card_has_one_why_line_above_its_rec_line(self):
        seen = 0
        for n, kind, body in views(GALLERY):
            if kind == "card":
                seen += 1
                check_why_line(self, f"gallery.md:{n}", body)
        self.assertGreaterEqual(seen, 15)

    def test_a_block_keeps_why_now_and_why_ask_under_its_table(self):
        for n, kind, body in views(GALLERY):
            if kind == "block":
                hs = heads(body)
                self.assertNotIn("Why you, why now", hs, f"gallery.md:{n}")
                self.assertLess(hs.index("table"), hs.index("Why now"), f"gallery.md:{n}")
                self.assertEqual(hs.index("Why now") + 1, hs.index("Why ask"), f"gallery.md:{n}")

    def test_open_questions_fold_above_the_impact_and_no_rec_line_says_unknown(self):
        folds = 0
        for n, kind, body in views(GALLERY):
            self.assertEqual(open_question_problems(f"gallery.md:{n}", body, kind == "block"), [])
            folds += sum(1 for x in body if FOLD.match(x))
        self.assertGreaterEqual(folds, 6)

    def test_an_empty_fold_is_left_out(self):
        flat = " ".join(RENDERING.read_text().split())
        self.assertIn("**Empty.** A fold with nothing in it is left out, line and all", flat)
        for n, kind, body in views(GALLERY):
            self.assertEqual(empty_fold_problems(f"gallery.md:{n}", body), [])
        # mutants: a fold shown with nothing open, closed and open
        card = ["**41 — X?**", "**Context:** y · z", "▸ Open questions — 0 open", "**Impact:** later: w"]
        self.assertTrue(empty_fold_problems("mutant", card))
        card[2] = "▸ Open questions — none"
        self.assertTrue(empty_fold_problems("mutant", card))
        card[2] = "▾ Open questions — 1 open: x"
        self.assertTrue(empty_fold_problems("mutant", card))
        card[2:3] = ["▸ Open questions — 1 open: x"]
        self.assertEqual(empty_fold_problems("good", card), [])

    def test_the_stored_card_keeps_its_context_before_its_impact(self):
        lines = GALLERY.read_text().splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("decision 85:"))
        fields = [x.strip().split(":")[0] for x in lines[k + 1:k + 8]]
        self.assertLess(fields.index("why ask"), fields.index("context"))
        self.assertEqual(fields.index("context") + 1, fields.index("impact"))
        ctx = lines[k + 1 + fields.index("context")]
        self.assertIn(" — then: ", ctx)


class Groups(unittest.TestCase):
    """A bundle whose items need different answers is a group of whole item cards."""

    def test_the_gallery_has_a_group_of_whole_cards(self):
        gs = groups(GALLERY)
        self.assertGreaterEqual(len(gs), 1)
        bodies = {b[0]: b for _, kind, b in views(GALLERY)}
        for n, count, cards, after in gs:
            check_group(self, f"gallery.md:{n}", count, cards, after,
                        [bodies[c] for c in cards])

    def test_a_view_stops_at_a_group_or_finding_heading(self):
        for n, kind, body in views(GALLERY):
            for x in body[1:]:
                self.assertIsNone(GROUP_OR_FINDING.match(x), f"gallery.md:{n}")

    def test_the_rendering_names_the_group_heading(self):
        text = RENDERING.read_text()
        self.assertIn("## A bundle as a group", text)
        self.assertIn("**Group: <plain name>** — *<N> decisions, <what they share>*", text)
        self.assertIn("**Shared context:**", text)


class Checks(unittest.TestCase):
    """Each check fails on the form it exists to catch, so a clean run means something."""

    CARD = ["**41 — Resume the backup?**", "**What:** x", "**Context:** y · z", "**Impact:** → a",
            "- **(a) Resume**", "  *→ it finishes*", "- (z) Decide later — *it waits*", "",
            "**Why you, why now:** the lease lapses at five.", "Rec **(a)** · basis **strong**"]

    def test_a_good_why_line_passes(self):
        check_why_line(self, "good", list(self.CARD))

    def test_the_old_two_lines_on_a_card_are_caught(self):
        card = list(self.CARD)
        card[8:9] = ["**Why now:** the lease lapses.", "**Why ask:** it is yours."]
        with self.assertRaises(AssertionError):
            check_why_line(self, "mutant", card)

    def test_a_why_line_above_the_options_or_too_long_is_caught(self):
        card = list(self.CARD)
        card.insert(4, card.pop(8))
        with self.assertRaises(AssertionError):
            check_why_line(self, "mutant", card)
        card = list(self.CARD)
        card[8] = "**Why you, why now:** " + "word " * 31
        with self.assertRaises(AssertionError):
            check_why_line(self, "mutant", card)

    def test_an_open_questions_line_out_of_place_or_an_unknown_is_caught(self):
        card = ["**41 — Resume the backup?**", "**What:** x", "**Context:** y · z",
                "▸ Open questions — 1 open: whether the lease can be extended",
                "**Impact:** later: w · reach: r", "- **(a) Resume**", "  *→ it finishes*",
                "Rec **(a)** · basis **strong** — *quota checked*"]
        self.assertEqual(open_question_problems("good", card), [])
        # the line under the Impact
        under = list(card)
        under.insert(4, under.pop(3))
        self.assertTrue(open_question_problems("mutant", under))
        # the Rec line's unknown restored
        rec = list(card)
        rec[-1] += " · unknown: none"
        self.assertIn("mutant: the Rec line says unknown", open_question_problems("mutant", rec))
        # a summary that is not a count
        bad = list(card)
        bad[3] = "▸ Open questions — whether the lease can be extended"
        self.assertTrue(open_question_problems("mutant", bad))
        # a block's fold left closed, or counting what it does not list
        block = card[:3] + ["▾ Open questions — 2 open: a", "- a", ""] + card[4:]
        self.assertTrue(open_question_problems("mutant", block, block=True))
        self.assertTrue(open_question_problems("mutant", card, block=True))

    def test_a_group_that_miscounts_or_shares_a_rec_line_is_caught(self):
        a = ["**51 — A?**", "Rec **(a)**"]
        b = ["**52 — B?**", "Rec **(a)**"]
        check_group(self, "good", 2, [a[0], b[0]], "**Shared context:** x", [a, b])
        with self.assertRaises(AssertionError):
            check_group(self, "mutant", 3, [a[0], b[0]], "**Shared context:** x", [a, b])
        with self.assertRaises(AssertionError):
            check_group(self, "mutant", 2, [a[0], b[0]], "**Shared context:** x", [a, b[:1]])
        with self.assertRaises(AssertionError):
            check_group(self, "mutant", 2, [a[0], b[0]], "", [a, b])


if __name__ == "__main__":
    unittest.main()
