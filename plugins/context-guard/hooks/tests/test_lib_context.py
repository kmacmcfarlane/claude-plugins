import json, os, sys, tempfile, time, unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Operator settings, canonical and deprecated alias: scrubbed so a stray value
# in the environment running the tests cannot leak in.
OPERATOR_ENV = ("CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW",
                "CONTEXT_GUARD_LEDGER_EVERY", "CLAUDE_KIT_LEDGER_EVERY")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        scrub = mock.patch.dict(os.environ)
        scrub.start()
        self.addCleanup(scrub.stop)
        for k in OPERATOR_ENV:
            os.environ.pop(k, None)
        os.environ["CLAUDE_CONFIG_DIR"] = self.tmp.name
        global L, ledger
        import lib_context as L
        import ledger

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def put_exact(self, sid, block):
        """The status line's exact block for `sid`, as its sensor record."""
        p = L.sensor_path(sid)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump({"v": 1, "exact": block}, f)


class TestThresholds(Base):
    def test_anchors(self):
        self.assertEqual(L.thresholds(1_000_000), {"due": 150_000, "hard": 60_000})
        self.assertEqual(L.thresholds(200_000), {"due": 70_000, "hard": 40_000})

    def test_clamped_and_monotonic(self):
        self.assertEqual(L.thresholds(100_000), {"due": 70_000, "hard": 40_000})
        self.assertEqual(L.thresholds(2_000_000), {"due": 150_000, "hard": 60_000})
        mid = L.thresholds(600_000)
        self.assertTrue(70_000 < mid["due"] < 150_000)
        self.assertTrue(40_000 < mid["hard"] < 60_000)


class TestEpoch(Base):
    def test_reset_clears_due_and_deferred_keeps_checkpoint_history(self):
        L.save_state("s", {"epoch": 3, "compact_deferred": True,
                           "due": {"tok": 1}, "checkpoint_epoch": 3})
        st = L.reset_epoch("s")
        self.assertEqual(L.epoch(st), 4)
        self.assertNotIn("compact_deferred", st)
        self.assertNotIn("due", st)
        self.assertFalse(L.checkpointed_this_epoch(st))

    def test_mark_checkpoint_binds_to_current_epoch(self):
        L.save_state("s", {"epoch": 2})
        st = L.mark_checkpoint("s")
        self.assertTrue(L.checkpointed_this_epoch(st))
        st = L.reset_epoch("s")
        self.assertFalse(L.checkpointed_this_epoch(st))

    def test_compact_summary_saved(self):
        st = L.reset_epoch("s", compact_summary="the summary")
        self.assertEqual(st["compact_summary"], "the summary")

    def test_reset_demotes_fresh_exact_to_window_only(self):
        # A record written seconds before the boundary is still fresh after
        # it; the new epoch must not inherit its tokens, only its window.
        import time
        self.put_exact("s", {"pct": 95.0, "tokens": 950_000,
                             "window": 1_000_000, "at": time.time() - 300})
        st = L.reset_epoch("s")
        self.assertEqual(L.sensor("s", st), {"window": 1_000_000, "at": 0})
        self.assertEqual(L.sensor("s"), {"window": 1_000_000, "at": 0})
        self.assertNotIn("exact", L.load_state("s"))   # demoted on read, not written
        # No transcript yet (status line not re-rendered): unknown, not 950K.
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win), (0, 1_000_000))
        self.assertTrue(src.startswith("inferred"))

    def test_reset_without_exact_record_is_a_noop_for_it(self):
        st = L.reset_epoch("s")
        self.assertNotIn("exact", st)


class TestDepth(Base):
    def _transcript(self, tokens):
        p = os.path.join(self.tmp.name, "t.jsonl")
        rec = {"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tokens - 2,
            "cache_creation_input_tokens": 0}}}
        open(p, "w").write(json.dumps(rec) + "\n")
        return p

    def test_exact_preferred_over_inference(self):
        import time
        self.put_exact("s", {"pct": 50.0, "tokens": 500_000,
                             "window": 1_000_000, "at": time.time()})
        tok, win, pct, src = L.depth(self._transcript(100_000), "s")
        self.assertEqual((tok, src), (500_000, "exact"))

    def test_stale_exact_keeps_window_and_token_floor(self):
        # Live-fired 2026-09-16: exact {186454 of 1M} older than EXACT_MAX_AGE_S
        # was discarded; inference guessed 200K and HARD-blocked a 1M session.
        self.put_exact("s", {"pct": 18.6, "tokens": 186_454,
                             "window": 1_000_000, "at": 0})
        tok, win, pct, src = L.depth(self._transcript(186_454), "s")
        self.assertTrue(src.startswith("inferred"))
        self.assertEqual(win, 1_000_000)          # window never shrinks
        self.assertEqual(tok, 186_454)
        self.assertLess(pct, 20)
        # transcript ahead of the stale record: transcript wins
        self.assertEqual(L.depth(self._transcript(300_000), "s")[0], 300_000)
        # transcript behind it: exact tokens are the floor
        self.assertEqual(L.depth(self._transcript(100_000), "s")[0], 186_454)

    def test_stale_exact_token_floor_dropped_after_boundary(self):
        self.put_exact("s", {"pct": 95.0, "tokens": 950_000,
                             "window": 1_000_000, "at": 0})
        p = os.path.join(self.tmp.name, "b.jsonl")
        rec = lambda tok: json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tok - 2,
            "cache_creation_input_tokens": 0}}})
        open(p, "w").write(rec(950_000) + "\n"
                           + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n"
                           + rec(30_000) + "\n")
        tok, win, pct, src = L.depth(p, "s")
        self.assertEqual((tok, win), (30_000, 1_000_000))  # window kept, floor dropped
        self.assertTrue(src.startswith("inferred"))
        self.assertEqual(L.scan_usage(p), (30_000, 950_000, True))
        self.assertEqual(L.read_usage(p), (30_000, 950_000))

    def test_demoted_exact_after_clear_uses_transcript_only(self):
        # /clear starts a transcript with no compact_boundary line: the
        # demoted record must not floor the count even without a boundary.
        import time
        self.put_exact("s", {"pct": 95.0, "tokens": 950_000,
                             "window": 1_000_000, "at": time.time() - 300})
        L.reset_epoch("s")
        tok, win, pct, src = L.depth(self._transcript(30_000), "s")
        self.assertEqual((tok, win), (30_000, 1_000_000))
        self.assertLess(pct, 5)
        self.assertEqual(src, "inferred, window from status line")
        # A record written after the boundary (past the grace) is exact again.
        at = L.load_state("s")["epoch_at"] + L.EPOCH_GRACE_S + 1
        self.put_exact("s", {"pct": 3.0, "tokens": 30_000,
                             "window": 1_000_000, "at": at})
        self.assertEqual(L.depth(self._transcript(30_000), "s")[3], "exact")

    def test_stale_exact_missing_transcript_still_reports(self):
        self.put_exact("s", {"pct": 50.0, "tokens": 500_000,
                             "window": 1_000_000, "at": 0})
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win), (500_000, 1_000_000))
        self.assertTrue(src.startswith("inferred"))

    def test_no_exact_record_is_plain_inferred(self):
        tok, win, pct, src = L.depth(self._transcript(100_000), "s")
        self.assertEqual((tok, win, src), (100_000, 200_000, "inferred"))

    def test_boundary_resets_current_keeps_peak(self):
        p = os.path.join(self.tmp.name, "b.jsonl")
        rec = lambda tok: json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tok - 2,
            "cache_creation_input_tokens": 0}}})
        open(p, "w").write(rec(600_000) + "\n"
                           + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n"
                           + rec(20_000) + "\n")
        tok, win, pct, src = L.depth(p)
        self.assertEqual((tok, win), (20_000, 1_000_000))  # fresh cur, old peak keeps window
        open(p, "a").write(json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n")
        self.assertEqual(L.depth(p)[0], 0)  # boundary with no usage yet -> unknown, not stale

    def test_window_inferred_from_peak(self):
        self.assertEqual(L.depth(self._transcript(100_000))[1], 200_000)
        self.assertEqual(L.depth(self._transcript(400_000))[1], 1_000_000)

    def test_window_floor(self):
        self.assertEqual(L.window(100_000), 200_000)
        self.assertEqual(L.window(100_000, floor=1_000_000), 1_000_000)
        self.assertEqual(L.window(400_000, floor=200_000), 1_000_000)  # floor never lowers
        self.assertEqual(L.window(100_000, floor=0), 200_000)

    def test_window_env_override(self):
        # The canonical name and the deprecated alias pin alike.
        for name in ("CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW"):
            with self.subTest(name=name):
                os.environ[name] = "500000"
                try:
                    self.assertEqual(L.window(100_000), 500_000)
                    self.assertEqual(L.window(100_000, floor=1_000_000), 500_000)  # pin wins
                    self.assertEqual(L.depth(self._transcript(100_000))[1], 500_000)
                    self.assertTrue(L._pinned(os.environ))
                finally:
                    os.environ.pop(name, None)

    def test_window_env_canonical_wins(self):
        os.environ["CONTEXT_GUARD_CONTEXT_WINDOW"] = "500000"
        os.environ["CLAUDE_KIT_CONTEXT_WINDOW"] = "300000"
        self.assertEqual(L.window(100_000), 500_000)
        self.assertTrue(L._pinned(os.environ))
        # A malformed canonical value never switches off a valid alias pin:
        # the pin only removes derived blocks, so falling through is fail-safe.
        for bad in ("lots", "1m", " 1000000", "1_000_000"):
            with self.subTest(bad=bad):
                os.environ["CONTEXT_GUARD_CONTEXT_WINDOW"] = bad
                self.assertEqual(L.window(100_000), 300_000)
                self.assertTrue(L._pinned(os.environ))
        # Both malformed: no pin, as an invalid value always meant.
        os.environ["CONTEXT_GUARD_CONTEXT_WINDOW"] = "1m"
        os.environ["CLAUDE_KIT_CONTEXT_WINDOW"] = "1m"
        self.assertEqual(L.window(100_000), 200_000)
        self.assertFalse(L._pinned(os.environ))
        os.environ["CLAUDE_KIT_CONTEXT_WINDOW"] = "300000"
        # An empty canonical value counts as unset: the alias applies.
        os.environ["CONTEXT_GUARD_CONTEXT_WINDOW"] = ""
        self.assertEqual(L.window(100_000), 300_000)
        self.assertTrue(L._pinned(os.environ))

    def test_window_env_invalid_is_ignored(self):
        for name in ("CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW"):
            for v in ("", "1e6", "-5", "abc"):
                with self.subTest(name=name, v=v):
                    os.environ[name] = v
                    try:
                        self.assertEqual(L.window(100_000), 200_000)
                        self.assertFalse(L._pinned(os.environ))
                    finally:
                        os.environ.pop(name, None)


def _iso(t):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class TestEpochRule(Base):
    """A transcript count belongs to the epoch its usage line was written in:
    after PostCompact stamps epoch_at, the compact_boundary line may not have
    reached the transcript when the queued opener's hook scans it (observed
    in spike bace's transcripts, Claude Code 2.1.284, cases B0, S2, S3)."""

    def setUp(self):
        super().setUp()
        self.p = os.path.join(self.tmp.name, "t.jsonl")
        self.t_old = time.time() - 60

    def usage(self, tokens, at=None):
        rec = {"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tokens - 2,
            "cache_creation_input_tokens": 0}}}
        if at is not None:
            rec["timestamp"] = _iso(at)
        return rec

    def write(self, *recs, append=False):
        with open(self.p, "a" if append else "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        return self.p

    def queued_opener(self):
        """The non-usage lines a queued prompt writes before the boundary lands."""
        return ({"type": "queue-operation", "operation": "enqueue",
                 "timestamp": _iso(time.time())},
                {"type": "attachment", "timestamp": _iso(time.time()),
                 "attachment": {"type": "hook_success", "content": "x"}})

    def test_fresh_scan_drops_a_pre_epoch_count_on_both_inferred_paths(self):
        self.write(self.usage(950_000, self.t_old))
        before = {m: L.measure(self.p, "s", mirror=m) for m in (True, False)}
        L.reset_epoch("s")
        for mirror in (True, False):
            with self.subTest(mirror=mirror):
                m = L.measure(self.p, "s", mirror=mirror)
                self.assertEqual(before[mirror]["tokens"], 950_000)
                self.assertEqual(m["tokens"], 0)
                self.assertEqual(m["source"], before[mirror]["source"])
                self.assertTrue(m["source"].startswith("inferred"))
                self.assertEqual(m["model_window"], 1_000_000)   # peak still sets it
                self.assertIn("predates this epoch", m["note"])
        self.assertEqual(L.depth(self.p, "s", mirror=False)[0], 0)

    def test_equal_stamp_is_the_earlier_epoch(self):
        self.write(self.usage(950_000, self.t_old))
        L.save_state("s", {"epoch": 1, "epoch_at": L._iso_ts(_iso(self.t_old))})
        self.assertEqual(L.measure(self.p, "s")["tokens"], 0)
        self.assertEqual(L.measure(self.p, "s", mirror=False)["tokens"], 0)

    def test_a_line_of_the_new_epoch_recovers(self):
        self.write(self.usage(950_000, self.t_old))
        L.reset_epoch("s")
        epoch_at = L.load_state("s")["epoch_at"]
        self.write({"type": "system", "subtype": "compact_boundary",
                    "timestamp": _iso(epoch_at + 0.1)},
                   self.usage(30_000, epoch_at + 0.5), append=True)
        for mirror in (True, False):
            with self.subTest(mirror=mirror):
                m = L.measure(self.p, "s", mirror=mirror)
                self.assertEqual((m["tokens"], m["model_window"]), (30_000, 1_000_000))
                self.assertTrue(m["source"].startswith("inferred"))
                self.assertNotIn("predates", m["note"])

    def test_unstamped_lines_behave_as_before(self):
        # every fixture before this rule: no timestamp, no drop
        self.write(self.usage(950_000))
        L.reset_epoch("s")
        for mirror in (True, False):
            with self.subTest(mirror=mirror):
                m = L.measure(self.p, "s", mirror=mirror)
                self.assertEqual(m["tokens"], 950_000)
                self.assertNotIn("predates", m["note"])

    def test_scans_report_cur_at(self):
        self.write(self.usage(950_000, self.t_old))
        want = L._iso_ts(_iso(self.t_old))
        self.assertEqual(L.scan_transcript(self.p)["cur_at"], want)
        self.assertEqual(L._scan_usage_at(self.p), (950_000, 950_000, False, want))
        self.assertEqual(L.scan_usage(self.p), (950_000, 950_000, False))
        b_at = self.t_old + 5
        self.write({"type": "system", "subtype": "compact_boundary",
                    "timestamp": _iso(b_at)}, append=True)
        r = L.scan_transcript(self.p)
        self.assertEqual((r["cur"], r["cur_at"]), (0, L._iso_ts(_iso(b_at))))
        self.assertEqual(L._scan_usage_at(self.p)[::3], (0, L._iso_ts(_iso(b_at))))

    def spy_cache_start(self):
        """Patch _cache_start to record the offset each scan resumed from."""
        starts, real = [], L._cache_start

        def spy(*a):
            r = real(*a)
            starts.append(r[0])
            return r
        patch = mock.patch.object(L, "_cache_start", spy)
        patch.start()
        self.addCleanup(patch.stop)
        return starts

    def test_cached_resume_carries_cur_at(self):
        # The S2 path: the prompt gate kept the scan cache on the previous
        # prompt; the opener's scan resumes from it and reads no usage line,
        # so cur and cur_at come from the cache alone.
        self.write(self.usage(950_000, self.t_old))
        m = L.measure(self.p, "s")
        cache = m["scan_cache"]
        self.assertEqual(cache["cur_at"], L._iso_ts(_iso(self.t_old)))
        L.update_state("s", lambda st: st.update(scan=cache))
        self.write(*self.queued_opener(), append=True)
        L.reset_epoch("s")
        starts = self.spy_cache_start()
        m = L.measure(self.p, "s")
        self.assertEqual(starts, [cache["size"]])            # resumed, not rescanned
        self.assertEqual(m["tokens"], 0)
        self.assertTrue(m["source"].startswith("inferred"))
        self.assertIn("predates this epoch", m["note"])
        self.assertEqual(m["scan_cache"]["cur_at"], cache["cur_at"])

    def test_malformed_or_missing_cached_cur_at_reads_as_none_without_rescan(self):
        self.write(self.usage(950_000, self.t_old))
        good = L.scan_transcript(self.p)["cache"]
        self.write(*self.queued_opener(), append=True)
        starts = self.spy_cache_start()
        for bad in ("2026-09-21T22:49:56Z", float("nan"), float("inf"), True, None, "drop"):
            with self.subTest(cur_at=bad):
                c = dict(good)
                if bad == "drop":
                    del c["cur_at"]                         # a cache from before the rule
                else:
                    c["cur_at"] = bad
                del starts[:]
                r = L.scan_transcript(self.p, c)
                self.assertEqual(starts, [good["size"]])
                self.assertEqual((r["cur"], r["cur_at"]), (950_000, None))
        # measure() with such a cache: the rule does not apply (today's behaviour)
        c = dict(good)
        del c["cur_at"]
        L.update_state("s", lambda st: st.update(scan=c))
        L.reset_epoch("s")
        del starts[:]
        self.assertEqual(L.measure(self.p, "s")["tokens"], 950_000)
        self.assertEqual(starts, [good["size"]])

    def test_epoch_cur_units(self):
        st = {"epoch_at": 1000.0}
        self.assertEqual(L._epoch_cur(950_000, None, st), (950_000, False))
        self.assertEqual(L._epoch_cur(950_000, 999.0, {}), (950_000, False))
        self.assertEqual(L._epoch_cur(950_000, 999.0, {"epoch_at": "soon"}), (950_000, False))
        self.assertEqual(L._epoch_cur(950_000, 1000.0, st), (0, True))       # equal: earlier
        self.assertEqual(L._epoch_cur(950_000, 999.9, st), (0, True))
        self.assertEqual(L._epoch_cur(950_000, 1000.1, st), (950_000, False))
        self.assertEqual(L._epoch_cur(950_000, time.time() + 3600, st),      # future: kept
                         (950_000, False))
        self.assertEqual(L._epoch_cur(0, 999.0, st), (0, False))
        self.assertEqual(L._epoch_cur(950_000, float("nan"), st), (950_000, False))
        self.assertEqual(L._epoch_cur(950_000, True, st), (950_000, False))
        # No grace for transcript counts: the line stamp is Claude Code's own.
        self.assertEqual(L._epoch_cur(950_000, 1000.0 + L.EPOCH_GRACE_S / 2, st),
                         (950_000, False))

    def test_future_epoch_at_is_ignored(self):
        # The clock stepped back after _reset: a cut more than FUTURE_SKEW_S
        # ahead of now does not apply; one within the skew still does.
        now = time.time()
        far = {"epoch_at": now + L.FUTURE_SKEW_S + 600}
        self.assertEqual(L._epoch_cur(950_000, now - 5, far), (950_000, False))
        self.assertEqual(L._epoch_cur(950_000, now - 5, {"epoch_at": now + 10}),
                         (0, True))
        self.write(self.usage(950_000, now - 5))
        L.save_state("s", far)
        for mirror in (True, False):
            with self.subTest(mirror=mirror):
                self.assertEqual(L.measure(self.p, "s", mirror=mirror)["tokens"], 950_000)


class TestEnvSetting(Base):
    def test_canonical_then_alias(self):
        names = ("CANON", "ALIAS")
        self.assertIsNone(L.env_setting(names, {}))
        self.assertEqual(L.env_setting(names, {"ALIAS": "2"}), "2")
        self.assertEqual(L.env_setting(names, {"CANON": "1"}), "1")
        self.assertEqual(L.env_setting(names, {"CANON": "1", "ALIAS": "2"}), "1")
        self.assertEqual(L.env_setting(names, {"CANON": "x", "ALIAS": "2"}), "x")
        self.assertEqual(L.env_setting(names, {"CANON": "", "ALIAS": "2"}), "2")
        self.assertIsNone(L.env_setting(names, {"CANON": "", "ALIAS": ""}))

    def test_validator_picks_the_first_valid_value(self):
        names, dig = ("CANON", "ALIAS"), str.isdigit
        self.assertEqual(L.env_setting(names, {"CANON": "1", "ALIAS": "2"}, dig), "1")
        self.assertEqual(L.env_setting(names, {"CANON": "x", "ALIAS": "2"}, dig), "2")
        self.assertEqual(L.env_setting(names, {"CANON": "1", "ALIAS": "y"}, dig), "1")
        # Nothing valid: the first non-empty value, raw, for the reader to
        # reject exactly as before.
        self.assertEqual(L.env_setting(names, {"CANON": "x", "ALIAS": "y"}, dig), "x")
        self.assertEqual(L.env_setting(names, {"ALIAS": "y"}, dig), "y")
        self.assertIsNone(L.env_setting(names, {"CANON": ""}, dig))

    def test_names(self):
        self.assertEqual(L.WINDOW_ENV,
                         ("CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW"))
        self.assertEqual(L.LEDGER_EVERY_ENV,
                         ("CONTEXT_GUARD_LEDGER_EVERY", "CLAUDE_KIT_LEDGER_EVERY"))


class TestLedger(Base):
    def test_append_and_tail(self):
        self.assertTrue(ledger.append("s", "D", "chose X over Y", ref="a/b.md"))
        self.assertTrue(ledger.append("s", "X", "rejected Z"))
        self.assertFalse(ledger.append("s", "Z", "bad kind"))
        t = ledger.tail("s")
        self.assertIn("- D chose X over Y -> a/b.md", t)
        self.assertIn("- X rejected Z", t)

    def test_tail_bounded_newest_first(self):
        for i in range(200):
            ledger.append("s", "D", f"entry {i}")
        t = ledger.tail("s", max_chars=200)
        self.assertLessEqual(len(t), 220)
        self.assertIn("entry 199", t)
        self.assertNotIn("entry 0\n", t)



class TestSweep(Base):
    def d(self):
        return os.path.dirname(L.state_path("x"))

    def touch(self, name, age_days=0):
        p = os.path.join(self.d(), name)
        with open(p, "w") as fh:
            fh.write("{}")
        t = time.time() - age_days * 86400
        os.utime(p, (t, t))
        return p

    def test_sweeps_old_temp_and_dead_locks_only(self):
        self.touch(".a.1.abcdef012345.tmp", 2)       # old temp: gone
        self.touch(".b.1.abcdef012345.tmp", 0.1)     # young temp: kept
        self.touch("c.json", 31); self.touch(".c.lock", 31)   # dead session: lock gone
        self.touch("d.json", 1); self.touch(".d.lock", 60)    # live session: kept
        self.touch(".e.lock", 31)                    # orphan lock, no state: gone
        self.touch(".f.lock", 1)                     # young orphan lock: kept
        self.touch(".k.1.abcdef012345.tmp", 9); self.touch(".k.lock", 90)  # keep=k
        removed = L.sweep_stale(keep="k")
        self.assertEqual(sorted(removed), [".a.1.abcdef012345.tmp", ".c.lock", ".e.lock"])
        left = set(os.listdir(self.d()))
        for n in (".b.1.abcdef012345.tmp", "c.json", "d.json", ".d.lock", ".f.lock",
                  ".k.1.abcdef012345.tmp", ".k.lock"):
            self.assertIn(n, left)

    def test_held_lock_is_not_removed(self):
        import fcntl
        self.touch("h.json", 40)
        p = self.touch(".h.lock", 40)
        fd = os.open(p, os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertEqual(L.sweep_stale(), [])
        finally:
            os.close(fd)
        self.assertTrue(os.path.exists(p))

    def test_runs_at_most_once_a_day_and_never_raises(self):
        self.touch(".a.1.abcdef012345.tmp", 2)
        self.assertEqual(len(L.sweep_stale()), 1)
        self.touch(".b.1.abcdef012345.tmp", 2)
        self.assertEqual(L.sweep_stale(), [])        # stamped: skipped
        self.assertEqual(len(L.sweep_stale(now=time.time() + 2 * 86400)), 1)
        from unittest import mock
        with mock.patch.object(L.os, "listdir", side_effect=OSError("boom")):
            self.assertEqual(L.sweep_stale(now=time.time() + 9 * 86400), [])

    def test_lock_open_refuses_symlink(self):
        outside = os.path.join(self.tmp.name, "outside")
        os.symlink(outside, os.path.join(self.d(), ".y.lock"))
        L.update_state("y", lambda st: st.update(a=1))   # proceeds unlocked
        self.assertFalse(os.path.exists(outside))
        self.assertEqual(L.load_state("y")["a"], 1)

    def test_swept_stamp_symlink_is_not_followed(self):
        victim = os.path.join(self.tmp.name, "victim.txt")
        with open(victim, "w") as fh:
            fh.write("precious")
        os.symlink(victim, os.path.join(self.d(), ".swept"))
        self.touch(".a.1.abcdef012345.tmp", 2)
        L.sweep_stale()
        with open(victim) as fh:
            self.assertEqual(fh.read(), "precious")
        dangling = os.path.join(self.tmp.name, "nowhere.txt")
        os.remove(os.path.join(self.d(), ".swept"))
        os.symlink(dangling, os.path.join(self.d(), ".swept"))
        L.sweep_stale(now=time.time() + 9 * 86400)
        self.assertFalse(os.path.exists(dangling))

    def test_planted_stamp_falls_back_and_keeps_the_daily_limit(self):
        # a .swept symlink can never be re-dated; without the fallback stamp
        # its lstat mtime ages past a day and every hook call sweeps
        os.symlink(os.path.join(self.tmp.name, "nowhere"), os.path.join(self.d(), ".swept"))
        old = time.time() - 3 * 86400
        os.utime(os.path.join(self.d(), ".swept"), (old, old), follow_symlinks=False)
        self.touch(".a.1.abcdef012345.tmp", 2)
        self.assertEqual(len(L.sweep_stale()), 1)
        self.assertTrue(os.path.isfile(os.path.join(self.d(), ".swept-2")))
        self.touch(".b.1.abcdef012345.tmp", 2)
        self.assertEqual(L.sweep_stale(), [])        # the fallback stamp holds
        self.assertEqual(len(L.sweep_stale(now=time.time() + 2 * 86400)), 1)

    def test_every_stamp_planted_skips_the_sweep(self):
        for name in L.SWEEP_STAMPS:
            os.mkdir(os.path.join(self.d(), name))
        self.touch(".a.1.abcdef012345.tmp", 2)
        self.assertEqual(L.sweep_stale(now=time.time() + 9 * 86400), [])
        self.assertIn(".a.1.abcdef012345.tmp", os.listdir(self.d()))

    def test_acquire_rejects_lock_on_orphaned_inode(self):
        # A waiter that opened the lock file before the sweep unlinked it wins
        # the flock on a dead inode; it must re-open the path, not trust it.
        from unittest import mock
        path = os.path.join(self.d(), ".o.lock")
        with open(path, "w"):
            pass
        orphan = os.open(path, os.O_RDWR)
        os.unlink(path)
        real_open, calls = os.open, []

        def fake_open(p, *a, **k):
            calls.append(p)
            return os.dup(orphan) if len(calls) == 1 else real_open(p, *a, **k)
        with mock.patch.object(L.os, "open", fake_open):
            fd = L._acquire("o")
        os.close(orphan)
        self.assertIsNotNone(fd)
        try:
            self.assertEqual(len(calls), 2)
            self.assertEqual(os.fstat(fd).st_ino, os.stat(path).st_ino)
        finally:
            L._release(fd)


class TestOwnStoreManifest(Base):
    """The store's ownership-by-path test, shared by the mark step (write)
    and rehydrate's read_store_manifest (read)."""
    def test_the_real_file_is_ours_and_nothing_else_is(self):
        p = L.manifest_path("S")
        os.makedirs(os.path.dirname(p))
        with open(p, "w") as fh:
            fh.write("x")
        self.assertTrue(L.own_store_manifest(p, "S"))
        self.assertFalse(L.own_store_manifest(p, "T"))          # another session
        self.assertFalse(L.own_store_manifest(p + ".bak", "S"))  # not a manifest
        self.assertFalse(L.own_store_manifest(None, "S"))        # exceptions are False
        self.assertFalse(L.own_store_manifest(p, None))
        outside = os.path.join(self.tmp.name, "peer.md")
        with open(outside, "w") as fh:
            fh.write("x")
        link = L.manifest_path("L")
        os.makedirs(os.path.dirname(link))
        os.symlink(outside, link)
        self.assertFalse(L.own_store_manifest(link, "L"))       # a link out
        # An unsafe id compares through safe_sid, never the raw id.
        raw = "a/b"
        q = L.manifest_path(raw)
        os.makedirs(os.path.dirname(q))
        with open(q, "w") as fh:
            fh.write("x")
        self.assertTrue(L.own_store_manifest(q, raw))


class TestMarkCheckpointCli(Base):
    def run_cli(self, sid):
        import subprocess
        return subprocess.run([sys.executable, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mark_checkpoint.py"), sid], capture_output=True, text=True,
            # cwd: the temp config dir, never this checkout, whose own
            # HANDOFF.md the mark step would otherwise try to stamp.
            env=dict(os.environ, CLAUDE_CONFIG_DIR=self.tmp.name), cwd=self.tmp.name,
            timeout=30)

    def test_refuses_unknown_session(self):
        p = self.run_cli("typo-sid")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no context-gate state for session 'typo-sid'", p.stderr)
        self.assertFalse(os.path.exists(L.state_path("typo-sid")))

    def test_marks_known_session(self):
        L.save_state("live", {"epoch": 2})
        p = self.run_cli("live")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("checkpoint recorded for epoch 2", p.stdout)
        self.assertEqual(L.load_state("live")["checkpoint_epoch"], 2)



class InputSinceUsage(Base):
    """22b2: whether a prompt or tool result follows the last measured fill."""
    A = {"type": "assistant", "message": {"usage": {"input_tokens": 5}}}
    A0 = {"type": "assistant", "message": {"usage": {"input_tokens": 0}}}
    U = {"type": "user", "message": {"content": "hi"}}
    S = {"type": "system", "subtype": "x"}

    def write(self, *recs, pad=0):
        p = os.path.join(self.tmp.name, "t.jsonl")
        with open(p, "w") as f:
            for r in recs:
                if r == "PAD":
                    r = dict(self.S, pad="x" * pad)
                f.write(json.dumps(r) + "\n")
        return p

    def test_idle_after_usage(self):
        self.assertFalse(L.input_since_usage(self.write(self.U, self.A, self.S, self.S)))

    def test_user_after_usage(self):
        self.assertTrue(L.input_since_usage(self.write(self.A, self.S, self.U)))

    def test_usage_without_tokens_is_not_a_measurement(self):
        self.assertTrue(L.input_since_usage(self.write(self.A, self.U, self.A0)))

    def test_missing_unreadable_or_empty_counts_as_pending(self):
        self.assertTrue(L.input_since_usage(""))
        self.assertTrue(L.input_since_usage(os.path.join(self.tmp.name, "nope")))
        self.assertTrue(L.input_since_usage(self.tmp.name))   # a directory
        self.assertTrue(L.input_since_usage(self.write()))
        self.assertTrue(L.input_since_usage(self.write(self.S)))

    def test_lines_across_chunk_boundaries(self):
        # padding lines larger than a chunk put the usage line mid-chunk
        p = self.write(self.U, self.A, "PAD", "PAD", self.S, pad=150_000)
        self.assertFalse(L.input_since_usage(p))
        p = self.write(self.A, "PAD", self.U, "PAD", pad=150_000)
        self.assertTrue(L.input_since_usage(p))

    def test_a_tail_past_the_cap_counts_as_pending(self):
        p = self.write(self.A, "PAD", pad=200_000)
        self.assertFalse(L.input_since_usage(p))
        self.assertTrue(L.input_since_usage(p, max_bytes=100_000))


if __name__ == "__main__":
    unittest.main()
