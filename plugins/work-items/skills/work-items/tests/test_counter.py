"""Decision numbers from a counter in store.yaml (03ab F8): `wi raise` gives
out N under the store's lock and writes the headline and its `raised:` line;
`wi counter` prints the last N, read-only; every read takes the larger of
the counter and the items' highest N (archive included, fenced lines not);
`wi lint` reseeds a counter behind the items, inside the lock, and never
lowers one ahead; `wi init` keeps the block; conflict markers and a value
that is not a whole number are refused.

Each check here was proved against a mutant of wi.py (the mutant named in
the test's docstring makes it fail). Temporary stores only; git runs with a
temp HOME and global config, and never sees a repo around the temp dir.

Standard library only. Run from plugins/work-items/skills/work-items:

    python3 -m unittest discover -s tests -q
"""
import contextlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"

spec = importlib.util.spec_from_file_location("wi_counter", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

GIT = shutil.which("git")
IID = "probe-item-1111"
ITEM = """---
id: {iid}
title: {iid}
type: task
status: todo
priority: 2
created: 2026-08-01
updated: 2026-08-01
---

Description of {iid}.

## Notes
{notes}
"""
UTC_SECOND = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"
SECRET = "DB_PASS=hunter2hunter2hunterXYZ"   # test_wi's assignment fake


class CounterCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="wi-f8-")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        home = self.tmp / "home"
        home.mkdir()
        (home / "gitconfig").write_text("")
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("GIT_", "WI_", "WORK_ITEMS_"))}
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home),
                   GIT_CONFIG_GLOBAL=str(home / "gitconfig"),
                   GIT_CONFIG_NOSYSTEM="1",
                   GIT_CEILING_DIRECTORIES=str(self.tmp),
                   WORK_ITEMS_OWNER="tester@local")
        self.env = env
        self.root = self.tmp / "base" / ".work-items"
        self.root.mkdir(parents=True)
        (self.root / "items").mkdir()
        self.yaml("tracking: tracked\n")
        self.item(IID)

    # -- helpers ---------------------------------------------------------

    def wi(self, *args, root=None, **kw):
        env = dict(self.env, WORK_ITEMS_ROOT=str(root or self.root))
        return subprocess.run([sys.executable, str(WI), *args], env=env,
                              capture_output=True, text=True, **kw)

    def ok(self, *args, **kw):
        r = self.wi(*args, **kw)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def yaml(self, body):
        (self.root / "store.yaml").write_text(
            "# wi store settings; format: the work-items skill's "
            "references/format.md\n" + body)

    def yaml_text(self):
        return (self.root / "store.yaml").read_text()

    def item(self, iid, notes="- 2026-08-01 started", where="items"):
        path = self.root / where / f"{iid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ITEM.format(iid=iid, notes=notes))
        return path

    def item_text(self, iid=IID):
        return (self.root / "items" / f"{iid}.md").read_text()

    def counter_value(self):
        m = re.search(r"^counters:\n(?:[ \t].*\n)*?[ \t]+decision: (\S+)$",
                      self.yaml_text(), re.M)
        return m and m.group(1)

    def snapshot(self):
        """Bytes and mtime of store.yaml and every item file."""
        paths = [self.root / "store.yaml"] + sorted(
            self.root.glob("items/*.md")) + sorted(
            self.root.glob("archive/*/*.md"))
        return {p: (p.read_bytes(), p.stat().st_mtime_ns)
                for p in paths if p.exists()}


class TestRaise(CounterCase):

    def test_raise_on_an_empty_store(self):
        """Prints 1; the item gains the headline then `  raised: <UTC>`,
        which decision_raised reads; the block holds 1. Mutant: no
        `raised:` line written."""
        r = self.ok("raise", IID, "--", "Which store? — options: (a) x | (b) y")
        self.assertEqual(r.stdout, "1\n")
        text = self.item_text()
        self.assertRegex(text, r"\ndecision 1: Which store\? — options: "
                               r"\(a\) x \| \(b\) y\n  raised: "
                               + UTC_SECOND + r"\n")
        self.assertEqual(self.counter_value(), "1")
        item = wi.load_item_anywhere(self.root, IID)
        self.assertRegex(wi.decision_raised(item)[1], "^" + UTC_SECOND + "$")
        self.assertEqual(wi.unanswered_decisions(item),
                         [(1, "Which store? — options: (a) x | (b) y")])

    def test_next_numbers_follow(self):
        self.assertEqual(self.ok("raise", IID, "--", "one?").stdout, "1\n")
        self.assertEqual(self.ok("raise", IID, "--", "two?").stdout, "2\n")
        self.assertEqual(self.counter_value(), "2")

    def test_counter_behind_the_items_archive_included(self):
        """Counter 3, items reaching 9 (the 9 in archive/2026/): 10.
        Mutants: the max over the items removed (4); archive/ dropped from
        the scan (9)."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 3\n")
        self.item("other-item-2222", notes="decision 8: eight?")
        self.item("old-item-3333", notes="decision 9: nine?\nanswer 9: a",
                  where="archive/2026")
        self.assertEqual(self.ok("raise", IID, "--", "next?").stdout, "10\n")
        self.assertEqual(self.counter_value(), "10")

    def test_counter_ahead_is_a_gap_kept(self):
        self.yaml("tracking: tracked\ncounters:\n  decision: 40\n")
        self.item("other-item-2222", notes="decision 8: eight?")
        self.assertEqual(self.ok("raise", IID, "--", "next?").stdout, "41\n")

    def test_a_fenced_decision_is_not_counted(self):
        """A `decision 12:` inside a fence is text. Mutant: the fence rule
        removed (13)."""
        self.item("other-item-2222",
                  notes="decision 2: two?\n\n```\ndecision 12: quoted\n```")
        self.assertEqual(self.ok("raise", IID, "--", "next?").stdout, "3\n")

    def test_two_raises_at_once_get_distinct_numbers(self):
        """Two threads raise; the allocation read waits on a Barrier(2), so
        without the lock both read the same floor. Mutant: the Lock
        removed from raise (both get the same N)."""
        barrier = threading.Barrier(2)
        floor = wi._decision_floor

        def waiting_floor(root):
            try:
                barrier.wait(timeout=1.0)   # under the lock: times out
            except threading.BrokenBarrierError:
                pass
            return floor(root)

        got, errors = [], []

        def one(q):
            try:
                got.append(wi.raise_decision(self.root, IID, q)[0])
            except Exception as e:   # surfaced below
                errors.append(e)

        with mock.patch.object(wi, "_decision_floor", waiting_floor):
            threads = [threading.Thread(target=one, args=(q,))
                       for q in ("first?", "second?")]
            for t in threads:
                t.start()
            for t in threads:
                t.join(30)
        self.assertEqual(errors, [])
        self.assertEqual(sorted(got), [1, 2])
        text = self.item_text()
        self.assertIn("first?", text)
        self.assertIn("second?", text)
        self.assertEqual(sorted(re.findall(r"^decision (\d+):", text, re.M)),
                         ["1", "2"])
        self.assertEqual(self.counter_value(), "2")

    def test_stdin_is_never_read(self):
        """stdin an open, never-closed pipe: raise returns at once. Mutant:
        stdin read whenever it is not a terminal (hangs)."""
        env = dict(self.env, WORK_ITEMS_ROOT=str(self.root))
        proc = subprocess.Popen([sys.executable, str(WI), "raise", IID, "--",
                                 "piped?"], env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            code = proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            self.fail("raise blocked on an open stdin")
        finally:
            proc.stdin.close()
        out = proc.stdout.read().decode()
        proc.stdout.close()
        proc.stderr.close()
        self.assertEqual((code, out), (0, "1\n"))

    def test_refused_questions_write_nothing(self):
        """Each refusal exits 1, names the question (never quoting it), and
        leaves the item and the counter as they were. Mutant: the note
        --raw refusals skipped."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 5\n")
        cases = {
            "fence opener": ("```sh", "opens a code fence"),
            "tilde fence": ("~~~", "opens a code fence"),
            "heading": ("## x", "starts '## '"),
            "secret shape": (SECRET, "likely secret value"),
            "line break": ("a\nb", "must be one line"),
            "empty": ("   ", "empty"),
            "a second headline": ("decision 5: x", "starts 'decision'"),
        }
        before = self.snapshot()
        for name, (question, why) in cases.items():
            with self.subTest(name):
                r = self.wi("raise", IID, "--", question)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("question:", r.stderr)
                self.assertIn(why, r.stderr)
                self.assertIn("nothing written", r.stderr)
                self.assertEqual(r.stdout, "")
                if name == "secret shape":
                    self.assertNotIn("hunter2", r.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_no_question_is_refused(self):
        r = self.wi("raise", IID)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("put it after --", r.stderr)

    def test_a_headline_in_any_case_is_refused(self):
        """Mutant: the case-insensitive match made case-sensitive."""
        before = self.snapshot()
        for question in ("Decision 9: x", "DECISION 9: x"):
            with self.subTest(question):
                r = self.wi("raise", IID, "--", question)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("starts 'decision'", r.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_blank_line_inside_the_block(self):
        """`counters:`, a blank line, then the key: the block reads 50 and
        the write keeps one decision line. Mutant: the block ending at the
        first line that is not indented (reads 0, writes a second
        block)."""
        self.yaml("tracking: tracked\ncounters:\n\n  decision: 50\n")
        self.assertEqual(self.ok("counter").stdout, "50\n")
        self.assertEqual(self.ok("raise", IID, "--", "q?").stdout, "51\n")
        text = self.yaml_text()
        self.assertEqual(text.count("decision:"), 1, text)
        self.assertEqual(text.count("counters:"), 1, text)
        self.assertEqual(self.counter_value(), "51")

    def test_a_trailing_blank_line_stays_outside_the_block(self):
        self.yaml("tracking: tracked\ncounters:\n  decision: 4\n\n# end\n")
        self.ok("raise", IID, "--", "q?")
        self.assertTrue(self.yaml_text().endswith(
            "counters:\n  decision: 5\n\n# end\n"), self.yaml_text())

    def test_a_word_starting_decision_is_a_question(self):
        self.assertEqual(self.ok("raise", IID, "--", "decisions: which?")
                         .stdout, "1\n")

    def test_unknown_item_writes_nothing(self):
        before = self.snapshot()
        r = self.wi("raise", "no-such-item", "--", "q?")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_a_raise_write_keeps_the_other_lines(self):
        """tracking:, repo: and comment lines survive the counter write.
        Mutant: write_counter rewriting the file as the old write_tracking
        body did (the counter alone)."""
        self.yaml("tracking: tracked\nrepo: own\n# a note\n"
                  "counters:\n  decision: 2\n  other-thing: 7\n")
        with mock.patch.object(wi, "_per_change_state", lambda root: None):
            n, _ = wi.raise_decision(self.root, IID, "q?")
        self.assertEqual(n, 3)
        self.assertEqual(self.yaml_text(),
                         "# wi store settings; format: the work-items "
                         "skill's references/format.md\ntracking: tracked\n"
                         "repo: own\n# a note\ncounters:\n  decision: 3\n"
                         "  other-thing: 7\n")
        self.assertEqual(wi.read_tracking(self.root), "tracked")
        self.assertTrue(wi.read_repo_own(self.root))

    def test_block_added_when_absent(self):
        self.ok("raise", IID, "--", "q?")
        self.assertEqual(self.yaml_text().split("\n", 1)[1],
                         "tracking: tracked\ncounters:\n  decision: 1\n")

    def test_no_store_yaml_gets_none(self):
        """A store without store.yaml takes its N from the items and gets no
        file (one without tracking: would be a lint problem)."""
        (self.root / "store.yaml").unlink()
        self.item("other-item-2222", notes="decision 4: four?")
        self.assertEqual(self.ok("raise", IID, "--", "q?").stdout, "5\n")
        self.assertFalse((self.root / "store.yaml").exists())

    def test_conflict_markers_refused(self):
        """A store.yaml holding conflict markers: raise exits 1 and writes
        nothing. Mutant: the check removed (raise writes)."""
        self.yaml("tracking: tracked\ncounters:\n<<<<<<< HEAD\n"
                  "  decision: 4\n=======\n  decision: 6\n>>>>>>> other\n")
        before = self.snapshot()
        r = self.wi("raise", IID, "--", "q?")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("merge conflict markers", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_a_counter_not_a_whole_number_is_refused(self):
        self.yaml("tracking: tracked\ncounters:\n  decision: x\n")
        before = self.snapshot()
        r = self.wi("raise", IID, "--", "q?")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("must be a whole number", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_existing_tests_output_unchanged_by_needs_input(self):
        """The headline raise writes is what needs-input lists."""
        self.ok("raise", IID, "--", "q?")
        r = self.ok("needs-input", "--plain")
        self.assertIn(f"{IID}\tdecision\t1\t", r.stdout)


class TestCounter(CounterCase):

    def test_empty_store_prints_zero(self):
        self.assertEqual(self.ok("counter").stdout, "0\n")

    def test_prints_the_max_and_writes_nothing(self):
        """Mutant: a write added (bytes or mtime change)."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 3\n")
        self.item("old-item-3333", notes="decision 9: nine?",
                  where="archive/2026")
        before = self.snapshot()
        time.sleep(0.01)
        self.assertEqual(self.ok("counter").stdout, "9\n")
        self.assertEqual(self.snapshot(), before)
        self.yaml("tracking: tracked\ncounters:\n  decision: 30\n")
        self.assertEqual(self.ok("counter").stdout, "30\n")

    def test_takes_no_lock(self):
        lock = self.root / ".lock"
        self.assertFalse(lock.exists())
        self.ok("counter")
        self.assertFalse(lock.exists())

    def test_refuses_a_counter_it_cannot_read(self):
        self.yaml("tracking: tracked\ncounters:\n  decision: x\n")
        r = self.wi("counter")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)


class TestLint(CounterCase):

    def test_reseeds_a_counter_behind(self):
        """A hand-written `decision 7:` past the counter: lint reseeds,
        prints the notice on stderr, and exits as it would. Mutant: the
        reseed removed."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 2\n")
        self.item("other-item-2222", notes="decision 7: by hand")
        r = self.ok("lint")
        self.assertIn("lint clean", r.stdout)
        self.assertIn("counter: decision reseeded 2 \u2192 7", r.stderr)
        self.assertEqual(self.counter_value(), "7")
        r = self.ok("lint")
        self.assertNotIn("counter:", r.stderr)

    def test_seeds_a_store_without_a_block(self):
        self.item("other-item-2222", notes="decision 309: by hand")
        r = self.ok("lint")
        self.assertIn("counter: decision reseeded 0 \u2192 309", r.stderr)
        self.assertEqual(self.yaml_text().split("\n", 1)[1],
                         "tracking: tracked\ncounters:\n  decision: 309\n")

    def test_a_counter_ahead_is_never_lowered(self):
        """Counter 320, items reaching 315: silent, nothing written.
        Mutant: the items' maximum written unconditionally (320 → 315)."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 320\n")
        self.item("other-item-2222", notes="decision 315: x")
        before = self.snapshot()
        r = self.ok("lint")
        self.assertNotIn("counter", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_reseed_rereads_under_the_lock(self):
        """The counter moved past the items between lint's first read and
        its lock: the reseed writes nothing. Mutant: the reseed writing the
        items' max without re-reading the counter under the lock."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 2\n")
        self.item("other-item-2222", notes="decision 7: by hand")
        real_lock = wi.Lock

        class MovingLock(real_lock):
            def __enter__(inner):
                self.yaml("tracking: tracked\ncounters:\n  decision: 50\n")
                return super().__enter__()

        with mock.patch.object(wi, "Lock", MovingLock):
            self.assertIsNone(wi.reseed_counter(self.root))
        self.assertEqual(self.counter_value(), "50")

    def test_a_counter_not_a_whole_number_is_a_problem(self):
        self.yaml("tracking: tracked\ncounters:\n  decision: x\n")
        self.item("other-item-2222", notes="decision 7: by hand")
        r = self.wi("lint")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("counters: decision must be a whole number", r.stdout)
        self.assertEqual(self.counter_value(), "x")

    def test_a_duplicated_key_is_a_problem(self):
        """Mutant: lint's duplicate check removed."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 5\n"
                  "  decision: 7\n")
        r = self.wi("lint")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("counters: decision appears more than once", r.stdout)

    def test_digits_are_ascii(self):
        """A counter in another script's digits is not a whole number.
        Mutant: COUNTER_VALUE_RE back to \\d."""
        self.yaml("tracking: tracked\ncounters:\n  decision: ٣\n")
        r = self.wi("lint")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("must be a whole number", r.stdout)

    def test_conflict_markers_a_problem_and_no_reseed(self):
        body = ("tracking: tracked\ncounters:\n<<<<<<< HEAD\n"
                "  decision: 4\n=======\n  decision: 6\n>>>>>>> other\n")
        self.yaml(body)
        self.item("other-item-2222", notes="decision 9: by hand")
        before = self.snapshot()
        r = self.wi("lint")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("merge conflict markers", r.stdout)
        self.assertNotIn("reseeded", r.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_no_store_yaml_no_reseed(self):
        (self.root / "store.yaml").unlink()
        self.item("other-item-2222", notes="decision 7: by hand")
        r = self.ok("lint")
        self.assertNotIn("counter", r.stderr)
        self.assertFalse((self.root / "store.yaml").exists())


class TestInitKeepsTheBlock(CounterCase):

    def test_init_rerun_keeps_the_block(self):
        """Mutant: write_tracking's old body (the block dropped)."""
        self.yaml("tracking: tracked\ncounters:\n  decision: 12\n")
        self.ok("init", "--track")
        self.assertEqual(self.counter_value(), "12")
        self.assertEqual(wi.read_tracking(self.root), "tracked")

    def test_write_tracking_keeps_the_block(self):
        self.yaml("tracking: ignored\ncounters:\n  decision: 12\n"
                  "  other-thing: 3\n")
        wi.write_tracking(self.root, "tracked", repo="own")
        self.assertEqual(self.yaml_text().split("\n", 1)[1],
                         "tracking: tracked\nrepo: own\ncounters:\n"
                         "  decision: 12\n  other-thing: 3\n")

    def test_write_tracking_without_a_block_adds_none(self):
        wi.write_tracking(self.root, "tracked")
        self.assertNotIn("counters", self.yaml_text())


@unittest.skipUnless(GIT, "git not available")
class TestOwnRepo(CounterCase):

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "own" / ".work-items"
        r = self.wi("init", "--no-track", root=self.root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.item(IID)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "item")

    def git(self, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=self.root, env=self.env, capture_output=True, text=True,
            check=True)

    def head_files(self):
        return self.git("show", "--name-only", "--no-renames", "--format=",
                        "HEAD").stdout.split()

    def test_raise_is_one_commit_holding_item_and_counter(self):
        before = len(self.git("log", "--format=%s").stdout.splitlines())
        r = self.ok("raise", IID, "--", "q?")
        self.assertNotIn("not committed", r.stderr)
        log = self.git("log", "--format=%s").stdout.splitlines()
        self.assertEqual(len(log), before + 1)
        self.assertEqual(log[0], f"wi raise: {IID}")
        self.assertEqual(sorted(self.head_files()),
                         sorted([f"items/{IID}.md", "store.yaml"]))
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_lint_reseed_commits_the_counter(self):
        self.item("other-item-2222", notes="decision 7: by hand")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "by hand")
        r = self.ok("lint")
        self.assertIn("reseeded 0 \u2192 7", r.stderr)
        self.assertEqual(self.head_files(), ["store.yaml"])
        self.assertEqual(self.git("status", "--porcelain").stdout, "")


if __name__ == "__main__":
    unittest.main()
