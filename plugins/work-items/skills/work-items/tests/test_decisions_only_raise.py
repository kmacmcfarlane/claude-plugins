"""Decisions enter a store only through `wi raise` (9fb8): a plain `wi note`
refuses a text opening `decision N:` (it would be bulleted, where no reader
counts it); `wi note --raw` writes a column-0 `decision N:` only as a copy
of a decision the store already holds, checked under the lock the write
takes; `wi lint` gives a `wi: note:` on stderr, never a problem, for a line
holding `decision N:` that is not a column-0 headline.

Each check here was proved against a mutant of wi.py (the mutant named in
the test's docstring makes it fail). Temporary stores only.

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import unittest
import contextlib
import io
from unittest import mock

from test_counter import CounterCase, IID, wi

STRAY = "not a column-0 headline"


class TestPlainNote(CounterCase):

    def test_plain_decision_headline_refused(self):
        """Exit 1, nothing written, the fix named. Mutant: the plain
        refusal removed from _note_decision_refusal."""
        self.item("other-item-2222", notes="decision 5: five?")
        before = self.snapshot()
        r = self.wi("note", IID, "--", "decision 210: which way?")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("text 1:", r.stderr)
        self.assertIn(f"wi raise {IID} -- ", r.stderr)
        self.assertIn(f"wi note {IID} --raw", r.stderr)
        self.assertNotIn("which way", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_plain_refused_after_whitespace_and_as_a_later_text(self):
        """Leading whitespace, and a second text: the whole note refused.
        Mutant: the pattern anchored at column 0 (no leading \\s*)."""
        before = self.snapshot()
        r = self.wi("note", IID, "--", "fine line", "  decision 3: q?")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("text 2:", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_plain_prose_mentioning_a_decision_passes(self):
        """`decision` mid-text, or not followed by `N:`, is prose.
        Mutant: the pattern searched anywhere in the text."""
        self.ok("note", IID, "--", "see decision 5: settled",
                "decision 2026-09-08 by the operator")
        self.assertIn("see decision 5: settled", self.item_text())


class TestRawNote(CounterCase):

    def test_raw_copy_of_an_existing_decision_written(self):
        """N held by another item (archive included): written column-0.
        Mutant: the archive dropped from items_decision_numbers (archived
        copy refused)."""
        self.item("old-item-3333", notes="decision 9: nine?",
                  where="archive/2026")
        self.ok("note", IID, "--raw", "--", "decision 9: nine?")
        self.assertIn("\ndecision 9: nine?\n", self.item_text())

    def test_raw_new_number_refused(self):
        """N above the last given out, and a gap below it, both refused,
        nothing written, `wi raise` named. Mutant: the under-lock check
        removed from cmd_note."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 20\n")
        self.item("other-item-2222", notes="decision 5: five?")
        before = self.snapshot()
        for n in (21, 7):
            r = self.wi("note", IID, "--raw", "--", f"decision {n}: q?")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn(f"decision {n} is not in the store", r.stderr)
            self.assertIn("wi raise", r.stderr)
            self.assertEqual(self.snapshot(), before)

    def test_raw_fenced_decision_does_not_count(self):
        """A fenced `decision N:` is text, so N is not in the store.
        Mutant: the fence rule dropped in items_decision_numbers."""
        self.item("other-item-2222", notes="```\ndecision 4: example\n```")
        r = self.wi("note", IID, "--raw", "--", "decision 4: example")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_raw_indented_headline_refused(self):
        """An indented raw `decision N:` reads as nothing; refused even for
        an existing N. Mutant: the raw branch of _note_decision_refusal
        returns None."""
        self.item("other-item-2222", notes="decision 5: five?")
        before = self.snapshot()
        r = self.wi("note", IID, "--raw", "--", "  decision 5: five?")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("indented", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_raw_copy_onto_an_item_holding_n_refused(self):
        """The target already holds N: refused, pointing to --revise.
        Mutant: the held-N check removed from cmd_note."""
        self.item(IID, notes="decision 5: five?")
        before = self.snapshot()
        r = self.wi("note", IID, "--raw", "--", "decision 5: five again?")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(f"wi raise {IID} --revise 5", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_raw_other_decision_lines_pass(self):
        """answer, group and indented card lines are not headlines."""
        self.item("other-item-2222", notes="decision 5: five?")
        self.ok("note", IID, "--raw", "--", "answer 5: (a)",
                "  why ask: see decision 5: above")

    def test_raw_check_reads_the_store_under_the_lock(self):
        """The store is read after the lock is taken: a raise that lands
        while the note waits makes its copy valid. Mutant: the known set
        read before `with Lock(root)`."""
        calls = []
        real_enter = wi.Lock.__enter__
        real_nums = wi.items_decision_numbers

        def enter(self):
            calls.append("lock")
            return real_enter(self)

        def nums(root):
            calls.append("read")
            return real_nums(root)

        self.item("other-item-2222", notes="decision 5: five?")
        args = wi.build_parser().parse_args(
            ["note", IID, "--raw", "--", "decision 5: five?"])
        args.root = str(self.root)
        with mock.patch.object(wi.Lock, "__enter__", enter), \
                mock.patch.object(wi, "items_decision_numbers", nums), \
                mock.patch.dict("os.environ", self.env), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wi.cmd_note(args), 0)
        self.assertEqual(calls[:2], ["lock", "read"])


class TestLintNote(CounterCase):

    def lint(self):
        return self.wi("lint")

    def test_bulleted_decision_is_a_note(self):
        """A bulleted `decision N:` is a `wi: note:` on stderr with its
        file:line and the fix; exit 0 on an otherwise clean store.
        Mutant: the stray_decision_notes loop removed from cmd_lint."""
        path = self.item(IID, notes="- 2026-10-26 decision 210: which?")
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = path.read_text().split("\n").index(
            "- 2026-10-26 decision 210: which?") + 1
        self.assertIn(f"wi: note: {path}:{line}: ", r.stderr)
        self.assertIn("wi raise", r.stderr)
        self.assertNotIn("decision 210", r.stdout)

    def test_indented_decision_is_a_note(self):
        """Mutant: _STRAY_DECISION_RE anchored at column 0 after a bullet."""
        self.item(IID, notes="decision 1: q?\n  decision 2: q?")
        r = self.lint()
        self.assertEqual(r.stderr.count(STRAY), 1, r.stderr)

    def test_quiet_on_headlines_prose_fences_and_other_lines(self):
        """No note for a headline, dated prose, a fenced line, answer and
        shown lines, or front matter. Mutants: the fence skip removed; the
        front-matter skip removed."""
        self.item(IID, notes=(
            "decision 3: q?\n"
            "answer 3: decision 3: was (a)\n"
            "shown 3: 2026-10-26T10:00Z decision 3: shown\n"
            "- 2026-09-08 Operator decision 2026-09-08 recorded\n"
            "```\n- decision 4: example\n```"))
        path = self.root / "items" / f"{IID}.md"
        path.write_text(path.read_text().replace(
            f"title: {IID}", f"title: {IID}\ntags:\n  - decision 9: a tag"))
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(STRAY, r.stderr)

    def test_prose_naming_a_decision_mid_line_is_quiet(self):
        """A bullet whose `decision N:` is mid-line is prose; a dated
        bullet and an indented line opening it still note. Mutant: the
        old unanchored pattern, searched anywhere in the line."""
        self.item(IID, notes=("decision 2: q?\n"
                              "- reviewer on decision 65: x\n"
                              "- 2026-10-26 decision 210: which?\n"
                              "  decision 2: again"))
        r = self.lint()
        self.assertEqual(r.stderr.count(STRAY), 2, r.stderr)
        path = self.root / "items" / f"{IID}.md"
        lines = path.read_text().split("\n")
        n = lines.index("- reviewer on decision 65: x") + 1
        self.assertNotIn(f"{path}:{n}:", r.stderr)

    def test_note_does_not_change_the_exit(self):
        """A store with a real problem still exits 3; the note stays on
        stderr. Mutant: the note appended to problems."""
        self.item(IID, notes="- 2026-10-26 decision 210: which?")
        self.item("dangling-item-4444")
        p = self.root / "items" / "dangling-item-4444.md"
        p.write_text(p.read_text().replace("priority: 2",
                                           "priority: 2\ndeps: [nope-0000]"))
        r = self.lint()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn(STRAY, r.stderr)
        self.assertNotIn(STRAY, r.stdout)


if __name__ == "__main__":
    unittest.main()
