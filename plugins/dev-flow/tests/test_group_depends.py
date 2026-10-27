"""The librarian writes the group and depends lines, and the writer-run line (03ab F1).

Answers 303 (c), 305 (a), 306 (a), 308 (b) and 309 (2026-10-22): which group each decision is
in, and which decision it waits on, are column-0 store lines; a group is an entity keyed by a
`g-<MMDD>-<hhh>` id (a short time plus a hash, no counter), so a rename never orphans its
members, and a bundle's shared context is stored once on its entity line. Only the store's
writer session writes them, at raise, reframe, rename and regroup; back-fill is lazy, per item,
at the next showing, revision or raise, and only in this session's own store. An answer page's
writers each record a `writer-run:` line, to tune the split's card cap; they are split from the
stored group and depends lines, and the records they return are stored with `$WI raise` before
the page is merged from them (03ab F4). The grammar is the
work-items format's (checked in that plugin's own suite); this file pins the librarian's rules
in `references/decisions.md` and the counter sentence in `references/report.md`. Each check
runs on the real file and on a mutant copy, which it must catch.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REFS = PLUGIN / "skills" / "librarian-mode" / "references"
DECISIONS = REFS / "decisions.md"
REPORT = REFS / "report.md"


def flat(text):
    return " ".join(text.split())


def bullet(text, opener):
    """The flattened top-level bullet that opens with `opener`, or '' when it is gone."""
    lines = text.splitlines()
    start = next((i for i, x in enumerate(lines) if x.startswith("- " + opener)), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith("- ") or lines[i].startswith("#")), len(lines))
    return flat("\n".join(lines[start:end]))


def row(text, opener):
    return next((x for x in text.splitlines() if x.startswith("| " + opener)), "")


GROUPED = [
    "a group's entity line `group g-<MMDD>-<hhh>: <plain name>`",
    "` · shares: <what its members share> · context: <shared context>`, written once there",
    "a member line `group N: g-<MMDD>-<hhh>` per decision",
    "whose targets on the same M are alternatives",
    "the `work-items` skill's format reference, § Groups and dependencies",
    "Group ids are not numbers and take nothing from the counter",
    "Only this session, the store's writer, writes them; a dispatched agent (planner, "
    "reviewer) never does",
    "never through `raise --lines`",
    "**At raise:** right after `$WI raise` prints N, in the same turn",
    "draw an id, check it is not taken, then write the entity line, then the member line",
    "**At a reframe** (N reframed as M): `group M: <N's id>`",
    "each open K whose set names N gets a new `depends K:` line, its whole set again with N "
    "replaced by M (the last line is the whole set)",
    "one `$WI note <id> --raw -- '<line>' ['<line>' …]` per item (one lock, so one commit in a "
    "store that commits its own changes)",
    "and K is re-shown, since its premise changed",
    "**A rename** is one new entity line, the members unchanged",
    "**A regroup** is one new member line",
    "**The id is never shown to the operator**, in chat or on a page",
]

BACKFILL = [
    "**Back-fill is lazy.**",
    "next shows an open decision that has no member line",
    "revises one, or raises a new decision in its item",
    "member lines for **every** open decision of that item that lacks one",
    "`closed K: superseded by M`",
    "Building an answer page is a showing",
    "Only in this session's own store; a `<repo>#N` decision gets none",
    "there is no back-fill pass",
]

WRITER_RUN = [
    "writer-run: <UTC time> <page short name> w<k>/<K> — cards <n> · tokens <input>/<output> "
    "· lints <n> [<keys>]",
    "every answer page built through the `decision-page` skill's writer split records each "
    "writer's run",
    "a run of one writer included",
    "appended to the body of the open item whose acceptance asks for `writer-run:` lines",
    "**Tokens** are that writer's input and output, from the dispatch result's usage; without "
    "it, the line says `tokens not recorded`",
    "the `lint:` lines `check_cards.js` prints for that writer's cards on the first merged "
    "check, before any fix",
    "`wi` does not read it",
]


def decisions_problems(text):
    out = []
    grouped = bullet(text, "**Grouped and depends:**")
    for phrase in GROUPED + BACKFILL:
        if phrase not in grouped:
            out.append(f"Grouped and depends lacks {phrase!r}")
    if "one back-fill pass" in flat(text) or "a back-fill pass:" in flat(text):
        out.append("a back-fill pass is prescribed")
    runs = bullet(text, "**Writer runs:**")
    for phrase in WRITER_RUN:
        if phrase not in runs:
            out.append(f"Writer runs lacks {phrase!r}")
    if "item_spend" in runs:
        out.append("Writer runs takes tokens from item_spend.py, which cannot split them")
    groups = row(text, "related decisions (groups)")
    for phrase in ["the stored group: the decision's last `group N:` member line",
                   "with none, the item's short name", "The stored group's name is chosen at "
                   "raise", "Never transitive"]:
        if phrase not in groups:
            out.append(f"the groups row lacks {phrase!r}")
    reshow = bullet(text, "**Re-show:**")
    if "the answers to the decisions its `depends N:` set names" not in reshow:
        out.append("the re-show reads no depends targets' answers")
    reframe = bullet(text, "**A reframe:**")
    if "M copies N's group and its `depends` set, and every open decision that depends on N " \
       "is repointed to M" not in reframe:
        out.append("the reframe bullet copies and repoints nothing")
    return out


def table_problems(text):
    """Every row of § What the librarian supplies to the skill has exactly 3 `|` delimiters,
    so 2 cells, as its header has: a row run into the next has more."""
    start = text.find("## What the librarian supplies to the skill")
    if start < 0:
        return ["no § What the librarian supplies to the skill"]
    body = text[start:text.index("\n## ", start + 1)]
    out = []
    for line in body.splitlines():
        if line.startswith("|"):
            cells = line.strip().strip("|").split("|")
            if len(cells) != 2:
                out.append(f"{len(cells)} cells: {line[:60]!r}")
    return out


def report_problems(text):
    want = ("Group ids are not numbers: they are a short time plus a hash (`decisions.md` "
            "§ What the store records, **Grouped and depends**), and take nothing from this "
            "counter.")
    start = text.find("## The counter")
    body = flat(text[start:text.find("\n## ", start + 1)]) if start >= 0 else ""
    return [] if want in body else ["§ The counter says nothing of group ids"]


class GroupedAndDepends(unittest.TestCase):

    def setUp(self):
        self.text = DECISIONS.read_text()

    def test_the_rules(self):
        self.assertEqual(decisions_problems(self.text), [])

    def test_each_phrase_is_load_bearing(self):
        # every pinned phrase, deleted from a copy, is caught
        text = flat(self.text)
        for phrase in GROUPED + BACKFILL + WRITER_RUN:
            self.assertIn(phrase, text)
        lines = self.text.splitlines()
        for phrase in ["**Grouped and depends:**", "**Writer runs:**"]:
            cut = "\n".join(x.replace(phrase, "**Gone:**") for x in lines)
            self.assertNotEqual(decisions_problems(cut), [], phrase)
        for old in ["Only in this session's own store", "**every** open decision",
                    "`tokens not recorded`", "check it is not taken",
                    "its whole set again with N replaced by M", "one lock, so one commit",
                    "a run of one writer included", "whose acceptance asks for `writer-run:`",
                    "the answers to the decisions its `depends N:` set names",
                    "is repointed to M", "with none, the item's short name"]:
            # the phrase may wrap, so it is cut wherever its words are split by whitespace
            pattern = r"\s+".join(re.escape(w) for w in old.split())
            cut, n = re.subn(pattern, "gone", self.text)
            self.assertGreater(n, 0, old)
            self.assertNotEqual(decisions_problems(cut), [], old)

    def test_no_item_spend_mutant(self):
        cut = self.text.replace("from the\n  dispatch result's usage",
                                "from the\n  `usage-report` skill's `scripts/item_spend.py`, else the "
                                "dispatch result's usage")
        self.assertNotEqual(cut, self.text)
        self.assertNotEqual(decisions_problems(cut), [])

    def test_every_binding_row_has_two_cells(self):
        self.assertEqual(table_problems(self.text), [])

    def test_binding_rows_mutant(self):
        # the groups row and the named-templates row run together on one line
        cut = self.text.replace("two groups |\n| named templates |", "two groups || named templates |")
        self.assertNotEqual(cut, self.text)
        self.assertNotEqual(table_problems(cut), [])

    def test_no_back_fill_pass_mutant(self):
        cut = self.text.replace("there is no back-fill pass.",
                                "there is no back-fill pass. Run one back-fill pass at start.")
        self.assertNotEqual(decisions_problems(cut), [])


WRITERS = [
    "split among writers by the `decision-page` skill's `references/writers.md`",
    "whose card `L` is the key of its stored group (the group id; the title its name)",
    "whose `dep` is its stored depends set as slugs",
    "When a page is built, a decision a card depends on that is not on the page goes in `refs` "
    "when it is answered; an open one is added as a card.",
    "Each writer returns `decision-card/5` records, checked in record mode",
    "a new decision with `$WI raise <id> --record <file>`",
    "a new revision with `$WI raise <id> --revise N --why '<why>' --record <file>`",
    "builds `cards.json` from the stored records plus `L`, `dep` and `refs`",
    "A writer never writes a store line.",
]


def writers_problems(text):
    """The librarian's half of the writer split (03ab F4): the layer and dependency from the
    store, refs and open targets, the writers' records stored with `$WI raise`, the merge."""
    b = bullet(text, "**An answer page's writers:**")
    return [f"An answer page's writers lacks {p!r}" for p in WRITERS if p not in b]


class AnswerPageWriters(unittest.TestCase):

    def setUp(self):
        self.text = DECISIONS.read_text()

    def test_the_bullet(self):
        self.assertEqual(writers_problems(self.text), [])

    def test_each_phrase_is_load_bearing(self):
        # each phrase, its words cut wherever they wrap, is caught; and the bullet gone is caught
        cut = self.text.replace("**An answer page's writers:**", "**Gone:**")
        self.assertEqual(len(writers_problems(cut)), len(WRITERS))
        for old in WRITERS:
            pattern = r"\s+".join(re.escape(w) for w in old.split())
            cut, n = re.subn(pattern, "gone", self.text)
            self.assertEqual(n, 1, old)
            self.assertNotEqual(writers_problems(cut), [], old)


class CounterSentence(unittest.TestCase):

    def test_report_names_group_ids(self):
        self.assertEqual(report_problems(REPORT.read_text()), [])

    def test_report_mutant(self):
        text = REPORT.read_text()
        cut = text.replace("Group ids are not numbers", "Groups are named")
        self.assertNotEqual(cut, text)
        self.assertNotEqual(report_problems(cut), [])


if __name__ == "__main__":
    unittest.main()
