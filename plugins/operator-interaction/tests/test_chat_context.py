"""Every card and block in chat carries a Context section, in the answer page's order.

The decisions skill's cards and blocks follow the page's `context` field: the decision line
(the title, then What), then Context, then the Impact and the options. A card's Context is
one or two sentences at the page's summary size, ending on the resume cue; a block's is a
bullet list at the page's medium size, its first bullet the card's Context. A list line
carries none. Checked against the templates in `references/rendering.md` and every card and
block in `references/gallery.md`.

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
        m = re.match(r"^\*\*([A-Za-z ]+):\*\*", line)
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
                                      or lines[j].startswith("#")):
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
        self.assertEqual(heads(card)[:5], ["What", "Context", "Impact", "Why now", "Why ask"])
        self.assertNotIn("cold reader only", "\n".join(card))

    def test_the_block_template_runs_what_context_bullets_table(self):
        block = fenced(RENDERING.read_text(), "**N — Title as a question?** ⚠ one-way")
        self.assertEqual(heads(block)[:5], ["What", "Context", "table", "Why now", "Why ask"])
        k = next(i for i, x in enumerate(block) if x.startswith("**Context:**"))
        self.assertTrue(block[k + 1].startswith("- the card's Context"), block[k + 1])

    def test_the_lost_context_label_is_gone_from_the_skill(self):
        for f in [SKILL_MD, *sorted(REFS.glob("*.md"))]:
            if f.name == "rulings.md":
                continue  # the record of what was ruled keeps the old shape's words
            self.assertNotIn("Context you may have lost", f.read_text(), f.name)

    def test_older_stored_cards_render_as_before(self):
        text = RENDERING.read_text()
        self.assertIn("**Older stored cards render as before.**", text)
        self.assertIn("renders as it did before Context existed", text)


class GalleryContexts(unittest.TestCase):
    """Every worked card and block carries its Context, in the page's order and size."""

    def test_the_gallery_has_cards_and_blocks(self):
        kinds = [k for _, k, _ in views(GALLERY)]
        self.assertGreaterEqual(kinds.count("card"), 12)
        self.assertGreaterEqual(kinds.count("block"), 2)

    def test_every_card_and_block_runs_what_context_impact(self):
        for n, kind, body in views(GALLERY):
            want = ["What", "Context", "Impact" if kind == "card" else "table"]
            self.assertEqual(heads(body)[:3], want, f"gallery.md:{n} ({kind})")

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

    def test_the_stored_card_keeps_its_context_before_its_impact(self):
        lines = GALLERY.read_text().splitlines()
        k = next(i for i, x in enumerate(lines) if x.startswith("decision 85:"))
        fields = [x.strip().split(":")[0] for x in lines[k + 1:k + 8]]
        self.assertLess(fields.index("why ask"), fields.index("context"))
        self.assertEqual(fields.index("context") + 1, fields.index("impact"))
        ctx = lines[k + 1 + fields.index("context")]
        self.assertIn(" — then: ", ctx)


if __name__ == "__main__":
    unittest.main()
