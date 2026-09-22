"""H2 (d0eb): the ledger re-injected after compaction keeps reasoning lines
(R/C/D/X/U/Q, every epoch) ahead of the machine-written P pointers, inside the
unchanged 2,500-char budget, and never rewrites the ledger file."""
import os, subprocess, sys, tempfile, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_rehydrate import MANIFEST, run_hook  # noqa: E402


class LedgerCase(unittest.TestCase):
    def setUp(self):
        self.cfg = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg.name)
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg.name
        global L, ledger
        import lib_context as L
        import ledger

    def tearDown(self):
        self.cfg.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def read(self, sid):
        with open(L.ledger_path(sid)) as fh:
            return fh.read()

    def write(self, sid, text):
        with open(L.ledger_path(sid), "w") as fh:
            fh.write(text)

    def shaped(self, sid="s", pointers=60):
        """0c7eafc7-shaped: a refusal and decisions in epoch 0, then epochs
        crowded with commit pointers, a little reasoning in the newest."""
        out = [f"# ledger {sid}",
               "- R refused sudo for dd on the operator's disk",
               "- D the gate stands down only on a recorded checkpoint",
               "- C corrected: the manifest stamp is UTC, not local"]
        n = 0
        for e in (1, 2, 3):
            out += ["", f"## epoch {e} — 2026-09-2{e} 10:00:00 — 800,000 tok"]
            for _ in range(pointers // 3):
                n += 1
                out.append(f"- P commit {n:07x}: merged: some-feature-branch-name-{n} -> "
                           f"/home/rt/work/src/github.com/kmacmcfarlane/claude-plugins")
            if e == 2:
                out.append("- X rejected moving the ledger into the repo")
        out += ["- Q does the tee survive a /clear?",
                "- U unverified: the hub prunes dead sessions daily"]
        text = "\n".join(out) + "\n"
        self.write(sid, text)
        return text


class TestDigest(LedgerCase):
    def test_missing_and_empty(self):
        self.assertEqual(ledger.digest("nobody"), "")
        self.write("e", "# ledger e\n\n## epoch 1 — x — 0 tok\n")
        self.assertEqual(ledger.digest("e"), "")

    def test_small_ledger_whole_in_file_order(self):
        self.write("s", "# ledger s\n- D one\n- P commit a: x\n\n## epoch 1 — t — 5 tok\n- X two\n")
        d = ledger.digest("s", budget=2500)
        self.assertEqual(d, "- D one\n- P commit a: x\n\n## epoch 1 — t — 5 tok\n- X two")

    def test_reasoning_from_every_epoch_before_pointers(self):
        text = self.shaped()
        d = ledger.digest("s", budget=2500)
        self.assertLessEqual(len(d), 2500)
        for needle in ("- R refused sudo", "- D the gate stands down", "- C corrected",
                       "- X rejected moving", "- Q does the tee", "- U unverified"):
            self.assertIn(needle, d)
        # The old raw tail kept none of epoch 0 and was mostly pointers.
        self.assertNotIn("- R refused", ledger.tail("s", max_chars=2500))
        body = [l for l in d.splitlines() if l.startswith("- ")]
        p = [l for l in body if l.startswith("- P ")]
        self.assertEqual(len(body) - len(p), 6)
        self.assertLess(len(p), 60)
        # The pointers kept are the newest ones.
        self.assertIn("some-feature-branch-name-60 ", d)
        self.assertNotIn("some-feature-branch-name-1 ", d)
        # Closing line counts what was left out and names the file.
        last = d.splitlines()[-1]
        self.assertIn("pointer line(s) left out", last)
        self.assertIn(L.ledger_path("s"), last)
        self.assertNotIn("reasoning and", last)
        # The ledger file itself is untouched.
        self.assertEqual(self.read("s"), text)

    def test_file_order_and_epoch_headers(self):
        self.shaped()
        lines = ledger.digest("s", budget=2500).splitlines()
        body = [l for l in lines if l.startswith(("- ", "## "))]
        self.assertEqual(body[:3], ["- R refused sudo for dd on the operator's disk",
                                    "- D the gate stands down only on a recorded checkpoint",
                                    "- C corrected: the manifest stamp is UTC, not local"])
        # Epoch 2 holds only its X line; its header precedes it, readable.
        i = lines.index("- X rejected moving the ledger into the repo")
        self.assertTrue(lines[i - 1].startswith("## epoch 2"))
        self.assertEqual(lines[i - 2], "")
        # Headers appear only above kept lines and never twice.
        heads = [l for l in lines if l.startswith("## ")]
        self.assertEqual(len(heads), len(set(heads)))
        for h in heads:
            nxt = lines[lines.index(h) + 1]
            self.assertTrue(nxt.startswith("- "), h)

    def test_only_pointers_still_inject(self):
        self.write("p", "# ledger p\n" + "".join(
            f"- P commit {i:07x}: merged: branch-{i} -> /some/long/repo/path/for/padding\n"
            for i in range(200)))
        d = ledger.digest("p", budget=2500)
        self.assertLessEqual(len(d), 2500)
        self.assertIn("branch-199 ", d)
        self.assertIn("pointer line(s) left out", d)
        self.assertNotIn("reasoning", d.splitlines()[-1].split(" left out")[0])

    def test_reasoning_over_budget_keeps_rc_and_newest(self):
        lines = ["# ledger r", "- R the one refusal from epoch zero"]
        lines += [f"- D decision number {i} with some padding text to take room" for i in range(200)]
        lines += [f"- P commit {i:07x}: x" for i in range(20)]
        self.write("r", "\n".join(lines) + "\n")
        d = ledger.digest("r", budget=2500)
        self.assertLessEqual(len(d), 2500)
        self.assertIn("- R the one refusal", d)
        self.assertIn("decision number 199 ", d)
        self.assertNotIn("decision number 0 ", d)
        self.assertNotIn("- P ", d)
        self.assertIn("reasoning and 20 pointer line(s) left out", d)

    def test_hand_written_lines_count_as_reasoning(self):
        lines = ["# ledger h", "note: the operator wants no push until decision 52"]
        lines += [f"- P commit {i:07x}: merged: branch-{i} -> /some/long/repo/path" for i in range(200)]
        self.write("h", "\n".join(lines) + "\n")
        self.assertIn("no push until decision 52", ledger.digest("h", budget=2500))


    def test_rc_capped_at_half_the_room_when_d_lines_wait(self):
        # R/C text alone is over the whole budget; D lines are present too.
        lines = ["# ledger h"]
        for i in range(60):
            lines.append(f"- R refusal {i:02d} padded out to about sixty characters.")
            lines.append(f"- D decision {i:02d} padded out to about sixty characters")
        self.write("h", "\n".join(lines) + "\n")
        d = ledger.digest("h", budget=2500)
        self.assertLessEqual(len(d), 2500)
        room = 2500 - 200 - len(L.ledger_path("h"))
        r = [l for l in d.splitlines() if l.startswith("- R ")]
        dd = [l for l in d.splitlines() if l.startswith("- D ")]
        self.assertTrue(dd, "no D line kept: R/C took the whole room")
        self.assertLessEqual(sum(len(l) + 1 for l in r), room // 2)
        self.assertGreater(sum(len(l) + 1 for l in r), room // 2 - 70)
        self.assertIn("- R refusal 59 ", d)             # newest R kept
        self.assertNotIn("- R refusal 00 ", d)          # oldest R dropped
        self.assertIn("- D decision 59 ", d)

    def test_overlong_line_cut_not_dropped(self):
        lines = ["# ledger o", "- C " + "corrected " * 400]
        lines += [f"- P commit {i:07x}: merged: branch-{i} -> /some/long/repo/path" for i in range(80)]
        self.write("o", "\n".join(lines) + "\n")
        d = ledger.digest("o", budget=2500)
        self.assertLessEqual(len(d), 2500)
        c = [l for l in d.splitlines() if l.startswith("- C ")]
        self.assertEqual(len(c), 1)
        self.assertTrue(c[0].endswith(" [cut]"))

    def test_small_budget_is_never_exceeded(self):
        self.shaped()
        for budget in (0, 1, 50, 120, 200, 300, 600, 1000):
            self.assertLessEqual(len(ledger.digest("s", budget=budget)), budget, budget)
        self.assertIn("left out", ledger.digest("s", budget=300))

    def test_hash_lines_other_than_the_title_are_kept(self):
        lines = ["# ledger k (successor of 0c7eafc7)"]
        lines += [f"- P commit {i:07x}: merged: branch-{i} -> /some/long/repo/path" for i in range(200)]
        self.write("k", "\n".join(lines) + "\n")
        d = ledger.digest("k", budget=2500)
        self.assertEqual(d.splitlines()[0], "# ledger k (successor of 0c7eafc7)")
        self.write("t", "# ledger t\n- D one\n")
        self.assertEqual(ledger.digest("t"), "- D one")

class TestCompactInjection(LedgerCase):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        for c in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", "-C", self.repo, "-c", "user.email=t@t",
                            "-c", "user.name=t"] + c, check=True, capture_output=True)
        head = subprocess.run(["git", "-C", self.repo, "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        with open(os.path.join(self.repo, "HANDOFF.md"), "w") as fh:
            fh.write(MANIFEST.format(
                written=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), head=head,
                mode="continue", scrolls="- x.md — notes"))

    def tearDown(self):
        self.tmp.cleanup()
        super().tearDown()

    def ctx(self, source):
        rc, out = run_hook({"session_id": "s", "source": source, "cwd": self.repo}, self.env)
        self.assertEqual(rc, 0)
        return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")

    def test_compact_carries_epoch_zero_reasoning(self):
        text = self.shaped()
        c = self.ctx("compact")
        self.assertIn("reasoning kept ahead of commit pointers", c)
        led = c.split("[context-guard ledger", 1)[1]
        self.assertIn("- R refused sudo for dd", led)
        self.assertIn("- C corrected: the manifest stamp", led)
        self.assertIn("pointer line(s) left out", led)
        self.assertLessEqual(len(led.split("]\n", 1)[1].split("\n\nThe operator")[0]), 2500)
        self.assertEqual(self.read("s"), text)

    def test_ledger_not_injected_on_startup(self):
        self.shaped()
        self.assertNotIn("refused sudo for dd", self.ctx("startup"))


if __name__ == "__main__":
    unittest.main()
