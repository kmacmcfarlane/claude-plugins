"""Older cards are read by one frozen reference (answer 343 (a)).

`skills/decisions/references/legacy-cards.md` holds the six reader rules, the map from each older
shape to the card record, and the dated reader clauses that left the skills when the record came
in. No file a feature names keeps a clause it moved: a fixed list of their phrases, each searched
for. The list grows with the features that move clauses, each adding its own: the page side
(`cards-schema.md`, the decision-page `SKILL.md`, `index.html`, `writer-digest.md`) first, then
the chat side (`rendering.md`, the decisions `SKILL.md`, `replies.md`, `gallery.md`).

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
DECISIONS = PLUGIN / "skills" / "decisions"
PAGE_SKILL = PLUGIN / "skills" / "decision-page"
LEGACY = DECISIONS / "references" / "legacy-cards.md"

# the files the page side moved its clauses out of
PAGE_FILES = [PAGE_SKILL / "references" / "cards-schema.md", PAGE_SKILL / "SKILL.md",
              PAGE_SKILL / "assets" / "index.html", PAGE_SKILL / "references" / "writer-digest.md"]

# the files the chat side moved its clauses out of
CHAT_FILES = [DECISIONS / "references" / "rendering.md", DECISIONS / "SKILL.md",
              DECISIONS / "references" / "replies.md", DECISIONS / "references" / "gallery.md"]

# each moved clause, by a phrase only it holds: (the phrase, the files it left)
MOVED = [
    ("written before `impact` existed", PAGE_FILES),
    ("written before Context came first", PAGE_FILES),
    ("written before `detail` existed", PAGE_FILES),
    ("written before undo went optional", PAGE_FILES),
    ("written before the level shapes", PAGE_FILES),
    ("written before bundle groups", PAGE_FILES),
    ("written before the reference rule", PAGE_FILES),
    ("stored or revised on or after 2026-10-14", PAGE_FILES),
    ("An older `stakes` field is ignored", PAGE_FILES),
    ("An older level written as one string", PAGE_FILES),
    ("Only the one-time format migration keeps it", PAGE_FILES),
    ("an older page's shows as plain text", PAGE_FILES),
    # the chat side
    ("Older stored lines read as written", CHAT_FILES),
    ("Older stored cards render as before", CHAT_FILES),
    ("renders as it did before Context existed", CHAT_FILES),
    ("keeps the older order", CHAT_FILES),
    ("before Effect covered the options", CHAT_FILES),
    ("from before the cue existed", CHAT_FILES),
    ("A card stored in the older form", CHAT_FILES),
    ("A card stored before undo was shown only", CHAT_FILES),
    ("a line stored before that rule may give the recommended", CHAT_FILES),
]

# the chat-side clauses the legacy reference holds, by the phrase it keeps
CHAT_HELD = ["**Older stored lines read as written**", "**Older stored cards render as before.**",
             "renders as it did before Context existed", "keeps the older order",
             "before Effect covered the options", "from before the cue existed",
             "**A card stored in the older form**", "before undo was shown only where it bites",
             "**A stored unknown**"]

# the map's rows, by their first cell
MAP_ROWS = ["`o[i] = [k, full, impact, title, oneLine]`", "`blocks.k.who`", "`act.k`", "`detail.o.k`", "`warn`",
            "`unknown`", "`impact.effect`, `detail.impact[*].effect`", "`stakes`",
            "option `text`", "option `pros`, `cons` (the one-line texts)", "option `prosT`, `consT` (the table's rows)",
            "`assume {basis, reason, assumptions[], tripwires[]}`", "`background {why, whyask}`",
            "`scope {k, text}`", "`likelihood {basis, text}`", "`dep {n, letters}`"]

RULES = ["**Read it as written.**", "**Never rewrite at render time.**", "**Upgrade only on a touch**",
         "**An answered card is never rewritten.**", "**A newer card is never downgraded.**",
         "**A missing fact is absent, never invented.**"]


def flat(s):
    return re.sub(r"\s+", " ", s)


def legacy_problems(legacy):
    out = []
    rows = {line.split("|")[1].strip() for line in legacy.splitlines() if line.startswith("| ")}
    for r in MAP_ROWS:
        if r not in rows:
            out.append("map row %s missing" % r)
    for r in RULES:
        if r not in legacy:
            out.append("rule %s missing" % r)
    return out


def moved_problems(texts):
    """texts: {path: text}. A moved clause still found in a file it left."""
    out = []
    for phrase, files in MOVED:
        for f in files:
            if phrase in flat(texts[f]):
                out.append("%s keeps %r" % (f.name, phrase))
    return out


class LegacyReference(unittest.TestCase):

    def setUp(self):
        self.legacy = LEGACY.read_text()
        self.texts = {f: f.read_text() for f in PAGE_FILES + CHAT_FILES}

    def test_it_holds_the_map_and_the_six_rules(self):
        self.assertEqual(legacy_problems(self.legacy), [])

    def test_each_era_clause_moved_is_held_here(self):
        for phrase, _ in MOVED[:10]:
            self.assertIn(phrase, flat(self.legacy), phrase)

    def test_each_chat_clause_moved_is_held_here(self):
        for phrase in CHAT_HELD:
            self.assertIn(phrase, flat(self.legacy), phrase)
        # what v5 removed from every view stays removed on a legacy card, a stored effect included
        self.assertIn("a stored `impact:` line's `→ …`) is not shown", flat(self.legacy))

    def test_no_file_keeps_a_moved_clause(self):
        self.assertEqual(moved_problems(self.texts), [])

    def test_each_file_points_here(self):
        for f in (PAGE_SKILL / "references" / "cards-schema.md", PAGE_SKILL / "SKILL.md",
                  DECISIONS / "references" / "rendering.md", DECISIONS / "references" / "replies.md",
                  DECISIONS / "SKILL.md"):
            self.assertIn("`references/legacy-cards.md`", self.texts[f], f.name)

    def test_mutants(self):
        # a clause restored in cards-schema.md
        schema = PAGE_FILES[0]
        texts = dict(self.texts)
        texts[schema] += "\nA `cards.json` written before bundle groups (2026-10-22) has layers of three elements.\n"
        self.assertIn("cards-schema.md keeps 'written before bundle groups'", moved_problems(texts))
        # a chat clause restored in rendering.md, and one in gallery.md
        texts = dict(self.texts)
        texts[CHAT_FILES[0]] += "\n**Older stored lines read as written.** An Impact line stored before Effect covered the options.\n"
        texts[CHAT_FILES[3]] += "\n*a line stored before that rule may give the recommended option's alone*\n"
        problems = moved_problems(texts)
        self.assertIn("rendering.md keeps 'Older stored lines read as written'", problems)
        self.assertIn("gallery.md keeps 'a line stored before that rule may give the recommended'", problems)
        # a map row deleted
        cut = "\n".join(line for line in self.legacy.splitlines() if not line.startswith("| `warn` |"))
        self.assertIn("map row `warn` missing", legacy_problems(cut))
        # a rule deleted
        self.assertTrue(legacy_problems(self.legacy.replace("**A newer card is never downgraded.**", "")))


if __name__ == "__main__":
    unittest.main()
