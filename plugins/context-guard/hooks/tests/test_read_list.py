"""5039 H6: the manifest's Read-in-full list, followed through. rehydrate.py
records it on a full injection of our own manifest, lineage.py marks
whole-file Reads, context_warn.py names the unread ones once on the next
prompt. Temp CLAUDE_CONFIG_DIRs only (test_lineage.Base)."""
import os, sys, unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_lineage as TL

LINE = "Read in full, not yet read this session"


class Base(TL.Base):
    def setUp(self):
        super().setUp()
        global L, RL, W
        import lib_context as L
        import read_list as RL
        import context_warn as W
        self.W = W
        os.makedirs(os.path.join(self.repo, "docs"))
        self.a = os.path.join(self.repo, "docs", "a.md")
        self.b = os.path.join(self.repo, "docs", "b.md")
        for p in (self.a, self.b):
            TL.writef(p, "x\n")

    def manifest(self, sid="X", lines=None, mode="handoff"):
        self.checkpoint(sid, mode=mode)
        lines = lines if lines is not None else [
            f"- {self.a} — the plan", "- `docs/b.md` — the ledger digest"]
        t = TL.readf(self.path).replace(
            "## Aware of", "## Read in full\n" + "\n".join(lines) + "\n\n## Aware of", 1)
        TL.writef(self.path, t)

    def prompt(self, sid, text="go on", **extra):
        out = self._run(self.W, dict({"session_id": sid, "prompt": text,
                                      "cwd": self.repo, "transcript_path": "",
                                      "hook_event_name": "UserPromptSubmit"}, **extra))
        return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")

    def pending(self, sid):
        return L.load_state(sid).get(RL.KEY)


class TestRecord(Base):
    def test_full_own_injection_records_existing_paths(self):
        self.manifest(lines=[f"- {self.a} — why", "- docs/b.md — why",
                             "- docs/missing.md — gone", "≤5 paths, one per line"])
        self.start("X", "compact")
        rec = self.pending("X")
        self.assertEqual([p["path"] for p in rec["paths"]], [self.a, self.b])
        self.assertEqual(rec["read"], [])

    def test_linked_clear_records_the_list(self):
        # H5: a linked /clear takes the full tier, so it records the list too.
        self.manifest()
        self.clear("X", "S")
        rec = self.pending("S")
        self.assertEqual([p["path"] for p in rec["paths"]], [self.a, self.b])
        self.assertIn(LINE, self.prompt("S"))

    def test_unlinked_clear_records_nothing(self):
        self.key = None
        self.manifest()
        self.clear("X", "S")
        self.assertIsNone(self.pending("S"))

    def test_foreign_manifest_records_nothing(self):
        self.manifest(sid="Y")
        self.start("B", "compact")
        self.assertIsNone(self.pending("B"))
        self.assertNotIn(LINE, self.prompt("B"))

    def test_header_only_injection_records_nothing(self):
        self.manifest()
        self.start("X", "startup")
        self.assertIsNone(self.pending("X"))

    def test_no_section_records_nothing(self):
        self.manifest(lines=[])
        self.start("X", "compact")
        self.assertIsNone(self.pending("X"))


class TestReminder(Base):
    def test_one_read_names_the_other_exactly_once(self):
        self.manifest()
        self.start("X", "compact")
        self.read("X", self.a)
        c = self.prompt("X")
        self.assertIn(LINE, c)
        self.assertIn(self.b, c)
        self.assertNotIn(self.a, c)
        self.assertNotIn(LINE, self.prompt("X"))
        self.assertIsNone(self.pending("X"))

    def test_all_read_is_silent(self):
        self.manifest()
        self.start("X", "compact")
        self.read("X", self.a)
        self.read("X", "docs/b.md")          # relative to cwd, by realpath
        self.assertIsNone(self.pending("X"))
        self.assertEqual(self.prompt("X"), "")

    def test_partial_read_does_not_count(self):
        self.manifest()
        self.start("X", "compact")
        self.read("X", self.a, offset=1)
        self.read("X", self.b, limit=10)
        c = self.prompt("X")
        self.assertIn(self.a, c)
        self.assertIn(self.b, c)

    def test_read_through_symlink_matches_by_realpath(self):
        self.manifest()
        self.start("X", "compact")
        link = os.path.join(self.repo, "alias.md")
        os.symlink(self.a, link)
        self.read("X", link)
        c = self.prompt("X")
        self.assertNotIn(self.a, c)
        self.assertIn(self.b, c)

    def test_subagent_read_does_not_count(self):
        self.manifest()
        self.start("X", "compact")
        self._run(TL.G, {"session_id": "X", "hook_event_name": "PostToolUse",
                         "tool_name": "Read", "cwd": self.repo, "agent_id": "a1",
                         "tool_input": {"file_path": self.a}})
        self.assertIn(self.a, self.prompt("X"))

    def test_subagent_prompt_is_silent_and_does_not_consume(self):
        self.manifest()
        self.start("X", "compact")
        self.assertNotIn(LINE, self.prompt("X", agent_id="a1"))
        self.assertIn(LINE, self.prompt("X"))

    def test_whitelisted_prompt_does_not_consume(self):
        self.manifest()
        self.start("X", "compact")
        for cmd in ("/clear", "/context-guard:checkpoint", "/compact keep it"):
            self.assertNotIn(LINE, self.prompt("X", cmd))
        self.assertIn(LINE, self.prompt("X"))

    def test_hard_stop_does_not_consume(self):
        self.manifest()
        self.start("X", "compact")
        with mock.patch.object(self.W, "decide", lambda *a, **k: "hard"), \
                mock.patch.object(self.W.L, "measure", lambda *a, **k: {
                    "tokens": 990_000, "window": 1_000_000, "pct": 99.0,
                    "source": "exact", "note": "", "block_window": 1_000_000}), \
                mock.patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                self.prompt("X")
        self.assertIsNotNone(self.pending("X"))
        self.assertIn(LINE, self.prompt("X"))

    def test_joins_the_gate_advisory(self):
        self.manifest()
        self.start("X", "compact")
        with mock.patch.object(self.W, "decide", lambda *a, **k: "band"), \
                mock.patch.object(self.W.L, "measure", lambda *a, **k: {
                    "tokens": 700_000, "window": 1_000_000, "pct": 70.0,
                    "source": "exact", "note": "", "block_window": 1_000_000}):
            c = self.prompt("X")
        self.assertIn("70% of the window is used", c)
        self.assertIn(LINE, c)

    def test_each_injection_reminds_once(self):
        self.manifest()
        self.start("X", "compact")
        self.read("X", self.a)
        self.read("X", self.b)
        self.start("X", "compact")            # a second compaction: reads are gone
        c = self.prompt("X")
        self.assertIn(self.a, c)
        self.assertIn(self.b, c)
        self.assertNotIn(LINE, self.prompt("X"))

    def test_malformed_record_keeps_the_gate(self):
        bad = [{"paths": [{"path": self.a, "real": [1]}], "read": 5},
               {"paths": [{"path": self.a, "real": self.a}], "read": 5},
               {"paths": "x"}, "garbage", {"paths": [{"path": self.a}], "read": [[1]]}]
        band = {"tokens": 700_000, "window": 1_000_000, "pct": 70.0,
                "source": "exact", "note": "", "block_window": 1_000_000}
        for i, rec in enumerate(bad):
            with self.subTest(rec=rec):
                sid = f"M{i}"
                L.update_state(sid, lambda st: st.__setitem__(RL.KEY, rec))
                with mock.patch.object(self.W.L, "measure", lambda *a, **k: band):
                    c = self.prompt(sid)
                self.assertIn("70% of the window is used", c)
                st = L.load_state(sid)
                self.assertEqual(st.get("prompt_n"), 1)       # the write completed
                self.assertNotIn(RL.KEY, st)

    def test_take_never_raises(self):
        class Boom(dict):
            def pop(self, *a):
                raise RuntimeError("x")
        self.assertEqual(RL.take(Boom({RL.KEY: 1})), [])

    def test_malformed_record_read_is_harmless(self):
        L.update_state("X", lambda st: st.__setitem__(
            RL.KEY, {"paths": [{"path": self.a, "real": os.path.realpath(self.a)},
                               {"path": self.b, "real": [2]}], "read": 5}))
        self.read("X", self.a)
        self.assertIsNone(self.pending("X"))

    def test_no_injection_no_line(self):
        self.assertEqual(self.prompt("fresh"), "")


class TestParse(Base):
    def test_shapes(self):
        t = ("## Read in full\n"
             f"1. `{self.a}` — ticked, numbered\n"
             "* docs/b.md:12 — line suffix\n"
             f"- {self.a}, again — deduplicated\n"
             "- docs/\x1bb.md — control character\n"
             "## Next\n- docs/b.md — another section\n")
        got = RL.paths_from_manifest(t, self.repo)
        self.assertEqual([p["path"] for p in got], [self.a, self.b])

    def test_garbage_is_empty(self):
        self.assertEqual(RL.paths_from_manifest(None, self.repo), [])
        self.assertEqual(RL.paths_from_manifest("no section", self.repo), [])

    def test_fenced_heading_is_not_the_section(self):
        t = ("## Doing\n```markdown\n## Read in full\n- docs/b.md — example\n```\n"
             "## Read in full\n- docs/a.md — real\n~~~\n- docs/b.md — fenced\n~~~\n"
             "## Next\n")
        got = RL.paths_from_manifest(t, self.repo)
        self.assertEqual([p["path"] for p in got], [self.a])

    def test_directory_is_skipped(self):
        t = "## Read in full\n- docs — a directory\n"
        self.assertEqual(RL.paths_from_manifest(t, self.repo), [])

    def test_tab_headings_are_headings(self):
        # "##" then a tab opens the section and ends it, as "## " does.
        t = ("## Doing\n- docs/b.md — not the section\n"
             "##\tRead in full\n- docs/a.md — listed\n"
             "##\tNext\n- docs/b.md — another section\n")
        self.assertEqual([p["path"] for p in RL.paths_from_manifest(t, self.repo)],
                         [self.a])
        self.assertEqual(RL.fence_note(t), "")

    def test_normal_manifest_is_unchanged(self):
        # Pinned: the list a normal manifest yields, and no note.
        t = ("---\nmode: handoff\n---\n## Doing\nx\n```sh\nls\n```\n"
             "## Read in full\n1. `docs/a.md` — plan\n\n- docs/b.md:3 — digest\n"
             "## Next\n- docs/a.md\n")
        self.assertEqual(RL.section_lines(t),
                         ["1. `docs/a.md` — plan", "- docs/b.md:3 — digest"])
        self.assertEqual(RL.paths_from_manifest(t, self.repo),
                         [{"path": self.a, "real": os.path.realpath(self.a)},
                          {"path": self.b, "real": os.path.realpath(self.b)}])
        self.assertEqual(RL.fence_note(t), "")

    def test_unclosed_fence_hiding_the_section_says_so(self):
        t = ("## Doing\nx\n```sh\nls\n\n## Read in full\n- docs/a.md — hidden\n"
             "## Next\n")
        self.assertEqual(RL.paths_from_manifest(t, self.repo), [])
        note = RL.fence_note(t)
        self.assertIn("never closed", note)
        self.assertIn("line 3", note)

    def test_closed_fence_or_no_section_is_silent(self):
        for t in ("## Doing\n```\n## Read in full\n- docs/a.md\n```\n",
                  "## Doing\n```\nno heading here\n",
                  "## Read in full\n- docs/a.md\n```\nunclosed after it\n",
                  None, 7):
            self.assertEqual(RL.fence_note(t), "", t)

    def test_injection_carries_the_fence_note(self):
        self.manifest()
        TL.writef(self.path, TL.readf(self.path).replace(
            "Building the thing.", "Building the thing.\n```text\nls", 1))
        out = self.start("X", "compact")
        self.assertIsNone(self.pending("X"))
        self.assertIn("is never closed", out)

    def _stale_next(self, doing_fence):
        # Next sits before Read in full and HEAD moves on, so rehydrate
        # withholds (rewrites) the Next body before reading the list.
        self.checkpoint("X", mode="handoff")
        t = TL.readf(self.path)
        head, _, _ = t.partition("## Aware of")
        if doing_fence:
            head = head.replace("Building the thing.", "Building the thing.\n```sh", 1)
        TL.writef(self.path, head + "## Next\n" + ("" if doing_fence else "```sh\n")
                  + f"wi show thing-1a2b\n## Read in full\n- {self.a} — plan\n\n"
                  "## Aware of\n- x\n")
        TL.writef(os.path.join(self.repo, "code.py"), "x = 1\n")
        self.git("add", "code.py")
        self.git("commit", "-q", "-m", "code")
        return self.start("X", "compact")

    def test_withheld_next_holding_the_fence_is_no_note(self):
        # The fence opener lives in the withheld Next: the list the read-list
        # hook reads is not hidden, so it is recorded and nothing says otherwise.
        out = self._stale_next(doing_fence=False)
        self.assertIn("Next withheld", out)
        self.assertNotIn("is never closed", out)
        self.assertEqual([p["path"] for p in self.pending("X")["paths"]], [self.a])

    def test_withheld_next_keeps_the_files_line_number(self):
        out = self._stale_next(doing_fence=True)
        raw = TL.readf(self.path).split("\n")
        self.assertIn("Next withheld", out)
        self.assertIsNone(self.pending("X"))
        self.assertIn(f"line {raw.index('```sh') + 1} ", out)

    def test_line_numbers_count_newlines_only(self):
        t = "## Doing\fx\u2028y\r\n```\n## Read in full\n- docs/a.md\n"
        self.assertIn("line 2 ", RL.fence_note(t))

    def test_normal_injection_has_no_fence_note(self):
        self.manifest()
        self.assertNotIn("is never closed", self.start("X", "compact"))


if __name__ == "__main__":
    unittest.main()
