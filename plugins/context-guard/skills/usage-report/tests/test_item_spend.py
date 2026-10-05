"""Tests for item_spend, the cost-budget reader (`usage_report.py item`).

Synthetic fixtures are written under a temp projects dir. The reproduction
fixtures under fixtures/f65b/ are four items of the claude-plugins store
(09f1, 6394, 0426, caef) with their agents' transcripts cut down to
timestamps, message ids and usage blocks (one line per API response, user-text
turns kept as bare markers, no content). Their expected figures are the plan
series f65b's evidence table (evidence/item-costs.md, regenerated for serial
05 by evidence/item_cost.py), priced at the shipped prices.json, which carries
the same rates as the series' prices_cited.json.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
FIXTURES = HERE / "fixtures" / "f65b"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location("item_spend", SCRIPTS / "item_spend.py")
item_spend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(item_spend)
ur = item_spend.ur

TEST_PRICES = {
    "version": "test", "retrieved": "2026-10-05",
    "normalization_base": "claude-opus-5", "default_model": "claude-sonnet-5",
    "aliases": {},
    "models": {
        # $1 per 1,000 output tokens keeps the arithmetic readable.
        "claude-opus-5": {"input": 5.0, "output": 1000.0, "cache_write_5m": 6.25,
                          "cache_write_1h": 10.0, "cache_read": 0.5},
        "claude-sonnet-5": {"input": 2.0, "output": 500.0, "cache_write_5m": 2.5,
                            "cache_write_1h": 4.0, "cache_read": 0.2},
    },
}

ID_A = "a" + "1" * 16
ID_B = "a" + "2" * 16
ID_C = "a" + "3" * 16
ID_CHILD = "a" + "4" * 16
ID_NAMED = "afix-the-thing-" + "5" * 16
ID_GONE = "a" + "6" * 16


def turn(ts):
    return json.dumps({"type": "user", "timestamp": ts,
                       "message": {"role": "user", "content": "brief"}})


def tool_result(ts):
    return json.dumps({"type": "user", "timestamp": ts,
                       "message": {"role": "user",
                                   "content": [{"type": "tool_result", "content": "ok"}]}})


_counter = [0]


def usage(ts, output, model="claude-opus-5", message_id=None, **extra):
    """An assistant line whose spend is `output` / 1000 dollars at opus test rates."""
    if message_id is None:
        _counter[0] += 1
        message_id = "msg_%d" % _counter[0]
    tokens = {"input_tokens": 0, "output_tokens": output,
              "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    tokens.update(extra)
    return json.dumps({"type": "assistant", "timestamp": ts, "requestId": "req_" + message_id,
                       "message": {"id": message_id, "model": model, "usage": tokens}})


class World:
    def __init__(self, tmp):
        self.root = Path(tmp) / "projects"
        self.sub = self.root / "-proj" / "sess" / "subagents"
        self.sub.mkdir(parents=True)
        self.tmp = Path(tmp)

    def agent(self, aid, lines, meta=None):
        (self.sub / ("agent-%s.jsonl" % aid)).write_text("\n".join(lines) + "\n")
        (self.sub / ("agent-%s.meta.json" % aid)).write_text(json.dumps(meta or {}))

    def item(self, body, item_type="feature"):
        path = self.tmp / "item.md"
        path.write_text("---\nid: x\ntype: %s\n---\n\n%s\n" % (item_type, body))
        return path

    def read(self, body, item_type="feature", table=None):
        item = item_spend.ItemRecord.load(self.item(body, item_type))
        return item_spend.read_item(item, item_spend.TranscriptIndex(self.root),
                                    table or ur.PriceTable(TEST_PRICES))


class ReproductionTests(unittest.TestCase):
    """The prototype's per-item results, through the shipped reader."""

    EXPECTED = {
        # tag: (phase, total, cumulative after each review, unrecorded rounds, nested segs)
        "09f1": ("build", 4.19, [2.55, 3.78, 4.19], 0, 0),
        "6394": ("build", 6.37, [2.63, 4.52, 5.52, 6.37], 3, 0),
        "0426": ("build", 13.47, [5.58, 10.44, 13.47], 4, 1),
        "caef": ("plan", 29.93, [6.82, 12.39, 13.68, 15.71, 22.10], 1, 2),
    }

    def test_evidence_items_reproduce(self):
        table = ur.PriceTable.load()
        index = item_spend.TranscriptIndex(FIXTURES / "projects")
        for tag, (phase, total, series, unrecorded, nested) in self.EXPECTED.items():
            with self.subTest(item=tag):
                item = item_spend.ItemRecord.load(FIXTURES / "items" / ("%s.md" % tag))
                data = item_spend.read_item(item, index, table)
                self.assertEqual(data["reading"], "read")
                self.assertEqual(data["usd"], total)
                self.assertEqual(list(data["phases"]), [phase])
                self.assertEqual(data["phases"][phase]["cumulative_after_review"], series)
                self.assertEqual(sum(f.get("count", 0) for f in data["flags"]
                                     if f["flag"] == "unrecorded"), unrecorded)
                self.assertEqual(sum(1 for s in data["segments"] if s["role"] == "nested"),
                                 nested)
                self.assertEqual(data["ids"], data["ids_joined"])


class IdShapeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = World(self.tmp.name)

    def test_every_agent_line_shape_counts(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000)])
        w.agent(ID_B, [turn("2026-10-01T11:00:00Z"), usage("2026-10-01T11:01:00Z", 2000)])
        w.agent(ID_C, [turn("2026-10-01T12:00:00Z"), usage("2026-10-01T12:01:00Z", 3000)],
                meta={"description": "plan reviewer for x"})
        w.agent(ID_NAMED, [turn("2026-10-01T13:00:00Z"),
                           usage("2026-10-01T13:01:00Z", 4000)])
        data = w.read("\n".join([
            "agent: implementer %s round 1" % ID_A,       # role first
            "agent: %s (plan reviewer r2)" % ID_B,        # id first, role after
            "agent: %s round 5 (resumed)" % ID_C,         # no role: meta description
            "agent: research-lane w1 %s, w2 %s round 1" % (ID_NAMED, ID_A),  # several ids
        ]))
        self.assertEqual(data["ids"], 4)
        self.assertEqual(data["usd"], 10.0)
        roles = {s["id"]: s["role"] for s in data["segments"]}
        self.assertEqual(roles[ID_A], "implementer")
        self.assertEqual(roles[ID_B], "reviewer")
        self.assertEqual(roles[ID_C], "reviewer")
        self.assertEqual(roles[ID_NAMED], "research")

    def test_role_comes_from_an_earlier_line_for_the_same_id(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000),
                       turn("2026-10-01T11:00:00Z"), usage("2026-10-01T11:01:00Z", 1000)])
        data = w.read("agent: reviewer %s round 1\nagent: %s round 2 (resumed)" % (ID_A, ID_A))
        self.assertEqual({s["role"] for s in data["segments"]}, {"reviewer"})

    def test_leading_role_word_wins_over_a_fable_note(self):
        self.assertEqual(item_spend.role_of("reviewer %s round 1 (fable)" % ID_A), "reviewer")
        self.assertEqual(item_spend.role_of("%s (fable second opinion)" % ID_A), "cross-check")


class SegmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = World(self.tmp.name)

    def test_resumed_agent_splits_at_text_turns_and_surplus_is_counted(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000),
                       tool_result("2026-10-01T10:02:00Z"),
                       usage("2026-10-01T10:03:00Z", 1000),
                       turn("2026-10-01T11:00:00Z"), usage("2026-10-01T11:01:00Z", 2000),
                       turn("2026-10-01T12:00:00Z"), usage("2026-10-01T12:01:00Z", 4000)])
        data = w.read("agent: implementer %s round 1\nagent: implementer %s round 2"
                      % (ID_A, ID_A))
        self.assertEqual([s["usd"] for s in data["segments"]], [2.0, 2.0, 4.0])
        self.assertEqual(data["usd"], 8.0)
        flags = [f for f in data["flags"] if f["flag"] == "unrecorded"]
        self.assertEqual((flags[0]["id"], flags[0]["count"]), (ID_A, 1))

    def test_fewer_segments_than_lines_is_flagged_lost(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000)])
        data = w.read("\n".join("agent: implementer %s round %d" % (ID_A, n)
                                for n in (1, 2, 3)))
        flags = [f for f in data["flags"] if f["flag"] == "lost"]
        self.assertEqual(flags[0]["count"], 2)
        self.assertEqual(data["reading"], "read")

    def test_streamed_response_counts_once_at_its_largest_output(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"),
                       usage("2026-10-01T10:01:00Z", 10, message_id="m1"),
                       usage("2026-10-01T10:01:01Z", 3000, message_id="m1"),
                       usage("2026-10-01T10:01:02Z", 20, message_id="m1")])
        self.assertEqual(w.read("agent: implementer %s round 1" % ID_A)["usd"], 3.0)

    def test_zero_usage_synthetic_records_are_skipped(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000),
                       usage("2026-10-01T10:02:00Z", 0, model="<synthetic>")])
        data = w.read("agent: implementer %s round 1" % ID_A)
        self.assertEqual((data["reading"], data["usd"], data["synthetic_skipped"]),
                         ("read", 1.0, 1))

    def test_unknown_claude_model_with_tokens_is_no_reading(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000),
                       usage("2026-10-01T10:02:00Z", 1000, model="claude-opus-9")])
        data = w.read("agent: implementer %s round 1" % ID_A)
        self.assertEqual(data["reading"], "unread")
        self.assertIsNone(data["usd"])
        self.assertIn("claude-opus-9", data["phases"]["build"]["unread"][0])

    def test_non_claude_model_is_left_out_and_flagged(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:01:00Z", 1000),
                       usage("2026-10-01T10:02:00Z", 5000, model="qwen3.8-27b")])
        data = w.read("agent: implementer %s round 1" % ID_A)
        self.assertEqual((data["reading"], data["usd"]), ("read", 1.0))
        flag = [f for f in data["flags"] if f["flag"] == "non-Claude"][0]
        self.assertEqual(flag["models"], {"qwen3.8-27b": 5000})

    def test_dated_model_id_prices_at_its_family(self):
        w = self.world
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"),
                       usage("2026-10-01T10:01:00Z", 1000, model="claude-sonnet-5-20260901")])
        self.assertEqual(w.read("agent: implementer %s round 1" % ID_A)["usd"], 0.5)


class PhaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = World(self.tmp.name)
        w = self.world
        # planner (plan), reviewer resumed across both phases, implementer (build)
        w.agent(ID_A, [turn("2026-10-01T10:00:00Z"), usage("2026-10-01T10:05:00Z", 4000)],
                meta={"description": "planner"})
        w.agent(ID_B, [turn("2026-10-01T10:30:00Z"), usage("2026-10-01T10:31:00Z", 1000),
                       turn("2026-10-01T13:00:00Z"), usage("2026-10-01T13:01:00Z", 500)])
        w.agent(ID_C, [turn("2026-10-01T12:00:00Z"), usage("2026-10-01T12:30:00Z", 2000)])
        # a child the planner spawned, which started after the build opened
        w.agent(ID_CHILD, [turn("2026-10-01T12:10:00Z"), usage("2026-10-01T12:11:00Z", 300)],
                meta={"parentAgentId": ID_A})
        self.lines = ["agent: planner %s round 1" % ID_A,
                      "agent: reviewer %s round 1" % ID_B,
                      "agent: implementer %s round 1" % ID_C,
                      "agent: reviewer %s round 1" % ID_B]

    def test_phases_split_by_time_against_budget_lines(self):
        body = "\n".join([
            "budget: 2026-10-01T09:59Z plan $28 — default plan",
            self.lines[0], self.lines[1],
            "cost: 2026-10-01T10:40Z plan $5.00 of $28 after review 1 — must-fix 0 — prices v2",
            "budget: 2026-10-01T11:59Z build $22 — default feature",
            "budget: 2026-10-01T12:40Z build $30 — answer 9 (was $22)",
            self.lines[2], self.lines[3]])
        data = self.world.read(body)
        self.assertEqual(data["phase_source"], "budget")
        plan, build = data["phases"]["plan"], data["phases"]["build"]
        self.assertEqual(plan["usd"], 5.0)
        self.assertEqual(plan["budget"], 28.0)
        # the reviewer's second segment and the nested child land in the build
        self.assertEqual(build["usd"], 2.8)
        self.assertEqual(build["budget"], 30.0)          # the last line is in force
        self.assertEqual(data["usd"], 7.8)               # phases sum to the item
        self.assertEqual(build["cumulative_after_review"], [2.8])

    def test_segments_before_every_budget_line_are_unbudgeted(self):
        body = "\n".join(self.lines[:2] + [
            "budget: 2026-10-01T11:59Z build $22 — default feature"] + self.lines[2:])
        data = self.world.read(body)
        self.assertEqual(data["phases"]["unbudgeted"]["usd"], 5.0)
        self.assertEqual(data["phases"]["build"]["usd"], 2.8)
        self.assertTrue(any(f["flag"] == "unbudgeted" for f in data["flags"]))

    def test_no_budget_line_infers_phases_at_the_first_implementer(self):
        data = self.world.read("\n".join(self.lines))
        self.assertEqual(data["phase_source"], "inferred")
        self.assertEqual(data["phases"]["plan"]["usd"], 5.0)
        self.assertEqual(data["phases"]["build"]["usd"], 2.8)

    def test_budget_line_without_a_time_is_ignored_and_flagged(self):
        data = self.world.read("budget: build $22 — default feature\n" + "\n".join(self.lines))
        self.assertEqual(data["phase_source"], "inferred")
        self.assertTrue(any(f["flag"] == "ignored line" for f in data["flags"]))


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = World(self.tmp.name)
        self.world.agent(ID_A, [turn("2026-10-01T10:00:00Z"),
                                usage("2026-10-01T10:01:00Z", 1000),
                                turn("2026-10-01T12:00:00Z"),
                                usage("2026-10-01T12:01:00Z", 2000)])

    def test_lost_transcript_reads_through_the_last_cost_line(self):
        body = "\n".join([
            "budget: 2026-10-01T09:00Z build $22 — default feature",
            "agent: reviewer %s round 1" % ID_GONE,
            "agent: implementer %s round 1" % ID_A,
            "cost: 2026-10-01T11:00Z build $9.50 of $22 after review 1 — must-fix 1 — prices v2",
            "agent: implementer %s round 2" % ID_A])
        data = self.world.read(body)
        build = data["phases"]["build"]
        self.assertEqual(build["reading"], "read")
        self.assertEqual(build["usd"], 11.5)            # $9.50 + the $2 round after it
        self.assertEqual(build["lost_transcripts"], [ID_GONE])
        self.assertTrue(any(f["flag"] == "lost transcript" for f in data["flags"]))

    def test_lost_transcript_after_the_last_cost_line_is_no_reading(self):
        body = "\n".join([
            "budget: 2026-10-01T09:00Z build $22 — default feature",
            "agent: implementer %s round 1" % ID_A,
            "cost: 2026-10-01T11:00Z build $9.50 of $22 after review 1 — must-fix 1 — prices v2",
            "agent: reviewer %s round 2" % ID_GONE])
        data = self.world.read(body)
        self.assertEqual(data["phases"]["build"]["reading"], "unread")
        self.assertIsNone(data["usd"])

    def test_lost_transcript_on_an_old_record_is_no_reading(self):
        data = self.world.read("agent: implementer %s round 1\nagent: reviewer %s round 1"
                               % (ID_A, ID_GONE))
        self.assertEqual(data["reading"], "unread")
        self.assertEqual(data["missing"], [ID_GONE])


class WeekTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = World(self.tmp.name)
        self.table = ur.PriceTable(TEST_PRICES)

    def args(self, **kw):
        base = dict(per_percent=None, no_week=False, week_used=None, week_resets_at=None)
        base.update(kw)
        return SimpleNamespace(**base)

    def test_rate_is_local_spend_since_the_window_opened_over_used_percent(self):
        w = self.world
        (w.root / "-proj" / "sess.jsonl").write_text("\n".join([
            usage("2026-09-20T10:00:00Z", 50000),            # before the window: ignored
            usage("2026-10-01T10:00:00Z", 30000),
            usage("2026-10-01T10:00:00Z", 30000, model="qwen3.8-27b")]) + "\n")
        w.agent(ID_A, [turn("2026-10-02T10:00:00Z"), usage("2026-10-02T10:01:00Z", 10000)])
        week = item_spend.week_rate(self.args(week_used=20, week_resets_at="2026-10-05T00:00Z"),
                                    self.table, w.root)
        self.assertAlmostEqual(week["per_percent"], 2.0)   # $40 over 20%

    def test_a_coarse_reading_gives_no_rate(self):
        week = item_spend.week_rate(self.args(week_used=1, week_resets_at="2026-10-05T00:00Z"),
                                    self.table, self.world.root)
        self.assertIsNone(week["per_percent"])
        self.assertIn("too coarse", week["why"])

    def test_given_rate_and_no_week(self):
        self.assertEqual(item_spend.week_rate(self.args(per_percent=22), self.table,
                                              self.world.root)["per_percent"], 22.0)
        self.assertIsNone(item_spend.week_rate(self.args(no_week=True), self.table,
                                               self.world.root)["per_percent"])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = World(self.tmp.name)
        self.world.agent(ID_A, [turn("2026-10-01T10:00:00Z"),
                                usage("2026-10-01T10:01:00Z", 11000)])
        self.item = self.world.item("budget: 2026-10-01T09:00Z build $22 — default feature\n"
                                    "agent: implementer %s round 1" % ID_A)
        self.prices = Path(self.tmp.name) / "prices.json"
        self.prices.write_text(json.dumps(TEST_PRICES))

    def run_cli(self, *extra):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "usage_report.py"), "item", str(self.item),
             "--projects-dir", str(self.world.root), "--prices", str(self.prices)]
            + list(extra), capture_output=True, text=True, timeout=60)

    def test_item_json(self):
        out = self.run_cli("--json", "--per-percent", "22")
        self.assertEqual(out.returncode, 0, out.stderr)
        data = json.loads(out.stdout)
        self.assertEqual(data["usd"], 11.0)
        self.assertEqual(data["phases"]["build"]["budget"], 22.0)
        self.assertEqual(data["share_of_week_percent"], 0.5)

    def test_item_text(self):
        out = self.run_cli("--per-percent", "22")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("build      $11.00 of $22.00 (default feature) (≈0.50% of a week)",
                      out.stdout)
        self.assertIn("week: $22.00 per 1% — given (--per-percent)", out.stdout)

    def test_item_without_week_reading_shows_dollars_alone(self):
        out = self.run_cli("--no-week")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("total      $11.00\n", out.stdout)
        self.assertIn("week: no share shown", out.stdout)

    def test_missing_item_file(self):
        self.item = Path(self.tmp.name) / "nope.md"
        out = self.run_cli()
        self.assertEqual(out.returncode, 1)


if __name__ == "__main__":
    unittest.main()
