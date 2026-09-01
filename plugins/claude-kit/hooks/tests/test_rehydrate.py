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


class TestStatuslineHeal(TestRehydrate):
    def heal_env(self, settings, marker=True):
        data = os.path.join(self.cfg.name, "plugins", "data", "claude-kit-x")
        os.makedirs(data, exist_ok=True)
        if marker:
            json.dump({"settings": settings, "command": "python3 /x/statusline.py"},
                      open(os.path.join(data, "statusline-installed.json"), "w"))
        env = dict(self.env)
        env.pop("CLAUDE_PLUGIN_DATA", None)
        return env

    def test_heal_restores_dropped_entry(self):
        # a stale session's settings write dropped statusLine (live-fired 2026-08-31)
        sp = os.path.join(self.cfg.name, "settings.json")
        json.dump({"model": "m"}, open(sp, "w"))
        rc, out = run_hook({"session_id": "s", "source": "startup", "cwd": self.repo},
                           self.heal_env(sp))
        self.assertIn("restored statusLine", out.get("systemMessage", ""))
        d = json.load(open(sp))
        self.assertEqual(d["statusLine"]["command"], "python3 /x/statusline.py")
        self.assertEqual(d["model"], "m")               # read-modify-write, not clobber

    def test_heal_leaves_present_entry_alone(self):
        sp = os.path.join(self.cfg.name, "settings.json")
        json.dump({"statusLine": {"type": "command", "command": "mine"}}, open(sp, "w"))
        rc, out = run_hook({"session_id": "s", "source": "startup", "cwd": self.repo},
                           self.heal_env(sp))
        self.assertNotIn("restored", out.get("systemMessage", ""))
        self.assertEqual(json.load(open(sp))["statusLine"]["command"], "mine")

    def test_heal_silent_without_marker(self):
        sp = os.path.join(self.cfg.name, "settings.json")
        json.dump({}, open(sp, "w"))
        rc, out = run_hook({"session_id": "s", "source": "startup", "cwd": self.repo},
                           self.heal_env(sp, marker=False))
        self.assertEqual(out, {})
        self.assertNotIn("statusLine", json.load(open(sp)))


if __name__ == "__main__":
    unittest.main()
