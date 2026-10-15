"""Tests for a work-item store that is its own git repo (d1e9 F1): telling
the store's .git apart (own, unrecorded, dedicated, missing, broken, old),
the hardened store git runner, custody through it, and the store-repo rows
of `prime` and `lint`.

Every git call here runs in a temp dir: HOME is a temp dir, the global
config is a temp file (GIT_CONFIG_GLOBAL), GIT_CONFIG_NOSYSTEM=1, and
GIT_CEILING_DIRECTORIES is the temp dir, so neither the machine's config
nor a repo around the temp dir is ever read. Marker scripts prove that no
hook, fsmonitor or clean filter runs: each test that relies on one first
shows the marker firing under plain git, then that it stays silent under
the runner, `wi prime` and `wi lint`.
"""
import contextlib
import fcntl
import importlib.util
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"

spec = importlib.util.spec_from_file_location("wi_store_repo", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

GIT = shutil.which("git")


def git_version():
    if not GIT:
        return (0,)
    out = subprocess.run(["git", "--version"], capture_output=True,
                         text=True).stdout
    m = re.search(r"(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0,)


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

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
"""


@unittest.skipUnless(GIT, "git not available")
class StoreRepoCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="d1e9f1-")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        home = self.tmp / "home"
        home.mkdir()
        self.gitconfig = home / "gitconfig"
        self.gitconfig.write_text("")
        self.marks = self.tmp / "marks"
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("GIT_", "WI_", "WORK_ITEMS_"))}
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home),
                   GIT_CONFIG_GLOBAL=str(self.gitconfig),
                   GIT_CONFIG_NOSYSTEM="1",
                   GIT_CEILING_DIRECTORIES=str(self.tmp),
                   WORK_ITEMS_OWNER="tester@local")
        env.pop("EMAIL", None)
        self.env = env
        patcher = mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    # -- helpers ---------------------------------------------------------

    def git(self, cwd, *args, check=True, env=None):
        full = dict(self.env, **(env or {}))
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(args),
            cwd=cwd, env=full, capture_output=True, text=True, check=check)

    def wi(self, args, root, env=None):
        full = dict(self.env, WORK_ITEMS_ROOT=str(root))
        full.update(env or {})
        return subprocess.run([sys.executable, str(WI)] + args, env=full,
                              capture_output=True, text=True)

    def marker(self, name, passthrough=False):
        """An executable script that appends its name to the marks file;
        a filter's copy also passes its stdin through."""
        path = self.tmp / "bin" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"#!/bin/sh\necho {name} >> '{self.marks}'\n"
                        + ("cat\n" if passthrough else ""))
        path.chmod(0o755)
        return path

    def marked(self):
        return self.marks.read_text().split() if self.marks.exists() else []

    def clear_marks(self):
        if self.marks.exists():
            self.marks.unlink()

    def store_files(self, store, own=True, items=("one-aaaa",)):
        (store / "items").mkdir(parents=True, exist_ok=True)
        (store / "README.md").write_text("# Work items\n")
        (store / ".gitignore").write_text(".lock\n*.tmp*\n")
        (store / "store.yaml").write_text(
            "tracking: tracked\n" + ("repo: own\n" if own else ""))
        for iid in items:
            (store / "items" / f"{iid}.md").write_text(ITEM.format(iid=iid))

    def make_host(self, name="host", ignore=True):
        host = self.tmp / name
        host.mkdir()
        self.git(host, "init", "-q")
        if ignore:
            (host / ".gitignore").write_text("/.work-items/\n")
        (host / "src.txt").write_text("host file\n")
        self.git(host, "add", "-A")
        self.git(host, "commit", "-q", "-m", "host")
        return host

    def make_own(self, host=True, own=True, commit=True):
        """A store at <host>/.work-items with its own repo, committed."""
        base = self.make_host() if host else self.tmp / "nohost"
        base.mkdir(exist_ok=True)
        store = base / ".work-items"
        self.store_files(store, own=own)
        self.git(store, "init", "-q", "--template=")
        if commit:
            self.git(store, "add", "-A")
            self.git(store, "commit", "-q", "-m", "init")
        return store

    def state(self, store):
        return wi.store_repo_state(store)


class TestDetection(StoreRepoCase):
    """d1e9 D1: what a store's .git is."""

    def test_plain_store_makes_no_git_call(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=False)
        with mock.patch.object(wi.subprocess, "run") as run:
            rs = self.state(store)
        self.assertEqual(rs.state, "plain")
        run.assert_not_called()

    def test_dir_git_own(self):
        store = self.make_own()
        rs = self.state(store)
        self.assertEqual(rs.state, "own", rs.reason)
        self.assertEqual(rs.git_dir, str(store / ".git"))
        self.assertEqual(rs.host, self.tmp / "host")

    def test_own_outside_any_repo(self):
        rs = self.state(self.make_own(host=False))
        self.assertEqual(rs.state, "own", rs.reason)
        self.assertIsNone(rs.host)

    def test_unrecorded_needs_a_host(self):
        self.assertEqual(self.state(self.make_own(own=False)).state,
                         "unrecorded")

    def test_dedicated_top_of_repo_store(self):
        self.assertEqual(
            self.state(self.make_own(host=False, own=False)).state,
            "dedicated")

    def test_missing(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=True)
        self.assertEqual(self.state(store).state, "missing")

    def test_git_file_inside_store_is_valid(self):
        self.make_host()
        store = self.tmp / "host" / ".work-items"
        self.store_files(store)
        self.git(self.tmp, "init", "-q", "--template=",
                 f"--separate-git-dir={store / 'gitdata'}", str(store))
        self.assertTrue((store / ".git").is_file())
        self.assertEqual(self.state(store).state, "own")

    def test_git_file_to_host_worktree_points_outside(self):
        host = self.make_host()
        wt = self.tmp / "wt"
        self.git(host, "worktree", "add", "-q", "--detach", str(wt))
        store = host / ".work-items"
        self.store_files(store)
        shutil.copy(wt / ".git", store / ".git")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(".git points outside the store", rs.reason)
        self.assertIn(str(host / ".git"), rs.reason)

    def test_absorbed_submodule_git_file_points_outside(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        (host / ".git" / "modules").mkdir()
        self.git(self.tmp, "init", "-q", "--template=",
                 f"--separate-git-dir={host / '.git' / 'modules' / 'store'}",
                 str(store))
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(".git points outside the store", rs.reason)

    def test_bare_git_is_broken(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        self.git(self.tmp, "init", "-q", "--bare", str(store / ".git"))
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("bare", rs.reason)

    def test_empty_git_is_broken_and_never_reaches_the_host(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        (store / ".git").mkdir()
        head = (host / ".git" / "HEAD").read_bytes()
        index = (host / ".git" / "index").read_bytes()
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("not a usable repository", rs.reason)
        r = wi._store_git(store, "add", "-A", "--", "items")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((host / ".git" / "HEAD").read_bytes(), head)
        self.assertEqual((host / ".git" / "index").read_bytes(), index)

    def test_symlink_git_inside_is_valid(self):
        store = self.make_own()
        (store / ".git").rename(store / "gitreal")
        (store / ".git").symlink_to("gitreal")
        self.assertEqual(self.state(store).state, "own")

    def test_symlink_git_outside_is_broken(self):
        host = self.make_host()
        other = self.tmp / "other"
        other.mkdir()
        self.git(other, "init", "-q")
        store = host / ".work-items"
        self.store_files(store)
        (store / ".git").symlink_to(other / ".git")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("points outside", rs.reason)

    def test_old_location_git(self):
        self.make_host()
        store = self.tmp / "host" / ".work"
        self.store_files(store)
        self.git(store, "init", "-q", "--template=")
        self.assertEqual(self.state(store).state, "old")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("holds a git repo at an old location", r.stdout)
        self.assertIn("Moving a store", r.stdout)


class TestAttributes(StoreRepoCase):
    """d1e9 D1'': an attribute file makes an own or own-unrecorded store
    broken; wi runs no filter it names."""

    def filtered_store(self, own=True):
        store = self.make_own(own=own)
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        return store

    def assert_broken_and_silent(self, store, path):
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn(f"{path} selects git attributes", rs.reason)
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        for cmd in (["prime"], ["lint"]):
            r = self.wi(cmd, store)
            self.assertIn("selects git attributes", r.stdout)
        self.assertEqual(self.wi(["lint"], store).returncode, 3)
        self.assertEqual(self.marked(), [])

    def test_info_attributes(self):
        store = self.filtered_store()
        info = store / ".git" / "info"
        info.mkdir()
        (info / "attributes").write_text("* filter=mark\n")
        # control: plain git runs that filter
        (store / "items" / "x.md").write_text("x\n")
        self.git(store, "add", "items/x.md")
        self.assertIn("clean", self.marked())
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        (store / "items" / "x.md").unlink()
        self.clear_marks()
        self.assert_broken_and_silent(store, ".git/info/attributes")

    def test_root_gitattributes(self):
        store = self.filtered_store()
        (store / ".gitattributes").write_text("* filter=mark\n")
        self.assert_broken_and_silent(store, ".gitattributes")

    def test_deeper_gitattributes(self):
        store = self.filtered_store()
        (store / "items" / "sub").mkdir()
        (store / "items" / "sub" / ".gitattributes").write_text(
            "* filter=mark\n")
        self.assert_broken_and_silent(store, "items/sub/.gitattributes")

    def test_index_only_gitattributes(self):
        store = self.make_own()
        (store / ".gitattributes").write_text("* filter=mark\n")
        self.git(store, "add", ".gitattributes")
        (store / ".gitattributes").unlink()
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        self.assert_broken_and_silent(store, ".gitattributes")

    def test_unrecorded_store_with_attributes_is_broken(self):
        store = self.filtered_store(own=False)
        (store / ".gitattributes").write_text("* filter=mark\n")
        self.assertEqual(self.state(store).state, "broken")

    def test_dedicated_store_keeps_its_attributes(self):
        store = self.make_own(host=False, own=False)
        (store / ".gitattributes").write_text("*.md text\n")
        self.assertEqual(self.state(store).state, "dedicated")
        r = self.wi(["lint"], store)
        self.assertNotIn("attributes", r.stdout + r.stderr)

    def test_global_attributes_file_runs_no_filter(self):
        store = self.make_own()
        filt = self.marker("clean", passthrough=True)
        attrs = self.tmp / "home" / "attributes"
        attrs.write_text("* filter=mark\n")
        self.git(self.tmp, "config", "--global", "core.attributesFile",
                 str(attrs))
        self.git(self.tmp, "config", "--global", "filter.mark.clean",
                 str(filt))
        (store / "items" / "x.md").write_text("x\n")
        # control: plain git reads the global attributes file
        self.git(store, "add", "items/x.md")
        self.assertIn("clean", self.marked())
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        self.clear_marks()
        self.assertEqual(self.state(store).state, "own")
        r = wi._store_git(store, "add", "--", "items/x.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        for cmd in (["prime"], ["lint"]):
            self.wi(cmd, store)
        self.assertEqual(self.marked(), [])

    @unittest.skipIf(git_version() < (2, 41),
                     "git below 2.41 does not read GIT_ATTR_SOURCE")
    def test_attr_source_env_is_scrubbed(self):
        store = self.make_own()
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        attrs = self.tmp / "attrs"
        attrs.mkdir()
        (attrs / ".gitattributes").write_text("* filter=mark\n")
        blob = subprocess.run(
            ["git", "hash-object", "-w", str(attrs / ".gitattributes")],
            cwd=store, env=self.env, capture_output=True, text=True,
            check=True).stdout.strip()
        tree = subprocess.run(
            ["git", "mktree"], cwd=store, env=self.env, capture_output=True,
            text=True, check=True,
            input=f"100644 blob {blob}\t.gitattributes\n").stdout.strip()
        (store / "items" / "x.md").write_text("x\n")
        self.git(store, "add", "items/x.md", env={"GIT_ATTR_SOURCE": tree})
        self.assertIn("clean", self.marked())      # control
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        self.clear_marks()
        with mock.patch.dict(os.environ, {"GIT_ATTR_SOURCE": tree}):
            r = wi._store_git(store, "add", "--", "items/x.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marked(), [])

    @unittest.skipIf(git_version() < (2, 43),
                     "git below 2.43 does not read attr.tree")
    def test_attr_tree_in_store_config_is_pinned_empty(self):
        store = self.make_own()
        filt = self.marker("clean", passthrough=True)
        self.git(store, "config", "filter.mark.clean", str(filt))
        attrs = self.tmp / "attrs"
        attrs.mkdir()
        (attrs / ".gitattributes").write_text("* filter=mark\n")
        blob = subprocess.run(
            ["git", "hash-object", "-w", str(attrs / ".gitattributes")],
            cwd=store, env=self.env, capture_output=True, text=True,
            check=True).stdout.strip()
        tree = subprocess.run(
            ["git", "mktree"], cwd=store, env=self.env, capture_output=True,
            text=True, check=True,
            input=f"100644 blob {blob}\t.gitattributes\n").stdout.strip()
        self.git(store, "config", "attr.tree", tree)
        (store / "items" / "x.md").write_text("x\n")
        self.git(store, "add", "items/x.md")
        self.assertIn("clean", self.marked())      # control
        self.git(store, "rm", "-q", "--cached", "items/x.md")
        self.clear_marks()
        r = wi._store_git(store, "add", "--", "items/x.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marked(), [])


class TestRunner(StoreRepoCase):
    """d1e9 D2: the hardened store runner."""

    def commit_via_runner(self, store, msg="runner"):
        (store / "items" / "two-bbbb.md").write_text(ITEM.format(iid="two-bbbb"))
        r = wi._store_git(store, "add", "-A", "--", "items")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = wi._store_git(store, "-c", "user.name=t", "-c", "user.email=t@t",
                          "commit", "-q", "-m", msg, "--", "items")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_no_hook_or_fsmonitor_runs(self):
        store = self.make_own()
        hooks = self.tmp / "hooks"
        hooks.mkdir()
        for name in ("pre-commit", "post-commit", "commit-msg"):
            shutil.copy(self.marker(f"global-{name}"), hooks / name)
        self.git(self.tmp, "config", "--global", "core.hooksPath", str(hooks))
        # control: plain git runs the global hooks
        (store / "items" / "c.md").write_text("c\n")
        self.git(store, "add", "items/c.md")
        self.git(store, "commit", "-q", "-m", "control")
        self.assertIn("global-pre-commit", self.marked())
        self.clear_marks()
        (store / ".git" / "hooks").mkdir(exist_ok=True)
        shutil.copy(self.marker("store-pre-commit"),
                    store / ".git" / "hooks" / "pre-commit")
        shutil.copy(self.marker("root-pre-commit"), store / "pre-commit")
        self.git(store, "config", "core.fsmonitor",
                 str(self.marker("fsmonitor")))
        self.commit_via_runner(store)
        wi._store_git(store, "status", "--porcelain")
        self.assertEqual(self.marked(), [])
        (store / "pre-commit").unlink()
        for cmd in (["prime"], ["lint"]):
            self.wi(cmd, store)
        self.assertEqual(self.marked(), [])

    def test_fsmonitor_control_and_prime_lint(self):
        store = self.make_own()
        self.git(store, "config", "core.fsmonitor",
                 str(self.marker("fsmonitor")))
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        self.git(store, "status", "--porcelain")
        self.assertIn("fsmonitor", self.marked())   # control
        self.clear_marks()
        (store / ".gitignore").write_text(".lock\n*.tmp*\nitems/\n")
        for cmd in (["prime"], ["lint"]):
            self.wi(cmd, store)
        self.assertEqual(self.marked(), [])

    def test_gpg_sign_with_missing_gpg_still_commits(self):
        store = self.make_own()
        self.git(self.tmp, "config", "--global", "commit.gpgSign", "true")
        self.git(self.tmp, "config", "--global", "gpg.program",
                 str(self.tmp / "no-such-gpg"))
        (store / "items" / "c.md").write_text("c\n")
        self.git(store, "add", "items/c.md")
        r = self.git(store, "commit", "-q", "-m", "control", check=False)
        self.assertNotEqual(r.returncode, 0)          # control
        self.commit_via_runner(store)

    def test_host_hook_env_acts_on_the_store(self):
        store = self.make_own()
        host = self.tmp / "host"
        host_index = (host / ".git" / "index").read_bytes()
        with mock.patch.dict(os.environ, {
                "GIT_DIR": str(host / ".git"),
                "GIT_WORK_TREE": str(host),
                "GIT_INDEX_FILE": str(host / ".git" / "index")}):
            r = wi._store_git(store, "rev-parse", "--show-toplevel")
            self.assertEqual(r.stdout.strip(), str(store))
            self.commit_via_runner(store)
        log = self.git(store, "log", "--format=%s").stdout.split()
        self.assertEqual(log[0], "runner")
        self.assertEqual((host / ".git" / "index").read_bytes(), host_index)

    def test_env_and_argv(self):
        store = self.make_own()
        seen = {}

        def fake(argv, **kw):
            seen.setdefault("calls", []).append((argv, kw["env"], kw["cwd"]))
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        with mock.patch.dict(os.environ, {"GIT_LITERAL_PATHSPECS": "1",
                                          "GIT_ATTR_SOURCE": "HEAD",
                                          "GIT_OBJECT_DIRECTORY": "/x",
                                          "GIT_ICASE_PATHSPECS": "1",
                                          "GIT_GLOB_PATHSPECS": "1",
                                          "GIT_NOGLOB_PATHSPECS": "1"}), \
                mock.patch.object(wi.subprocess, "run", fake):
            wi._store_git(store, "status")
            wi._store_git(store, "check-ignore", "-q", "items")
        (argv, env, cwd), (argv2, env2, _) = seen["calls"]
        self.assertEqual(cwd, str(store))
        for pin in ("core.hooksPath=/dev/null", "core.fsmonitor=false",
                    "commit.gpgSign=false", "gc.auto=0",
                    "maintenance.auto=false", "core.attributesFile=/dev/null",
                    f"attr.tree={wi.EMPTY_TREE}"):
            self.assertIn(pin, argv)
        self.assertEqual(argv[-1], "status")
        self.assertEqual(env["GIT_CEILING_DIRECTORIES"], str(store.parent))
        self.assertEqual(env["GIT_ATTR_NOSYSTEM"], "1")
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["LC_ALL"], "C")
        self.assertEqual(env["GIT_LITERAL_PATHSPECS"], "1")
        self.assertNotIn("GIT_ATTR_SOURCE", env)
        self.assertNotIn("GIT_OBJECT_DIRECTORY", env)
        for name in ("GIT_ICASE_PATHSPECS", "GIT_GLOB_PATHSPECS",
                     "GIT_NOGLOB_PATHSPECS"):
            self.assertNotIn(name, env)
            self.assertNotIn(name, env2)
        self.assertNotIn("GIT_LITERAL_PATHSPECS", env2)
        self.assertEqual(argv2[-3:], ["check-ignore", "-q", "items"])


class TestNestedRepo(StoreRepoCase):
    """Review round 1: git status recurses into a gitlink, where the nested
    repo's own config and attributes are not pinned."""

    def nested(self):
        store = self.make_own()
        sub = store / "items" / "sub"
        sub.mkdir()
        self.git(sub, "init", "-q", "--template=")
        (sub / "f.txt").write_text("one\n")
        self.git(sub, "add", "f.txt")
        self.git(sub, "commit", "-q", "-m", "sub")
        self.git(store, "add", "items/sub")
        self.git(store, "commit", "-q", "-m", "gitlink")
        (sub / ".git" / "info").mkdir()
        (sub / ".git" / "info" / "attributes").write_text("* filter=mark\n")
        self.git(sub, "config", "filter.mark.clean",
                 str(self.marker("clean", passthrough=True)))
        (sub / "f.txt").write_text("two\n")
        return store, sub

    def test_nested_repo_filter_never_runs(self):
        store, _ = self.nested()
        self.git(store, "status", "--porcelain")
        self.assertIn("clean", self.marked())      # control
        self.clear_marks()
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/sub/.git is a nested git repo or gitlink",
                      rs.reason)
        for cmd in (["prime"], ["lint"]):
            r = self.wi(cmd, store)
            self.assertIn("nested git repo or gitlink", r.stdout)
        # the status call itself never recurses, whatever the state says
        wi._uncommitted(store)
        self.assertEqual(self.marked(), [])

    def test_index_only_gitlink_is_broken(self):
        store, sub = self.nested()
        shutil.rmtree(sub)
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/sub is a nested git repo or gitlink", rs.reason)

    def test_git_file_below_root_is_broken(self):
        store = self.make_own()
        (store / "items" / ".git").write_text("gitdir: /nowhere\n")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/.git is a nested git repo", rs.reason)

    def test_gitattributes_name_is_case_blind(self):
        store = self.make_own()
        (store / "items" / ".GitAttributes").write_text("* filter=mark\n")
        rs = self.state(store)
        self.assertEqual(rs.state, "broken")
        self.assertIn("items/.GitAttributes selects git attributes",
                      rs.reason)


class TestEdges(StoreRepoCase):
    """Review round 1: a ceiling that would split, a read-only store."""

    def test_pathsep_in_parent_reads_as_unknown(self):
        base = self.tmp / "a:b"
        base.mkdir()
        store = base / ".work-items"
        self.store_files(store)
        self.git(store, "init", "-q", "--template=")
        self.assertIsNone(wi._store_git(store, "status"))
        self.assertEqual(self.state(store).state, "unknown")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    @unittest.skipIf(os.geteuid() == 0, "root ignores file modes")
    def test_read_only_store_lint_skips_uncommitted(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        store.chmod(0o555)
        self.addCleanup(store.chmod, 0o755)
        r = self.wi(["lint"], store)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("uncommitted check skipped", r.stderr)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestCustody(StoreRepoCase):
    """d1e9 D6': custody's reads run through the runner in an own store."""

    def test_items_rule_in_own_store_gitignore_is_named(self):
        store = self.make_own()
        (store / ".gitignore").write_text(".lock\n*.tmp*\nitems/\n")
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn(".gitignore:3 'items/'", r.stdout)
        self.assertNotIn("--no-track", r.stdout)
        r = self.wi(["prime"], store)
        self.assertIn(".gitignore:3 'items/'", r.stdout)

    def test_custody_goes_through_the_runner(self):
        store = self.make_own()
        calls = []
        real = wi._store_git

        def spy(*a, **kw):
            calls.append(a[1:3])
            return real(*a, **kw)

        with mock.patch.object(wi, "_store_git", spy):
            wi.custody_warning(store)
        self.assertIn(("check-ignore", "-v"), calls)


class TestChecks(StoreRepoCase):
    """d1e9 D6: the store-repo rows of lint and prime."""

    def lint(self, store, code=0):
        r = self.wi(["lint"], store)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r

    def test_clean_own_store(self):
        store = self.make_own()
        r = self.lint(store)
        self.assertIn("lint clean: 1 items", r.stdout)
        self.assertEqual(r.stderr, "")
        r = self.wi(["prime"], store)
        self.assertNotIn("WARNING", r.stdout)
        self.assertNotIn("note", r.stdout)

    def test_missing(self):
        store = self.tmp / "host" / ".work-items"
        self.make_host()
        self.store_files(store)
        r = self.lint(store, 3)
        self.assertIn("records `repo: own` in store.yaml but has no .git",
                      r.stdout)
        self.assertIn("`wi init --no-track` to start new history", r.stdout)
        self.assertIn("has no .git", self.wi(["prime"], store).stdout)

    def test_broken(self):
        store = self.tmp / "host" / ".work-items"
        self.make_host()
        self.store_files(store)
        (store / ".git").mkdir()
        r = self.lint(store, 3)
        self.assertIn("not a usable store repo", r.stdout)
        self.assertIn("never `rm -rf`", r.stdout)

    def test_uncommitted_is_a_notice(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        r = self.lint(store, 0)
        self.assertIn("1 uncommitted path(s)", r.stderr)
        self.assertIn("`wi commit`", r.stderr)
        self.assertIn("uncommitted", self.wi(["prime"], store).stdout)

    def test_uncommitted_skipped_under_a_held_lock(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        with open(store / ".lock", "a") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            start = time.monotonic()
            r = self.lint(store, 0)
            self.assertLess(time.monotonic() - start, 8)
        self.assertIn("uncommitted check skipped", r.stderr)
        self.assertNotIn("uncommitted path", r.stderr)

    def test_stale_index_lock(self):
        store = self.make_own()
        lock = store / ".git" / "index.lock"
        lock.write_text("")
        old = time.time() - 3600
        os.utime(lock, (old, old))
        r = self.lint(store, 3)
        self.assertIn(f"{lock} is 1h00m old", r.stdout)
        self.assertIn("remove it only when no git process runs", r.stdout)
        self.assertIn("index.lock", self.wi(["prime"], store).stdout)

    def test_fresh_index_lock_is_not_reported(self):
        store = self.make_own()
        (store / ".git" / "index.lock").write_text("")
        r = self.lint(store, 0)
        self.assertNotIn("index.lock", r.stdout)

    def test_host_does_not_ignore(self):
        store = self.make_own()
        (self.tmp / "host" / ".gitignore").write_text("")
        r = self.lint(store, 3)
        self.assertIn("does not ignore store", r.stdout)
        self.assertIn("`wi init --no-track`", r.stdout)
        # prime reads no host
        self.assertNotIn("does not ignore", self.wi(["prime"], store).stdout)

    def test_host_tracks_the_store(self):
        host = self.make_host()
        store = host / ".work-items"
        self.store_files(store)
        self.git(host, "add", "-f", ".work-items/README.md")
        self.git(host, "commit", "-q", "-m", "tracked")
        self.git(store, "init", "-q", "--template=")
        self.git(store, "add", "-A")
        self.git(store, "commit", "-q", "-m", "init")
        r = self.lint(store, 3)
        self.assertIn("tracks 1 path(s) under .work-items", r.stdout)
        self.assertIn("rm -r -q --cached -- .work-items", r.stdout)

    def test_remote_names_only(self):
        store = self.make_own()
        self.git(store, "remote", "add", "origin",
                 "https://user:secret@example.invalid/x.git")
        r = self.lint(store, 0)
        self.assertIn("has a remote (origin)", r.stderr)
        self.assertIn("meant to be local", r.stderr)
        self.assertNotIn("secret", r.stdout + r.stderr)
        self.assertNotIn("secret", self.wi(["prime"], store).stdout)

    def test_repo_value_other_than_own(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=False)
        (store / "store.yaml").write_text("tracking: tracked\nrepo: shared\n")
        r = self.lint(store, 3)
        self.assertIn("repo must be own (got 'shared')", r.stdout)

    def test_more_than_one_repo_line(self):
        store = self.make_own()
        (store / "store.yaml").write_text(
            "tracking: tracked\nrepo: own\nrepo: own\n")
        self.git(store, "commit", "-q", "-am", "yaml")
        r = self.lint(store, 3)
        self.assertIn("more than one repo: line", r.stdout)

    def test_prime_shows_one_store_repo_line(self):
        store = self.make_own()
        (store / "items" / "one-aaaa.md").write_text(
            ITEM.format(iid="one-aaaa") + "edit\n")
        lock = store / ".git" / "index.lock"
        lock.write_text("")
        old = time.time() - 3600
        os.utime(lock, (old, old))
        out = self.wi(["prime"], store).stdout
        self.assertIn("uncommitted", out)        # first in table order
        self.assertNotIn("index.lock", out)

    def test_plain_store_unchanged(self):
        store = self.tmp / ".work-items"
        self.store_files(store, own=False)
        r = self.lint(store, 0)
        self.assertEqual(r.stderr, "")


class TestPathspec(StoreRepoCase):
    """d1e9 D4' and D4'': only existing paths, matched exactly."""

    def test_listing_match(self):
        self.assertEqual(wi._kept_by_listing(["archive"],
                                             ["archive/2026/x.md"]),
                         ["archive"])
        self.assertEqual(wi._kept_by_listing(["items/x.md"],
                                             ["items/x.md.tmp1"]), [])
        self.assertEqual(wi._kept_by_listing(["items/x.md"], ["items/x.md"]),
                         ["items/x.md"])

    def test_existing_paths(self):
        store = self.make_own()
        (store / "archive" / "2026").mkdir(parents=True)
        (store / "archive" / "2026" / "x.md").write_text("x\n")
        self.git(store, "add", "archive")
        self.git(store, "commit", "-q", "-m", "archive")
        shutil.rmtree(store / "archive")
        self.assertEqual(
            wi.existing_paths(store, wi.OWN_PATHS),
            ["items", "archive", "README.md", "store.yaml", ".gitignore"])
        self.git(store, "rm", "-r", "-q", "--cached", "archive")
        self.assertNotIn("archive", wi.existing_paths(store, wi.OWN_PATHS))


class TestGitPins(StoreRepoCase):
    """Pins of the git behaviour d1e9 rests on; a git change shows here."""

    def test_check_ignore_exits_1_inside_store_repo(self):
        store = self.make_own()
        r = self.git(store, "check-ignore", "-q", str(store), check=False)
        self.assertEqual(r.returncode, 1)
        r = self.git(self.tmp / "host", "check-ignore", "-q", ".work-items",
                     check=False)
        self.assertEqual(r.returncode, 0)

    def test_check_ignore_refuses_literal_pathspecs(self):
        store = self.make_own()
        r = self.git(store, "check-ignore", "-q", "items", check=False,
                     env={"GIT_LITERAL_PATHSPECS": "1"})
        self.assertEqual(r.returncode, 128)

    def test_empty_git_falls_through_without_a_ceiling(self):
        host = self.make_host()
        store = host / ".work-items"
        (store / ".git").mkdir(parents=True)
        r = self.git(store, "rev-parse", "--show-toplevel", check=False)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), str(host))
        r = self.git(store, "rev-parse", "--show-toplevel", check=False,
                     env={"GIT_CEILING_DIRECTORIES": str(host)})
        self.assertEqual(r.returncode, 128)

    def test_empty_hooks_path_runs_no_hook(self):
        store = self.make_own()
        hooks = self.tmp / "hooks"
        hooks.mkdir()
        shutil.copy(self.marker("pre-commit"), hooks / "pre-commit")
        self.git(self.tmp, "config", "--global", "core.hooksPath", str(hooks))
        shutil.copy(self.marker("root-pre-commit"), store / "pre-commit")
        self.git(store, "add", "pre-commit")
        self.git(store, "-c", "core.hooksPath=", "commit", "-q", "-m", "x")
        self.assertEqual(self.marked(), [])

    def test_commit_with_nothing_staged_exits_1(self):
        store = self.make_own()
        r = self.git(store, "commit", "-q", "-m", "x", check=False)
        self.assertEqual(r.returncode, 1)

    def test_pathspec_matching_nothing_fails(self):
        # why only existing paths go into a pathspec: add exits 128, commit 1
        store = self.make_own()
        r = self.git(store, "add", "-A", "--", "archive", check=False)
        self.assertEqual(r.returncode, 128)
        r = self.git(store, "commit", "-q", "-m", "x", "--", "archive",
                     check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("did not match", r.stderr)


if __name__ == "__main__":
    unittest.main()
