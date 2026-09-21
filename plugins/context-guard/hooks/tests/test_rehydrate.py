import json, os, subprocess, sys, tempfile, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)

MANIFEST = """---
handoff: 1
repo: demo
session: old
written: {written}
head: {head}
mode: {mode}
---
## Doing
Building the thing.

## Goal
mode: continue — operator: "finish phase 2"

## Read in full
a/plan.md — the plan

## Aware of
- REFUSED sudo for dd

## Next
wi show thing-1a2b

## Scrolls
{scrolls}
"""


def run_hook(payload, env):
    p = subprocess.run([sys.executable, os.path.join(HOOKS, "rehydrate.py")],
                       input=json.dumps(payload), capture_output=True,
                       text=True, env=env, timeout=30)
    return p.returncode, json.loads(p.stdout) if p.stdout.strip() else {}


class TestRehydrate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg.name)
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg.name
        global L, ledger
        import lib_context as L
        import ledger
        self.repo = self.tmp.name
        for c in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", "-C", self.repo, "-c", "user.email=t@t",
                            "-c", "user.name=t"] + c, check=True, capture_output=True)
        self.head = subprocess.run(["git", "-C", self.repo, "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()

    def tearDown(self):
        self.tmp.cleanup(); self.cfg.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def write_manifest(self, mode="continue", written=None, head=None, scrolls="- x.md — notes"):
        written = written or time.strftime("%Y-%m-%dT%H:%M:%SZ")
        open(os.path.join(self.repo, "HANDOFF.md"), "w").write(
            MANIFEST.format(written=written, head=head or self.head,
                            mode=mode, scrolls=scrolls))

    def hook(self, source, sid="s"):
        return run_hook({"session_id": sid, "source": source, "cwd": self.repo}, self.env)

    def ctx(self, out):
        return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")

    def test_silent_without_manifest(self):
        rc, out = self.hook("startup")
        self.assertEqual((rc, out), (0, {}))

    def test_compact_full_with_ledger_and_precedence(self):
        self.write_manifest()
        ledger.append("s", "X", "rejected the obvious fix")
        rc, out = self.hook("compact")
        c = self.ctx(out)
        for needle in ("FRESH", "## Doing", "REFUSED sudo", "Precedence:",
                       "rejected the obvious fix"):
            self.assertIn(needle, c)

    def test_resume_sha_gate(self):
        self.write_manifest()
        rc, out = self.hook("resume")
        self.assertIn("## Doing", self.ctx(out))       # first sight: full
        rc, out = self.hook("resume")
        c = self.ctx(out)
        self.assertNotIn("## Doing", c)                # unchanged: header only
        self.assertIn("manifest", c)
        self.write_manifest(scrolls="- y.md — changed")
        rc, out = self.hook("resume")
        self.assertIn("## Doing", self.ctx(out))       # changed: full again

    def test_startup_header_only(self):
        self.write_manifest()
        rc, out = self.hook("startup")
        c = self.ctx(out)
        self.assertNotIn("## Doing", c)
        self.assertIn("FRESH", c)

    def write_mode_skill(self, value, mode="continue"):
        self.write_manifest(mode=mode)
        p = os.path.join(self.repo, "HANDOFF.md")
        t = open(p).read().replace("mode: " + mode + "\n",
                                   "mode: " + mode + "\n" + value + "\n", 1)
        open(p, "w").write(t)

    def test_mode_skill_named_on_every_tier(self):
        self.write_mode_skill("mode_skill: /some-plugin:some-mode start  # re-enter")
        for source in ("startup", "clear", "compact"):
            rc, out = self.hook(source, sid=source)
            c = self.ctx(out)
            self.assertEqual(rc, 0)
            self.assertIn("FRESH", c)
            self.assertIn("re-enter it first with `/some-plugin:some-mode start`.",
                          c.split("\n")[0], source)

    def test_mode_skill_absent_or_invalid_is_silent(self):
        for value in ("", "mode_skill:", "mode_skill: not-a-command"):
            self.write_mode_skill(value)
            rc, out = self.hook("startup", sid="x" + str(len(value)))
            c = self.ctx(out)
            self.assertIn("FRESH", c)
            self.assertNotIn("standing mode", c)

    def test_mode_skill_not_named_when_landed(self):
        self.write_mode_skill("mode_skill: /some-plugin:some-mode start", mode="landed")
        rc, out = self.hook("startup")
        c = self.ctx(out)
        self.assertIn("LANDED", c)
        self.assertNotIn("standing mode", c)

    def test_stale_label_and_reconfirm(self):
        self.write_manifest(written="2026-01-01T00:00:00Z")
        rc, out = self.hook("compact")
        c = self.ctx(out)
        self.assertIn("STALE", c)
        self.assertIn("re-confirmed", c)

    def test_landed_mode(self):
        self.write_manifest(mode="landed")
        rc, out = self.hook("compact")
        self.assertIn("LANDED", self.ctx(out))

    def test_cap_and_trim_order(self):
        self.write_manifest(scrolls="\n".join(f"- f{i}.md — {'z' * 200}" for i in range(60)))
        rc, out = self.hook("compact")
        c = self.ctx(out)
        self.assertLess(len(c), 10_000)
        self.assertIn("trimmed", c)
        self.assertIn("## Read in full", c)            # mandatory tier survives

    def test_custom_instructions_replayed_once(self):
        self.write_manifest()
        st = L.load_state("s"); st["custom_instructions"] = "keep the auth thread"
        L.save_state("s", st)
        rc, out = self.hook("compact")
        self.assertIn("keep the auth thread", self.ctx(out))
        rc, out = self.hook("compact")
        self.assertNotIn("keep the auth thread", self.ctx(out))

    def test_empty_custom_instructions_consumed_too(self):
        self.write_manifest()
        for ci in ("", None):
            with self.subTest(ci=ci):
                st = L.load_state("s"); st["custom_instructions"] = ci
                L.save_state("s", st)
                self.hook("compact")
                self.assertNotIn("custom_instructions", L.load_state("s"))

    def test_sandbox_dir_preferred(self):
        os.makedirs(os.path.join(self.repo, ".claude-sandbox"))
        open(os.path.join(self.repo, ".claude-sandbox", "HANDOFF.md"), "w").write(
            MANIFEST.format(written=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            head=self.head, mode="continue", scrolls="- s.md — x"))
        self.write_manifest(scrolls="- root.md — should lose")
        rc, out = self.hook("compact")
        self.assertIn(".claude-sandbox", self.ctx(out))


class TestForkAdoption(TestRehydrate):
    def test_fork_adopts_parent_ledger_and_instructions(self):
        ledger.append("parent-sid", "X", "rejected the obvious fix")
        st = L.load_state("parent-sid"); st["custom_instructions"] = "keep the thread"
        L.save_state("parent-sid", st)
        tp = os.path.join(self.repo, "fork.jsonl")
        open(tp, "w").write(json.dumps({"type": "user", "sessionId": "parent-sid"}) + "\n"
                            + json.dumps({"type": "user", "sessionId": "child-sid"}) + "\n")
        self.write_manifest()
        rc, out = run_hook({"session_id": "child-sid", "source": "fork",
                            "cwd": self.repo, "transcript_path": tp}, self.env)
        led = open(L.ledger_path("child-sid")).read()
        self.assertIn("adopted from parent parent-sid", led)
        self.assertIn("rejected the obvious fix", led)
        self.assertEqual(L.load_state("child-sid")["custom_instructions"], "keep the thread")

    def test_fork_session_rewritten_sids_recovered_by_record_uuid(self):
        # --fork-session rewrites every copied record's sessionId to the child;
        # only the record uuids tie the transcripts together (live-fired 2026-09-01)
        ledger.append("parent2-sid", "D", "uuid-matched adoption marker")
        st = L.load_state("parent2-sid"); st["custom_instructions"] = "guidance-x"
        L.save_state("parent2-sid", st)
        rec = {"type": "user", "uuid": "shared-rec-uuid-1", "sessionId": "parent2-sid"}
        open(os.path.join(self.repo, "parent2-sid.jsonl"), "w").write(json.dumps(rec) + "\n")
        child_rec = dict(rec, sessionId="child3-sid")
        tp = os.path.join(self.repo, "child3-sid.jsonl")
        open(tp, "w").write(json.dumps(child_rec) + "\n")
        run_hook({"session_id": "child3-sid", "source": "fork",
                  "cwd": self.repo, "transcript_path": tp}, self.env)
        led = open(L.ledger_path("child3-sid")).read()
        self.assertIn("adopted from parent parent2-sid", led)
        self.assertIn("uuid-matched adoption marker", led)
        self.assertEqual(L.load_state("child3-sid")["custom_instructions"], "guidance-x")

    def test_fork_never_overwrites_own_ledger(self):
        ledger.append("child2", "D", "my own line")
        tp = os.path.join(self.repo, "fork.jsonl")
        open(tp, "w").write(json.dumps({"type": "user", "sessionId": "parent-sid"}) + "\n")
        run_hook({"session_id": "child2", "source": "fork",
                  "cwd": self.repo, "transcript_path": tp}, self.env)
        led = open(L.ledger_path("child2")).read()
        self.assertIn("my own line", led)
        self.assertNotIn("adopted", led)


def snapshot(path):
    """(bytes, mtime_ns, inode) of a file, or None when it is absent."""
    try:
        st = os.stat(path)
        with open(path, "rb") as f:
            return f.read(), st.st_mtime_ns, st.st_ino
    except FileNotFoundError:
        return None


class TestStatuslineHandover(TestRehydrate):
    """3c48 F4: context-guard never writes settings.json. The old heal and
    legacy migration are gone; a read-only "moved" notice replaces them."""

    def setUp(self):
        super().setUp()
        self.env = dict(self.env, HOME=self.cfg.name)
        self.env.pop("CLAUDE_PLUGIN_DATA", None)
        self.sp = os.path.join(self.cfg.name, "settings.json")

    def data_dir(self, name):
        d = os.path.join(self.cfg.name, "plugins", "data", name)
        os.makedirs(d, exist_ok=True)
        return d

    def cmd(self, plugin):
        return "python3 " + json.dumps(os.path.join(
            self.cfg.name, "plugins", "data", plugin, "current-hooks", "statusline.py"))

    def settings(self, d, path=None):
        with open(path or self.sp, "w") as f:
            json.dump(d, f, indent=4)
            f.write("\n")

    def marker(self, plugin, settings, command="python3 /x/statusline.py"):
        with open(os.path.join(self.data_dir(plugin), "statusline-installed.json"), "w") as f:
            json.dump({"settings": settings, "command": command}, f)

    def start(self, source="startup", sid="s"):
        rc, out = self.hook(source, sid)
        self.assertEqual(rc, 0)
        return out.get("systemMessage", "")

    def stamp(self):
        return os.path.join(self.cfg.name, "claude-kit", "context-gate",
                            ".statusline-moved-notice")

    # -- no settings write, in every state the old heal or migration acted on --

    def assert_untouched(self, setup):
        setup()
        before = snapshot(self.sp)
        for source in ("startup", "resume", "clear", "compact"):
            self.start(source)
            self.assertEqual(snapshot(self.sp), before, source)
        return before

    def test_dropped_entry_with_own_marker_is_not_restored(self):
        def setup():
            self.settings({"model": "m"})
            self.marker("context-guard-x", self.sp)
        self.assert_untouched(setup)
        self.assertNotIn("statusLine", json.load(open(self.sp)))

    def test_legacy_claude_kit_entry_is_not_migrated(self):
        def setup():
            self.settings({"model": "m", "statusLine": {
                "type": "command", "command": self.cmd("claude-kit-x")}})
            self.marker("claude-kit-x", self.sp, self.cmd("claude-kit-x"))
            self.data_dir("context-guard-x")
        self.assert_untouched(setup)
        # the legacy marker is not moved or deleted either
        self.assertTrue(os.path.exists(os.path.join(
            self.cfg.name, "plugins", "data", "claude-kit-x", "statusline-installed.json")))
        self.assertFalse(os.path.exists(os.path.join(
            self.cfg.name, "plugins", "data", "context-guard-x", "statusline-installed.json")))

    def test_no_settings_file_is_never_created(self):
        self.marker("context-guard-x", self.sp)
        self.start()
        self.assertIsNone(snapshot(self.sp))

    def test_no_hook_source_writes_settings(self):
        # the grep-level guarantee: no hook opens settings for writing
        import glob as g
        for f in g.glob(os.path.join(HOOKS, "*.py")):
            with open(f) as fh:
                src = fh.read()
            for bad in ("heal_statusline", "_restore_statusline",
                        "_migrate_legacy_statusline"):
                self.assertNotIn(bad, src, f)

    # -- the notice --

    def test_notice_when_deprecated_copy_is_active(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        before = snapshot(self.sp)
        msg = self.start()
        self.assertIn("moved to the `statusline` plugin", msg)
        self.assertIn("/plugin install statusline@kmacmcfarlane", msg)
        self.assertEqual(snapshot(self.sp), before)

    def test_notice_for_a_claude_kit_entry_too(self):
        self.settings({"statusLine": {"type": "command", "command": self.cmd("claude-kit-y")}})
        self.assertIn("moved to the `statusline` plugin", self.start())

    def test_notice_cadence_once_per_week(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        self.assertIn("moved", self.start("startup", "a"))
        for source, sid in (("startup", "b"), ("resume", "a"), ("clear", "c"),
                            ("compact", "a"), ("startup", "d")):
            self.assertNotIn("moved", self.start(source, sid), (source, sid))
        six_days = time.time() - 6 * 86400
        os.utime(self.stamp(), (six_days, six_days))
        self.assertNotIn("moved", self.start("startup", "e"))
        eight_days = time.time() - 8 * 86400
        os.utime(self.stamp(), (eight_days, eight_days))
        self.assertIn("moved", self.start("startup", "f"))
        self.assertNotIn("moved", self.start("startup", "g"))

    def test_notice_never_on_the_prompt_path(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        t = os.path.join(self.tmp.name, "t.jsonl")
        open(t, "w").close()
        for _ in range(3):
            p = subprocess.run([sys.executable, os.path.join(HOOKS, "context_warn.py")],
                               input=json.dumps({"session_id": "s", "prompt": "hi",
                                                 "transcript_path": t}),
                               capture_output=True, text=True, env=self.env, timeout=30)
            self.assertNotIn("moved", p.stdout)
        self.assertFalse(os.path.exists(self.stamp()))

    def test_future_stamp_does_not_silence_forever(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        os.makedirs(os.path.dirname(self.stamp()), exist_ok=True)
        open(self.stamp(), "w").close()
        future = time.time() + 365 * 86400
        os.utime(self.stamp(), (future, future))
        self.assertIn("moved", self.start())

    def test_unwritable_stamp_withholds_the_notice(self):
        # a stamp that cannot be dated (here a dangling symlink, which
        # O_NOFOLLOW refuses) must not turn into a notice every session
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        os.makedirs(os.path.dirname(self.stamp()), exist_ok=True)
        os.symlink(os.path.join(self.tmp.name, "nowhere"), self.stamp())
        old = time.time() - 30 * 86400
        os.utime(self.stamp(), (old, old), follow_symlinks=False)
        for sid in ("a", "b"):
            self.assertNotIn("moved", self.start("startup", sid))

    def test_silent_when_statusline_plugin_is_installed(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        d = self.data_dir("statusline-kmacmcfarlane")
        with open(os.path.join(d, "owner.json"), "w") as f:
            json.dump({"v": 1, "state": "installed", "settings": self.sp,
                       "command": self.cmd("statusline-kmacmcfarlane")}, f)
        before = snapshot(self.sp)
        self.assertEqual(self.start(), "")
        self.assertEqual(snapshot(self.sp), before)
        self.assertFalse(os.path.exists(self.stamp()))

    def test_silent_when_statusline_owns_the_entry(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("statusline-kmacmcfarlane")}})
        self.assertEqual(self.start(), "")

    def test_silent_for_a_foreign_entry_or_none(self):
        self.settings({"statusLine": {"type": "command", "command": "my-own-line.sh"}})
        self.assertEqual(self.start("startup", "a"), "")
        self.settings({"model": "m"})
        self.assertEqual(self.start("startup", "b"), "")
        os.remove(self.sp)
        self.assertEqual(self.start("startup", "c"), "")
        self.assertFalse(os.path.exists(self.stamp()))

    def test_notice_for_a_settings_file_a_marker_names(self):
        local = os.path.join(self.tmp.name, "settings.local.json")
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}}, local)
        self.marker("context-guard-x", local)
        before = snapshot(local)
        self.assertIn("moved", self.start())
        self.assertEqual(snapshot(local), before)

    def test_notice_joins_the_rehydration_message(self):
        self.settings({"statusLine": {"type": "command",
                                      "command": self.cmd("context-guard-x")}})
        self.write_manifest()
        msg = self.start("compact")
        self.assertIn("Rehydrated from", msg)
        self.assertIn("moved to the `statusline` plugin", msg)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "no FIFOs on this platform")
    def test_fifo_settings_neither_hangs_nor_notices(self):
        os.mkfifo(self.sp)
        self.assertEqual(self.start(), "")

    def test_garbage_settings_are_silent(self):
        for raw in ("{", "[]", json.dumps({"statusLine": "x"}),
                    json.dumps({"statusLine": {"command": 5}})):
            with open(self.sp, "w") as f:
                f.write(raw)
            self.assertEqual(self.start(), "", raw)


if __name__ == "__main__":
    unittest.main()
