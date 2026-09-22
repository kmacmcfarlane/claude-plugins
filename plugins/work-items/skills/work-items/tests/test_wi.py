"""Tests for the wi work-item CLI.

Fixtures under tests/fixtures/ are excerpts copied from the real
{brainboy,clustertool,opencode,ptp}/TODO.md files — the live files are never
read here. The backlog-yaml export is validated against the claude-sandbox
scaffold's backlog.py `validate --strict` when that script is invocable, and
falls back to a structural assertion otherwise.
"""
import contextlib
import difflib
import errno
import hashlib
import importlib.util
import io
import itertools
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

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


# Characters the escape bug fed on, plus the ones a bare scalar cannot hold.
ESCAPE_ALPHABET = (':', '"', '\\', '#', ' ', "'", ',', '[', ']', '{', '}', '-',
                   '—', 'é', '日', '🙂', '\t', '\x07', '\x1b', '\x85',
                   '\u2028', '\ufeff', 'a', 'Z', '0', '&', '*', '!', '|', '>',
                   '%', '@', '`', '?', '\ufffe', '\uffff')


def escape_values(count=400, seed=0x0401):
    import random
    rng = random.Random(seed)
    fixed = ['x: "y"', 'x: \\"y\\"', '\\', '"', '""', 'a\\', ' lead',
             'trail ', ' both ', 'c:\\dir', 'x: c:\\dir', '#hash', 'a #b',
             'end:', '—', '— x', "it's", "'q'", '"q"', 'a, b', '[x]',
             '\\\\\\"', 'say "hi"', '日本: "語"', 'a\tb', 'ab\t c',
             '\t', 'x\ufffey', '\uffff']
    for v in fixed:
        yield v
    for _ in range(count):
        yield "".join(rng.choice(ESCAPE_ALPHABET)
                      for _ in range(rng.randint(1, 12)))
    # a tab among characters that alone would stay bare: a bare tab is
    # the one thing a YAML loader rejects that wi read back fine
    for _ in range(count // 8):
        yield "".join(rng.choice("ab c1\t") for _ in range(rng.randint(2, 8)))


class TestScalarRoundTrip(WiTestCase):
    """emit and parse are exact inverses (0401): no rewrite ever changes a
    value, and a quoted value never gains a backslash."""

    def meta_for(self, v):
        return {"id": "rt-0001", "title": v, "tags": [v, "plain"],
                "refs": [v], "x_backlog": {"k": v}}

    def front_text(self, v):
        """emit_front's layout for meta_for(v). The writer refuses a control
        character in a value, so for those the same lines are built from
        _emit_scalar directly: the scalar contract still round-trips."""
        if not wi._FRONT_REFUSE_RE.search(v):
            return wi.emit_front(self.meta_for(v))
        with self.assertRaises(wi.WiError):
            wi.emit_front(self.meta_for(v))
        e = wi._emit_scalar
        return (f"id: rt-0001\ntitle: {e(v)}\ntags: [{e(v, flow=True)}, plain]"
                f"\nrefs:\n  - {e(v)}\nx_backlog:\n  k: {e(v)}")

    def test_parse_emit_is_identity_in_every_context(self):
        for v in escape_values():
            with self.subTest(v=v):
                text = self.front_text(v)
                meta, _, errors = wi.parse_front(text.split("\n"))
                self.assertEqual(errors, [])
                self.assertEqual(meta["title"], v)
                self.assertEqual(meta["tags"], [v, "plain"])
                self.assertEqual(meta["refs"], [v])
                self.assertEqual(meta["x_backlog"], {"k": v})
                # emit -> parse -> emit is stable
                self.assertEqual(wi.emit_front(meta, plain=False), text)

    def test_emitted_front_matter_is_yaml_a_strict_loader_agrees_with(self):
        try:
            from ruamel.yaml import YAML
        except ImportError:
            self.skipTest("ruamel.yaml not installed")
        import io
        yaml = YAML(typ="safe")
        for v in escape_values(count=150):
            if v.strip() in ("", "—"):
                continue  # wi reads these as "no value"; YAML has no such rule
            with self.subTest(v=v):
                text = self.front_text(v)
                loaded = yaml.load(io.StringIO(text))
                if not isinstance(loaded["title"], str):
                    continue  # YAML types a bare 0 / true; wi keeps strings
                self.assertEqual(loaded["title"], v)
                self.assertEqual(loaded["tags"], [v, "plain"])
                self.assertEqual(loaded["refs"], [v])
                self.assertEqual(loaded["x_backlog"], {"k": v})

    def test_item_render_is_byte_stable_across_rewrites(self):
        for v in escape_values(count=100):
            if v.strip() in ("", "—") or wi._FRONT_REFUSE_RE.search(v):
                continue  # the writer refuses control characters
            with self.subTest(v=v):
                item = wi.Item(dict(self.meta_for(v), type="task",
                                    status="todo", priority=2),
                               [], "desc", [])
                first = item.render()
                again = wi.Item.parse(first)
                self.assertEqual(again.get("title"), v)
                again.meta["priority"] = 3
                again.meta["priority"] = 2
                self.assertEqual(wi.Item.parse(again.render()).render(), first)

    def test_reported_case_survives_real_commands(self):
        title = 'x: "y" \\z'
        tag = 'k: "v", \\w'
        reason = 'ext: waits on "a: b" \\ c'
        iid = json.loads(self.wi_ok(["add", title, "--tag", tag,
                                     "--dep", reason, "--json"]))["id"]
        path = self.root / "items" / f"{iid}.md"
        written = path.read_text()
        self.assertIn('title: "x: \\"y\\" \\\\z"\n', written)
        for args in (["set", iid, "priority", "1"],
                     ["set", iid, "priority", "3"],
                     ["handoff", iid, "--next", "go"],
                     ["handoff", iid, "--doing", "more"],
                     ["set", iid, "priority", "2"]):
            self.wi_ok(args)
        rec = json.loads(self.wi_ok(["show", iid, "--json"]))
        self.assertEqual(rec["title"], title)
        self.assertEqual(rec["tags"], [tag])
        self.assertEqual(rec["deps"], [reason])
        fm = lambda t: t.split("\n---\n", 1)[0]
        self.assertEqual(fm(path.read_text()).replace("priority: 2", ""),
                         fm(written).replace("priority: 2", ""))
        self.wi_ok(["done", iid])
        rec = json.loads(self.wi_ok(["show", iid, "--json"]))
        self.assertEqual((rec["title"], rec["tags"], rec["deps"]),
                         (title, [tag], [reason]))
        self.assertEqual(path.read_text().count("\\"), written.count("\\"))

    def test_hand_written_legacy_scalars_still_load(self):
        text = CANONICAL.replace(
            "title: Replication task 3 destination retention is a no-op",
            "title: 'it''s \"fine\"'\nnote_a: \"bad \\q escape\"\n"
            "note_b: \"unterminated \\\"\nnote_c: \"a\\nb\"")
        item = wi.Item.parse(text, path="x.md")
        self.assertEqual(item.get("title"), 'it\'s "fine"')
        self.assertEqual(item.get("note_a"), "bad \\q escape")
        self.assertEqual(item.get("note_b"), "unterminated \\")
        self.assertEqual(item.get("note_c"), "a\\nb")  # never a line break
        out = item.render()
        self.assertEqual(wi.Item.parse(out).render(), out)


    def test_tab_and_reader_hostile_characters_are_never_bare(self):
        for v in ("a\tb", "ab\t c", "x\ufffey", "\ud800"):
            with self.subTest(v=v):
                out = wi._emit_scalar(v)
                self.assertTrue(out.startswith('"'), out)
                self.assertNotIn("\t", out)
                self.assertEqual(wi._parse_scalar(out)[0], v)
        self.assertEqual(wi._emit_scalar("a\tb"), '"a\\tb"')

    def test_yaml_value_and_merge_keys_are_quoted(self):
        try:
            from ruamel.yaml import YAML
        except ImportError:
            self.skipTest("ruamel.yaml not installed")
        for v in ("=", "<<"):
            with self.subTest(v=v):
                text = wi.emit_front({"title": v, "tags": [v]})
                self.assertEqual(text, f'title: "{v}"\ntags: ["{v}"]')
                self.assertEqual(YAML(typ="safe").load(text),
                                 {"title": v, "tags": [v]})
                self.assertEqual(wi.parse_front(text.split("\n"))[0],
                                 {"title": v, "tags": [v]})

    def test_writer_refuses_a_tab_or_control_character(self):
        iid = json.loads(self.wi_ok(["add", "fine", "--json"]))["id"]
        path = self.root / "items" / f"{iid}.md"
        before = path.read_bytes()
        items_before = sorted(p.name for p in (self.root / "items").iterdir())
        for args in (["add", "tab\there"], ["add", "ok", "--tag", "t\tg"],
                     ["add", "bell\x07"], ["set", iid, "title", "x\ty"],
                     ["set", iid, "tags", "a\x1bb"], ["block", iid, "why\there"]):
            with self.subTest(args=args):
                r = run(args, self.root)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("control character", r.stderr)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(sorted(p.name for p in
                                        (self.root / "items").iterdir()),
                                 items_before)

    def test_import_folds_control_characters(self):
        src = self.tmp / "in.yaml"
        src.write_text("schema_version: 2\nstories:\n  - id: S-001\n"
                       '    title: "tab\\there\\x07bell"\n    status: blocked\n'
                       '    priority: 50\n    blocked_reason: "C:\\temp"\n')
        self.wi_ok(["import", "--format", "backlog-yaml", str(src)])
        rec = json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))[0]
        one = json.loads(self.wi_ok(["show", rec["id"], "--json"]))
        self.assertEqual(one["title"], "tab here bell")
        self.assertEqual(one["blocked"], "C: emp")
        self.wi_ok(["lint"])

    def test_lint_is_clean_on_everything_wi_writes(self):
        odd = [v for v in escape_values(count=60)
               if v.strip() and v.strip() == v and not wi._CONTROL_RE.search(v)
               and v not in ("—",) and not wi._LINE_BREAK_RE.search(v)
               and len(v) <= 120]
        dep = json.loads(self.wi_ok(["add", "dep", "--json"]))["id"]
        for v in odd[:40]:
            iid = json.loads(self.wi_ok(["add", v, "--tag", v, "--json"]))["id"]
            self.wi_ok(["set", iid, "parent", dep])
            self.wi_ok(["block", iid, v])
        self.assertIn("lint clean", self.wi_ok(["lint"]))

    def test_unterminated_quote_in_flow_list_reads_the_old_way(self):
        meta, _, errors = wi.parse_front(['tags: ["abc, d, e]'])
        self.assertEqual(errors, [])
        self.assertEqual(meta["tags"], ['"abc', "d", "e"])

    def test_hand_written_backslash_path_is_a_lint_finding(self):
        self.write_item("path-1111")
        self.write_item("temp-2222")
        self.write_item("clean-3333", title="C:\\temp")  # wi-written: fine
        for iid, raw in (("path-1111", '"C:\\Users\\foo\\bar"'),
                         ("temp-2222", '"C:\\temp\\tools"')):
            p = self.root / "items" / f"{iid}.md"
            p.write_text(p.read_text().replace(f"title: {iid}", f"title: {raw}"))
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("path-1111.md: front-matter 'title' holds a control", r.stdout)
        self.assertIn("wi set path-1111 title", r.stdout)
        # \t is the likeliest escape in a Windows path: C:<TAB>emp<TAB>ools
        self.assertIn("temp-2222.md: front-matter 'title' holds a control", r.stdout)
        self.assertNotIn("clean-3333", r.stdout)

    def test_import_reads_a_dash_placeholder_as_no_value(self):
        src = self.tmp / "in.yaml"
        src.write_text("schema_version: 2\nstories:\n  - id: S-001\n"
                       "    title: t\n    status: todo\n    priority: 50\n"
                       '    review_feedback: "—"\n    claimed_by: "—"\n')
        self.wi_ok(["import", "--format", "backlog-yaml", str(src)])
        rec = json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))[0]
        one = json.loads(self.wi_ok(["show", rec["id"], "--json"]))
        self.assertIsNone(one.get("feedback"))
        self.assertIsNone(one.get("owner"))
        text = (self.root / "items" / (rec["id"] + ".md")).read_text()
        self.assertNotIn("—\"", text)

    def test_import_reads_a_blank_blocked_reason_as_no_value(self):
        src = self.tmp / "in.yaml"
        src.write_text("schema_version: 2\nstories:\n  - id: S-001\n"
                       "    title: t\n    status: todo\n"
                       '    blocked_reason: "   "\n')
        self.wi_ok(["import", "--format", "backlog-yaml", str(src)])
        rec = json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))[0]
        one = json.loads(self.wi_ok(["show", rec["id"], "--json"]))
        self.assertIsNone(one.get("blocked"))
        self.assertFalse(one.get("deps"))
        text = (self.root / "items" / (rec["id"] + ".md")).read_text()
        self.assertNotIn("\nblocked:", text)
        self.wi_ok(["lint"])


class TestRepairEscapes(WiTestCase):
    AMPLIFIED = 'title: "x: \\\\\\\\\\\\\\"y\\\\\\\\\\\\\\""'  # "y" after 3 rewrites

    def seed(self):
        self.write_item("amp-1111")
        self.write_item("legit-2222", title="x: c:\\dir \\n")
        path = self.root / "items" / "amp-1111.md"
        path.write_text(path.read_text().replace("title: amp-1111", self.AMPLIFIED))
        return path

    def test_amplified_item_loads_and_dry_run_names_it(self):
        path = self.seed()
        before = path.read_bytes()
        self.assertEqual(run(["lint"], self.root).returncode, 0)
        out = self.wi_ok(["repair-escapes"])
        self.assertIn("would repair\tamp-1111\ttitle", out)
        self.assertIn('-> "x: \\"y\\""', out)
        self.assertNotIn("legit-2222", out)
        self.assertIn("1 to repair (dry run", out)
        self.assertEqual(path.read_bytes(), before)

    def test_apply_repairs_and_is_then_clean(self):
        path = self.seed()
        self.wi_ok(["repair-escapes", "--apply"])
        self.assertIn('title: "x: \\"y\\""\n', path.read_text())
        rec = json.loads(self.wi_ok(["show", "amp-1111", "--json"]))
        self.assertEqual(rec["title"], 'x: "y"')
        self.assertIn("0 to repair", self.wi_ok(["repair-escapes"]))

    def test_id_limits_the_repair(self):
        path = self.seed()
        before = path.read_bytes()
        self.wi_ok(["repair-escapes", "--apply", "--id", "legit-2222"])
        self.assertEqual(path.read_bytes(), before)

    def amplify(self, iid, extra=""):
        path = self.root / "items" / f"{iid}.md"
        path.write_text(path.read_text().replace(
            f"title: {iid}", self.AMPLIFIED + extra))
        return path

    def test_id_repairs_one_and_leaves_another_amplified_item_alone(self):
        self.write_item("amp-1111")
        self.write_item("amp-2222")
        one, two = self.amplify("amp-1111"), self.amplify("amp-2222")
        before = two.read_bytes()
        out = self.wi_ok(["repair-escapes", "--apply", "--id", "amp-1111"])
        self.assertIn("repaired\tamp-1111\ttitle", out)
        self.assertNotIn("amp-2222", out)
        self.assertIn('title: "x: \\"y\\""\n', one.read_text())
        self.assertEqual(two.read_bytes(), before)
        self.assertIn("amp-2222", self.wi_ok(["repair-escapes"]))

    def test_lists_and_maps_and_key_filter(self):
        self.write_item("amp-1111")
        amp = '"a\\\\\\"b"'  # a"b after two rewrites
        path = self.amplify("amp-1111", f"\ntags: [{amp}, plain]\n"
                            f"refs:\n  - {amp}\n  - plain\n"
                            f"x_backlog:\n  k: {amp}\n  j: plain")
        dry = self.wi_ok(["repair-escapes"])
        for key in ("title", "tags", "refs", "x_backlog"):
            self.assertIn(f"would repair\tamp-1111\t{key}\t", dry)
        self.assertIn("4 to repair", dry)
        self.wi_ok(["repair-escapes", "--apply", "--key", "tags"])
        rec = json.loads(self.wi_ok(["show", "amp-1111", "--json"]))
        self.assertEqual(rec["tags"], ['a"b', "plain"])
        self.assertIn("3 to repair", self.wi_ok(["repair-escapes"]))
        self.wi_ok(["repair-escapes", "--apply"])
        item = wi.Item.parse(path.read_text())
        self.assertEqual(item.get("refs"), ['a"b', "plain"])
        self.assertEqual(item.get("x_backlog"), {"k": 'a"b', "j": "plain"})
        self.assertEqual(item.get("title"), 'x: "y"')

    def test_heuristic_also_lists_a_value_meant_with_escapes(self):
        """Documented limit: a value whose backslashes all pair is listed
        whether or not an older wi amplified it — review the dry run."""
        title = 'wi: document why \\" and \\\\ are escaped'
        iid = json.loads(self.wi_ok(["add", title, "--json"]))["id"]
        path = self.root / "items" / f"{iid}.md"
        before = path.read_bytes()
        self.assertIn(iid, self.wi_ok(["repair-escapes"]))
        self.assertEqual(path.read_bytes(), before)  # dry run writes nothing


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

    def test_multiline_titles_are_folded_to_one_line(self):
        """import-todo titles never carry a line break into front matter: a
        bold title wrapped across lines, or with CR/CRLF, is folded."""
        todo = self.tmp / "TODO.md"
        todo.write_bytes(b"- **Wrapped\r\n  title: here** \xe2\x80\x94 body\r\n"
                         b"- **Second\r  one.** rest\n")
        self.wi_ok(["import-todo", str(todo)])
        titles = sorted(it["title"] for it in self.items())
        self.assertEqual(titles, ["Second one", "Wrapped title: here"])
        self.wi_ok(["lint"])

    def import_one(self, line):
        """Import a one-entry TODO.md into a fresh store; return its item."""
        self.root = Path(tempfile.mkdtemp(dir=self.tmp)) / ".work"
        self.assertEqual(run(["init"], self.root).returncode, 0)
        todo = self.tmp / "TODO.md"
        todo.write_text("# TODO\n\n" + line + "\n")
        self.wi_ok(["import-todo", str(todo)])
        items = self.items()
        self.assertEqual(len(items), 1, items)
        return items[0]

    def test_strike_over_only_the_bold_title_is_closed(self):
        """bf1b: `~~**Title**~~ rest` imported open with the markers in the
        title. A strike covering the whole title closes the entry, whichever
        side of the bold it sits on; ~~ and ** are stripped."""
        for line in ("- [ ] ~~**Retire the old runner**~~ rest of it",
                     "- [ ] **~~Retire the old runner~~** — rest of it",
                     "- [ ] ~~**Retire the old runner.**~~ rest of it"):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]),
                                 ("Retire the old runner", "done"))
                self.assertTrue(it["closed"])

    def test_strike_over_the_whole_entry_is_closed(self):
        for line, title in (("- [ ] ~~**Retire the old runner** rest~~",
                             "Retire the old runner"),
                            ("- [ ] ~~plain struck entry~~", "plain struck entry")):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]), (title, "done"))

    def test_checked_box_with_title_strike_is_done_and_stripped(self):
        it = self.import_one("- [x] ~~**Retire the old runner**~~ rest")
        self.assertEqual((it["title"], it["status"]),
                         ("Retire the old runner", "done"))

    def test_partial_strikes_stay_open(self):
        """A strike over part of the title, or over only the trailing text,
        is an edit, not a closure — the rule closes an entry only when the
        strike covers its whole title — so the entry stays open and the
        struck text is kept as written."""
        for line, title in (("- [ ] **Retire ~~the old~~ runner** rest",
                             "Retire ~~the old~~ runner"),
                            ("- [ ] **Retire the old runner** ~~was 5 hosts~~ 3",
                             "Retire the old runner")):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]), (title, "todo"))

    def test_whole_entry_strike_judged_on_the_title_line(self):
        """A whole-entry strike closes the entry when it opens on the bold
        title and closes on that line: continuation lines, and a note after
        the strike on the same line, are description (the trailing-note case
        is closed — the strike covers the whole title)."""
        for line, desc in (
                ("- [ ] ~~**Retire the old runner** rest~~\n  → done in abc123",
                 "rest\n→ done in abc123"),
                ("- [ ] ~~**Retire the old runner** rest~~ (done 2026-09-01)",
                 "rest (done 2026-09-01)"),
                ("- [ ] ~~**Retire the old runner** rest~~ then ~~more~~",
                 "rest then ~~more~~")):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]),
                                 ("Retire the old runner", "done"))
                show = json.loads(self.wi_ok(["show", it["id"], "--json"]))
                self.assertEqual(show["body"].strip(), desc)

    def test_plain_struck_first_line_closes_only_on_a_closure_note(self):
        """With no bold, a struck first line closes when nothing follows it,
        a parenthesis follows, or a dash then a closure word or a date."""
        for line in ("- [ ] ~~Migrate to PG15~~",
                     "- [ ] ~~Migrate to PG15~~ — DONE 2026-09-01",
                     "- [ ] ~~Migrate to PG15~~ — fixed",
                     "- [ ] ~~Migrate to PG15~~ - 2026-09-01",
                     "- [ ] ~~Migrate to PG15~~ (2026-09-01)",
                     "- [ ] ~~Migrate to PG15~~ (done)"):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]),
                                 ("Migrate to PG15", "done"))

    def test_plain_struck_first_line_replaced_or_partial_stays_open(self):
        """`~~X~~ — Y instead` is a replacement, and `~~X~~ rest` a strike
        over part of the title: both stay open with their markers."""
        for line in ("- [ ] ~~Migrate to PG15~~ — PG16 instead",
                     "- [ ] ~~Migrate~~ to PG15"):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]),
                                 (line[6:], "todo"))

    def test_plain_struck_first_line_with_a_caveat_stays_open(self):
        """A parenthesis closes only when it opens on a closure word or a
        date, and a closure word must be a whole word: `fixed-width`,
        `closed-source`, `done-ish` and `done?` are not closures."""
        for line in ("- [ ] ~~Use Redis~~ (use Memcached instead)",
                     "- [ ] ~~Use Redis~~ (not yet)",
                     "- [ ] ~~Use Redis~~ — fixed-width font",
                     "- [ ] ~~Use Redis~~ — closed-source alternative",
                     "- [ ] ~~Use Redis~~ — done-ish, reopen",
                     "- [ ] ~~Use Redis~~ — done? not yet"):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]),
                                 (line[6:], "todo"))

    def test_empty_strike_never_closes(self):
        for line in ("- [ ] ~~ ~~", "- [ ] ~~** **~~ rest"):
            with self.subTest(line=line):
                it = self.import_one(line)
                self.assertEqual((it["title"], it["status"]), (line[6:], "todo"))
                self.wi_ok(["lint"])

    def test_whole_entry_strike_joins_inside_and_after_with_a_space(self):
        it = self.import_one("- [ ] ~~**Retire the old runner** x~~y")
        self.assertEqual(it["status"], "done")
        show = json.loads(self.wi_ok(["show", it["id"], "--json"]))
        self.assertEqual(show["body"].strip(), "x y")

    def test_strike_in_rest_after_a_struck_title_is_kept(self):
        it = self.import_one("- [ ] ~~**Retire the old runner**~~ rest ~~old~~ new")
        self.assertEqual((it["title"], it["status"]),
                         ("Retire the old runner", "done"))
        show = json.loads(self.wi_ok(["show", it["id"], "--json"]))
        self.assertEqual(show["body"].strip(), "rest ~~old~~ new")

    def test_reimport_skips_entries_imported_under_the_pre_bf1b_title(self):
        """Before bf1b a struck entry imported open under its literal first
        line; a re-import must recognise that item by its old marker and
        create nothing, keeping import-todo idempotent across the fix."""
        entries = ("- [ ] ~~**Retire runner**~~ rest",
                   "- [ ] ~~**Whole thing** rest~~")
        legacy = ("~~**Retire runner**~~ rest", "~~**Whole thing** rest~~")
        for n, title in enumerate(legacy):
            self.write_item(f"legacy-{n}", title,
                            refs=[wi.todo_marker(title)])
        todo = self.tmp / "TODO.md"
        todo.write_text("# TODO\n\n" + "\n".join(entries) + "\n")
        out = self.wi_ok(["import-todo", str(todo)])
        self.assertNotIn("created", out)
        self.assertEqual(out.count("skipped"), 2)
        self.assertEqual(len(self.items()), 2)

    def test_literal_tilde_in_title_is_not_a_strike(self):
        it = self.import_one("- [ ] **Move ~/bin to ~5 GiB disk** rest")
        self.assertEqual((it["title"], it["status"]),
                         ("Move ~/bin to ~5 GiB disk", "todo"))

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

    def test_import_folds_multiline_values(self):
        """Block scalars and multi-line titles fold to one line; the store
        stays loadable and every story is imported."""
        src = self.tmp / "in.yaml"
        src.write_text(
            "schema_version: 2\nstories:\n"
            "  - id: S-001\n    title: \"two\\nlines\"\n    status: blocked\n"
            "    priority: 50\n    review_feedback: |\n      first point\n"
            "      status: done\n    blocked_reason: >-\n      a\n\n      b\n"
            "    acceptance:\n      - \"x\\n## Handoff\"\n    odd_field: |\n"
            "      p\n      q\n"
            "  - id: S-002\n    title: plain\n    status: todo\n"
            "    requires: [S-001]\n")
        self.wi_ok(["import", "--format", "backlog-yaml", str(src)])
        recs = {r["alias"]: r for r in json.loads(
            self.wi_ok(["ls", "--status", "all", "--json"]))}
        self.assertEqual(set(recs), {"S-001", "S-002"})
        one = json.loads(self.wi_ok(["show", recs["S-001"]["id"], "--json"]))
        self.assertEqual(one["title"], "two lines")
        self.assertEqual(one["feedback"], "first point status: done")
        self.assertEqual(one["blocked"], "a b")
        self.assertEqual(one["status"], "blocked")
        self.assertEqual(recs["S-002"]["deps"], [one["id"]])
        text = (self.root / "items" / (one["id"] + ".md")).read_text()
        self.assertIn("- [ ] x ## Handoff\n", text)
        self.assertIn("odd_field: p q", text)
        self.assertEqual(text.count("\n## Handoff"), 1)
        self.wi_ok(["lint"])
        # --update folds too
        src.write_text("schema_version: 2\nstories:\n  - id: S-001\n"
                       "    title: t\n    status: blocked\n    blocked_reason: r\n"
                       "    review_feedback: |\n      again\n      here\n")
        self.wi_ok(["import", "--format", "backlog-yaml", "--update", str(src)])
        one = json.loads(self.wi_ok(["show", recs["S-001"]["id"], "--json"]))
        self.assertEqual(one["feedback"], "again here")
        self.wi_ok(["lint"])

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


class TestIdCollisions(WiTestCase):
    """A 4-hex suffix repeats; a repeat must be retried, never written over
    an item (5408: a fresh import of same-slug titles lost one)."""

    @staticmethod
    def repeating_urandom(n=3):
        """os.urandom whose bytes change only every n calls, so the same
        title draws the same suffix n times running."""
        calls = itertools.count()
        return lambda k: (next(calls) // n).to_bytes(k, "big")

    def wi_main(self, argv, urandom):
        err = io.StringIO()
        with mock.patch.object(wi.os, "urandom", urandom), \
                contextlib.redirect_stderr(err), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = wi.main(["--root", str(self.root)] + argv)
        return rc, err.getvalue()

    def files(self):
        return sorted(p.name for p in (self.root / "items").glob("*.md"))

    def test_add_retries_a_repeated_suffix(self):
        fake = self.repeating_urandom()
        for _ in range(5):
            rc, err = self.wi_main(["add", "dup"], fake)
            self.assertEqual(rc, 0, err)
        recs = json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))
        self.assertEqual(len(recs), 5)
        self.assertEqual(len({r["id"] for r in recs}), 5)
        self.assertEqual(len(self.files()), 5)
        self.wi_ok(["lint"])

    def test_fresh_import_of_same_slug_titles_keeps_every_item(self):
        src = self.tmp / "in.yaml"
        src.write_text("schema_version: 2\nstories:\n" + "".join(
            f"  - id: S-{i:03d}\n    title: dup\n    status: todo\n"
            for i in range(44)))
        rc, err = self.wi_main(["import", "--format", "backlog-yaml", str(src)],
                               self.repeating_urandom())
        self.assertEqual(rc, 0, err)
        recs = json.loads(self.wi_ok(["ls", "--status", "all", "--json"]))
        self.assertEqual(sorted(r["alias"] for r in recs),
                         [f"S-{i:03d}" for i in range(44)])
        self.assertEqual(len({r["id"] for r in recs}), 44)
        self.assertEqual(len(self.files()), 44)
        self.wi_ok(["lint"])

    @staticmethod
    def zero_suffix(title):
        """The suffix a draw makes when os.urandom returns zero bytes."""
        return hashlib.sha1((title + wi.today()).encode() + bytes(8)).hexdigest()[:4]

    def test_import_update_new_item_skips_an_id_in_the_store(self):
        taken = "dup-" + self.zero_suffix("dup")
        self.write_item(taken, "kept")
        before = (self.root / "items" / f"{taken}.md").read_text()
        # the store's id and then a free one
        seq = iter([bytes(8), bytes(8), b"\x01" * 8])
        src = self.tmp / "in.yaml"
        src.write_text("schema_version: 2\nstories:\n"
                       "  - id: S-001\n    title: dup\n    status: todo\n")
        rc, err = self.wi_main(["import", "--format", "backlog-yaml", "--update",
                                str(src)], lambda k: next(seq))
        self.assertEqual(rc, 0, err)
        self.assertEqual((self.root / "items" / f"{taken}.md").read_text(), before)
        self.assertEqual(len(self.files()), 2)
        self.wi_ok(["lint"])

    def test_exhausted_retries_fail_loudly_and_write_nothing(self):
        # the same bytes every draw, and a bound: a retry loop without its
        # ID_TRIES cap fails here instead of hanging the suite
        calls = itertools.count(1)

        def const(k):
            if next(calls) > wi.ID_TRIES + 8:
                raise AssertionError("id retry drew past ID_TRIES: unbounded")
            return bytes(k)
        taken = "dup-" + self.zero_suffix("dup")
        self.write_item(taken, "kept")
        before = (self.root / "items" / f"{taken}.md").read_text()
        rc, err = self.wi_main(["add", "dup"], const)
        self.assertEqual(rc, 3)
        self.assertIn("no free id", err)
        self.assertEqual(self.files(), [f"{taken}.md"])
        self.assertEqual((self.root / "items" / f"{taken}.md").read_text(), before)

    def test_write_layer_refuses_to_overwrite_for_a_new_item(self):
        self.write_item("kept-1111", "kept")
        before = (self.root / "items" / "kept-1111.md").read_text()
        fresh = lambda iid: wi.Item(
            {"id": iid, "title": "new", "status": "todo", "created": "2026-09-01",
             "updated": "2026-09-01"}, [], "", [("Handoff", wi.emit_handoff({}))])
        # a batch whose second item collides: nothing is written
        with self.assertRaises(wi.WiError) as ctx:
            wi.save_items(self.root, [fresh("other-2222"), fresh("kept-1111")])
        self.assertEqual(ctx.exception.code, 3)
        self.assertEqual(self.files(), ["kept-1111.md"])
        self.assertEqual((self.root / "items" / "kept-1111.md").read_text(), before)
        # two new items with one id in one batch
        with self.assertRaises(wi.WiError):
            wi.save_items(self.root, [fresh("twin-3333"), fresh("twin-3333")])
        self.assertEqual(self.files(), ["kept-1111.md"])
        # an id that lives in archive/ is taken too
        (self.root / "archive" / "2026").mkdir(parents=True)
        (self.root / "archive" / "2026" / "gone-4444.md").write_text(before)
        with self.assertRaises(wi.WiError):
            wi.save_items(self.root, [fresh("gone-4444")])
        self.assertEqual(self.files(), ["kept-1111.md"])
        # the create itself is exclusive, even past the up-front check
        path = self.root / "items" / "race-5555.md"
        path.write_text("someone else's\n")
        with self.assertRaises(wi.WiError):
            wi.atomic_write(path, "mine\n", create=True)
        self.assertEqual(path.read_text(), "someone else's\n")
        self.assertEqual(list((self.root / "items").glob("*.tmp*")), [])

    def test_add_skips_a_stray_file_whose_stem_is_not_its_id(self):
        """Only the filename, not any loaded id, holds this id: the stray
        file under the drawn name must survive and the add take another."""
        stray = self.root / "items" / f"dup-{self.zero_suffix('dup')}.md"
        self.write_item("other-9999", "stray")
        (self.root / "items" / "other-9999.md").rename(stray)
        before = stray.read_text()
        seq = iter([bytes(8), b"\x01" * 8])
        rc, err = self.wi_main(["add", "dup"], lambda k: next(seq))
        self.assertEqual(rc, 0, err)
        self.assertEqual(stray.read_text(), before)
        self.assertEqual(len(self.files()), 2)

    def no_links(self):
        def link(src, dst):
            raise OSError(errno.EPERM, "Operation not permitted")
        return mock.patch.object(wi.os, "link", link)

    def failing_replace(self):
        real = os.replace

        def replace(src, dst):
            if Path(dst).suffix == ".md":
                raise OSError(errno.EIO, "Input/output error")
            return real(src, dst)
        return mock.patch.object(wi.os, "replace", replace)

    def test_create_without_hard_links_falls_back_whole(self):
        with self.no_links():
            rc, err = self.wi_main(["add", "fallback"], os.urandom)
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.files()), 1)
        self.assertEqual(list((self.root / "items").glob("*.tmp*")), [])
        self.wi_ok(["lint"])
        # the fallback still refuses an existing file
        path = self.root / "items" / "race-5555.md"
        path.write_text("someone else's\n")
        with self.no_links(), self.assertRaises(wi.WiError):
            wi.atomic_write(path, "mine\n", create=True)
        self.assertEqual(path.read_text(), "someone else's\n")

    def test_create_fallback_failure_leaves_no_file(self):
        self.write_item("kept-1111", "kept")
        with self.no_links(), self.failing_replace():
            rc, err = self.wi_main(["add", "doomed"], os.urandom)
        self.assertEqual(rc, 3)
        self.assertIn("nothing written", err)
        self.assertEqual(self.files(), ["kept-1111.md"])
        self.assertEqual(list((self.root / "items").glob("*.tmp*")), [])
        self.wi_ok(["ls", "--status", "all"])
        self.wi_ok(["lint"])

    def test_archive_without_hard_links_falls_back_whole(self):
        self.write_item("old-1111", status="done", closed="2026-01-02")
        before = (self.root / "items" / "old-1111.md").read_text()
        with self.no_links():
            rc, err = self.wi_main(["archive", "--older-than", "0d"], os.urandom)
        self.assertEqual(rc, 0, err)
        dest = self.root / "archive" / "2026" / "old-1111.md"
        self.assertEqual(dest.read_text(), before)
        self.assertEqual(self.files(), [])
        self.wi_ok(["show", "old-1111", "--brief"])

    def test_archive_fallback_failure_leaves_the_item_in_place(self):
        self.write_item("old-1111", status="done", closed="2026-01-02")
        before = (self.root / "items" / "old-1111.md").read_text()
        with self.no_links(), self.failing_replace():
            rc, err = self.wi_main(["archive", "--older-than", "0d"], os.urandom)
        self.assertEqual(rc, 3)
        self.assertIn("cannot write", err)
        self.assertEqual((self.root / "items" / "old-1111.md").read_text(), before)
        self.assertEqual(list((self.root / "archive").glob("*/*")), [])
        self.wi_ok(["show", "old-1111", "--brief"])
        self.wi_ok(["lint"])

    def test_archive_refuses_to_overwrite_an_archived_file(self):
        self.write_item("old-1111", status="done", closed="2026-01-02")
        dest = self.root / "archive" / "2026" / "old-1111.md"
        dest.parent.mkdir(parents=True)
        dest.write_text("already archived\n")
        r = run(["archive", "--older-than", "0d"], self.root)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertEqual(dest.read_text(), "already archived\n")
        self.assertTrue((self.root / "items" / "old-1111.md").exists())

    def test_archive_finishes_a_move_killed_between_link_and_unlink(self):
        """220b: the hard link landed, the unlink did not. Archive finishes
        the move (whatever the cutoff) instead of refusing forever."""
        self.write_item("old-1111", status="done", closed=wi.today())
        src = self.root / "items" / "old-1111.md"
        before = src.read_text()
        dest = self.root / "archive" / wi.today()[:4] / "old-1111.md"
        dest.parent.mkdir(parents=True)
        os.link(src, dest)
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("`wi archive` finishes the move", r.stdout)
        r = run(["archive"], self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("archived 1", r.stdout)
        self.assertFalse(src.exists())
        self.assertEqual(dest.read_text(), before)
        self.wi_ok(["show", "old-1111", "--brief"])
        self.wi_ok(["lint"])
        # an unrelated file at the destination is still refused
        self.write_item("old-2222", status="done", closed="2026-01-02")
        other = self.root / "archive" / "2026" / "old-2222.md"
        other.write_text(before)
        self.assertEqual(run(["archive", "--older-than", "0d"],
                             self.root).returncode, 3)
        self.assertTrue((self.root / "items" / "old-2222.md").exists())

    def test_archive_refuses_one_file_reached_by_two_paths(self):
        """A destination that is the source's own directory entry, through a
        symlinked directory, is not a half-done move: unlinking the source
        would delete the only copy. Archive refuses and keeps the item."""
        self.write_item("old-1111", status="done", closed="2026-01-02")
        src = self.root / "items" / "old-1111.md"
        before = src.read_text()
        (self.root / "archive").mkdir(exist_ok=True)
        (self.root / "archive" / "2026").symlink_to(Path("..") / "items")
        r = run(["archive", "--older-than", "0d"], self.root)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("already exists", r.stderr)
        self.assertEqual(src.read_text(), before)
        self.assertFalse(wi._half_moved(src, self.root / "archive" / "2026"
                                        / "old-1111.md"))
        # the write layer refuses it too
        with self.assertRaises(wi.WiError):
            wi._move_no_clobber(src, self.root / "archive" / "2026" / "old-1111.md")
        self.assertEqual(src.read_text(), before)

    def test_half_moved_needs_two_links_in_two_directories(self):
        items = self.root / "items"
        a = items / "a-1111.md"
        a.write_text("x\n")
        # the same path twice, and one entry by two spellings of its directory
        self.assertFalse(wi._half_moved(a, a))
        self.assertFalse(wi._half_moved(a, items / ".." / "items" / "a-1111.md"))
        # two links in one directory: identical parents, not an archive move
        b = items / "b-2222.md"
        os.link(a, b)
        self.assertFalse(wi._half_moved(a, b))
        # two links in two directories: the half-done move
        other = self.root / "archive" / "2026"
        other.mkdir(parents=True)
        os.link(a, other / "a-1111.md")
        self.assertTrue(wi._half_moved(a, other / "a-1111.md"))

    def test_lint_fix_quotes_paths(self):
        d = self.tmp / "odd dir"
        d.mkdir()
        (d / "x-1111.md").write_text("")
        self.assertEqual(wi.stale_reservation_fix(d / "x-1111.md"),
                         f"nothing was written to it: rm '{d}/x-1111.md'")
        (d / "x-1111.md.tmp7").write_text("content")
        self.assertIn(f"mv '{d}/x-1111.md.tmp7' '{d}/x-1111.md'",
                      wi.stale_reservation_fix(d / "x-1111.md"))

    def test_empty_item_file_is_a_stale_reservation(self):
        """220b: a kill between the O_EXCL reservation and the rename leaves
        an empty item file. Commands skip it, naming it; lint names the fix;
        its name stays taken."""
        self.write_item("kept-1111", "kept")
        self.write_item("lost-2222", "lost")
        item = self.root / "items" / "lost-2222.md"
        tmp = item.with_name(item.name + ".tmp4242")
        item.rename(tmp)
        item.write_text("")
        r = run(["ls", "--status", "all"], self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("kept-1111", r.stdout)
        self.assertIn(f"skipping {item}", r.stderr)
        self.assertIn("wi lint", r.stderr)
        self.wi_ok(["show", "kept-1111", "--brief"])
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn(f"{item}: empty file", r.stdout)
        self.assertIn(f"mv {tmp} {item}", r.stdout)
        # the reserved name is not handed out again
        self.assertIn("lost-2222", wi.taken_ids(self.root, []))
        # the lint fix restores the item
        tmp.rename(item)
        self.wi_ok(["show", "lost-2222", "--brief"])
        self.wi_ok(["lint"])
        # an archive killed after reserving its destination: source intact,
        # nothing written to the reservation, archive refuses naming it
        self.write_item("old-3333", status="done", closed="2026-01-02")
        dest = self.root / "archive" / "2026" / "old-3333.md"
        dest.parent.mkdir(parents=True)
        dest.write_text("")
        r = run(["archive", "--older-than", "0d"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("empty file", r.stderr)
        self.assertTrue((self.root / "items" / "old-3333.md").exists())
        r = run(["lint"], self.root)
        self.assertIn(f"rm {dest}", r.stdout)
        dest.unlink()
        self.wi_ok(["archive", "--older-than", "0d"])
        self.wi_ok(["lint"])

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

    def assert_claim_refused(self, iid, *named):
        path = self.root / "items" / f"{iid}.md"
        before = path.read_text()
        r = run(["claim", iid], self.root)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        for text in named:
            self.assertIn(text, r.stderr)
        self.assertEqual(path.read_text(), before)  # nothing written
        return r

    def test_claim_refuses_unmet_dep(self):
        # the live-fired case: `block --on` leaves status todo, so only the
        # dep keeps it out of `next`; claim must refuse it the same way
        self.write_item("base-1111")
        self.write_item("kid-2222")
        self.wi_ok(["block", "kid-2222", "--on", "base-1111"])
        self.assertNotIn("kid-2222", self.wi_ok(["next", "--plain"]))
        self.assert_claim_refused("kid-2222", "base-1111 (todo)")

    def test_claim_names_every_unmet_dep_only(self):
        self.write_item("wip-1111", status="doing")
        self.write_item("fin-2222", status="done")
        self.write_item("kid-3333", deps=["wip-1111", "fin-2222", "ext: vendor"])
        r = self.assert_claim_refused("kid-3333", "wip-1111 (doing)",
                                      "ext: vendor (external")
        self.assertNotIn("fin-2222", r.stderr)

    def test_claim_allows_done_and_dropped_deps(self):
        self.write_item("fin-1111", status="done")
        self.write_item("gone-2222", status="dropped")
        self.write_item("kid-3333", deps=["fin-1111", "gone-2222"])
        self.wi_ok(["claim", "kid-3333"])
        rec = json.loads(self.wi_ok(["show", "kid-3333", "--json"]))
        self.assertEqual((rec["status"], rec["owner"]), ("doing", "tester@local"))

    def test_claim_refuses_unknown_dep(self):
        # an id that resolves to no item never counts as met (as in `next`)
        self.write_item("kid-1111", deps=["ghost-9999"])
        self.assert_claim_refused("kid-1111",
                                  "ghost-9999 (unknown: in neither items/")

    def test_next_claim_still_skips_unmet_dep(self):
        self.write_item("base-1111", priority=3)
        self.write_item("kid-2222", priority=0, deps=["base-1111"])
        rec = json.loads(self.wi_ok(["next", "--pipeline", "--one", "--claim",
                                     "worker-1", "--json"]))
        self.assertEqual(rec["id"], "base-1111")

    def test_claim_allows_dep_at_doing_stage_uat(self):
        # 1d1c rider: a dep awaiting UAT counts as met, for claim as for next
        self.write_item("uat-1111", status="doing", stage="uat")
        self.write_item("kid-2222", deps=["uat-1111"])
        self.assertIn("kid-2222", self.wi_ok(["next", "--plain"]))
        self.wi_ok(["claim", "kid-2222"])
        rec = json.loads(self.wi_ok(["show", "kid-2222", "--json"]))
        self.assertEqual((rec["status"], rec["owner"]), ("doing", "tester@local"))

    def test_reclaim_owned_doing_item_with_unmet_deps_unchanged(self):
        # 1d1c rider: the dep gate applies to a todo item only; re-claiming
        # an item this owner already holds stays a no-op success
        self.write_item("base-1111")
        self.write_item("kid-2222", status="doing", deps=["base-1111"],
                        owner="tester@local", claimed="2026-08-01T00:00Z")
        path = self.root / "items" / "kid-2222.md"
        before = path.read_text()
        out = self.wi_ok(["claim", "kid-2222"])
        self.assertIn("claimed kid-2222 as tester@local", out)
        self.assertEqual(path.read_text(), before)

    def archive_by_hand(self, iid):
        """Move an item into archive/ as a file (how a non-closed item gets
        there: `wi archive` moves closed items only)."""
        dest = self.root / "archive" / "2026" / f"{iid}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        (self.root / "items" / f"{iid}.md").rename(dest)

    def assert_ready_everywhere(self, iid, ready):
        """next, next --pipeline, ls --ready and show --json give one answer."""
        check = self.assertIn if ready else self.assertNotIn
        check(iid, run(["next", "--plain"], self.root).stdout)
        check(iid, run(["next", "--pipeline"], self.root).stdout)
        check(iid, run(["ls", "--ready", "--plain"], self.root).stdout)
        prime = run(["prime"], self.root).stdout
        ready_lines = prime[prime.index("READY"):] if "READY" in prime else ""
        check(iid, ready_lines)
        rec = json.loads(self.wi_ok(["show", iid, "--json"]))
        self.assertEqual(rec["ready"], ready)
        self.assertEqual(rec["blocked_by_unresolved"] == [], ready)

    def test_archived_done_dep_is_met_for_next_ls_show_and_claim(self):
        self.write_item("fin-1111", status="done")
        self.write_item("gone-2222", status="dropped")
        self.write_item("kid-3333", deps=["fin-1111", "gone-2222"])
        self.wi_ok(["archive", "--older-than", "0s"])
        self.assertFalse((self.root / "items" / "fin-1111.md").exists())
        self.assertTrue((self.root / "archive" / "2026" / "fin-1111.md").exists())
        self.assert_ready_everywhere("kid-3333", True)
        self.wi_ok(["claim", "kid-3333"])
        rec = json.loads(self.wi_ok(["show", "kid-3333", "--json"]))
        self.assertEqual((rec["status"], rec["owner"]), ("doing", "tester@local"))

    def test_archived_dep_not_closed_is_judged_by_its_status(self):
        self.write_item("wip-1111")
        self.write_item("kid-2222", deps=["wip-1111"])
        self.archive_by_hand("wip-1111")
        self.assert_ready_everywhere("kid-2222", False)
        rec = json.loads(self.wi_ok(["show", "kid-2222", "--json"]))
        self.assertEqual(rec["blocked_by_unresolved"], ["wip-1111"])
        self.assert_claim_refused("kid-2222", "wip-1111 (todo)")
        # the same archived dep at doing+uat is met, as it would be in items/
        self.write_item("uat-3333", status="doing", stage="uat")
        self.write_item("kid-4444", deps=["uat-3333"])
        self.archive_by_hand("uat-3333")
        self.assert_ready_everywhere("kid-4444", True)

    def test_id_in_items_and_archive_items_copy_wins_everywhere(self):
        # a half-finished hand move: the items/ copy (todo) is current, the
        # archive/ copy (done) is stale; every command must judge by items/
        self.write_item("dup-1111", status="done")
        self.archive_by_hand("dup-1111")
        text = (self.root / "archive" / "2026" / "dup-1111.md").read_text()
        text = text.replace("status: done", "status: todo")
        text = re.sub(r"(?m)^closed:.*\n", "", text)
        (self.root / "items" / "dup-1111.md").write_text(text)
        self.write_item("kid-2222", deps=["dup-1111"])
        self.assert_ready_everywhere("kid-2222", False)
        self.assertNotIn("kid-2222", run(["ls", "--status", "all", "--ready",
                                          "--plain"], self.root).stdout)
        self.assert_claim_refused("kid-2222", "dup-1111 (todo)")

    def test_unparseable_archive_file_is_skipped_not_fatal(self):
        self.write_item("fin-1111", status="done")
        self.write_item("kid-2222", deps=["fin-1111"])
        self.write_item("wait-3333", deps=["ghost-9999"])  # forces the read
        self.wi_ok(["archive", "--older-than", "0s"])
        arch = self.root / "archive" / "2026"
        (arch / "junk-aaaa.md").write_text("no front matter here\n")
        (arch / "bin-bbbb.md").write_bytes(b"\xff\xfe\x00garbage\x80")
        for cmd in (["next", "--plain"], ["prime"], ["ls", "--ready", "--plain"]):
            r = run(cmd, self.root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("kid-2222", r.stdout)
            self.assertNotIn("Traceback", r.stderr)
            self.assertIn("junk-aaaa.md", r.stderr)
            self.assertIn("bin-bbbb.md", r.stderr)

    def test_dep_index_reads_the_archive_once_and_only_on_a_miss(self):
        self.write_item("live-1111", status="done")
        for iid in ("fin-2222", "fin-3333"):
            self.write_item(iid, status="done")
            self.archive_by_hand(iid)
        items = wi.load_all(self.root)
        with mock.patch.object(wi, "load_paths", wraps=wi.load_paths) as lp:
            idx = wi.DepIndex(self.root, items)
            self.assertTrue(wi.dep_resolved("live-1111", idx))
            self.assertEqual(lp.call_count, 0)
            self.assertTrue(wi.dep_resolved("fin-2222", idx))
            self.assertTrue(wi.dep_resolved("fin-3333", idx))
            self.assertFalse(wi.dep_resolved("ghost-9999", idx))
            self.assertEqual(lp.call_count, 1)

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


HOST = os.uname().nodename.split(".")[0]


class TestDefaultOwner(WiTestCase):
    """The claimant order: WI_OWNER, $USER, `git config user.name` (from the
    store's repo), getpass.getuser(), `unknown`. Git is isolated from the
    machine's own config (no global/system file, HOME in the temp dir) and
    getpass is mocked, so nothing here reads the real user or git identity."""

    def setUp(self):
        super().setUp()
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.iso = {"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home),
                    "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_SYSTEM": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG_COUNT",
                  "GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
            self.iso[k] = None
        self.no_repo = self.tmp / "no-repo"
        self.no_repo.mkdir()

    def repo_with_name(self, name):
        repo = self.tmp / "repo"
        store = repo / ".work"
        store.mkdir(parents=True, exist_ok=True)
        with self.env():
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            if name is not None:
                subprocess.run(["git", "-C", str(repo), "config", "user.name",
                                name], check=True)
        return store

    @contextlib.contextmanager
    def env(self, **over):
        want = dict(self.iso, WI_OWNER=None, USER=None, LOGNAME=None,
                    LNAME=None, USERNAME=None)
        want.update(over)
        with mock.patch.dict(os.environ):
            for k, v in want.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            yield

    def owner(self, root, getuser="pwuser", **env):
        def fake():
            if isinstance(getuser, Exception):
                raise getuser
            return getuser
        with self.env(**env), mock.patch.object(wi.getpass, "getuser", fake):
            return wi.default_owner(root)

    def test_wi_owner_wins_verbatim(self):
        store = self.repo_with_name("Git Name")
        self.assertEqual(self.owner(store, WI_OWNER="me@box", USER="u"),
                         "me@box")

    def test_user_beats_git(self):
        store = self.repo_with_name("Git Name")
        self.assertEqual(self.owner(store, USER="kyle"), f"kyle@{HOST}")

    def test_git_user_name_when_user_unset(self):
        store = self.repo_with_name("Kyle McFarlane")
        self.assertEqual(self.owner(store), f"Kyle-McFarlane@{HOST}")

    def test_empty_user_counts_as_unset(self):
        store = self.repo_with_name("gitname")
        self.assertEqual(self.owner(store, USER="", WI_OWNER=""),
                         f"gitname@{HOST}")

    def test_git_name_sanitized_to_one_token(self):
        # a space splits `wi status` columns, an @ the user@host split, a
        # leading - reads as a flag; each run of unsafe chars is one -
        store = self.repo_with_name("  -Jo  O'Brien @ Home: #1 ")
        self.assertEqual(self.owner(store), f"Jo-O-Brien-Home-1@{HOST}")

    def test_git_read_from_store_repo_not_cwd(self):
        store = self.repo_with_name("store-user")
        with contextlib.chdir(self.no_repo) if hasattr(contextlib, "chdir") \
                else contextlib.nullcontext():
            self.assertEqual(self.owner(store), f"store-user@{HOST}")

    def test_getpass_when_git_has_no_name(self):
        store = self.repo_with_name(None)
        self.assertEqual(self.owner(store), f"pwuser@{HOST}")

    def test_getpass_when_not_a_repo(self):
        self.assertEqual(self.owner(self.no_repo), f"pwuser@{HOST}")

    def test_git_unusable_name_falls_through(self):
        store = self.repo_with_name("@@@")
        self.assertEqual(self.owner(store), f"pwuser@{HOST}")

    def test_git_failure_skipped(self):
        store = self.repo_with_name("Git Name")
        for failure in (None, subprocess.CompletedProcess([], 1, "", "err")):
            with mock.patch.object(wi, "_git", return_value=failure):
                self.assertEqual(self.owner(store), f"pwuser@{HOST}")

    def test_git_timeout_is_short_and_skipped(self):
        store = self.repo_with_name("Git Name")
        seen = {}

        def slow(*a, **kw):
            seen["timeout"] = kw.get("timeout")
            raise subprocess.TimeoutExpired(a[0], kw.get("timeout"))
        with mock.patch.object(wi.subprocess, "run", slow):
            self.assertEqual(self.owner(store), f"pwuser@{HOST}")
        self.assertLessEqual(seen["timeout"], 5)

    def test_unknown_when_getpass_raises(self):
        self.assertEqual(self.owner(self.no_repo, getuser=KeyError("uid")),
                         f"unknown@{HOST}")
        self.assertEqual(self.owner(self.no_repo, getuser=OSError("none")),
                         f"unknown@{HOST}")

    def test_claim_end_to_end_uses_git_name(self):
        store = self.repo_with_name("Kyle McFarlane")
        self.assertEqual(run(["init"], store).returncode, 0)
        self.root = store
        self.write_item("mine-1111")
        env = dict((k, v) for k, v in self.iso.items() if v is not None)
        full = dict(os.environ, WI_ROOT=str(store), **env)
        for k in ("WI_OWNER", "USER", "GIT_DIR", "GIT_WORK_TREE"):
            full.pop(k, None)
        r = subprocess.run([sys.executable, str(WI), "claim", "mine-1111"],
                           env=full, capture_output=True, text=True,
                           cwd=str(self.no_repo))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"as Kyle-McFarlane@{HOST}", r.stdout)
        rec = json.loads(self.wi_ok(["show", "mine-1111", "--json"]))
        self.assertEqual(rec["owner"], f"Kyle-McFarlane@{HOST}")

    def test_existing_user_claim_still_matches(self):
        # $USER still comes before git: a kyle@host claim made before this
        # change is re-claimed (a no-op) by the same user, not refused
        store = self.repo_with_name("Kyle McFarlane")
        self.assertEqual(run(["init"], store).returncode, 0)
        self.root = store
        self.write_item("held-1111", status="doing", owner=f"kyle@{HOST}",
                        claimed="2026-09-01T10:00Z")
        before = (store / "items" / "held-1111.md").read_text()
        with self.env(USER="kyle"), mock.patch.object(
                wi.getpass, "getuser", lambda: "pwuser"):
            self.assertFalse(wi._claim(wi.load_item_anywhere(store, "held-1111"),
                                       wi.default_owner(store)))
        self.assertEqual((store / "items" / "held-1111.md").read_text(), before)

    def test_old_unknown_claim_needs_pin_or_steal(self):
        # USER was unset before and git now names the user: an item claimed
        # as unknown@host reads as someone else's. release still works (it
        # checks no owner); a re-claim needs --steal, or WI_OWNER pinned to
        # the old spelling, which keeps matching
        store = self.repo_with_name("Kyle McFarlane")
        self.assertEqual(run(["init"], store).returncode, 0)
        self.root = store
        old = f"unknown@{HOST}"
        self.write_item("old-1111", status="doing", owner=old,
                        claimed="2026-09-01T10:00Z")
        with self.env(), mock.patch.object(wi.getpass, "getuser",
                                           lambda: "pwuser"):
            me = wi.default_owner(store)
            self.assertNotEqual(me, old)
            with self.assertRaises(wi.WiError) as cm:
                wi._claim(wi.load_item_anywhere(store, "old-1111"), me)
            self.assertEqual(cm.exception.code, 4)
            stolen = wi.load_item_anywhere(store, "old-1111")
            self.assertTrue(wi._claim(stolen, me, steal=True))
            self.assertEqual(stolen.get("owner"), me)
        with self.env(WI_OWNER=old):
            self.assertEqual(wi.default_owner(store), old)
            self.assertFalse(wi._claim(wi.load_item_anywhere(store, "old-1111"),
                                       wi.default_owner(store)))


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


# Body shapes a hand-edited item can take. Every rewriting command must keep
# every body byte outside the lines it owns: the four Handoff bullets (handoff),
# dated lines appended under ## Notes (claim, done, handoff --learned), and a
# ## Notes section appended at the end when there is none.
BODY_SHAPES = {
    # the e832 shape: unheaded bullets after the Handoff block, Handoff last
    "trailing-unheaded": (
        "\nDesc line.\n\n## Handoff\n- doing: —\n- next: —\n- blocked: —\n"
        "- learned: —\n\n- 2026-09-18 (from 81a5): carry this forward\n\n"
        "- (F0 review lows) keep me too\n"),
    # irregular spacing, stray prose and trailing whitespace between sections
    "between-sections": (
        "\n\n\nDesc   line.  \n\n\n\n## Acceptance\n- [ ] one\n\n\n"
        "loose prose under acceptance\n   \n## Handoff\n\n- doing: x\n"
        "  indented aside\n- next: y\n- blocked: —\n- learned: —\n\t\n\n\n"
        "## Notes\n- 2026-09-01 first\n\n\n"),
    # several ## sections in an unusual order, Handoff in the middle
    "many-sections-any-order": (
        "\nDesc.\n\n## Notes\n- 2026-09-01 early note\n\n## Custom\ncustom body\n"
        "\n## Handoff\n- doing: a\n- next: b\n- blocked: —\n- learned: —\n"
        "\n## Acceptance\n- [x] done thing\n\n## Testing\n- command: make\n"),
    # Handoff not last, extra text inside it, unheaded text after Notes,
    # a key line out of order and a second copy of a key in the trailing text
    "handoff-not-last": (
        "\nDesc.\n\n## Handoff\n- next: n\n- doing: d\n- blocked: —\n"
        "- learned: —\ntrailing text inside handoff\n- doing: not the owned line\n"
        "\n## Notes\n- 2026-09-01 n1\n\nunheaded after notes\n\n## Zeta\nz\n"),
    # no ## Notes at all, trailing text after Handoff
    "no-notes": (
        "\nDesc.\n\n## Handoff\n- doing: —\n- next: —\n- blocked: —\n"
        "- learned: —\n\ntrailing without heading\n"),
    # 23a8: headings (and Handoff bullets) inside fenced code blocks are text;
    # Notes precede the real Handoff and end in a fence
    "fenced-headings": (
        "\nDesc.\n\n~~~\n## Handoff\n- doing: tilde fake\n~~~\n\n"
        "## Notes\n- 2026-09-01 n1\n```markdown\n## Handoff\n- doing: fake\n"
        "- next: fake\n```\n\n## Handoff\n- doing: d\n- next: —\n"
        "- blocked: —\n- learned: —\n"),
    # unclosed fences (a pasted ```sh with no closer, a ```` "closed" by ```)
    # are not fences: the real Handoff after them is still the section
    "unclosed-fence": (
        "\nDesc.\n\n## Notes\n- 2026-09-01 n1\n````\n```\n```sh\nmake\n\n"
        "## Handoff\n- doing: OLD\n- next: OLDNEXT\n- blocked: —\n"
        "- learned: —\n"),
}

NOTE_LINE_RE = re.compile(r"^- \d{4}-\d{2}-\d{2} .*$")


class TestBodyPreservation(WiTestCase):
    """e832: rewrites must not drop or reshape body text they do not own."""

    IID = "keep-body-1111"

    def write_raw(self, body, eol, front_extra=""):
        front = (f"id: {self.IID}\ntitle: keep body\ntype: task\npriority: 2\n"
                 f"{front_extra}created: 2026-08-01\nupdated: 2026-08-01\n")
        text = "---\n" + front + "---\n" + body
        path = self.root / "items" / f"{self.IID}.md"
        path.write_bytes(text.replace("\n", eol).encode())
        return path

    @staticmethod
    def split_body(raw, eol):
        close = eol + "---" + eol
        return raw[raw.index(close, 3) + len(close):]

    @staticmethod
    def lines(text):
        return re.findall(r"[^\n]*\n|[^\n]+\Z", text)

    def owned_handoff_lines(self, body_lines):
        """Indices of the first `- key:` line of each key in ## Handoff. What
        counts as a heading is production's fence rule (wi._heading_flags),
        pinned on its own by test_fenced_headings_are_not_sections and
        test_unclosed_fence_does_not_hide_handoff."""
        owned, seen, inside = set(), set(), False
        flags = wi._heading_flags(body_lines)
        for i, line in enumerate(body_lines):
            if flags[i]:
                if inside:
                    break
                inside = line.rstrip("\r\n") == "## Handoff"
                continue
            m = inside and re.match(r"^- (doing|next|blocked|learned):",
                                    line.rstrip("\r\n"))
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                owned.add(i)
        return owned

    def assert_only_owned_changes(self, before, after, eol, handoff=None,
                                  inserts=False):
        """Everything outside the owned lines is byte-identical: diff ops are
        equal; inserts of note lines / a ## Notes heading / blank lines (when
        `inserts`); and same-count replaces of owned Handoff bullets that keep
        their line ending (when `handoff`)."""
        b, a = self.lines(before), self.lines(after)
        owned = self.owned_handoff_lines(b) if handoff else set()
        sm = difflib.SequenceMatcher(None, b, a, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                continue
            ctx = f"{op} before{b[i1:i2]!r} after{a[j1:j2]!r}"
            if op == "insert" and inserts:
                for line in a[j1:j2]:
                    self.assertTrue(line.endswith(eol), ctx)
                    c = line[:-len(eol)]
                    self.assertTrue(c == "" or c == "## Notes"
                                    or NOTE_LINE_RE.match(c), ctx)
                continue
            self.assertEqual(op, "replace", ctx)
            self.assertEqual(i2 - i1, j2 - j1, ctx)
            for i, j in zip(range(i1, i2), range(j1, j2)):
                self.assertIn(i, owned, ctx)
                key = re.match(r"^- (\w+):", b[i]).group(1)
                ending = b[i][len(b[i].rstrip("\r\n")):]
                self.assertEqual(a[j], f"- {key}: {handoff[key]}" + ending, ctx)
        if handoff:
            # every owned bullet carries its new value
            for i in owned:
                key = re.match(r"^- (\w+):", b[i]).group(1)
                self.assertIn(f"- {key}: {handoff[key]}{eol}", a)

    COMMANDS = {
        # name: (front-matter extra, argv tail, kind)
        "claim": ("status: todo\n", ["claim", IID], "insert"),
        "claim-steal": ("status: doing\nowner: other@x\nclaimed: 2026-09-01T00:00Z\n",
                        ["claim", IID, "--steal"], "insert"),
        "next-claim": ("status: todo\n",
                       ["next", "--pipeline", "--one", "--claim", "w1"], "insert"),
        "release": ("status: doing\nowner: tester@local\nclaimed: 2026-09-01T00:00Z\n",
                    ["release", IID], "same"),
        "handoff": ("status: doing\n",
                    ["handoff", IID, "--doing", "D1", "--next", "N1",
                     "--blocked", "B1"], "handoff"),
        "handoff-learned": ("status: doing\n",
                            ["handoff", IID, "--learned", "L1"], "handoff+insert"),
        "block": ("status: todo\n", ["block", IID, "waiting on vendor"], "same"),
        "block-on": ("status: todo\n", ["block", IID, "--on", "other-2222"], "same"),
        "unblock": ("status: blocked\nblocked: vendor\n", ["unblock", IID], "same"),
        "unblock-dep": ("status: todo\ndeps:\n  - other-2222\n",
                        ["unblock", IID, "--dep", "other-2222"], "same"),
        "set": ("status: todo\n", ["set", IID, "priority", "0"], "same"),
        "park": ("status: doing\nowner: w1\nclaimed: 2026-09-01T00:00Z\n",
                 ["park", IID, "not this quarter"], "insert"),
        "unpark": ("status: parked\nparked: later\n", ["unpark", IID], "insert"),
        "migrate-parked": ("status: blocked\nblocked: \"PARKED: later\"\n",
                           ["migrate-parked", "--apply"], "insert"),
        "release-parked": ("status: parked\nparked: later\n",
                           ["release", IID], "same"),
        "set-unpark": ("status: parked\nparked: later\n",
                       ["set", IID, "status", "todo"], "insert"),
        "done": ("status: doing\n", ["done", IID, "--note", "shipped"], "insert"),
        "drop": ("status: todo\n", ["done", IID, "--drop"], "insert"),
        "export": ("status: todo\n", ["export", "OUT", "--format", "backlog-yaml",
                                      "--project", "t"], "same"),
        "import-update": ("status: todo\nalias: S-001\n",
                          ["import", "--format", "backlog-yaml", "--update", "IN"],
                          "same"),
    }

    IMPORT_YAML = ("schema_version: 2\nstories:\n  - id: S-001\n"
                   "    title: keep body\n    status: in_progress\n"
                   "    priority: 50\n    claimed_by: w9\n")

    def run_matrix(self, names):
        for shape, body in BODY_SHAPES.items():
            for eol in ("\n", "\r\n"):
                for name in names:
                    front, argv, kind = self.COMMANDS[name]
                    with self.subTest(shape=shape, eol=repr(eol), command=name):
                        shutil.rmtree(self.root / "items")
                        (self.root / "items").mkdir()
                        self.write_item("other-2222", status="done")
                        path = self.write_raw(body, eol, front)
                        before = self.split_body(path.read_bytes().decode(), eol)
                        (self.tmp / "in.yaml").write_text(self.IMPORT_YAML)
                        argv = [str(self.tmp / "b.yaml") if a == "OUT" else
                                str(self.tmp / "in.yaml") if a == "IN" else a
                                for a in argv]
                        self.wi_ok(argv)
                        raw = path.read_bytes().decode()
                        if eol == "\r\n":
                            self.assertNotIn("\n", raw.replace("\r\n", ""))
                        after = self.split_body(raw, eol)
                        if kind == "same":
                            self.assertEqual(after, before)
                            continue
                        h = None
                        if kind.startswith("handoff"):
                            b_lines = self.lines(before)
                            old = wi.parse_handoff("".join(
                                b_lines[i] for i in sorted(
                                    self.owned_handoff_lines(b_lines)))
                                .replace("\r\n", "\n"))
                            h = {k: getattr_arg(argv, k) or old[k] or "—"
                                 for k in wi.HANDOFF_KEYS}
                        self.assert_only_owned_changes(
                            before, after, eol, handoff=h,
                            inserts=kind.endswith("insert"))
                        if kind.endswith("insert"):
                            self.assertGreater(len(after), len(before))

    def test_claim_and_next_claim_keep_body(self):
        self.run_matrix(["claim", "claim-steal", "next-claim"])

    def test_release_keeps_body(self):
        self.run_matrix(["release"])

    def test_handoff_keeps_body(self):
        self.run_matrix(["handoff", "handoff-learned"])

    def test_block_unblock_keep_body(self):
        self.run_matrix(["block", "block-on", "unblock", "unblock-dep"])

    def test_set_keeps_body(self):
        self.run_matrix(["set"])

    def test_park_unpark_migrate_keep_body(self):
        self.run_matrix(["park", "unpark", "migrate-parked", "release-parked",
                         "set-unpark"])

    def test_done_and_drop_keep_body(self):
        self.run_matrix(["done", "drop"])

    def test_export_alias_writeback_keeps_body(self):
        self.run_matrix(["export"])

    def test_import_update_keeps_body(self):
        self.run_matrix(["import-update"])
        # the update did land: pipeline fields changed, body did not
        rec = json.loads(self.wi_ok(["show", self.IID, "--json"]))
        self.assertEqual((rec["status"], rec["stage"], rec["owner"]),
                         ("doing", "implement", "w9"))

    def test_archive_moves_file_byte_identical(self):
        for shape, body in BODY_SHAPES.items():
            for eol in ("\n", "\r\n"):
                with self.subTest(shape=shape, eol=repr(eol)):
                    path = self.write_raw(
                        body, eol, "status: done\nclosed: 2020-01-02\n")
                    raw = path.read_bytes()
                    self.wi_ok(["archive", "--older-than", "0d"])
                    moved = self.root / "archive" / "2020" / path.name
                    self.assertEqual(moved.read_bytes(), raw)
                    moved.unlink()

    def test_claim_then_handoff_keeps_trailing_notes(self):
        """The observed e832 sequence, end to end."""
        path = self.write_raw(BODY_SHAPES["trailing-unheaded"], "\n",
                              "status: todo\n")
        self.wi_ok(["claim", self.IID])
        self.wi_ok(["handoff", self.IID, "--doing", "dispatched",
                    "--next", "review -> land"])
        text = path.read_text()
        self.assertIn("\n- doing: dispatched\n- next: review -> land\n"
                      "- blocked: —\n- learned: —\n\n"
                      "- 2026-09-18 (from 81a5): carry this forward\n\n"
                      "- (F0 review lows) keep me too\n\n## Notes\n", text)

    def test_handoff_inserts_missing_bullets_in_place(self):
        path = self.write_raw("\nD.\n\n## Handoff\n- next: n\ntail\n\n## X\nx\n",
                              "\n", "status: doing\n")
        self.wi_ok(["handoff", self.IID, "--doing", "d"])
        self.assertTrue(path.read_text().endswith(
            "---\n\nD.\n\n## Handoff\n- doing: d\n- next: n\n- blocked: —\n"
            "- learned: —\ntail\n\n## X\nx\n"))

    def test_no_final_newline_is_kept_as_prefix(self):
        path = self.write_raw("\nD.\n\n## Handoff\n- doing: —\n- next: —\n"
                              "- blocked: —\n- learned: —\n\nlast words", "\n",
                              "status: todo\n")
        before = self.split_body(path.read_text(), "\n")
        self.wi_ok(["claim", self.IID])
        after = self.split_body(path.read_text(), "\n")
        self.assertTrue(after.startswith(before), after)
        self.assertIn("## Notes\n- ", after[len(before):])

    def test_whitespace_only_body_without_newline_gets_heading_on_own_line(self):
        for eol in ("\n", "\r\n"):
            for body in ("   ", "\t", eol + "  "):
                with self.subTest(eol=repr(eol), body=repr(body)):
                    path = self.write_raw("", eol, "status: todo\n")
                    path.write_bytes(path.read_bytes() + body.encode())
                    self.wi_ok(["claim", self.IID])
                    after = self.split_body(path.read_bytes().decode(), eol)
                    self.assertEqual(
                        after, body + eol + "## Notes" + eol
                        + f"- {wi.today()} claimed by tester@local" + eol)
        # and at the model level, for every section-appending path
        item = wi.Item.parse("---\nid: x\n---\n  ")
        item.set_handoff({"doing": "d"})
        self.assertEqual(item.body, "  \n## Handoff\n- doing: d\n- next: —\n"
                                    "- blocked: —\n- learned: —\n")
        self.assertEqual(item.handoff()["doing"], "d")

    def test_fenced_headings_are_not_sections(self):
        for eol in ("\n", "\r\n"):
            with self.subTest(eol=repr(eol)):
                path = self.write_raw(BODY_SHAPES["fenced-headings"], eol,
                                      "status: doing\n")
                self.wi_ok(["handoff", self.IID, "--doing", "real",
                            "--learned", "L1"])
                after = self.split_body(path.read_bytes().decode(), eol)
                expected = BODY_SHAPES["fenced-headings"].replace(
                    "- next: fake\n```\n\n",
                    f"- next: fake\n```\n- {wi.today()} learned: L1\n\n").replace(
                    "## Handoff\n- doing: d\n- next: —\n- blocked: —\n"
                    "- learned: —\n",
                    "## Handoff\n- doing: real\n- next: —\n- blocked: —\n"
                    "- learned: L1\n")
                self.assertEqual(after, expected.replace("\n", eol))
                rec = json.loads(self.wi_ok(["show", self.IID, "--json"]))
                self.assertEqual(rec["handoff"]["doing"], "real")
                self.assertEqual(rec["summary"], "Desc.")
        item = wi.Item.parse("---\nid: x\n---\n" + BODY_SHAPES["fenced-headings"])
        self.assertEqual([n for n, _ in item.sections], ["Notes", "Handoff"])
        self.assertIn("## Handoff", item.section("Notes"))
        # a backtick run with a backtick after it is inline code, not a fence;
        # a shorter or different-character run does not close a fence
        item = wi.Item.parse("---\nid: x\n---\n``` a ` b\n## A\n"
                             "````\n```\n~~~\n## B\n````\n## C\n")
        self.assertEqual([n for n, _ in item.sections], ["A", "C"])

    def test_unclosed_fence_does_not_hide_handoff(self):
        for eol in ("\n", "\r\n"):
            with self.subTest(eol=repr(eol)):
                path = self.write_raw(BODY_SHAPES["unclosed-fence"], eol,
                                      "status: doing\nowner: tester@local\n"
                                      "claimed: 2026-09-01T00:00Z\n")
                for n in range(3):
                    self.wi_ok(["handoff", self.IID, "--doing", f"NEW{n}",
                                "--learned", f"L{n}"])
                after = self.split_body(path.read_bytes().decode(), eol)
                self.assertEqual(after.count("## Handoff"), 1, after)
                self.assertIn(eol.join(["## Handoff", "- doing: NEW2",
                                        "- next: OLDNEXT", "- blocked: —",
                                        "- learned: L2", ""]), after)
                rec = json.loads(self.wi_ok(["show", self.IID, "--json"]))
                self.assertEqual((rec["handoff"]["doing"], rec["handoff"]["next"]),
                                 ("NEW2", "OLDNEXT"))
                self.wi_ok(["lint"])
                path.unlink()
        # model level: each unclosed opener is plain text, a closed pair
        # after it still hides its heading
        flags = wi._heading_flags(["```sh", "## A", "~~~", "## B", "~~~", "## C"])
        self.assertEqual(flags, [False, True, False, False, False, True])

    # an unclosed ```sh in Notes pairs with the opener of a normal block in a
    # later section: the real Handoff (and the later heading) become code
    CROSS_SECTION = (
        "\nDesc.\n\n## Notes\n- 2026-09-01 n1\n```sh\nmake\n\n## Handoff\n"
        "- doing: OLD\n- next: OLDNEXT\n- blocked: —\n- learned: —\n\n"
        "## Implementer result\n```\nlog\n```\n")

    def test_fence_paired_across_sections_refuses_not_duplicates(self):
        for eol in ("\n", "\r\n"):
            with self.subTest(eol=repr(eol), shape="handoff hidden"):
                path = self.write_raw(self.CROSS_SECTION, eol, "status: doing\n")
                raw = path.read_bytes()
                for argv in (["handoff", self.IID, "--doing", "NEW",
                              "--learned", "L"],
                             ["handoff", self.IID, "--next", "N"]):
                    r = run(argv, self.root)
                    self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
                    self.assertIn("'## Handoff' is inside a fenced code block",
                                  r.stderr)
                    self.assertEqual(path.read_bytes(), raw)
                # Notes is still a real section: a note is appended in place
                self.wi_ok(["done", self.IID, "--note", "ok"])
                after = path.read_bytes().decode()
                self.assertTrue(after.endswith(self.split_body(
                    raw.decode(), eol) + f"- {wi.today()} done: ok{eol}"))
                self.assertEqual(after.count("## Handoff"), 1)
                path.unlink()
            with self.subTest(eol=repr(eol), shape="notes hidden"):
                body = self.CROSS_SECTION.replace(
                    "## Notes\n- 2026-09-01 n1\n```sh\nmake\n\n## Handoff",
                    "```sh\nmake\n\n## Notes\n- 2026-09-01 n1\n\n## Handoff")
                path = self.write_raw(body, eol, "status: todo\n")
                raw = path.read_bytes()
                r = run(["claim", self.IID], self.root)
                self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
                self.assertIn("'## Notes' is inside a fenced code block", r.stderr)
                self.assertIn("add a real '## Notes' heading outside the fence",
                              r.stderr)
                self.assertIn("close an unclosed ``` or ~~~ above it", r.stderr)
                self.assertEqual(path.read_bytes(), raw)
                path.unlink()

    def test_closed_fenced_example_does_not_block_appending(self):
        """A closed example holding `## Notes` / `## Handoff` (and no later
        heading in the same fence) is text: the real section is appended."""
        example = ("\nDesc.\n\n```markdown\n## Handoff\n- doing: example\n"
                   "```\n\n~~~\n## Notes\n- 2020-01-01 example\n~~~\n")
        for eol in ("\n", "\r\n"):
            with self.subTest(eol=repr(eol)):
                path = self.write_raw(example, eol, "status: todo\n")
                before = self.split_body(path.read_bytes().decode(), eol)
                self.wi_ok(["claim", self.IID])
                self.wi_ok(["handoff", self.IID, "--doing", "D", "--next", "N"])
                self.wi_ok(["done", self.IID, "--note", "ok"])
                after = self.split_body(path.read_bytes().decode(), eol)
                self.assertTrue(after.startswith(before), after)
                tail = after[len(before):].replace(eol, "\n")
                self.assertEqual(
                    tail, f"\n## Notes\n- {wi.today()} claimed by tester@local\n"
                          f"- {wi.today()} done: ok\n\n## Handoff\n- doing: D\n"
                          "- next: N\n- blocked: —\n- learned: —\n")
                item = wi.Item.parse(path.read_bytes().decode())
                self.assertEqual([n for n, _ in item.sections], ["Notes", "Handoff"])
                self.wi_ok(["lint"])
                path.unlink()

    def test_many_unclosed_openers_scan_linearly(self):
        lines = ["```sh", "x", "## H"] * 5000
        start = time.monotonic()
        flags = wi._heading_flags(lines)
        self.assertLess(time.monotonic() - start, 1.0)
        self.assertEqual(sum(flags), 5000)
        # the memo does not skip a shorter opener that does have a closer
        self.assertEqual(wi._heading_flags(
            ["````", "## A", "```", "## B", "```", "## C"]),
            [False, True, False, False, False, True])

    def test_handoff_value_with_line_break_is_rejected_unwritten(self):
        path = self.write_raw(BODY_SHAPES["no-notes"], "\n", "status: doing\n")
        raw = path.read_bytes()
        for key in wi.HANDOFF_KEYS:
            for bad in ("one\ntwo", "one\r\n## Injected", "trail\r"):
                with self.subTest(key=key, value=repr(bad)):
                    r = run(["handoff", self.IID, "--doing", "ok",
                             "--" + key, bad], self.root)
                    self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                    self.assertIn(f"--{key} must be one line", r.stderr)
                    self.assertEqual(path.read_bytes(), raw)

    def test_other_one_line_values_with_line_break_are_rejected_unwritten(self):
        """block reason / --on, set value, done|drop --note and add title are
        one line too: no front-matter key or heading injection, no write."""
        path = self.write_raw(BODY_SHAPES["no-notes"], "\n", "status: todo\n")
        raw = path.read_bytes()
        cases = [
            (["block", self.IID, "waiting\nstatus: done"], "reason"),
            (["block", self.IID, "--on", "other\r\n- x"], "--on"),
            (["set", self.IID, "title", "x\npriority: 0"], "value"),
            (["set", self.IID, "blocked", "a\rb"], "value"),
            (["done", self.IID, "--note", "ok\n## Handoff\n- doing: injected"],
             "--note"),
            (["done", self.IID, "--drop", "--note", "gone\r\n"], "--note"),
        ]
        for argv, what in cases:
            with self.subTest(argv=argv):
                r = run(argv, self.root)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn(f"{what} must be one line", r.stderr)
                self.assertEqual(path.read_bytes(), raw)
        before = sorted(p.name for p in (self.root / "items").iterdir())
        r = run(["add", "two\nlines"], self.root)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("title must be one line", r.stderr)
        self.assertEqual(sorted(p.name for p in (self.root / "items").iterdir()),
                         before)
        self.wi_ok(["lint"])

    def test_front_matter_writer_rejects_line_breaks(self):
        """The writer-level backstop: every command that puts a value into
        front matter exits 1 and writes nothing when it holds a line break."""
        path = self.write_raw(BODY_SHAPES["no-notes"], "\n", "status: todo\n")
        raw = path.read_bytes()
        for argv in (["claim", self.IID, "--as", "me\npriority: x"],
                     ["next", "--pipeline", "--one", "--claim", "w\r\nstatus: done"]):
            with self.subTest(argv=argv):
                r = run(argv, self.root)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("front-matter 'owner' must be one line", r.stderr)
                self.assertEqual(path.read_bytes(), raw)
        before = sorted(p.name for p in (self.root / "items").iterdir())
        for flag, key in (("--tag", "tags"), ("--dep", "deps"),
                          ("--parent", "parent"), ("--ref", "refs")):
            with self.subTest(flag=flag):
                r = run(["add", "ok title", flag, "a\nstatus: done", "--force"],
                        self.root)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn(f"front-matter '{key}' must be one line", r.stderr)
        self.assertEqual(sorted(p.name for p in (self.root / "items").iterdir()),
                         before)
        self.wi_ok(["lint"])
        # model level: dict (x_ extras) and list values are checked too
        with self.assertRaises(wi.WiError):
            wi.emit_front({"id": "x", "x_backlog": {"k": "a\nb"}}, ["x_backlog"])
        # a batch writes nothing when any one item is rejected
        todo = self.tmp / "TODO.md"
        todo.write_text("## First\nfine\n\n## Second\nsee [x](a\nb)\n")
        r = run(["import-todo", str(todo)], self.root)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in (self.root / "items").iterdir()),
                         before)

    def test_write_side_keeps_line_endings_byte_exact(self):
        """newline='' on write: mixed CRLF / LF / lone CR outside the owned
        lines come back byte for byte after a rewrite."""
        body = ("\r\nDesc\rwith lone CR.\nLF line\r\n\r\n## Handoff\r\n"
                "- doing: —\r\n- next: —\n- blocked: —\r\n- learned: —\r\n"
                "\ntail LF\ntail CRLF\r\n")
        path = self.write_raw("", "\r\n", "status: doing\n")
        path.write_bytes(path.read_bytes() + body.encode())
        self.wi_ok(["handoff", self.IID, "--doing", "D", "--next", "N"])
        after = self.split_body(path.read_bytes().decode(), "\r\n")
        self.assertEqual(after, body.replace("- doing: —\r\n", "- doing: D\r\n")
                         .replace("- next: —\n", "- next: N\n"))
        # atomic_write itself opens with newline='' and writes the text as is
        seen, real_open = [], open

        def recording_open(*a, **kw):
            seen.append(kw.get("newline"))
            return real_open(*a, **kw)
        wi.open = recording_open
        self.addCleanup(delattr, wi, "open")
        target = self.tmp / "w.md"
        wi.atomic_write(target, "a\r\nb\nc\rd")
        self.assertEqual(seen, [""])
        self.assertEqual(target.read_bytes(), b"a\r\nb\nc\rd")


def getattr_arg(argv, key):
    flag = "--" + key
    return argv[argv.index(flag) + 1] if flag in argv else None


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


class TestParked(WiTestCase):
    """ca20: `parked` is a first-class deferred status, not a blocked item
    whose reason starts with PARKED."""

    def ids(self, args):
        return [r["id"] for r in json.loads(self.wi_ok(args + ["--json"]))]

    def test_park_and_unpark_round_trip(self):
        self.write_item("defer-1111", status="doing", owner="tester@local",
                        claimed="2026-08-30T10:00Z", stage="review",
                        handoff={"doing": "x", "next": "y"})
        self.wi_ok(["park", "defer-1111", "not this quarter"])
        rec = json.loads(self.wi_ok(["show", "defer-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"], rec["owner"],
                          rec["claimed"], rec["stage"]),
                         ("parked", "not this quarter", None, None, None))
        self.assertIn("parked: not this quarter", rec["sections"]["Notes"])
        self.wi_ok(["lint"])
        # re-parking with the same reason writes nothing
        path = self.root / "items" / "defer-1111.md"
        before = path.read_bytes()
        self.wi_ok(["park", "defer-1111", "not this quarter"])
        self.assertEqual(path.read_bytes(), before)
        out = self.wi_ok(["unpark", "defer-1111"])
        self.assertIn("-> todo", out)
        rec = json.loads(self.wi_ok(["show", "defer-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"]), ("todo", None))
        self.assertIn("unparked", rec["sections"]["Notes"])
        self.wi_ok(["lint"])

    def test_unpark_returns_blocked_item_to_blocked(self):
        self.write_item("blk-1111", status="blocked", blocked="vendor")
        self.wi_ok(["park", "blk-1111", "revisit in Q3"])
        rec = json.loads(self.wi_ok(["show", "blk-1111", "--json"]))
        self.assertEqual((rec["status"], rec["blocked"]), ("parked", "vendor"))
        self.assertIn("-> blocked", self.wi_ok(["unpark", "blk-1111"]))
        rec = json.loads(self.wi_ok(["show", "blk-1111", "--json"]))
        self.assertEqual((rec["status"], rec["blocked"], rec["parked"]),
                         ("blocked", "vendor", None))

    def test_refusals(self):
        self.write_item("todo-1111")
        self.write_item("closed-2222", status="done")
        for argv, code in ((["park", "todo-1111", ""], 1),
                           (["park", "todo-1111", "a\nstatus: done"], 1),
                           (["park", "closed-2222", "x"], 1),
                           (["unpark", "todo-1111"], 1)):
            with self.subTest(argv=argv):
                path = self.root / "items" / (argv[1] + ".md")
                before = path.read_bytes()
                self.assertEqual(run(argv, self.root).returncode, code)
                self.assertEqual(path.read_bytes(), before)
        self.wi_ok(["park", "todo-1111", "later"])
        r = run(["claim", "todo-1111"], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("unpark first", r.stderr)

    def test_lint_requires_a_reason(self):
        self.write_item("bare-1111", status="parked")
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("parked without a reason", r.stdout)

    def test_excluded_from_ready_next_and_default_ls(self):
        self.write_item("ready-1111")
        self.write_item("parked-2222", status="parked", parked="someday",
                        priority=0)
        self.write_item("child-3333", deps=["parked-2222"])
        self.assertEqual(self.ids(["ls", "--ready"]), ["ready-1111"])
        self.assertNotIn("parked-2222", self.ids(["ls"]))
        self.assertEqual(self.ids(["ls", "--status", "parked"]), ["parked-2222"])
        self.assertIn("parked-2222", self.ids(["ls", "--status", "all"]))
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertEqual([r["id"] for r in data["ready"]], ["ready-1111"])
        self.assertEqual(data["counts"]["parked"], 1)
        self.assertEqual(data["counts"]["done"], 0)
        self.assertNotIn("parked-2222", json.dumps(data["blocked"]))
        out = self.wi_ok(["next"])
        self.assertNotIn("parked-2222", out)
        self.assertIn("1 parked (wi ls --status parked)", out)
        self.assertNotIn("parked-2222", self.wi_ok(["next", "--plain"]))
        pipe = self.wi_ok(["next", "--pipeline"])
        self.assertNotIn("parked-2222", pipe)
        self.assertNotIn("child-3333", pipe)   # a parked dep does not resolve

    def test_prime_counts_parked_on_one_line_not_under_blocked(self):
        self.write_item("blk-1111", status="blocked", blocked="vendor")
        for i in range(3):
            self.write_item(f"park-{i}-2222", status="parked", parked="later")
        out = self.wi_ok(["prime"])
        lines = out.split("\n")
        self.assertIn("PARKED 3 (wi ls --status parked)", lines)
        blocked = [ln for ln in lines if ln.startswith("BLOCKED")]
        self.assertEqual(len(blocked), 1)
        self.assertNotIn("park-", blocked[0])
        self.assertEqual(sum("park-" in ln for ln in lines), 0)

    def test_drop_and_archive(self):
        self.write_item("gone-1111", status="parked", parked="later")
        self.wi_ok(["done", "gone-1111", "--drop"])
        self.wi_ok(["archive", "--older-than", "0d"])
        self.assertEqual(len(list((self.root / "archive").glob("*/gone-1111.md"))), 1)
        self.wi_ok(["lint"])

    def test_migrate_parked_dry_run_then_apply(self):
        self.write_item("old-park-1111", status="blocked",
                        blocked="PARKED: waiting for Q3 budget")
        self.write_item("old-park-2222", status="blocked", blocked="PARKED")
        self.write_item("real-block-3333", status="blocked",
                        blocked="parked car in the way")
        self.write_item("todo-4444", blocked="PARKED: stale field")
        items = sorted((self.root / "items").glob("*.md"))
        before = {p: p.read_bytes() for p in items}
        out = self.wi_ok(["migrate-parked"])
        self.assertIn("would park\told-park-1111\twaiting for Q3 budget", out)
        self.assertIn("would park\told-park-2222\tPARKED", out)
        self.assertNotIn("real-block-3333", out)
        self.assertNotIn("todo-4444", out)
        self.assertIn("2 to migrate (dry run", out)
        self.assertEqual({p: p.read_bytes() for p in items}, before)
        self.wi_ok(["migrate-parked", "--apply"])
        rec = json.loads(self.wi_ok(["show", "old-park-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"], rec["blocked"]),
                         ("parked", "waiting for Q3 budget", None))
        self.assertIn("parked (migrated from blocked: PARKED: waiting for Q3 "
                      "budget)", rec["sections"]["Notes"])
        for iid in ("real-block-3333", "todo-4444"):
            p = self.root / "items" / (iid + ".md")
            self.assertEqual(p.read_bytes(), before[p])
        self.wi_ok(["lint"])
        self.assertIn("0 migrated", self.wi_ok(["migrate-parked", "--apply"]))

    def test_backlog_yaml_bridge_maps_parked_to_blocked_and_back(self):
        self.write_item("defer-1111", "Deferred thing", status="parked",
                        parked="not this quarter")
        out = self.tmp / "backlog.yaml"
        self.wi_ok(["export", "--format", "backlog-yaml", str(out),
                    "--project", "t"])
        text = out.read_text()
        self.assertIn("status: blocked", text)
        self.assertIn('blocked_reason: "PARKED: not this quarter"', text)
        TestBacklogYaml._validate(self, out, self.tmp / "backlog_done.yaml")
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        r = run(["import", "--format", "backlog-yaml", str(out)], fresh)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(run(["ls", "--status", "all", "--json"], fresh).stdout)[0]
        self.assertEqual((rec["status"], rec["parked"], rec["blocked"]),
                         ("parked", "not this quarter", None))
        out2 = self.tmp / "backlog2.yaml"
        self.assertEqual(run(["export", "--format", "backlog-yaml", str(out2),
                              "--project", "t"], fresh).returncode, 0)
        self.assertEqual(out2.read_text(), text)
        # --update: a story unblocked upstream clears the park
        self.wi_ok(["import", "--format", "backlog-yaml", "--update",
                    str(out)])
        out.write_text(text.replace("status: blocked", "status: todo")
                       .replace('    blocked_reason: "PARKED: not this quarter"\n', ""))
        self.wi_ok(["import", "--format", "backlog-yaml", "--update", str(out)])
        rec = json.loads(self.wi_ok(["show", "defer-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"]), ("todo", None))
        self.wi_ok(["lint"])

    def test_release_never_unparks(self):
        """A stale agent's cleanup `wi release` after the operator parked its
        item must not put the item back in the ready queue."""
        self.write_item("held-1111", status="doing", owner="agent@x",
                        claimed="2026-08-30T10:00Z",
                        handoff={"doing": "x", "next": "y"})
        self.wi_ok(["park", "held-1111", "operator: not now"])
        self.wi_ok(["release", "held-1111"])
        rec = json.loads(self.wi_ok(["show", "held-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"], rec["owner"]),
                         ("parked", "operator: not now", None))
        self.assertEqual(run(["ls", "--ready"], self.root).returncode, 2)
        self.wi_ok(["lint"])
        self.assertIn("-> todo", self.wi_ok(["unpark", "held-1111"]))

    def test_import_update_keeps_blocked_reason_under_a_park(self):
        self.write_item("blk-1111", "Blocked then parked", status="blocked",
                        blocked="vendor")
        self.wi_ok(["park", "blk-1111", "later"])
        out = self.tmp / "backlog.yaml"
        self.wi_ok(["export", "--format", "backlog-yaml", str(out),
                    "--project", "t"])
        self.assertIn('blocked_reason: "PARKED: later"', out.read_text())
        self.wi_ok(["import", "--format", "backlog-yaml", "--update", str(out)])
        rec = json.loads(self.wi_ok(["show", "blk-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"], rec["blocked"]),
                         ("parked", "later", "vendor"))
        self.assertIn("-> blocked", self.wi_ok(["unpark", "blk-1111"]))
        # a fresh import has only the export: the kept blocked reason is lost
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        self.assertEqual(run(["import", "--format", "backlog-yaml", str(out)],
                             fresh).returncode, 0)
        rec = json.loads(run(["ls", "--status", "all", "--json"], fresh).stdout)[0]
        self.assertEqual((rec["status"], rec["parked"], rec["blocked"]),
                         ("parked", "later", None))

    def test_provenance_group_is_not_the_reason(self):
        real = ("PARKED (operator 2026-09-19): Paseo adoption undecided; "
                "unblock to do it, or done --drop to archive")
        self.assertEqual(wi.parked_reason(real),
                         "Paseo adoption undecided; unblock to do it, or "
                         "done --drop to archive")
        self.assertEqual(wi.parked_reason("PARKED - later"), "later")
        self.assertEqual(wi.parked_reason("PARKED (x)"), "PARKED (x)")
        self.assertIsNone(wi.parked_reason("PARKEDX: no"))
        self.assertIsNone(wi.parked_reason("parked: lower case"))
        self.write_item("sb-1111", status="blocked", blocked=real)
        self.wi_ok(["migrate-parked", "--apply"])
        rec = json.loads(self.wi_ok(["show", "sb-1111", "--json"]))
        self.assertEqual(rec["parked"], wi.parked_reason(real))
        # the provenance survives in the Notes line
        self.assertIn(f"parked (migrated from blocked: {real})",
                      rec["sections"]["Notes"])
        self.wi_ok(["lint"])

    def test_lint_flags_leftover_parked_reason_on_open_items(self):
        for st, extra in (("todo", {}), ("blocked", {"blocked": "v"}),
                          ("doing", {"handoff": {"next": "n"}})):
            self.write_item(f"left-{st}-1111", status=st, parked="stale",
                            **extra)
        self.write_item("dropped-2222", status="dropped", parked="history")
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        for st in ("todo", "doing", "blocked"):
            self.assertIn(f"left-{st}-1111.md: parked reason on a {st} item",
                          r.stdout)
        self.assertNotIn("dropped-2222", r.stdout)

    def test_set_status_goes_through_park_and_unpark(self):
        self.write_item("s-1111", status="doing", owner="a@x",
                        claimed="2026-08-30T10:00Z",
                        handoff={"doing": "x", "next": "y"})
        path = self.root / "items" / "s-1111.md"
        before = path.read_bytes()
        r = run(["set", "s-1111", "status", "parked"], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("wi park s-1111", r.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(run(["set", "s-1111", "parked", "x"], self.root)
                         .returncode, 3)
        self.assertEqual(path.read_bytes(), before)
        self.wi_ok(["park", "s-1111", "later"])
        self.wi_ok(["set", "s-1111", "status", "todo"])
        rec = json.loads(self.wi_ok(["show", "s-1111", "--json"]))
        self.assertEqual((rec["status"], rec["parked"]), ("todo", None))
        self.assertIn("unparked (set status todo)", rec["sections"]["Notes"])
        self.wi_ok(["lint"])

    def test_block_supersedes_park(self):
        self.write_item("p-1111", status="parked", parked="later")
        self.wi_ok(["block", "p-1111", "vendor"])
        rec = json.loads(self.wi_ok(["show", "p-1111", "--json"]))
        self.assertEqual((rec["status"], rec["blocked"], rec["parked"]),
                         ("blocked", "vendor", None))


class TestGrooming(WiTestCase):
    """b020: `grooming` holds an item for the operator's answers, and
    `needs-input` lists everything awaiting the operator."""

    def ids(self, args):
        return [r["id"] for r in json.loads(self.wi_ok(args + ["--json"]))]

    def show(self, iid):
        return json.loads(self.wi_ok(["show", iid, "--json"]))

    def test_groom_and_ungroom_round_trip(self):
        self.write_item("g-1111", status="doing", owner="tester@local",
                        claimed="2026-08-30T10:00Z", stage="review",
                        handoff={"doing": "x", "next": "y"})
        self.wi_ok(["groom", "g-1111", "a or b? which store?"])
        rec = self.show("g-1111")
        self.assertEqual((rec["status"], rec["grooming"], rec["owner"],
                          rec["claimed"], rec["stage"]),
                         ("grooming", "a or b? which store?", None, None, None))
        self.assertIn("grooming: a or b? which store?", rec["sections"]["Notes"])
        self.wi_ok(["lint"])
        path = self.root / "items" / "g-1111.md"
        before = path.read_bytes()
        self.wi_ok(["groom", "g-1111", "a or b? which store?"])
        self.assertEqual(path.read_bytes(), before)
        self.assertIn("-> todo", self.wi_ok(["ungroom", "g-1111"]))
        rec = self.show("g-1111")
        self.assertEqual((rec["status"], rec["grooming"]), ("todo", None))
        self.assertIn("ungroomed", rec["sections"]["Notes"])
        self.wi_ok(["lint"])

    def test_ungroom_returns_blocked_item_to_blocked(self):
        self.write_item("b-1111", status="blocked", blocked="vendor")
        self.wi_ok(["groom", "b-1111", "wait or switch vendor?"])
        self.assertEqual(self.show("b-1111")["blocked"], "vendor")
        self.assertIn("-> blocked", self.wi_ok(["ungroom", "b-1111"]))
        rec = self.show("b-1111")
        self.assertEqual((rec["status"], rec["blocked"], rec["grooming"]),
                         ("blocked", "vendor", None))

    def test_refusals(self):
        self.write_item("t-1111")
        self.write_item("closed-2222", status="done")
        for argv, code in ((["groom", "t-1111", ""], 1),
                           (["groom", "t-1111", "a\nstatus: done"], 1),
                           (["groom", "closed-2222", "x"], 1),
                           (["ungroom", "t-1111"], 1)):
            with self.subTest(argv=argv):
                path = self.root / "items" / (argv[1] + ".md")
                before = path.read_bytes()
                self.assertEqual(run(argv, self.root).returncode, code)
                self.assertEqual(path.read_bytes(), before)
        self.wi_ok(["groom", "t-1111", "which?"])
        r = run(["claim", "t-1111"], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ungroom first", r.stderr)

    def test_lint_requires_questions_and_flags_leftovers(self):
        self.write_item("bare-1111", status="grooming")
        for st, extra in (("todo", {}), ("blocked", {"blocked": "v"}),
                          ("parked", {"parked": "later"}),
                          ("doing", {"handoff": {"next": "n"}})):
            self.write_item(f"left-{st}-2222", status=st, grooming="stale",
                            **extra)
        self.write_item("dropped-3333", status="dropped", grooming="history")
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("bare-1111.md: grooming without questions", r.stdout)
        for st in ("todo", "doing", "blocked", "parked"):
            self.assertIn(f"left-{st}-2222.md: grooming questions on a {st} "
                          "item", r.stdout)
        self.assertNotIn("dropped-3333", r.stdout)

    def test_not_ready_but_in_default_ls(self):
        self.write_item("ready-1111")
        self.write_item("groom-2222", status="grooming", grooming="which?",
                        priority=0)
        self.write_item("child-3333", deps=["groom-2222"])
        self.assertEqual(self.ids(["ls", "--ready"]), ["ready-1111"])
        self.assertIn("groom-2222", self.ids(["ls"]))
        self.assertEqual(self.ids(["ls", "--status", "grooming"]), ["groom-2222"])
        data = json.loads(self.wi_ok(["next", "--json"]))
        self.assertEqual([r["id"] for r in data["ready"]], ["ready-1111"])
        self.assertEqual(data["counts"]["grooming"], 1)
        out = self.wi_ok(["next"])
        self.assertNotIn("groom-2222", out)
        self.assertIn("1 grooming (wi needs-input)", out)
        pipe = self.wi_ok(["next", "--pipeline"])
        self.assertNotIn("groom-2222", pipe)
        self.assertNotIn("child-3333", pipe)   # a grooming dep does not resolve

    def test_release_never_ungrooms(self):
        self.write_item("h-1111", status="doing", owner="agent@x",
                        claimed="2026-08-30T10:00Z",
                        handoff={"doing": "x", "next": "y"})
        self.wi_ok(["groom", "h-1111", "which?"])
        self.wi_ok(["release", "h-1111"])
        self.assertEqual(self.show("h-1111")["status"], "grooming")
        self.wi_ok(["lint"])

    def test_park_block_and_groom_supersede_each_other(self):
        self.write_item("s-1111", status="parked", parked="later")
        self.wi_ok(["groom", "s-1111", "which?"])
        rec = self.show("s-1111")
        self.assertEqual((rec["status"], rec["parked"], rec["grooming"]),
                         ("grooming", None, "which?"))
        self.wi_ok(["park", "s-1111", "later"])
        rec = self.show("s-1111")
        self.assertEqual((rec["status"], rec["parked"], rec["grooming"]),
                         ("parked", "later", None))
        self.wi_ok(["groom", "s-1111", "which?"])
        self.wi_ok(["block", "s-1111", "vendor"])
        rec = self.show("s-1111")
        self.assertEqual((rec["status"], rec["blocked"], rec["grooming"]),
                         ("blocked", "vendor", None))
        self.wi_ok(["lint"])

    def test_set_status_goes_through_groom_and_ungroom(self):
        self.write_item("s-1111")
        path = self.root / "items" / "s-1111.md"
        before = path.read_bytes()
        r = run(["set", "s-1111", "status", "grooming"], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("wi groom s-1111", r.stderr)
        self.assertEqual(run(["set", "s-1111", "grooming", "x"], self.root)
                         .returncode, 3)
        self.assertEqual(path.read_bytes(), before)
        self.wi_ok(["groom", "s-1111", "which?"])
        self.wi_ok(["set", "s-1111", "status", "todo"])
        rec = self.show("s-1111")
        self.assertEqual((rec["status"], rec["grooming"]), ("todo", None))
        self.assertIn("ungroomed (set status todo)", rec["sections"]["Notes"])
        self.wi_ok(["lint"])

    def test_backlog_yaml_bridge_maps_grooming_to_blocked_and_back(self):
        self.write_item("g-1111", "Needs answers", status="grooming",
                        grooming="a or b?")
        out = self.tmp / "backlog.yaml"
        self.wi_ok(["export", "--format", "backlog-yaml", str(out),
                    "--project", "t"])
        text = out.read_text()
        self.assertIn("status: blocked", text)
        self.assertIn('blocked_reason: "GROOMING: a or b?"', text)
        TestBacklogYaml._validate(self, out, self.tmp / "backlog_done.yaml")
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        r = run(["import", "--format", "backlog-yaml", str(out)], fresh)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(run(["ls", "--status", "all", "--json"], fresh).stdout)[0]
        self.assertEqual((rec["status"], rec["grooming"], rec["blocked"]),
                         ("grooming", "a or b?", None))
        self.wi_ok(["import", "--format", "backlog-yaml", "--update", str(out)])
        self.assertEqual(self.show("g-1111")["grooming"], "a or b?")
        self.wi_ok(["lint"])

    def test_needs_input_lists_grooming_and_unanswered_decisions(self):
        self.write_item("groom-1111", status="grooming", grooming="which store?",
                        priority=1)
        self.write_item("dec-2222", sections=(
            "## Notes\n"
            "decision 3: a or b\n"
            "decision 4: keep the alias?\n"
            "- 2026-09-20 operator said something\n"
            "answer 3: a\n"
            "decision 7: already answered further down\n"
            "```\ndecision 9: an example in a fence\n```\n"
            "answer 7: yes\n"))
        self.write_item("parked-3333", status="parked", parked="later",
                        sections="## Notes\ndecision 5: revisit when?\n")
        self.write_item("answered-4444",
                        sections="## Notes\ndecision 6: x\nanswer 6: y\n")
        self.write_item("closed-5555", status="done",
                        sections="## Notes\ndecision 8: never shown\n")
        self.write_item("indented-6666",
                        sections="## Notes\n- decision 10: not the marker\n")
        out = self.wi_ok(["needs-input"])
        self.assertEqual(out.splitlines(), [
            "groom-1111  grooming: which store?",
            "dec-2222  decision 4: keep the alias?",
            "parked-3333  decision 5: revisit when?"])
        plain = self.wi_ok(["needs-input", "--plain"]).splitlines()
        self.assertIn("groom-1111\tgrooming\t-\twhich store?", plain)
        self.assertIn("dec-2222\tdecision\t4\tkeep the alias?", plain)
        data = json.loads(self.wi_ok(["needs-input", "--json"]))
        self.assertEqual([r["id"] for r in data],
                         ["groom-1111", "dec-2222", "parked-3333"])
        self.assertEqual(data[1]["decisions"], [{"n": 4, "text": "keep the alias?"}])
        self.assertEqual(data[0]["grooming"], "which store?")
        self.wi_ok(["lint"])

    def test_needs_input_empty_exits_2(self):
        self.write_item("t-1111")
        r = run(["needs-input"], self.root)
        self.assertEqual((r.returncode, r.stdout), (2, ""))

    def test_needs_input_reads_crlf_bodies(self):
        path = self.root / "items" / "crlf-1111.md"
        path.write_bytes(
            b"---\r\nid: crlf-1111\r\ntitle: c\r\nstatus: todo\r\n"
            b"created: 2026-08-01\r\nupdated: 2026-08-01\r\n---\r\n\r\n"
            b"decision 2: crlf?\r\n")
        self.assertIn("crlf-1111  decision 2: crlf?",
                      self.wi_ok(["needs-input"]))

    def test_prime_shows_grooming_count_and_hold_line(self):
        self.write_item("blk-1111", status="blocked", blocked="vendor")
        self.write_item("g-2222", status="grooming", grooming="which?")
        self.write_item("g-3333", status="grooming", grooming="when?")
        self.write_item("park-4444", status="parked", parked="later")
        self.write_item("hold-5555", "Operator hold until review", tags=["hold"])
        self.write_item("oldhold-6666", "Old hold", status="done", tags=["hold"])
        lines = self.wi_ok(["prime"]).split("\n")
        self.assertIn("GROOMING 2 (wi needs-input)", lines)
        self.assertIn("PARKED 1 (wi ls --status parked)", lines)
        # the HOLD line comes first, right under the header
        self.assertEqual(lines[1], "HOLD 1: hold-5555 (Operator hold until review)")
        self.assertFalse(any("oldhold" in ln for ln in lines))   # closed: no hold
        self.assertFalse(any("g-2222" in ln for ln in lines))    # a count, not a list

    def test_ls_dep_lists_dependents(self):
        self.write_item("base-1111")
        self.write_item("kid-2222", deps=["base-1111"])
        self.write_item("kid-3333", deps=["base-1111", "ext: vendor"],
                        status="blocked", blocked="v")
        self.write_item("other-4444")
        self.write_item("donekid-5555", deps=["base-1111"], status="done")
        self.assertEqual(sorted(self.ids(["ls", "--dep", "base-1111"])),
                         ["kid-2222", "kid-3333"])
        self.assertEqual(sorted(self.ids(["ls", "--dep", "base"])),
                         ["kid-2222", "kid-3333"])   # a prefix resolves
        self.assertEqual(sorted(self.ids(["ls", "--dep", "base-1111",
                                          "--status", "all"])),
                         ["donekid-5555", "kid-2222", "kid-3333"])
        self.assertEqual(self.ids(["ls", "--dep", "ext: vendor"]), ["kid-3333"])
        self.assertEqual(run(["ls", "--dep", "other-4444"], self.root)
                         .returncode, 2)


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


class TestUndecodableFile(WiTestCase):
    """A non-UTF-8 file in items/ or archive/: strict readers exit with the
    parse-error code naming the file, never a traceback; lint lists it and
    keeps going; DepIndex's lenient archive read still skips it (cc39)."""
    BAD = b"\xff\xfe\x00garbage\x80\n"

    def setUp(self):
        super().setUp()
        self.write_item("good-1111")
        self.write_item("doing-2222", status="doing")  # a lint finding

    def place(self, where):
        if where == "items":
            path = self.root / "items" / "bin-bbbb.md"
        else:
            path = self.root / "archive" / "2026" / "bin-bbbb.md"
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.BAD)
        return path

    def assert_clean(self, r, path):
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn(str(path), r.stderr + r.stdout)

    def test_strict_readers_name_the_file(self):
        for where in ("items", "archive"):
            with self.subTest(where=where):
                path = self.place(where)
                self.assert_clean(run(["claim", "good-1111"], self.root,
                                      env={"WI_OWNER": "t@local"}), path)
                self.assert_clean(run(["show", "good-1111"], self.root), path)
                path.unlink()

    def test_lint_lists_it_and_keeps_going(self):
        for where in ("items", "archive"):
            with self.subTest(where=where):
                path = self.place(where)
                r = run(["lint"], self.root)
                self.assert_clean(r, path)
                self.assertIn("undecodable", r.stdout)
                self.assertIn("doing-2222", r.stdout)  # the rest still linted
                path.unlink()

    def test_lenient_archive_read_unchanged(self):
        self.place("archive")
        self.write_item("kid-3333", deps=["ghost-9999"])  # forces the read
        for cmd in (["next", "--plain"], ["ls", "--ready", "--plain"]):
            r = run(cmd, self.root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("Traceback", r.stderr)
            self.assertIn("good-1111", r.stdout)
            self.assertIn("bin-bbbb.md", r.stderr)


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




class TestSet(WiTestCase):
    """`wi set` list-field replace/clear semantics and add-mirrored
    dep/parent validation (format.md 'Editing fields')."""

    def deps_of(self, iid):
        return json.loads(self.wi_ok(["show", iid, "--json"]))["deps"]

    def test_list_field_is_replaced_whole_not_appended(self):
        self.write_item("real-a-1111")
        self.write_item("real-b-2222")
        self.write_item("target-3333", deps=["real-a-1111"])
        self.wi_ok(["set", "target-3333", "deps", "real-a-1111,real-b-2222"])
        self.assertEqual(self.deps_of("target-3333"),
                         ["real-a-1111", "real-b-2222"])
        self.wi_ok(["set", "target-3333", "deps", "real-b-2222"])
        self.assertEqual(self.deps_of("target-3333"), ["real-b-2222"])

    def test_dangling_dep_rejected_exit_1_and_nothing_written(self):
        self.write_item("target-3333")
        before = (self.root / "items" / "target-3333.md").read_text()
        r = run(["set", "target-3333", "deps", "nope-0000"], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not resolve", r.stderr)
        self.assertEqual((self.root / "items" / "target-3333.md").read_text(),
                         before)

    def test_each_dep_in_multi_value_validated(self):
        self.write_item("real-a-1111")
        self.write_item("target-3333")
        r = run(["set", "target-3333", "deps", "real-a-1111,nope-0000"],
                self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("nope-0000", r.stderr)

    def test_ext_dep_allowed_and_force_bypasses(self):
        self.write_item("target-3333")
        self.wi_ok(["set", "target-3333", "deps", "ext: other-repo"])
        self.assertEqual(self.deps_of("target-3333"), ["ext: other-repo"])
        self.wi_ok(["set", "target-3333", "deps", "nope-0000", "--force"])
        self.assertEqual(self.deps_of("target-3333"), ["nope-0000"])

    def test_self_dep_rejected_even_with_force(self):
        self.write_item("target-3333")
        for extra in ([], ["--force"]):
            r = run(["set", "target-3333", "deps", "target-3333"] + extra,
                    self.root)
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("cannot depend on itself", r.stderr)
        self.assertIsNone(self.deps_of("target-3333"))

    def test_self_parent_rejected_even_with_force(self):
        self.write_item("target-3333")
        for extra in ([], ["--force"]):
            r = run(["set", "target-3333", "parent", "target-3333"] + extra,
                    self.root)
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("cannot be its own parent", r.stderr)
        rec = json.loads(self.wi_ok(["show", "target-3333", "--json"]))
        self.assertIsNone(rec["parent"])

    def test_parent_validated_like_add(self):
        self.write_item("parent-1111")
        self.write_item("child-2222")
        r = run(["set", "child-2222", "parent", "nope-0000"], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not resolve", r.stderr)
        self.wi_ok(["set", "child-2222", "parent", "parent-1111"])
        rec = json.loads(self.wi_ok(["show", "child-2222", "--json"]))
        self.assertEqual(rec["parent"], "parent-1111")
        self.wi_ok(["set", "child-2222", "parent", "nope-0000", "--force"])

    def test_empty_value_clears_list_and_scalar_fields(self):
        self.write_item("real-a-1111")
        self.write_item("target-3333", deps=["real-a-1111"],
                        parent="real-a-1111", tags=["x"])
        self.wi_ok(["set", "target-3333", "deps", ""])
        self.assertIsNone(self.deps_of("target-3333"))
        self.wi_ok(["set", "target-3333", "tags", "—"])
        rec = json.loads(self.wi_ok(["show", "target-3333", "--json"]))
        self.assertIsNone(rec["tags"])
        self.wi_ok(["set", "target-3333", "parent", ""])
        rec = json.loads(self.wi_ok(["show", "target-3333", "--json"]))
        self.assertIsNone(rec["parent"])

    def test_schema_validation_still_exits_3(self):
        self.write_item("target-3333")
        r = run(["set", "target-3333", "status", "bogus"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("invalid status", r.stderr)

    def test_immutable_and_unknown_fields_exit_1(self):
        self.write_item("target-3333")
        self.assertEqual(
            run(["set", "target-3333", "id", "x-1111"], self.root).returncode, 1)
        self.assertEqual(
            run(["set", "target-3333", "nofield", "x"], self.root).returncode, 1)


class TestInitShapes(WiTestCase):
    """`wi init` vs the host .gitignore, per agents/decisions/0002: a
    private-shaped repo tracks config + work, so init must never whole-dir
    ignore .claude-sandbox/; only the sidecar (foreign-safe) shape gets the
    ignore, and never as a duplicate line."""

    def sandbox_repo(self, name):
        repo = self.tmp / name
        (repo / ".claude-sandbox").mkdir(parents=True)
        return repo, repo / ".claude-sandbox" / "work"

    def test_private_shape_adds_no_ignore_and_says_why(self):
        # repro of the 2026-09-06 operator-attention incident: fresh private
        # repo, .claude-sandbox/ present, no sidecar git — init must leave the
        # host .gitignore alone so the new store stays trackable
        repo, store = self.sandbox_repo("private")
        r = run(["init"], store)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("private-shaped", r.stdout)
        self.assertFalse((repo / ".gitignore").exists())
        self.assertTrue((store / "items").is_dir())

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_private_shape_store_commits_with_git_add_all(self):
        repo, store = self.sandbox_repo("private-git")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        self.assertEqual(run(["init"], store).returncode, 0)
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        staged = subprocess.run(
            ["git", "-C", str(repo), "diff", "--cached", "--name-only"],
            capture_output=True, text=True).stdout
        self.assertIn(".claude-sandbox/work/README.md", staged)

    def test_sidecar_shape_gets_whole_dir_ignore(self):
        repo, store = self.sandbox_repo("sidecar")
        (repo / ".claude-sandbox" / ".git").mkdir()
        (repo / ".gitignore").write_text("*.pyc\n")
        r = run(["init"], store)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((repo / ".gitignore").read_text(),
                         "*.pyc\n/.claude-sandbox/\n")

    def test_already_ignored_adds_no_duplicate(self):
        repo, store = self.sandbox_repo("ignored")
        (repo / ".gitignore").write_text("/.claude-sandbox/\n")
        r = run(["init"], store)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((repo / ".gitignore").read_text(),
                         "/.claude-sandbox/\n")

    def test_sidecar_with_existing_ignore_adds_no_duplicate(self):
        repo, store = self.sandbox_repo("sidecar-ignored")
        (repo / ".claude-sandbox" / ".git").mkdir()
        (repo / ".gitignore").write_text(".claude-sandbox/\n")
        r = run(["init"], store)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((repo / ".gitignore").read_text(),
                         ".claude-sandbox/\n")

    def test_plain_work_store_stays_quiet(self):
        store = self.tmp / ".work2"
        r = run(["init"], store)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, f"initialised {store}\n")
        self.assertFalse((self.tmp / ".gitignore").exists())


@unittest.skipUnless(shutil.which("git"), "git not available")
class TestHostGitignoreUntouched(WiTestCase):
    """7772 (7f00 recurrence): after init, no wi command may write the host
    .gitignore. In operator-attention the operator removed the whole-dir
    /.claude-sandbox/ line and committed (e5516d2), then the line reappeared
    after a later `wi add`; the writer was the claude-sandbox launcher's
    layout setup (trackInHost: false), not wi. These tests pin that every
    wi subcommand, run the way an operator runs it (cwd auto-resolve, no
    WI_ROOT), leaves the host .gitignore byte-identical."""

    GI = "*.pyc\n.claude-sandbox/work/.lock\n"
    AUTO = {"WI_ROOT": ""}   # empty = resolve .claude-sandbox/work from cwd

    def git(self, repo, *args, check=True):
        # isolate from the caller's git: no global/system config (signing,
        # excludesFile, hooks) and no inherited GIT_DIR-style overrides
        env = {k: v for k, v in os.environ.items()
               if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        return subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c",
             "user.name=t", "-c", "commit.gpgsign=false", "-c",
             "core.excludesFile="] + list(args),
            capture_output=True, text=True, check=check, env=env)

    def wi_in(self, repo, args):
        r = run(args, "", env=self.AUTO, cwd=repo)
        self.assertEqual(r.returncode, 0, f"{args}: {r.stderr}{r.stdout}")
        return r.stdout

    def private_repo(self, name, gi=GI):
        repo = self.tmp / name
        (repo / ".claude-sandbox").mkdir(parents=True)
        self.git(repo, "init", "-q")
        (repo / ".gitignore").write_text(gi)
        return repo

    def assert_store_trackable(self, repo):
        gi = (repo / ".gitignore").read_text()
        self.assertNotIn("/.claude-sandbox/", gi.splitlines())
        items = list((repo / ".claude-sandbox/work/items").glob("*.md"))
        self.assertTrue(items)
        for p in items:
            ignored = self.git(repo, "check-ignore", "-q", str(p),
                               check=False)
            self.assertNotEqual(ignored.returncode, 0, f"{p} is ignored")

    def every_command(self, repo):
        """Run each subcommand once against the auto-resolved store,
        asserting the host .gitignore never changes."""
        gi_path = repo / ".gitignore"
        before = gi_path.read_bytes()
        iid = self.wi_in(repo, ["add", "second item", "--json"])
        iid = json.loads(iid)["id"]
        dep = json.loads(self.wi_in(repo, ["add", "dep item", "--json"]))["id"]
        todo = repo / "TODO.md"
        todo.write_text("# TODO\n\n## imported thing\n\nbody\n")
        steps = [
            ["init"], ["ls"], ["next", "--plain", "--non-interactive"],
            ["show", iid], ["prime"], ["lint"],
            ["claim", iid], ["handoff", iid, "--next", "go"],
            ["set", iid, "priority", "1"], ["block", iid, "--on", dep],
            ["unblock", iid, "--dep", dep], ["release", iid],
            ["park", iid, "later"], ["unpark", iid], ["migrate-parked"],
            ["groom", iid, "which?"], ["needs-input"], ["ungroom", iid],
            ["repair-escapes"],
            ["import-todo", str(todo)],
            ["export", str(repo / "backlog.yaml"), "--format", "backlog-yaml"],
            ["import", str(repo / "backlog.yaml"), "--format", "backlog-yaml"],
            ["done", dep], ["archive", "--older-than", "0d"],
        ]
        choices = set(next(a for a in wi.build_parser()._actions
                           if a.dest == "command").choices)
        self.assertEqual({s[0] for s in steps} | {"add"}, choices,
                         "every wi subcommand must be exercised here")
        for step in steps:
            self.wi_in(repo, step)
            self.assertEqual(gi_path.read_bytes(), before,
                             f"`wi {' '.join(step)}` changed host .gitignore")

    def test_private_init_then_add_leaves_gitignore_alone(self):
        repo = self.private_repo("init-add")
        self.wi_in(repo, ["init"])
        self.wi_in(repo, ["add", "first item"])
        self.assertEqual((repo / ".gitignore").read_text(), self.GI)
        self.assert_store_trackable(repo)
        self.every_command(repo)

    def test_operator_removed_ignore_line_is_not_reappended(self):
        # the operator-attention sequence: the whole-dir line got in, the
        # operator removed it and committed, then kept using wi
        repo = self.private_repo("removed", gi="*.pyc\n/.claude-sandbox/\n")
        self.wi_in(repo, ["init"])            # 'ignored' shape: untouched
        self.assertEqual((repo / ".gitignore").read_text(),
                         "*.pyc\n/.claude-sandbox/\n")
        (repo / ".gitignore").write_text(self.GI)
        self.wi_in(repo, ["add", "first item"])
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-qm", "track the store")
        self.wi_in(repo, ["add", "after removal"])
        self.assertEqual((repo / ".gitignore").read_text(), self.GI)
        self.assert_store_trackable(repo)
        self.every_command(repo)
        diff = self.git(repo, "diff", "--", ".gitignore").stdout
        self.assertEqual(diff, "")

    def test_sidecar_shape_unchanged(self):
        # sidecar keeps the 7f00 behaviour: init ensures the whole-dir
        # ignore; other commands still never touch the host .gitignore
        repo = self.private_repo("sidecar", gi="*.pyc\n")
        self.git(repo / ".claude-sandbox", "init", "-q")
        out = self.wi_in(repo, ["init"])
        self.assertIn("sidecar git", out)
        self.assertEqual((repo / ".gitignore").read_text(),
                         "*.pyc\n/.claude-sandbox/\n")
        self.wi_in(repo, ["add", "first item"])
        self.every_command(repo)
        self.assertEqual((repo / ".gitignore").read_text(),
                         "*.pyc\n/.claude-sandbox/\n")


@unittest.skipUnless(shutil.which("git"), "git not available")
class TestStoreCustodyWarning(WiTestCase):
    """8efe: `wi prime` (header) and `wi lint` warn when the resolved store
    is silently untracked by the git repo that contains it — new items would
    be git-ignored, or >= UNTRACKED_MIN_ITEMS items with none tracked. Silent
    outside git and without git. A sidecar store is judged against its own
    nested repo."""

    def setUp(self):
        super().setUp()
        # hermetic git for both the helper and wi's own calls: no global or
        # system config, and no discovery above the test's tmp dir
        self.env = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CEILING_DIRECTORIES": str(self.tmp)}

    def git(self, repo, *args, check=True):
        env = {k: v for k, v in os.environ.items()
               if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
        env.update(self.env)
        return subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c",
             "user.name=t", "-c", "commit.gpgsign=false", "-c",
             "core.excludesFile="] + list(args),
            capture_output=True, text=True, check=check, env=env)

    def store_in(self, repo, gi=None, git_init=True, n_items=2):
        (repo / ".claude-sandbox").mkdir(parents=True, exist_ok=True)
        if git_init:
            self.git(repo, "init", "-q")
        if gi is not None:
            (repo / ".gitignore").write_text(gi)
        self.root = repo / ".claude-sandbox" / "work"
        self.assertEqual(run(["init"], self.root, env=self.env).returncode, 0)
        for i in range(n_items):
            self.write_item(f"item-{i:02d}-aaaa")
        return self.root

    def prime(self, env=None):
        r = run(["prime"], self.root, env=dict(self.env, **(env or {})))
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.split("\n")

    def lint(self, env=None):
        return run(["lint"], self.root, env=dict(self.env, **(env or {})))

    def assert_silent(self, env=None):
        out = self.prime(env)
        self.assertTrue(out[0].startswith("wi: "))
        self.assertNotIn("WARNING", "\n".join(out))
        r = self.lint(env)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("WARNING", r.stdout)
        self.assertIn("lint clean", r.stdout)

    SANDBOX_FIX = "set trackInHost: true in the sandbox config"
    SIDECAR_FIX = "for a public repo, give .claude-sandbox/ its own sidecar git"
    NARROW_FIX = ("fix: remove it or narrow it (a negation cannot re-include "
                  "files under an ignored directory)")
    REWRITE_FIX = ("fix: remove it, or rewrite it as `/.claude-sandbox/*` "
                   "plus `!/.claude-sandbox/work/`")

    def assert_warns(self, *parts, absent=()):
        out = self.prime()
        self.assertTrue(out[0].startswith("wi: "))
        warn = out[1]
        self.assertTrue(warn.startswith("wi: WARNING store "), warn)
        self.assertIn("silently untracked", warn)
        self.assertNotIn("18a7", warn)
        for part in parts:
            self.assertIn(part, warn)
        for part in absent:
            self.assertNotIn(part, warn)
        self.assertEqual(sum("WARNING" in ln for ln in out), 1)
        r = self.lint()
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn(warn, r.stdout.splitlines())
        self.assertNotIn("lint clean", r.stdout)
        return warn

    def test_tracked_private_store_is_silent(self):
        repo = self.tmp / "private"
        self.store_in(repo, gi="*.pyc\n")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-qm", "store")
        self.assert_silent()

    def test_whole_dir_ignore_warns(self):
        self.store_in(self.tmp / "ignored", gi="*.pyc\n/.claude-sandbox/\n")
        self.assert_warns(
            "new items are git-ignored by .gitignore:2 '/.claude-sandbox/'",
            self.REWRITE_FIX, self.SANDBOX_FIX, "490d8ca",
            self.SIDECAR_FIX, absent=("git add", "negate"))

    def test_negation_under_whole_dir_ignore_is_dead(self):
        # git cannot re-include a path under an excluded parent: the
        # negation does nothing, so the warning must not suggest one
        repo = self.tmp / "deadneg"
        self.store_in(repo, gi="/.claude-sandbox/\n!/.claude-sandbox/work/\n")
        self.assert_warns(".gitignore:1 '/.claude-sandbox/'",
                          self.REWRITE_FIX, self.SANDBOX_FIX, self.SIDECAR_FIX,
                          absent=("negate",))
        # the suggested rewrite does re-include the store
        (repo / ".gitignore").write_text(
            "/.claude-sandbox/*\n!/.claude-sandbox/work/\n")
        self.git(repo, "add", "-A")
        self.assert_silent()

    def test_excludes_file_path_with_colon_n_colon_parses(self):
        # -v output is <source>:<line>:<pattern>; a source path holding
        # ':1:' mis-split a regex parse, the -z fields do not
        repo = self.tmp / "colon"
        self.store_in(repo)
        excl = self.tmp / "ex:1:dir" / "excludes"
        excl.parent.mkdir()
        excl.write_text("# comment\n*.md\n")
        self.git(repo, "config", "core.excludesFile", str(excl))
        self.assert_warns(f"git-ignored by {excl}:2 '*.md'",
                          "remove or negate that rule", self.SANDBOX_FIX,
                          absent=(self.SIDECAR_FIX, "rewrite it"))

    def test_ignore_masked_by_tracked_items_still_warns(self):
        # operator-attention: the store was tracked, then the whole-dir line
        # came back; tracked files hide it from check-ignore on the dir, but
        # the next `wi add` would be ignored
        repo = self.tmp / "masked"
        self.store_in(repo, gi="*.pyc\n")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-qm", "store")
        (repo / ".gitignore").write_text("*.pyc\n/.claude-sandbox/\n")
        self.assert_warns(".gitignore:2 '/.claude-sandbox/'",
                          self.REWRITE_FIX, self.SANDBOX_FIX, self.SIDECAR_FIX)

    def test_md_ignore_names_rule_without_sidecar_remedy(self):
        # not a whole-dir ignore: the sidecar remedy would be wrong advice
        self.store_in(self.tmp / "md", gi="*.pyc\n*.md\n")
        self.assert_warns("git-ignored by .gitignore:2 '*.md'",
                          "remove or negate that rule", self.SANDBOX_FIX,
                          absent=(self.SIDECAR_FIX, "rewrite it"))

    def test_info_exclude_is_named_as_the_source(self):
        repo = self.tmp / "exclude"
        self.store_in(repo)
        with open(repo / ".git" / "info" / "exclude", "a") as fh:
            fh.write(".claude-sandbox/\n")
        self.assert_warns(".git/info/exclude:", "'.claude-sandbox/'",
                          self.REWRITE_FIX, self.SANDBOX_FIX, self.SIDECAR_FIX)

    def test_negated_rule_is_silent(self):
        self.store_in(self.tmp / "negated",
                      gi="*.md\n!.claude-sandbox/work/items/*.md\n")
        self.assert_silent()

    def test_dot_work_store_gets_no_sandbox_remedies(self):
        repo = self.tmp / "dotwork"
        repo.mkdir()
        self.git(repo, "init", "-q")
        (repo / ".gitignore").write_text(".work/\n")
        self.root = repo / ".work"
        self.assertEqual(run(["init"], self.root, env=self.env).returncode, 0)
        self.write_item("item-00-aaaa")
        self.assert_warns("git-ignored by .gitignore:1 '.work/'",
                          self.NARROW_FIX,
                          absent=("trackInHost", "sidecar", "490d8ca",
                                  "negate"))

    def test_directory_rules_get_narrow_not_negate(self):
        # a negation cannot re-include files under an ignored directory, for
        # rules beyond the whole-dir sandbox spellings too
        for name, gi, rule in (
                ("slash", "/.claude-sandbox/work/\n",
                 ".gitignore:1 '/.claude-sandbox/work/'"),
                ("parent", "work\n", ".gitignore:1 'work'"),
                ("items", "items\n", ".gitignore:1 'items'")):
            with self.subTest(name):
                self.store_in(self.tmp / f"dir-{name}", gi=gi)
                self.assert_warns(rule, self.NARROW_FIX, self.SANDBOX_FIX,
                                  absent=("negate", "rewrite it",
                                          self.SIDECAR_FIX))

    def excludes_under(self, repo, dirname):
        """core.excludesFile '*.md' under tmp/<dirname> (bytes, so a
        non-UTF-8 name works), written straight into .git/config."""
        d = os.fsencode(str(self.tmp)) + b"/" + dirname
        os.mkdir(d)
        with open(d + b"/excludes", "wb") as fh:
            fh.write(b"*.md\n")
        with open(repo / ".git" / "config", "ab") as fh:
            fh.write(b"[core]\n\tquotePath = true\n\texcludesFile = \""
                     + d.replace(b"\t", b"\\t") + b"/excludes\"\n")
        return d + b"/excludes"

    def test_tab_and_non_ascii_source_path_with_quotepath_on(self):
        # quotePath would print "...\\303\\251..." in -v output; -z
        # gives the raw path, shown as is
        repo = self.tmp / "tabpath"
        self.store_in(repo)
        excl = self.excludes_under(repo, "t\tb \u00e9".encode())
        self.assert_warns(f"git-ignored by {excl.decode()}:1 '*.md'",
                          "remove or negate that rule")

    def test_non_utf8_source_path_fails_open_readably(self):
        # raw Latin-1 bytes in the source used to crash text decoding
        repo = self.tmp / "latin1"
        self.store_in(repo)
        self.excludes_under(repo, b"p\xe9")
        for env in ({}, {"LC_ALL": "C", "LANG": "C"}):
            with self.subTest(env=env):
                r = run(["prime"], self.root, env=dict(self.env, **env))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertNotIn("Traceback", r.stderr)
                warn = r.stdout.split("\n")[1]
                self.assertIn("WARNING", warn)
                self.assertIn("p\\xe9/excludes:1 '*.md'", warn)
                r = run(["lint"], self.root, env=dict(self.env, **env))
                self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
                self.assertNotIn("Traceback", r.stderr)

    def test_hung_git_fails_open(self):
        # a git that never answers on the stdin path is killed by the
        # timeout and the check stays silent
        self.store_in(self.tmp / "hung", gi="/.claude-sandbox/\n")
        fake = self.tmp / "fakebin"
        fake.mkdir()
        (fake / "git").write_text("#!/bin/sh\nexec sleep 30\n")
        (fake / "git").chmod(0o755)
        path = {"PATH": f"{fake}{os.pathsep}{os.environ.get('PATH', '')}"}
        start = time.monotonic()
        self.assert_silent(env=path)
        # prime + lint, one bounded call each (under 10 items)
        self.assertLess(time.monotonic() - start, 4 * wi.GIT_TIMEOUT + 5)

    def test_new_untracked_store_below_threshold_is_silent(self):
        # a freshly initialised store before its first `git add` is normal
        self.store_in(self.tmp / "fresh",
                      n_items=wi.UNTRACKED_MIN_ITEMS - 1)
        self.assert_silent()

    def test_grown_untracked_store_warns_until_added(self):
        repo = self.tmp / "grown"
        self.store_in(repo, n_items=wi.UNTRACKED_MIN_ITEMS)
        self.assert_warns(
            f"it holds {wi.UNTRACKED_MIN_ITEMS} items and git tracks none",
            "fix: `git add` the store",
            absent=("git-ignored", "trackInHost", "sidecar", "negate"))
        self.git(repo, "add", ".claude-sandbox")   # staging is enough
        self.assert_silent()

    def test_outside_git_is_silent(self):
        self.store_in(self.tmp / "nogit", gi="/.claude-sandbox/\n",
                      git_init=False, n_items=wi.UNTRACKED_MIN_ITEMS)
        self.assert_silent()

    def test_git_missing_is_silent(self):
        self.store_in(self.tmp / "nogitbin", gi="/.claude-sandbox/\n")
        empty = self.tmp / "empty-path"
        empty.mkdir()
        self.assert_silent(env={"PATH": str(empty)})

    def test_sidecar_store_ignoring_its_own_work_gets_no_host_advice(self):
        repo = self.tmp / "sidecar"
        (repo / ".claude-sandbox").mkdir(parents=True)
        self.git(repo, "init", "-q")
        self.git(repo / ".claude-sandbox", "init", "-q")
        # init appends the whole-dir ignore to the host .gitignore; the
        # nested repo, not the host, owns the store
        self.store_in(repo, git_init=False)
        self.assertIn("/.claude-sandbox/",
                      (repo / ".gitignore").read_text().splitlines())
        sidecar = repo / ".claude-sandbox"
        self.git(sidecar, "add", "-A")
        self.git(sidecar, "commit", "-qm", "store")
        self.assert_silent()
        (sidecar / ".gitignore").write_text("/work/\n")
        # judged by the nested repo's own rule, which lives in the sidecar
        # repo: no host advice (trackInHost, the launcher, a sidecar git)
        self.assert_warns("git-ignored by .gitignore:1 '/work/' in the "
                          "sidecar repo .claude-sandbox/",
                          "fix: remove it or narrow it there (a negation",
                          absent=("trackInHost", "490d8ca", self.SIDECAR_FIX,
                                  "rewrite it", "negate"))

    def test_sidecar_excludes_file_is_named_as_is(self):
        # a rule from core.excludesFile does not live in the sidecar repo
        repo = self.tmp / "sidecar-excl"
        (repo / ".claude-sandbox").mkdir(parents=True)
        self.git(repo, "init", "-q")
        self.git(repo / ".claude-sandbox", "init", "-q")
        self.store_in(repo, git_init=False)
        excl = self.tmp / "sidecar-excludes"
        excl.write_text("*.md\n")
        self.git(repo / ".claude-sandbox", "config", "core.excludesFile",
                 str(excl))
        self.assert_warns(f"git-ignored by {excl}:1 '*.md'; "
                          "fix: remove or negate that rule",
                          absent=("sidecar repo", "there", "trackInHost",
                                  self.SIDECAR_FIX))

    def test_prime_keeps_warning_under_tiny_budget(self):
        self.store_in(self.tmp / "budget", gi="/.claude-sandbox/\n",
                      n_items=30)
        r = run(["prime", "--budget", "60"], self.root, env=self.env)
        lines = r.stdout.split("\n")
        self.assertTrue(lines[0].startswith("wi: "))
        self.assertIn("WARNING", lines[1])

    def test_prime_header_kept_when_alone_over_budget(self):
        # no warning: a budget below the header's own size keeps the header
        # (trimming used to pop it when only [header, "…"] was left)
        self.store_in(self.tmp / "trim", gi="*.pyc\n", n_items=30)
        self.git(self.root.parent.parent, "add", "-A")
        r = run(["prime", "--budget", "10"], self.root, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.rstrip("\n").split("\n")
        self.assertEqual(len(lines), 1, r.stdout)
        self.assertTrue(lines[0].startswith("wi: "), r.stdout)
        self.assertNotIn("WARNING", r.stdout)


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



class TestB020Lows(WiTestCase):
    """b020 review lows, folded with 0c59, b9e8 and 9d8c: lint hints that
    work, decision text, ls --dep ambiguity, line separators, and an export
    that loads and round-trips."""

    def show(self, iid):
        return json.loads(self.wi_ok(["show", iid, "--json"]))

    def export(self, root=None, name="backlog.yaml"):
        out = self.tmp / name
        r = run(["export", "--format", "backlog-yaml", str(out),
                 "--project", "test"], root or self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out, out.with_name(out.stem + "_done" + out.suffix)

    def load_yaml(self, path):
        from ruamel.yaml import YAML
        return YAML(typ="safe").load(path.read_text())

    # (1)
    def test_lint_hint_for_a_stray_field_names_a_command_that_clears_it(self):
        self.write_item("gp-1111", status="grooming", grooming="which?",
                        parked="stale")
        self.write_item("pg-2222", status="parked", parked="later",
                        grooming="stale")
        self.write_item("tp-3333", parked="stale")
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        for iid, field in (("gp-1111", "parked"), ("pg-2222", "grooming"),
                           ("tp-3333", "parked")):
            line = [ln for ln in r.stdout.splitlines() if iid in ln][0]
            self.assertNotIn("unpark", line)
            self.assertNotIn("ungroom", line)
            cmd = f'wi set {iid} {field} ""'
            self.assertIn(cmd, line)
            self.wi_ok(["set", iid, field, ""])
        self.assertIn("lint clean", self.wi_ok(["lint"]))
        self.assertEqual((self.show("gp-1111")["status"],
                          self.show("pg-2222")["status"]), ("grooming", "parked"))

    # (2)
    def test_needs_input_keeps_the_last_text_of_a_repeated_decision(self):
        self.write_item("rev-1111", sections=(
            "## Notes\ndecision 4: first wording\ndecision 5: other\n"
            "decision 4: revised wording\n"))
        data = json.loads(self.wi_ok(["needs-input", "--json"]))
        self.assertEqual(data[0]["decisions"],
                         [{"n": 4, "text": "revised wording"},
                          {"n": 5, "text": "other"}])

    # (3)
    def test_answer_40_does_not_answer_decision_4(self):
        self.write_item("num-1111", sections=(
            "## Notes\ndecision 4: open?\ndecision 40: answered\n"
            "answer 40: yes\n"))
        self.assertEqual(self.wi_ok(["needs-input"]).splitlines(),
                         ["num-1111  decision 4: open?"])

    # (4)
    def test_ls_dep_refuses_an_ambiguous_prefix(self):
        self.write_item("abc-1111")
        self.write_item("abc-2222")
        self.write_item("child-3333", deps=["abc-1111", "ext: vendor"])
        r = run(["ls", "--dep", "abc"], self.root)
        self.assertEqual(r.returncode, 2)
        self.assertIn("ambiguous id 'abc'", r.stderr)
        self.assertEqual([x["id"] for x in json.loads(self.wi_ok(
            ["ls", "--dep", "abc-1", "--json"]))], ["child-3333"])
        self.assertEqual([x["id"] for x in json.loads(self.wi_ok(
            ["ls", "--dep", "ext: vendor", "--json"]))], ["child-3333"])

    # (6)
    def test_one_line_writer_refuses_every_line_separator(self):
        self.write_item("t-1111", status="doing", owner="tester@local",
                        claimed="2026-08-30T10:00Z",
                        handoff={"doing": "x", "next": "y"})
        path = self.root / "items" / "t-1111.md"
        before = path.read_bytes()
        for sep in ("\u2028", "\u2029", "\x85", "\x0b", "\x0c", "\x1c"):
            for argv in (["handoff", "t-1111", "--next", f"a{sep}b"],
                         ["done", "t-1111", "--note", f"a{sep}b"],
                         ["block", "t-1111", f"a{sep}b"],
                         ["park", "t-1111", f"a{sep}b"],
                         ["groom", "t-1111", f"a{sep}b"],
                         ["set", "t-1111", "title", f"a{sep}b"],
                         ["add", f"a{sep}b"]):
                with self.subTest(sep=hex(ord(sep)), argv=argv[0]):
                    r = run(argv, self.root)
                    self.assertEqual(r.returncode, 1, r.stderr)
                    self.assertIn(f"U+{ord(sep):04X}", r.stderr)
                    self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(list((self.root / "items").glob("*.md"))), 1)

    def test_export_of_a_hand_written_line_separator_stays_loadable(self):
        self.write_item("sep-1111")
        path = self.root / "items" / "sep-1111.md"
        path.write_text(path.read_text().replace(
            "Description of sep-1111.", "one\u2028two\x85three"))
        out, done_out = self.export()
        story = self.load_yaml(out)["stories"][0]
        self.assertTrue(story["notes"].startswith("one\u2028two\x85three"))
        self.assertIn('notes: "one\\u2028two\\x85three', out.read_text())
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        self.assertEqual(run(["import", "--format", "backlog-yaml", str(out)],
                             fresh).returncode, 0)
        out2, _ = self.export(fresh, "backlog2.yaml")
        self.assertEqual(out2.read_text(), out.read_text())

    # 0c59
    def test_export_quotes_values_starting_with_a_bracket_or_brace(self):
        titles = ["[wip] x", "{curly} y", "[1, 2]", "{}", "[", "- dash",
                  "? q", "& anchor", "* star", "! tag", "| pipe", "> fold",
                  "% pct", "@ at", "` tick", "# hash"]
        for t in titles:
            self.wi_ok(["add", t])
        self.write_item("acc-9999", sections="## Acceptance\n- [ ] [x] done\n")
        out, done_out = self.export()
        loaded = self.load_yaml(out)["stories"]
        self.assertEqual(sorted(s["title"] for s in loaded),
                         sorted(titles + ["acc-9999"]))
        acc = [s for s in loaded if s["title"] == "acc-9999"][0]
        self.assertEqual(acc["acceptance"], ["[x] done"])
        TestBacklogYaml._validate(self, out, done_out)
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        self.assertEqual(run(["import", "--format", "backlog-yaml", str(out)],
                             fresh).returncode, 0)
        out2, _ = self.export(fresh, "backlog2.yaml")
        self.assertEqual(out2.read_text(), out.read_text())

    def test_export_passes_a_json_encoded_extra_field_through(self):
        src = self.tmp / "in.yaml"
        src.write_text("schema_version: 2\nstories:\n  - id: S-001\n"
                       "    title: t\n    status: todo\n    priority: 50\n"
                       "    labels: [a, b]\n    meta: {k: v}\n"
                       '    note_like: "[not json"\n')
        self.wi_ok(["import", "--format", "backlog-yaml", str(src)])
        out, _ = self.export()
        story = self.load_yaml(out)["stories"][0]
        self.assertEqual((story["labels"], story["meta"], story["note_like"]),
                         (["a", "b"], {"k": "v"}, "[not json"))

    # (7) = b9e8
    def test_ext_deps_round_trip_idempotently(self):
        self.write_item("blk-1111", status="blocked", blocked="vendor",
                        deps=["ext: upstream fix", "ext:other"])
        self.write_item("park-2222", status="parked", parked="later",
                        deps=["ext: x"])
        self.write_item("groom-3333", status="grooming", grooming="which?",
                        deps=["ext: y"])
        self.write_item("todo-4444", deps=["ext: z"])
        items = sorted((self.root / "items").glob("*.md"))
        snapshots = []
        for _ in range(4):
            out, _ = self.export()
            text = out.read_text()
            self.wi_ok(["import", "--format", "backlog-yaml", "--update",
                        str(out)])
            snapshots.append((text, [p.read_bytes() for p in items]))
        self.assertEqual(snapshots[1], snapshots[2])
        self.assertEqual(snapshots[2], snapshots[3])
        self.assertEqual(text.count("requires ext:"), 4, text)
        self.assertIn(
            'blocked_reason: "vendor; requires ext: upstream fix, ext:other"',
            text)
        self.assertIn('blocked_reason: "requires ext: z"', text)
        want = {"blk-1111": ("blocked", "vendor", None, None),
                "park-2222": ("parked", None, "later", None),
                "groom-3333": ("grooming", None, None, "which?"),
                "todo-4444": ("todo", None, None, None)}
        for iid, state in want.items():
            rec = self.show(iid)
            self.assertEqual((rec["status"], rec["blocked"], rec["parked"],
                              rec["grooming"]), state, iid)
        self.wi_ok(["lint"])
        # a fresh import restores the ext: deps from the suffix
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        self.assertEqual(run(["import", "--format", "backlog-yaml", str(out)],
                             fresh).returncode, 0)
        recs = {r["alias"]: r for r in json.loads(run(
            ["ls", "--status", "all", "--json"], fresh).stdout)}
        by_title = {r["title"]: r for r in recs.values()}
        self.assertEqual(by_title["blk-1111"]["deps"],
                         ["ext: upstream fix", "ext:other"])
        self.assertEqual(by_title["park-2222"]["deps"], ["ext: x"])
        self.assertEqual(by_title["groom-3333"]["deps"], ["ext: y"])
        self.assertEqual(by_title["todo-4444"]["deps"], ["ext: z"])
        blk = json.loads(run(["show", by_title["blk-1111"]["id"], "--json"],
                             fresh).stdout)
        self.assertEqual(blk["blocked"], "vendor")
        self.assertEqual(by_title["todo-4444"]["status"], "todo")
        out2, _ = self.export(fresh, "backlog2.yaml")
        self.assertEqual(out2.read_text(), out.read_text())

    def test_reasons_that_mention_requires_ext_survive_round_trips(self):
        """Fix round 1: only the suffix export appended is stripped."""
        self.write_item("wait-1111", status="blocked",
                        blocked="waiting; requires ext: vendor sign-off")
        self.write_item("legal-2222", status="blocked",
                        blocked="requires ext: legal sign-off")
        self.write_item("park-3333", status="parked",
                        parked="later; requires ext: x")
        self.write_item("mix-4444", status="blocked",
                        blocked="a; requires ext: b; c", deps=["ext: e57"])
        self.write_item("todo-5555", deps=["ext: z"])
        want = {"wait-1111": ("blocked", "waiting; requires ext: vendor sign-off",
                              None, []),
                "legal-2222": ("blocked", "requires ext: legal sign-off",
                               None, []),
                "park-3333": ("parked", None, "later; requires ext: x", []),
                "mix-4444": ("blocked", "a; requires ext: b; c", None,
                             ["ext: e57"]),
                "todo-5555": ("todo", None, None, ["ext: z"])}
        items = sorted((self.root / "items").glob("*.md"))
        snaps = []
        for _ in range(4):
            out, _ = self.export()
            self.wi_ok(["import", "--format", "backlog-yaml", "--update",
                        str(out)])
            snaps.append((out.read_text(), [p.read_bytes() for p in items]))
            for iid, state in want.items():
                rec = self.show(iid)
                self.assertEqual((rec["status"], rec["blocked"], rec["parked"],
                                  rec["deps"] or []), state, iid)
        self.assertEqual(snaps[1], snaps[3])
        self.wi_ok(["lint"])
        # a fresh import: the last `; requires ext:` group is the suffix, and
        # a blocked story's whole reason is never taken for one
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        self.assertEqual(run(["import", "--format", "backlog-yaml", str(out)],
                             fresh).returncode, 0)
        recs = {r["title"]: r for r in json.loads(run(
            ["ls", "--status", "all", "--json"], fresh).stdout)}
        for title in ("mix-4444", "legal-2222"):
            rec = json.loads(run(["show", recs[title]["id"], "--json"],
                                 fresh).stdout)
            self.assertEqual((rec["blocked"], rec["deps"] or []),
                             want[title][1:2] + want[title][3:], title)
        self.assertEqual(run(["lint"], fresh).returncode, 0)

    def test_a_new_items_refusal_names_no_file(self):
        r = run(["add", "t", "--tag", "a\tb"], self.root)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("front-matter 'tags' holds a control character", r.stderr)
        self.assertNotIn(".md", r.stderr)
        self.assertEqual(list((self.root / "items").glob("*.md")), [])

    def test_front_matter_refuses_a_line_separator_in_any_field(self):
        for flag in ("--tag", "--ref"):
            for sep in (" ", " "):
                with self.subTest(flag=flag, sep=hex(ord(sep))):
                    r = run(["add", "t", flag, f"a{sep}b"], self.root)
                    self.assertEqual(r.returncode, 1, r.stderr)
                    self.assertIn(f"U+{ord(sep):04X}, a line separator",
                                  r.stderr)
                    # a new item's refusal names no file: none was written
                    self.assertNotIn(".md", r.stderr)
        self.assertEqual(list((self.root / "items").glob("*.md")), [])
        # a hand-written escaped one is a lint finding
        self.write_item("hand-1111")
        path = self.root / "items" / "hand-1111.md"
        path.write_text(path.read_text().replace(
            "title: hand-1111", 'title: "a\\u2028b"'))
        r = run(["lint"], self.root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("hand-1111.md: front-matter 'title' holds a control",
                      r.stdout)
        # import folds one to a space, as it folds a line break
        src = self.tmp / "in.yaml"
        src.write_text('schema_version: 2\nstories:\n  - id: S-001\n'
                       '    title: "x\\u2028y"\n    status: todo\n')
        fresh = self.tmp / ".fresh"
        self.assertEqual(run(["init"], fresh).returncode, 0)
        self.assertEqual(run(["import", "--format", "backlog-yaml", str(src)],
                             fresh).returncode, 0)
        self.assertEqual(json.loads(run(["ls", "--json"], fresh).stdout)[0]
                         ["title"], "x y")

    # 9d8c
    def test_batch_write_refusal_names_the_item(self):
        self.write_item("ok-1111")
        self.write_item("bad-2222")
        path = self.root / "items" / "bad-2222.md"
        path.write_text(path.read_text().replace(
            "title: bad-2222", 'title: "C:\\temp"'))
        before = {p.name: p.read_bytes()
                  for p in (self.root / "items").glob("*.md")}
        out = self.tmp / "backlog.yaml"
        r = run(["export", "--format", "backlog-yaml", str(out)], self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn("bad-2222", r.stderr)
        self.assertIn(str(path), r.stderr)
        self.assertIn("front-matter 'title' holds a control character", r.stderr)
        self.assertFalse(out.exists())
        self.assertEqual({p.name: p.read_bytes()
                          for p in (self.root / "items").glob("*.md")}, before)


class TestLeadingPunctuationRoundTrip(WiTestCase):
    """370b: a park reason, grooming question or blocked reason that starts
    with punctuation, and a title with surrounding or non-breaking spaces,
    survive export -> import (fresh and --update) byte-identical on the
    first cycle; migrate-parked reads hand-written text as it always has."""

    # hand-written blocked reason -> (parked reason, Notes original); pinned
    # before 370b changed the bridge, and must never move
    MIGRATE = {
        "PARKED: \u2014 Paseo undecided": "Paseo undecided",
        "PARKED (operator 2026-09-19): Paseo undecided": "Paseo undecided",
        "PARKED (operator \u2026): later": "later",
        "PARKED \u2014 later": "later",
        "PARKED - later": "later",
        "PARKED:later": "later",
        "PARKED: - x": "x",
        "PARKED: ...": "PARKED: ...",
        "PARKED: -": "PARKED: -",
        "PARKED: \u2014": "PARKED: \u2014",
        'PARKED: "-"': '"-"',
        'PARKED: "quoted reason"': '"quoted reason"',
        "PARKED": "PARKED",
    }

    def show(self, iid, root=None):
        r = run(["show", iid, "--json"], root or self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_migrate_parked_reads_hand_written_text_as_before(self):
        for text, want in self.MIGRATE.items():
            self.assertEqual(wi.parked_reason(text), want, text)
        ids = {}
        for n, text in enumerate(self.MIGRATE):
            ids[text] = self.write_item(f"mp-{n:04d}", status="blocked",
                                        blocked=text)
        out = self.wi_ok(["migrate-parked"])
        for text, want in self.MIGRATE.items():
            self.assertIn(f"would park\t{ids[text]}\t{want}\n", out, text)
        self.wi_ok(["migrate-parked", "--apply"])
        for text, want in self.MIGRATE.items():
            rec = self.show(ids[text])
            self.assertEqual((rec["status"], rec["parked"], rec["blocked"]),
                             ("parked", want, None), text)
            self.assertIn(f"parked (migrated from blocked: {text})",
                          rec["sections"]["Notes"])
        self.wi_ok(["lint"])

    def export(self, root, name):
        out = self.tmp / name
        r = run(["export", "--format", "backlog-yaml", str(out),
                 "--project", "test"], root)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out

    def states(self, root):
        """(title, status, blocked, parked, grooming) per alias."""
        recs = json.loads(run(["ls", "--status", "all", "--json"], root).stdout)
        out = {}
        for r in recs:
            full = self.show(r["id"], root)
            out[r["alias"]] = (full["title"], full["status"], full["blocked"],
                               full["parked"], full["grooming"])
        return out

    def assert_cycle_zero_stable(self):
        """export -> fresh import -> export, and export -> import --update ->
        export: both byte-identical to the first export, every state kept."""
        out = self.export(self.root, "b0.yaml")
        text = out.read_text()
        want = self.states(self.root)
        fresh = self.tmp / ".fresh"
        shutil.rmtree(fresh, ignore_errors=True)
        self.assertEqual(run(["init"], fresh).returncode, 0)
        r = run(["import", "--format", "backlog-yaml", str(out)], fresh)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.export(fresh, "b1.yaml").read_text(), text)
        self.assertEqual(self.states(fresh), want)
        self.wi_ok(["import", "--format", "backlog-yaml", "--update",
                    str(out)])
        self.assertEqual(self.export(self.root, "b2.yaml").read_text(), text)
        self.assertEqual(self.states(self.root), want)
        self.assertEqual(run(["lint"], fresh).returncode, 0)
        self.wi_ok(["lint"])
        return text

    def test_named_shapes_round_trip_on_cycle_zero(self):
        for n, reason in enumerate(("-", "\u2014", "...", "- x",
                                    "\u2014 reason", ": later", '"-"',
                                    '"quoted"', "later")):
            self.write_item(f"park-{n:04d}", status="parked", parked=reason)
        for n, q in enumerate(("- [ ] x", "- which?", "\u2014", "...")):
            self.write_item(f"groom-{n:04d}", status="grooming", grooming=q)
        self.write_item("blk-0000", status="blocked", blocked="- vendor")
        self.write_item("sp-0000", "  spaced  title  ")
        self.write_item("nb-0000", "x\u00a0y")
        text = self.assert_cycle_zero_stable()
        # the plain form is kept wherever it already round-tripped
        self.assertIn('blocked_reason: "PARKED: later"', text)
        self.assertIn('blocked_reason: "PARKED: \\"-\\""', text)
        self.assertIn('blocked_reason: "GROOMING: \\"- [ ] x\\""', text)
        self.assertIn('blocked_reason: "- vendor"', text)

    def test_fuzz_punctuation_leading_reasons_round_trip(self):
        import random
        rng = random.Random(370)
        punct = list("-\u2014\u2013.\u2026:;,*#>[](){}\"'`!?/|~_=+") + [
            "- [ ] ", "- ", "\u2014 ", ": ", "...", "PARKED", "GROOMING",
            "\u00a0", "  "]
        words = ["x", "later", "which?", "vendor", "a  b", "c\u00a0d", ""]
        for n in range(90):
            text = "".join(rng.choice(punct)
                           for _ in range(rng.randint(1, 3)))
            text = (text + rng.choice(words)).strip()
            kind = n % 3
            if kind == 0:
                if not text:
                    continue
                self.write_item(f"fz-{n:04d}", status="parked", parked=text)
            elif kind == 1:
                if not text:
                    continue
                self.write_item(f"fz-{n:04d}", status="grooming",
                                grooming=text)
            else:
                # a plain block: `\u2014` alone reads as no value, and a
                # reason starting PARKED/GROOMING is a park/grooming (both
                # the documented bridge rule, not drift)
                if (not text or text == "\u2014"
                        or text.startswith(("PARKED", "GROOMING"))):
                    continue
                self.write_item(f"fz-{n:04d}", status="blocked", blocked=text)
        self.assert_cycle_zero_stable()

    # fix round 1: hand-written blocked_reason -> (status, parked, grooming,
    # blocked). Main's reading, except the forms export itself writes.
    HAND = [
        ('PARKED: "x"', ("parked", '"x"', None, None)),
        ('PARKED: ""', ("parked", '""', None, None)),
        ('PARKED: "a" and "b"', ("parked", '"a" and "b"', None, None)),
        ('PARKED: "foo" said the vendor, then "bar"',
         ("parked", '"foo" said the vendor, then "bar"', None, None)),
        ('GROOMING: "q?"', ("grooming", None, '"q?"', None)),
        ('GROOMING: ""', ("grooming", None, '""', None)),
        ("PARKED: \u2014 later", ("parked", "later", None, None)),
        # export's own quoted form: the text inside, verbatim
        ('PARKED: "-"', ("parked", "-", None, None)),
        ('PARKED: "\u2014 later"', ("parked", "\u2014 later", None, None)),
        ('GROOMING: "- [ ] x"', ("grooming", None, "- [ ] x", None)),
    ]

    def test_hand_written_quoted_reasons_import_as_on_main(self):
        src = self.tmp / "hand.yaml"
        lines = ["schema_version: 2", "stories:"]
        for n, (reason, _) in enumerate(self.HAND):
            lines += [f"  - id: S-{n + 1:03d}", f"    title: t{n}",
                      "    status: blocked", "    priority: 50",
                      f"    blocked_reason: \"{wi._dq_escape(reason)}\""]
        lines += ["  - id: S-900", "    title: padded", "    status: todo",
                  "    priority: 50", '    ticket_mode: " interactive "',
                  '    complexity: " low "', '    claimed_by: " a@b "',
                  # the placeholder, padded, is still no value
                  "  - id: S-901", "    title: placeholder",
                  "    status: todo", "    priority: 50",
                  '    blocked_reason: " \u2014 "']
        src.write_text("\n".join(lines) + "\n")
        self.wi_ok(["import", "--format", "backlog-yaml", str(src)])
        recs = {r["alias"]: r for r in json.loads(
            self.wi_ok(["ls", "--status", "all", "--json"]))}
        for n, (reason, want) in enumerate(self.HAND):
            rec = self.show(recs[f"S-{n + 1:03d}"]["id"])
            self.assertEqual((rec["status"], rec["parked"], rec["grooming"],
                              rec["blocked"]), want, reason)
        # enum-like fields are still folded: trimmed, not kept padded
        text = (self.root / "items" / (recs["S-900"]["id"] + ".md")).read_text()
        self.assertIn("mode: interactive\n", text)
        self.assertIn("complexity: low\n", text)
        self.assertIn("owner: a@b\n", text)
        self.assertIsNone(self.show(recs["S-901"]["id"])["blocked"])
        self.wi_ok(["lint"])


if __name__ == "__main__":
    unittest.main()
