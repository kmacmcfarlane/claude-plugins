"""The librarian's store keeps card records (feature K3 of the v5 card layout plan).

Answers 341 (a), 342 (a) and 343 (a) (2026-10-23): one record for a decision's card on every
surface, stamped `decision-card/5`, stored one immutable file per revision by `$WI raise
--record` and read back by `$WI show --card` (the work-items format's § Card records). Legacy
cards are read by the decisions skill's legacy reference and upgraded on a touch, never on a
read that only lists them. This file pins the librarian's side in
`references/decisions.md` § What the store records: the raise and revise commands, machine
lines without a new record, the checker and its disclosure, the headline-only fallback, the
reader rule for a legacy block after a record, the missing-file rule, the older-`wi` rule and
the cases that never upgrade. Each rule is checked on the real file and on a mutant copy with
its sentence deleted, which it must catch.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REFS = PLUGIN / "skills" / "librarian-mode" / "references"
DECISIONS = REFS / "decisions.md"
MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"


def flat(text):
    return " ".join(text.split())


# (what the rule is, the phrases it holds): each phrase must stand in decisions.md
RULES = [
    ("the raise", [
        "$WI raise <id> --record <file> [--lines <lines file>]",
        "write the card the decisions skill renders as its record",
        "`$WI raise` prints N. It writes the record once, then appends the headline it builds "
        "from the record, `raised:` and the `card:` line",
    ]),
    ("the checker", [
        "node <decision-page skill dir>/scripts/check_cards.js --record <file>",
        "The check is the `decision-page` skill's checker in record mode (its "
        "`scripts/check_cards.js`), run from that skill's base directory as the session's skill "
        "list gives it",
    ]),
    ("the disclosure", [
        "the record is stored after `wi`'s own checks only",
        "*card records not schema-checked: no decision-page skill* (or *no node*)",
    ]),
    ("the headline-only fallback", [
        "Without the `decisions` skill as well there is no card-record reference: the librarian "
        "raises headline-only decisions, `$WI raise <id> -- '<question> — options: (a) … "
        "[recommended] | … | (z) decide later'`, with the one `why ask:` line under each through "
        "`$WI note <id> --raw`",
        "and the one `why ask:` line written without the decisions skill) is a headline-only "
        "decision",
    ]),
    ("the record's n", [
        "The record's `n` is any `n` of 1 or more; `wi` writes the N it gives out over it",
    ]),
    ("the raised time", [
        "`TZ=UTC git -C \"$WORK_ITEMS_ROOT\" log --reverse "
        "--date=format-local:%Y-%m-%dT%H:%M:%SZ --format=%cd -S'decision N:' -- "
        "\"$WORK_ITEMS_ROOT/items/<item file>\"`, the first hit",
    ]),
    ("the revise", [
        "**Revised:** `$WI raise <id> --revise N --why '<why>' --record <file>`",
        "A new record carries a **new** `rev` for new content; the same `rev` only for a "
        "format-only upgrade",
        "An answered card is never revised: `wi` refuses it",
    ]),
    ("machine lines", [
        "`$WI raise <id> --revise N --why '<why>' --lines <lines file>` and no `--record`: the "
        "record and its `rev` stay unchanged, so its page answers keep counting",
        "**current** `card:` line",
        "The lines file holds one indented line per machine line, each opening with its key",
        "`--revise N --lines` needs a `card:` line for N, so a legacy card is upgraded first",
        "after a `--revise N --record`, the machine lines that still apply ride that revision's "
        "`--lines`",
    ]),
    ("the grant", [
        "A signed grant names the card's current revision, `card: <record path> rev <rev> "
        "sha256:<hex>`, with the values `show --card` prints",
        "is an input for the signed-grants build, which settles it",
        "A card a live grant names is never upgraded or revised while the grant runs",
    ]),
    ("reading a card", [
        "**Reading a card:** `$WI show <id> --card N --json` reads the current record",
        "*decision N has no card record*: a legacy card or a headline only",
        "An exit 2 that says *unrecognized arguments* is an older `wi`",
    ]),
    ("the legacy card", [
        "legacy cards are read by the decisions skill's legacy reference "
        "(`references/legacy-cards.md`), as written",
        "It is **upgraded on its next touch** — a card or block showing, a page publish, a "
        "revision; never an answer, a list line, a Groom row, a tag-size mention, an estate "
        "sweep or a ref",
        "**An answered card is never upgraded.**",
        "A card that is also on a live answer page is upgraded from that page card, its page "
        "`rev` kept, so the page's answers still count",
        "is a headline-only decision, never a stored card to backfill as one",
    ]),
    ("the reader rule", [
        "a legacy block for N after a `card:` line for N, in file order",
        "A backfill, or nothing the record lacks: the record stays current, and `revised: <UTC> "
        "— legacy backfill after v5 ignored` is appended under that block",
        "A real revision: it is upgraded into a new record with a **new** `rev`",
        "While that v5 block stands, every view takes the question, options and rec from the "
        "record (`$WI show --card`), never from the last headline line",
    ]),
    ("the missing file", [
        "**A missing or mismatched record file** (`$WI show --card` exits 3): show the headline, "
        "and say *card record missing (`<path>`); restore it from the store's history*; never "
        "backfill it",
    ]),
    ("the older wi", [
        "**An older `wi`** (no `--record`): the record stays in the session's scratchpad",
        "the headline `wi` would build from the record",
        "the card is shown from the scratchpad copy, and `--revise N --record` follows once "
        "`wi` updates",
        "Never legacy lines in its place",
    ]),
]


def problems(text):
    flat_text = flat(text)
    out = []
    for name, phrases in RULES:
        for p in phrases:
            if p not in flat_text:
                out.append(f"{name}: missing {p[:60]!r}")
    if 'git -C "$MAIN" log --reverse' in flat_text:
        out.append("the raised time is read from the main checkout's history")
    # no stored card in indented lines is written any more
    if re.search(r"^\s+(what|why now|context|rec|basis|unknown): <", text, re.M):
        out.append("a stored-line card template is still written")
    return out


class StoreRecords(unittest.TestCase):

    def setUp(self):
        self.text = DECISIONS.read_text()

    def test_the_rules(self):
        self.assertEqual(problems(self.text), [])

    def test_each_sentence_deleted_is_caught(self):
        flat_text = flat(self.text)
        for name, phrases in RULES:
            for p in phrases:
                cut = flat_text.replace(p, "")
                self.assertNotEqual(cut, flat_text, p)
                self.assertTrue(problems(cut), f"{name}: {p}")

    def test_the_main_checkout_recipe_restored_is_caught(self):
        cut = self.text.replace('git -C "$WORK_ITEMS_ROOT" log', 'git -C "$MAIN" log')
        self.assertNotEqual(cut, self.text)
        self.assertIn("the raised time is read from the main checkout's history", problems(cut))

    def test_a_stored_line_template_restored_is_caught(self):
        self.assertIn("a stored-line card template is still written",
                      problems(self.text + "\n    what: <what is decided>\n"))

    def test_the_manifest_declares_the_checker(self):
        desc = json.loads(MANIFEST.read_text())["description"]
        want = ("whose decisions skill's card-record reference librarian-mode writes each card "
                "record to, and whose decision-page skill's checker it runs on each record "
                "before storing it, when node is present")
        self.assertIn(want, desc)
        self.assertIn("without the checker the record is stored after wi's own checks and the "
                      "Report says so", desc)
        self.assertNotIn(want, desc.replace("whose decisions skill's card-record", "whose"))


if __name__ == "__main__":
    unittest.main()
