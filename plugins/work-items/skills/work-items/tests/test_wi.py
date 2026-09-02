"""Tests for the wi work-item CLI.

Fixtures under tests/fixtures/ are excerpts copied from the real
{brainboy,clustertool,opencode,ptp}/TODO.md files — the live files are never
read here. The backlog-yaml export is validated against the claude-sandbox
scaffold's backlog.py `validate --strict` when that script is invocable, and
falls back to a structural assertion otherwise.
"""
import importlib.util
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WI = HERE.parent / "scripts" / "wi.py"
FIXTURES = HERE / "fixtures"
BACKLOG_PY = Path("/home/rt/work/src/github.com/kmacmcfarlane/claude-sandbox"
                  "/scaffold-ralph/scripts/backlog/backlog.py")

spec = importlib.util.spec_from_file_location("wi", WI)
wi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wi)


def run(args, root, env=None, cwd=None):
    full_env = dict(os.environ, WI_ROOT=str(root), WI_OWNER="tester@local")
    full_env.update(env or {})
    return subprocess.run([sys.executable, str(WI)] + args, env=full_env,
                          capture_output=True, text=True, cwd=cwd)


def _race_claim(spec_tuple):
    root, item_id, owner = spec_tuple
    return run(["claim", item_id], root, env={"WI_OWNER": owner}).returncode


CANONICAL = """---
id: repl3-retention-7f2a
title: Replication task 3 destination retention is a no-op
type: bug
status: doing
stage: implement
priority: 1
tags: [zfs, replication]
deps:
  - snapshot-cleanup-3c1d
owner: kyle@hooper
claimed: 2026-08-30T14:02Z
created: 2026-08-05
updated: 2026-08-30
refs:
  - plans/2026-08-05-snapshot-retention-reduction.md
---

zettarepl's target-side retention is driven only by naming schemas.

## Acceptance
- [ ] two hourly runs later, brainboy shows pruning

## Handoff
- doing: applying the midclt call on a test dataset first
- next: verify zettarepl prunes after two runs
- blocked: —
- learned: —

## Notes
- 2026-08-30 claimed by kyle@hooper
"""


class WiTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wi-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / ".work"
        self.assertEqual(run(["init"], self.root).returncode, 0)

    def write_item(self, iid, title=None, status="todo", priority=2, deps=(),
                   itype="task", stage=None, handoff=None, sections="",
                   **meta_extra):
        meta = {"id": iid, "title": title or iid, "type": itype,
                "status": status, "stage": stage, "priority": priority,
                "deps": list(deps), "created": "2026-08-01",
                "updated": "2026-08-01"}
        if status in ("done", "dropped"):
            meta["closed"] = meta_extra.pop("closed", "2026-08-02")
        meta.update(meta_extra)
        h = wi.emit_handoff(handoff or {})
        item = wi.Item(meta, [], f"Description of {iid}.",
                       [("Handoff", h)] + wi.parse_body(sections)[1])
        wi.save_item(self.root, item)
        return iid

    def wi_ok(self, args, **kw):
        result = run(args, self.root, **kw)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result.stdout


class TestFrontMatter(WiTestCase):
    def test_canonical_round_trip_is_byte_identical(self):
        item = wi.Item.parse(CANONICAL)
        self.assertEqual(item.render(), CANONICAL)

    def test_odd_input_preserves_unknown_keys_and_sections(self):
        text = CANONICAL.replace("type: bug", 'type: "bug"\ncustom_key: kept')
        text = text.replace("## Notes", "## Rollout plan\nstep one\n\n## Notes")
        item = wi.Item.parse(text)
        out = item.render()
        self.assertIn("custom_key: kept", out)
        self.assertIn("## Rollout plan\nstep one", out)
        # second pass is stable
        self.assertEqual(wi.Item.parse(out).render(), out)

    def test_nested_yaml_is_rejected_not_rewritten(self):
        bad = CANONICAL.replace("tags: [zfs, replication]",
                                "tags:\n  - nested:\n      deep: true")
        with self.assertRaises(wi.WiError) as ctx:
            wi.Item.parse(bad, path="x.md")
        self.assertEqual(ctx.exception.code, 3)

    def test_show_brief_and_json(self):
        (self.root / "items" / "repl3-retention-7f2a.md").write_text(CANONICAL)
        brief = self.wi_ok(["show", "repl3", "--brief"])
        self.assertIn("## Handoff", brief)
        self.assertIn("plans/2026-08-05-snapshot-retention-reduction.md", brief)
        rec = json.loads(self.wi_ok(["show", "repl3-retention-7f2a", "--json"]))
        self.assertEqual(rec["handoff"]["next"],
                         "verify zettarepl prunes after two runs")
        self.assertEqual(rec["acceptance"],
                         [{"text": "two hourly runs later, brainboy shows pruning",
                           "done": False}])


class TestImportTodo(WiTestCase):
    def items(self):
        return json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))

    def test_brainboy_sections(self):
        self.wi_ok(["import-todo", str(FIXTURES / "brainboy_todo.md")])
        by_title = {it["title"]: it for it in self.items()}
        self.assertEqual(len(by_title), 6)
        done = by_title["Discord webhook key rename"]
        self.assertEqual(done["status"], "done")
        self.assertEqual(done["closed"], "2026-08-06")
        self.assertIn("repo:clustertool", done["tags"])
        high = by_title["lucy offsite incrementals contain no data"]
        self.assertEqual((high["status"], high["priority"]), ("done", 0))
        still = by_title["replication task 3's destination retention is a no-op"]
        self.assertEqual((still["status"], still["priority"]), ("todo", 1))
        low = by_title["Move the boot device off the 2011 OCZ Vertex3"]
        self.assertEqual(low["priority"], 4)
        sops = by_title["Extend the SOPS pre-commit hook with entropy/pattern detection"]
        self.assertIn("repo:clustertool", sops["tags"])
        self.assertTrue(any(r.startswith("todo:") for r in still["refs"]))

    def test_idempotent_rerun_creates_nothing(self):
        self.wi_ok(["import-todo", str(FIXTURES / "brainboy_todo.md")])
        out = self.wi_ok(["import-todo", str(FIXTURES / "brainboy_todo.md")])
        self.assertNotIn("created", out)
        self.assertEqual(out.count("skipped"), 6)
        self.assertEqual(len(self.items()), 6)

    def test_clustertool_bold_bullets(self):
        self.wi_ok(["import-todo", str(FIXTURES / "clustertool_todo.md")])
        titles = {it["title"] for it in self.items()}
        self.assertEqual(len(titles), 3)
        self.assertIn("Require the `pre-commit` check on `main` via branch "
                      "protection / ruleset", titles)

    def test_opencode_and_ptp_checkboxes(self):
        self.wi_ok(["import-todo", str(FIXTURES / "opencode_todo.md")])
        by_title = {it["title"]: it for it in self.items()}
        self.assertEqual(len(by_title), 4)
        self.assertEqual(by_title["On-demand model switching"]["status"], "done")
        self.assertEqual(by_title["Warm model switching"]["status"], "todo")
        self.wi_ok(["import-todo", str(FIXTURES / "ptp_todo.md")])
        self.assertEqual(len(self.items()), 7)
        self.assertIn("Script the qBittorrent add via WebUI API",
                      {it["title"] for it in self.items()})

    def test_refs_extracted_from_in_repo_links(self):
        todo = self.tmp / "TODO.md"
        todo.write_text("# TODO\n\n## Fix the thing\n\nSee "
                        "[the plan](plans/fix.md) and "
                        "[docs](https://example.com/x).\n")
        self.wi_ok(["import-todo", str(todo)])
        refs = self.items()[0]["refs"]
        self.assertIn("plans/fix.md", refs)
        self.assertFalse(any(r.startswith("https:") for r in refs))

    def test_dry_run_writes_nothing(self):
        out = self.wi_ok(["import-todo", "--dry-run",
                          str(FIXTURES / "ptp_todo.md")])
        self.assertIn("would create", out)
        self.assertEqual(run(["ls"], self.root).returncode, 2)


class TestBacklogYaml(WiTestCase):
    def seed(self):
        self.write_item("fix-retention-1111", "Fix retention", itype="bug",
                        priority=0,
                        sections="## Acceptance\n- [ ] pruning observed\n\n"
                                 "## Testing\n- command: zfs list -t snapshot\n")
        self.write_item("boot-device-2222", "Move boot device", priority=4,
                        deps=["fix-retention-1111"])
        self.write_item("review-me-3333", "In review", status="doing",
                        stage="review", owner="w1", claimed="2026-08-30T10:00Z",
                        handoff={"doing": "x", "next": "y"})
        self.write_item("old-done-4444", "Already done", status="done")

    def test_export_import_round_trip_and_validate(self):
        self.seed()
        out = self.tmp / "backlog.yaml"
        self.wi_ok(["export", "--format", "backlog-yaml", str(out),
                    "--project", "test"])
        done_out = self.tmp / "backlog_done.yaml"
        self.assertTrue(done_out.exists())
        # aliases were allocated per type prefix and written back
        aliases = {it["id"]: it.get("alias")
                   for it in json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))}
        self.assertEqual(aliases["fix-retention-1111"], "B-001")
        self.assertTrue(aliases["boot-device-2222"].startswith("S-"))

        self._validate(out, done_out)

        # round trip: import into a fresh root, export again, byte-identical
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        r = run(["import", "--format", "backlog-yaml", str(out), str(done_out)],
                fresh)
        self.assertEqual(r.returncode, 0, r.stderr)
        out2 = self.tmp / "backlog2.yaml"
        r = run(["export", "--format", "backlog-yaml", str(out2),
                 "--project", "test"], fresh)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out2.read_text(), out.read_text())
        self.assertEqual((self.tmp / "backlog2_done.yaml").read_text(),
                         done_out.read_text())
        # the 9-state mapping survived: review came back as doing+review
        reviewed = [it for it in json.loads(run(
            ["ls", "--status", "all", "--json"], fresh).stdout)
            if it["alias"] == aliases["review-me-3333"]]
        self.assertEqual((reviewed[0]["status"], reviewed[0]["stage"]),
                         ("doing", "review"))

    def _validate(self, out, done_out):
        """backlog.py validate --strict when invocable, else structural."""
        if BACKLOG_PY.exists():
            probe = subprocess.run([sys.executable, str(BACKLOG_PY), "--help"],
                                   capture_output=True)
            if probe.returncode == 0:
                r = subprocess.run(
                    [sys.executable, str(BACKLOG_PY), "--backlog", str(out),
                     "--done", str(done_out), "validate", "--strict"],
                    capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                return "backlog.py"
        text = out.read_text()
        self.assertIn("schema_version: 2", text)
        for key in ("title:", "priority:", "status:", "requires:",
                    "acceptance:", "testing:"):
            self.assertIn(key, text)
        return "structural"

    def test_import_update_touches_pipeline_fields_only(self):
        self.seed()
        out = self.tmp / "backlog.yaml"
        self.wi_ok(["export", "--format", "backlog-yaml", str(out),
                    "--project", "test"])
        text = out.read_text().replace("status: review", "status: testing")
        text = text.replace('claimed_by: "w1"', 'claimed_by: "w2"')
        out.write_text(text)
        self.wi_ok(["import", "--format", "backlog-yaml", "--update", str(out)])
        rec = json.loads(self.wi_ok(["show", "review-me-3333", "--json"]))
        self.assertEqual((rec["status"], rec["stage"], rec["owner"]),
                         ("doing", "testing", "w2"))
        self.assertEqual(rec["summary"], "Description of review-me-3333.")
        self.assertEqual(len(json.loads(self.wi_ok(
            ["ls", "--status", "all", "--json"]))), 4)


class TestNextRanking(WiTestCase):
    def seed(self):
        self.write_item("done-dep-aaaa", status="done")
        self.write_item("open-dep-bbbb", priority=3)
        self.write_item("ready-p0-cccc", priority=0)
        self.write_item("ready-p2-dddd", priority=2)
        self.write_item("waiting-eeee", priority=0, deps=["open-dep-bbbb"])
        self.write_item("unblocked-ffff", priority=1, deps=["done-dep-aaaa"])
        self.write_item("ext-dep-gggg", priority=0, deps=["ext: other-repo"])
        self.write_item("blocked-hhhh", status="blocked",
                        blocked="waiting on disk")
        self.write_item("doing-iiii", status="doing", owner="w1",
                        claimed="2026-08-30T10:00Z",
                        handoff={"doing": "a", "next": "b"})

    def test_interactive_ranking(self):
        self.seed()
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertEqual([it["id"] for it in data["doing"]], ["doing-iiii"])
        self.assertEqual([it["id"] for it in data["blocked"]], ["blocked-hhhh"])
        self.assertEqual([it["id"] for it in data["ready"]],
                         ["ready-p0-cccc", "unblocked-ffff", "ready-p2-dddd",
                          "open-dep-bbbb"])
        self.assertEqual(data["counts"]["waiting"], 2)  # waiting-eeee, ext-dep

    def test_dep_on_uat_stage_counts_as_resolved(self):
        self.write_item("uat-dep-aaaa", status="doing", stage="uat",
                        handoff={"next": "x"})
        self.write_item("child-bbbb", deps=["uat-dep-aaaa"])
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertIn("child-bbbb", [it["id"] for it in data["ready"]])

    def test_cycle_keeps_both_out(self):
        self.write_item("cyc-a-1111", deps=["cyc-b-2222"])
        self.write_item("cyc-b-2222", deps=["cyc-a-1111"])
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertEqual(data["ready"], [])

    def test_pipeline_order_and_bugs_first(self):
        self.write_item("todo-task-1111", priority=0)
        self.write_item("todo-bug-2222", priority=2, itype="bug")
        self.write_item("stage-test-3333", status="doing", stage="testing",
                        handoff={"next": "x"})
        self.write_item("stage-rev-4444", status="doing", stage="review",
                        handoff={"next": "x"})
        self.write_item("stage-impl-5555", status="doing",
                        handoff={"next": "x"})
        self.write_item("stage-uatf-6666", status="doing", stage="uat_feedback",
                        handoff={"next": "x"})
        rows = [ln.split("\t") for ln in
                self.wi_ok(["next", "--pipeline"]).strip().split("\n")]
        self.assertEqual([r[0] for r in rows],
                         ["testing", "review", "in_progress", "uat_feedback",
                          "todo", "todo"])
        self.assertEqual([r[1] for r in rows[-2:]],
                         ["todo-bug-2222", "todo-task-1111"])

    def test_pipeline_one_empty_exits_2(self):
        self.assertEqual(
            run(["next", "--pipeline", "--one"], self.root).returncode, 2)

    def test_pipeline_claim(self):
        self.write_item("claim-me-1111", priority=0)
        out = self.wi_ok(["next", "--pipeline", "--one", "--claim", "worker-1",
                          "--json"])
        rec = json.loads(out)
        self.assertEqual(rec["queue"], "todo")
        after = json.loads(self.wi_ok(["show", "claim-me-1111", "--json"]))
        self.assertEqual((after["status"], after["stage"], after["owner"]),
                         ("doing", "implement", "worker-1"))


class TestClaim(WiTestCase):
    def test_claim_semantics(self):
        self.write_item("target-1111")
        self.wi_ok(["claim", "target-1111"])
        before = (self.root / "items" / "target-1111.md").read_text()
        self.wi_ok(["claim", "target-1111"])  # idempotent for same owner
        self.assertEqual((self.root / "items" / "target-1111.md").read_text(),
                         before)
        r = run(["claim", "target-1111"], self.root, env={"WI_OWNER": "other@x"})
        self.assertEqual(r.returncode, 4)
        self.assertIn("held by tester@local", r.stderr)
        self.wi_ok(["claim", "target-1111", "--steal"],
                   env={"WI_OWNER": "other@x"})
        text = (self.root / "items" / "target-1111.md").read_text()
        self.assertIn("stolen from tester@local", text)
        self.wi_ok(["release", "target-1111"])
        rec = json.loads(self.wi_ok(["show", "target-1111", "--json"]))
        self.assertEqual((rec["status"], rec["owner"]), ("todo", None))

    def test_claim_blocked_exits_1(self):
        self.write_item("blocked-1111", status="blocked", blocked="reason")
        self.assertEqual(run(["claim", "blocked-1111"], self.root).returncode, 1)

    def test_eight_concurrent_claims_one_winner(self):
        self.write_item("race-1111")
        specs = [(str(self.root), "race-1111", f"worker-{n}@host")
                 for n in range(8)]
        with multiprocessing.Pool(8) as pool:
            codes = pool.map(_race_claim, specs)
        self.assertEqual(sorted(codes), [0, 4, 4, 4, 4, 4, 4, 4])
        item = wi.Item.parse((self.root / "items" / "race-1111.md").read_text())
        self.assertEqual(item.get("status"), "doing")
        self.assertIn(item.get("owner"), [f"worker-{n}@host" for n in range(8)])


class TestHandoffDoneArchive(WiTestCase):
    def test_handoff_idempotent_and_learned_once(self):
        self.write_item("ho-1111", status="doing", owner="tester@local",
                        claimed="2026-08-30T10:00Z")
        args = ["handoff", "ho-1111", "--doing", "applying", "--next", "verify",
                "--learned", "SOURCE parses zero"]
        self.wi_ok(args)
        first = (self.root / "items" / "ho-1111.md").read_text()
        self.wi_ok(args)
        self.assertEqual((self.root / "items" / "ho-1111.md").read_text(), first)
        self.assertEqual(first.count("learned: SOURCE parses zero"), 2)  # handoff + note

    def test_done_unblocks_dependents_and_archive_resolves(self):
        self.write_item("dep-1111")
        self.write_item("child-2222", deps=["dep-1111"])
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertNotIn("child-2222", [it["id"] for it in data["ready"]])
        self.wi_ok(["done", "dep-1111", "--note", "shipped"])
        rec = json.loads(self.wi_ok(["show", "dep-1111", "--json"]))
        self.assertEqual((rec["status"], rec["owner"], rec["stage"]),
                         ("done", None, None))
        self.assertTrue(rec["closed"])
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertIn("child-2222", [it["id"] for it in data["ready"]])
        # file did not move on done; archive moves it and show still resolves
        self.assertTrue((self.root / "items" / "dep-1111.md").exists())
        self.wi_ok(["archive", "--older-than", "0d"])
        self.assertFalse((self.root / "items" / "dep-1111.md").exists())
        self.assertEqual(len(list((self.root / "archive").glob("*/dep-1111.md"))), 1)
        self.wi_ok(["show", "dep-1111", "--brief"])

    def test_ambiguous_prefix_exits_2(self):
        self.write_item("same-prefix-1111")
        self.write_item("same-prefix-2222")
        self.assertEqual(run(["show", "same-prefix"], self.root).returncode, 2)
        self.wi_ok(["show", "same-prefix-1"])


class TestMergeSimulation(WiTestCase):
    def test_two_branch_union_lints_clean(self):
        self.write_item("shared-1111")
        branch_b = self.tmp / ".work-b"
        shutil.copytree(self.root, branch_b)
        # branch A: add two items, close the shared one
        self.wi_ok(["add", "A first item"])
        self.wi_ok(["add", "A second item"])
        self.wi_ok(["done", "shared-1111"])
        # branch B: add one item, hand off on nothing shared
        r = run(["add", "B only item"], branch_b)
        self.assertEqual(r.returncode, 0, r.stderr)
        # union the files (what a clean git merge produces)
        for path in (branch_b / "items").glob("*.md"):
            dest = self.root / "items" / path.name
            if not dest.exists():
                shutil.copy(path, dest)
        self.assertEqual(run(["lint"], self.root).returncode, 0)
        data = json.loads(self.wi_ok(["next", "--json"]))
        titles = {it["title"] for it in data["ready"]}
        self.assertEqual(titles, {"A first item", "A second item", "B only item"})


class TestPrime(WiTestCase):
    def seed_many(self, n=40):
        for i in range(n):
            self.write_item(f"ready-item-{i:02d}-aaaa",
                            f"A rather long ready item title number {i} about "
                            f"replication and snapshot retention hygiene")
        self.write_item("doing-item-9999", status="doing", owner="tester@local",
                        claimed="2026-08-30T10:00Z",
                        handoff={"doing": "applying the fix",
                                 "next": "verify pruning after two runs"})

    def test_budget_300_respected(self):
        self.seed_many()
        out = self.wi_ok(["prime", "--budget", "300"])
        self.assertLessEqual(len(out) / 4, 300)
        self.assertIn("next: verify pruning after two runs", out)
        self.assertIn("… (+", out)

    def test_budget_120_keeps_header_and_doing(self):
        self.seed_many()
        out = self.wi_ok(["prime", "--budget", "120"])
        self.assertLessEqual(len(out) / 4, 120)
        self.assertIn("wi:", out.split("\n")[0])
        self.assertIn("doing-item-9999", out)


class TestLint(WiTestCase):
    def test_malformed_front_matter_flagged(self):
        (self.root / "items" / "bad-item-0000.md").write_text(
            "---\nid bad-item-0000\n: nope\n---\n\nbody\n")
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("bad-item-0000", r.stdout)

    def test_doing_without_next_and_dangling_dep(self):
        self.write_item("doing-1111", status="doing")
        self.write_item("dangling-2222", deps=["nope-0000"])
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("empty handoff next", r.stdout)
        self.assertIn("dangling dep", r.stdout)

    def test_secret_values_flagged_but_paths_and_keys_ok(self):
        self.write_item(
            "leaky-1111", sections="## Notes\n"
            "DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/AbCdEf\n"
            "api_key: sk-live-4f9a8b7c6d5e4f3a2b1c\n"
            "-----BEGIN RSA PRIVATE KEY-----\n")
        self.write_item(
            "clean-2222", sections="## Notes\n"
            "creds: clusterenv.yaml key DISCORD_WEBHOOK_BACKUPS\n"
            "set API_KEY=<your key> in the env file\n")
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout.count("likely secret value"), 2)
        self.assertIn("PEM private key", r.stdout)
        self.assertNotIn("clean-2222", r.stdout)

    def test_conflict_markers_flagged(self):
        (self.root / "items" / "conflicted-0000.md").write_text(
            CANONICAL.replace("## Notes", "<<<<<<< HEAD\n## Notes"))
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("conflict markers", r.stdout)


class TestIds(WiTestCase):
    def test_same_title_twice_differs_and_slugs_are_clean(self):
        self.wi_ok(["add", "Fix the thing"])
        self.wi_ok(["add", "Fix the thing"])
        ids = [it["id"] for it in
               json.loads(self.wi_ok(["ls", "--json"]))]
        self.assertEqual(len(set(ids)), 2)
        self.wi_ok(["add", "Ünicode — & punctuation!! everywhere"])
        ids = [it["id"] for it in json.loads(self.wi_ok(["ls", "--json"]))]
        for iid in ids:
            self.assertRegex(iid, r"^[a-z0-9][a-z0-9-]*-[0-9a-f]{4}$")




class TestDetailsBlocks(unittest.TestCase):
    def test_details_content_never_becomes_items(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "scripts"))
        from wi import parse_todo
        text = (
            "# TODO\n\n"
            "## ~~old problem~~ — RESOLVED 2026-08-30\n\n"
            "Fixed. Historical entry preserved below.\n\n"
            "<details><summary>Original entry</summary>\n\n"
            "## old problem was 6-12x over target\n\n"
            "lots of stale detail\n\n</details>\n\n"
            "## still open thing\n\nreal work.\n"
        )
        items = parse_todo(text)
        titles = [i["title"] for i in items]
        self.assertNotIn("old problem was 6-12x over target", titles)
        self.assertEqual(sum(1 for i in items if i["status"] == "done"), 1)
        self.assertIn("still open thing", titles)


if __name__ == "__main__":
    unittest.main()
