"""The librarian finds and gives out decision numbers through `wi`'s counter, not a grep.

Answer 309 (b) (2026-10-22, work item 03ab F8): decision numbers come from a counter kept in
the store's `store.yaml`, given out by `$WI raise` under the store's lock and read by
`$WI counter`. The librarian's text that found the next number by grepping the store
(`^decision [0-9]`) switches to the counter: Rehydrate's Step 3 reads `$WI counter`,
`report.md` § The counter raises with `$WI raise`, `decisions.md` names the counter in its
numbering row and where it says what reads the headline, and SKILL.md § Intake step 3 raises
with `$WI raise <id>`.

Plugins update separately (03ab `10` § H1), so an older installed `wi` with no `raise` or
`counter` (argparse's `invalid choice: 'raise'`, exit 2) keeps the old way: the grep plus one,
written with `$WI note <id> --raw`. Rehydrate's fenced line runs the grep only when
`$WI counter` fails; `report.md` and `decisions.md` each say the fallback in words.

Each check is proved by a mutant that restores the old text or deletes the new. Standard
library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LIB = PLUGIN / "skills" / "librarian-mode"
REHYDRATE = LIB / "references" / "rehydrate.md"
REPORT = LIB / "references" / "report.md"
DECISIONS = LIB / "references" / "decisions.md"
SKILL = LIB / "SKILL.md"

GREP = "grep -rh '^decision [0-9]'"
REHYDRATE_LINE = "$WI counter || " + GREP
FALLBACK = "`invalid choice: 'raise'`"


def flat(text):
    return " ".join(text.split())


def mutate(text, old, new):
    """`text` with `old` replaced by `new`, matching across line breaks; `old` must occur
    exactly once, so a mutant that misses its target fails rather than passing vacuously."""
    pat = r"\s+".join(re.escape(w) for w in old.split())
    found = re.findall(pat, text)
    assert len(found) == 1, (old, len(found))
    return re.sub(pat, lambda m: new, text)


def section(text, heading):
    """The body of the `## <heading>` section, up to the next `## ` heading."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def rehydrate_problems(text):
    out = []
    lines = text.splitlines()
    if not any(x.startswith(REHYDRATE_LINE) for x in lines):
        out.append("no `$WI counter ||` line")
    if any(GREP in x and not x.startswith(REHYDRATE_LINE) for x in lines):
        out.append("a bare counter grep")
    return out


def report_problems(text):
    body = flat(section(text, "The counter"))
    out = []
    if not body:
        return ["no § The counter"]
    if "raising a decision is `$WI raise <id>`, which gives out N under the store's lock" \
            not in body:
        out.append("no `$WI raise`")
    if "`$WI counter` prints the last N given out (`rehydrate.md` § Step 3)" not in body:
        out.append("no `$WI counter`")
    if "continue from the highest N" in body or "raising a decision appends one line" in body:
        out.append("the old counter text")
    if f"An older `wi` ({FALLBACK}, exit 2): N is one more than the last decision number" \
            not in body or "written with `$WI note <id> --raw`" not in body:
        out.append("no older-wi fallback")
    if "Group ids are not numbers: they are a short time plus a hash" not in body \
            or "take nothing from this counter" not in body:
        out.append("no group-id sentence")
    return out


def decisions_problems(text):
    body = flat(text)
    out = []
    if "| the caller's numbering | the store counter" not in body \
            or "N from `$WI raise`, which gives it out under the store's lock" not in body:
        out.append("numbering row without `$WI raise`")
    if "continues from the highest N" in body:
        out.append("numbering row continues from the highest N")
    if "the counter (`$WI counter`) read it unchanged" not in body:
        out.append("headline read without `$WI counter`")
    if "so `$WI counter` and `wi` read it unchanged" not in body:
        out.append("label read without `$WI counter`")
    if "the counter grep (`^decision [0-9]`)" in body or "the counter grep and `wi`" in body:
        out.append("the counter grep as the reader")
    if f"with no `raise` at all, {FALLBACK}, exit 2, N is one more than the last decision " \
            "number the counter grep prints (`rehydrate.md` § Step 3)" not in body:
        out.append("no older-wi fallback")
    return out


def skill_problems(text):
    body = flat(text)
    out = []
    if "every decision (one or many) raised with `$WI raise <id>` on the item" not in body:
        out.append("Intake step 3 without `$WI raise <id>`")
    if "as `decision N:` on the item" in body:
        out.append("Intake step 3 writes `decision N:` by hand")
    return out


class CounterText(unittest.TestCase):

    def test_rehydrate(self):
        text = REHYDRATE.read_text(encoding="utf-8")
        self.assertEqual(rehydrate_problems(text), [])
        # mutants: the old bare grep restored; the line deleted
        old = text.replace(REHYDRATE_LINE, GREP)
        self.assertIn("no `$WI counter ||` line", rehydrate_problems(old))
        self.assertIn("a bare counter grep", rehydrate_problems(old))
        gone = "\n".join(x for x in text.splitlines() if not x.startswith(REHYDRATE_LINE))
        self.assertIn("no `$WI counter ||` line", rehydrate_problems(gone))

    def test_report(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertEqual(report_problems(text), [])
        # mutants: each new sentence deleted or the old one restored
        self.assertIn("no `$WI raise`", report_problems(
            mutate(text, "raising a decision is `$WI raise <id>`",
                      "raising a decision appends one line")))
        self.assertIn("the old counter text", report_problems(
            mutate(text, "raising a decision is `$WI raise <id>`",
                      "raising a decision appends one line")))
        self.assertIn("no `$WI counter`", report_problems(
            mutate(text, "`$WI counter` prints the last N given out",
                      "on re-entry continue from the highest N")))
        self.assertIn("the old counter text", report_problems(
            mutate(text, "`$WI counter` prints the last N given out",
                      "on re-entry continue from the highest N")))
        self.assertIn("no older-wi fallback", report_problems(
            mutate(text, f"An older `wi` ({FALLBACK}", "An older `wi` (")))
        self.assertIn("no older-wi fallback", report_problems(
            mutate(text, "written with `$WI note <id> --raw`", "written")))
        self.assertIn("no group-id sentence", report_problems(
            mutate(text, "Group ids are not numbers", "Group ids")))
        self.assertEqual(["no § The counter"],
                         report_problems(mutate(text, "## The counter", "## A counter")))

    def test_decisions(self):
        text = DECISIONS.read_text(encoding="utf-8")
        self.assertEqual(decisions_problems(text), [])
        # mutants: the old words restored, one place at a time
        row = mutate(text, "N from `$WI raise`, which gives it out under the store's lock, and "
                        "the last one given out from `$WI counter`",
                        "`decision N:` continues from the highest N")
        self.assertIn("numbering row without `$WI raise`", decisions_problems(row))
        self.assertIn("numbering row continues from the highest N", decisions_problems(row))
        head = mutate(text, "the counter (`$WI counter`) read it unchanged",
                         "the counter grep (`^decision [0-9]`) read it unchanged")
        self.assertIn("headline read without `$WI counter`", decisions_problems(head))
        self.assertIn("the counter grep as the reader", decisions_problems(head))
        label = mutate(text, "so `$WI counter` and `wi` read it unchanged",
                          "so the counter grep and `wi` read it unchanged")
        self.assertIn("label read without `$WI counter`", decisions_problems(label))
        self.assertIn("the counter grep as the reader", decisions_problems(label))
        self.assertIn("no older-wi fallback", decisions_problems(
            mutate(text, f"with no `raise` at all, {FALLBACK}", "with no `raise` at all")))

    def test_skill(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertEqual(skill_problems(text), [])
        old = mutate(text, "raised with `$WI raise <id>` on the item",
                                 "as `decision N:` on the item")
        self.assertIn("Intake step 3 without `$WI raise <id>`", skill_problems(old))
        self.assertIn("Intake step 3 writes `decision N:` by hand", skill_problems(old))


if __name__ == "__main__":
    unittest.main()
