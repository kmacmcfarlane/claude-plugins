"""Tests for `wi estate`, the read-only cross-repo sweep.

Every store here is a fixture built in a temp dir: a scan dir holding a few
repo dirs, each with a `.claude-sandbox/work` or `.work` store. The live
estate is never read.
"""
import base64
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"

spec = importlib.util.spec_from_file_location("wi_estate", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)

NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def item_text(iid, status="todo", priority=2, created="2026-09-01",
              tags=(), deps=(), claimed=None, owner=None, body="", title=None):
    lines = ["---", f"id: {iid}", f"title: {title or iid}", "type: task",
             f"status: {status}", f"priority: {priority}"]
    if tags:
        lines.append("tags: [" + ", ".join(tags) + "]")
    if deps:
        lines.append("deps:")
        lines += [f"  - {d}" for d in deps]
    if owner:
        lines.append(f"owner: {owner}")
    if claimed:
        lines.append(f"claimed: {claimed}")
    lines += [f"created: {created}", f"updated: {created}"]
    if status in ("done", "dropped"):
        lines.append(f"closed: {created}")
    lines += ["---", "", f"Description of {iid}.", "", "## Handoff",
              "- doing: —", "- next: —", "- blocked: —", "- learned: —"]
    if body:
        lines += [body.rstrip("\n")]
    return "\n".join(lines) + "\n"


def run(args, cwd=None, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "WI_ROOT"}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(WI)] + args, env=env,
                          capture_output=True, text=True, cwd=cwd)


def tree_digest(path):
    """Every file under path with its bytes' hash and mtime."""
    out = {}
    for dirpath, _dirs, files in os.walk(path):
        for f in files:
            p = Path(dirpath) / f
            out[str(p)] = (hashlib.sha1(p.read_bytes()).hexdigest(),
                           p.stat().st_mtime_ns)
    return out


class EstateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wi-estate-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.scan = self.tmp / "src"
        self.scan.mkdir()

    def store(self, repo, rel=".claude-sandbox/work"):
        s = self.scan / repo / rel
        (s / "items").mkdir(parents=True, exist_ok=True)
        return s

    def put(self, store, iid, **kw):
        (store / "items" / f"{iid}.md").write_text(item_text(iid, **kw))

    def scan_one(self, **kw):
        return wi.estate_scan([self.scan], now=NOW, **kw)

    def repo(self, report, name):
        rows = [r for r in report["repos"] if r["repo"] == name]
        self.assertEqual(len(rows), 1, report)
        return rows[0]


class TestDiscovery(EstateCase):
    def test_both_store_layouts_and_no_store(self):
        self.put(self.store("alpha"), "a-one-0001")
        self.put(self.store("beta", ".work"), "b-one-0001")
        (self.scan / "gamma").mkdir()          # a repo with no store
        (self.scan / ".hidden" / ".work" / "items").mkdir(parents=True)
        report = self.scan_one()
        self.assertEqual([(r["repo"], r["store"]) for r in report["repos"]],
                         [("alpha", ".claude-sandbox/work"), ("beta", ".work")])

    def test_symlinked_repo_out_of_the_dir_is_not_followed(self):
        outside = self.tmp / "elsewhere" / "repo"
        (outside / ".work" / "items").mkdir(parents=True)
        (outside / ".work" / "items" / "x-0001.md").write_text(item_text("x-0001"))
        os.symlink(outside, self.scan / "linked")
        self.assertEqual(self.scan_one()["repos"], [])

    def test_symlinked_item_file_out_of_the_dir_is_reported_not_read(self):
        s = self.store("alpha")
        self.put(s, "a-one-0001")
        secret = self.tmp / "outside.md"
        secret.write_text(item_text("out-side-0001"))
        os.symlink(secret, s / "items" / "out-side-0001.md")
        r = self.repo(self.scan_one(), "alpha")
        self.assertEqual(r["counts"]["todo"], 1)
        self.assertEqual(len(r["problems"]), 1)
        self.assertIn("symlink", r["problems"][0]["error"])

    def test_no_store_anywhere_exits_2(self):
        (self.scan / "empty").mkdir()
        res = run(["estate", "--dir", str(self.scan)])
        self.assertEqual(res.returncode, 2, res.stderr)

    def test_missing_dir_is_a_usage_error(self):
        res = run(["estate", "--dir", str(self.tmp / "nope")])
        self.assertEqual(res.returncode, 1)

    def git(self, *args, cwd=None):
        r = subprocess.run(["git", "-c", "user.name=t", "-c",
                            "user.email=t@t", "-c", "init.defaultBranch=main"]
                           + list(args), cwd=cwd, capture_output=True,
                           text=True)
        if r.returncode != 0:
            self.skipTest(f"git unavailable: {r.stderr}")
        return r

    def committed_repo(self, path):
        self.git("init", "-q", str(path))
        self.git("commit", "-q", "--allow-empty", "-m", "x", cwd=path)
        return path

    def test_linked_worktree_beside_the_main_checkout_is_skipped(self):
        # named to sort before its main checkout: the main still wins
        main = self.committed_repo(self.scan / "zulu")
        self.git("worktree", "add", "-q", str(self.scan / "alpha-wt"), cwd=main)
        self.put(self.store("zulu"), "z-one-0001")
        self.put(self.store("alpha-wt"), "z-one-0001")
        report = self.scan_one()
        self.assertEqual([r["repo"] for r in report["repos"]], ["zulu"])
        self.assertEqual([(x["repo"], x["reason"][:15])
                          for x in report["skipped"]],
                         [("alpha-wt", "linked worktree")])
        res = run(["estate", "--dir", str(self.scan)])
        self.assertIn("skipped alpha-wt: linked worktree of", res.stdout)

    def test_bare_repo_whose_only_checkout_is_a_worktree_is_kept(self):
        src = self.committed_repo(self.tmp / "src-repo")
        bare = self.tmp / "bare.git"
        self.git("clone", "-q", "--bare", str(src), str(bare))
        self.git("--git-dir", str(bare), "worktree", "add", "-q",
                 str(self.scan / "alpha"))
        self.put(self.store("alpha"), "a-one-0001")
        report = self.scan_one()
        self.assertEqual([r["repo"] for r in report["repos"]], ["alpha"])
        self.assertEqual(report["skipped"], [])

    def test_nul_in_a_dot_git_file_does_not_stop_the_sweep(self):
        self.put(self.store("alpha"), "a-one-0001")
        (self.scan / "alpha" / ".git").write_bytes(b"gitdir: a\0b\n")
        self.put(self.store("beta"), "b-one-0001")
        report = self.scan_one()
        self.assertEqual([r["repo"] for r in report["repos"]],
                         ["alpha", "beta"])

    def test_nul_in_a_commondir_does_not_stop_the_sweep(self):
        for name, write in (
                ("alpha", lambda p: p.write_bytes(b"../x\0y\n")),
                ("beta", lambda p: os.symlink("/dev/zero", p))):
            gitdir = self.tmp / f"{name}-gitdir"
            gitdir.mkdir()
            write(gitdir / "commondir")
            self.put(self.store(name), f"{name}-0001")
            (self.scan / name / ".git").write_text(f"gitdir: {gitdir}\n")
        report = self.scan_one()
        self.assertEqual([r["repo"] for r in report["repos"]],
                         ["alpha", "beta"])
        self.assertEqual(report["skipped"], [])

    def test_fifo_commondir_does_not_hang_the_sweep(self):
        gitdir = self.tmp / "alpha-gitdir"
        gitdir.mkdir()
        os.mkfifo(gitdir / "commondir")
        self.put(self.store("alpha"), "a-one-0001")
        (self.scan / "alpha" / ".git").write_text(f"gitdir: {gitdir}\n")
        env = {k: v for k, v in os.environ.items() if k != "WI_ROOT"}
        try:
            res = subprocess.run([sys.executable, str(WI), "estate", "--dir",
                                  str(self.scan), "--json"], env=env,
                                 capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            self.fail("the sweep hung opening a FIFO commondir")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual([r["repo"] for r in json.loads(res.stdout)["repos"]],
                         ["alpha"])

    def test_separate_git_dir_clone_is_kept(self):
        self.git("init", "-q", "--separate-git-dir", str(self.tmp / "sep.git"),
                 str(self.scan / "alpha"))
        self.assertTrue((self.scan / "alpha" / ".git").is_file())
        self.put(self.store("alpha"), "a-one-0001")
        self.assertEqual([r["repo"] for r in self.scan_one()["repos"]],
                         ["alpha"])

    def test_submodule_is_kept_when_the_dir_is_the_superproject(self):
        sub_src = self.committed_repo(self.tmp / "subsrc")
        sup = self.committed_repo(self.tmp / "super")
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q",
                 str(sub_src), "mod", cwd=sup)
        (sup / "mod" / ".work" / "items").mkdir(parents=True)
        (sup / "mod" / ".work" / "items" / "m-one-0001.md").write_text(
            item_text("m-one-0001"))
        report = wi.estate_scan([sup], now=NOW)
        self.assertEqual([r["repo"] for r in report["repos"]], ["mod"])
        self.assertEqual(report["skipped"], [])

    def test_symlinked_alias_inside_the_dir_is_counted_once(self):
        self.put(self.store("alpha"), "a-one-0001")
        os.symlink(self.scan / "alpha", self.scan / "zeta")
        os.symlink(self.scan / "alpha", self.scan / "aardvark")
        report = self.scan_one()
        self.assertEqual([r["repo"] for r in report["repos"]], ["alpha"])
        self.assertEqual(sorted((x["repo"], x["reason"].split(" of ")[0])
                                for x in report["skipped"]),
                         [("aardvark", "symlink alias"),
                          ("zeta", "symlink alias")])

    def test_default_refuses_home_and_above(self):
        home = self.tmp / "home"
        (home / "repo").mkdir(parents=True)
        self.git("init", "-q", str(home / "repo"))
        env = {"HOME": str(home)}
        res = run(["estate"], cwd=home / "repo", env_extra=env)
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("--dir", res.stderr)
        self.git("init", "-q", str(home))          # a repo at $HOME itself
        res = run(["estate"], cwd=home, env_extra=env)
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("--dir", res.stderr)

    def test_default_dir_from_a_linked_worktree(self):
        main = self.scan / "alpha"
        self.put(self.store("alpha"), "a-one-0001")
        self.git("init", "-q", str(main))
        self.git("commit", "-q", "--allow-empty", "-m", "x", cwd=main)
        wt = self.tmp / "elsewhere" / "wt"
        self.git("worktree", "add", "-q", str(wt), cwd=main)
        res = run(["estate", "--json"], cwd=wt)
        self.assertEqual(res.returncode, 0, res.stderr)
        got = json.loads(res.stdout)
        self.assertEqual(got["dirs"], [os.path.realpath(self.scan)])

    def test_default_dir_from_a_submodule_is_the_superprojects_parent(self):
        sub_src = self.tmp / "subsrc"
        self.git("init", "-q", str(sub_src))
        self.git("commit", "-q", "--allow-empty", "-m", "x", cwd=sub_src)
        sup = self.scan / "alpha"
        self.put(self.store("alpha"), "a-one-0001")
        self.git("init", "-q", str(sup))
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q",
                 str(sub_src), "mod", cwd=sup)
        res = run(["estate", "--json"], cwd=sup / "mod")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout)["dirs"],
                         [os.path.realpath(self.scan)])

    def test_text_mode_names_the_scanned_dirs(self):
        (self.scan / "empty").mkdir()
        res = run(["estate", "--dir", str(self.scan)])
        self.assertEqual(res.returncode, 2)
        self.assertIn(f"scanned {self.scan}", res.stdout)

    def test_root_flag_is_refused(self):
        res = run(["--root", str(self.tmp), "estate", "--dir", str(self.scan)])
        self.assertEqual(res.returncode, 1)
        self.assertIn("--dir", res.stderr)

    def test_negative_top_is_refused(self):
        res = run(["estate", "--dir", str(self.scan), "--top", "-1"])
        self.assertEqual(res.returncode, 1)

    def test_non_utf8_names_print_under_strict_utf8(self):
        bad = os.fsencode(str(self.scan)) + b"/caf\xe9"
        os.makedirs(bad + b"/.work/items")
        with open(bad + b"/.work/items/r\xe9-0001.md", "wb") as fh:
            fh.write(b"not an item\n")
        env = {"PYTHONIOENCODING": "utf-8"}
        res = run(["estate", "--dir", str(self.scan)], env_extra=env)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("caf\\xe9", res.stdout)
        res = run(["estate", "--dir", str(self.scan), "--json"], env_extra=env)
        self.assertEqual(res.returncode, 0, res.stderr)
        got = json.loads(res.stdout)
        json.dumps(got, ensure_ascii=False).encode("utf-8")  # no lone surrogate
        self.assertEqual(got["repos"][0]["repo"], "caf\\xe9")
        raw = os.fsdecode(base64.b64decode(got["repos"][0]["path_raw"]))
        self.assertTrue(os.path.isdir(raw))       # the printable path is not
        self.assertEqual(os.fsencode(raw), bad)

    def test_default_dir_is_the_parent_of_the_repo(self):
        repo = self.scan / "alpha"
        self.put(self.store("alpha"), "a-one-0001")
        self.put(self.store("beta"), "b-one-0001")
        if subprocess.run(["git", "init", "-q", str(repo)],
                          capture_output=True).returncode != 0:
            self.skipTest("git unavailable")
        res = run(["estate", "--json"], cwd=repo)
        self.assertEqual(res.returncode, 0, res.stderr)
        got = json.loads(res.stdout)
        self.assertEqual([r["repo"] for r in got["repos"]], ["alpha", "beta"])


class TestSummary(EstateCase):
    def test_counts_and_ready_ranking(self):
        s = self.store("alpha")
        self.put(s, "low-0001", priority=3, created="2026-09-01")
        self.put(s, "high-0001", priority=1, created="2026-09-10")
        self.put(s, "old-high-0001", priority=1, created="2026-09-02")
        self.put(s, "waiting-0001", deps=["low-0001"])
        self.put(s, "doing-0001", status="doing", claimed="2026-09-25T11:00Z",
                 owner="me@host")
        self.put(s, "blocked-0001", status="blocked")
        self.put(s, "done-0001", status="done")
        r = self.repo(self.scan_one(top=2), "alpha")
        c = r["counts"]
        self.assertEqual((c["open"], c["todo"], c["doing"], c["blocked"],
                          c["ready"], c["done"]), (6, 4, 1, 1, 3, 1))
        self.assertEqual([i["id"] for i in r["ready"]],
                         ["old-high-0001", "high-0001"])

    def test_archived_done_dep_is_met(self):
        s = self.store("alpha")
        self.put(s, "after-0001", deps=["gone-0001"])
        (s / "archive" / "2026").mkdir(parents=True)
        (s / "archive" / "2026" / "gone-0001.md").write_text(
            item_text("gone-0001", status="done"))
        r = self.repo(self.scan_one(), "alpha")
        self.assertEqual([i["id"] for i in r["ready"]], ["after-0001"])
        self.assertEqual(r["counts"]["done"], 0)   # archive is not counted

    def test_answered_versus_unanswered_decisions(self):
        s = self.store("alpha")
        body = "\n".join([
            "decision 1: answered one — (a) x | (b) y",
            "answer 1: (a)",
            "decision 2: still open — (a) x | (b) y",
            "  raised: 2026-09-20T10:00Z",
            "  what: the thing",
            "decision 3: open, no card",
            "```",
            "decision 4: inside a fence is text",
            "```",
        ])
        self.put(s, "asks-0001", body=body)
        self.put(s, "closed-0001", status="done",
                 body="decision 9: on a closed item")
        r = self.repo(self.scan_one(), "alpha")
        got = [(d["id"], d["n"], d["raised"], d["age_days"])
               for d in r["decisions"]]
        self.assertEqual(got, [("asks-0001", 2, "2026-09-20T10:00Z", 5),
                               ("asks-0001", 3, None, None)])
        self.assertEqual(r["decisions"][0]["text"],
                         "still open — (a) x | (b) y")

    def test_raised_belongs_to_its_own_card(self):
        s = self.store("alpha")
        body = "\n".join([
            "decision 5: first",
            "not indented, ends the card",
            "  raised: 2026-09-01T00:00Z",
        ])
        self.put(s, "card-0001", body=body)
        r = self.repo(self.scan_one(), "alpha")
        self.assertIsNone(r["decisions"][0]["raised"])

    def test_first_raised_wins_on_a_revised_card(self):
        s = self.store("alpha")
        body = "\n".join([
            "decision 2: first ask",
            "  raised: 2026-09-10T00:00Z",
            "decision 2: revised ask",
            "  raised: 2026-09-20T00:00Z",
            "  revised: 2026-09-20T00:00Z — options changed",
        ])
        self.put(s, "rev-0001", body=body)
        d = self.repo(self.scan_one(), "alpha")["decisions"]
        self.assertEqual([(x["n"], x["text"], x["raised"]) for x in d],
                         [(2, "revised ask", "2026-09-10T00:00Z")])

    def test_ready_matches_wi_next_across_an_archived_dep(self):
        s = self.store("alpha")
        self.put(s, "after-done-0001", deps=["gone-0001"], priority=1)
        self.put(s, "after-open-0001", deps=["arch-open-0001"])
        self.put(s, "free-0001", priority=3)
        (s / "archive" / "2026").mkdir(parents=True)
        (s / "archive" / "2026" / "gone-0001.md").write_text(
            item_text("gone-0001", status="done"))
        (s / "archive" / "2026" / "arch-open-0001.md").write_text(
            item_text("arch-open-0001", status="todo"))
        nxt = subprocess.run([sys.executable, str(WI), "--root", str(s),
                              "next", "--json"], capture_output=True, text=True)
        want = [i["id"] for i in json.loads(nxt.stdout)["ready"]]
        got = [i["id"] for i in
               self.repo(self.scan_one(top=10), "alpha")["ready"]]
        self.assertEqual(got, want)
        self.assertEqual(got, ["after-done-0001", "free-0001"])

    def test_lists_are_capped_with_a_count_of_the_rest(self):
        s = self.store("alpha")
        body = "\n".join(f"decision {n}: q{n}" for n in range(1, 8))
        self.put(s, "many-0001", body=body)
        r = self.repo(self.scan_one(cap=5), "alpha")
        self.assertEqual(len(r["decisions"]), 5)
        self.assertEqual(r["omitted"]["decisions"], 2)
        self.assertEqual(r["omitted"]["stale"], 0)

    def test_stale_doing_claims(self):
        s = self.store("alpha")
        self.put(s, "fresh-0001", status="doing", claimed="2026-09-25T10:00Z",
                 owner="a@h")
        self.put(s, "stale-0001", status="doing", claimed="2026-09-22T10:00Z",
                 owner="b@h")
        r = self.repo(self.scan_one(stale="24h"), "alpha")
        self.assertEqual([x["id"] for x in r["stale"]], ["stale-0001"])
        self.assertEqual(r["stale"][0]["owner"], "b@h")

    def test_security_hint(self):
        s = self.store("alpha")
        self.put(s, "tagged-0001", tags=["security"])
        self.put(s, "titled-0001", title="Rotate the leaked deploy key")
        self.put(s, "noisy-0001", title="Refresh the auth token cache permissions")
        self.put(s, "plain-0001", title="Tidy the docs")
        self.put(s, "done-sec-0001", status="done", tags=["security"])
        r = self.repo(self.scan_one(), "alpha")
        self.assertEqual(sorted(x["id"] for x in r["security"]),
                         ["tagged-0001", "titled-0001"])


class TestMalformed(EstateCase):
    def test_bad_item_is_reported_and_the_rest_summarised(self):
        s = self.store("alpha")
        self.put(s, "good-0001")
        (s / "items" / "bad-0001.md").write_text("no front matter here\n")
        (s / "items" / "empty-0001.md").write_text("")
        self.put(self.store("beta"), "fine-0001")
        report = self.scan_one()
        a = self.repo(report, "alpha")
        self.assertEqual(a["counts"]["todo"], 1)
        self.assertEqual(sorted(Path(p["path"]).name for p in a["problems"]),
                         ["bad-0001.md", "empty-0001.md"])
        self.assertEqual(self.repo(report, "beta")["counts"]["todo"], 1)

    def test_directory_named_md_is_not_an_empty_file(self):
        s = self.store("alpha")
        (s / "items" / "odd-0001.md").mkdir()
        a = self.repo(self.scan_one(), "alpha")
        self.assertEqual(len(a["problems"]), 1)
        self.assertIn("not a regular file", a["problems"][0]["error"])

    def test_undecodable_item_is_reported(self):
        s = self.store("alpha")
        (s / "items" / "bin-0001.md").write_bytes(b"---\nid: \xff\xfe\n---\n")
        a = self.repo(self.scan_one(), "alpha")
        self.assertEqual(len(a["problems"]), 1)

    def test_cli_does_not_crash_on_a_malformed_store(self):
        s = self.store("alpha")
        (s / "items" / "bad-0001.md").write_text("---\nid: x\n")
        res = run(["estate", "--dir", str(self.scan)])
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("PROBLEM", res.stdout)


class TestReadOnly(EstateCase):
    def test_stores_are_unchanged_by_a_run(self):
        s = self.store("alpha")
        self.put(s, "one-0001", status="doing", claimed="2026-09-01T00:00Z")
        self.put(s, "two-0001", body="decision 1: open")
        self.put(self.store("beta", ".work"), "three-0001")
        before = tree_digest(self.scan)
        for args in (["estate", "--dir", str(self.scan)],
                     ["estate", "--dir", str(self.scan), "--json"]):
            self.assertEqual(run(args).returncode, 0)
        self.assertEqual(tree_digest(self.scan), before)
        self.assertFalse((s / ".lock").exists())


class TestJsonShape(EstateCase):
    def test_shape(self):
        s = self.store("alpha")
        self.put(s, "one-0001", tags=["security"],
                 body="decision 1: open\n  raised: 2026-09-24")
        self.put(s, "two-0001", status="doing", claimed="2026-09-01T00:00Z",
                 owner="o@h")
        res = run(["estate", "--dir", str(self.scan), "--json", "--top", "1"])
        self.assertEqual(res.returncode, 0, res.stderr)
        got = json.loads(res.stdout)
        self.assertEqual(set(got), {"dirs", "stale_after", "generated", "repos",
                                    "skipped"})
        self.assertEqual(got["dirs"], [str(self.scan)])
        r = got["repos"][0]
        self.assertEqual(set(r), {"repo", "path", "path_raw", "store",
                                  "counts", "ready",
                                  "decisions", "stale", "security", "problems",
                                  "omitted"})
        self.assertEqual(r["omitted"], {"decisions": 0, "security": 0,
                                        "stale": 0, "problems": 0})
        self.assertEqual(set(r["counts"]),
                         {"todo", "doing", "blocked", "parked", "grooming",
                          "done", "dropped", "open", "ready"})
        self.assertEqual(set(r["ready"][0]),
                         {"id", "title", "priority", "type", "tags"})
        self.assertEqual(set(r["decisions"][0]),
                         {"id", "title", "n", "text", "raised", "age_days"})
        self.assertIsInstance(r["decisions"][0]["age_days"], int)
        self.assertEqual(set(r["stale"][0]),
                         {"id", "title", "owner", "claimed", "age"})
        self.assertEqual(set(r["security"][0]),
                         {"id", "title", "status", "priority", "tags"})


if __name__ == "__main__":
    unittest.main()
