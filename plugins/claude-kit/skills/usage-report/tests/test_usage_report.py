"""Tests for the usage_report transcript parser.

Every fixture is synthetic and written under a temp projects dir: the real
transcripts under ~/.claude/projects are never read, written or depended on.
Arithmetic is asserted against a small test-owned price table so the numbers
stay deterministic when the shipped table is repriced; a separate test checks
the shipped table's shape.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "usage_report.py"
SHIPPED_PRICES = HERE.parent / "scripts" / "prices.json"

spec = importlib.util.spec_from_file_location("usage_report", SCRIPT)
usage_report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage_report)

TEST_PRICES = {
    "version": "test",
    "retrieved": "2026-09-16",
    "normalization_base": "claude-opus-5",
    "default_model": "claude-sonnet-5",
    "aliases": {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5"},
    "models": {
        "claude-opus-5": {"input": 5.0, "output": 25.0, "cache_write_5m": 6.25,
                          "cache_write_1h": 10.0, "cache_read": 0.5},
        "claude-sonnet-5": {"input": 2.0, "output": 10.0, "cache_write_5m": 2.5,
                            "cache_write_1h": 4.0, "cache_read": 0.2},
    },
}


def assistant_line(message_id, model, timestamp, block=1, agent_id=None,
                   session_id="sess", input_tokens=0, output_tokens=0,
                   cache_read=0, cache_5m=0, cache_1h=0):
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_input_tokens": cache_read,
        "cache_creation_input_tokens": cache_5m + cache_1h,
        "cache_creation": {"ephemeral_5m_input_tokens": cache_5m,
                           "ephemeral_1h_input_tokens": cache_1h},
    }
    line = {"type": "assistant", "timestamp": timestamp, "sessionId": session_id,
            "apiBlockIndex": block,
            "message": {"id": message_id, "model": model, "role": "assistant",
                        "type": "message", "usage": usage}}
    if agent_id:
        line["agentId"] = agent_id
        line["isSidechain"] = True
    return json.dumps(line)


def user_line(timestamp="2026-09-10T00:00:00.000Z"):
    return json.dumps({"type": "user", "timestamp": timestamp,
                       "message": {"role": "user", "content": "hi"}})


def boundary_line(timestamp="2026-09-10T00:00:00.000Z"):
    return json.dumps({"type": "system", "subtype": "compact_boundary",
                       "timestamp": timestamp, "content": "Conversation compacted",
                       "compactMetadata": {"trigger": "manual", "preTokens": 623531,
                                           "postTokens": 21124}})


class Fixture:
    """A temp projects dir with one project slug, built line by line."""

    def __init__(self, tmp, slug="-proj"):
        self.root = Path(tmp) / "projects"
        self.project = self.root / slug
        self.project.mkdir(parents=True)

    def session(self, session_id, lines):
        path = self.project / (session_id + ".jsonl")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def dispatch(self, session_id, agent_id, meta, lines):
        directory = self.project / session_id / "subagents"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ("agent-%s.jsonl" % agent_id)).write_text(
            "\n".join(lines) + "\n", encoding="utf-8")
        if meta is not None:
            (directory / ("agent-%s.meta.json" % agent_id)).write_text(
                json.dumps(meta), encoding="utf-8")

    def prices(self, data=None):
        path = self.root.parent / "prices.json"
        path.write_text(json.dumps(data or TEST_PRICES), encoding="utf-8")
        return path


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Fixture(self.tmp.name)
        self.warnings = []
        self.table = usage_report.PriceTable(TEST_PRICES,
                                             warn=self.warnings.append)

    def test_split_response_counts_once(self):
        """Three lines with one message.id and repeated usage are one record."""
        lines = [assistant_line("msg_1", "claude-opus-5",
                                "2026-09-10T00:00:0%d.000Z" % i, block=i,
                                output_tokens=1000, input_tokens=10)
                 for i in (1, 2, 3)]
        path = self.fixture.session("sess", lines)
        scan = usage_report.read_transcript(path, table=self.table)
        self.assertEqual(len(scan.records), 1)
        self.assertEqual(scan.duplicates, 2)
        self.assertEqual(usage_report.totals_for(scan.records)["output"], 1000)

    def test_lines_without_usage_and_boundaries(self):
        path = self.fixture.session("sess", [
            user_line(),
            assistant_line("msg_1", "claude-opus-5", "2026-09-10T00:00:01.000Z",
                           output_tokens=5),
            boundary_line(),
            json.dumps({"type": "user", "isCompactSummary": True,
                        "message": {"role": "user", "usage": None}}),
            "not json at all",
            assistant_line("msg_2", "claude-opus-5", "2026-09-10T00:00:02.000Z",
                           output_tokens=7),
        ])
        scan = usage_report.read_transcript(path, table=self.table)
        self.assertEqual(len(scan.records), 2)
        self.assertEqual(scan.boundaries, 1)
        self.assertEqual(scan.malformed, 1)
        self.assertEqual(usage_report.totals_for(scan.records)["output"], 12)

    def test_cache_split_and_totals(self):
        path = self.fixture.session("sess", [
            assistant_line("msg_1", "claude-opus-5", "2026-09-10T00:00:01.000Z",
                           input_tokens=2, output_tokens=3, cache_read=100,
                           cache_5m=40, cache_1h=60)])
        record = usage_report.read_transcript(path, table=self.table).records[0]
        self.assertEqual(record.tokens["cache_creation"], 100)
        self.assertEqual((record.cache_write_5m, record.cache_write_1h), (40, 60))
        # 2*5 + 3*25 + 100*0.5 + 40*6.25 + 60*10 per 1M
        expected = (2 * 5 + 3 * 25 + 100 * 0.5 + 40 * 6.25 + 60 * 10) / 1e6
        self.assertAlmostEqual(record.cost_usd, expected)
        # Opus is the normalization base, so an Opus record is 1:1.
        self.assertAlmostEqual(record.opus_equivalent_tokens, 205.0)

    def test_opus_equivalent_weights_a_cheaper_model_down(self):
        path = self.fixture.session("sess", [
            assistant_line("msg_1", "claude-sonnet-5", "2026-09-10T00:00:01.000Z",
                           input_tokens=1000, output_tokens=1000)])
        record = usage_report.read_transcript(path, table=self.table).records[0]
        # input 2/5, output 10/25
        self.assertAlmostEqual(record.opus_equivalent_tokens, 1000 * 0.4 + 1000 * 0.4)
        self.assertAlmostEqual(record.cost_usd, (1000 * 2 + 1000 * 10) / 1e6)

    def test_unknown_model_warns_once_and_falls_back(self):
        path = self.fixture.session("sess", [
            assistant_line("msg_1", "claude-arcticfox-9", "2026-09-10T00:00:01.000Z",
                           input_tokens=1000),
            assistant_line("msg_2", "claude-arcticfox-9", "2026-09-10T00:00:02.000Z",
                           input_tokens=1000)])
        scan = usage_report.read_transcript(path, table=self.table)
        self.assertEqual(len(self.warnings), 1)
        self.assertIn("claude-arcticfox-9", self.warnings[0])
        self.assertEqual(self.table.unknown_models, ["claude-arcticfox-9"])
        for record in scan.records:
            self.assertFalse(record.model_known)
            self.assertEqual(record.price_key, "claude-sonnet-5")
            self.assertAlmostEqual(record.cost_usd, 1000 * 2 / 1e6)

    def test_missing_model_is_unknown_not_silently_the_default(self):
        """A usage line with no model must warn and get its own bucket."""
        path = self.fixture.session("sess", [
            json.dumps({"type": "assistant", "timestamp": "2026-09-10T00:00:01.000Z",
                        "sessionId": "sess",
                        "message": {"id": "msg_1", "role": "assistant",
                                    "usage": {"input_tokens": 1000,
                                              "output_tokens": 0}}}),
            json.dumps({"type": "assistant", "timestamp": "2026-09-10T00:00:02.000Z",
                        "sessionId": "sess",
                        "message": {"id": "msg_2", "role": "assistant",
                                    "model": None,
                                    "usage": {"input_tokens": 1000,
                                              "output_tokens": 0}}}),
            assistant_line("msg_3", "claude-opus-5", "2026-09-10T00:00:03.000Z",
                           input_tokens=1000)])
        session = usage_report.read_session(path, table=self.table)
        self.assertEqual(len(self.warnings), 1)
        self.assertIn(usage_report.NO_MODEL, self.warnings[0])
        self.assertEqual(self.table.unknown_models, [usage_report.NO_MODEL])
        data = usage_report.summarize([session], self.table)
        bucket = usage_report.UNKNOWN_PREFIX + usage_report.NO_MODEL
        self.assertEqual(sorted(data["by_model"]), ["claude-opus-5", bucket])
        self.assertEqual(data["by_model"][bucket]["input"], 2000)
        self.assertEqual(data["by_model"]["claude-opus-5"]["input"], 1000)
        self.assertTrue(any(usage_report.NO_MODEL in w for w in data["warnings"]))
        # still priced, at the default, so the dollar total is not silently zero
        self.assertGreater(data["by_model"][bucket]["cost_usd"], 0)

    def test_unknown_model_gets_its_own_bucket(self):
        path = self.fixture.session("sess", [
            assistant_line("msg_1", "claude-arcticfox-9", "2026-09-10T00:00:01.000Z",
                           input_tokens=1000)])
        session = usage_report.read_session(path, table=self.table)
        data = usage_report.summarize([session], self.table)
        self.assertEqual(sorted(data["by_model"]),
                         [usage_report.UNKNOWN_PREFIX + "claude-arcticfox-9"])

    def test_dedupe_is_file_scoped(self):
        """The same message.id in two sessions is two responses, not one."""
        first = self.fixture.session("sess_a", [
            assistant_line("msg_shared", "claude-opus-5",
                           "2026-09-10T00:00:01.000Z", session_id="sess_a",
                           output_tokens=100)])
        second = self.fixture.session("sess_b", [
            assistant_line("msg_shared", "claude-opus-5",
                           "2026-09-10T00:00:02.000Z", session_id="sess_b",
                           output_tokens=100)])
        for path in (first, second):
            scan = usage_report.read_transcript(path, table=self.table)
            self.assertEqual(len(scan.records), 1)
            self.assertEqual(scan.duplicates, 0)
        sessions = usage_report.read_project(self.fixture.project, table=self.table)
        data = usage_report.summarize(sessions, self.table)
        self.assertEqual(len(data["sessions"]), 2)
        self.assertEqual(data["totals"]["output"], 200)
        self.assertEqual(data["duplicate_lines_dropped"], 0)

    def test_dated_model_id_resolves_to_its_family(self):
        self.table.models["claude-haiku-4-5"] = {
            "input": 1.0, "output": 5.0, "cache_write_5m": 1.25,
            "cache_write_1h": 2.0, "cache_read": 0.1}
        key, _, known = self.table.prices_for("claude-haiku-4-5-20251001")
        self.assertTrue(known)
        self.assertEqual(key, "claude-haiku-4-5")
        self.assertEqual(self.warnings, [])

    def test_default_model_is_configurable(self):
        table = usage_report.PriceTable(TEST_PRICES, default_model="claude-opus-5",
                                        warn=self.warnings.append)
        key, _, known = table.prices_for("claude-nope-1")
        self.assertFalse(known)
        self.assertEqual(key, "claude-opus-5")


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Fixture(self.tmp.name)
        self.table = usage_report.PriceTable(TEST_PRICES, warn=lambda m: None)
        self.fixture.session("sess", [
            assistant_line("main_1", "claude-opus-5", "2026-09-10T00:00:01.000Z",
                           output_tokens=100)])
        # depth 1, tier requested explicitly
        self.fixture.dispatch("sess", "aaa", {
            "agentType": "fullstack-developer", "description": "Do the thing",
            "spawnDepth": 1, "model": "sonnet"}, [
            assistant_line("a_1", "claude-sonnet-5", "2026-09-10T00:01:00.000Z",
                           agent_id="aaa", output_tokens=200),
            assistant_line("a_1", "claude-sonnet-5", "2026-09-10T00:01:01.000Z",
                           agent_id="aaa", block=2, output_tokens=200)])
        # depth 2, spawned by aaa, tier inherited (no model key)
        self.fixture.dispatch("sess", "bbb", {
            "agentType": "claude-code-guide", "description": "Nested",
            "spawnDepth": 2, "parentAgentId": "aaa"}, [
            assistant_line("b_1", "claude-opus-5", "2026-09-10T00:02:00.000Z",
                           agent_id="bbb", output_tokens=50)])
        self.session = usage_report.read_session(
            self.fixture.project / "sess.jsonl", table=self.table)

    def test_subagent_join_and_attribution(self):
        self.assertEqual(len(self.session.dispatches), 2)
        by_id = {d.agent_id: d for d in self.session.dispatches}
        self.assertEqual(by_id["aaa"].agent_type, "fullstack-developer")
        self.assertEqual(by_id["aaa"].requested_tier, "sonnet")
        self.assertEqual(by_id["aaa"].tier_source, "meta")
        self.assertEqual(by_id["aaa"].models_used(), ["claude-sonnet-5"])
        self.assertIsNone(by_id["bbb"].requested_tier)
        self.assertEqual(by_id["bbb"].tier_source, "inherited")
        self.assertEqual(by_id["bbb"].models_used(), ["claude-opus-5"])
        self.assertEqual(by_id["bbb"].parent_agent_id, "aaa")
        self.assertEqual(by_id["bbb"].spawn_depth, 2)
        # every record carries the parent session
        for record in self.session.all_records():
            self.assertEqual(record.session_id, "sess")
        # the dispatch dedupe is per file too
        self.assertEqual(len(by_id["aaa"].records), 1)

    def test_rollup_is_the_default(self):
        data = usage_report.summarize([self.session], self.table)
        self.assertEqual(len(data["dispatches"]), 1)
        row = data["dispatches"][0]
        self.assertEqual(row["agent_id"], "aaa")
        self.assertEqual(row["rolled_up_dispatches"], 1)
        self.assertEqual(row["totals"]["output"], 250)
        self.assertEqual(row["models"], ["claude-opus-5", "claude-sonnet-5"])
        self.assertEqual(sorted(data["by_requested_tier"]), ["sonnet"])
        # the session total still counts main + both dispatches once
        self.assertEqual(data["totals"]["output"], 350)

    def test_flat_keeps_nested_dispatches_separate(self):
        data = usage_report.summarize([self.session], self.table, flat=True)
        rows = {r["agent_id"]: r for r in data["dispatches"]}
        self.assertEqual(sorted(rows), ["aaa", "bbb"])
        self.assertEqual(rows["aaa"]["totals"]["output"], 200)
        self.assertEqual(rows["aaa"]["rolled_up_dispatches"], 0)
        self.assertEqual(rows["bbb"]["totals"]["output"], 50)
        self.assertEqual(sorted(data["by_requested_tier"]), ["inherit", "sonnet"])
        self.assertEqual(data["totals"]["output"], 350)

    def test_dispatch_without_a_meta_file(self):
        """A transcript with no .meta.json is still a dispatch, attributes empty."""
        self.fixture.dispatch("sess", "ddd", None, [
            assistant_line("d_1", "claude-opus-5", "2026-09-10T00:04:00.000Z",
                           agent_id="ddd", output_tokens=11)])
        session = usage_report.read_session(self.fixture.project / "sess.jsonl",
                                            table=self.table)
        dispatch = {d.agent_id: d for d in session.dispatches}["ddd"]
        self.assertEqual(dispatch.meta, {})
        self.assertIsNone(dispatch.agent_type)
        self.assertIsNone(dispatch.requested_tier)
        self.assertEqual(dispatch.tier_source, "inherited")
        self.assertEqual(dispatch.spawn_depth, 1)
        self.assertIsNone(dispatch.parent_agent_id)
        data = usage_report.summarize([session], self.table)
        row = {r["agent_id"]: r for r in data["dispatches"]}["ddd"]
        self.assertEqual(row["totals"]["output"], 11)
        self.assertIn("inherit", data["by_requested_tier"])

    def test_orphan_parent_is_promoted_to_a_row(self):
        self.fixture.dispatch("sess", "ccc", {"spawnDepth": 2,
                                              "parentAgentId": "gone"}, [
            assistant_line("c_1", "claude-opus-5", "2026-09-10T00:03:00.000Z",
                           agent_id="ccc", output_tokens=9)])
        session = usage_report.read_session(self.fixture.project / "sess.jsonl",
                                            table=self.table)
        data = usage_report.summarize([session], self.table)
        self.assertEqual(sorted(r["agent_id"] for r in data["dispatches"]),
                         ["aaa", "ccc"])


class SinceAndScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Fixture(self.tmp.name)
        self.table = usage_report.PriceTable(TEST_PRICES, warn=lambda m: None)

    def test_since_filters_records(self):
        path = self.fixture.session("sess", [
            assistant_line("old", "claude-opus-5", "2026-09-01T00:00:00.000Z",
                           output_tokens=1000),
            assistant_line("new", "claude-opus-5", "2026-09-15T00:00:00.000Z",
                           output_tokens=7)])
        since = usage_report.parse_since("2026-09-10")
        scan = usage_report.read_transcript(path, table=self.table, since=since)
        self.assertEqual([r.message_id for r in scan.records], ["new"])
        self.assertEqual(usage_report.totals_for(scan.records)["output"], 7)

    def test_parse_since_relative_and_iso(self):
        now = datetime(2026, 9, 16, tzinfo=timezone.utc)
        self.assertEqual(usage_report.parse_since("7d", now=now),
                         now - timedelta(days=7))
        self.assertEqual(usage_report.parse_since("2026-09-01T00:00:00Z"),
                         datetime(2026, 9, 1, tzinfo=timezone.utc))
        self.assertIsNone(usage_report.parse_since(None))
        with self.assertRaises(ValueError):
            usage_report.parse_since("last tuesday")

    def test_scope_defaults_to_the_cwd_slug_and_falls_back_to_a_prefix(self):
        root = self.fixture.root
        cwd = Path(self.tmp.name) / "repo"
        slug = usage_report.slug_for_path(cwd)
        (root / slug).mkdir()
        self.assertEqual([p.name for p in usage_report.resolve_scope(root, cwd=cwd)],
                         [slug])
        nested = cwd / ".claude" / "worktrees" / "wt"
        self.assertEqual([p.name for p in usage_report.resolve_scope(root, cwd=nested)],
                         [slug])
        other = Path(self.tmp.name) / "elsewhere"
        self.assertEqual(usage_report.resolve_scope(root, cwd=other), [])
        self.assertEqual(len(usage_report.resolve_scope(root, cwd=other,
                                                        all_projects=True)), 2)

    def test_scope_prefix_match_respects_component_boundaries(self):
        """/foo/barbaz must not resolve to the project at /foo/bar."""
        root = self.fixture.root
        project = Path(self.tmp.name) / "foo" / "bar"
        (root / usage_report.slug_for_path(project)).mkdir()
        sibling = Path(self.tmp.name) / "foo" / "barbaz"
        self.assertEqual(usage_report.resolve_scope(root, cwd=sibling), [])
        inside = project / "sub"
        self.assertEqual([p.name for p in usage_report.resolve_scope(root, cwd=inside)],
                         [usage_report.slug_for_path(project)])

    def test_empty_and_absent_scope(self):
        """No matching project, and no projects root at all, both report nothing."""
        root = self.fixture.root
        table = self.table
        self.assertEqual(usage_report.resolve_scope(root, cwd=Path(self.tmp.name)), [])
        missing = Path(self.tmp.name) / "no-such-projects-dir"
        self.assertEqual(usage_report.resolve_scope(missing, cwd=Path(self.tmp.name)), [])
        data = usage_report.summarize([], table, scope=[])
        self.assertEqual(data["scope"], [])
        self.assertEqual(data["totals"]["total_tokens"], 0)
        self.assertEqual(data["dispatches"], [])
        self.assertEqual(data["sessions"], [])
        # an empty project directory reads as zero sessions, not an error
        self.assertEqual(usage_report.read_project(self.fixture.project,
                                                   table=table), [])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Fixture(self.tmp.name)
        self.prices = self.fixture.prices()
        self.fixture.session("sess", [
            assistant_line("main_1", "claude-opus-5", "2026-09-10T00:00:01.000Z",
                           output_tokens=100),
            assistant_line("main_1", "claude-opus-5", "2026-09-10T00:00:02.000Z",
                           block=2, output_tokens=100),
            boundary_line()])
        self.fixture.dispatch("sess", "aaa", {"agentType": "researcher",
                                              "spawnDepth": 1, "model": "sonnet"}, [
            assistant_line("a_1", "claude-sonnet-5", "2026-09-10T00:01:00.000Z",
                           agent_id="aaa", output_tokens=200)])

    def run_cli(self, *args):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--projects-dir", str(self.fixture.root),
             "--prices", str(self.prices), "--all"] + list(args),
            capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1",
                                                 "PATH": "/usr/bin:/bin"})
        return proc

    def test_summary_json(self):
        proc = self.run_cli("summary", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["totals"]["output"], 300)
        self.assertEqual(data["compact_boundaries"], 1)
        self.assertEqual(data["duplicate_lines_dropped"], 1)
        self.assertEqual(len(data["dispatches"]), 1)
        self.assertEqual(data["dispatches"][0]["requested_tier"], "sonnet")
        self.assertEqual(sorted(data["by_model"]),
                         ["claude-opus-5", "claude-sonnet-5"])
        self.assertFalse(data["flat"])

    def test_scan_and_plain_summary(self):
        scan = self.run_cli("scan", "--json")
        self.assertEqual(scan.returncode, 0, scan.stderr)
        data = json.loads(scan.stdout)
        self.assertEqual(data["sessions"][0]["dispatch_files"], 1)
        self.assertEqual(data["sessions"][0]["main_records"], 1)
        plain = self.run_cli("summary")
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("opus-equivalent tokens", plain.stdout)

    def test_default_scope_with_no_matching_project_is_not_an_error(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--projects-dir", str(self.fixture.root),
             "--prices", str(self.prices), "scan"],
            capture_output=True, text=True, cwd=self.tmp.name,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("no project directory in scope", proc.stdout)
        summary = subprocess.run(
            [sys.executable, str(SCRIPT), "--projects-dir", str(self.fixture.root),
             "--prices", str(self.prices), "summary", "--json"],
            capture_output=True, text=True, cwd=self.tmp.name,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
        self.assertEqual(summary.returncode, 0, summary.stderr)
        data = json.loads(summary.stdout)
        self.assertEqual(data["scope"], [])
        self.assertEqual(data["totals"]["total_tokens"], 0)

    def test_no_subcommand_prints_help(self):
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("usage", proc.stdout.lower())


class ShippedPriceTableTests(unittest.TestCase):
    def test_table_is_versioned_and_covers_the_observed_models(self):
        table = usage_report.PriceTable.load(SHIPPED_PRICES, warn=lambda m: None)
        self.assertTrue(table.version)
        self.assertTrue(table.retrieved)
        self.assertEqual(table.base, "claude-opus-5")
        self.assertTrue(table.canonical(table.default_model))
        # every model id observed in the local transcripts, plus the tier
        # aliases the meta files use
        for model in ("claude-opus-5", "claude-sonnet-5", "claude-fable-5-1",
                      "claude-fable-5", "claude-opus-4-7", "claude-opus-4-8",
                      "claude-haiku-4-5-20251001", "opus", "sonnet", "fable",
                      "haiku"):
            key, prices, known = table.prices_for(model)
            self.assertTrue(known, model)
            for price_class in usage_report.PRICE_CLASSES:
                self.assertGreater(prices[price_class], 0, (model, price_class))


if __name__ == "__main__":
    unittest.main()
