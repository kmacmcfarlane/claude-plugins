"""rehydrate.py: current repo state outranks the manifest — DEAD CLAIM lines
for `items:` the store has closed, and `## Next` withheld once HEAD moves."""
import json, os, subprocess, sys, tempfile, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANIFEST = """---
handoff: 1
repo: demo
session: old
written: {written}
head: {head}
mode: continue
{items}---
## Doing
Building the thing.

## Goal
mode: continue — operator: "finish phase 2"

## Aware of
- REFUSED sudo for dd

## Next
wi show build-the-widget-aaaa

## Scrolls
- x.md — notes
"""


def put(path, text, mode="w"):
    with open(path, mode) as fh:
        fh.write(text)


ITEM = "---\nid: {id}\ntitle: t\ntype: chore\nstatus: {status}\n---\nbody\n"


class TestRehydrateStale(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg.name)
        self.env.pop("WI_ROOT", None)
        self.env.pop("CLAUDE_PLUGIN_DATA", None)
        self.repo = self.tmp.name
        self.g("init", "-q")
        self.commit("base")
        self.head = self.rev()

    def tearDown(self):
        self.tmp.cleanup(); self.cfg.cleanup()

    def g(self, *args):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.email=t@t",
                               "-c", "user.name=t"] + list(args), check=True,
                              capture_output=True, text=True).stdout.strip()

    def rev(self):
        return self.g("rev-parse", "--short", "HEAD")

    def commit(self, msg, path=None):
        if path:
            full = os.path.join(self.repo, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            put(full, msg + "\n", "a")
            self.g("add", path)
            self.g("commit", "-q", "-m", msg)
        else:
            self.g("commit", "-q", "--allow-empty", "-m", msg)

    def item(self, iid, status, archived=False):
        d = os.path.join(self.repo, ".claude-sandbox", "work",
                         "archive/2026" if archived else "items")
        os.makedirs(d, exist_ok=True)
        os.makedirs(os.path.join(self.repo, ".claude-sandbox", "work", "items"),
                    exist_ok=True)
        put(os.path.join(d, iid + ".md"), ITEM.format(id=iid, status=status))

    def manifest(self, items="", head=None):
        os.makedirs(os.path.join(self.repo, ".claude-sandbox"), exist_ok=True)
        put(os.path.join(self.repo, ".claude-sandbox", "HANDOFF.md"),
            MANIFEST.format(written=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            head=head or self.head, items=items))

    def hook(self, source="compact", env=None):
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "rehydrate.py")],
                           input=json.dumps({"session_id": "s", "source": source,
                                             "cwd": self.repo}),
                           capture_output=True, text=True, env=env or self.env,
                           timeout=30)
        out = json.loads(p.stdout) if p.stdout.strip() else {}
        return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")

    # ── DEAD CLAIM ──────────────────────────────────────────────────────────
    def test_dead_claims_listed_live_ones_not(self):
        self.item("build-the-widget-aaaa", "done")
        self.item("fix-the-gadget-bbbb", "doing")
        self.item("old-idea-cccc", "dropped", archived=True)
        self.manifest("items:\n  - build-the-widget-aaaa\n  - fix-the-gadget-bbbb\n"
                      "  - old-idea-cccc\n  - vanished-dddd\n")
        c = self.hook()
        self.assertIn("DEAD CLAIM build-the-widget-aaaa (done)", c)
        self.assertIn("DEAD CLAIM old-idea-cccc (dropped)", c)
        self.assertIn("DEAD CLAIM vanished-dddd (missing)", c)
        self.assertNotIn("fix-the-gadget-bbbb (", c)

    def test_inline_list_and_prefix_ids(self):
        self.item("build-the-widget-aaaa", "done")
        self.manifest("items: [build-the-widget, fix-x]\n")
        c = self.hook()
        self.assertIn("DEAD CLAIM build-the-widget (done)", c)
        self.assertIn("DEAD CLAIM fix-x (missing)", c)

    def test_dead_claims_in_header_only_tier(self):
        self.item("build-the-widget-aaaa", "done")
        self.manifest("items:\n  - build-the-widget-aaaa\n")
        c = self.hook("startup")
        self.assertNotIn("## Doing", c)
        self.assertIn("DEAD CLAIM build-the-widget-aaaa (done)", c)

    def test_wi_root_env_wins(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        os.makedirs(os.path.join(other.name, "items"))
        put(os.path.join(other.name, "items", "zz-1111.md"),
            ITEM.format(id="zz-1111", status="done"))
        self.item("zz-1111", "doing")          # repo store says doing; env says done
        self.manifest("items:\n  - zz-1111\n")
        c = self.hook(env=dict(self.env, WI_ROOT=other.name))
        self.assertIn("DEAD CLAIM zz-1111 (done)", c)

    def test_no_store_is_silent(self):
        self.manifest("items:\n  - build-the-widget-aaaa\n")
        c = self.hook()
        self.assertIn("## Doing", c)
        self.assertNotIn("DEAD CLAIM", c)

    def test_no_items_key_is_silent(self):
        self.item("build-the-widget-aaaa", "done")
        self.manifest()
        self.assertNotIn("DEAD CLAIM", self.hook())

    # ── Next withheld ───────────────────────────────────────────────────────
    def test_next_shown_at_recorded_head(self):
        self.manifest()
        c = self.hook()
        self.assertIn("wi show build-the-widget-aaaa", c)
        self.assertNotIn("Next withheld", c)

    def test_next_withheld_after_code_commit(self):
        self.manifest()
        self.commit("code", "src/a.txt")
        self.commit("code2", "src/b.txt")
        c = self.hook()
        self.assertNotIn("wi show build-the-widget-aaaa", c)
        self.assertIn(f"Next withheld: head moved 2 commits since this manifest "
                      f"({self.head}..{self.rev()}); run wi prime and git log.", c)
        for keep in ("## Doing", "## Aware of", "REFUSED sudo", "## Scrolls"):
            self.assertIn(keep, c)

    def test_withheld_line_once_in_full_and_in_header_tier(self):
        self.manifest()
        self.commit("code", "src/a.txt")
        self.assertEqual(self.hook().count("Next withheld"), 1)
        self.assertIn("Next withheld", self.hook("startup"))

    def test_store_only_commits_do_not_count(self):
        self.manifest()
        self.commit("chore", ".claude-sandbox/work/items/x.md")
        self.commit("chore2", ".claude-sandbox/work/items/y.md")
        c = self.hook()
        self.assertIn("wi show build-the-widget-aaaa", c)
        self.assertNotIn("Next withheld", c)

    def test_mixed_commits_count_only_code(self):
        self.manifest()
        self.commit("chore", ".claude-sandbox/work/items/x.md")
        self.commit("code", "src/a.txt")
        self.assertIn("head moved 1 commits", self.hook())

    def test_next_withheld_when_not_ancestor(self):
        self.commit("side", "src/side.txt")
        side = self.rev()
        self.g("reset", "-q", "--hard", self.head)
        self.commit("main", "src/main.txt")
        self.manifest(head=side)
        c = self.hook()
        self.assertIn("Next withheld", c)
        self.assertIn("not an ancestor", c)
        self.assertNotIn("wi show build-the-widget-aaaa", c)

    def test_unknown_head_withheld(self):
        self.manifest(head="deadbee")
        c = self.hook()
        self.assertIn("Next withheld: head moved ? commits", c)

    # ── precedence ──────────────────────────────────────────────────────────
    def test_precedence_puts_repo_state_over_manifest(self):
        self.manifest()
        c = self.hook()
        self.assertIn("current repo state (git log, the work-item store) beats "
                      "this manifest", c)
        self.assertIn("beat any machine summary", c)


if __name__ == "__main__":
    unittest.main()
