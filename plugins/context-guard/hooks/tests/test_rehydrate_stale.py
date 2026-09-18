"""rehydrate.py: current repo state outranks the manifest — DEAD CLAIM lines
for `items:` the store has closed, and `## Next` withheld once HEAD moves."""
import importlib, json, os, subprocess, sys, tempfile, time, unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANIFEST = """---
handoff: 1
repo: demo
session: old
written: {written}
head: {head}
mode: {mode}
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


ITEM = "---\nid: {id}\ntitle: t\ntype: chore\nstatus: {status}\n{extra}---\nbody\n"


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

    def item(self, iid, status, archived=False, extra=""):
        d = os.path.join(self.repo, ".claude-sandbox", "work",
                         "archive/2026" if archived else "items")
        os.makedirs(d, exist_ok=True)
        os.makedirs(os.path.join(self.repo, ".claude-sandbox", "work", "items"),
                    exist_ok=True)
        put(os.path.join(d, iid + ".md"), ITEM.format(id=iid, status=status, extra=extra))

    def manifest(self, items="", head=None, mode="continue", written=None):
        os.makedirs(os.path.join(self.repo, ".claude-sandbox"), exist_ok=True)
        put(os.path.join(self.repo, ".claude-sandbox", "HANDOFF.md"),
            MANIFEST.format(written=written or time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            head=head or self.head, items=items, mode=mode))

    def hook(self, source="compact", env=None, timeout=30):
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "rehydrate.py")],
                           input=json.dumps({"session_id": "s", "source": source,
                                             "cwd": self.repo}),
                           capture_output=True, text=True, env=env or self.env,
                           timeout=timeout)
        self.assertEqual(p.returncode, 0, p.stderr)
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
            ITEM.format(id="zz-1111", status="done", extra=""))
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
        self.assertIn("head moved 1 commit since", self.hook())

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
        self.assertIn("recorded head not found locally", c)
        self.assertNotIn("not an ancestor", c)

    # ── robustness (review round 1) ─────────────────────────────────────────
    def test_template_comment_and_entry_comments_stripped(self):
        self.item("build-the-widget-aaaa", "done")
        self.item("ok-1111", "doing")
        self.manifest("items:            # optional: wi ids you expect open\n"
                      "  - build-the-widget-aaaa  # the widget\n"
                      "  - ok-1111 # note\n")
        c = self.hook()
        self.assertIn("DEAD CLAIM build-the-widget-aaaa (done)", c)
        self.assertNotIn("DEAD CLAIM #", c)
        self.assertNotIn("ok-1111", c.split("---")[0])   # no claim line for it
        self.assertNotIn("DEAD CLAIM ok-1111", c)

    def test_alias_resolves(self):
        self.item("long-live-item-eeee", "doing", extra="alias: live\n")
        self.item("long-dead-item-ffff", "done", extra="alias: gone\n")
        self.manifest("items: [live, gone]\n")
        c = self.hook()
        self.assertNotIn("DEAD CLAIM live", c)
        self.assertIn("DEAD CLAIM gone (done)", c)

    def test_malformed_items_not_dead_claims(self):
        self.item("ok-1111", "doing")
        for val in ("{a: b}", "-", ": weird", "[ok-1111, , 'ok-1111'"):
            with self.subTest(val=val):
                self.manifest(f"items: {val}\n")
                c = self.hook()
                self.assertNotIn("DEAD CLAIM", c)
        self.manifest("items: {a: b}\n")
        self.assertIn("items: 1 unparseable entry skipped", self.hook())

    def test_huge_items_list_capped_and_doing_survives(self):
        self.item("x-0", "doing")
        self.manifest("items:\n" + "".join(f"  - gone-{i:04d}-{'z' * 20}\n"
                                            for i in range(3000)))
        c = self.hook()
        self.assertLess(len(c), 10_000)
        for keep in ("## Doing", "## Goal", "Building the thing."):
            self.assertIn(keep, c)
        self.assertIn("(+30 more)", c)                  # 50 read, 20 shown

    def test_landed_skips_both_checks(self):
        self.item("build-the-widget-aaaa", "done")
        self.manifest("items:\n  - build-the-widget-aaaa\n", mode="landed")
        self.commit("code", "src/a.txt")
        c = self.hook()
        self.assertIn("LANDED", c)
        self.assertNotIn("DEAD CLAIM", c)
        self.assertNotIn("Next withheld", c)

    def test_hanging_git_never_fails_the_hook(self):
        shim = tempfile.TemporaryDirectory()
        self.addCleanup(shim.cleanup)
        put(os.path.join(shim.name, "git"), "#!/bin/sh\nsleep 30\n")
        os.chmod(os.path.join(shim.name, "git"), 0o755)
        self.item("build-the-widget-aaaa", "done")
        self.manifest("items:\n  - build-the-widget-aaaa\n")
        env = dict(self.env, PATH=shim.name + os.pathsep + self.env.get("PATH", ""))
        t0 = time.time()
        c = self.hook(env=env, timeout=40)
        self.assertLess(time.time() - t0, 15)           # one 5s wait, not one per call
        self.assertIn("## Doing", c)                    # rehydration survives
        self.assertNotIn("Next withheld", c)
        self.assertIn("FRESH (git unavailable) manifest", c.split("\n", 1)[0])

    def test_git_timeout_in_process(self):
        self.env_patch = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.cfg.name})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        sys.path.insert(0, HOOKS)
        self.addCleanup(sys.path.remove, HOOKS)
        rh = importlib.import_module("rehydrate")
        self.addCleanup(rh._git_hung.clear)
        boom = subprocess.TimeoutExpired("git", 5)
        with mock.patch.object(rh.subprocess, "run", side_effect=boom) as run:
            self.assertEqual(rh.stale_checks({"head": self.head}, self.repo, "FRESH"),
                             (None, [], []))
            self.assertIsNone(rh.git(self.repo, "status"))
            self.assertEqual(run.call_count, 1)

    # ── liveness ignores store chores ───────────────────────────────────────
    def test_store_chores_do_not_age_the_manifest(self):
        self.manifest()
        for i in range(31):
            self.commit(f"chore {i}", ".claude-sandbox/work/items/x.md")
        c = self.hook("startup")
        self.assertIn("FRESH", c)
        self.commit("code", "src/a.txt")
        self.assertIn("AGED", self.hook("startup"))

    # ── round-2 lows (4a19) ─────────────────────────────────────────────────
    def header(self, c):
        return c.split("\n", 1)[0]

    def test_missing_head_labelled_aged_not_fresh(self):
        self.manifest(head="deadbee")
        for src in ("startup", "compact"):
            with self.subTest(source=src):
                c = self.hook(src)
                self.assertIn("AGED (recorded head not found locally) manifest",
                              self.header(c))
                self.assertNotIn("FRESH", self.header(c))
                self.assertIn("Next withheld: head moved ? commits", c)

    def test_rewound_head_labelled_aged_not_fresh(self):
        self.commit("code", "src/a.txt")
        ahead = self.rev()
        self.manifest(head=ahead)
        self.g("reset", "-q", "--hard", self.head)
        c = self.hook()
        self.assertIn("AGED (recorded head is not an ancestor) manifest", self.header(c))
        self.assertNotIn("FRESH", self.header(c))
        self.assertIn(f"Next withheld: head moved 0 commits ahead, 1 behind since this "
                      f"manifest ({ahead}..{self.head}, recorded head is not an "
                      f"ancestor); run wi prime and git log.", c)
        self.assertNotIn("wi show build-the-widget-aaaa", c)

    def diverge(self, n_main=1):
        """Recorded head on a side branch; HEAD gains n_main code commits."""
        self.commit("side", "src/side.txt")
        self.commit("side store chore", ".claude-sandbox/work/items/s.md")
        side = self.rev()
        self.g("reset", "-q", "--hard", self.head)
        for i in range(n_main):
            self.commit(f"main {i}", f"src/main{i}.txt")
        return side

    def test_diverged_branch_labelled_aged_with_ahead_behind(self):
        side = self.diverge(2)
        self.manifest(head=side)
        c = self.hook()
        self.assertIn("AGED (recorded head is not an ancestor) manifest", self.header(c))
        self.assertIn(f"Next withheld: head moved 2 commits ahead, 1 behind since this "
                      f"manifest ({side}..{self.rev()}, recorded head is not an "
                      f"ancestor); run wi prime and git log.", c)

    def test_diverged_one_commit_singular(self):
        side = self.diverge(1)
        self.manifest(head=side)
        self.assertIn("head moved 1 commit ahead, 1 behind since", self.hook())

    def test_stale_with_reason_on_drift(self):
        side = self.diverge(31)
        self.manifest(head=side)
        c = self.hook()
        self.assertIn("STALE (recorded head is not an ancestor) manifest", self.header(c))
        self.assertIn("head moved 31 commits ahead, 1 behind since", c)
        self.assertIn("must be re-confirmed with the operator", c)

    def test_stale_with_reason_on_age(self):
        self.manifest(head="deadbee", written="2020-01-01T00:00:00Z")
        c = self.hook("startup")
        self.assertIn("STALE (recorded head not found locally) manifest", self.header(c))
        self.assertIn("head moved ? commits since", c)

    def test_plain_stale_on_age_has_no_reason(self):
        self.manifest(written="2020-01-01T00:00:00Z")
        c = self.hook("startup")
        self.assertIn("STALE manifest", self.header(c))

    def test_git_failing_labelled_unverified_not_fresh(self):
        shim = tempfile.TemporaryDirectory()
        self.addCleanup(shim.cleanup)
        put(os.path.join(shim.name, "git"), "#!/bin/sh\nexit 1\n")
        os.chmod(os.path.join(shim.name, "git"), 0o755)
        self.manifest()
        env = dict(self.env, PATH=shim.name + os.pathsep + self.env.get("PATH", ""))
        c = self.hook(env=env)
        self.assertIn("FRESH (git unavailable) manifest", self.header(c))
        self.assertIn("wi show build-the-widget-aaaa", c)  # documented degrade
        self.assertNotIn("Next withheld", c)
        self.manifest(written="2020-01-01T00:00:00Z")
        self.assertIn("STALE (git unavailable) manifest", self.header(self.hook(env=env)))

    def test_liveness_unverified_only_with_recorded_head(self):
        rh = self.rh()
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.assertEqual(rh.liveness({"written": now, "head": "abc"}, None),
                         ("FRESH", "git unavailable"))
        self.assertEqual(rh.liveness({"written": now}, None), ("FRESH", None))

    def test_label_fresh_only_when_next_shown(self):
        self.manifest()
        c = self.hook()
        self.assertIn("FRESH manifest", self.header(c))
        self.assertNotIn("Next withheld", c)
        self.commit("code", "src/a.txt")
        c = self.hook()
        self.assertIn("AGED manifest", self.header(c))    # plain drift: no reason
        self.assertIn("head moved 1 commit since", c)

    def test_unparseable_line_has_its_own_heading(self):
        self.item("ok-1111", "doing")
        self.manifest("items: {a: b}\n")
        for src in ("compact", "startup"):
            with self.subTest(source=src):
                c = self.hook(src)
                self.assertIn("items: 1 unparseable entry skipped", c)
                self.assertIn("not checked against the store", c)
                self.assertNotIn("contradicts", c)

    def test_unparseable_line_not_under_contradicts_heading(self):
        self.item("build-the-widget-aaaa", "done")
        self.manifest("items: [build-the-widget-aaaa, 'x y']\n")
        c = self.hook()
        i = c.index("contradicts (the store wins):")
        block = c[i:c.index("\n\n", i)]
        self.assertIn("DEAD CLAIM build-the-widget-aaaa (done)", block)
        self.assertNotIn("unparseable", block)
        j = c.index("not checked against the store:")
        self.assertIn("items: 1 unparseable entry skipped", c[j:].split("\n\n")[0])

    def rh(self):
        sys.path.insert(0, HOOKS)
        self.addCleanup(sys.path.remove, HOOKS)
        return importlib.import_module("rehydrate")

    def test_trim_items_only_inside_frontmatter(self):
        rh = self.rh()
        body_items = "## Doing\nitems:\n  - keep-me-in-the-body\n"
        no_fm_items = "---\nhead: abc\n---\n" + body_items
        self.assertEqual(rh._trim_items(no_fm_items), no_fm_items)
        with_fm = "---\nhead: abc\nitems:\n  - a-1\n  - b-2\n---\n" + body_items
        out = rh._trim_items(with_fm)
        self.assertIn("items: (trimmed — read the manifest file)\n---\n", out)
        self.assertNotIn("a-1", out)
        self.assertTrue(out.endswith(body_items))
        self.assertEqual(rh._trim_items(body_items), body_items)   # no frontmatter

    def test_trim_items_crlf_frontmatter(self):
        rh = self.rh()
        crlf = "---\r\nhead: abc\r\nitems:\r\n  - a-1\r\n  - b-2\r\n---\r\n" \
            "## Doing\r\nitems:\r\n  - keep-me\r\n"
        out = rh._trim_items(crlf)
        self.assertIn("items: (trimmed — read the manifest file)\r\n---\r\n", out)
        self.assertNotIn("a-1", out)
        self.assertTrue(out.endswith("## Doing\r\nitems:\r\n  - keep-me\r\n"))

    def test_body_items_survive_hook_trim(self):
        self.manifest()
        path = os.path.join(self.repo, ".claude-sandbox", "HANDOFF.md")
        with open(path) as fh:
            text = fh.read()
        text = text.replace(
            "Building the thing.\n", "Building the thing.\nitems:\n  - keep-me-body\n")
        text = text.replace("- x.md — notes\n", "".join(
            f"- s{i:04d}.md — {'n' * 60}\n" for i in range(200)))
        put(path, text)
        c = self.hook()
        self.assertIn("## Scrolls\n(trimmed", c)                # trim ran
        self.assertIn("items:\n  - keep-me-body", c)
        self.assertNotIn("items: (trimmed", c)

    # ── precedence ──────────────────────────────────────────────────────────
    def test_precedence_puts_repo_state_over_manifest(self):
        self.manifest()
        c = self.hook()
        self.assertIn("current repo state (git log, the work-item store) beats "
                      "this manifest", c)
        self.assertIn("beat any machine summary", c)
        self.assertIn("beat everything else, including your own recollection", c)


if __name__ == "__main__":
    unittest.main()
