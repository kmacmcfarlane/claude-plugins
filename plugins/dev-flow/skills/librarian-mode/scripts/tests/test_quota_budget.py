"""Tests for quota_budget.py (librarian-mode's quota sense, 1222 F1).

Every test runs against a temp config dir passed as CLAUDE_CONFIG_DIR; the real
~/.claude is never read or written. Time is pinned with --now.
"""
import contextlib
import importlib.util
import io
import json
import os
import signal
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "quota_budget.py"
spec = importlib.util.spec_from_file_location("quota_budget", SCRIPT)
qb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qb)

NOW = 1_790_000_000.0
SID = "11111111-2222-3333-4444-555555555555"
H = 3600.0


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = self._tmp.name
        self.store = os.path.join(self.cfg, "claude-kit", "librarian")
        self.env = {"CLAUDE_CONFIG_DIR": self.cfg, "CLAUDE_CODE_SESSION_ID": SID}

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixtures
    def sensor(self, five=(10.0, NOW + 2 * H), week=(30.0, NOW + 100 * H), at=NOW - 60,
               sid=SID, v=1, rate_limits=True):
        d = os.path.join(self.cfg, "statusline", "sensor")
        os.makedirs(d, exist_ok=True)
        rec = {"v": v}
        if rate_limits:
            rl = {"at": at}
            if five:
                rl["five_hour"] = {"used_percentage": five[0], "resets_at": five[1]}
            if week:
                rl["seven_day"] = {"used_percentage": week[0], "resets_at": week[1]}
            rec["rate_limits"] = rl
        with open(os.path.join(d, sid + ".json"), "w") as f:
            json.dump(rec, f)

    def samples(self, rows):
        os.makedirs(self.store, exist_ok=True)
        with open(os.path.join(self.store, "samples.jsonl"), "a") as f:
            for at, five, week in rows:
                d = {"v": 1, "at": at, "session": "other"}
                if five:
                    d["five_hour"] = {"used_percentage": five[0], "resets_at": five[1]}
                if week:
                    d["seven_day"] = {"used_percentage": week[0], "resets_at": week[1]}
                f.write(json.dumps(d) + "\n")

    def intent(self, obj):
        os.makedirs(self.store, exist_ok=True)
        with open(os.path.join(self.store, "intent.json"), "w") as f:
            json.dump(obj, f)

    def claim(self, repo, obj):
        d = os.path.join(self.store, "claims")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, repo + ".json"), "w") as f:
            json.dump(obj, f)

    def read_claim(self, repo):
        with open(os.path.join(self.store, "claims", repo + ".json")) as f:
            return json.load(f)

    def run_qb(self, *argv, now=NOW, env=None):
        out = io.StringIO()
        err = io.StringIO()
        args = ["--now", str(now), "--repo", "myrepo"] + list(argv)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = qb.main(args, env=self.env if env is None else env)
        return rc, json.loads(out.getvalue()), err.getvalue()


class TestVelocity(Base):
    def test_groups_by_resets_at_and_ignores_previous_window(self):
        old, new = NOW - 1 * H, NOW + 4 * H
        self.samples([
            (NOW - 3 * H, (80.0, old), (20.0, NOW + 100 * H)),
            (NOW - 1.5 * H, (95.0, old), (22.0, NOW + 100 * H)),
            (NOW - 1 * H + 30, (2.0, new), (23.0, NOW + 100 * H)),
        ])
        self.sensor(five=(6.0, new), week=(24.0, NOW + 100 * H), at=NOW)
        rc, r, _ = self.run_qb()
        self.assertEqual(rc, 0)
        self.assertEqual(r["signal"], "ok")
        w5 = r["windows"]["five_hour"]
        # only the new window's points: 2 -> 6 over (1 h - 30 s)
        self.assertEqual(w5["velocity_points"], 2)
        self.assertAlmostEqual(w5["velocity"], 4.0 / ((H - 30) / H), places=3)
        self.assertGreater(w5["velocity"], 0)

    def test_small_resets_at_jitter_is_one_window(self):
        reset = NOW + 3 * H
        self.samples([(NOW - H, (10.0, reset + 20), (30.0, NOW + 100 * H))])
        self.sensor(five=(12.0, reset), week=(31.0, NOW + 100 * H + 40), at=NOW)
        _, r, _ = self.run_qb()
        self.assertAlmostEqual(r["windows"]["five_hour"]["velocity"], 2.0, places=3)
        self.assertAlmostEqual(r["windows"]["seven_day"]["velocity"], 1.0, places=3)

    def test_stale_low_reading_does_not_pull_velocity_down(self):
        reset = NOW + 3 * H
        self.samples([
            (NOW - 2 * H, (10.0, reset), None),
            (NOW - 1 * H, (20.0, reset), None),
            (NOW - 30 * 60, (9.0, reset), None),  # a stale payload
        ])
        self.sensor(five=(30.0, reset), at=NOW)
        _, r, _ = self.run_qb()
        # lookback 2 h: from the 10% point to the 30% point
        self.assertAlmostEqual(r["windows"]["five_hour"]["velocity"], 10.0, places=3)

    def test_lookback_uses_newest_point_at_least_that_old(self):
        reset = NOW + 3 * H
        self.samples([
            (NOW - 4.5 * H, (0.0, reset), None),
            (NOW - 3 * H, (5.0, reset), None),   # newest point >= 2 h old
            (NOW - 1 * H, (20.0, reset), None),
        ])
        self.sensor(five=(35.0, reset), at=NOW)
        _, r, _ = self.run_qb()
        self.assertAlmostEqual(r["windows"]["five_hour"]["velocity"], 10.0, places=3)

    def test_single_point_or_short_span_has_no_velocity(self):
        self.sensor(at=NOW)
        _, r, _ = self.run_qb()
        self.assertIsNone(r["windows"]["five_hour"]["velocity"])
        self.samples([(NOW - 60, (9.0, NOW + 2 * H), (30.0, NOW + 100 * H))])
        _, r, _ = self.run_qb()
        self.assertIsNone(r["windows"]["five_hour"]["velocity"])


class TestSignal(Base):
    def assertNoSignal(self, r, fragment):
        self.assertEqual(r["signal"], "none")
        self.assertIn(fragment, r["reason"])
        self.assertIsNone(r["windows"])
        self.assertEqual(r["next_check"], qb.NEXT_CHECK_NO_SIGNAL_S)

    def test_missing_record(self):
        rc, r, _ = self.run_qb()
        self.assertEqual(rc, 0)
        self.assertNoSignal(r, "no sensor record")

    def test_no_session_id(self):
        env = {"CLAUDE_CONFIG_DIR": self.cfg}
        rc, r, _ = self.run_qb(env=env)
        self.assertEqual(rc, 0)
        self.assertNoSignal(r, "no session id")
        self.assertEqual(r["claims"]["action"], "skipped-no-session")

    def test_session_argument_wins(self):
        self.sensor(sid="abc")
        _, r, _ = self.run_qb("--session", "abc")
        self.assertEqual(r["signal"], "ok")
        self.assertEqual(r["session"], "abc")

    def test_stale_record(self):
        self.sensor(at=NOW - qb.STALE_AFTER_S - 1)
        _, r, _ = self.run_qb()
        self.assertNoSignal(r, "stale")

    def test_stale_after_is_tunable(self):
        self.sensor(at=NOW - 2 * H)
        _, r, _ = self.run_qb("--stale-after", str(3 * H))
        self.assertEqual(r["signal"], "ok")

    def test_unknown_version_and_no_rate_limits(self):
        self.sensor(v=2)
        self.assertNoSignal(self.run_qb()[1], "version")
        self.sensor(rate_limits=False)
        self.assertNoSignal(self.run_qb()[1], "no rate limits")

    def test_one_window_missing(self):
        self.sensor(week=None)
        self.assertNoSignal(self.run_qb()[1], "lacks")

    def test_window_reset_since_reading(self):
        self.sensor(five=(90.0, NOW - 10), at=NOW - 60)
        self.assertNoSignal(self.run_qb()[1], "reset since")

    def test_future_stamp(self):
        self.sensor(at=NOW + qb.FUTURE_SKEW_S + 10)
        self.assertNoSignal(self.run_qb()[1], "future")

    def test_ok_result_shape_and_next_check(self):
        self.sensor(five=(10.0, NOW + 1200), week=(30.0, NOW + 100 * H), at=NOW)
        _, r, _ = self.run_qb()
        self.assertEqual(r["signal"], "ok")
        for w in ("five_hour", "seven_day"):
            for k in ("used", "velocity", "allowed", "reserve", "headroom", "hours_to_reset"):
                self.assertIn(k, r["windows"][w])
        self.assertEqual(r["next_check"], 1200 + qb.RESET_GRACE_S)
        self.sensor(five=(10.0, NOW + 3 * H), at=NOW)
        self.assertEqual(self.run_qb()[1]["next_check"], qb.NEXT_CHECK_MAX_S)
        self.sensor(five=(10.0, NOW + 1), at=NOW)
        self.assertEqual(self.run_qb()[1]["next_check"], 1 + qb.RESET_GRACE_S)


class TestIntentAndAllowed(Base):
    def setUp(self):
        super().setUp()
        # five-hour: used 40, 3 h to reset; weekly: used 50, 100 h to reset
        self.sensor(five=(40.0, NOW + 3 * H), week=(50.0, NOW + 100 * H), at=NOW)

    def check(self, mode, r5, rw):
        _, r, _ = self.run_qb()
        self.assertEqual(r["intent"]["mode"], mode)
        self.assertEqual((r["reserves"]["five_hour"], r["reserves"]["seven_day"]), (r5, rw))
        a5 = (100 - 40 - r5) / 3.0
        aw = (100 - 50 - rw) / 100.0
        self.assertAlmostEqual(r["windows"]["five_hour"]["allowed"], a5, places=3)
        self.assertAlmostEqual(r["windows"]["seven_day"]["allowed"], aw, places=3)
        self.assertEqual(r["binding"], "five_hour" if a5 < aw else "seven_day")
        self.assertAlmostEqual(r["allowed"], min(a5, aw), places=3)
        return r

    def test_default_is_present(self):
        r = self.check("present", 25, 15)
        self.assertEqual(r["intent"]["source"], "default")

    def test_modes(self):
        for stored, mode, r5, rw in (("present", "present", 25, 15), ("away", "away", 10, 15),
                                     ("done for the day", "done-for-the-day", 0, 15),
                                     ("done_for_the_day", "done-for-the-day", 0, 15),
                                     ("vacation", "vacation", 5, 10)):
            self.intent({"mode": stored, "until": NOW + H, "set_by": "x", "at": NOW - 60})
            self.check(mode, r5, rw)

    def test_no_until_holds(self):
        self.intent({"mode": "away"})
        self.check("away", 10, 15)

    def test_expired_reads_present(self):
        self.intent({"mode": "vacation", "until": NOW - 1})
        r = self.check("present", 25, 15)
        self.assertTrue(r["intent"]["expired"])

    def test_iso_until(self):
        self.intent({"mode": "away", "until": "2099-01-01T00:00:00Z"})
        self.check("away", 10, 15)

    def test_unknown_mode_reads_present(self):
        self.intent({"mode": "sleeping"})
        r = self.check("present", 25, 15)
        self.assertEqual(r["intent"]["source"], "unknown-mode")

    def test_garbled_intent_reads_present(self):
        os.makedirs(self.store, exist_ok=True)
        with open(os.path.join(self.store, "intent.json"), "w") as f:
            f.write("{not json")
        self.check("present", 25, 15)

    def test_headroom_below_zero_allows_zero(self):
        self.sensor(five=(80.0, NOW + 3 * H), week=(50.0, NOW + 100 * H), at=NOW)
        _, r, _ = self.run_qb()
        self.assertLess(r["windows"]["five_hour"]["headroom"], 0)
        self.assertEqual(r["windows"]["five_hour"]["allowed"], 0)
        self.assertEqual(r["binding"], "five_hour")


class TestSamplesAndSink(Base):
    def lines(self):
        p = os.path.join(self.store, "samples.jsonl")
        if not os.path.exists(p):
            return []
        with open(p) as f:
            return [json.loads(x) for x in f]

    def test_fallback_appends_one_sample_per_call(self):
        self.sensor(at=NOW)
        self.run_qb()
        self.run_qb(now=NOW + 10)
        rows = self.lines()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["session"], SID)
        self.assertEqual(rows[0]["five_hour"]["used_percentage"], 10.0)
        self.assertEqual(rows[0]["at"], NOW)

    def test_no_signal_appends_nothing(self):
        self.run_qb()
        self.assertEqual(self.lines(), [])

    def test_read_only_writes_nothing(self):
        self.sensor(at=NOW)
        _, r, _ = self.run_qb("--read-only")
        self.assertEqual(r["signal"], "ok")
        self.assertFalse(os.path.exists(self.store))

    def test_prune_keeps_recent_history(self):
        old = [(NOW - 20 * 86400 + i, (1.0, NOW + 2 * H), (1.0, NOW + 100 * H)) for i in range(3)]
        self.samples(old)
        self.sensor(at=NOW)
        with mock.patch.object(qb, "SAMPLES_PRUNE_AT", 10):
            self.run_qb()
        rows = self.lines()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["at"], NOW)

    def sink(self, rows, day="2026-09-21"):
        d = os.path.join(self.cfg, "plugins", "data", "claude-analytics-kmacmcfarlane", "samples")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, day + ".jsonl"), "a") as f:
            for ts, five, week in rows:
                f.write(json.dumps({"ts": ts, "session_id": "s", "model": "m", "rate_limits": {
                    "five_hour": {"used_percentage": five[0], "resets_at": five[1]},
                    "seven_day": {"used_percentage": week[0], "resets_at": week[1]}}}) + "\n")
        return d

    def test_live_sink_is_the_history_and_no_sample_is_written(self):
        reset, wreset = NOW + 3 * H, NOW + 100 * H
        self.sink([(NOW - H, (10.0, reset), (30.0, wreset)),
                   ("2026-09-21T13:43:20Z", (11.0, reset), (30.5, wreset))])
        self.sink([(NOW - 120, (13.0, reset), (31.0, wreset))], day="2026-09-22")
        self.sensor(five=(14.0, reset), week=(31.0, wreset), at=NOW)
        _, r, _ = self.run_qb()
        self.assertEqual(r["source"]["history"], "sink")
        self.assertEqual(r["source"]["reading"], "sensor")
        self.assertAlmostEqual(r["windows"]["five_hour"]["velocity"], 4.0, places=3)
        self.assertEqual(self.lines(), [])

    def test_sink_supplies_the_reading_when_the_record_is_missing(self):
        reset, wreset = NOW + 3 * H, NOW + 100 * H
        self.sink([(NOW - 60, (12.0, reset), (31.0, wreset))], day="2026-09-22")
        _, r, _ = self.run_qb()
        self.assertEqual(r["signal"], "ok")
        self.assertEqual(r["source"]["reading"], "sink")
        self.assertEqual(r["windows"]["five_hour"]["used"], 12.0)

    def test_stale_sink_falls_back_to_sampling(self):
        self.sink([(NOW - 5 * H, (10.0, NOW + 3 * H), (30.0, NOW + 100 * H))])
        self.sensor(at=NOW)
        _, r, _ = self.run_qb()
        self.assertEqual(r["source"]["history"], "samples")
        self.assertEqual(len(self.lines()), 1)

    def test_garbage_lines_are_skipped(self):
        os.makedirs(self.store, exist_ok=True)
        with open(os.path.join(self.store, "samples.jsonl"), "w") as f:
            f.write("not json\n[1,2]\n{\"at\": \"x\"}\n")
        self.sensor(at=NOW)
        rc, r, _ = self.run_qb()
        self.assertEqual((rc, r["signal"]), (0, "ok"))


class TestClaims(Base):
    def test_create_and_refresh(self):
        _, r, _ = self.run_qb()
        self.assertEqual(r["claims"]["action"], "created")
        c = self.read_claim("myrepo")
        self.assertEqual((c["repo"], c["session_id"], c["at"], c["in_flight"]),
                         ("myrepo", SID, NOW, []))
        # F2 will add fields and in-flight items; a refresh keeps them
        c["in_flight"] = [{"item": "x", "tier": "opus", "since": NOW}]
        c["demand"] = {"count": 2, "best": 1}
        self.claim("myrepo", c)
        _, r, _ = self.run_qb(now=NOW + 60)
        self.assertEqual(r["claims"]["action"], "refreshed")
        c = self.read_claim("myrepo")
        self.assertEqual(c["at"], NOW + 60)
        self.assertEqual(len(c["in_flight"]), 1)
        self.assertEqual(c["demand"], {"count": 2, "best": 1})

    def test_identity_from_own_registry_file_only(self):
        reg = os.path.join(self.cfg, "sessions")
        os.makedirs(reg)
        with open(os.path.join(reg, "42.json"), "w") as f:
            json.dump({"sessionId": SID, "name": "myrepo - librarian", "pid": 42,
                       "pidDomain": "pidns:1", "procStart": "123"}, f)
        env = dict(self.env, CLAUDE_PID="42")
        self.run_qb(env=env)
        c = self.read_claim("myrepo")
        self.assertEqual((c["session_name"], c["pid"], c["pidDomain"], c["procStart"]),
                         ("myrepo - librarian", 42, "pidns:1", "123"))
        # a registry file of another session is not ours to read from
        with open(os.path.join(reg, "42.json"), "w") as f:
            json.dump({"sessionId": "someone-else", "name": "x", "pid": 42}, f)
        os.unlink(os.path.join(self.store, "claims", "myrepo.json"))
        self.run_qb(env=env)
        self.assertIsNone(self.read_claim("myrepo")["session_name"])

    def foreign(self, age, in_flight=(), **extra):
        c = {"v": 1, "repo": "myrepo", "session_id": "other", "at": NOW - age,
             "in_flight": list(in_flight)}
        c.update(extra)
        self.claim("myrepo", c)

    def test_fresh_foreign_claim_is_a_conflict_and_left_alone(self):
        self.foreign(H)
        _, r, _ = self.run_qb()
        self.assertEqual(r["claims"]["action"], "conflict")
        self.assertFalse(r["claims"]["written"])
        self.assertTrue(r["claims"]["previous"]["fresh"])
        self.assertEqual(self.read_claim("myrepo")["session_id"], "other")

    def test_takeover_flag_resets_in_flight(self):
        self.foreign(H, in_flight=[{"item": "a"}])
        _, r, _ = self.run_qb("--takeover")
        self.assertEqual(r["claims"]["action"], "takeover")
        c = self.read_claim("myrepo")
        self.assertEqual((c["session_id"], c["in_flight"]), (SID, []))

    def test_same_process_takeover_after_clear(self):
        reg = os.path.join(self.cfg, "sessions")
        os.makedirs(reg)
        with open(os.path.join(reg, "7.json"), "w") as f:
            json.dump({"sessionId": SID, "name": "n", "pid": 7, "pidDomain": "d",
                       "procStart": "p"}, f)
        self.foreign(H, in_flight=[{"item": "a"}], pid=7, pidDomain="d", procStart="p")
        _, r, _ = self.run_qb(env=dict(self.env, CLAUDE_PID="7"))
        self.assertEqual(r["claims"]["action"], "takeover-same-process")
        self.assertEqual(self.read_claim("myrepo")["in_flight"], [])

    def test_missing_proc_start_is_not_same_process(self):
        reg = os.path.join(self.cfg, "sessions")
        os.makedirs(reg)
        with open(os.path.join(reg, "7.json"), "w") as f:
            json.dump({"sessionId": SID, "pid": 7, "pidDomain": "d"}, f)
        self.foreign(H, pid=7, pidDomain="d")
        _, r, _ = self.run_qb(env=dict(self.env, CLAUDE_PID="7"))
        self.assertEqual(r["claims"]["action"], "conflict")

    def test_idle_claim_expires_after_two_hours(self):
        self.foreign(2 * H - 1)
        self.assertEqual(self.run_qb()[1]["claims"]["action"], "conflict")
        self.foreign(2 * H + 1)
        self.assertEqual(self.run_qb()[1]["claims"]["action"], "replaced-expired")
        self.assertEqual(self.read_claim("myrepo")["session_id"], SID)

    def test_in_flight_claim_expires_after_four_hours(self):
        self.foreign(3 * H, in_flight=[{"item": "a"}])
        self.assertEqual(self.run_qb()[1]["claims"]["action"], "conflict")
        self.foreign(4 * H + 1, in_flight=[{"item": "a"}])
        self.assertEqual(self.run_qb()[1]["claims"]["action"], "replaced-expired")

    def test_fresh_count(self):
        self.claim("a", {"at": NOW - H, "in_flight": []})                  # fresh
        self.claim("b", {"at": NOW - 3 * H, "in_flight": []})              # expired idle
        self.claim("c", {"at": NOW - 3 * H, "in_flight": [{"i": 1}, {"i": 2}]})  # fresh in flight
        self.claim("d", {"at": NOW - 5 * H, "in_flight": [{"i": 1}]})      # expired in flight
        self.claim("e", {"at": "garbage"})                                  # unreadable at
        os.makedirs(os.path.join(self.store, "claims", "stale"))
        with open(os.path.join(self.store, "claims", "stale", "f.json"), "w") as f:
            json.dump({"at": NOW, "in_flight": []}, f)                      # tombstone
        _, r, _ = self.run_qb()                                              # + our own
        self.assertEqual(r["claims"]["fresh"], 3)
        self.assertEqual(r["claims"]["fresh_in_flight"], 2)

    def test_hostile_repo_name_stays_in_claims_dir(self):
        _, r, _ = self.run_qb("--repo", "../../evil")
        self.assertEqual(os.path.dirname(r["claims"]["path"]), os.path.join(self.store, "claims"))
        self.assertTrue(os.path.basename(r["claims"]["path"]).startswith("repo-"))

    def test_repo_defaults_to_main_checkout_basename(self):
        repo = os.path.join(self.cfg, "work", "proj")
        os.makedirs(repo)
        subprocess.run(["git", "init", "-q", repo], check=True)
        self.assertEqual(qb.repo_name(repo), "proj")
        self.assertEqual(qb.repo_name(os.path.join(self.cfg, "nowhere")), "nowhere")


class TestAtomicityAndPerms(Base):
    def test_private_perms(self):
        self.sensor(at=NOW)
        self.run_qb()
        for d in (self.store, os.path.join(self.store, "claims")):
            self.assertEqual(stat.S_IMODE(os.stat(d).st_mode), 0o700, d)
        for f in ("samples.jsonl", os.path.join("claims", "myrepo.json")):
            self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.store, f)).st_mode), 0o600, f)
        # claude-kit itself was created by us too: private
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(self.store)).st_mode), 0o700)

    def test_existing_parent_perms_untouched(self):
        kit = os.path.join(self.cfg, "claude-kit")
        os.makedirs(kit)
        os.chmod(kit, 0o755)
        self.run_qb()
        self.assertEqual(stat.S_IMODE(os.stat(kit).st_mode), 0o755)

    def test_failed_write_leaves_old_file_and_no_temp(self):
        path = os.path.join(self.store, "claims", "x.json")
        qb.atomic_write_json(path, {"old": True})
        with mock.patch.object(qb.json, "dump", side_effect=RuntimeError("disk full")):
            with self.assertRaises(RuntimeError):
                qb.atomic_write_json(path, {"new": True})
        with open(path) as f:
            self.assertEqual(json.load(f), {"old": True})
        self.assertEqual(os.listdir(os.path.dirname(path)), ["x.json"])

    def test_write_goes_through_replace(self):
        path = os.path.join(self.store, "t.json")
        with mock.patch.object(qb.os, "replace", wraps=os.replace) as rep:
            qb.atomic_write_json(path, {"a": 1})
        rep.assert_called_once()
        self.assertEqual(rep.call_args[0][1], path)

    def test_store_write_error_exits_1_and_still_prints(self):
        os.makedirs(os.path.dirname(self.store))
        with open(self.store, "w") as f:  # a file where the store dir should be
            f.write("x")
        self.sensor(at=NOW)
        rc, r, err = self.run_qb()
        self.assertEqual(rc, 1)
        self.assertEqual(r["signal"], "ok")
        self.assertTrue(r["errors"])
        self.assertIn("quota_budget:", err)

    def test_internal_error_never_raises(self):
        with mock.patch.object(qb, "compute", side_effect=ValueError("boom")):
            rc, r, err = self.run_qb()
        self.assertEqual(rc, 1)
        self.assertEqual(r["signal"], "none")
        self.assertIn("internal error", err)


DEEP = "[" * 200000 + "]" * 200000  # json.loads raises RecursionError on this


class TestPoisonedInput(Base):
    """R2: a deeply nested or otherwise poisoned file or line never escapes a reader."""

    def poison(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write('{"a": ' + DEEP + "}")

    def assertCleanRun(self, **kw):
        rc, r, err = self.run_qb(**kw)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("internal error", err)
        return r

    def test_deep_json_raises_recursion_error_in_the_parser(self):
        with self.assertRaises(RecursionError):
            json.loads(DEEP)

    def test_sensor_record(self):
        self.poison(os.path.join(self.cfg, "statusline", "sensor", SID + ".json"))
        r = self.assertCleanRun()
        self.assertEqual(r["signal"], "none")

    def test_intent(self):
        self.sensor(at=NOW)
        self.poison(os.path.join(self.store, "intent.json"))
        r = self.assertCleanRun()
        self.assertEqual((r["signal"], r["intent"]["mode"]), ("ok", "present"))

    def test_own_claim_file_is_replaced(self):
        self.poison(os.path.join(self.store, "claims", "myrepo.json"))
        r = self.assertCleanRun()
        self.assertEqual(r["claims"]["action"], "replaced-unreadable")
        self.assertEqual(self.read_claim("myrepo")["session_id"], SID)

    def test_other_claim_file_is_not_counted(self):
        self.poison(os.path.join(self.store, "claims", "other.json"))
        r = self.assertCleanRun()
        self.assertEqual(r["claims"]["fresh"], 1)

    def test_registry_file(self):
        self.poison(os.path.join(self.cfg, "sessions", "42.json"))
        self.assertCleanRun(env=dict(self.env, CLAUDE_PID="42"))
        self.assertIsNone(self.read_claim("myrepo")["session_name"])

    def test_samples_line_is_skipped_and_pruned(self):
        os.makedirs(self.store)
        with open(os.path.join(self.store, "samples.jsonl"), "w") as f:
            f.write(DEEP + "\n")
            f.write('{"at": ' + "9" * 5000 + ', "five_hour": {"used_percentage": 1, "resets_at": 1}}\n')
        self.samples([(NOW - H, (8.0, NOW + 2 * H), (29.0, NOW + 100 * H))])
        self.sensor(at=NOW)
        with mock.patch.object(qb, "SAMPLES_PRUNE_AT", 10):
            r = self.assertCleanRun()
        self.assertAlmostEqual(r["windows"]["five_hour"]["velocity"], 2.0, places=3)
        with open(os.path.join(self.store, "samples.jsonl")) as f:
            rows = [json.loads(x) for x in f]
        self.assertEqual([x["at"] for x in rows], [NOW - H, NOW])

    def test_sink_line_is_skipped(self):
        d = os.path.join(self.cfg, "plugins", "data", "claude-analytics-kmacmcfarlane", "samples")
        os.makedirs(d)
        with open(os.path.join(d, "2026-09-22.jsonl"), "w") as f:
            f.write(DEEP + "\n")
        self.sensor(at=NOW)
        r = self.assertCleanRun()
        self.assertEqual(r["source"]["history"], "samples")

    def test_huge_numbers_are_not_times(self):
        self.assertIsNone(qb.epoch(10 ** 400))
        self.assertIsNone(qb.finite(10 ** 400))
        self.assertIsNone(qb.epoch("99999-01-01T00:00:00"))


class TestHardening(Base):
    """99b4: the F1 review r2 lows."""

    def claim_path(self, repo="myrepo"):
        return os.path.join(self.store, "claims", repo + ".json")

    # L1: replaced-unreadable only on a parse failure of a regular file under READ_MAX
    def test_non_object_json_claim_is_replaced(self):
        os.makedirs(os.path.dirname(self.claim_path()))
        with open(self.claim_path(), "w") as f:
            f.write("[1, 2]")
        _, r, _ = self.run_qb()
        self.assertEqual(r["claims"]["action"], "replaced-unreadable")
        self.assertEqual(self.read_claim("myrepo")["session_id"], SID)

    def test_bad_utf8_claim_is_replaced(self):
        os.makedirs(os.path.dirname(self.claim_path()))
        with open(self.claim_path(), "wb") as f:
            f.write(b"\xff\xfe{")
        _, r, _ = self.run_qb()
        self.assertEqual(r["claims"]["action"], "replaced-unreadable")

    def assertUnusable(self, r):
        c = r["claims"]
        self.assertEqual((c["action"], c["written"], c.get("unusable")), ("conflict", False, True))

    def test_oversized_claim_is_a_conflict_and_left_alone(self):
        os.makedirs(os.path.dirname(self.claim_path()))
        body = json.dumps({"v": 1, "session_id": "other", "at": NOW, "pad": "x" * 200})
        with open(self.claim_path(), "w") as f:
            f.write(body)
        with mock.patch.object(qb, "READ_MAX", 64):
            rc, r, _ = self.run_qb()
        self.assertEqual(rc, 0)
        self.assertUnusable(r)
        with open(self.claim_path()) as f:
            self.assertEqual(f.read(), body)

    def test_oversized_claim_is_left_alone_even_with_takeover(self):
        os.makedirs(os.path.dirname(self.claim_path()))
        with open(self.claim_path(), "w") as f:
            f.write("x" * 100)
        with mock.patch.object(qb, "READ_MAX", 64):
            _, r, _ = self.run_qb("--takeover")
        self.assertUnusable(r)
        with open(self.claim_path()) as f:
            self.assertEqual(f.read(), "x" * 100)

    def test_directory_at_claim_path_is_a_conflict(self):
        os.makedirs(self.claim_path())
        rc, r, _ = self.run_qb()
        self.assertEqual(rc, 0)
        self.assertUnusable(r)
        self.assertTrue(os.path.isdir(self.claim_path()))

    def test_symlink_at_claim_path_is_a_conflict_and_target_untouched(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = os.path.join(outside.name, "target")
        with open(target, "w") as f:
            f.write("not json")
        os.makedirs(os.path.dirname(self.claim_path()))
        os.symlink(target, self.claim_path())
        _, r, _ = self.run_qb()
        self.assertUnusable(r)
        self.assertTrue(os.path.islink(self.claim_path()))
        with open(target) as f:
            self.assertEqual(f.read(), "not json")

    def test_dangling_symlink_at_claim_path_is_a_conflict(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = os.path.join(outside.name, "target")
        os.makedirs(os.path.dirname(self.claim_path()))
        os.symlink(target, self.claim_path())
        _, r, _ = self.run_qb()
        self.assertUnusable(r)
        self.assertFalse(os.path.lexists(target))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads mode-000 files")
    def test_unreadable_claim_is_a_conflict(self):
        os.makedirs(os.path.dirname(self.claim_path()))
        with open(self.claim_path(), "w") as f:
            f.write("{}")
        os.chmod(self.claim_path(), 0)
        _, r, _ = self.run_qb()
        self.assertUnusable(r)
        os.chmod(self.claim_path(), 0o600)
        with open(self.claim_path()) as f:
            self.assertEqual(f.read(), "{}")

    # L2: a symlink planted at samples.lock never creates or touches its target
    def test_symlink_at_samples_lock_creates_nothing_outside_the_store(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = os.path.join(outside.name, "planted")
        os.makedirs(self.store)
        os.symlink(target, os.path.join(self.store, "samples.lock"))
        self.sensor(at=NOW)
        rc, r, err = self.run_qb()
        self.assertFalse(os.path.lexists(target))
        self.assertEqual(rc, 1)
        self.assertIn("samples.jsonl append failed", err)
        self.assertEqual(r["signal"], "ok")

    def test_symlink_at_samples_jsonl_writes_nothing_outside_the_store(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        missing = os.path.join(outside.name, "planted")
        existing = os.path.join(outside.name, "existing")
        with open(existing, "w") as f:
            f.write("keep")
        for target in (missing, existing):
            with self.subTest(target=os.path.basename(target)):
                link = os.path.join(self.store, "samples.jsonl")
                os.makedirs(self.store, exist_ok=True)
                if os.path.lexists(link):
                    os.unlink(link)
                os.symlink(target, link)
                self.sensor(at=NOW)
                rc, r, err = self.run_qb()
                self.assertEqual(rc, 1)
                self.assertIn("samples.jsonl append failed", err)
                self.assertEqual(r["signal"], "ok")
                self.assertTrue(os.path.islink(link))
        self.assertFalse(os.path.lexists(missing))
        with open(existing) as f:
            self.assertEqual(f.read(), "keep")

    def test_symlink_at_samples_lock_leaves_an_existing_target_alone(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = os.path.join(outside.name, "planted")
        with open(target, "w") as f:
            f.write("keep")
        os.chmod(target, 0o644)
        os.makedirs(self.store)
        os.symlink(target, os.path.join(self.store, "samples.lock"))
        self.sensor(at=NOW)
        self.run_qb()
        with open(target) as f:
            self.assertEqual(f.read(), "keep")
        self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), 0o644)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes mode-0400 files")
    def test_read_only_lock_file_still_locks(self):
        os.makedirs(self.store)
        lock = os.path.join(self.store, "samples.lock")
        with open(lock, "w"):
            pass
        os.chmod(lock, 0o400)
        self.sensor(at=NOW)
        rc, _, err = self.run_qb()
        self.assertEqual(rc, 0, err)
        self.assertTrue(os.path.exists(os.path.join(self.store, "samples.jsonl")))

    # L3: only parse failures are skipped as bad lines
    def test_parse_failures_are_skipped(self):
        p = os.path.join(self.cfg, "x.jsonl")
        with open(p, "wb") as f:
            f.write(b"not json\n\xff\xfe\n" + DEEP.encode() + b"\n{\"ok\": 1}\n")
        self.assertEqual(qb.read_jsonl(p, lambda d: d), [{"ok": 1}])

    def test_error_other_than_a_parse_failure_is_not_a_bad_line(self):
        p = os.path.join(self.cfg, "x.jsonl")
        with open(p, "w") as f:
            f.write('{"ok": 1}\n')

        def broken(d):
            raise KeyError("a bug in parse")

        with self.assertRaises(KeyError):
            qb.read_jsonl(p, broken)

    def test_parse_callback_error_reaches_main_as_an_internal_error(self):
        self.samples([(NOW - H, (8.0, NOW + 2 * H), (29.0, NOW + 100 * H))])
        self.sensor(at=NOW)

        def broken(d):
            raise KeyError("a bug in parse")

        with mock.patch.object(qb, "parse_sample", broken):
            rc, r, err = self.run_qb()
        self.assertEqual((rc, r["signal"], r["reason"]), (1, "none", "internal error"))
        self.assertIn("KeyError", err)

    def test_symlink_to_a_readable_claim_is_judged_by_content(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = os.path.join(outside.name, "claim.json")
        body = json.dumps({"v": 1, "repo": "myrepo", "session_id": SID, "at": NOW - 60,
                           "in_flight": []})
        with open(target, "w") as f:
            f.write(body)
        os.makedirs(os.path.dirname(self.claim_path()))
        os.symlink(target, self.claim_path())
        _, r, _ = self.run_qb()
        self.assertEqual(r["claims"]["action"], "refreshed")
        self.assertFalse(os.path.islink(self.claim_path()))
        with open(target) as f:
            self.assertEqual(f.read(), body)

    def test_missing_file_reads_as_empty(self):
        self.assertEqual(qb.read_jsonl(os.path.join(self.cfg, "nope.jsonl"), qb.parse_sample), [])


class TestEpoch(Base):
    def test_milliseconds_heuristic(self):
        self.assertEqual(qb.epoch(1_790_000_000_123), 1_790_000_000.123)
        self.assertEqual(qb.epoch(1_790_000_000), 1_790_000_000.0)
        self.assertEqual(qb.epoch(99_999_999_999), 99_999_999_999.0)   # at the threshold: seconds
        self.assertEqual(qb.epoch(100_000_000_001), 100_000_000.001)   # above it: ms
        self.assertIsNone(qb.epoch(True))
        self.assertIsNone(qb.epoch(float("nan")))

    def test_ms_stamps_work_end_to_end(self):
        self.sensor(five=(10.0, (NOW + 2 * H) * 1000), week=(30.0, (NOW + 100 * H) * 1000),
                    at=NOW * 1000)
        _, r, _ = self.run_qb()
        self.assertEqual(r["signal"], "ok")
        self.assertAlmostEqual(r["windows"]["five_hour"]["hours_to_reset"], 2.0, places=3)


class TestSinkEdges(Base):
    def sinkdir(self):
        d = os.path.join(self.cfg, "plugins", "data", "claude-analytics-kmacmcfarlane", "samples")
        os.makedirs(d, exist_ok=True)
        return d

    def line(self, ts, five, week=30.0):
        return json.dumps({"ts": ts, "session_id": "s", "rate_limits": {
            "five_hour": {"used_percentage": five, "resets_at": NOW + 3 * H},
            "seven_day": {"used_percentage": week, "resets_at": NOW + 100 * H}}}) + "\n"

    def test_future_line_neither_makes_sink_live_nor_wins_the_reading(self):
        d = self.sinkdir()
        with open(os.path.join(d, "2026-09-22.jsonl"), "w") as f:
            f.write(self.line(NOW + 10 * H, 99.0))           # clock-skewed writer
            f.write(self.line(NOW - 5 * H, 10.0))            # old, so not live
        _, r, _ = self.run_qb()
        self.assertEqual(r["signal"], "none")                # no sensor record, sink not live
        self.sensor(five=(20.0, NOW + 3 * H), at=NOW)
        _, r, _ = self.run_qb()
        self.assertEqual(r["source"]["history"], "samples")

    def test_future_line_ignored_when_sink_is_live(self):
        d = self.sinkdir()
        with open(os.path.join(d, "2026-09-22.jsonl"), "w") as f:
            f.write(self.line(NOW + 10 * H, 99.0))
            f.write(self.line(NOW - 60, 12.0))
        _, r, _ = self.run_qb()
        self.assertEqual((r["source"]["reading"], r["windows"]["five_hour"]["used"]), ("sink", 12.0))

    def test_only_day_files_are_read(self):
        d = self.sinkdir()
        for n in ("usage-cache-2026-09-22.jsonl", "2026-09-22.jsonl.tmp", "latest.jsonl"):
            with open(os.path.join(d, n), "w") as f:
                f.write(self.line(NOW - 60, 50.0))
        _, r, _ = self.run_qb()
        self.assertEqual(r["signal"], "none")
        self.assertEqual(r["source"]["history"], "samples")

    def test_dir_glob_needs_the_marketplace_suffix(self):
        os.makedirs(os.path.join(self.cfg, "plugins", "data", "claude-analyticsX", "samples"))
        self.assertEqual(qb.sink_dirs(self.cfg), [])
        self.assertEqual(qb.sink_dirs(self.cfg), qb.sink_dirs(self.cfg))
        self.sinkdir()
        self.assertEqual(len(qb.sink_dirs(self.cfg)), 1)


class TestClaimRaces(Base):
    def test_concurrent_creators_on_empty_claims_one_wins(self):
        env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg)
        env.pop("CLAUDE_PID", None)
        n = 12
        procs = [subprocess.Popen([sys.executable, str(SCRIPT), "--now", str(NOW), "--repo", "r",
                                   "--session", "s%02d" % i], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, env=env) for i in range(n)]
        results = []
        for p in procs:
            out, err = p.communicate(timeout=60)
            self.assertEqual(p.returncode, 0, err)
            results.append(json.loads(out)["claims"])
        winners = [c for c in results if c["written"]]
        self.assertEqual(len(winners), 1, [c["action"] for c in results])
        self.assertEqual(winners[0]["action"], "created")
        self.assertTrue(all(c["action"] == "conflict" for c in results if not c["written"]))
        with open(os.path.join(self.store, "claims", "r.json")) as f:
            on_disk = json.load(f)["session_id"]
        self.assertEqual(on_disk, "s%02d" % results.index(winners[0]))
        self.assertEqual([n for n in os.listdir(os.path.join(self.store, "claims"))], ["r.json"])

    def test_create_race_loser_rejudges(self):
        real = qb.create_exclusive_json

        def someone_first(path, obj):
            real(path, {"v": 1, "session_id": "other", "at": NOW, "in_flight": []})
            return real(path, obj)

        with mock.patch.object(qb, "create_exclusive_json", side_effect=someone_first):
            _, r, _ = self.run_qb()
        self.assertEqual((r["claims"]["action"], r["claims"]["written"]), ("conflict", False))
        self.assertEqual(self.read_claim("myrepo")["session_id"], "other")

    def test_replace_then_reread_detects_a_lost_race(self):
        self.claim("myrepo", {"v": 1, "session_id": SID, "at": NOW - 60, "in_flight": []})
        real = qb.atomic_write_json

        def then_takeover(path, obj):
            real(path, obj)
            real(path, {"v": 1, "session_id": "taker", "at": NOW, "in_flight": []})

        with mock.patch.object(qb, "atomic_write_json", side_effect=then_takeover):
            _, r, _ = self.run_qb()
        c = r["claims"]
        self.assertEqual((c["action"], c["written"], c["lost_race"]), ("conflict", False, True))
        self.assertEqual(c["previous"]["session_id"], "taker")

    def test_refresh_keeps_identity_it_cannot_read(self):
        self.claim("myrepo", {"v": 1, "session_id": SID, "at": NOW - 60, "in_flight": [],
                              "session_name": "lib", "pid": 7, "pidDomain": "d", "procStart": "p"})
        self.run_qb()  # no CLAUDE_PID: identity unreadable this call
        c = self.read_claim("myrepo")
        self.assertEqual((c["session_name"], c["pid"], c["pidDomain"], c["procStart"], c["at"]),
                         ("lib", 7, "d", "p", NOW))


class TestRepoName(Base):
    def test_worktree_resolves_to_main_repo(self):
        main = os.path.join(self.cfg, "src", "mainrepo")
        wt = os.path.join(self.cfg, "elsewhere", "wt-name")
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main"]
        subprocess.run(git + ["init", "-q", main], check=True)
        subprocess.run(git + ["-C", main, "commit", "-q", "--allow-empty", "-m", "x"], check=True)
        subprocess.run(git + ["-C", main, "worktree", "add", "-q", "-b", "b", wt], check=True)
        self.assertEqual(qb.repo_name(wt), "mainrepo")
        sub = os.path.join(wt, "deep")
        os.makedirs(sub)
        self.assertEqual(qb.repo_name(sub), "mainrepo")

    def test_bare_repo_strips_dot_git(self):
        bare = os.path.join(self.cfg, "proj.git")
        subprocess.run(["git", "init", "-q", "--bare", bare], check=True)
        self.assertEqual(qb.repo_name(bare), "proj")


class TestCli(Base):
    def test_subprocess_prints_json(self):
        self.sensor(at=NOW)
        env = dict(os.environ, **self.env)
        p = subprocess.run([sys.executable, str(SCRIPT), "--now", str(NOW), "--repo", "r"],
                           capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout)
        self.assertEqual((r["signal"], r["claims"]["action"]), ("ok", "created"))

    def test_bad_argument_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(qb.main(["--stale-after", "x"], env=self.env), 2)

    def test_never_names_a_settings_file(self):
        src = SCRIPT.read_text()
        self.assertNotIn("settings.json", src)
        self.assertNotIn(".claude.json", src)


@unittest.skipUnless(hasattr(os, "mkfifo"), "needs os.mkfifo")
class TestFifo(Base):
    """4e5d: a FIFO with no peer planted at a store or sink data file must not
    block the script. Each run is a subprocess with a timeout, so a regression
    fails the test instead of hanging the suite."""

    def run_cli(self, *argv):
        env = dict(os.environ, **self.env)
        try:
            p = subprocess.run([sys.executable, str(SCRIPT), "--now", str(NOW), "--repo", "myrepo"]
                               + list(argv), capture_output=True, text=True, env=env, timeout=10)
        except subprocess.TimeoutExpired:
            self.fail("quota_budget.py blocked on a FIFO")
        return p.returncode, json.loads(p.stdout), p.stderr

    def fifo(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        os.mkfifo(path, 0o600)
        return path

    def test_fifo_at_samples_jsonl_fails_the_append_as_a_store_write_error(self):
        path = self.fifo(os.path.join(self.store, "samples.jsonl"))
        self.sensor(at=NOW)
        rc, r, err = self.run_cli()
        self.assertEqual(rc, 1)
        self.assertIn("samples.jsonl append failed", err)
        self.assertEqual(len(r["errors"]), 1)
        self.assertEqual((r["signal"], r["claims"]["action"]), ("ok", "created"))
        self.assertTrue(stat.S_ISFIFO(os.lstat(path).st_mode))

    def test_fifo_at_samples_jsonl_reads_as_absent(self):
        self.fifo(os.path.join(self.store, "samples.jsonl"))
        self.sensor(at=NOW)
        rc, r, err = self.run_cli("--read-only")
        self.assertEqual(rc, 0, err)
        self.assertEqual(r["signal"], "ok")
        self.assertEqual(r["windows"]["five_hour"]["velocity_points"], 1)

    def test_fifo_at_samples_lock_fails_the_append_as_a_store_write_error(self):
        self.fifo(os.path.join(self.store, "samples.lock"))
        self.sensor(at=NOW)
        rc, r, err = self.run_cli()
        self.assertEqual(rc, 1)
        self.assertIn("samples.jsonl append failed", err)
        self.assertEqual(r["signal"], "ok")
        self.assertFalse(os.path.exists(os.path.join(self.store, "samples.jsonl")))

    def test_fifo_sink_day_file_reads_as_absent(self):
        d = os.path.join(self.cfg, "plugins", "data", "claude-analytics-kmacmcfarlane", "samples")
        self.fifo(os.path.join(d, "2026-09-22.jsonl"))
        with open(os.path.join(d, "2026-09-21.jsonl"), "w") as f:
            f.write(json.dumps({"ts": NOW - 60, "session_id": "s", "rate_limits": {
                "five_hour": {"used_percentage": 12.0, "resets_at": NOW + 3 * H},
                "seven_day": {"used_percentage": 30.0, "resets_at": NOW + 100 * H}}}) + "\n")
        rc, r, err = self.run_cli()
        self.assertEqual(rc, 0, err)
        self.assertEqual((r["source"]["reading"], r["windows"]["five_hour"]["used"]), ("sink", 12.0))

    def test_fifo_at_claim_path_is_an_unusable_conflict(self):
        path = self.fifo(os.path.join(self.store, "claims", "myrepo.json"))
        for argv in ((), ("--takeover",)):
            with self.subTest(argv=argv):
                rc, r, err = self.run_cli(*argv)
                self.assertEqual(rc, 0, err)
                c = r["claims"]
                self.assertEqual((c["action"], c["written"], c.get("unusable"), c["fresh"]),
                                 ("conflict", False, True, 0))
                self.assertTrue(stat.S_ISFIFO(os.lstat(path).st_mode))

    @unittest.skipUnless(hasattr(signal, "SIGALRM"), "needs SIGALRM for the timeout guard")
    def test_fifo_is_refused_by_every_opener_without_blocking(self):
        path = self.fifo(os.path.join(self.cfg, "f.json"))

        def blocked(signum, frame):
            raise AssertionError("an opener blocked on a FIFO")

        old = signal.signal(signal.SIGALRM, blocked)
        self.addCleanup(signal.signal, signal.SIGALRM, old)
        self.addCleanup(signal.alarm, 0)
        signal.alarm(10)
        self.assertIsNone(qb.read_json(path))
        self.assertEqual(qb.read_jsonl(path, lambda d: d), [])
        self.assertEqual(qb.claim_file_state(path), "unusable")
        with mock.patch.object(qb.os, "lstat", lambda p: os.stat_result((stat.S_IFREG | 0o600,) + (0,) * 9)):
            self.assertEqual(qb.claim_file_state(path), "unusable")  # past a raced lstat
        with self.assertRaises(OSError):
            qb.open_lock(path)


if __name__ == "__main__":
    unittest.main()
